<template>
  <div class="student-ai-chatbot shadow">
    <Transition name="slide-up">
      <div v-if="isOpen" class="chat-window card border-0 shadow-2xl overflow-hidden d-flex flex-row"
           :class="{ 'fullscreen': isFullScreen, 'chat-dark-theme': isDarkMode }">
           
        <ChatSidebar
          :sessions="sessions"
          :currentSessionId="currentSessionId"
          :editingSessionId="editingSessionId"
          :renamingSessionId="renamingSessionId"
          v-model:renameDraft="renameDraft"
          :isDarkMode="isDarkMode"
          @start-new-chat="startNewChat"
          @load-session="(id) => loadSession(id, scrollToBottom)"
          @start-rename="startRenameSession"
          @submit-rename="submitRenameSession"
          @cancel-rename="cancelRenameSession"
          @delete-session="handleDeleteSession"
          @toggle-dark-mode="toggleDarkMode"
          @set-rename-ref="renameInputRef = $event"
        />

        <div class="chat-main d-flex flex-column flex-grow-1 bg-white">
          <div class="chat-header p-3 d-flex align-items-center justify-content-between flex-shrink-0">
            <div class="d-flex align-items-center gap-2">
              <div class="avatar-sm assistant-header-avatar text-white rounded-3 shadow-sm d-flex align-items-center justify-content-center">
                <i class="bi bi-mortarboard-fill fs-6"></i>
              </div>
              <div>
                <h6 class="mb-0 fw-bold small">Academic Assistant</h6>
                <div class="d-flex align-items-center gap-1">
                   <span class="bg-success rounded-circle" style="width:6px; height:6px;"></span>
                   
                </div>
              </div>
            </div>
            <div class="d-flex align-items-center gap-2">
               <button @click="shareChat" class="btn btn-link link-secondary p-1" title="Share Chat"><i class="bi bi-share"></i></button>
               <button @click="toggleFullScreen" class="btn btn-link link-secondary p-1" :title="isFullScreen ? 'Exit Full Screen' : 'Full Screen'"><i :class="isFullScreen ? 'bi bi-fullscreen-exit' : 'bi bi-arrows-fullscreen'"></i></button>
               <button @click="toggleChat" class="btn btn-link link-dark p-1 text-decoration-none" title="Close"><i class="bi bi-x-lg"></i></button>
            </div>
          </div>

          <div class="d-flex flex-column flex-grow-1 min-vh-0 w-100 h-100" :class="{ 'justify-content-center pb-5': messages.length === 0 }">
             
            <div class="chat-body p-0 overflow-auto d-flex flex-column w-100" @scroll="handleChatScroll" :class="messages.length === 0 ? 'flex-grow-0 overflow-hidden' : 'flex-grow-1'" ref="messageBox">
              <div v-if="messages.length === 0" class="empty-chat d-flex flex-column align-items-center justify-content-center w-100 mx-auto py-4 px-4 mb-1 mt-5 pt-5" style="max-width: 880px;">
                 <h3 class="fw-semibold text-dark mb-4" style="font-size: 2.2rem;">What's on the agenda today?</h3>
                 <div class="d-flex flex-wrap justify-content-center gap-3 px-3 w-100 mb-4">
                    <button @click="inputQuery = 'What assignments are due?'" class="btn btn-outline-secondary rounded-pill px-4 py-2 bg-white text-dark fw-medium border-light-subtle shadow-sm hover-shadow-md transition-all">Assignments</button>
                    <button @click="inputQuery = 'Check my attendance'" class="btn btn-outline-secondary rounded-pill px-4 py-2 bg-white text-dark fw-medium border-light-subtle shadow-sm hover-shadow-md transition-all">Attendance</button>
                 </div>
              </div>

              <div v-for="(msg, index) in messages" :key="index" :id="`chat-msg-${index}`" class="message-row w-100 px-4 py-3">
              <div class="max-width-chat mx-auto d-flex gap-3 align-items-end"
                   v-if="!(msg.role === 'user' && editSourceIndex === index)"
                   :class="msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'">
                <div v-if="msg.role !== 'user'" class="avatar-msg assistant-avatar rounded-circle shadow-sm d-flex align-items-center justify-content-center flex-shrink-0">
                  <i class="bi bi-mortarboard-fill"></i>
                </div>
                <div class="message-content-wrap" :class="msg.role === 'user' ? 'user-content-wrap' : 'assistant-content-wrap'">
                  <div class="message-bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'">
                    <div v-if="msg.docName" class="mb-2 d-inline-block bg-success text-white border border-success border-opacity-25 rounded-3 px-2 py-1 extra-tiny">
                      <i class="bi bi-file-earmark-text me-1"></i> {{ msg.docName }}
                    </div>
                    <div class="markdown-body small text-dark line-height-relaxed" v-html="formatMessage(msg.content)"></div>
                  </div>
                  <div v-if="msg.role === 'user'" class="message-actions-bottom d-flex align-items-center gap-2">
                    <button
                      @click="copyMessage(msg.content, index)"
                      class="btn btn-link p-0 message-action-btn"
                      title="Copy"
                    >
                      <i :class="copiedMessageIndex === index ? 'bi bi-check2' : 'bi bi-copy'"></i>
                    </button>
                    <button
                      @click="editAndResend(index)"
                      class="btn btn-link p-0 message-action-btn"
                      title="Edit and resend"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </button>
                  </div>
                </div>
                <div v-if="msg.role === 'user'" class="d-flex flex-column align-items-end gap-1 flex-shrink-0">
                  <div class="avatar-msg user-avatar rounded-circle shadow-sm d-flex align-items-center justify-content-center">
                    <i class="bi bi-person-fill"></i>
                  </div>
                </div>
              </div>

              <div
                v-if="msg.role === 'user' && editSourceIndex === index"
                class="max-width-chat mx-auto d-flex justify-content-end mt-2"
              >
                <div class="inline-edit-composer w-100">
                  <textarea
                    ref="inlineEditInput"
                    v-model="inlineEditQuery"
                    @keydown.enter.exact.prevent="handleInlineEditSend"
                    rows="3"
                    class="form-control border-0 shadow-none bg-transparent small inline-edit-input"
                    placeholder="Edit your message"
                    :disabled="loading"
                    style="min-height: 70px; resize: vertical;"
                  ></textarea>
                  <div class="inline-edit-actions d-flex justify-content-end gap-2">
                    <button
                      @click="cancelEditResend"
                      class="btn btn-sm inline-btn-cancel"
                      :disabled="loading"
                    >
                      Cancel
                    </button>
                    <button
                      @click="handleInlineEditSend"
                      class="btn btn-sm inline-btn-send"
                      :disabled="loading || !inlineEditQuery.trim()"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="showThinkingIndicator" class="message-row w-100 px-4 py-3">
               <div class="max-width-chat mx-auto d-flex gap-3 align-items-end justify-content-start">
                  <div class="avatar-msg assistant-avatar rounded-circle shadow-sm d-flex align-items-center justify-content-center flex-shrink-0">
                    <i class="bi bi-mortarboard-fill"></i>
                  </div>
                  <div class="message-bubble bubble-assistant loading-state d-flex align-items-center mt-2">
                    <div class="typing-indicator d-flex align-items-center gap-1">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
               </div>
            </div>

            <div style="height: 280px; flex-shrink: 0; width: 100%;"></div>
          </div>

          <div class="chat-minimap-track" v-if="userMessageIndices.length > 0 && messages.length > 0">
            <div v-for="(item, idx) in userMessageIndices" :key="item.index"
                 class="minimap-node"
                 :class="(activeMessageIndex !== -1 ? activeMessageIndex === item.index : idx === userMessageIndices.length - 1) ? 'minimap-node-active' : ''"
                 @click="scrollToMessage(item.index)"
                 title="Jump to message">
            </div>
          </div>

          <ChatComposer
            v-model="inputQuery"
            :isEmptyChat="messages.length === 0"
            :uploadedDocument="uploadedDocument"
            :editSourceIndex="editSourceIndex"
            :loading="loading"
            :isUploading="isUploading"
            :hasActiveRequest="!!activeRequestController"
            @send="handleSend"
            @stop-response="handleStopResponse"
            @upload-file="handleUpload"
            @remove-document="removeDocument"
          />

          </div>
        </div>
      </div>
    </Transition>

    <ConfirmDialog
      v-model="showDeleteConfirm"
      title="Delete Chat Session"
      message="Are you sure you want to delete this conversation? This action cannot be undone."
      icon-class="bi bi-trash-fill"
      icon-bg-class="bg-danger-subtle text-danger"
      confirm-text="Delete"
      confirm-btn-class="btn-danger"
      :loading="isDeleting"
      @confirm="confirmDeleteSession"
      @cancel="sessionToDelete = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import ConfirmDialog from '@/components/shared/common/feedback/ConfirmDialog.vue'
import ChatSidebar from './ChatSidebar.vue'
import ChatComposer from './ChatComposer.vue'

import { formatMessage } from '@/utils/chatHelpers'
import { useChatSessionManager } from '@/composables/student/useChatSessionManager'
import { useDocumentUpload } from '@/composables/student/useDocumentUpload'
import { useChatStream } from '@/composables/student/useChatStream'

const isOpen = ref(false)
const isDarkMode = ref(localStorage.getItem('chat_dark_mode') === 'true')
const isFullScreen = ref(false)
const messageBox = ref(null)
const inlineEditInput = ref(null)

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('chat_dark_mode', isDarkMode.value)
}

const toggleFullScreen = () => {
  isFullScreen.value = !isFullScreen.value
}

const messages = ref([])
const inputQuery = ref('')
const editSourceIndex = ref(null)
const inlineEditQuery = ref('')
const copiedMessageIndex = ref(null)
const activeMessageIndex = ref(-1)

const pushAssistantNotice = (content) => {
  messages.value.push({ role: 'assistant', content, source: 'System' })
  scrollToBottom()
}

const startNewChat = () => {
  currentSessionId.value = null
  localStorage.removeItem('current_chat_session_id')
  messages.value = []
  editSourceIndex.value = null
  inlineEditQuery.value = ''
}

const {
  sessions, currentSessionId, showDeleteConfirm, sessionToDelete,
  isDeleting, renamingSessionId, editingSessionId, renameDraft,
  renameInputRef, loadSessions, loadSession, handleDeleteSession,
  confirmDeleteSession, startRenameSession, cancelRenameSession,
  submitRenameSession
} = useChatSessionManager({
  messages, loading: ref(false), editSourceIndex, inlineEditQuery, startNewChatCallback: startNewChat
})

const {
  loading, showThinkingIndicator, activeRequestController,
  stopNoticeShown, handleStopResponse, submitMessage
} = useChatStream({
  messages, currentSessionId, loadSessionsCallback: loadSessions,
  scrollToBottomCallback: () => scrollToBottom(), onAssistantNotice: pushAssistantNotice
})

const {
  isUploading, uploadedDocument, handleUpload, removeDocument
} = useDocumentUpload({
  onAssistantNotice: pushAssistantNotice,
  currentSessionId,
  loadSessionsCallback: loadSessions,
})

const userMessageIndices = computed(() => {
  return messages.value.map((msg, index) => ({ msg, index })).filter(item => item.msg.role === 'user')
})

const handleChatScroll = () => {
  if (!messageBox.value || userMessageIndices.value.length === 0) return
  const container = messageBox.value
  const viewportCenter = container.scrollTop + container.clientHeight / 2

  let closestIndex = userMessageIndices.value[0].index
  let minDistance = Infinity

  userMessageIndices.value.forEach(item => {
    const el = document.getElementById(`chat-msg-${item.index}`)
    if (el) {
      const distance = Math.abs(el.offsetTop - viewportCenter)
      if (distance < minDistance) {
        minDistance = distance
        closestIndex = item.index
      }
    }
  })
  activeMessageIndex.value = closestIndex
}

const scrollToMessage = (index) => {
  const el = document.getElementById(`chat-msg-${index}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    activeMessageIndex.value = index
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageBox.value) {
    messageBox.value.scrollTop = messageBox.value.scrollHeight
    handleChatScroll()
  }
}

const handleSend = async () => {
  let query = inputQuery.value.trim()
  const docReady = uploadedDocument.value && uploadedDocument.value.status === 'ready'
  const docUploading = uploadedDocument.value && uploadedDocument.value.status === 'uploading'
  const docError = uploadedDocument.value && uploadedDocument.value.status === 'error'
  
  if (!query && !docReady) return
  if (loading.value) return

  if (docUploading) {
    pushAssistantNotice('Document is still uploading/indexing. Please wait until the status turns green before asking from the file.')
    return
  }

  if (docError) {
    pushAssistantNotice('File is not uploaded yet. Please upload the file again, then ask your question.')
    return
  }

  if (!query && docReady) {
    query = "Please analyze the uploaded document."
  }

  inputQuery.value = ''
  
  let docName = null
  if (docReady) {
    docName = uploadedDocument.value.name
    uploadedDocument.value = null
  }

  await submitMessage(query, null, docName)
}

const handleInlineEditSend = async () => {
  const query = inlineEditQuery.value.trim()
  const sourceIndex = editSourceIndex.value
  if (!query || loading.value || sourceIndex === null) return
  await submitMessage(query, sourceIndex, null, editSourceIndex, inlineEditQuery)
}

const editAndResend = async (index) => {
  const msg = messages.value[index]
  if (!msg || msg.role !== 'user') return
  inlineEditQuery.value = msg.rawQuery || msg.content || ''
  editSourceIndex.value = index
  await nextTick()
  inlineEditInput.value?.focus?.()
}

const cancelEditResend = () => {
  editSourceIndex.value = null
  inlineEditQuery.value = ''
}

const shareChat = async () => {
  if (messages.value.length === 0) {
    alert("No chat history to share.");
    return;
  }
  
  let chatText = "Chat Session with Academic Assistant:\n\n";
  messages.value.forEach(msg => {
    const role = msg.role === 'user' ? 'You' : 'Assistant';
    chatText += `[${role}]: ${msg.content}\n\n`;
  });
  
  try {
    if (navigator.share) {
      await navigator.share({ title: 'Academic Assistant Chat', text: chatText });
    } else {
      await navigator.clipboard.writeText(chatText);
      alert("Chat copied to clipboard!");
    }
  } catch (error) {
    console.error("Error sharing chat:", error);
  }
}

const copyMessage = async (text, index) => {
  if (!text) return
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      const temp = document.createElement('textarea')
      temp.value = text
      temp.style.position = 'fixed'
      temp.style.opacity = '0'
      document.body.appendChild(temp)
      temp.select()
      document.execCommand('copy')
      document.body.removeChild(temp)
    }
    copiedMessageIndex.value = index
    setTimeout(() => {
      if (copiedMessageIndex.value === index) copiedMessageIndex.value = null
    }, 1200)
  } catch (error) {
    console.error('Copy failed:', error)
  }
}

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loadSessions()
    if (currentSessionId.value) {
      loadSession(currentSessionId.value, scrollToBottom)
    }
  }
}

const onHandleToggle = () => {
  toggleChat()
}

onMounted(() => {
  if (currentSessionId.value) loadSession(currentSessionId.value, scrollToBottom)
  
  window.addEventListener('toggle-ai-chat', (e) => {
    if (e.detail.action === 'open') {
      isOpen.value = true
      loadSessions()
      const sid = e.detail.sessionId || currentSessionId.value
      if (sid) loadSession(sid, scrollToBottom)
    }
  })
})

onUnmounted(() => {
  if (activeRequestController.value) {
    activeRequestController.value.abort('Chat panel closed')
    activeRequestController.value = null
  }
  window.removeEventListener('toggle-ai-chat', onHandleToggle)
})
</script>

