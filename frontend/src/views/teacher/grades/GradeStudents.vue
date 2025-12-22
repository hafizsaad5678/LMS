<template>
  <TeacherPageTemplate
    title="Grade Students"
    subtitle="Enter and manage student grades"
    icon="bi bi-award"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <div class="row g-4">
      <!-- Filters Card -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm sticky-top" style="top: 80px;">
          <div class="card-header bg-white border-bottom">
            <h6 class="mb-0 fw-semibold">
              <i class="bi bi-funnel me-2 text-teacher"></i>Filters
            </h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">Class</label>
              <select v-model="selectedClass" class="form-select">
                <option value="">Select a class...</option>
                <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                  {{ cls.name }}
                </option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label small fw-semibold">Assessment Type</label>
              <select v-model="assessmentType" class="form-select">
                <option value="assignment">Assignment</option>
                <option value="quiz">Quiz</option>
                <option value="midterm">Midterm</option>
                <option value="final">Final Exam</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label small fw-semibold">Assessment</label>
              <select v-model="selectedAssessment" class="form-select" :disabled="!selectedClass">
                <option value="">Select assessment...</option>
                <option v-for="assessment in assessments" :key="assessment.id" :value="assessment.id">
                  {{ assessment.title }}
                </option>
              </select>
            </div>

            <div v-if="selectedAssessment" class="alert alert-info border-0 small">
              <div class="mb-2"><strong>Total Marks:</strong> {{ currentAssessment?.total_marks }}</div>
              <div><strong>Students:</strong> {{ students.length }}</div>
            </div>

            <button @click="loadGrades" class="btn btn-teacher-primary w-100" :disabled="!selectedAssessment">
              <i class="bi bi-arrow-clockwise me-2"></i>Load Grades
            </button>
          </div>
        </div>
      </div>

      <!-- Grades Table -->
      <div class="col-lg-8">
        <div v-if="!selectedAssessment" class="text-center py-5">
          <i class="bi bi-award display-1 text-muted"></i>
          <h4 class="text-muted mt-3">Select Assessment</h4>
          <p class="text-muted">Choose a class and assessment to start grading</p>
        </div>

        <div v-else class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold">
                <i class="bi bi-table me-2 text-teacher"></i>Grade Entry
              </h6>
              <div class="d-flex gap-2">
                <span class="badge bg-success">{{ gradedCount }} Graded</span>
                <span class="badge bg-warning text-dark">{{ pendingCount }} Pending</span>
              </div>
            </div>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th style="width: 50px;">#</th>
                    <th>Student Name</th>
                    <th>Roll No</th>
                    <th class="text-center">Obtained Marks</th>
                    <th class="text-center">Percentage</th>
                    <th class="text-center">Grade</th>
                    <th>Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in students" :key="student.id">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar-circle avatar-circle-sm me-2">
                          {{ student.name.charAt(0) }}
                        </div>
                        <span class="fw-semibold">{{ student.name }}</span>
                      </div>
                    </td>
                    <td>{{ student.roll_no }}</td>
                    <td>
                      <input 
                        v-model.number="student.obtained_marks" 
                        type="number" 
                        class="form-control form-control-sm text-center"
                        :max="currentAssessment?.total_marks"
                        min="0"
                        @input="calculateGrade(student)"
                      >
                    </td>
                    <td class="text-center">
                      <span class="fw-semibold">{{ student.percentage }}%</span>
                    </td>
                    <td class="text-center">
                      <span :class="['badge', getGradeBadge(student.grade)]">
                        {{ student.grade }}
                      </span>
                    </td>
                    <td>
                      <input 
                        v-model="student.remarks" 
                        type="text" 
                        class="form-control form-control-sm"
                        placeholder="Optional remarks"
                      >
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="card-footer bg-white border-top">
            <div class="d-flex justify-content-between align-items-center">
              <div class="text-muted small">
                <i class="bi bi-info-circle me-1"></i>
                Changes are saved automatically
              </div>
              <div class="d-flex gap-2">
                <button @click="exportGrades" class="btn btn-outline-secondary">
                  <i class="bi bi-download me-2"></i>Export
                </button>
                <button @click="publishGrades" class="btn btn-teacher-primary" :disabled="publishing">
                  <span v-if="publishing">
                    <span class="spinner-border spinner-border-sm me-2"></span>Publishing...
                  </span>
                  <span v-else>
                    <i class="bi bi-send me-2"></i>Publish Grades
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import TeacherPageTemplate from '@/components/navbar/TeacherPageTemplate.vue'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/teacher/dashboard' },
  { name: 'Grades', href: '/teacher/grades/students' },
  { name: 'Grade Students' }
]

const actions = [
  { label: 'View Reports', icon: 'bi bi-graph-up', variant: 'btn-teacher-outline', onClick: () => router.push('/teacher/grades/report') }
]

const selectedClass = ref('')
const assessmentType = ref('assignment')
const selectedAssessment = ref('')
const publishing = ref(false)

const classes = ref([
  { id: 1, name: 'Data Structures - CS201' },
  { id: 2, name: 'Database Systems - CS301' },
  { id: 3, name: 'Web Development - CS202' }
])

const assessments = ref([
  { id: 1, title: 'Assignment 1 - Binary Trees', total_marks: 100 },
  { id: 2, title: 'Quiz 1 - Data Structures Basics', total_marks: 50 },
  { id: 3, title: 'Midterm Exam', total_marks: 100 }
])

const students = ref([])

const mockStudents = [
  { id: 1, name: 'Ahmed Ali', roll_no: 'CS-2023-001', obtained_marks: 85, percentage: 85, grade: 'A', remarks: '' },
  { id: 2, name: 'Fatima Khan', roll_no: 'CS-2023-002', obtained_marks: 92, percentage: 92, grade: 'A+', remarks: 'Excellent work' },
  { id: 3, name: 'Hassan Raza', roll_no: 'CS-2023-003', obtained_marks: 78, percentage: 78, grade: 'B+', remarks: '' },
  { id: 4, name: 'Ayesha Malik', roll_no: 'CS-2023-004', obtained_marks: 88, percentage: 88, grade: 'A', remarks: '' },
  { id: 5, name: 'Usman Ahmed', roll_no: 'CS-2023-005', obtained_marks: 0, percentage: 0, grade: 'F', remarks: 'Not submitted' }
]

const currentAssessment = computed(() => {
  return assessments.value.find(a => a.id === selectedAssessment.value)
})

const gradedCount = computed(() => students.value.filter(s => s.obtained_marks > 0).length)
const pendingCount = computed(() => students.value.filter(s => s.obtained_marks === 0).length)

watch(selectedClass, () => {
  selectedAssessment.value = ''
  students.value = []
})

const calculateGrade = (student) => {
  const totalMarks = currentAssessment.value?.total_marks || 100
  student.percentage = Math.round((student.obtained_marks / totalMarks) * 100)
  
  if (student.percentage >= 90) student.grade = 'A+'
  else if (student.percentage >= 85) student.grade = 'A'
  else if (student.percentage >= 80) student.grade = 'A-'
  else if (student.percentage >= 75) student.grade = 'B+'
  else if (student.percentage >= 70) student.grade = 'B'
  else if (student.percentage >= 65) student.grade = 'B-'
  else if (student.percentage >= 60) student.grade = 'C+'
  else if (student.percentage >= 55) student.grade = 'C'
  else if (student.percentage >= 50) student.grade = 'C-'
  else student.grade = 'F'
}

const getGradeBadge = (grade) => {
  if (grade.startsWith('A')) return 'bg-success'
  if (grade.startsWith('B')) return 'bg-info'
  if (grade.startsWith('C')) return 'bg-warning text-dark'
  return 'bg-danger'
}

const loadGrades = () => {
  students.value = JSON.parse(JSON.stringify(mockStudents))
}

const exportGrades = () => {
  alert('Exporting grades to CSV...')
}

const publishGrades = () => {
  publishing.value = true
  setTimeout(() => {
    publishing.value = false
    alert('Grades published successfully!')
  }, 1000)
}
</script>
