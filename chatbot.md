# local-reg-engine.py

import time
import os
from typing import Dict, List, Any
from django.conf import settings
from django.db.models import Q

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from chatbot.llm import get_chat_llm
from chatbot.rag_utils import get_embeddings, get_faiss_cls, normalize_similarity_score
from todo.models import Todo

# Configuration Constants

DEFAULT_TEMPERATURE = 0.7
MAX_CONTEXT_RESULTS = 10
MIN_SIMILARITY_SCORE = 0.2
HISTORY_LIMIT = 12

class LocalRAGEngine:
def **init**(self, user_id: int = 0, temperature: float = DEFAULT_TEMPERATURE):
self.user_id = user_id
self.\_faiss_cls = get_faiss_cls()
self.embeddings = get_embeddings()
self.llm = get_chat_llm(temperature=temperature)

        self.index_dir = os.path.join(str(settings.BASE_DIR), 'faiss_indexes', f'user_todos_lc_{user_id}')
        self._vector_store = None
        self._store_loaded = False

    @property
    def vector_store(self):
        if not self._store_loaded:
            self._vector_store = self._load_vector_store()
            if (not self._vector_store) and Todo.objects.filter(user_id=self.user_id).exists():
                self._auto_rebuild()
            self._store_loaded = True
        return self._vector_store

    @vector_store.setter
    def vector_store(self, store):
        self._vector_store = store
        self._store_loaded = True

    def _load_vector_store(self):
        if os.path.exists(os.path.join(self.index_dir, "index.faiss")):
            return self._faiss_cls.load_local(
                self.index_dir,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        return None

    def _auto_rebuild(self):
        """Silently index all todos for this user on first run."""
        todos = Todo.objects.filter(user_id=self.user_id)
        if todos.exists():
            self.index_todos(todos)
        print(f"Auto-index complete for user {self.user_id}.")

    def index_todos(self, todos):
        """Add or update todos in vector index."""
        documents = []
        ids = []
        for todo in todos:
            text = f"Task: {todo.title}. Status: {'Done' if todo.completed else 'Pending'}"
            if todo.description:
                text += f". Details: {todo.description}"

            doc_id = f"todo_{todo.id}"
            documents.append(Document(
                page_content=text,
                metadata={'todo_id': todo.id, 'user_id': self.user_id}
            ))
            ids.append(doc_id)

        if not documents:
            return {'status': 'skipped', 'count': 0}

        if not self.vector_store:
            self.vector_store = self._faiss_cls.from_documents(documents, self.embeddings, ids=ids)
        else:
            # Delete existing ids to prevent duplicates
            try:
                self.vector_store.delete(ids)
            except Exception:
                pass
            self.vector_store.add_documents(documents, ids=ids)
        return {'status': 'indexed', 'count': len(documents)}

    def query(self, user_query: str, history=None, stream=False, user_memory: str = "") -> Dict:
        start_time = time.time()

        context_docs = self._get_context(user_query)
        context_text = "\n".join(f"- {d['text']}" for d in context_docs) or "No relevant tasks found."
        history_text = self._format_history(history or [])
        memory_text = (user_memory or "").strip() or "No saved user memory."

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an AI productivity assistant.\n\n"
                "Rules:\n"
                "- Use task context when relevant.\n"
                "- If context answers the question, prioritize it.\n"
                "- If context is unrelated, answer normally.\n"
                "- Be concise and helpful.\n\n"
                "Saved User Memory:\n{user_memory}\n\n"
                "Task Context:\n{context}\n\n"
                "Recent Conversation:\n{chat_history}",
            ),
            ("human", "{input}"),
        ])

        messages = prompt.format_messages(
            user_memory=memory_text,
            context=context_text,
            chat_history=history_text,
            input=user_query,
        )

        if stream:
            return self._stream_response(messages)

        response = self.llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)

        return {
            'answer': answer,
            'context': context_docs,
            'tokens': len(answer) // 4,
            'time': round(time.time() - start_time, 2)
        }

    def _stream_response(self, messages):
        for chunk in self.llm.stream(messages):
            text = getattr(chunk, "content", "")
            if text:
                yield text

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        if not history:
            return "No prior conversation."

        lines = []
        for item in history[-HISTORY_LIMIT:]:
            role = (item.get("role") or "user").strip().lower()
            content = (item.get("content") or "").strip()
            if not content:
                continue
            label = "Assistant" if role in {"assistant", "bot"} else "User"
            lines.append(f"{label}: {content}")

        return "\n".join(lines) if lines else "No prior conversation."

    def _get_context(self, user_query: str) -> List[Dict]:
        keyword_matches = Todo.objects.filter(user_id=self.user_id).filter(
            Q(title__icontains=user_query) | Q(description__icontains=user_query)
        )[:MAX_CONTEXT_RESULTS]

        context_docs = []
        seen_ids = set()

        for todo in keyword_matches:
            seen_ids.add(todo.id)
            context_docs.append({
                'text': f"Task: {todo.title} ({'Done' if todo.completed else 'Pending'}). Details: {todo.description or ''}",
                'score': 1.0,
                'todo_id': todo.id
            })

        if self.vector_store:
            similar = self.vector_store.similarity_search_with_score(user_query, k=MAX_CONTEXT_RESULTS)

            for doc, raw_score in similar:
                todo_id = doc.metadata.get('todo_id')
                score = normalize_similarity_score(raw_score)
                if todo_id in seen_ids or score < MIN_SIMILARITY_SCORE:
                    continue

                context_docs.append({
                    'text': doc.page_content,
                    'score': score,
                    'todo_id': todo_id
                })
                seen_ids.add(todo_id)

        return context_docs

# memory-space.py

import re
from typing import List

from django.contrib.auth.models import User

from .models import UserMemory

MAX_MEMORY_LINES = 30

def get*user_memory_text(user: User) -> str:
memory, * = UserMemory.objects.get_or_create(user=user)
return memory.memory_text.strip()

def update*user_memory(user: User, user_message: str) -> str:
memory, * = UserMemory.objects.get_or_create(user=user)

    existing_lines = _normalize_lines(memory.memory_text.splitlines())
    extracted_lines = _extract_memory_lines(user_message)

    for line in extracted_lines:
        if line not in existing_lines:
            existing_lines.append(line)

    if len(existing_lines) > MAX_MEMORY_LINES:
        existing_lines = existing_lines[-MAX_MEMORY_LINES:]

    memory.memory_text = "\n".join(existing_lines)
    memory.save(update_fields=["memory_text", "updated_at"])
    return memory.memory_text

def clear*user_memory(user: User):
memory, * = UserMemory.objects.get_or_create(user=user)
memory.memory_text = ""
memory.save(update_fields=["memory_text", "updated_at"])

def \_normalize_lines(lines: List[str]) -> List[str]:
normalized = []
seen = set()
for line in lines:
clean = line.strip()
if not clean:
continue
key = clean.lower()
if key in seen:
continue
seen.add(key)
normalized.append(clean)
return normalized

def \_extract_memory_lines(message: str) -> List[str]:
text = (message or "").strip()
if not text:
return []

    try:
        from .llm import get_chat_llm
        from langchain_core.prompts import ChatPromptTemplate

        llm = get_chat_llm(temperature=0.0)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract important personal facts, preferences, or goals about the user from their message. "
                       "Return ONLY a list of short facts separated by newlines. If no facts are present, return exactly 'NONE'."),
            ("human", "{input}")
        ])
        response = llm.invoke(prompt.format_messages(input=text))
        content = response.content.strip()

        if content == "NONE" or not content:
            return []

        lines = [line.lstrip("-* ").strip() for line in content.splitlines() if line.strip() and line.strip() != "NONE"]
        return _normalize_lines(lines)
    except Exception as e:
        print(f"Memory extraction failed: {e}")
        return []

# models .py

from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
title = models.CharField(max_length=255, default="New Chat")
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class ChatMessage(models.Model):
session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
role = models.CharField(max_length=10) # 'user' or 'bot'
content = models.TextField()
created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

class UserMemory(models.Model):
"""Stores learned facts and habits about the user
User prefers morning productivity
User works on coding tasks at night
User tracks fitness tasks"""
user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_memory')
memory_text = models.TextField(blank=True, default="")
updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Memory for {self.user.username}"

# reg-utilis.py

import os

from django.conf import settings

def get_faiss_cls():
from langchain_community.vectorstores import FAISS

    return FAISS

def get_hf_embeddings_cls():
try:
from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
from langchain_community.embeddings import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings

def get_embeddings():
model_path = os.path.join(str(settings.BASE_DIR), "models", "all-MiniLM-L6-v2")
model_name = model_path if os.path.exists(model_path) else "sentence-transformers/all-MiniLM-L6-v2"

    embeddings_cls = get_hf_embeddings_cls()
    return embeddings_cls(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def normalize_similarity_score(raw_score) -> float:
score = float(raw_score)
if 0.0 <= score <= 1.0:
return score
if score < 0.0:
return max(0.0, min(1.0, (score + 1.0) / 2.0))
return 1.0 / (1.0 + score)

# signls.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from todo.models import Todo
from .views import get_engine
import os

@receiver(post_save, sender=Todo)
def index_todo_on_save(sender, instance, created, \*\*kwargs):
"""Auto-index when todo is created or updated — uses per-user engine."""
try:
get_engine(instance.user_id).index_todos([instance])
print(f"Indexed todo {instance.id} for user {instance.user_id}")
except Exception as e:
print(f"Failed to index todo {instance.id}: {e}")

@receiver(post_delete, sender=Todo)
def remove_todo_from_index(sender, instance, \*\*kwargs):
"""Rebuild the user's FAISS index completely when a todo is deleted."""
try:
from todo.models import Todo
engine = get_engine(instance.user_id) # Clear/Delete the index folder and rebuild
import shutil
if os.path.exists(engine.index_dir):
shutil.rmtree(engine.index_dir)
engine.vector_store = None
todos = Todo.objects.filter(user_id=instance.user_id)
engine.index_todos(todos)
print(f"FAISS index rebuilt for user {instance.user_id} after deleting todo {instance.id}")
except Exception as e:
print(f"Failed to rebuild FAISS index on delete: {e}")

# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
import json
from .local_rag_engine import LocalRAGEngine
from .models import ChatSession, ChatMessage, UserMemory
from .serializers import ChatSessionSerializer, ChatSessionListSerializer, UserMemorySerializer
from .memory_service import get_user_memory_text, update_user_memory, clear_user_memory

# Per-user engine cache If we don't declare this empty

# dictionary at the very top of the file, the get_engine function

# won't have anywhere to save the engines once it builds them.

from functools import lru_cache

@lru_cache(maxsize=100)
def get_engine(user_id: int):
return LocalRAGEngine(user_id=user_id)

class ChatAPIView(APIView):
"""Main chat endpoint"""
permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('message')
        session_id = request.data.get('session_id')
        stream = request.data.get('stream', False)

        if not query:
            return Response({'error': 'Message required'}, status=400)

        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            title = query[:30] + '...' if len(query) > 30 else query
            session = ChatSession.objects.create(user=request.user, title=title)

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=query)

        try:
            # Get past messages for context
            recent_messages = ChatMessage.objects.filter(session=session).order_by('-created_at')[:5]

            # Reverse to chronological order
            history = []
            for msg in reversed(list(recent_messages)):
                if msg.content != query: # Skip the one we literally just saved above
                    history.append({"role": "assistant" if msg.role == 'bot' else "user", "content": msg.content})

            user_memory = get_user_memory_text(request.user)

            # Generate answer
            engine = get_engine(request.user.id)

            if stream:
                def event_stream():
                    result_generator = engine.query(
                        query,
                        history=history,
                        stream=True,
                        user_memory=user_memory,
                    )
                    full_answer = ""
                    for chunk in result_generator:
                        full_answer += chunk
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"

                    # Save bot message
                    ChatMessage.objects.create(session=session, role='bot', content=full_answer)
                    update_user_memory(request.user, query)

                    yield f"data: {json.dumps({'session_id': session.id, 'done': True})}\n\n"

                return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            else:
                result = engine.query(
                    query,
                    history=history,
                    stream=False,
                    user_memory=user_memory,
                )
                answer = result['answer']

                # Save bot message
                ChatMessage.objects.create(session=session, role='bot', content=answer)
                update_user_memory(request.user, query)

                result['session_id'] = session.id
                return Response(result)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

class IndexTodosView(APIView):
"""Manually rebuild LangChain FAISS index"""
permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            engine = get_engine(request.user.id)
            from todo.models import Todo
            todos = Todo.objects.filter(user_id=request.user.id)
            result = engine.index_todos(todos)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class IndexStatsView(APIView):
"""Get FAISS index statistics (placeholder for LangChain)"""
permission_classes = [IsAuthenticated]

    def get(self, request):
        engine = get_engine(request.user.id)
        if engine.vector_store:
            count = engine.vector_store.index.ntotal
        else:
            count = 0
        return Response({'total_indexed': count, 'engine': 'LangChain FAISS'})

class ChatSessionListView(APIView):
"""List all chat sessions for the current user or create a new one"""
permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user)
        serializer = ChatSessionListSerializer(sessions, many=True)
        return Response(serializer.data)

class ChatSessionDetailView(APIView):
"""Get history of a specific chat session or delete it"""
permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)

    def delete(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class WarmupView(APIView):
"""Warm up per-user RAG engine after login to avoid first-message cold start."""
permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            engine = get_engine(request.user.id)
            indexed = int(engine.vector_store.index.ntotal) if engine.vector_store else 0
            return Response({
                'status': 'ready',
                'indexed': indexed,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class UserMemoryView(APIView):
"""Read or clear learned user memory."""
permission_classes = [IsAuthenticated]

    def get(self, request):
        memory, _ = UserMemory.objects.get_or_create(user=request.user)
        return Response(UserMemorySerializer(memory).data)

    def delete(self, request):
        clear_user_memory(request.user)
        return Response({'status': 'cleared'})

# for document upload

# chunking.py

from typing import List, Dict
from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
def **init**(self, chunk_size: int = None, chunk_overlap: int = None): # Use safe defaults when optional settings are not configured. # 800 chars keeps a full Q+Explanation pair in a single chunk.
self.chunk_size = int(chunk_size or getattr(settings, 'CHUNK_SIZE', 800))
self.chunk_overlap = int(chunk_overlap or getattr(settings, 'CHUNK_OVERLAP', 100))

        # Use LangChain's RecursiveCharacterTextSplitter for smarter splitting
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def chunk_text(self, text: str) -> List[Dict]:
        """
        Split text into overlapping chunks using LangChain's recursive splitter.
        Returns: List of dicts with 'text', 'chunk_index', 'page'
        """
        chunks = self.splitter.split_text(text)

        return [{
            'text': chunk.strip(),
            'chunk_index': i,
            'page': None
        } for i, chunk in enumerate(chunks) if chunk.strip()]

# models.py

import os
import uuid
from django.db import models
from django.contrib.auth.models import User

def user*directory_path(instance, filename):
"""File ko user-specific folder mein save karo"""
ext = filename.split('.')[-1]
filename = f"{uuid.uuid4()}.{ext}"
return f'uploads/user*{instance.user.id}/{filename}'

class UploadedFile(models.Model):
FILE_TYPES = [
('pdf', 'PDF'),
('txt', 'Text'),
('docx', 'Word'),
]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    total_chunks = models.PositiveIntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} ({self.user.username})"

    def delete(self, *args, **kwargs):
        # File delete hone pe actual file bhi delete karo
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class FileChunk(models.Model):
uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='chunks')
chunk_index = models.PositiveIntegerField()
chunk_text = models.TextField()
page_number = models.PositiveIntegerField(null=True, blank=True)
created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chunk_index']
        unique_together = ['uploaded_file', 'chunk_index']

    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.uploaded_file.original_filename}"

# text-extractors.py

class TextExtractor:
"""Factory class for text extraction"""

    @staticmethod
    def extract(file_path: str, file_type: str) -> str:
        if file_type == 'pdf':
            return PDFExtractor.extract(file_path)
        elif file_type == 'txt':
            return TXTExtractor.extract(file_path)
        elif file_type == 'docx':
            return DOCXExtractor.extract(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

class PDFExtractor:
@staticmethod
def extract(file_path: str) -> str:
try:
from pypdf import PdfReader
reader = PdfReader(file_path)
text = ""
for page in reader.pages:
text += page.extract_text() + "\n"
return text
except ImportError: # Fallback to pdfplumber
import pdfplumber
with pdfplumber.open(file_path) as pdf:
return "\n".join(page.extract_text() or "" for page in pdf.pages)

class TXTExtractor:
@staticmethod
def extract(file_path: str) -> str:
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
return f.read()

class DOCXExtractor:
@staticmethod
def extract(file_path: str) -> str:
from docx import Document
doc = Document(file_path)
return "\n".join(paragraph.text for paragraph in doc.paragraphs)

# vector-stores.py

class TextExtractor:
"""Factory class for text extraction"""

    @staticmethod
    def extract(file_path: str, file_type: str) -> str:
        if file_type == 'pdf':
            return PDFExtractor.extract(file_path)
        elif file_type == 'txt':
            return TXTExtractor.extract(file_path)
        elif file_type == 'docx':
            return DOCXExtractor.extract(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

class PDFExtractor:
@staticmethod
def extract(file_path: str) -> str:
try:
from pypdf import PdfReader
reader = PdfReader(file_path)
text = ""
for page in reader.pages:
text += page.extract_text() + "\n"
return text
except ImportError: # Fallback to pdfplumber
import pdfplumber
with pdfplumber.open(file_path) as pdf:
return "\n".join(page.extract_text() or "" for page in pdf.pages)

class TXTExtractor:
@staticmethod
def extract(file_path: str) -> str:
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
return f.read()

class DOCXExtractor:
@staticmethod
def extract(file_path: str) -> str:
from docx import Document
doc = Document(file_path)
return "\n".join(paragraph.text for paragraph in doc.paragraphs)

# views.py

import os
import re
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import UploadedFile, FileChunk
from .serializers import (
UploadedFileSerializer, FileUploadSerializer,
QuestionSerializer
)
from .text_extractors import TextExtractor
from .chunking import TextChunker
from .vector_store import DocumentVectorStore
from chatbot.llm import get_chat_llm
from chatbot.models import ChatSession, ChatMessage
from langchain_core.prompts import ChatPromptTemplate

# Per-user vector store cache — model loaded only once per user session

\_vector_stores: dict = {}

def get_vector_store(user_id: int) -> DocumentVectorStore:
if user_id not in \_vector_stores:
\_vector_stores[user_id] = DocumentVectorStore(user_id)
return \_vector_stores[user_id]

def summarize_document(chunks) -> str:
if not chunks:
return "No content available to summarize."

    context_text = "\n".join(f"- {c['chunk_text']}" for c in chunks[:25])
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Summarize the document in concise bullet points. "
            "Highlight key tasks, decisions, dates, and action items.",
        ),
        ("human", "Document context:\n{context}"),
    ])
    messages = prompt.format_messages(context=context_text)
    response = get_chat_llm(temperature=0.0).invoke(messages)
    return response.content if hasattr(response, "content") else str(response)

def \_compact_text(value: str) -> str:
return re.sub(r"\s+", "", (value or "").lower())

def \_extract_exact_line_answer(question: str, chunks) -> str:
question_compact = \_compact_text(question).strip("?")
if not question_compact:
return ""

    for chunk in chunks:
        for line in chunk.get('text', '').splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            if question_compact in _compact_text(candidate):
                return candidate
    return ""

class FileUploadView(APIView):
permission_classes = [IsAuthenticated]
parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        file_ext = uploaded_file.name.split('.')[-1].lower()

        # Determine file type
        file_type_map = {
            'pdf': 'pdf',
            'txt': 'txt',
            'docx': 'docx'
        }
        file_type = file_type_map.get(file_ext)

        if not file_type:
            return Response(
                {'error': 'Unsupported file type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove previous versions of same filename so FAISS stays clean.
        # Stale old-chunker entries otherwise pollute retrieval quality.
        existing = UploadedFile.objects.filter(
            user=request.user,
            original_filename=uploaded_file.name
        )
        if existing.exists():
            vs = get_vector_store(request.user.id)
            for old_file in existing:
                vs.delete_file_chunks(old_file.id)
            existing.delete()  # DB cascade removes FileChunk rows too
            # Invalidate cache so fresh index is used next request
            _vector_stores.pop(request.user.id, None)

        # Save file
        db_file = UploadedFile.objects.create(
            user=request.user,
            original_filename=uploaded_file.name,
            file=uploaded_file,
            file_type=file_type,
            file_size=uploaded_file.size,
            is_processed=False
        )

        # Process in background (or here for simplicity)
        try:
            self._process_file(db_file)
            return Response({
                'message': 'File uploaded and processed successfully',
                'file': UploadedFileSerializer(db_file).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            db_file.delete()
            return Response({
                'error': f'Processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_file(self, db_file: UploadedFile):
        """Extract, chunk, embed and index file"""
        # 1. Extract text
        extractor = TextExtractor()
        raw_text = extractor.extract(db_file.file.path, db_file.file_type)

        if not raw_text.strip():
            raise ValueError("No text could be extracted from file")

        # 2. Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk_text(raw_text)

        if not chunks:
            raise ValueError("Could not create chunks from text")

        # 3. Save chunks to DB
        file_chunks_for_vs = []
        for i, chunk_data in enumerate(chunks):
            FileChunk.objects.create(
                uploaded_file=db_file,
                chunk_index=i,
                chunk_text=chunk_data['text'],
                page_number=chunk_data.get('page')
            )
            file_chunks_for_vs.append({
                'text': chunk_data['text'],
                'chunk_index': i,
                'page': chunk_data.get('page')
            })

        # 4. Add to FAISS (use cached store so model loads only once)
        vector_store = get_vector_store(db_file.user.id)
        vector_store.add_chunks(file_chunks_for_vs, db_file.id)

        # 5. Update file status
        db_file.total_chunks = len(chunks)
        db_file.is_processed = True
        db_file.save()

    def get(self, request):
        """List user's uploaded files"""
        files = UploadedFile.objects.filter(user=request.user)
        serializer = UploadedFileSerializer(files, many=True)
        return Response(serializer.data)

class FileDeleteView(APIView):
permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        file = get_object_or_404(UploadedFile, id=file_id, user=request.user)

        vector_store = get_vector_store(request.user.id)
        vector_store.delete_file_chunks(file.id)
        _vector_stores.pop(request.user.id, None)

        # Delete file (cascades to chunks)
        file.delete()

        return Response({'message': 'File deleted successfully'})

class AskQuestionView(APIView):
permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        file_id = serializer.validated_data.get('file_id')
        session_id = request.data.get('session_id')

        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            title = question[:30] + '...' if len(question) > 30 else question
            session = ChatSession.objects.create(user=request.user, title=title)

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=question)

        # Validate file_id if provided
        if file_id:
            get_object_or_404(UploadedFile, id=file_id, user=request.user)

        try:
            vector_store = get_vector_store(request.user.id)
            relevant_chunks = vector_store.search(question, top_k=8, file_id=file_id)

            if not relevant_chunks:
                ans = 'No relevant information found in your documents.'
                ChatMessage.objects.create(session=session, role='bot', content=ans)
                return Response({
                    'answer': ans,
                    'sources': [],
                    'chunks_used': 0,
                    'session_id': session.id
                })

            # 2. Prefer exact context line for symbolic/equation-style questions.
            # This avoids model "general knowledge" overriding document facts.
            ans = _extract_exact_line_answer(question, relevant_chunks)

            if not ans:
                context_text = "\n".join(f"- {c['text']}" for c in relevant_chunks)

                prompt = ChatPromptTemplate.from_messages([
                    (
                        "system",
                        "You are a strict document assistant. Answer ONLY using the provided context. "
                        "If the answer is not explicitly present in context, respond exactly with: "
                        "'Not found in provided documents.'\n\n"
                        "Context:\n{context}",
                    ),
                    ("human", "{input}"),
                ])

                llm = get_chat_llm(temperature=0.0)
                messages = prompt.format_messages(input=question, context=context_text)
                response = llm.invoke(messages)
                ans = response.content if hasattr(response, "content") else str(response)

            ChatMessage.objects.create(session=session, role='bot', content=ans)

            # 3. Format sources
            file_map = {
                f.id: f.original_filename
                for f in UploadedFile.objects.filter(user=request.user)
            }
            sources = []
            for chunk in relevant_chunks:
                sources.append({
                    'file_name': file_map.get(chunk['file_id'], f"File {chunk['file_id']}"),
                    'file_id': chunk['file_id'],
                    'chunk_index': chunk['chunk_index'],
                    'page': chunk.get('page'),
                    'relevance_score': round(chunk['score'], 3)
                })

            return Response({
                'answer': ans,
                'sources': sources,
                'chunks_used': len(relevant_chunks),
                'session_id': session.id
            })

        except Exception as e:
            return Response({
                'error': f'Failed to generate answer: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RebuildDocIndexView(APIView):
"""
Wipe the FAISS document index and re-process all files from source.
This re-extracts text, re-chunks with current settings, and re-embeds -
fixing any stale data left by previous chunker versions.
"""
permission_classes = [IsAuthenticated]

    def post(self, request):
        import shutil
        from django.conf import settings as dj_settings

        user = request.user
        # Evict cached store.
        _vector_stores.pop(user.id, None)

        # Wipe FAISS files on disk so we start completely fresh.
        index_dir = os.path.join(str(dj_settings.BASE_DIR), 'faiss_indexes', f'user_lc_{user.id}')
        if os.path.exists(index_dir):
            shutil.rmtree(index_dir)

        # Re-process every file end-to-end: extract → chunk → embed.
        vs = get_vector_store(user.id)
        files = UploadedFile.objects.filter(user=user, is_processed=True)
        total_chunks = 0
        errors = []

        for f in files:
            try:
                # Delete stale DB chunks for this file.
                f.chunks.all().delete()

                # Re-extract raw text from the stored file.
                extractor = TextExtractor()
                raw_text = extractor.extract(f.file.path, f.file_type)
                if not raw_text.strip():
                    errors.append(f'{f.original_filename}: no text extracted')
                    continue

                # Re-chunk with the current (fixed) chunker.
                chunker = TextChunker()
                chunks = chunker.chunk_text(raw_text)
                if not chunks:
                    errors.append(f'{f.original_filename}: chunking produced no chunks')
                    continue

                # Save fresh chunks to DB and build FAISS vectors.
                file_chunks = []
                for i, chunk_data in enumerate(chunks):
                    FileChunk.objects.create(
                        uploaded_file=f,
                        chunk_index=i,
                        chunk_text=chunk_data['text'],
                        page_number=chunk_data.get('page')
                    )
                    file_chunks.append({
                        'text': chunk_data['text'],
                        'chunk_index': i,
                        'page': chunk_data.get('page')
                    })

                vs.add_chunks(file_chunks, f.id)
                f.total_chunks = len(chunks)
                f.save()
                total_chunks += len(chunks)

            except Exception as e:
                errors.append(f'{f.original_filename}: {str(e)}')

        response_data = {
            'message': f'Rebuilt index for {files.count()} file(s) with {total_chunks} chunks.',
            'files': files.count(),
            'chunks': total_chunks,
        }
        if errors:
            response_data['errors'] = errors
        return Response(response_data)

class FileSummaryView(APIView):
permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        file = get_object_or_404(UploadedFile, id=file_id, user=request.user)

        if not file.is_processed:
            return Response({
                'error': 'File is still being processed'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get chunks
        chunks = list(file.chunks.values('chunk_index', 'chunk_text'))

        # Generate summary
        summary = summarize_document(chunks)

        return Response({
            'file_name': file.original_filename,
            'summary': summary,
            'total_chunks': file.total_chunks
        })

---

# Session Handoff: Chatbot Concerns and Future Plan (2026-03-18)

This section captures the key concerns discussed in chat so future sessions can continue without losing context.

## Project Direction (FYP Scope)

- Keep scope as one Student Academic Chatbot.
- Do not expand into separate admin chatbot and teacher chatbot for FYP.
- Focus user-facing intents on:
  - Assignment reminders and deadline help
  - Quiz concern handling (result explanation, wrong-answer help)
  - Attendance status and alerts
  - Document-based student support (uploaded docs + RAG)

## Key Code Review Concerns

1. Security concern: FAISS load uses `allow_dangerous_deserialization=True`.
   - Risk: unsafe deserialization if index files are tampered.

2. Request latency concern: file upload endpoint processes extraction/chunking/embedding synchronously.
   - Risk: slow response and timeout under bigger files or concurrent users.

3. Error-handling concern: broad `except` + `pass` or `print` in indexing and signal paths.
   - Risk: hidden index inconsistencies and difficult debugging.

4. Cache lifecycle concern: in-memory per-user stores/engines are process-local and partially invalidated.
   - Risk: stale retrieval state and uneven behavior after reload/restart.

5. Hardcoded configuration concern:
   - Temperature, history limits, top-k, similarity threshold, chunk size/overlap fallback, embedding device path are fixed in code.
   - Need migration to settings/env for future tuning.

6. Domain coupling concern:
   - Current local engine is strongly tied to Todo entities.
   - FYP chatbot target is student academic entities (assignments/quizzes/attendance/materials).

7. Duplication concern:
   - Repeated extractor-style code sections increase maintenance overhead.

## Hardcoded Items Identified

- `DEFAULT_TEMPERATURE = 0.7`
- `MAX_CONTEXT_RESULTS = 10`
- `MIN_SIMILARITY_SCORE = 0.2`
- `HISTORY_LIMIT = 12`
- Document search `top_k=8`
- Embedding model fallback `sentence-transformers/all-MiniLM-L6-v2`
- Embedding device `cpu`

These are acceptable for MVP, but should be moved to centralized configuration before final hardening.

## What Is Good Already

- Clear module split (engine, memory, sessions/messages, file RAG pipeline).
- Source-aware responses for document QA.
- User-scoped data access patterns in views.
- Rebuild-index endpoint exists for recovery scenarios.

## Priority Plan (Must/Should/Could)

### Must Fix (for reliability and FYP defense)

1. Move key tuning values to Django settings/env.
2. Replace unsafe FAISS deserialization usage or protect index trust boundary.
3. Replace `print`/silent catches with structured logging and explicit fallback handling.
4. Align retrieval tools with student domain data (assignments/quizzes/attendance) instead of Todo-only logic.

### Should Fix (next)

1. Move heavy document processing to background worker (Celery/RQ).
2. Add cache invalidation policy notes (on upload/delete/rebuild/login).
3. Add confidence/fallback policy: when evidence is weak, return safe answer and ask clarifying question.

### Could Fix (later)

1. Add observability metrics: retrieval hit rate, latency, errors.
2. Add answer citations in all chatbot paths.
3. Add intent routing layer for cleaner student query handling.

## Final Recommended FYP Positioning

- Product statement: one domain-specific Student Academic Chatbot.
- Core capability set for demo and report:
  1. Assignment deadline reminders
  2. Quiz-related concern support
  3. Attendance insight
  4. Document-grounded Q&A using LangChain + FAISS

This keeps scope realistic and defendable while still showing meaningful AI engineering.

Best framing:
One Student Academic Chatbot with multiple intents, not many separate features.

Recommended scope (balanced and defendable)

Core intent set (must have)

Assignments: upcoming, overdue, subject-wise

Quizzes: upcoming quiz, last attempt summary, wrong-answer explanation

Attendance: current percentage, risk alert

General student help: explain topic simply (ChatGPT-like but academic-safe)

Data sources

LMS APIs and DB for real-time facts (assignment, quiz, attendance)

Document upload plus RAG using LangChain for notes or PDFs

Small rule engine for reminders and alerts

Chatbot behavior model

Intent router first:
Assignment query, quiz query, attendance query, document doubt, general study query

Tool call layer:
Fetch live LMS data for factual answers,,RAG layer:
Use uploaded documents for content-based doubts

Fallback:
If no data found, clearly say not found and suggest next action

Important guardrails (very important for viva quality)

Never hallucinate assignment deadlines

Always mention source type:
from LMS records or from uploaded document

If confidence low, ask clarifying question

Keep this out of MVP

Teacher assistant

Admin chatbot

Plagiarism and auto-grading

Complex recommendation engine,,,
Scope freeze kar do now
Student chatbot only, with 4 intents:
assignment deadlines, quiz help, attendance insight, document Q&A.

Intent-first architecture banao
Pehle user query ko intent me map karo, phir:
LMS data tool call ya RAG call ya LLM response.
Is se hallucination bohot kam hogi.

Factual vs generative split clear rakho
Deadlines/attendance/quiz score: always database se.
Explanation/simplification: LLM se.

Ek strong guardrail add karo
Agar evidence low ho to direct bolo:
“Data me clear answer nahi mila, ye nearest info hai…”
Ye viva me strong point banega.

Evaluation sheet abhi se start karo
At least:
intent accuracy, response latency, source-grounded answer rate, user satisfaction (simple form).

Demo-ready flow prepare karo
Live demo script:
“upcoming assignments” -> “attendance risk” -> “quiz wrong answer explain” -> “document doubt answer with source”.

Time bachane ke liye “nice-to-have” skip karo
No teacher/admin bot, no plagiarism, no complex recommender in MVP.

---

# Session Handoff: Existing LLM Service Context (Verified from Workspace)

This section records the current backend AI integration so future sessions can continue without re-discovery.

## Current Reusable LLM Architecture

- A central provider router already exists in [Project/ai_core/services/llm_provider.py](Project/ai_core/services/llm_provider.py).
- Quiz generation does not call providers directly; it calls one reusable function:
  - `call_llm(...)` from [Project/ai_core/services/llm_provider.py](Project/ai_core/services/llm_provider.py)
  - used in [Project/ai_core/services/quiz_generator.py](Project/ai_core/services/quiz_generator.py)
- This is the correct reusable pattern for future chatbot features.

## Provider Switching Strategy (Env-Driven)

- Provider selection is environment-driven:
  - `AI_PROVIDER` supports `pollin` / `pollinations` / `gemini`
  - `AI_MODEL` controls model name per provider
  - `AI_FALLBACK_PROVIDER` is supported for automatic fallback
- Current project configuration is using Pollinations flow with OpenAI-compatible chat endpoint semantics.

## Pollinations Integration (Current)

- Pollinations endpoint base default is set inside provider service and can be overridden with env.
- Auth is expected via `POLLINATIONS_API_KEY`.
- JSON-oriented responses are enforced at provider/prompt level (including strict prompts and response parsing helpers).
- Provider service includes retry logic, retryable status handling, and custom error mapping.

## Gemini Integration (Current)

- Gemini path exists as alternate provider in same router.
- Uses `GEMINI_API_KEY` (or fallback generic `AI_API_KEY`) and supports `GEMINI_MODEL` override.
- Same `call_llm(...)` contract is preserved, so switching provider does not require quiz service rewrites.

## Why This Matters for Next Chatbot Work

- For student chatbot implementation, reuse this same `call_llm(...)` router pattern.
- Do not hardcode provider calls in chatbot/business services.
- Keep all provider changes in env + router only.
- This aligns with the project goal: future provider swap with minimal code changes.

## Important Security/Operations Note

- Keep API keys only in env files and secret managers; never in source/docs shared externally.
- If any key was exposed during development, rotate it before demo/deployment.

## Immediate Development Rule for Future Sessions

When adding chatbot intents (assignment/quiz/attendance/doc Q&A):

1. Use LMS/domain tool functions for data retrieval.
2. Use `call_llm(...)` only for generation/explanation.
3. Keep provider config/env-driven.
4. Preserve one router abstraction for maintainability.

# chatbot.py views

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models.chatbot import ChatSession, ChatMessage, ChatMetric
from ..serializers.chatbot import ChatSessionSerializer, ChatMessageSerializer
from ..services.chat_orchestrator import orchestrate_response
import logging

logger = logging.getLogger(**name**)

class StudentChatView(APIView):
"""
Main endpoint for student academic chatbot.
"""
permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('message')
        session_id = request.data.get('session_id')

        if not query:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_VALUE)

        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user, title=query[:50])

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=query)

        # Get history for context (optional, last 5 messages)
        history_msgs = ChatMessage.objects.filter(session=session).order_by('-created_at')[:5]
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(history_msgs)
        ]

        try:
            # Plan tool routing and get result
            result = orchestrate_response(request.user, query, history=history)

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

            # NEW: Save ChatMetric
            ChatMetric.objects.create(
                message=bot_msg,
                is_grounded=(result.get('source') != "LLM General")
            )

            return Response({
                'session_id': str(session.id),
                'message': ChatMessageSerializer(bot_msg).data,
                'at_risk': result.get('at_risk', False),
                'data': result.get('data') # Optional domain data
            })

        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return Response({
                'error': 'Chatbot encountered an issue.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentChatSessionsView(APIView):
permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user)
        return Response(ChatSessionSerializer(sessions, many=True).data)

    def delete(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# quizes.py tools

from lms_cors.models.grading import QuizAttempt, Quiz, QuizQuestion
from django.db.models import Max
from django.utils import timezone

def get_last_quiz_attempt(student_id):
"""
Returns summary of the very last submitted quiz attempt.
"""
last_attempt = QuizAttempt.objects.filter(student_id=student_id).order_by('-started_at').first()
if not last_attempt:
return None

    return {
        "id": str(last_attempt.id),
        "quiz_title": last_attempt.quiz.title if last_attempt.quiz else "Unknown",
        "score": float(last_attempt.score or 0),
        "max_marks": float(last_attempt.quiz.total_marks or 0),
        "status": last_attempt.status,
        "date": last_attempt.started_at.strftime("%Y-%m-%d"),
        "answers": last_attempt.answers # Map of question_id -> actual_answer
    }

def explain_quiz_mistakes(student_id, attempt_id=None):
"""
Examines an attempt, identifies wrong answers, and gets context
for explanation.
"""
if attempt_id:
attempt = QuizAttempt.objects.filter(student_id=student_id, id=attempt_id).first()
else:
attempt = QuizAttempt.objects.filter(student_id=student_id).order_by('-started_at').first()

    if not attempt or not attempt.answers:
        return None

    # Identify wrong questions for MCQ types (simple heuristic: comparison)
    # This requires more metadata from question models in a real setup.
    # For now, we return attempt metadata to feed the LLM.

    # Fetch actual questions for the quiz
    questions = QuizQuestion.objects.filter(quiz=attempt.quiz).prefetch_related('options')

    mistakes = []
    for q in questions:
        user_answer = attempt.answers.get(str(q.id))
        if not user_answer:
            continue

        # Check correctness (MCQ helper)
        if q.question_type == 'mcq':
            correct_opt = q.options.filter(is_correct=True).first()
            is_correct = (user_answer == (correct_opt.option_text if correct_opt else None))
            if not is_correct:
                mistakes.append({
                    "id": str(q.id),
                    "question_text": q.question_text,
                    "your_answer": user_answer,
                    "correct_answer": correct_opt.option_text if correct_opt else "N/A",
                    "explanation": q.explanation or "No explanation available."
                })

    return mistakes[:3] # Limit mistakes to focus conversation

# docs.py tools

from ..rag_utils import get_embeddings, get_faiss_cls, normalize_similarity_score
from ...models.chatbot import UploadedFile, FileChunk
from ..constants import FAISS_INDEX_DIR, CHAT_TOP_K, CHAT_MIN_SIMILARITY_SCORE
import os

def query*documents(user_id, question):
"""
Searches the user’s uploaded documents for an answer.
Returns chunks with context and confidence.
"""
index_dir = os.path.join(FAISS_INDEX_DIR, f'user_docs_lc*{user_id}')
faiss_cls = get_faiss_cls()
embeddings = get_embeddings()

    # Try to load existing user index
    if not os.path.exists(os.path.join(index_dir, "index.faiss")):
        return {"status": "no_index", "results": []}

    try:
        vector_store = faiss_cls.load_local(
            index_dir, embeddings, allow_dangerous_deserialization=True
        )

        # Search with similarity score
        results = vector_store.similarity_search_with_score(question, k=CHAT_TOP_K)

        filtered_results = []
        for doc, score in results:
            # Normalize and check threshold
            norm_score = normalize_similarity_score(score)
            if norm_score >= CHAT_MIN_SIMILARITY_SCORE:
                # Meta usually contains doc_id and chunk_id for citations
                filtered_results.append({
                    "text": doc.page_content,
                    "score": round(norm_score, 2),
                    "file_name": doc.metadata.get("original_filename", "Uploaded File"),
                    "page": doc.metadata.get("page_number", "N/A")
                })

        return {
            "status": "success",
            "results": filtered_results,
            "confidence": max([r['score'] for r in filtered_results]) if filtered_results else 0
        }
    except Exception as e:
        print(f"Document search failed: {e}")
        return {"status": "error", "message": str(e), "results": []}

# attendence.py tools

from lms_cors.models.attendance import Attendance
from django.db.models import Count, Q
from ..constants import ATTENDANCE_RISK_THRESHOLD

def get_attendance_summary(student_id):
"""
Returns summary of current attendance percentage across all subjects.
"""
records = Attendance.objects.filter(student_id=student_id)
if not records.exists():
return None

    total = records.count()
    present = records.filter(Q(status='present') | Q(status='late')).count()

    percentage = (present / total * 100) if total > 0 else 0

    return {
        "percentage": round(percentage, 2),
        "total": total,
        "present": present,
        "absent": records.filter(status='absent').count(),
        "is_at_risk": percentage < ATTENDANCE_RISK_THRESHOLD,
        "risk_threshold": ATTENDANCE_RISK_THRESHOLD,
        "records_list": [
            {
                "date": str(r.session_date),
                "status": r.status,
                "subject": r.subject.code if r.subject else "N/A"
            } for r in records[:5]
        ]
    }

# assignments.py tools

from lms_cors.models.assignments import Assignment, SubmissionHistory
from django.utils import timezone
from django.db.models import Q

def get_upcoming_assignments(student_id):
"""
Lists all assignments not yet submitted and due in the future.
"""
now = timezone.now() # Find all assignments for student's subjects (if enrollment data exists) # Simple query for all assignments as an MVP starting point
assignments = Assignment.objects.filter(due_date\_\_gt=now).order_by('due_date')

    # Filter out submitted ones
    submitted_ids = SubmissionHistory.objects.filter(student_id=student_id).values_list('assignment_id', flat=True)
    upcoming = assignments.exclude(id__in=submitted_ids)

    return [
        {
            "id": str(a.id),
            "title": a.title,
            "subject": a.subject.code if a.subject else "Unknown",
            "due_date": a.due_date.strftime("%Y-%m-%d %H:%M"),
            "status": "upcoming"
        } for a in upcoming[:5]
    ]

def get_overdue_assignments(student_id):
"""
Lists all assignments where due date has passed without submission.
"""
now = timezone.now()
overdue = Assignment.objects.filter(due_date**lt=now).order_by('-due_date')
submitted_ids = SubmissionHistory.objects.filter(student_id=student_id).values_list('assignment_id', flat=True)
overdue = overdue.exclude(id**in=submitted_ids)

    return [
        {
            "id": str(a.id),
            "title": a.title,
            "subject": a.subject.code if a.subject else "Unknown",
            "due_date": a.due_date.strftime("%Y-%m-%d"),
            "status": "overdue"
        } for a in overdue[:5]
    ]

# reg-utilis.py services

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from django.conf import settings

def get_embeddings():
"""Returns the default embedding model for the academic chatbot.""" # Using a lightweight, high-quality open model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
return HuggingFaceEmbeddings(
model_name=model_name,
model_kwargs=model_kwargs,
encode_kwargs=encode_kwargs
)

def get_faiss_cls():
"""Returns the FAISS class for vector storage."""
return FAISS

def process_document_to_chunks(text, filename="document"):
"""Splits a document text into manageable chunks for RAG."""
text_splitter = RecursiveCharacterTextSplitter(
chunk_size=1000,
chunk_overlap=100,
length_function=len,
add_start_index=True,
)
chunks = text_splitter.create_documents([text], metadatas=[{"source": filename}])
return chunks

def build_vector_store(documents, store_path):
"""Builds and saves a FAISS vector store from documents."""
embeddings = get_embeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
vectorstore.save_local(store_path)
return vectorstore

def load_vector_store(store_path):
"""Loads an existing FAISS vector store."""
if not os.path.exists(store_path):
return None
embeddings = get_embeddings()
return FAISS.load_local(store_path, embeddings, allow_dangerous_deserialization=True)

def normalize_similarity_score(score):
"""
Normalizes a FAISS L2 score (lower is better) to a [0, 1] similarity score (higher is better).
Since L2 scores depend on the embedding dimension, we apply a safe exponential mapping.
"""
import math
try: # Heuristic for MiniLM-L6 (384-dim). Adjust as needed. # L2 score 0 -> similarity 1. # L2 score 1 -> similarity ~0.37. # L2 score 2 -> similarity ~0.13.
return math.exp(-score)
except:
return 0.0

# intent-router.py services

import json
from .llm_provider import call_llm

INTENT_ROUTER_PROMPT = """
Analyze the user query and classify it into one of the following academic intents for a student:

1. assignment - Questions about upcoming, overdue, or subject-wise assignments, deadlines, or submissions.
2. quiz - Questions about last quiz attempts, scores, wrong-answer explanations, or upcoming quizzes.
3. attendance - Questions about current attendance percentage, status, or attendance alerts/risks.
4. rag - Questions that seem to refer to notes, specific documents, or personal academic content likely to be in uploaded documents.
5. general - General academic questions, study tips, or greetings.

Return only a JSON object with:

- "intent": The primary category from the list above.
- "slots": A dictionary of extracted entities like {"subject": "Math", "date": "next week"}, or {} if none.
- "reason": A brief 1-sentence reason for this classification.

User Query: "{query}"
"""

def classify_intent(query: str):
"""
Classifies the user query into a domain intent.
Uses pattern matching first for fast routing, falls back to LLM.
"""
query_lower = query.lower()

    # Rule-based fast pass
    query_lower = query.lower()
    slots = {}

    # Extract common slots (simple pattern matching)
    if "overdue" in query_lower:
        slots["type"] = "overdue"
    elif "upcoming" in query_lower:
        slots["type"] = "upcoming"

    if any(word in query_lower for word in ['assignment', 'homework', 'deadline', 'submit']):
        return {"intent": "assignment", "slots": slots, "confidence": 1.0}
    if any(word in query_lower for word in ['attendance', 'present', 'absent', 'percentage']):
        return {"intent": "attendance", "slots": slots, "confidence": 1.0}
    if any(word in query_lower for word in ['quiz', 'test', 'score', 'mark', 'attempt', 'wrong answer']):
        return {"intent": "quiz", "slots": slots, "confidence": 1.0}
    if any(word in query_lower for word in ['document', 'pdf', 'notes', 'tell me about', 'what does it say']):
        return {"intent": "rag", "slots": slots, "confidence": 0.8}

    # LLM Fallback for ambiguous queries
    prompt = INTENT_ROUTER_PROMPT.format(query=query)
    try:
        response = call_llm(prompt, temperature=0.0)
        # Attempt to clean response if it contains markdown markers
        cleaned = response.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned)
        return {
            "intent": data.get("intent", "general"),
            "slots": data.get("slots", {}),
            "confidence": 0.7 # Mixed confidence for LLM classification
        }
    except Exception as e:
        print(f"Intent classification failed: {e}")
        return {"intent": "general", "slots": {}, "confidence": 0.5}

# constants.py services

from django.conf import settings
import os

# Evaluation & Metrics

CHAT_EVAL_ENABLED = True
CHAT_MIN_SIMILARITY_SCORE = 0.2
CHAT_HISTORY_LIMIT = 10

# RAG Configuration

CHAT_CHUNK_SIZE = 800
CHAT_CHUNK_OVERLAP = 100
CHAT_TOP_K = 5

# Domain Rules

ATTENDANCE_RISK_THRESHOLD = 75.0 # Percentage

# Paths

FAISS_INDEX_DIR = os.path.join(settings.BASE_DIR, 'faiss_indexes')
DOCS_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')

# Confidence Fallback

LOW_CONFIDENCE_THRESHOLD = 0.4
LOW_CONFIDENCE_MESSAGE = "Data me clear answer nahi mila, ye nearest info hai..."

# chat-orchestrator.py services

from .intent_router import classify_intent
from .llm_provider import call_llm
from .tools.assignments import get_upcoming_assignments, get_overdue_assignments
from .tools.quizzes import get_last_quiz_attempt, explain_quiz_mistakes
from .tools.attendance import get_attendance_summary
from .tools.docs import query_documents
from .constants import LOW_CONFIDENCE_THRESHOLD, LOW_CONFIDENCE_MESSAGE
from lms_cors.models import Student
from django.core.cache import cache
import time
import logging

logger = logging.getLogger(**name**)

def student_assignment_tool(user, student_id, query, slots):
upcoming = get_upcoming_assignments(student_id)
overdue = get_overdue_assignments(student_id)

    if not upcoming and not overdue:
        return {"text": LOW_CONFIDENCE_MESSAGE, "source": "LMS Records", "data": {"upcoming": [], "overdue": []}}

    text = summarize_assignments(upcoming, overdue)
    return {"text": text, "source": "LMS Records", "data": {"upcoming": upcoming, "overdue": overdue}}

def student_attendance_tool(user, student_id, query, slots):
summary = get_attendance_summary(student_id)
if not summary or summary['total'] == 0:
return {"text": LOW_CONFIDENCE_MESSAGE, "source": "LMS Records", "data": summary}

    text = compose_attendance_response(summary)
    return {
        "text": text,
        "source": "LMS Records",
        "at_risk": summary.get("is_at_risk", False),
        "data": summary
    }

def student_quiz_tool(user, student_id, query, slots):
if any(word in query.lower() for word in ['mistake', 'wrong', 'explain', 'why']):
mistakes = explain_quiz_mistakes(student_id)
if mistakes:
text = draft_mistakes_explanation(mistakes)
return {"text": text, "source": "LMS + LLM Analysis", "data": mistakes}
return {"text": LOW_CONFIDENCE_MESSAGE, "source": "LMS Records"}

    last_attempt = get_last_quiz_attempt(student_id)
    if last_attempt:
        text = f"Your last quiz '{last_attempt['quiz_title']}' on {last_attempt['date']} was {last_attempt['status']}. Score: {last_attempt['score']}/{last_attempt['max_marks']}."
        return {"text": text, "source": "LMS Records", "data": last_attempt}
    return {"text": LOW_CONFIDENCE_MESSAGE, "source": "LMS Records"}

def doc_rag_tool(user, student_id, query, slots):
docs_res = query_documents(user.id, query)
if docs_res["results"]:
context_parts = []
citations_list = []
for r in docs_res['results']:
context_parts.append(f"- {r['text']} (Source: {r['file_name']}, Page: {r.get('page', 'N/A')})")
citations_list.append(f"- {r['file_name']} (Page: {r.get('page', 'N/A')})")

        context = "\n".join(context_parts)
        llm_prompt = f"Using the provided context from the user's uploaded documents, answer their question precisely. Always mention which document or page contains the info if available. Query: {query}\n\nContext:\n{context}"
        text = call_llm(llm_prompt)

        # Add formatted citations
        unique_citations = list(set(citations_list))
        citation_text = "\n\nSources:\n" + "\n".join(unique_citations)
        return {
            "text": text + citation_text,
            "source": "Uploaded Document",
            "citation": docs_res["results"],
            "confidence": docs_res["confidence"]
        }

    llm_ans = call_llm(f"The following question was asked, but no relevant document context was found. Answer it in a general academic way: {query}")
    return {"text": f"{LOW_CONFIDENCE_MESSAGE}\n\n{llm_ans}", "source": "LLM Fallback"}

# Tool Registry for Role-based access

TOOLS = {
"student": {
"assignment": student_assignment_tool,
"attendance": student_attendance_tool,
"quiz": student_quiz_tool,
"rag": doc_rag_tool,
},
"teacher": { # Future-proof: teacher tools would go here
}
}

def orchestrate_response(user, query, history=None):
"""
Orchestrator with Caching and Role-based Tool Registry.
"""
start_time = time.time()

    # Check cache first
    cache_key = f"chat_res_{user.id}_{hash(query)}"
    cached_res = cache.get(cache_key)
    if cached_res:
        logger.info(f"Cache hit for chat query: {query[:20]}...")
        return cached_res

    # Determine role (assuming student for now as per instructions)
    role = "student" # Default to student for MVP
    student = Student.objects.filter(user=user).first()
    student_id = student.id if student else None

    # Analyze intent
    intent_data = classify_intent(query)
    intent = intent_data.get("intent")
    slots = intent_data.get("slots", {})

    # Default response structure
    res_data = {
        "text": "",
        "source": "LLM",
        "intent": intent,
        "latency": 0,
        "citation": [],
        "confidence": intent_data.get("confidence", 0.5),
        "at_risk": False,
        "data": None
    }

    # Dispatch to tool from registry
    tool_func = TOOLS.get(role, {}).get(intent)

    if tool_func and student_id:
        try:
            tool_output = tool_func(user, student_id, query, slots)
            res_data.update(tool_output)
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            res_data["text"] = "I encountered an error trying to fetch that information for you."
    elif intent == "general" or not tool_func:
        res_data["text"] = call_llm(query, history=history)
        res_data["source"] = "LLM General"

    # Add Visible Source Tag
    if res_data["text"] and res_data["source"]:
        # Don't double tag if already tagged by tool
        if "(Source:" not in res_data["text"]:
            res_data["text"] += f"\n\n(Source: {res_data['source']})"

    res_data["latency"] = round(time.time() - start_time, 2)

    # Cache the result for 5 minutes
    cache.set(cache_key, res_data, 300)

    return res_data

# Response Composers (Keep for use by tools)

def summarize_assignments(upcoming, overdue):
text = ""
if upcoming:
text += f"You have {len(upcoming)} upcoming assignments:\n"
text += "\n".join([f"- {a['title']} ({a['subject']}) due on {a['due_date']}" for a in upcoming])
if overdue:
text += "\n\n" if text else ""
text += f"⚠️ You have {len(overdue)} OVERDUE assignments:\n"
text += "\n".join([f"- {a['title']} ({a['subject']}) was due on {a['due_date']}" for a in overdue])
return text

def compose_attendance_response(summary):
risk_msg = " (⚠️ Risk: Below threshold)" if summary['is_at_risk'] else " (Safe)"
text = f"Your cumulative attendance is {summary['percentage']}%{risk_msg}. Total sessions: {summary['total']}, Present/Late: {summary['present']}, Absent: {summary['absent']}."
return text

def draft_mistakes_explanation(mistakes): # Pass mistakes to LLM to explain concepts nicely
context = "\n".join([f"Q: {m['question_text']}\nUser Answer: {m['your_answer']}\nCorrect Answer: {m['correct_answer']}\nInitial Explanation: {m['explanation']}" for m in mistakes])

    prompt = f"""
    The student made mistakes in their last quiz. Analyze these mistakes and provide a structured explanation.
    For each mistake, strictly follow this structure:

    1. Concept: [Name of the core academic concept]
    2. Mistake: [Briefly why the student's answer was incorrect]
    3. Correct Logic: [Step-by-step reasoning for the right answer]

    Keep it encouraging and academic.

    Mistakes Data:
    {context}
    """
    return call_llm(prompt)

# chatbot.py models

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class ChatSession(models.Model):
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
title = models.CharField(max_length=255, default="New Chat")
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class ChatMessage(models.Model):
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
role = models.CharField(max_length=10) # 'user' or 'bot'
content = models.TextField()
intent = models.CharField(max_length=50, blank=True, null=True)
source = models.CharField(max_length=100, blank=True, null=True)
latency = models.FloatField(default=0.0)
confidence = models.FloatField(default=0.0)
created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

class ChatMetric(models.Model):
"""
Stores evaluation metrics for each interaction
"""
message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, related_name='metrics')
is_grounded = models.BooleanField(default=True) # Factual correctness check
user_satisfaction = models.IntegerField(null=True, blank=True) # 1-5 rating
feedback_text = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_metrics'

class UploadedFile(models.Model):
"""
Specifically for chatbot document Q&A if separate from general LMS materials.
Or we can just store references to lms_cors.Material.
Let's use references for the MVP.
"""
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
user = models.ForeignKey(User, on_delete=models.CASCADE)
material = models.ForeignKey('lms_cors.Material', on_delete=models.CASCADE, null=True, blank=True)
filename = models.CharField(max_length=255)
index_status = models.CharField(max_length=20, default='pending') # pending, indexed, failed
created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_uploaded_files'

class FileChunk(models.Model):
"""
Metadata for searchable chunks if we need DB tracking beyond FAISS meta.
"""
file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='chunks')
chunk_index = models.IntegerField()
content_summary = models.TextField() # For quick preview

    class Meta:
        db_table = 'chat_file_chunks'
