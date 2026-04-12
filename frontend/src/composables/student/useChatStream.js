import { ref } from 'vue'
import aiChatService from '@/services/shared/aiChatService'
import { getGreetingResponse, isRequestCancelledError } from '@/utils/chatHelpers'

export function useChatStream({ messages, currentSessionId, loadSessionsCallback, scrollToBottomCallback, onAssistantNotice }) {
  const loading = ref(false)
  const showThinkingIndicator = ref(false)
  const activeRequestController = ref(null)
  const stopNoticeShown = ref(false)

  const handleStopResponse = () => {
    const controller = activeRequestController.value
    if (!controller) return

    stopNoticeShown.value = true
    controller.abort('Stopped by user')
    activeRequestController.value = null
    loading.value = false
    showThinkingIndicator.value = false
    
    if (onAssistantNotice) {
      onAssistantNotice('Response stopped. You can send a new message anytime.')
    }
  }

  const submitMessage = async (query, sourceIndex = null, docName = null, editSourceIndexRef = null, inlineEditQueryRef = null) => {
    if (sourceIndex !== null && messages.value[sourceIndex]?.role === 'user') {
      messages.value = messages.value.slice(0, sourceIndex + 1)
      messages.value[sourceIndex] = {
        ...messages.value[sourceIndex],
        content: query,
        rawQuery: query 
      }
      if (editSourceIndexRef) editSourceIndexRef.value = null
      if (inlineEditQueryRef) inlineEditQueryRef.value = ''
    } else {
      messages.value.push({ role: 'user', content: query, rawQuery: query, docName: docName || null })
    }
    
    if (scrollToBottomCallback) scrollToBottomCallback()

    const greetingResponse = getGreetingResponse(query)
    if (greetingResponse) {
      messages.value.push({
        role: 'assistant',
        content: greetingResponse,
        source: 'System'
      })
      if (scrollToBottomCallback) scrollToBottomCallback()
      return
    }
    
    loading.value = true
    showThinkingIndicator.value = true
    const requestController = new AbortController()
    activeRequestController.value = requestController
    stopNoticeShown.value = false
    let assistantMessageIndex = -1

    try {
      const res = await aiChatService.sendMessageStream(query, currentSessionId.value, {
        signal: requestController.signal,
        onChunk: (chunk) => {
          const chunkText = String(chunk ?? '')
          if (!chunkText) return

          if (assistantMessageIndex < 0 && !chunkText.trim()) {
            return
          }

          if (assistantMessageIndex < 0) {
            assistantMessageIndex = messages.value.push({
              role: 'assistant',
              content: chunkText,
              source: 'AI'
            }) - 1
          } else if (messages.value[assistantMessageIndex]) {
            messages.value[assistantMessageIndex].content += chunkText
          }

          if (showThinkingIndicator.value) {
            showThinkingIndicator.value = false
          }
          if (scrollToBottomCallback) scrollToBottomCallback()
        },
      })

      if (!res) {
        throw new Error('No final streaming payload received')
      }
      
      if (res.session_id) {
        const previousSessionId = currentSessionId.value
        currentSessionId.value = res.session_id
        localStorage.setItem('current_chat_session_id', res.session_id)
        if (loadSessionsCallback && previousSessionId !== res.session_id) {
          await loadSessionsCallback()
        }
      }

      const finalContent = String(res?.message?.content || '')
      if (assistantMessageIndex >= 0 && messages.value[assistantMessageIndex]) {
        if (!messages.value[assistantMessageIndex].content && finalContent) {
          messages.value[assistantMessageIndex].content = finalContent
        }
        messages.value[assistantMessageIndex].source = res?.message?.source || messages.value[assistantMessageIndex].source
        if (!messages.value[assistantMessageIndex].content) {
          messages.value[assistantMessageIndex].content = 'Empty response received'
        }
      } else {
        messages.value.push({
          role: 'assistant',
          content: finalContent || 'Empty response received',
          source: res?.message?.source || 'AI'
        })
      }
    } catch (error) {
      console.error('Chat error:', error)
      const cancelled = requestController.signal.aborted || isRequestCancelledError(error)
      if (cancelled) {
        if (!stopNoticeShown.value && onAssistantNotice) {
          onAssistantNotice('Response stopped. You can send a new message anytime.')
        }
        return
      }
      if (assistantMessageIndex >= 0 && messages.value[assistantMessageIndex]) {
        messages.value[assistantMessageIndex].content = "I'm sorry, I'm having trouble connecting to the knowledge base right now. Please try again in a moment."
        messages.value[assistantMessageIndex].source = 'System'
      } else {
        messages.value.push({
          role: 'assistant',
          content: "I'm sorry, I'm having trouble connecting to the knowledge base right now. Please try again in a moment.",
          source: 'System'
        })
      }
    } finally {
      if (activeRequestController.value === requestController) {
        activeRequestController.value = null
      }
      stopNoticeShown.value = false
      showThinkingIndicator.value = false
      loading.value = false
      if (scrollToBottomCallback) scrollToBottomCallback()
    }
  }

  return {
    loading,
    showThinkingIndicator,
    activeRequestController,
    stopNoticeShown,
    handleStopResponse,
    submitMessage
  }
}
