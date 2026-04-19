<template>
  <StudentPageTemplate
    title="GPA / CGPA Calculator"
    subtitle="Calculate GPA, CGPA, and GPA conversions with quick academic tools"
    icon="bi bi-calculator"
    :breadcrumbs="breadcrumbs"
  >
    <div class="row g-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm border-start-student-thick">
          <div class="card-body">
            <ul class="nav nav-pills gap-2 mb-4" role="tablist">
              <li class="nav-item" role="presentation">
                <button class="btn btn-sm" :class="activeTab === 'gpa' ? 'btn-student-primary' : 'btn-student-outline'" @click="activeTab = 'gpa'" type="button">
                  GPA Calculator
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="btn btn-sm" :class="activeTab === 'cgpa' ? 'btn-student-primary' : 'btn-student-outline'" @click="activeTab = 'cgpa'" type="button">
                  CGPA Calculator
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="btn btn-sm" :class="activeTab === 'grade' ? 'btn-student-primary' : 'btn-student-outline'" @click="activeTab = 'grade'" type="button">
                  Grade to GPA
                </button>
              </li>
            </ul>

            <div class="card border-0 bg-light mb-4">
              <div class="card-body py-3">
                <div class="row g-3 align-items-end">
                  <div class="col-md-6 col-lg-4">
                    <label class="form-label fw-semibold mb-1">Set Current GPA (Dashboard)</label>
                    <input
                      v-model.number="currentGpaOverride"
                      type="number"
                      min="0"
                      max="4"
                      step="0.01"
                      class="form-control"
                      placeholder="e.g. 3.25"
                    />
                  </div>
                  <div class="col-md-6 col-lg-4 d-flex gap-2">
                    <button class="btn btn-student-primary" @click="saveCurrentGpa">
                      <i class="bi bi-check2-circle me-1"></i>Set Current GPA
                    </button>
                    <button class="btn btn-student-outline" @click="clearCurrentGpa">Clear</button>
                  </div>
                  <div class="col-12" v-if="currentGpaMessage">
                    <div class="small" :class="currentGpaError ? 'text-danger' : 'text-success'">{{ currentGpaMessage }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'gpa'">
              <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-2">
                <h6 class="fw-bold mb-0">Enter Subjects</h6>
                <div class="d-flex gap-2">
                  <button class="btn btn-student-outline btn-sm" @click="addSubjectRow">
                    <i class="bi bi-plus-lg me-1"></i>Add Field
                  </button>
                  <button class="btn btn-student-outline btn-sm" @click="resetGpa">
                    <i class="bi bi-arrow-counterclockwise me-1"></i>Reset
                  </button>
                </div>
              </div>

              <div class="table-responsive">
                <table class="table table-bordered align-middle">
                  <thead class="bg-success text-white">
                    <tr>
                      <th class="w-10">#</th>
                      <th>Obtained Marks</th>
                      <th>Course Credit Hrs.</th>
                      <th class="w-10 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in gpaRows" :key="index">
                      <td>
                        {{ index + 1 }}
                      </td>
                      <td>
                        <input
                          v-model.number="row.obtainedMarks"
                          type="number"
                          min="0"
                          max="100"
                          step="0.01"
                          class="form-control"
                          placeholder="Enter obtained marks (out of 100)"
                        />
                      </td>
                      <td>
                        <select v-model.number="row.creditHours" class="form-select">
                          <option :value="null">Select Cr. Hrs.</option>
                          <option v-for="ch in creditHourOptions" :key="ch" :value="ch">{{ ch }}</option>
                        </select>
                      </td>
                      <td class="text-center">
                        <button
                          class="btn btn-sm btn-outline-danger"
                          @click="removeSubjectRow(index)"
                          :disabled="gpaRows.length === 1"
                          title="Delete row"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <p class="text-danger mt-3 mb-2">
                <strong>Disclaimer:</strong>
                This calculator is for facilitation only. Please verify results from official LMS/UMS records.
              </p>

              <div class="d-flex justify-content-end">
                <button class="btn btn-student-primary" @click="calculateGpa">Calculate GPA</button>
              </div>

              <div class="mt-3" v-if="gpaResultVisible">
                <div v-if="gpaError" class="alert alert-danger mb-0">{{ gpaError }}</div>
                <div v-else class="p-3 rounded bg-student-light border-start-student-thick text-success-emphasis fw-semibold">
                  <strong>Calculated GPA:</strong> {{ gpaResult }}
                  <span class="ms-3"><strong>Total Credits:</strong> {{ currentCredits }}</span>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'cgpa'">
              <div class="row g-3">
                <div class="col-md-3">
                  <label class="form-label fw-semibold">Previous CGPA</label>
                  <input v-model.number="cgpaForm.previousCgpa" type="number" min="0" max="4" step="0.01" class="form-control" />
                </div>
                <div class="col-md-3">
                  <label class="form-label fw-semibold">Previous Credits</label>
                  <input v-model.number="cgpaForm.previousCredits" type="number" min="0" step="0.5" class="form-control" />
                </div>
                <div class="col-md-3">
                  <label class="form-label fw-semibold">Current GPA</label>
                  <input v-model.number="cgpaForm.currentGpa" type="number" min="0" max="4" step="0.01" class="form-control" />
                </div>
                <div class="col-md-3">
                  <label class="form-label fw-semibold">Current Credit Hours</label>
                  <input v-model.number="cgpaForm.currentCredits" type="number" min="0" step="0.5" class="form-control" />
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-3">
                <button class="btn btn-student-outline" @click="resetCgpa">Reset</button>
                <button class="btn btn-student-primary" @click="calculateCgpa">Calculate CGPA</button>
              </div>

              <div class="mt-3" v-if="cgpaResultVisible">
                <div v-if="cgpaError" class="alert alert-danger mb-0">{{ cgpaError }}</div>
                <div v-else class="p-3 rounded bg-student-light border-start-student-thick text-success-emphasis fw-semibold">
                  <strong>Final CGPA:</strong> {{ cgpaResult }}
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'grade'">
              <div class="row g-3 mb-3 align-items-end">
                <div class="col-md-5">
                  <label class="form-label fw-semibold">Method</label>
                  <input type="text" class="form-control" value="Custom Set" readonly />
                </div>
              </div>

              <div class="card border-0 bg-light mb-3">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="fw-bold mb-0">Custom Set Mapping</h6>
                    <button class="btn btn-student-outline btn-sm" @click="addCustomGradeField">
                      <i class="bi bi-plus-lg me-1"></i>Add Field
                    </button>
                  </div>
                  <div class="table-responsive">
                    <table class="table table-sm table-bordered align-middle mb-0">
                      <thead class="table-light">
                        <tr>
                          <th>Grade</th>
                          <th>GPA Points</th>
                          <th class="text-center w-10">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, index) in customGradeScale" :key="`${row.grade}-${index}`">
                          <td>
                            <input v-model.trim="customGradeScale[index].grade" type="text" class="form-control form-control-sm" placeholder="e.g. A+" />
                          </td>
                          <td>
                            <input
                              v-model.number="customGradeScale[index].points"
                              type="number"
                              min="0"
                              max="4"
                              step="0.01"
                              class="form-control form-control-sm"
                              placeholder="Leave empty for non-GPA"
                            />
                          </td>
                          <td class="text-center">
                            <button
                              class="btn btn-sm btn-outline-danger"
                              @click="removeCustomGradeField(index)"
                              :disabled="customGradeScale.length === 1"
                              title="Delete mapping row"
                            >
                              <i class="bi bi-trash"></i>
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div class="table-responsive">
                <table class="table table-bordered align-middle">
                  <thead class="table-light">
                    <tr>
                      <th class="w-10">#</th>
                      <th>Grade</th>
                      <th>Credit Hours</th>
                      <th class="w-10 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in gradeRows" :key="index">
                      <td>{{ index + 1 }}</td>
                      <td>
                        <select v-model="row.grade" class="form-select">
                          <option value="">Select Grade</option>
                          <option v-for="grade in activeGradeOptions" :key="grade" :value="grade">{{ grade }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="row.creditHours" class="form-select">
                          <option :value="null">Select Cr. Hrs.</option>
                          <option v-for="ch in creditHourOptions" :key="ch" :value="ch">{{ ch }}</option>
                        </select>
                      </td>
                      <td class="text-center">
                        <button
                          class="btn btn-sm btn-outline-danger"
                          @click="removeGradeRow(index)"
                          :disabled="gradeRows.length === 1"
                          title="Delete row"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="d-flex gap-2 justify-content-md-end mt-3">
                <button class="btn btn-student-outline" @click="addGradeRow">
                  <i class="bi bi-plus-lg me-1"></i>Add Field
                </button>
                <button class="btn btn-student-outline" @click="resetGradeToGpa">Reset</button>
                <button class="btn btn-student-primary" @click="convertGradeToGpa">Check GPA</button>
              </div>

              <div class="mt-3" v-if="gradeResultVisible">
                <div v-if="gradeError" class="alert alert-danger mb-0">{{ gradeError }}</div>
                <div v-else class="p-3 rounded bg-student-light border-start-student-thick text-success-emphasis fw-semibold">
                  <strong>Calculated GPA (Custom Set):</strong> {{ gradeResult }}
                  <span class="ms-3"><strong>Total Credits:</strong> {{ gradeTotalCredits }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { StudentPageTemplate } from '@/components/shared/panels'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { STORAGE_KEYS, getUserId } from '@/utils/constants/storage'

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: STUDENT_ROUTES.MY_GRADES.path },
  { name: 'GPA / CGPA Calculator' }
]

const { studentId } = useStudentBase()
const resolvedStudentId = studentId || getUserId()

const activeTab = ref('gpa')
const creditHourOptions = [1, 2, 3, 4, 5, 6]

const set1GradeScale = [
  { grade: 'A+', points: 4.0 },
  { grade: 'A', points: 3.7 },
  { grade: 'B+', points: 3.4 },
  { grade: 'B', points: 3.0 },
  { grade: 'B-', points: 2.5 },
  { grade: 'C+', points: 2.0 },
  { grade: 'C', points: 1.5 },
  { grade: 'D', points: 1.0 },
  { grade: 'F', points: 0.0 },
  { grade: 'W', points: null },
  { grade: 'I', points: null },
  { grade: 'SA', points: null }
]

const customGradeScale = ref(set1GradeScale.map(row => ({ ...row })))
const makeDefaultGradeRows = () => [{ grade: '', creditHours: null }]
const gradeRows = ref(makeDefaultGradeRows())
const gradeResult = ref('0.00')
const gradeError = ref('')
const gradeResultVisible = ref(false)

const activeGradeScale = computed(() => {
  return customGradeScale.value
})

const activeGradeOptions = computed(() => {
  const seen = new Set()
  return activeGradeScale.value
    .map(row => String(row.grade || '').trim().toUpperCase())
    .filter((grade) => {
      if (!grade || seen.has(grade)) return false
      seen.add(grade)
      return true
    })
})

const gradeTotalCredits = computed(() => {
  return gradeRows.value.reduce((sum, row) => {
    const ch = Number(row.creditHours)
    return Number.isFinite(ch) && ch > 0 ? sum + ch : sum
  }, 0)
})

const makeDefaultRows = () => Array.from({ length: 6 }, () => ({ obtainedMarks: null, creditHours: null }))

const gpaRows = ref(makeDefaultRows())
const gpaResult = ref('0.00')
const gpaError = ref('')
const gpaResultVisible = ref(false)

const cgpaForm = ref({ previousCgpa: null, previousCredits: null, currentGpa: null, currentCredits: null })
const cgpaResult = ref('0.00')
const cgpaError = ref('')
const cgpaResultVisible = ref(false)

const currentCredits = computed(() => {
  return gpaRows.value.reduce((sum, row) => {
    const ch = Number(row.creditHours)
    return Number.isFinite(ch) && ch > 0 ? sum + ch : sum
  }, 0)
})

const currentGpaOverride = ref(null)
const currentGpaMessage = ref('')
const currentGpaError = ref(false)

const loadCurrentGpa = () => {
  if (!resolvedStudentId) return
  const saved = localStorage.getItem(STORAGE_KEYS.CURRENT_GPA(resolvedStudentId))
  if (saved !== null && saved !== '') {
    const parsed = Number(saved)
    if (Number.isFinite(parsed)) {
      currentGpaOverride.value = parsed
    }
  }
}

const saveCurrentGpa = () => {
  currentGpaMessage.value = ''
  currentGpaError.value = false

  if (!resolvedStudentId) {
    currentGpaError.value = true
    currentGpaMessage.value = 'Unable to identify student for saving GPA.'
    return
  }

  const value = Number(currentGpaOverride.value)
  if (!Number.isFinite(value) || value < 0 || value > 4) {
    currentGpaError.value = true
    currentGpaMessage.value = 'Current GPA must be between 0 and 4.'
    return
  }

  localStorage.setItem(STORAGE_KEYS.CURRENT_GPA(resolvedStudentId), value.toFixed(2))
  currentGpaOverride.value = Number(value.toFixed(2))
  currentGpaMessage.value = 'Current GPA saved. Dashboard card will show this value.'
}

const clearCurrentGpa = () => {
  currentGpaMessage.value = ''
  currentGpaError.value = false

  if (!resolvedStudentId) return
  localStorage.removeItem(STORAGE_KEYS.CURRENT_GPA(resolvedStudentId))
  currentGpaOverride.value = null
  currentGpaMessage.value = 'Saved Current GPA cleared. Dashboard will use server value.'
}

loadCurrentGpa()

const mapPercentageToGpa = (percentage) => {
  if (percentage >= 85) return 4.0
  if (percentage >= 80) return 3.7
  if (percentage >= 75) return 3.3
  if (percentage >= 70) return 3.0
  if (percentage >= 65) return 2.7
  if (percentage >= 61) return 2.3
  if (percentage >= 58) return 2.0
  if (percentage >= 55) return 1.7
  if (percentage >= 50) return 1.0
  return 0.0
}

const addSubjectRow = () => {
  gpaRows.value.push({ obtainedMarks: null, creditHours: null })
}

const removeSubjectRow = (index) => {
  if (gpaRows.value.length > 1) {
    gpaRows.value.splice(index, 1)
  }
}

const addCustomGradeField = () => {
  customGradeScale.value.push({ grade: '', points: null })
}

const removeCustomGradeField = (index) => {
  if (customGradeScale.value.length > 1) {
    customGradeScale.value.splice(index, 1)
  }
}

const addGradeRow = () => {
  gradeRows.value.push({ grade: '', creditHours: null })
}

const removeGradeRow = (index) => {
  if (gradeRows.value.length > 1) {
    gradeRows.value.splice(index, 1)
  }
}

const calculateGpa = () => {
  gpaError.value = ''
  gpaResultVisible.value = true

  const validRows = gpaRows.value.filter(r => r.obtainedMarks !== null && r.obtainedMarks !== '' && r.creditHours)
  if (validRows.length === 0) {
    gpaError.value = 'Please add at least one row with obtained marks and credit hours.'
    return
  }

  let totalQualityPoints = 0
  let totalCredits = 0

  for (const row of validRows) {
    const credits = Number(row.creditHours)
    const obtained = Number(row.obtainedMarks)
    const gradePoints = mapPercentageToGpa(obtained)

    if (!Number.isFinite(credits) || credits <= 0) {
      gpaError.value = 'Please provide valid credit hours for all rows.'
      return
    }

    if (!Number.isFinite(obtained) || obtained < 0 || obtained > 100) {
      gpaError.value = 'Obtained marks must be between 0 and 100.'
      return
    }

    totalQualityPoints += credits * gradePoints
    totalCredits += credits
  }

  if (totalCredits <= 0) {
    gpaError.value = 'Total credit hours must be greater than zero.'
    return
  }

  gpaResult.value = (totalQualityPoints / totalCredits).toFixed(2)
}

const calculateCgpa = () => {
  cgpaError.value = ''
  cgpaResultVisible.value = true

  const prevCgpa = Number(cgpaForm.value.previousCgpa)
  const prevCredits = Number(cgpaForm.value.previousCredits)
  const currGpa = Number(cgpaForm.value.currentGpa)
  const currCredits = Number(cgpaForm.value.currentCredits)

  if (!Number.isFinite(prevCgpa) || prevCgpa < 0 || prevCgpa > 4) {
    cgpaError.value = 'Previous CGPA must be between 0 and 4.'
    return
  }

  if (!Number.isFinite(prevCredits) || prevCredits <= 0) {
    cgpaError.value = 'Previous credits must be greater than zero.'
    return
  }

  if (!Number.isFinite(currGpa) || currGpa < 0 || currGpa > 4) {
    cgpaError.value = 'Current GPA must be between 0 and 4.'
    return
  }

  if (!Number.isFinite(currCredits) || currCredits <= 0) {
    cgpaError.value = 'Current credit hours must be greater than zero.'
    return
  }

  const finalCgpa = ((prevCgpa * prevCredits) + (currGpa * currCredits)) / (prevCredits + currCredits)
  cgpaResult.value = finalCgpa.toFixed(2)
}

const convertGradeToGpa = () => {
  gradeError.value = ''
  gradeResultVisible.value = true

  const validRows = gradeRows.value.filter(r => r.grade && r.creditHours)
  if (validRows.length === 0) {
    gradeError.value = 'Please add at least one row with grade and credit hours.'
    return
  }

  let totalQualityPoints = 0
  let totalCredits = 0

  for (const row of validRows) {
    const selectedGrade = String(row.grade).trim().toUpperCase()
    const selected = activeGradeScale.value.find(
      item => String(item.grade || '').trim().toUpperCase() === selectedGrade
    )

    if (!selected) {
      gradeError.value = `Invalid grade selection: ${row.grade}`
      return
    }

    if (selected.points === null || selected.points === undefined) {
      gradeError.value = `Grade ${selected.grade} is non-GPA (no points).`
      return
    }

    const points = Number(selected.points)
    const credits = Number(row.creditHours)

    if (!Number.isFinite(points) || points < 0 || points > 4) {
      gradeError.value = `Invalid GPA points for grade ${selected.grade}.`
      return
    }

    if (!Number.isFinite(credits) || credits <= 0) {
      gradeError.value = 'Please provide valid credit hours in all filled rows.'
      return
    }

    totalQualityPoints += points * credits
    totalCredits += credits
  }

  if (totalCredits <= 0) {
    gradeError.value = 'Total credits must be greater than zero.'
    return
  }

  gradeResult.value = (totalQualityPoints / totalCredits).toFixed(2)
}

const resetGpa = () => {
  gpaRows.value = makeDefaultRows()
  gpaResult.value = '0.00'
  gpaError.value = ''
  gpaResultVisible.value = false
}

const resetCgpa = () => {
  cgpaForm.value = { previousCgpa: null, previousCredits: null, currentGpa: null, currentCredits: null }
  cgpaResult.value = '0.00'
  cgpaError.value = ''
  cgpaResultVisible.value = false
}

const resetGradeToGpa = () => {
  customGradeScale.value = set1GradeScale.map(row => ({ ...row }))
  gradeRows.value = makeDefaultGradeRows()
  gradeResult.value = '0.00'
  gradeError.value = ''
  gradeResultVisible.value = false
}

watch(activeGradeOptions, (options) => {
  gradeRows.value = gradeRows.value.map((row) => {
    const normalized = String(row.grade || '').trim().toUpperCase()
    if (normalized && !options.includes(normalized)) {
      return { ...row, grade: '' }
    }
    return row
  })
})
</script>
