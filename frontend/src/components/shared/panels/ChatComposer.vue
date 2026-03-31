<template>
  <div class="chat-footer w-100 flex-shrink-0">
    <div class="max-width-chat mx-auto position-relative">
       <div class="input-container-modern shadow-sm rounded-4 border bg-white overflow-hidden transition-all"
            :class="isEmptyChat ? 'border-secondary border-opacity-25 shadow-lg mx-auto w-100' : ''">
          <div class="chat-input-shell d-flex flex-column px-3 pt-2">
          <!-- Document Chip -->
          <div v-if="uploadedDocument" class="uploaded-doc-chip d-inline-flex align-items-center border border-secondary border-opacity-25 rounded-4 p-2 my-2 position-relative shadow-sm" :class="{ 'bg-dark text-white border-0': uploadedDocument.status === 'uploading', 'bg-white': uploadedDocument.status !== 'uploading' }" style="min-width: 220px; max-width: 320px; width: fit-content; margin-left: 32px;">
            <div class="text-white rounded-3 d-flex align-items-center justify-content-center me-2 flex-shrink-0 transition-all doc-chip-icon" :class="{'bg-danger': uploadedDocument.status === 'error', 'bg-success': uploadedDocument.status === 'ready', 'doc-chip-uploading-icon': uploadedDocument.status === 'uploading'}">
              <i v-if="uploadedDocument.status === 'ready'" class="bi bi-file-earmark-check-fill fs-5"></i>
              <i v-else-if="uploadedDocument.status === 'error'" class="bi bi-file-earmark-x-fill fs-5"></i>
              <span v-else class="doc-loader-ring" aria-label="Uploading"></span>
            </div>
            <div class="d-flex flex-column overflow-hidden flex-grow-1 pe-4 w-100">
              <span class="small fw-semibold text-truncate lh-sm tooltip-trigger mb-1" :class="uploadedDocument.status === 'uploading' ? 'text-white' : 'text-dark'" :title="uploadedDocument.name">{{ uploadedDocument.name }}</span>
              
              <!-- Small Loading Bar when Uploading -->
              <div v-if="uploadedDocument.status === 'uploading'" class="w-100 mt-1 pe-1">
                <div class="progress" style="height: 4px;">
                   <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" :style="{ width: `${uploadedDocument.progress || 14}%` }"></div>
                </div>
                <span class="extra-tiny mt-1 d-block" :class="uploadedDocument.status === 'uploading' ? 'text-light opacity-75' : 'text-muted'">{{ uploadedDocument.statusText || 'Processing model...' }}</span>
              </div>
              
              <!-- Ready / Error Status text -->
              <span v-else class="extra-tiny lh-sm d-flex align-items-center gap-1 mt-1 text-muted">
                {{ uploadedDocument.status === 'error' ? (uploadedDocument.statusText || 'Failed to process') : 'Ready' }}
                <i v-if="uploadedDocument.status === 'ready'" class="bi bi-check-circle-fill text-success" style="font-size: 0.9em;"></i>
                <i v-if="uploadedDocument.status === 'error'" class="bi bi-x-circle-fill text-danger" style="font-size: 0.9em;"></i>
              </span>
            </div>
            <!-- Unified Delete/Dismiss button available strictly to the right -->
            <button @click="$emit('remove-document')" class="btn btn-link btn-xs p-0 position-absolute top-50 end-0 translate-middle-y me-2 lh-1 rounded-circle z-index-1" :class="uploadedDocument.status === 'uploading' ? 'text-light bg-dark-subtle' : 'text-secondary bg-light'" title="Cancel/Remove Document" style="opacity: 0.7;">
              <i class="bi bi-x-circle-fill fs-5"></i>
            </button>
          </div>
          
          <div class="d-flex align-items-start gap-2 w-100">
            <i class="bi bi-search chat-input-icon mt-2"></i>
            <textarea 
              ref="chatMainInput"
              :value="modelValue" 
              @input="onInput"
              @keydown.enter.exact.prevent="$emit('send')" 
              rows="2"
              class="form-control border-0 bg-transparent shadow-none py-2 px-1 small chat-main-input"
              style="min-height: 44px; max-height: 180px; overflow-y: hidden;"
              :placeholder="editSourceIndex !== null ? 'Editing a previous message above...' : 'Search notes or ask your question...'"
              :disabled="loading || editSourceIndex !== null"
            ></textarea>
          </div>
        </div>
        <div class="d-flex justify-content-between align-items-center px-4 py-2 bg-light-soft border-top position-relative">
          <div v-if="showEmojiPicker" class="emoji-picker-panel shadow-sm border rounded-3 bg-white p-2">
            <button
              v-for="icon in emojiOptions"
              :key="icon"
              @click="appendEmoji(icon)"
              class="btn btn-light btn-sm emoji-btn"
              type="button"
            >
              {{ icon }}
            </button>
          </div>
           <div class="d-flex gap-2">
              <input type="file" ref="fileInput" class="d-none" @change="(e) => $emit('upload-file', e)" accept=".pdf,.docx,.txt">
              <button @click="$refs.fileInput.click()" class="btn btn-link btn-xs p-0 text-muted" title="Upload Document" :disabled="editSourceIndex !== null || isUploading"><i class="bi bi-paperclip fs-6"></i></button>
            <button @click="showEmojiPicker = !showEmojiPicker" class="btn btn-link btn-xs p-0 text-muted" title="Insert emoji" :disabled="editSourceIndex !== null"><i class="bi bi-emoji-smile fs-6"></i></button>
           </div>
           
           <button
             v-if="hasActiveRequest"
             @click="$emit('stop-response')"
             class="btn btn-outline-danger btn-sm rounded-3 px-3 d-flex align-items-center gap-2"
             :disabled="isUploading"
           >
              <span class="extra-tiny fw-bold">STOP</span>
              <i class="bi bi-stop-fill tiny-text"></i>
           </button>
           
           <button
             v-else
             @click="$emit('send')"
             class="btn btn-success btn-sm rounded-3 px-3 d-flex align-items-center gap-2"
             :disabled="loading || isUploading || editSourceIndex !== null || (!modelValue.trim() && (!uploadedDocument || uploadedDocument.status !== 'ready'))"
           >
              <span class="extra-tiny fw-bold">SEND</span>
              <i class="bi bi-send-fill tiny-text"></i>
           </button>
        </div>
     </div>
     <div class="text-center mt-3 mb-2 tiny-text text-muted opacity-75 w-100">
       AI can make mistakes — verify important information.
     </div>
  </div>
</div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { clamp, MAIN_INPUT_MIN_HEIGHT, MAIN_INPUT_MAX_HEIGHT, EMOJI_OPTIONS } from '@/utils/chatHelpers'

const props = defineProps({
  modelValue: { type: String, default: '' },
  isEmptyChat: { type: Boolean, default: false },
  uploadedDocument: { type: Object, default: null },
  editSourceIndex: { type: Number, default: null },
  loading: { type: Boolean, default: false },
  isUploading: { type: Boolean, default: false },
  hasActiveRequest: { type: Boolean, default: false }
})

const emit = defineEmits([
  'update:modelValue',
  'send',
  'stop-response',
  'upload-file',
  'remove-document'
])

const chatMainInput = ref(null)
const fileInput = ref(null)
const showEmojiPicker = ref(false)
const emojiOptions = EMOJI_OPTIONS

const resetMainInputHeight = () => {
  const el = chatMainInput.value
  if (!el) return
  el.style.height = `${MAIN_INPUT_MIN_HEIGHT}px`
  el.style.overflowY = 'hidden'
}

const autoGrowMainInput = async () => {
  await nextTick()
  const el = chatMainInput.value
  if (!el) return
  el.style.height = 'auto'
  const nextHeight = clamp(el.scrollHeight, MAIN_INPUT_MIN_HEIGHT, MAIN_INPUT_MAX_HEIGHT)
  el.style.height = `${nextHeight}px`
  el.style.overflowY = el.scrollHeight > MAIN_INPUT_MAX_HEIGHT ? 'auto' : 'hidden'
}

const onInput = (event) => {
  emit('update:modelValue', event.target.value)
  autoGrowMainInput()
}

const appendEmoji = (icon) => {
  const newVal = `${props.modelValue}${props.modelValue ? ' ' : ''}${icon}`
  emit('update:modelValue', newVal)
  showEmojiPicker.value = false
  autoGrowMainInput()
}

// Optionally reset height when empty
watch(() => props.modelValue, (newVal) => {
  if (!newVal) resetMainInputHeight()
})
</script>
