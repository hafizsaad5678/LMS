import json
import logging
import threading
from io import BytesIO

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.chatbot import ChatSession, ChatMessage, ChatMetric
from ..models.chatbot import UploadedFile
from ..serializers.chatbot import ChatSessionSerializer, ChatMessageSerializer
from ..services.config import CHAT_HISTORY_LIMIT, SOURCE_LABEL_LLM_FALLBACK, SOURCE_LABEL_LLM_GENERAL, DOC_MODE_CACHE_TTL_SECONDS, UPLOAD_POLL_INTERVAL_PROCESSING_MS, UPLOAD_POLL_INTERVAL_PENDING_MS
from ..services.utils import get_doc_mode_cache_key

logger = logging.getLogger(__name__)


def _is_timeout_like_error(exc: Exception) -> bool:
    text = str(exc).lower()
    name = type(exc).__name__.lower()
    return (
        'timeout' in text
        or 'timed out' in text
        or 'readtimeout' in name
        or 'apitimeouterror' in name
    )


def _stream_fallback_text(exc: Exception) -> str:
    if _is_timeout_like_error(exc):
        return 'The AI provider is taking too long right now. Please try again in a moment or ask a shorter question.'
    return "I'm sorry, I'm having trouble connecting to the knowledge base right now. Please try again in a moment."

class StudentChatView(APIView):
    """
    Main endpoint for student academic chatbot.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('message')
        session_id = request.data.get('session_id')
        stream_requested = bool(request.data.get('stream') or request.query_params.get('stream'))
        
        if not query:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user, title=query[:50])
            
        # Save user message
        user_msg = ChatMessage.objects.create(session=session, role='user', content=query)
        
        # Get history for context (exclude current message to avoid duplication in LLM context)
        history_msgs = (
            ChatMessage.objects.filter(session=session)
            .exclude(id=user_msg.id)
            .order_by('-created_at')[:CHAT_HISTORY_LIMIT]
        )
        history = []
        for msg in reversed(history_msgs):
            role = (msg.role or 'user').strip().lower()
            if role == 'bot':
                role = 'assistant'
            elif role != 'assistant':
                role = 'user'
            history.append({"role": role, "content": msg.content})
        
        try:
            from ..services.chat.chatbot import orchestrate_response

            # Get response from chatbot service (it handles streaming check internally)
            result = orchestrate_response(
                request.user,
                query,
                history=history,
                streaming=stream_requested,
                session_id=str(session.id),
            )

            # Streaming mode (SSE)
            if stream_requested and result.get('stream_generator'):
                def event_stream():
                    full = ""
                    source = result.get('source', SOURCE_LABEL_LLM_GENERAL)
                    intent = result.get('intent', 'general')
                    latency = result.get('latency', 0.0)
                    confidence = result.get('confidence', 0.0)

                    # The generator might be a list or a single function.
                    gen_funcs = result['stream_generator'] if isinstance(result['stream_generator'], list) else [result['stream_generator']]

                    for gen_func in gen_funcs:
                        try:
                            for chunk in gen_func():
                                chunk_text = str(chunk or '')
                                if not chunk_text:
                                    continue
                                full += chunk_text
                                yield f"data: {json.dumps({'chunk': chunk_text})}\n\n"
                        except Exception as stream_exc:
                            logger.error("Chatbot stream error: %s", stream_exc, exc_info=True)
                            source = SOURCE_LABEL_LLM_FALLBACK
                            fallback_chunk = _stream_fallback_text(stream_exc)
                            full += fallback_chunk
                            yield f"data: {json.dumps({'chunk': fallback_chunk})}\n\n"
                            break

                    if not full:
                        source = SOURCE_LABEL_LLM_FALLBACK
                        full = "I'm sorry, I couldn't generate a response right now. Please try again shortly."
                        yield f"data: {json.dumps({'chunk': full})}\n\n"

                    try:
                        bot_msg = ChatMessage.objects.create(
                            session=session,
                            role='bot',
                            content=full,
                            intent=intent,
                            source=source,
                            latency=latency,
                            confidence=confidence,
                        )
                    except Exception as save_exc:
                        logger.error("Failed to save streamed bot message: %s", save_exc, exc_info=True)
                        done_payload = {
                            'done': True,
                            'session_id': str(session.id),
                            'message': {
                                'role': 'bot',
                                'content': full,
                                'source': source,
                                'intent': intent,
                                'latency': latency,
                                'confidence': confidence,
                            }
                        }
                        yield f"data: {json.dumps(done_payload)}\n\n"
                        return

                    try:
                        ChatMetric.objects.create(
                            message=bot_msg,
                            is_grounded=(source != SOURCE_LABEL_LLM_GENERAL),
                        )
                    except Exception as metric_exc:
                        logger.error("Failed to save streamed chat metric: %s", metric_exc, exc_info=True)

                    yield f"data: {json.dumps({'done': True, 'session_id': str(session.id), 'message': ChatMessageSerializer(bot_msg).data})}\n\n"

                response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
                response['Cache-Control'] = 'no-cache'
                response['X-Accel-Buffering'] = 'no'
                return response

            # Non-streaming JSON mode
            # Save bot message with metadata
            bot_msg = ChatMessage.objects.create(
                session=session,
                role='bot',
                content=result['text'],
                intent=result.get('intent'),
                source=result.get('source'),
                latency=result.get('latency', 0.0),
                confidence=result.get('confidence', 0.0)
            )

            # Save ChatMetric
            ChatMetric.objects.create(
                message=bot_msg,
                is_grounded=(result.get('source') != SOURCE_LABEL_LLM_GENERAL)
            )

            return Response({
                'session_id': str(session.id),
                'message': ChatMessageSerializer(bot_msg).data,
                'at_risk': result.get('at_risk', False),
                'data': result.get('data') # Optional domain data
            })
            
        except Exception as e:
            if _is_timeout_like_error(e):
                timeout_text = _stream_fallback_text(e)
                bot_msg = ChatMessage.objects.create(
                    session=session,
                    role='bot',
                    content=timeout_text,
                    intent='general',
                    source=SOURCE_LABEL_LLM_FALLBACK,
                    latency=0.0,
                    confidence=0.0,
                )
                ChatMetric.objects.create(
                    message=bot_msg,
                    is_grounded=False,
                )
                return Response({
                    'session_id': str(session.id),
                    'message': ChatMessageSerializer(bot_msg).data,
                    'at_risk': False,
                    'data': None,
                })

            logger.error(f"Chatbot error: {e}", exc_info=True)
            return Response({
                'error': 'Chatbot encountered an issue.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentChatSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id=None):
        if session_id:
            # Get a single session with messages
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            return Response(ChatSessionSerializer(session).data)
        
        # List all sessions (summary)
        sessions = ChatSession.objects.filter(user=request.user)
        return Response(ChatSessionSerializer(sessions, many=True).data)

    def delete(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, session_id=None):
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        title = str(request.data.get('title', '')).strip()

        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)

        session.title = title[:255]
        session.save(update_fields=['title', 'updated_at'])
        return Response(ChatSessionSerializer(session).data, status=status.HTTP_200_OK)


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.FILES.get('file')
        session_id = request.data.get('session_id')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user, title=file_obj.name[:50] or 'New Chat')
        
        # Save record
        try:
            uploaded_file = UploadedFile.objects.create(
                user=request.user,
                filename=file_obj.name,
                index_status=UploadedFile.IndexStatus.PENDING
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Async processing: read bytes now (request file object may close after response)
        try:
            content_bytes = file_obj.read()
        except Exception as e:
            uploaded_file.index_status = UploadedFile.IndexStatus.ERROR
            uploaded_file.save()
            return Response({'error': f'Failed to read uploaded file: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        def _run_indexing(user_id: int, session_id_value: str, uploaded_file_id: str, filename: str, data: bytes):
            try:
                from ..services.rag.utils import process_and_index_document

                UploadedFile.objects.filter(id=uploaded_file_id).update(index_status=UploadedFile.IndexStatus.PROCESSING)
                f = BytesIO(data)
                result = process_and_index_document(user_id, f, filename)
                uf = UploadedFile.objects.filter(id=uploaded_file_id).first()
                if not uf:
                    return
                if result.get('status') == 'success':
                    uf.index_status = UploadedFile.IndexStatus.INDEXED
                    cache.set(get_doc_mode_cache_key(user_id, session_id_value), True, DOC_MODE_CACHE_TTL_SECONDS)
                else:
                    uf.index_status = UploadedFile.IndexStatus.FAILED
                uf.save()
            except Exception as e:
                logger.error(f'Async upload processing failed: {e}', exc_info=True)
                UploadedFile.objects.filter(id=uploaded_file_id).update(index_status=UploadedFile.IndexStatus.ERROR)

        threading.Thread(
            target=_run_indexing,
            args=(request.user.id, str(session.id), str(uploaded_file.id), file_obj.name, content_bytes),
            daemon=True,
        ).start()

        return Response(
            {'status': 'pending', 'filename': file_obj.name, 'file_id': str(uploaded_file.id), 'session_id': str(session.id)},
            status=status.HTTP_202_ACCEPTED,
        )


class DocumentUploadStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)

        raw_status = (uploaded_file.index_status or '').strip().lower()
        if raw_status in {UploadedFile.IndexStatus.INDEXED, 'ready', 'success'}:
            status_value = 'indexed'
        elif raw_status in {UploadedFile.IndexStatus.FAILED, UploadedFile.IndexStatus.ERROR}:
            status_value = 'failed'
        elif raw_status in {UploadedFile.IndexStatus.PROCESSING}:
            status_value = 'processing'
        else:
            status_value = 'pending'

        if status_value == 'pending':
            poll_interval_ms = UPLOAD_POLL_INTERVAL_PROCESSING_MS
        elif status_value == 'processing':
            poll_interval_ms = UPLOAD_POLL_INTERVAL_PENDING_MS
        else:
            poll_interval_ms = 0

        return Response(
            {
                'file_id': str(uploaded_file.id),
                'filename': uploaded_file.filename,
                'status': status_value,
                'poll_interval_ms': poll_interval_ms,
            },
            status=status.HTTP_200_OK,
        )







