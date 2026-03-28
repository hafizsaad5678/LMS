<template>
  <div class="student-ai-chatbot shadow">
    <!-- Chat Window -->
    <Transition name="slide-up">
      <div v-if="isOpen" class="chat-window card border-0 shadow-2xl overflow-hidden d-flex flex-row">
        <!-- ChatGPT-style Sidebar -->
        <div class="chat-sidebar d-flex flex-column bg-dark text-white border-end border-secondary">
          <div class="p-3 w-100">
            <button @click="startNewChat" class="btn btn-outline-light btn-sm w-100 d-flex align-items-center justify-content-center gap-2 py-2 rounded-3 border-secondary">
              <i class="bi bi-plus-lg"></i> New Chat
            </button>
          </div>
          
          <div class="flex-grow-1 w-100 overflow-auto p-2 history-container px-3">
            <h6 class="text-uppercase text-secondary extra-small mb-3 px-1 mt-2">Yesterday</h6>
            <div v-if="sessions.length === 0" class="text-center py-4 px-2 opacity-25 small italic">No recent chats</div>
            <div v-for="sess in sessions" :key="sess.id" 
                 class="history-item px-3 py-2 rounded-3 mb-1 d-flex align-items-center gap-2 transition-all position-relative cursor-pointer"
                 :class="{ 'active bg-secondary bg-opacity-25': currentSessionId === sess.id }"
                 @click="loadSession(sess.id)">
              <i class="bi bi-chat-left-text-fill small opacity-50 flex-shrink-0"></i>
              <span class="text-truncate small flex-grow-1">{{ sess.title || 'Conversation' }}</span>
              <button @click.stop="handleDeleteSession(sess.id)" 
                      class="btn btn-link btn-xs p-0 text-white-50 delete-btn opacity-0 transition-opacity flex-shrink-0"
                      title="Delete chat">
                  <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>

          <!-- User Quick Profile in Sidebar -->
          <div class="mt-auto p-3 border-top border-secondary bg-dark-soft">
             <div class="d-flex align-items-center gap-2 small opacity-75">
                <div class="avatar-xs bg-success rounded-circle text-white d-flex align-items-center justify-content-center">
                   <i class="bi bi-person-fill tiny-text"></i>
                </div>
                <span class="text-truncate">Student Workspace</span>
             </div>
          </div>
        </div>

        <!-- Main Chat Area -->
        <div class="chat-main d-flex flex-column flex-grow-1 bg-white">
          <!-- Header -->
          <div class="chat-header p-3 d-flex align-items-center justify-content-between">
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
               <button class="btn btn-link link-secondary p-1"><i class="bi bi-share"></i></button>
               <button @click="toggleChat" class="btn btn-link link-dark p-1 text-decoration-none"><i class="bi bi-x-lg"></i></button>
            </div>
          </div>

          <!-- Messages Area -->
          <div class="chat-body flex-grow-1 p-0 overflow-auto d-flex flex-column" ref="messageBox">
            <div v-if="messages.length === 0" class="empty-chat text-center my-auto py-5 px-4">
               <div class="mx-auto bg-light rounded-circle d-flex align-items-center justify-content-center mb-4 shadow-sm assistant-stars-icon">
                  <i class="bi bi-stars fs-2 text-success"></i>
               </div>
               <h5 class="fw-bold text-dark">LMS Intelligence</h5>
               <p class="text-muted small mx-auto empty-chat-text">
                  Ask about upcoming assignments, analyze your attendance, or explain complex course topics.
               </p>
               <div class="d-flex flex-wrap justify-content-center gap-2 mt-4 px-3">
                  <button @click="inputQuery = 'What assignments are due?'" class="btn btn-outline-secondary btn-xs rounded-pill px-3">Upcoming Assignments</button>
                  <button @click="inputQuery = 'Check my attendance'" class="btn btn-outline-secondary btn-xs rounded-pill px-3">Attendance Summary</button>
               </div>
            </div>

            <div v-for="(msg, index) in messages" :key="index" class="message-row w-100 px-4 py-3">
              <div class="max-width-chat mx-auto d-flex gap-3 align-items-end"
                   v-if="!(msg.role === 'user' && editSourceIndex === index)"
                   :class="msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'">
                <div v-if="msg.role !== 'user'" class="avatar-msg assistant-avatar rounded-circle shadow-sm d-flex align-items-center justify-content-center flex-shrink-0">
                  <i class="bi bi-mortarboard-fill"></i>
                </div>
                <div class="message-content-wrap" :class="msg.role === 'user' ? 'user-content-wrap' : 'assistant-content-wrap'">
                  <div class="message-bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'">
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
                    rows="1"
                    class="form-control border-0 shadow-none bg-transparent small inline-edit-input"
                    placeholder="Edit your message"
                    :disabled="loading"
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

            <!-- Thinking Indicator -->
            <div v-if="loading" class="message-row w-100 px-4 py-3">
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
          </div>

          <!-- Footer / Input Area -->
          <div class="chat-footer p-4 pt-2">
            <div class="max-width-chat mx-auto position-relative">
               <div class="input-container-modern shadow-lg rounded-4 border bg-white overflow-hidden">
                  <div class="chat-input-shell d-flex align-items-start gap-2 px-3 pt-2">
                    <i class="bi bi-search chat-input-icon mt-2"></i>
                    <textarea 
                      v-model="inputQuery" 
                      @keydown.enter.prevent="handleSend" 
                      rows="1"
                      class="form-control border-0 bg-transparent shadow-none py-2 px-1 resize-none small chat-main-input" 
                      :placeholder="editSourceIndex !== null ? 'Editing a previous message above...' : 'Search notes or ask your question...'"
                      :disabled="loading || editSourceIndex !== null"
                    ></textarea>
                  </div>
                  <div class="d-flex justify-content-between align-items-center px-4 py-2 bg-light-soft border-top">
                     <div class="d-flex gap-2">
                        <input type="file" ref="fileInput" class="d-none" @change="handleUpload" accept=".pdf,.docx,.txt">
                        <button @click="$refs.fileInput.click()" class="btn btn-link btn-xs p-0 text-muted" title="Upload Document" :disabled="editSourceIndex !== null"><i class="bi bi-paperclip fs-6"></i></button>
                        <button class="btn btn-link btn-xs p-0 text-muted" :disabled="editSourceIndex !== null"><i class="bi bi-emoji-smile fs-6"></i></button>
                     </div>
                     <button @click="handleSend" class="btn btn-success btn-sm rounded-3 px-3 d-flex align-items-center gap-2" 
                             :disabled="loading || isUploading || editSourceIndex !== null || !inputQuery.trim()">
                        <span class="extra-tiny fw-bold">SEND</span>
                        <i class="bi bi-send-fill tiny-text"></i>
                      </button>
                  </div>
               </div>
               <div class="text-center mt-2 tiny-text text-muted opacity-75 w-100">
                 AI can make mistakes — verify important information.
               </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Confirm Dialog -->
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import aiChatService from '@/services/shared/aiChatService'
import ConfirmDialog from '@/components/shared/common/feedback/ConfirmDialog.vue'

const isOpen = ref(false)
const loading = ref(false)
const isUploading = ref(false)
const inputQuery = ref('')
const messages = ref([])
const sessions = ref([])
const currentSessionId = ref(localStorage.getItem('current_chat_session_id'))
const messageBox = ref(null)
const inlineEditInput = ref(null)
const editSourceIndex = ref(null)
const inlineEditQuery = ref('')
const copiedMessageIndex = ref(null)

// Delete confirmation state
const showDeleteConfirm = ref(false)
const sessionToDelete = ref(null)
const isDeleting = ref(false)

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loadSessions()
    // If there's a current session, load its messages
    if (currentSessionId.value) {
      loadSession(currentSessionId.value)
    }
  }
}

const onHandleToggle = () => {
  toggleChat()
}

onMounted(() => {
  if (currentSessionId.value) loadSession(currentSessionId.value)
  
  window.addEventListener('toggle-ai-chat', (e) => {
    if (e.detail.action === 'open') {
      isOpen.value = true
      loadSessions()
      const sid = e.detail.sessionId || currentSessionId.value
      if (sid) loadSession(sid)
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('toggle-ai-chat', onHandleToggle)
})


const startNewChat = () => {
  currentSessionId.value = null
  localStorage.removeItem('current_chat_session_id')
  messages.value = []
  editSourceIndex.value = null
  inlineEditQuery.value = ''
}

const loadSession = async (sid) => {
  // Reset view for loading
  loading.value = true
  currentSessionId.value = sid
  localStorage.setItem('current_chat_session_id', sid)
  editSourceIndex.value = null
  inlineEditQuery.value = ''
  
  try {
    const res = await aiChatService.getSessionMessages(sid)
    const messagesList = res.messages || [] 
    messages.value = messagesList.map(m => ({
      role: m.role,
      content: m.content
    }))
    scrollToBottom()
  } catch (err) {
    console.error('Session messages load failed', err)
  } finally {
    loading.value = false
  }
}


const handleUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isUploading.value = true
  
  // Show upload in progress
  messages.value.push({ 
    role: 'user', 
    content: `Uploading document: ${file.name}...` 
  })
  scrollToBottom()

  try {
    const res = await aiChatService.uploadDocument(file)
    
    // Show success
    messages.value.push({
      role: 'assistant',
      content: res.message || `Document "${file.name}" processed successfully. You can ask me questions about it!`,
      source: 'System'
    })

  } catch (err) {
    console.error('Upload failed', err)
    messages.value.push({ 
      role: 'assistant', 
      content: "Failed to upload document. Please ensure it's a valid PDF or DOCX file.", 
      source: 'System' 
    })
  } finally {
    isUploading.value = false
    event.target.value = '' // Reset input
    scrollToBottom()
  }
}

const handleSend = async () => {
  const query = inputQuery.value.trim()
  if (!query || loading.value) return

  inputQuery.value = ''
  await submitMessage(query)
}

const handleInlineEditSend = async () => {
  const query = inlineEditQuery.value.trim()
  const sourceIndex = editSourceIndex.value
  if (!query || loading.value || sourceIndex === null) return
  await submitMessage(query, sourceIndex)
}

const submitMessage = async (query, sourceIndex = null) => {
  // When editing, replace the selected user message and drop trailing turns.
  if (sourceIndex !== null && messages.value[sourceIndex]?.role === 'user') {
    messages.value = messages.value.slice(0, sourceIndex + 1)
    messages.value[sourceIndex] = {
      ...messages.value[sourceIndex],
      content: query
    }
    editSourceIndex.value = null
    inlineEditQuery.value = ''
  } else {
    // Push user message immediately for normal sends.
    messages.value.push({ role: 'user', content: query })
  }
  scrollToBottom()
  
  loading.value = true
  try {
    const res = await aiChatService.sendMessage(query, currentSessionId.value)
    
    // Update session state
    if (res.session_id) {
       currentSessionId.value = res.session_id
       localStorage.setItem('current_chat_session_id', res.session_id)
       // Refresh history to see new title or updated session
       await loadSessions()
    }
    

    messages.value.push({
      role: 'assistant',
      content: res.message.content || "Empty response received", 
      source: res.message.source
    })
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({ 
      role: 'assistant', 
      content: "I'm sorry, I'm having trouble connecting to the knowledge base right now. Please try again in a moment.", 
      source: 'System' 
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const formatMessage = (text) => {
  if (!text) return ''
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')
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

const isEditableUserMessage = (index) => {
  if (messages.value[index]?.role !== 'user') return false
  for (let i = index + 1; i < messages.value.length; i += 1) {
    if (messages.value[i]?.role === 'user') return false
  }
  return true
}

const editAndResend = async (index) => {
  const msg = messages.value[index]
  if (!msg || msg.role !== 'user') return
  inlineEditQuery.value = msg.content || ''
  editSourceIndex.value = index
  await nextTick()
  inlineEditInput.value?.focus?.()
}

const cancelEditResend = () => {
  editSourceIndex.value = null
  inlineEditQuery.value = ''
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageBox.value) messageBox.value.scrollTop = messageBox.value.scrollHeight
}

const loadSessions = async () => {
  try {
    const res = await aiChatService.getSessions()
    // Sort sessions by updated_at descending if available
    sessions.value = res.sort((a,b) => new Date(b.updated_at) - new Date(a.updated_at))
  } catch (err) { console.error('History load failed', err) }
}

const handleDeleteSession = (sid) => {
  sessionToDelete.value = sid
  showDeleteConfirm.value = true
}

const confirmDeleteSession = async () => {
  if (!sessionToDelete.value) return
  isDeleting.value = true
  
  try {
    const sid = sessionToDelete.value
    await aiChatService.deleteSession(sid)
    sessions.value = sessions.value.filter(s => s.id !== sid)
    
    // If we deleted the active session, reset
    if (currentSessionId.value === sid) {
       startNewChat()
    }
  } catch (err) {
    console.error('Delete failed', err)
  } finally {
    isDeleting.value = false
    showDeleteConfirm.value = false
    sessionToDelete.value = null
  }
}
</script>

<style scoped></style>
