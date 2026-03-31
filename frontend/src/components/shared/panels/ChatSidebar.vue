<template>
  <div class="chat-sidebar d-flex flex-column bg-dark text-white border-end border-secondary">
    <div class="p-3 w-100">
      <button @click="$emit('start-new-chat')" class="btn btn-outline-light btn-sm w-100 d-flex align-items-center justify-content-center gap-2 py-2 rounded-3 border-secondary">
        <i class="bi bi-plus-lg"></i> New Chat
      </button>
    </div>
    
    <div class="flex-grow-1 w-100 overflow-auto p-2 history-container px-3">
      <h6 class="text-uppercase text-secondary extra-small mb-3 px-1 mt-2">Yesterday</h6>
      <div v-if="sessions.length === 0" class="text-center py-4 px-2 opacity-25 small italic">No recent chats</div>
      
      <div v-for="sess in sessions" :key="sess.id" 
           class="history-item px-3 py-2 rounded-3 mb-1 d-flex align-items-center gap-2 transition-all position-relative cursor-pointer"
           :class="{ 'active bg-secondary bg-opacity-25': currentSessionId === sess.id }"
           @click="$emit('load-session', sess.id)">
        <i class="bi bi-chat-left-text-fill small opacity-50 flex-shrink-0"></i>
        
        <div v-if="editingSessionId === sess.id" class="history-rename-wrap flex-grow-1" @click.stop>
          <input
            :ref="(el) => { if(el) $emit('set-rename-ref', el) }"
            :value="renameDraft"
            @input="$emit('update:renameDraft', $event.target.value)"
            class="history-rename-input"
            type="text"
            maxlength="255"
            @click.stop
            @blur="$emit('cancel-rename')"
            @keydown.enter.prevent="$emit('submit-rename', sess)"
            @keydown.esc.prevent="$emit('cancel-rename')"
          />
        </div>
        <span v-else class="text-truncate small flex-grow-1">{{ sess.title || 'Conversation' }}</span>
        
        <template v-if="editingSessionId === sess.id">
          <button
            @mousedown.prevent
            @click.stop="$emit('submit-rename', sess)"
            class="btn btn-link btn-xs p-0 text-success rename-save-btn flex-shrink-0"
            title="Save name"
            :disabled="renamingSessionId === sess.id"
          >
            <i :class="renamingSessionId === sess.id ? 'bi bi-hourglass-split' : 'bi bi-check-lg'"></i>
          </button>
          <button
            @mousedown.prevent
            @click.stop="$emit('cancel-rename')"
            class="btn btn-link btn-xs p-0 text-white-50 rename-cancel-btn flex-shrink-0"
            title="Cancel rename"
            :disabled="renamingSessionId === sess.id"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </template>
        <button
          v-else
          @click.stop="$emit('start-rename', sess)"
          class="btn btn-link btn-xs p-0 text-white-50 rename-btn opacity-0 transition-opacity flex-shrink-0"
          title="Rename chat"
          :disabled="renamingSessionId === sess.id"
        >
          <i :class="renamingSessionId === sess.id ? 'bi bi-hourglass-split' : 'bi bi-pencil-square'"></i>
        </button>
        
        <button v-if="editingSessionId !== sess.id" @click.stop="$emit('delete-session', sess.id)" 
                class="btn btn-link btn-xs p-0 text-white-50 delete-btn opacity-0 transition-opacity flex-shrink-0"
                title="Delete chat">
            <i class="bi bi-trash"></i>
        </button>
      </div>
    </div>

    <!-- User Quick Profile & Settings in Sidebar -->
    <div class="mt-auto p-3 border-top border-secondary bg-dark-soft d-flex align-items-center justify-content-between">
       <div class="d-flex align-items-center gap-2 small opacity-75 w-75">
          <div class="avatar-xs bg-success rounded-circle text-white d-flex align-items-center justify-content-center flex-shrink-0">
             <i class="bi bi-person-fill tiny-text"></i>
          </div>
          <span class="text-truncate">Student Workspace</span>
       </div>
       
       <button @click="$emit('toggle-dark-mode')" class="btn btn-link btn-sm p-1 text-white-50 hover-opacity-100" title="Toggle Dark/Light Mode">
          <i :class="isDarkMode ? 'bi bi-moon-fill text-warning' : 'bi bi-sun'"></i>
       </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sessions: { type: Array, required: true },
  currentSessionId: { type: [String, Number], default: null },
  editingSessionId: { type: [String, Number], default: null },
  renamingSessionId: { type: [String, Number], default: null },
  renameDraft: { type: String, default: '' },
  isDarkMode: { type: Boolean, default: false }
})

defineEmits([
  'start-new-chat',
  'load-session',
  'set-rename-ref',
  'update:renameDraft',
  'submit-rename',
  'cancel-rename',
  'start-rename',
  'delete-session',
  'toggle-dark-mode'
])
</script>
