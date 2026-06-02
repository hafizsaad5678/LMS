<template>
  <BaseModal :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" title="Grade Explanation & Breakdown" :show-footer="false">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2 text-muted">Retrieving assessment record history...</p>
    </div>
    
    <div v-else class="p-2">
      <!-- Student Info Card -->
      <div class="bg-light p-3 rounded-4 mb-3 border-start border-4 border-primary d-flex justify-content-between align-items-center">
        <div>
          <h6 class="fw-bold text-dark mb-1">{{ studentName }}</h6>
          <p class="text-muted small mb-0">ROLL NO: {{ studentEnrollment || '—' }}</p>
        </div>
        <div class="text-end">
          <span class="badge rounded-pill fw-bold px-3 py-1 mb-1" style="background-color: var(--teacher-primary-light) !important; color: var(--teacher-primary) !important;">
            Grade: {{ letterGrade || 'Pending' }}
          </span>
          <div class="small text-muted fw-bold" style="font-size: 0.75rem;">GPA: {{ computedGpa }}</div>
        </div>
      </div>

      <!-- Formula Breakdown Section -->
      <div class="mb-3">
        <div class="small text-muted text-uppercase fw-bold mb-2"><i class="bi bi-calculator me-1"></i> Formula Breakdown</div>
        
        <div class="border rounded-3 p-3 bg-light-subtle mb-3">
          <div class="row text-center">
            <div class="col-4 border-end">
              <div class="small text-muted text-uppercase fw-bold mb-1" style="font-size: 0.7rem;">Midterm</div>
              <div class="fw-bold text-dark">{{ midtermTotal.scaled.toFixed(2) }}</div>
              <div class="small text-muted">/ 40</div>
            </div>
            <div class="col-4 border-end">
              <div class="small text-muted text-uppercase fw-bold mb-1" style="font-size: 0.7rem;">Sessional</div>
              <div class="fw-bold text-dark">{{ sessionalTotal.scaled.toFixed(2) }}</div>
              <div class="small text-muted">/ 60</div>
            </div>
            <div class="col-4">
              <div class="small text-primary text-uppercase fw-bold mb-1" style="font-size: 0.7rem;">Total</div>
              <div class="fw-bold text-primary">{{ totalScaled.toFixed(2) }}</div>
              <div class="small text-muted">/ 100</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Component Scores -->
      <div class="mb-2">
        <div class="small text-muted text-uppercase fw-bold mb-2"><i class="bi bi-list-task me-1"></i> Detailed Scores</div>
        
        <div v-if="gradeModalData.length === 0" class="alert alert-light border py-2 px-3 small text-muted">
          No granular quizzes or assignments found for this student.
        </div>
        
        <div v-else class="accordion accordion-flush border rounded-3 overflow-hidden" id="accordionGradeDetails">
          <!-- Quizzes -->
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button bg-light-subtle fw-bold text-dark p-3 py-2 shadow-none" type="button" @click="toggleQuizzes" :class="{ collapsed: !quizzesExpanded }" style="font-size: 0.85rem;">
                <i class="bi bi-question-circle text-primary me-2"></i> Quizzes & Exams ({{ groupedGradeModalData.quiz.length }})
              </button>
            </h2>
            <div class="accordion-collapse collapse" :class="{ show: quizzesExpanded }">
              <div class="accordion-body p-0">
                <table class="table table-sm table-hover mb-0 align-middle small">
                  <thead class="table-light text-muted">
                    <tr>
                      <th class="ps-3 fw-normal">Name</th>
                      <th class="text-center fw-normal">Score</th>
                      <th class="text-center fw-normal">Weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="q in groupedGradeModalData.quiz" :key="q.id">
                      <td class="ps-3">{{ q.component_name || q.assignment_title }}</td>
                      <td class="text-center font-monospace">{{ q.marks_obtained }}/{{ q.max_marks || q.total_marks }}</td>
                      <td class="text-center font-monospace text-muted">{{ q.weightage ? q.weightage + '%' : '—' }}</td>
                    </tr>
                    <tr v-if="!groupedGradeModalData.quiz.length">
                      <td colspan="3" class="text-center py-2 text-muted">None</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Assignments -->
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button bg-light-subtle fw-bold text-dark p-3 py-2 shadow-none" type="button" @click="toggleAssignments" :class="{ collapsed: !assignmentsExpanded }" style="font-size: 0.85rem;">
                <i class="bi bi-file-earmark-text text-success me-2"></i> Assignments ({{ groupedGradeModalData.assignment.length }})
              </button>
            </h2>
            <div class="accordion-collapse collapse" :class="{ show: assignmentsExpanded }">
              <div class="accordion-body p-0">
                <table class="table table-sm table-hover mb-0 align-middle small">
                  <thead class="table-light text-muted">
                    <tr>
                      <th class="ps-3 fw-normal">Name</th>
                      <th class="text-center fw-normal">Score</th>
                      <th class="text-center fw-normal">Weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="a in groupedGradeModalData.assignment" :key="a.id">
                      <td class="ps-3">{{ a.component_name || a.assignment_title }}</td>
                      <td class="text-center font-monospace">{{ a.marks_obtained }}/{{ a.max_marks || a.total_marks }}</td>
                      <td class="text-center font-monospace text-muted">{{ a.weightage ? a.weightage + '%' : '—' }}</td>
                    </tr>
                    <tr v-if="!groupedGradeModalData.assignment.length">
                      <td colspan="3" class="text-center py-2 text-muted">None</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Midterms -->
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button bg-light-subtle fw-bold text-dark p-3 py-2 shadow-none" type="button" @click="toggleMidterm" :class="{ collapsed: !midtermExpanded }" style="font-size: 0.85rem;">
                <i class="bi bi-file-earmark-diff text-danger me-2"></i> Midterm Exams ({{ groupedGradeModalData.midterm.length }})
              </button>
            </h2>
            <div class="accordion-collapse collapse" :class="{ show: midtermExpanded }">
              <div class="accordion-body p-0">
                <table class="table table-sm table-hover mb-0 align-middle small">
                  <thead class="table-light text-muted">
                    <tr>
                      <th class="ps-3 fw-normal">Name</th>
                      <th class="text-center fw-normal">Score</th>
                      <th class="text-center fw-normal">Weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="m in groupedGradeModalData.midterm" :key="m.id">
                      <td class="ps-3">{{ m.component_name || m.assignment_title }}</td>
                      <td class="text-center font-monospace">{{ m.marks_obtained }}/{{ m.max_marks || m.total_marks }}</td>
                      <td class="text-center font-monospace text-muted">{{ m.weightage ? m.weightage + '%' : '—' }}</td>
                    </tr>
                    <tr v-if="!groupedGradeModalData.midterm.length">
                      <td colspan="3" class="text-center py-2 text-muted">None</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Other Components -->
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button bg-light-subtle fw-bold text-dark p-3 py-2 shadow-none" type="button" @click="toggleOther" :class="{ collapsed: !otherExpanded }" style="font-size: 0.85rem;">
                <i class="bi bi-collection text-secondary me-2"></i> Other Components ({{ groupedGradeModalData.other.length }})
              </button>
            </h2>
            <div class="accordion-collapse collapse" :class="{ show: otherExpanded }">
              <div class="accordion-body p-0">
                <table class="table table-sm table-hover mb-0 align-middle small">
                  <thead class="table-light text-muted">
                    <tr>
                      <th class="ps-3 fw-normal">Name</th>
                      <th class="text-center fw-normal">Score</th>
                      <th class="text-center fw-normal">Weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="o in groupedGradeModalData.other" :key="o.id">
                      <td class="ps-3">{{ o.component_name || o.assignment_title }}</td>
                      <td class="text-center font-monospace">{{ o.marks_obtained }}/{{ o.max_marks || o.total_marks }}</td>
                      <td class="text-center font-monospace text-muted">{{ o.weightage ? o.weightage + '%' : '—' }}</td>
                    </tr>
                    <tr v-if="!groupedGradeModalData.other.length">
                      <td colspan="3" class="text-center py-2 text-muted">None</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { BaseModal } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  studentId: { type: String, required: true },
  subjectId: { type: String, required: true },
  studentName: { type: String, required: true },
  studentEnrollment: { type: String, default: '' },
  midMarks: { type: [Number, String], default: 0 },
  midPaperMarks: { type: [Number, String], default: null },
  sessionalMarks: { type: [Number, String], default: 0 },
  totalMarks: { type: [Number, String], default: 0 },
  letterGrade: { type: String, default: 'Pending' },
  gpa: { type: [Number, String], default: null }
})

const emit = defineEmits(['update:modelValue'])

const gradeModalData = ref([])
const loading = ref(false)

const quizzesExpanded = ref(true)
const assignmentsExpanded = ref(true)
const midtermExpanded = ref(true)
const otherExpanded = ref(true)

const toggleQuizzes = () => quizzesExpanded.value = !quizzesExpanded.value
const toggleAssignments = () => assignmentsExpanded.value = !assignmentsExpanded.value
const toggleMidterm = () => midtermExpanded.value = !midtermExpanded.value
const toggleOther = () => otherExpanded.value = !otherExpanded.value

const computedGpa = computed(() => {
  if (props.gpa !== null && props.gpa !== undefined && props.gpa !== '') {
    return parseFloat(props.gpa).toFixed(2)
  }
  // Fallback map from letter grade to GPA
  const gpaMap = {
    'A+': 4.00, 'A': 4.00, 'A-': 3.70,
    'B+': 3.30, 'B': 3.00, 'B-': 2.70,
    'C+': 2.30, 'C': 2.00, 'C-': 1.70,
    'D': 1.00, 'F': 0.00, 'Pending': 0.00
  }
  const gradeKey = (props.letterGrade || 'Pending').trim().toUpperCase()
  return (gpaMap[gradeKey] !== undefined ? gpaMap[gradeKey] : 0.00).toFixed(2)
})

const groupedGradeModalData = computed(() => {
  const groups = {
    midterm: [],
    quiz: [],
    assignment: [],
    other: []
  }
  
  gradeModalData.value.forEach(item => {
    const type = item.component_type || 'other'
    if (groups[type]) {
      groups[type].push(item)
    } else {
      groups['other'].push(item)
    }
  })
  
  // Always inject the manual Mid Paper marks so it's transparent to the user
  // Prefer the freshly fetched value from SubjectResult (DB ground truth) over the prop
  const rawMidPaper = fetchedMidPaperMarks.value !== null && fetchedMidPaperMarks.value !== undefined 
    ? fetchedMidPaperMarks.value 
    : (props.midPaperMarks !== null && props.midPaperMarks !== undefined && props.midPaperMarks !== '' ? parseFloat(props.midPaperMarks) : 0)
  const midPaperVal = parseFloat(rawMidPaper) || 0
  
  groups.midterm.push({
    id: 'manual_mid_paper',
    component_name: 'Mid Paper (Manual Entry)',
    marks_obtained: midPaperVal.toFixed(2),
    max_marks: 20,
    weightage: 100 // Because this directly forms the 20 marks, we give it 100% of the midterm paper's sub-weight!
  })
  
  return groups
})

const midtermTotal = computed(() => {
  const groups = groupedGradeModalData.value
  const hasDetails = groups.quiz.length > 0 || groups.assignment.length > 0 || groups.midterm.length > 0
  if (!hasDetails) {
    const val = parseFloat(props.midMarks) || 0
    return { obtained: val, max: 40, pct: (val / 40) * 100, scaled: val }
  }
  
  // 1. Quizzes (out of 10)
  let quizVal = 0
  if (groups.quiz.length > 0) {
    let quizWeighted = 0
    let quizWeightSum = 0
    groups.quiz.forEach(item => {
      const max = parseFloat(item.max_marks || item.total_marks || 0)
      const obt = parseFloat(item.marks_obtained || 0)
      const weight = parseFloat(item.weightage || 0)
      if (max > 0) {
        const pct = (obt / max) * 100
        quizWeighted += pct * weight / 100
        quizWeightSum += weight
      }
    })
    if (quizWeightSum > 0) {
      const pct = (quizWeighted / quizWeightSum) * 100
      quizVal = (pct / 100) * 10
    } else {
      const max = groups.quiz.reduce((sum, item) => sum + parseFloat(item.max_marks || item.total_marks || 0), 0)
      const obtained = groups.quiz.reduce((sum, item) => sum + parseFloat(item.marks_obtained || 0), 0)
      const pct = max > 0 ? (obtained / max) * 100 : 0
      quizVal = (pct / 100) * 10
    }
  }

  // 2. Assignments (out of 10)
  let assignmentVal = 0
  if (groups.assignment.length > 0) {
    let assignmentWeighted = 0
    let assignmentWeightSum = 0
    groups.assignment.forEach(item => {
      const max = parseFloat(item.max_marks || item.total_marks || 0)
      const obt = parseFloat(item.marks_obtained || 0)
      const weight = parseFloat(item.weightage || 0)
      if (max > 0) {
        const pct = (obt / max) * 100
        assignmentWeighted += pct * weight / 100
        assignmentWeightSum += weight
      }
    })
    if (assignmentWeightSum > 0) {
      const pct = (assignmentWeighted / assignmentWeightSum) * 100
      assignmentVal = (pct / 100) * 10
    } else {
      const max = groups.assignment.reduce((sum, item) => sum + parseFloat(item.max_marks || item.total_marks || 0), 0)
      const obtained = groups.assignment.reduce((sum, item) => sum + parseFloat(item.marks_obtained || 0), 0)
      const pct = max > 0 ? (obtained / max) * 100 : 0
      assignmentVal = (pct / 100) * 10
    }
  }

  // 3. Midterm Paper (out of 20)
  let midtermPaperVal = 0
  if (groups.midterm.length > 0) {
    let midtermWeighted = 0
    let midtermWeightSum = 0
    groups.midterm.forEach(item => {
      const max = parseFloat(item.max_marks || item.total_marks || 0)
      const obt = parseFloat(item.marks_obtained || 0)
      const weight = parseFloat(item.weightage || 0)
      if (max > 0) {
        const pct = (obt / max) * 100
        midtermWeighted += pct * weight / 100
        midtermWeightSum += weight
      }
    })
    if (midtermWeightSum > 0) {
      const pct = (midtermWeighted / midtermWeightSum) * 100
      midtermPaperVal = (pct / 100) * 20
    } else {
      const max = groups.midterm.reduce((sum, item) => sum + parseFloat(item.max_marks || item.total_marks || 0), 0)
      const obtained = groups.midterm.reduce((sum, item) => sum + parseFloat(item.marks_obtained || 0), 0)
      const pct = max > 0 ? (obtained / max) * 100 : 0
      midtermPaperVal = (pct / 100) * 20
    }
  }
  
  const totalScaled = quizVal + assignmentVal + midtermPaperVal
  return { obtained: totalScaled, max: 40, pct: (totalScaled / 40) * 100, scaled: totalScaled }
})

const sessionalTotal = computed(() => {
  const val = parseFloat(props.sessionalMarks) || 0
  return { obtained: val, max: 60, pct: (val / 60) * 100, scaled: val }
})

const totalScaled = computed(() => {
  return midtermTotal.value.scaled + sessionalTotal.value.scaled
})

const fetchedMidPaperMarks = ref(null)

const fetchDetails = async () => {
  if (!props.modelValue || !props.studentId || !props.subjectId) return
  
  loading.value = true
  try {
    const params = {
      subject: props.subjectId,
      student: props.studentId
    }
    const [marksRes, resultsRes] = await Promise.all([
      teacherPanelService.getAllMarks(params),
      teacherPanelService.getSubjectResults(params)
    ])
    gradeModalData.value = marksRes.results || marksRes || []
    
    // Extract mid_paper_marks directly from SubjectResult (ground truth)
    const results = resultsRes.results || resultsRes || []
    if (results.length > 0) {
      const r = results[0]
      fetchedMidPaperMarks.value = r.mid_paper_marks !== null && r.mid_paper_marks !== undefined ? parseFloat(r.mid_paper_marks) : null
    }
  } catch (error) {
    console.error('Failed to fetch detailed grades:', error)
  } finally {
    loading.value = false
  }
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    fetchDetails()
  }
})

onMounted(() => {
  if (props.modelValue) {
    fetchDetails()
  }
})
</script>
