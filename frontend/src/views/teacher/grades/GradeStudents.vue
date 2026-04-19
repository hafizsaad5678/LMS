<template>
  <TeacherPageTemplate
    title="Assessment Manager"
    subtitle="Manage assessments and enter grades"
    icon="bi bi-clipboard-check"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Delete Assessment"
      message="This will delete all student grades associated with this assessment! Are you sure?"
      type="danger"
      theme="teacher"
      confirm-text="Delete"
      @confirm="confirmDeleteComponent"
    />

    <!-- Filters -->
    <ClassFilterCard
      v-model="selectedSubject"
      v-model:department="selectedDepartment"
      v-model:program="selectedProgram"
      :departments="departments"
      :programs="programs"
      :filtered-subjects="filteredSubjects"
      @change="loadComponents"
    />

    <div v-if="selectedSubject" class="row g-4 d-flex align-items-stretch">
      <!-- Left Sidebar: Assessments List -->
      <div class="col-lg-4 col-xl-3 d-flex flex-column">
        <AssessmentSidebar
          class="flex-grow-1"
          :items="components"
          :loading="loading"
          :selected-id="selectedComponent?.id"
          @create="openCreateModal"
          @select="openMarksEntry"
          @edit="editComponent"
          @delete="deleteComponent"
        />
      </div>

      <!-- Right Detail: Grading Interface -->
      <div class="col-lg-8 col-xl-9 d-flex flex-column">
        <div class="card border-0 shadow-sm flex-grow-1 min-h-600">
          <div v-if="!selectedComponent" class="card-body d-flex flex-column align-items-center justify-content-center py-5 text-center text-muted">
            <div class="bg-light rounded-circle p-4 mb-4">
              <i class="bi bi-arrow-left-circle display-4 text-teacher opacity-50"></i>
            </div>
            <h5>Select an assessment to start grading</h5>
            <p class="small mw-300">Choose from the list on the left to view students and enter marks for a specific component.</p>
          </div>

          <div v-else class="card-body p-4">
            <!-- Focused Header -->
            <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
              <div>
                <h5 class="fw-bold mb-1">{{ selectedComponent.name }}</h5>
                <div class="d-flex align-items-center gap-3">
                  <span class="small text-muted"><i class="bi bi-bullseye me-1"></i>Max Marks: <strong>{{ selectedComponent.max_marks }}</strong></span>
                  <span class="small text-muted"><i class="bi bi-people me-1"></i>Students: <strong>{{ marksData.length }}</strong></span>
                  <div class="vr mx-1"></div>
                  <div class="d-flex align-items-center small" :class="selectedComponent.is_visible_to_students ? 'text-success' : 'text-muted'">
                    <i class="bi" :class="selectedComponent.is_visible_to_students ? 'bi-eye-fill' : 'bi-eye-slash'"></i>
                    <span class="ms-1">{{ selectedComponent.is_visible_to_students ? 'Visible' : 'Hidden' }}</span>
                  </div>
                </div>
              </div>
              <div class="d-flex gap-2">
                <button @click="saveMarks" class="btn btn-teacher rounded-pill px-4 shadow-sm" :disabled="saving || !marksData.some(m => m.is_dirty)">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-cloud-check me-2"></i>
                  Save Grades
                </button>
              </div>
            </div>

            <!-- Grading Table -->
            <GradingTable :marks-data="marksData" :max-marks="Number(selectedComponent.max_marks)" />
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State (No Subject Selected) -->
    <div v-else class="text-center py-5 mt-5">
      <div class="mb-4">
        <div class="bg-light rounded-circle p-5 d-inline-block shadow-sm mb-4">
          <i class="bi bi-journal-check display-1 text-teacher opacity-50"></i>
        </div>
      </div>
      <h3 class="fw-bold text-dark mb-2">Ready to Grade?</h3>
      <p class="text-muted mx-auto max-w-450">
        Choose a <span class="text-teacher fw-bold">Department</span> and <span class="text-teacher fw-bold">Class</span> above to view your assessments and start entering student marks.
      </p>
    </div>

    <!-- Create/Edit Modal -->
    <AssessmentFormModal
      v-model="showModal"
      :form="form"
      :subjects="filteredSubjects"
      :is-editing="isEditing"
      :loading="submitting"
      @submit="submitComponent"
    />
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { ClassFilterCard, AssessmentSidebar, AssessmentFormModal } from '@/components/teacher/shared'
import GradingTable from '@/components/teacher/grades/GradingTable.vue'
import { useClassFilters } from '@/composables/teacher/useClassFilters'
import { useCrudModal } from '@/composables/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

// Use composables
const { 
  departments, 
  programs, 
  selectedDepartment, 
  selectedProgram, 
  selectedSubject, 
  filteredSubjects, 
  loadClasses 
} = useClassFilters()

// State
const components = ref([])
const loading = ref(false)
const selectedComponent = ref(null)
const marksData = ref([])
const saving = ref(false)

const loadComponents = async () => {
  if (!selectedSubject.value) return
  loading.value = true
  try {
    const res = await teacherPanelService.getComponents({ subject: selectedSubject.value })
    components.value = res.results || res || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// Use CRUD modal composable
const {
  alert,
  showSuccess,
  showError,
  showInfo,
  showModal,
  showConfirmDialog,
  editMode: isEditing,
  submitting,
  form,
  selectedItem: componentToDelete,
  openCreateModal,
  openEditModal,
  handleSubmit: submitComponent,
  confirmDelete: deleteComponent,
  handleDelete: confirmDeleteComponent
} = useCrudModal({
  entityName: 'Assessment',
  createFn: (data) => teacherPanelService.createComponent({ ...data, subject: selectedSubject.value }),
  updateFn: teacherPanelService.updateComponent,
  deleteFn: teacherPanelService.deleteComponent,
  onSuccess: loadComponents,
  defaultForm: {
    name: '',
    component_type: 'quiz',
    max_marks: 10,
    weightage: 0,
    is_visible_to_students: false,
    status: 'draft',
    description: ''
  }
})


// Breadcrumbs and Actions for TeacherPageTemplate
const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: TEACHER_ROUTES.GRADE_MANAGEMENT.path },
  { name: 'Grade Students' }
]

const actions = computed(() => {
  if (!selectedSubject.value) return []
  return [
    {
      label: 'New Assessment',
      icon: 'bi bi-plus-lg',
      variant: 'btn-teacher-outline',
      onClick: () => openCreateModal()
    }
  ]
})

const editComponent = (comp) => {
  openEditModal({ ...comp, subject: comp.subject || selectedSubject.value })
}
const openMarksEntry = async (comp) => {
  selectedComponent.value = comp
  marksData.value = []
  
  try {
    await teacherPanelService.initializeStudents(comp.id)
    const res = await teacherPanelService.getComponentMarks(comp.id)
    const marks = Array.isArray(res) ? res : (res.results || [])
    
    marksData.value = marks.map(m => ({
      ...m,
      is_dirty: false,
      is_locked: m.is_locked || false
    }))
  } catch (e) {
    console.error(e)
    showError('Failed to load marks')
  }
}

const saveMarks = async () => {
  const dirtyRows = marksData.value.filter(m => m.is_dirty)
  if (dirtyRows.length === 0) {
    showInfo('No changes to save')
    return
  }
  
  saving.value = true
  try {
    const payload = dirtyRows.map(m => ({
      student_id: m.student,
      marks_obtained: m.marks_obtained,
      remarks: m.remarks,
      is_locked: m.is_locked || false
    }))
    
    await teacherPanelService.bulkUpdateMarks(selectedComponent.value.id, payload)
    marksData.value.forEach(m => m.is_dirty = false)
    showSuccess('Grades saved successfully!')
    
    // Auto-redirect to Grade Management
    setTimeout(() => {
      router.push(TEACHER_ROUTES.GRADE_MANAGEMENT.path)
    }, 1500)
  } catch (e) {
    showError('Failed to save grades')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadClasses()
  
  // Check for query parameters from route
  const route = router.currentRoute.value
  if (route.query.subject) {
    selectedSubject.value = route.query.subject
    await loadComponents()
    
    // If component ID is provided, open it directly
    if (route.query.component) {
      const comp = components.value.find(c => c.id === route.query.component)
      if (comp) {
        await openMarksEntry(comp)
      }
    }
  }
})
</script>

