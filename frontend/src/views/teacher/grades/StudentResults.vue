<template>
  <TeacherPageTemplate
    title="Pass/Fail Management"
    subtitle="Manage and declare pass/fail results for your students"
    icon="bi bi-award"
    :breadcrumbs="breadcrumbs"
  >
    <!-- Notifications -->
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="4000"
      @close="alert.show = false"
    />

    <!-- Subject Filters -->
    <ClassFilterCard
      v-model="selectedSubject"
      v-model:department="selectedDepartment"
      v-model:program="selectedProgram"
      :departments="departments"
      :programs="programs"
      :filtered-subjects="filteredSubjects"
      @change="onSubjectChange"
    />

    <div v-if="selectedSubject" class="card border-0 shadow-sm mt-4">
      <div class="card-body p-4">
        
        <!-- Header Actions -->
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
          <div>
            <h5 class="fw-bold mb-1">Spreadsheet Entry Grid</h5>
            <p class="text-muted small mb-0">{{ resultsData.length }} Students found. Pass cutoff is aggregate 50%.</p>
          </div>
          
          <div class="d-flex flex-wrap gap-2">
            <!-- CSV Bulk Import -->
            <button 
              class="btn btn-outline-success shadow-sm"
              @click="$refs.csvInput.click()"
              :disabled="loading"
            >
              <i class="bi bi-file-earmark-excel me-2"></i>
              Import CSV/Excel Sheet
            </button>
            <input 
              type="file" 
              ref="csvInput" 
              class="d-none" 
              accept=".csv,.txt" 
              @change="handleCSVUpload"
            >

            <button 
              class="btn btn-outline-teacher shadow-sm"
              @click="initializeResults"
              :disabled="loading || processingInit"
            >
              <span v-if="processingInit" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-person-lines-fill me-2"></i>
              Sync Enrolled Students
            </button>

            <button 
              class="btn btn-outline-teacher shadow-sm"
              @click="autoCalculateResults"
              :disabled="loading || processingCalc"
            >
              <span v-if="processingCalc" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-calculator me-2"></i>
              Auto-Calculate Results
            </button>
            
            <button 
              class="btn btn-teacher shadow-sm px-4"
              @click="saveResults"
              :disabled="loading || saving || !hasChanges"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-cloud-check me-2"></i>
              Save Changes
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-teacher" role="status"></div>
          <p class="mt-2 text-muted">Loading spreadsheet results...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="resultsData.length === 0" class="text-center py-5 text-muted">
          <div class="display-1 mb-3"><i class="bi bi-file-earmark-x"></i></div>
          <h5>No Results Found</h5>
          <p>Click "Sync Enrolled Students" to initialize result records for this subject.</p>
        </div>

        <!-- Results Spreadsheet Grid -->
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle border">
            <thead class="table-light text-muted small text-uppercase">
              <tr>
                <th style="width: 50px;" class="text-center">#</th>
                <th>Student</th>
                <th class="text-center" style="width: 120px;">Mid (40)</th>
                <th class="text-center" style="width: 120px;">Sessional (60)</th>
                <th class="text-center" style="width: 120px;">Total (100)</th>
                <th class="text-center" style="width: 90px;">Grade</th>
                <th class="text-center" style="width: 90px;">GPA</th>
                <th class="text-center" style="width: 110px;">Status</th>
                <th>Remarks</th>
                <th style="width: 100px;" class="text-center">Transcript</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in resultsData" :key="row.id">
                <td class="text-center text-muted fw-semibold">{{ index + 1 }}</td>
                <td>
                  <div class="d-flex align-items-center gap-2">
                    <div class="avatar bg-teacher-light text-teacher rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 35px; height: 35px;">
                      {{ getInitials(row.student_name) }}
                    </div>
                    <div>
                      <div class="fw-bold text-dark">{{ row.student_name }}</div>
                      <div class="small text-muted">{{ row.student_enrollment }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div 
                    class="form-control form-control-sm text-center font-monospace bg-light"
                    style="cursor: not-allowed; opacity: 0.85;"
                    title="Auto-calculated from Quizzes (10) + Assignments (10) + Mid Paper (20)"
                  >{{ row.mid_marks || 0 }}</div>
                </td>
                <td>
                  <input 
                    type="number" 
                    min="0" 
                    max="60" 
                    step="0.5"
                    v-model.number="row.sessional_marks"
                    @input="calculateRowResult(row); markDirty(row)"
                    class="form-control form-control-sm text-center font-monospace"
                    placeholder="0"
                  >
                </td>
                <td class="text-center">
                  <div class="d-flex flex-column align-items-center justify-content-center">
                    <span class="badge rounded-pill fw-bold px-2 py-1" :class="row.total_marks >= 50 ? 'badge-total-pass' : 'badge-total-fail'">
                      {{ row.total_marks !== null ? row.total_marks : 0 }} / 100
                    </span>
                  </div>
                </td>
                <td class="text-center">
                  <button 
                    @click="openGradeExplanationModal(row)"
                    class="btn btn-link fw-bold p-0 text-decoration-none shadow-none"
                    :class="getGradeColor(row.letter_grade)"
                    title="Click to view grade breakdown & assessments"
                    style="cursor: pointer; font-size: 1rem; transition: transform 0.2s; border: none; background: transparent;"
                    onmouseover="this.style.transform='scale(1.15)';"
                    onmouseout="this.style.transform='scale(1)';"
                  >
                    {{ row.letter_grade || '--' }}
                  </button>
                </td>
                <td class="text-center">
                  <span class="fw-semibold text-secondary font-monospace">{{ row.gpa !== null ? row.gpa.toFixed(2) : '0.00' }}</span>
                </td>
                <td class="text-center">
                  <select 
                    v-model="row.result" 
                    @change="markDirty(row)"
                    class="form-select form-select-sm fw-bold border-1 text-center py-1 px-2" 
                    :class="row.result === 'pass' ? 'badge-total-pass text-success border-success' : 'badge-total-fail text-danger border-danger'"
                    style="width: 105px; cursor: pointer; border-radius: 8px; font-size: 0.85rem; display: inline-block;"
                  >
                    <option value="pass" class="text-success fw-bold">PASS</option>
                    <option value="fail" class="text-danger fw-bold">FAIL</option>
                  </select>
                </td>
                <td>
                  <input 
                    type="text" 
                    v-model="row.remarks" 
                    @input="markDirty(row)"
                    class="form-control form-control-sm" 
                    placeholder="Remarks..."
                  >
                </td>
                <td class="text-center">
                  <button 
                    class="btn btn-sm btn-outline-teacher rounded-pill shadow-sm"
                    @click="openTranscriptModal(row)"
                    title="Upload Semester Transcript PDF & GPA"
                  >
                    <i class="bi bi-file-earmark-pdf"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- No Subject Selected -->
    <div v-else class="text-center py-5 mt-5">
      <div class="mb-4">
        <div class="bg-light rounded-circle p-5 d-inline-block shadow-sm mb-4">
          <i class="bi bi-journal-text display-1 text-teacher opacity-50"></i>
        </div>
      </div>
      <h3 class="fw-bold text-dark mb-2">Spreadsheet Result Entry</h3>
      <p class="text-muted mx-auto max-w-450">
        Choose a <span class="text-teacher fw-bold">Department</span> and <span class="text-teacher fw-bold">Class</span> above to start loading the spreadsheet grid.
      </p>
    </div>

    <!-- Transcript / PDF Upload Modal -->
    <BaseModal v-model="showModal" title="Semester History Result Upload" :show-footer="false">
      <div v-if="modalStudent" class="p-2">
        <div class="bg-light p-3 rounded-4 mb-4 border-start border-4 border-primary d-flex justify-content-between align-items-center">
          <div>
            <h6 class="fw-bold text-dark mb-1">{{ modalStudent.student_name }}</h6>
            <p class="text-muted small mb-0 font-monospace">ROLL NO: {{ modalStudent.student_enrollment }}</p>
          </div>
        </div>

        <form @submit.prevent="saveTranscript">
          <!-- SGPA and CGPA row -->
          <div class="row g-3 mb-3">
            <div class="col-6">
              <label class="form-label text-dark fw-semibold small">Semester GPA (SGPA)</label>
              <input 
                type="number" 
                step="0.01" 
                min="0" 
                max="4.0" 
                class="form-control" 
                v-model="modalSgpa" 
                placeholder="e.g. 3.75"
              >
            </div>
            <div class="col-6">
              <label class="form-label text-dark fw-semibold small">Cumulative GPA (CGPA)</label>
              <input 
                type="number" 
                step="0.01" 
                min="0" 
                max="4.0" 
                class="form-control" 
                v-model="modalCgpa" 
                placeholder="e.g. 3.58"
              >
            </div>
          </div>

          <!-- PDF/Image Upload -->
          <div class="mb-3">
            <label class="form-label text-dark fw-semibold small">Transcript / Result Document</label>
            <div 
              class="upload-area border border-dashed rounded-3 p-3 text-center bg-light cursor-pointer position-relative"
              @click="$refs.fileInput.click()"
            >
              <input 
                type="file" 
                ref="fileInput" 
                class="d-none" 
                accept="image/*,application/pdf" 
                @change="handleModalFileChange"
              >
              <div v-if="!modalFile" class="py-2 text-muted">
                <i class="bi bi-cloud-arrow-up display-6 text-primary mb-2 d-block"></i>
                <span class="small d-block text-primary fw-semibold">Click to upload Image or PDF</span>
                <span class="text-xs text-muted d-block mt-1">Images are converted automatically to PDF</span>
              </div>
              <div v-else class="py-2 text-success">
                <i class="bi bi-file-earmark-check-fill display-6 mb-2 d-block text-success"></i>
                <span class="small fw-semibold d-block text-truncate text-dark" style="max-width: 250px;">{{ modalFile.name }}</span>
                <span class="text-xs text-muted d-block mt-1" v-if="isImage">Auto-conversion to PDF enabled</span>
              </div>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="d-flex justify-content-end gap-2 mt-4 pt-3 border-top">
            <button type="button" class="btn btn-light px-4 rounded-pill fw-bold text-secondary border" @click="closeModal" :disabled="uploading">Cancel</button>
            <button type="submit" class="btn btn-primary px-4 rounded-pill fw-bold shadow-sm" :disabled="uploading || (!modalFile && !modalSgpa && !modalCgpa)">
              <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-cloud-upload me-2"></i>
              Upload Result
            </button>
          </div>
        </form>
      </div>
    </BaseModal>

    <!-- Detailed Grade Breakdown Modal -->
    <GradeBreakdownModal
      v-model="showGradeModal"
      v-if="showGradeModal && gradeModalStudent"
      :student-id="gradeModalStudent.student"
      :subject-id="selectedSubject"
      :student-name="gradeModalStudent.student_name"
      :student-enrollment="gradeModalStudent.student_enrollment"
      :mid-marks="gradeModalStudent.mid_marks"
      :sessional-marks="gradeModalStudent.sessional_marks"
      :total-marks="gradeModalStudent.total_marks"
      :letter-grade="gradeModalStudent.letter_grade"
      :gpa="gradeModalStudent.gpa"
    />

  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { jsPDF } from 'jspdf'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { ClassFilterCard } from '@/components/teacher/shared'
import { AlertMessage, BaseModal } from '@/components/shared/common'
import GradeBreakdownModal from '@/components/teacher/grades/GradeBreakdownModal.vue'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { useClassFilters } from '@/composables/teacher/useClassFilters'
import teacherPanelService from '@/services/teacher/teacherPanelService'

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: TEACHER_ROUTES.GRADE_MANAGEMENT.path },
  { name: 'Pass/Fail Management' }
]

const alert = ref({ show: false, type: '', title: '', message: '' })
const showAlert = (type, title, message) => {
  alert.value = { show: true, type, title, message }
}

const { 
  departments, 
  programs, 
  selectedDepartment, 
  selectedProgram, 
  selectedSubject, 
  filteredSubjects,
  loadClasses
} = useClassFilters()

onMounted(async () => {
  await loadClasses()
})

const loading = ref(false)
const saving = ref(false)
const processingInit = ref(false)
const processingCalc = ref(false)
const resultsData = ref([])

// Modal States
const showModal = ref(false)
const modalStudent = ref(null)
const modalFile = ref(null)
const modalSgpa = ref('')
const modalCgpa = ref('')
const isImage = ref(false)
const uploading = ref(false)

// Grade Explanation Modal States
const showGradeModal = ref(false)
const gradeModalStudent = ref(null)

const openGradeExplanationModal = (row) => {
  gradeModalStudent.value = row
  showGradeModal.value = true
}

const closeGradeModal = () => {
  showGradeModal.value = false
}

const hasChanges = computed(() => resultsData.value.some(r => r.isDirty))

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}

const getGradeColor = (grade) => {
  if (!grade) return 'text-muted'
  if (grade.startsWith('A')) return 'text-success'
  if (grade.startsWith('B')) return 'text-primary'
  if (grade.startsWith('C')) return 'text-warning text-dark'
  if (grade === 'F') return 'text-danger'
  return 'text-dark'
}

const markDirty = (row) => {
  row.isDirty = true
}

const selectedSubjectSemesterId = computed(() => {
  if (resultsData.value.length > 0) {
    return resultsData.value[0].semester
  }
  return null
})

const calculateRowResult = (row) => {
  // Clamp Mid Marks between 0 and 40
  if (row.mid_marks !== null && row.mid_marks !== undefined && row.mid_marks !== '') {
    let midVal = parseFloat(row.mid_marks)
    if (midVal > 40) {
      row.mid_marks = 40
    } else if (midVal < 0 || isNaN(midVal)) {
      row.mid_marks = 0
    }
  }

  // Clamp Sessional Marks between 0 and 60
  if (row.sessional_marks !== null && row.sessional_marks !== undefined && row.sessional_marks !== '') {
    let sessVal = parseFloat(row.sessional_marks)
    if (sessVal > 60) {
      row.sessional_marks = 60
    } else if (sessVal < 0 || isNaN(sessVal)) {
      row.sessional_marks = 0
    }
  }

  const mid = parseFloat(row.mid_marks) || 0
  const sess = parseFloat(row.sessional_marks) || 0
  row.total_marks = mid + sess
  row.percentage = row.total_marks

  const pct = row.percentage
  let grade = 'F'
  if (pct >= 90) grade = 'A+'
  else if (pct >= 85) grade = 'A'
  else if (pct >= 80) grade = 'A-'
  else if (pct >= 75) grade = 'B+'
  else if (pct >= 70) grade = 'B'
  else if (pct >= 65) grade = 'B-'
  else if (pct >= 60) grade = 'C+'
  else if (pct >= 55) grade = 'C'
  else if (pct >= 50) grade = 'C-'
  else if (pct >= 40) grade = 'D'
  
  row.letter_grade = grade

  const gpaMap = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0
  }
  row.gpa = gpaMap[grade] || 0.0
  row.result = row.total_marks >= 50 ? 'pass' : 'fail'
}

const loadResults = async () => {
  if (!selectedSubject.value) return
  
  loading.value = true
  try {
    const res = await teacherPanelService.getSubjectResults({ subject: selectedSubject.value })
    resultsData.value = (res.results || res).map(r => {
      const mid = r.mid_marks !== null && r.mid_marks !== undefined ? parseFloat(r.mid_marks) : null
      const sessional = r.sessional_marks !== null && r.sessional_marks !== undefined ? parseFloat(r.sessional_marks) : null
      const total = mid !== null || sessional !== null ? (mid || 0) + (sessional || 0) : null
      return {
        ...r,
        mid_marks: mid,
        sessional_marks: sessional,
        total_marks: total,
        gpa: r.gpa !== null ? parseFloat(r.gpa) : null,
        isDirty: false
      }
    })
  } catch (error) {
    showAlert('error', 'Error', 'Failed to load results. ' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

const onSubjectChange = () => {
  if (selectedSubject.value) {
    loadResults()
  } else {
    resultsData.value = []
  }
}

const initializeResults = async () => {
  if (!selectedSubject.value) return
  processingInit.value = true
  try {
    const res = await teacherPanelService.initializeSubjectResults(selectedSubject.value)
    showAlert('success', 'Initialized', res.message || 'Student records synchronized.')
    await loadResults()
  } catch (error) {
    showAlert('error', 'Error', 'Failed to initialize students. ' + (error.response?.data?.error || error.message))
  } finally {
    processingInit.value = false
  }
}

const autoCalculateResults = async () => {
  if (!selectedSubject.value) return
  processingCalc.value = true
  try {
    const res = await teacherPanelService.autoCalculateSubjectResults(selectedSubject.value)
    showAlert('success', 'Calculated', res.message || 'Auto-calculation complete.')
    await loadResults()
  } catch (error) {
    showAlert('error', 'Error', 'Failed to auto-calculate. ' + (error.response?.data?.error || error.message))
  } finally {
    processingCalc.value = false
  }
}

const saveResults = async () => {
  if (!selectedSubject.value || !hasChanges.value) return
  saving.value = true
  
  const dirtyRecords = resultsData.value.filter(r => r.isDirty).map(r => ({
    id: r.id,
    mid_marks: r.mid_marks,
    sessional_marks: r.sessional_marks,
    result: r.result,
    remarks: r.remarks
  }))

  try {
    await teacherPanelService.bulkUpdateSubjectResults(selectedSubject.value, dirtyRecords)
    showAlert('success', 'Saved', 'Grades spreadsheet updated successfully.')
    
    // Reset dirty flags
    resultsData.value.forEach(r => {
      if (r.isDirty) r.isDirty = false
    })
  } catch (error) {
    showAlert('error', 'Error', 'Failed to save changes. ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

// CSV Bulk Parser
const handleCSVUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target.result
    const lines = text.split(/\r?\n/)
    if (lines.length < 2) {
      showAlert('warning', 'Empty File', 'The uploaded file has no data.')
      return
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase())
    
    const enrollmentIdx = headers.findIndex(h => h.includes('enroll') || h.includes('id') || h.includes('roll'))
    const nameIdx = headers.findIndex(h => h.includes('name'))
    const midIdx = headers.findIndex(h => h.includes('mid'))
    const sessionalIdx = headers.findIndex(h => h.includes('session') || h.includes('sess'))

    if (enrollmentIdx === -1 && nameIdx === -1) {
      showAlert('error', 'Invalid Format', 'Could not find Enrollment Number or Student Name column.')
      return
    }
    if (midIdx === -1 && sessionalIdx === -1) {
      showAlert('error', 'Invalid Format', 'Could not find Mid Marks or Sessional Marks column.')
      return
    }

    let matchCount = 0
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue
      const cols = lines[i].split(',').map(c => c.trim())
      
      let student = null
      if (enrollmentIdx !== -1 && cols[enrollmentIdx]) {
        const val = cols[enrollmentIdx].toLowerCase()
        student = resultsData.value.find(r => r.student_enrollment.toLowerCase().includes(val) || val.includes(r.student_enrollment.toLowerCase()))
      }
      if (!student && nameIdx !== -1 && cols[nameIdx]) {
        const val = cols[nameIdx].toLowerCase()
        student = resultsData.value.find(r => r.student_name.toLowerCase().includes(val))
      }

      if (student) {
        if (midIdx !== -1 && cols[midIdx] !== undefined) {
          const val = parseFloat(cols[midIdx])
          if (!isNaN(val)) {
            student.mid_marks = val
          }
        }
        if (sessionalIdx !== -1 && cols[sessionalIdx] !== undefined) {
          const val = parseFloat(cols[sessionalIdx])
          if (!isNaN(val)) {
            student.sessional_marks = val
          }
        }
        calculateRowResult(student)
        student.isDirty = true
        matchCount++
      }
    }

    showAlert('success', 'Import Success', `Successfully imported marks for ${matchCount} student(s). Save changes to persist.`)
    event.target.value = ''
  }
  reader.readAsText(file)
}

// Modal actions
const openTranscriptModal = (row) => {
  modalStudent.value = row
  modalFile.value = null
  modalSgpa.value = ''
  modalCgpa.value = ''
  isImage.value = false
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  setTimeout(() => {
    modalStudent.value = null
    modalFile.value = null
  }, 300)
}

const handleModalFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  modalFile.value = file
  isImage.value = file.type.startsWith('image/')
}

const convertImageToPdf = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const doc = new jsPDF({
          orientation: img.width > img.height ? 'landscape' : 'portrait',
          unit: 'px',
          format: [img.width, img.height]
        })
        doc.addImage(e.target.result, 'JPEG', 0, 0, img.width, img.height)
        const pdfBlob = doc.output('blob')
        resolve(new File([pdfBlob], `${file.name.split('.')[0]}.pdf`, { type: 'application/pdf' }))
      }
      img.onerror = reject
      img.src = e.target.result
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const saveTranscript = async () => {
  if (!modalStudent.value || !selectedSubjectSemesterId.value) return
  uploading.value = true

  try {
    let finalFile = modalFile.value
    
    // Image-to-PDF Conversion using jsPDF in browser!
    if (finalFile && isImage.value) {
      finalFile = await convertImageToPdf(finalFile)
    }

    const formData = new FormData()
    formData.append('semester_id', selectedSubjectSemesterId.value)
    if (finalFile) {
      formData.append('result_pdf', finalFile, `${modalStudent.value.student_name.replace(/\s+/g, '_')}_result.pdf`)
    }
    if (modalSgpa.value !== null && modalSgpa.value !== '') {
      formData.append('sgpa', modalSgpa.value)
    }
    if (modalCgpa.value !== null && modalCgpa.value !== '') {
      formData.append('cgpa', modalCgpa.value)
    }

    await teacherPanelService.uploadSemesterResult(modalStudent.value.student, formData)
    
    showAlert('success', 'Upload Success', `Semester result PDF & GPA uploaded successfully for ${modalStudent.value.student_name}.`)
    closeModal()
  } catch (error) {
    showAlert('error', 'Upload Error', 'Failed to upload result. ' + (error.response?.data?.error || error.message))
  } finally {
    uploading.value = false
  }
}
</script>
