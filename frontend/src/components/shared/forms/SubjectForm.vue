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
              <SelectInput 
                v-model="localDepartment" 
                label="Department" 
                :options="deptOptions" 
                :required="true" 
                placeholder="Select Department"
                hint="Step 1: Select department"
                @change="onDeptChange" 
              />
            </div>
            <div class="col-md-6">
              <SelectInput 
                v-model="localProgram" 
                label="Course/Program" 
                :options="progOptions" 
                :required="true" 
                :disabled="!localDepartment"
                :placeholder="!localDepartment ? 'Select Department First' : 'Select Course'"
                hint="Step 2: Select course"
                @change="onProgChange" 
              />
            </div>
            <div class="col-md-6">
              <SelectInput 
                v-model="modelValue.semester" 
                label="Semester" 
                :options="semesterOptions" 
                :required="true" 
                :disabled="!localProgram || loadingSemesters"
                :placeholder="!localProgram ? 'Select Course First' : 'Select Semester'"
                hint="Step 3: Assign to semester"
              />
            </div>
          </div>
          <div v-if="localProgram && displaySemesters.length === 0 && !loadingSemesters" class="alert alert-warning mt-3">
            <i class="bi bi-exclamation-triangle me-2"></i>No semesters found. Create semesters first.
          </div>
        </div>

        <!-- Description -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-text-paragraph me-2"></i>Description
          </h6>
          <RichTextEditor 
            v-model="modelValue.description" 
            placeholder="Enter subject description..." 
          />
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
import { BaseInput, SelectInput, RichTextEditor } from '@/components/shared/common'

const props = defineProps({
  modelValue: { type: Object, required: true },
  departments: { type: Array, default: () => [] },
  programs: { type: Array, default: () => [] },
  semesters: { type: Array, default: () => [] },
  activeSemestersOnly: { type: Boolean, default: false },
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

const displaySemesters = computed(() => {
  if (!props.activeSemestersOnly) return props.semesters
  return props.semesters.filter((semester) => String(semester?.status || '').trim().toLowerCase() === 'active')
})

const filteredPrograms = computed(() => {
  if (!localDepartment.value) return []
  return props.programs.filter(p => p.department === localDepartment.value || String(p.department) === String(localDepartment.value))
})

// Mapped options for SelectInput
const deptOptions = computed(() => props.departments.map(d => ({ value: d.id, label: `${d.name} (${d.code})` })))
const progOptions = computed(() => filteredPrograms.value.map(p => ({ value: p.id, label: `${p.name} (${p.code})` })))
const semesterOptions = computed(() => displaySemesters.value.map(s => ({ value: s.id, label: `${s.name} (Semester ${s.number})` })))

watch([
  () => props.activeSemestersOnly,
  () => localProgram.value,
  () => displaySemesters.value.length
], () => {
  if (!props.activeSemestersOnly || !localProgram.value || props.modelValue?.semester) return
  const firstActive = displaySemesters.value[0]
  if (firstActive?.id) {
    props.modelValue.semester = String(firstActive.id)
  }
})
</script>
