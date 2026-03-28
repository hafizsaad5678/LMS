from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from ..models.chatbot import ChatSession, ChatMessage, ChatMetric
from ..serializers.chatbot import ChatSessionSerializer, ChatMessageSerializer
from ..services.config import CHAT_HISTORY_LIMIT, SOURCE_LABEL_LLM_GENERAL
from ..services.chat.chatbot import orchestrate_response
import json
import logging

logger = logging.getLogger(__name__)

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
            # Get response from chatbot service (it handles streaming check internally)
            result = orchestrate_response(request.user, query, history=history, streaming=stream_requested)

            # Streaming mode (SSE)
            if stream_requested and result.get('stream_generator'):
                def event_stream():
                    try:
                        full = ""
                        # The generator might be a list or a single function
                        gen_funcs = result['stream_generator'] if isinstance(result['stream_generator'], list) else [result['stream_generator']]
                        for gen_func in gen_funcs:
                            for chunk in gen_func():
                                full += chunk
                                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

                        # Save bot message with metadata after stream completes
                        bot_msg = ChatMessage.objects.create(
                            session=session,
                            role='bot',
                            content=full,
                            intent=result.get('intent', 'general'),
                            source=result.get('source', SOURCE_LABEL_LLM_GENERAL),
                            latency=result.get('latency', 0.0),
                            confidence=result.get('confidence', 0.0),
                        )

                        ChatMetric.objects.create(
                            message=bot_msg,
                            is_grounded=(result.get('source') != SOURCE_LABEL_LLM_GENERAL),
                        )

                        yield f"data: {json.dumps({'done': True, 'session_id': str(session.id), 'message': ChatMessageSerializer(bot_msg).data})}\n\n"
                    except Exception as e:
                        logger.error(f"Chatbot stream error: {e}", exc_info=True)
                        yield f"data: {json.dumps({'error': 'Chatbot encountered an issue.', 'details': str(e)})}\n\n"

                response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
                response['Cache-Control'] = 'no-cache'
                response['X-Accel-Buffering'] = 'no'
                return response

            # Non-streaming JSON mode
            # result = orchestrate_response(request.user, query, history=history) # Already called above

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


from rest_framework.parsers import MultiPartParser, FormParser
from ..models.chatbot import UploadedFile
from ..services.rag.utils import process_and_index_document
import threading
from io import BytesIO

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save record
        try:
            uploaded_file = UploadedFile.objects.create(
                user=request.user,
                filename=file_obj.name,
                index_status='pending'
            )
            uploaded_file.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Async processing: read bytes now (request file object may close after response)
        try:
            content_bytes = file_obj.read()
        except Exception as e:
            uploaded_file.index_status = 'error'
            uploaded_file.save()
            return Response({'error': f'Failed to read uploaded file: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        def _run_indexing(user_id: int, uploaded_file_id: str, filename: str, data: bytes):
            try:
                f = BytesIO(data)
                result = process_and_index_document(user_id, f, filename)
                uf = UploadedFile.objects.filter(id=uploaded_file_id).first()
                if not uf:
                    return
                if result.get('status') == 'success':
                    uf.index_status = 'indexed'
                else:
                    uf.index_status = 'failed'
                uf.save()
            except Exception as e:
                logger.error(f'Async upload processing failed: {e}', exc_info=True)
                UploadedFile.objects.filter(id=uploaded_file_id).update(index_status='error')

        threading.Thread(
            target=_run_indexing,
            args=(request.user.id, str(uploaded_file.id), file_obj.name, content_bytes),
            daemon=True,
        ).start()

        return Response(
            {'status': 'pending', 'filename': file_obj.name, 'file_id': str(uploaded_file.id)},
            status=status.HTTP_202_ACCEPTED,
        )

