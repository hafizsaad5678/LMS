<template>
  <div class="card border-0 shadow-sm mb-4">
    <div class="card-body">
      <div class="row g-3 align-items-center">
        <div class="col-md-4">
          <label class="form-label small fw-bold text-muted">Department</label>
          <select v-model="localDepartment" class="form-select">
            <option value="">All Departments</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
              {{ dept.name }}
            </option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label small fw-bold text-muted">Program</label>
          <select v-model="localProgram" class="form-select">
            <option value="">All Programs</option>
            <option v-for="prog in programs" :key="prog.id" :value="prog.id">
              {{ prog.name }}
            </option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label small fw-bold text-muted">{{ subjectLabel }}</label>
          <select 
            v-model="localSubject" 
            @change="$emit('change', localSubject)"
            class="form-select" 
            :disabled="filteredSubjects.length === 0"
          >
            <option value="" disabled>Choose a subject...</option>
            <option v-for="sub in filteredSubjects" :key="sub.id" :value="sub.id">
              {{ sub.name }}
            </option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  departments: { type: Array, default: () => [] },
  programs: { type: Array, default: () => [] },
  filteredSubjects: { type: Array, default: () => [] },
  modelValue: { type: String, default: '' },
  department: { type: String, default: '' },
  program: { type: String, default: '' },
  subjectLabel: { type: String, default: 'Select Class' }
})

const emit = defineEmits(['update:modelValue', 'update:department', 'update:program', 'change'])

const localDepartment = computed({
  get: () => props.department,
  set: (val) => emit('update:department', val)
})

const localProgram = computed({
  get: () => props.program,
  set: (val) => emit('update:program', val)
})

const localSubject = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>
