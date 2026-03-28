<template>
  <div class="rte-container" :class="{ 'readonly': readonly }">
    <!-- Toolbar -->
    <div v-if="!readonly" class="rte-toolbar">
      <button 
        type="button" 
        class="rte-btn" 
        @click="execCommand('bold')" 
        title="Bold"
        :class="{ active: activeStates.bold }"
      >
        <i class="bi bi-type-bold"></i>
      </button>
      <button 
        type="button" 
        class="rte-btn" 
        @click="execCommand('italic')" 
        title="Italic"
        :class="{ active: activeStates.italic }"
      >
        <i class="bi bi-type-italic"></i>
      </button>
      <button 
        type="button" 
        class="rte-btn" 
        @click="execCommand('underline')" 
        title="Underline"
        :class="{ active: activeStates.underline }"
      >
        <i class="bi bi-type-underline"></i>
      </button>
      
      <div class="vr mx-1"></div>

      <button 
        type="button" 
        class="rte-btn" 
        @click="execCommand('insertUnorderedList')" 
        title="Bullet List"
        :class="{ active: activeStates.unorderedList }"
      >
        <i class="bi bi-list-ul"></i>
      </button>
      <button 
        type="button" 
        class="rte-btn" 
        @click="execCommand('insertOrderedList')" 
        title="Numbered List"
        :class="{ active: activeStates.orderedList }"
      >
        <i class="bi bi-list-ol"></i>
      </button>

      <div class="vr mx-1"></div>

      <button 
        type="button" 
        class="rte-btn" 
        @click="toggleCodeBlock" 
        title="Code Block"
        :class="{ active: activeStates.code }"
      >
        <i class="bi bi-code-slash"></i>
      </button>
      
      <button 
        type="button" 
        class="rte-btn" 
        @click="createLink" 
        title="Insert Link"
      >
        <i class="bi bi-link-45deg"></i>
      </button>
    </div>

    <!-- Editable Area -->
    <div
      ref="editor"
      class="rte-content"
      :contenteditable="!readonly"
      :placeholder="placeholder"
      @input="onInput"
      @paste="onPaste"
      @keyup="updateActiveStates"
      @mouseup="updateActiveStates"
      @blur="onBlur"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, reactive } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Type here...'
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'change'])

const editor = ref(null)
const activeStates = reactive({
  bold: false,
  italic: false,
  underline: false,
  unorderedList: false,
  orderedList: false,
  code: false
})

// Initialize content
onMounted(() => {
  if (editor.value) {
    editor.value.innerHTML = props.modelValue || ''
  }
  // Load CSS if not already loaded (though we added it to assets, sometimes it helps to ensure it's here)
  import('@/assets/css/rte.css').catch(() => {
    console.warn('RTE CSS failed to load via import. Ensure it is included in main.js or locally.')
  })
})

// Sync modelValue -> innerHTML
watch(() => props.modelValue, (newVal) => {
  if (editor.value && newVal !== editor.value.innerHTML) {
    // Save selection if focused
    const selection = window.getSelection()
    let range = null
    if (selection.rangeCount > 0 && document.activeElement === editor.value) {
      range = selection.getRangeAt(0)
    }

    editor.value.innerHTML = newVal || ''

    // Restore selection (primitive)
    if (range && document.activeElement === editor.value) {
      // Restore range logic can be complex, for simple v-model sync we usually 
      // rely on the fact that if newVal comes from outside, it's a full replace.
    }
  }
})

const onInput = () => {
  const content = sanitize(editor.value.innerHTML)
  emit('update:modelValue', content)
  updateActiveStates()
}

const onBlur = () => {
  emit('blur')
  emit('change', editor.value.innerHTML)
}

const execCommand = (command, value = null) => {
  if (props.readonly) return
  editor.value.focus()
  document.execCommand(command, false, value)
  onInput()
}

const toggleCodeBlock = () => {
  // Simple implementation: wrap in <pre><code> or just format as monospace
  // document.execCommand('formatBlock', false, 'pre') is the standard way
  const selection = window.getSelection()
  const parent = selection.anchorNode?.parentElement
  
  if (parent && (parent.tagName === 'PRE' || parent.closest('pre'))) {
    document.execCommand('formatBlock', false, 'p')
  } else {
    document.execCommand('formatBlock', false, 'pre')
  }
  onInput()
}

const createLink = () => {
  const url = prompt('Enter the URL:', 'https://')
  if (url) {
    execCommand('createLink', url)
  }
}

const onPaste = (e) => {
  e.preventDefault()
  const text = e.clipboardData.getData('text/plain')
  document.execCommand('insertText', false, text)
}

const sanitize = (html) => {
  if (!html) return ''
  // Safety: Remove script tags
  let clean = html.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gim, "")
  // Safety: Remove on* attributes
  clean = clean.replace(/ on\w+="[^"]*"/g, "")
  return clean
}

const updateActiveStates = () => {
  activeStates.bold = document.queryCommandState('bold')
  activeStates.italic = document.queryCommandState('italic')
  activeStates.underline = document.queryCommandState('underline')
  activeStates.unorderedList = document.queryCommandState('insertUnorderedList')
  activeStates.orderedList = document.queryCommandState('insertOrderedList')
  
  const selection = window.getSelection()
  if (selection.rangeCount > 0) {
    const parent = selection.anchorNode.parentElement
    activeStates.code = parent.tagName === 'PRE' || parent.closest('pre')
  }
}
</script>

<style scoped>
/* Scoped styles can be minimal as we use rte.css */
.readonly .rte-content {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
}
</style>
