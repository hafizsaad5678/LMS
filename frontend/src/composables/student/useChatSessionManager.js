import { ref, nextTick } from 'vue'
import aiChatService from '@/services/shared/aiChatService'

export function useChatSessionManager({ messages, loading, editSourceIndex, inlineEditQuery, startNewChatCallback }) {
  const sessions = ref([])
  const currentSessionId = ref(localStorage.getItem('current_chat_session_id') || null)
  
  const showDeleteConfirm = ref(false)
  const sessionToDelete = ref(null)
  const isDeleting = ref(false)
  
  const renamingSessionId = ref(null)
  const editingSessionId = ref(null)
  const renameDraft = ref('')
  const renameInputRef = ref(null)

  const loadSessions = async () => {
    try {
      const res = await aiChatService.getSessions()
      sessions.value = res.sort((a,b) => new Date(b.updated_at) - new Date(a.updated_at))
    } catch (err) { 
      console.error('History load failed', err) 
    }
  }

  const loadSession = async (sid, scrollToBottomCallback) => {
    loading.value = true
    currentSessionId.value = sid
    localStorage.setItem('current_chat_session_id', sid)
    
    if (editSourceIndex) editSourceIndex.value = null
    if (inlineEditQuery) inlineEditQuery.value = ''
    
    try {
      const res = await aiChatService.getSessionMessages(sid)
      const messagesList = res.messages || [] 
      messages.value = messagesList.map(m => ({
        role: m.role,
        content: m.content,
        rawQuery: m.role === 'user' ? (m.rawQuery || m.content) : null
      }))
      if (scrollToBottomCallback) {
        scrollToBottomCallback()
      }
    } catch (err) {
      console.error('Session messages load failed', err)
    } finally {
      loading.value = false
    }
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
      
      if (currentSessionId.value === sid && startNewChatCallback) {
         startNewChatCallback()
      }
    } catch (err) {
      console.error('Delete failed', err)
    } finally {
      isDeleting.value = false
      showDeleteConfirm.value = false
      sessionToDelete.value = null
    }
  }

  const startRenameSession = async (session) => {
    if (!session?.id || renamingSessionId.value === session.id) return
    editingSessionId.value = session.id
    renameDraft.value = String(session.title || 'Conversation').trim()
    await nextTick()
    const inputEl = Array.isArray(renameInputRef.value) ? renameInputRef.value[0] : renameInputRef.value
    inputEl?.focus?.()
    inputEl?.select?.()
  }

  const cancelRenameSession = () => {
    if (renamingSessionId.value) return
    editingSessionId.value = null
    renameDraft.value = ''
  }

  const submitRenameSession = async (session) => {
    const sid = session?.id || editingSessionId.value
    if (!sid || renamingSessionId.value === sid) return

    const existing = sessions.value.find((s) => s.id === sid)
    const currentTitle = String(existing?.title || 'Conversation').trim()
    const nextTitle = String(renameDraft.value || '').trim()

    if (!nextTitle || nextTitle === currentTitle) {
      cancelRenameSession()
      return
    }

    renamingSessionId.value = sid
    try {
      const updated = await aiChatService.renameSession(sid, nextTitle)
      const target = sessions.value.find((s) => s.id === sid)
      if (target) target.title = updated?.title || nextTitle
      editingSessionId.value = null
      renameDraft.value = ''
    } catch (err) {
      console.error('Rename failed', err)
    } finally {
      renamingSessionId.value = null
    }
  }

  return {
    sessions,
    currentSessionId,
    showDeleteConfirm,
    sessionToDelete,
    isDeleting,
    renamingSessionId,
    editingSessionId,
    renameDraft,
    renameInputRef,
    loadSessions,
    loadSession,
    handleDeleteSession,
    confirmDeleteSession,
    startRenameSession,
    cancelRenameSession,
    submitRenameSession
  }
}
