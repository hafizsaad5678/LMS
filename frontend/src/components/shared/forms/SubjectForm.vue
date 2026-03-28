<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
      <h5 class="card-title mb-0 fw-semibold">
        <i class="bi bi-book me-2 text-admin"></i>
        Subject Information
      </h5>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="$emit('submit')">
        <!-- Basic Information -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-info-circle me-2"></i>Basic Information
          </h6>
          <div class="row g-3">
            <div class="col-md-8">
              <BaseInput v-model="modelValue.name" label="Subject Name" type="text" placeholder="e.g., Data Structures" :required="true" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.code" label="Subject Code" type="text" placeholder="e.g., CS201" :required="true" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model.number="modelValue.credit_hours" label="Credit Hours" type="number" placeholder="3" :required="true" />
            </div>
          </div>
        </div>

        <!-- Academic Placement -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-diagram-3 me-2"></i>Academic Placement
          </h6>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Department <span class="text-danger">*</span></label>
              <select v-model="localDepartment" class="form-select" required @change="onDeptChange">
                <option value="">Select Department</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }} ({{ dept.code }})</option>
              </select>
              <small class="text-muted">Step 1: Select department</small>
            </div>
            <div class="col-md-6">
              <label class="form-label">Course/Program <span class="text-danger">*</span></label>
              <select v-model="localProgram" class="form-select" required :disabled="!localDepartment" @change="onProgChange">
                <option value="">{{ !localDepartment ? 'Select Department First' : 'Select Course' }}</option>
                <option v-for="prog in filteredPrograms" :key="prog.id" :value="prog.id">{{ prog.name }} ({{ prog.code }})</option>
              </select>
              <small class="text-muted">Step 2: Select course</small>
            </div>
            <div class="col-md-6">
              <label class="form-label">Semester <span class="text-danger">*</span></label>
              <select v-model="modelValue.semester" class="form-select" required :disabled="!localProgram || loadingSemesters">
                <option value="">{{ loadingSemesters ? 'Loading...' : (!localProgram ? 'Select Course First' : 'Select Semester') }}</option>
                <option v-for="sem in semesters" :key="sem.id" :value="sem.id">{{ sem.name }} (Semester {{ sem.number }})</option>
              </select>
              <small class="text-muted">Step 3: Assign to semester</small>
            </div>
          </div>
          <div v-if="localProgram && semesters.length === 0 && !loadingSemesters" class="alert alert-warning mt-3">
            <i class="bi bi-exclamation-triangle me-2"></i>No semesters found. Create semesters first.
          </div>
        </div>

        <!-- Description -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-text-paragraph me-2"></i>Description
          </h6>
          <textarea v-model="modelValue.description" class="form-control" rows="4" placeholder="Enter subject description..."></textarea>
        </div>

        <!-- Form Actions -->
        <div class="d-flex gap-3 justify-content-end pt-3 border-top">
          <button type="button" @click="$emit('cancel')" class="btn btn-admin-outline px-4" :disabled="submitting">
            <i class="bi bi-x-circle me-2"></i>Cancel
          </button>
          <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
            <span v-if="submitting"><span class="spinner-border spinner-border-sm me-2"></span>{{ isEditMode ? 'Updating...' : 'Adding...' }}</span>
            <span v-else><i class="bi bi-check-circle me-2"></i>{{ isEditMode ? 'Update' : 'Add' }} Subject</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { BaseInput } from '@/components/shared/common'

const props = defineProps({
  modelValue: { type: Object, required: true },
  departments: { type: Array, default: () => [] },
  programs: { type: Array, default: () => [] },
  semesters: { type: Array, default: () => [] },
  selectedDepartment: { type: [String, Number], default: '' },
  selectedProgram: { type: [String, Number], default: '' },
  loadingSemesters: { type: Boolean, default: false },
  isEditMode: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel', 'department-change', 'program-change'])

// Local refs for two-way binding in template
const localDepartment = ref(props.selectedDepartment)
const localProgram = ref(props.selectedProgram)

watch(() => props.selectedDepartment, (val) => { localDepartment.value = val })
watch(() => props.selectedProgram, (val) => { localProgram.value = val })

const onDeptChange = () => emit('department-change', localDepartment.value)
const onProgChange = () => emit('program-change', localProgram.value)

const filteredPrograms = computed(() => {
  if (!localDepartment.value) return []
  return props.programs.filter(p => p.department === localDepartment.value || String(p.department) === String(localDepartment.value))
})
</script>
