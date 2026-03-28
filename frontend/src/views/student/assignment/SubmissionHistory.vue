<template>
  <StudentPageTemplate
    :title="
      studentName ? `Submission History: ${studentName}` : 'Submission History'
    "
    subtitle="View all your past assignment submissions and grades"
    icon="bi bi-clock-history"
    :breadcrumbs="breadcrumbs"
  >
    <!-- Stats Section -->
    <div class="row g-4 mb-4">
      <div v-for="stat in statsCards" :key="stat.title" class="col-md-3">
        <StatCard v-bind="stat" />
      </div>
    </div>

    <!-- Filters Section -->
    <div class="px-2 pt-1 pb-2">
      <SearchFilter
        v-model="searchQuery"
        :show-card="false"
        theme="student"
        @refresh="loadData"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4">
            <SelectInput
              v-model="filterStatus"
              :options="SUBMISSION_STATUS_OPTIONS"
              placeholder="All Submissions"
              :no-margin="true"
              @change="resetPagination"
            />
          </div>
        </template>
      </SearchFilter>
    </div>

    <!-- Submissions List -->
    <div v-if="loading" class="text-center py-5">
      <LoadingSpinner color="primary" />
    </div>

    <AlertMessage
      v-else-if="error"
      type="error"
      :message="error"
      title="Error"
    />

    <EmptyState
      v-else-if="filteredSubmissions.length === 0"
      title="No Submissions Found"
      message="You haven't submitted any assignments yet or no records match your criteria."
      icon="bi bi-folder2-open"
    />

    <div v-else class="row g-4 mt-2">
      <div v-for="sub in paginatedSubmissions" :key="sub.id" class="col-md-6 col-lg-4">
        <div class="submission-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
          <StudentStatusCardHeader
            :header-class="sub.grade ? 'bg-success-light' : 'bg-student-light'"
            :icon-class="`bi bi-${sub.grade ? 'check-circle-fill' : 'hourglass-split'}`"
            :badge-class="sub.grade ? 'bg-success text-white' : 'bg-student text-white'"
            :badge-text="sub.grade ? 'Graded' : 'Submitted'"
            :title-class="sub.grade ? 'text-success' : 'text-student'"
            :subtitle-class="sub.grade ? 'text-success-50' : 'text-student-50'"
          >
            <template #title>{{ sub.assignment_title || sub.assignment?.title }}</template>
            <template #subtitle>
              <i class="bi bi-book me-1"></i>{{ sub.subject_name || sub.assignment?.subject?.name }}
            </template>
          </StudentStatusCardHeader>

          <!-- Card Body -->
          <div class="card-body p-4 d-flex flex-column">
            <div class="submission-meta d-flex flex-wrap gap-3 mb-3">
              <div class="meta-item">
                <i class="bi bi-calendar-check text-muted me-1"></i>
                <span class="small text-muted">{{ formatDate(sub.submitted_at) }}</span>
              </div>
              <div v-if="sub.grade" class="meta-item">
                <i class="bi bi-award text-success me-1"></i>
                <span class="small fw-bold text-success">{{ sub.grade.marks_obtained }}/{{ sub.grade.total_marks }}</span>
              </div>
              <div v-else class="meta-item">
                <i class="bi bi-clock-history text-muted me-1"></i>
                <span class="small text-muted fst-italic">Pending</span>
              </div>
            </div>

            <div class="submission-comments bg-light p-3 rounded-3 mb-4 flex-grow-1">
              <small class="text-muted d-block mb-1 fw-bold text-uppercase letter-spacing-1 text-xxs-70">My Comments</small>
              <p class="small mb-0 text-dark overflow-hidden text-truncate-2" v-if="sub.comments">
                {{ sub.comments }}
              </p>
              <p class="small text-muted mb-0 fst-italic" v-else>
                No comments provided
              </p>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex gap-2">
              <button class="btn btn-outline-light text-dark border-secondary-subtle flex-grow-1 rounded-3 py-2 small" @click="toggleExpand(sub.id)">
                <i :class="`bi bi-chevron-${expandedId === sub.id ? 'up' : 'down'} me-1`"></i> Details
              </button>

              <button 
                v-if="sub.file_upload || sub.file_url"
                class="btn btn-student flex-grow-1 rounded-3 py-2 fw-bold" 
                @click="downloadSubmission(sub)"
              >
                <i class="bi bi-download me-1"></i>
                Download
              </button>
            </div>
          </div>

          <!-- Expandable Details Overlay -->
          <div v-if="expandedId === sub.id" class="px-4 pb-4 animate__animated animate__fadeIn">
             <div class="row g-3 pt-3 border-top mt-1">
                <div class="col-md-6" v-if="sub.comments">
                  <h6 class="text-student small fw-bold mb-2">My Submission</h6>
                  <div class="p-3 bg-light rounded-3 small text-break" v-html="sub.comments"></div>
                </div>
                
                <div class="col-md-6" v-if="sub.grade">
                  <h6 class="text-success small fw-bold mb-2">Grade Details</h6>
                  <div class="p-3 bg-success-light border border-success-subtle rounded-3 small">
                    <div class="mb-2">
                       <small class="text-muted d-block">Score:</small>
                       <span class="fw-bold">{{ sub.grade.marks_obtained }}/{{ sub.grade.total_marks }}</span>
                    </div>
                    <div v-if="sub.grade.feedback">
                       <small class="text-muted d-block">Teacher Feedback:</small>
                       <div class="mt-1" v-html="sub.grade.feedback"></div>
                    </div>
                  </div>
                </div>
                
                <div class="col-12 text-center py-3" v-else>
                  <i class="bi bi-clock-history text-warning fs-4 mb-1 d-block"></i>
                  <p class="mb-0 small fw-bold text-muted">Grading in Progress</p>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <Pagination
      v-if="totalPages > 1"
      :current-page="currentPage"
      :total-pages="totalPages"
      :display-pages="displayPages"
      theme="student"
      @change="changePage"
    />
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { smartSearch } from "@/utils";
import { api, studentService } from "@/services/shared";
import { StudentPageTemplate } from "@/components/shared/panels";
import {
  AlertMessage,
  StatCard,
  SearchFilter,
  SelectInput,
  LoadingSpinner,
  EmptyState,
  Pagination,
  BaseButton,
  StudentStatusCardHeader,
} from "@/components/shared/common";
import { usePagination } from "@/composables/shared";
import { useStudentId } from "@/composables/shared/domain/useStudentId";
import { formatDate as formatDateUtil } from "@/utils/formatters";
import { SUBMISSION_STATUS_OPTIONS } from "@/utils/constants/options";
import { getFileUrl } from "@/utils/constants/config";

const { studentId } = useStudentId();
const {
  currentPage,
  totalPages,
  displayPages,
  paginate,
  changePage,
  resetPagination,
} = usePagination({ pageSize: 10 });

const loading = ref(true);
const error = ref(null);
const submissions = ref([]);
const studentName = ref("");
const expandedId = ref(null);
const filterStatus = ref("");
const searchQuery = ref("");

const breadcrumbs = [
  { name: "Dashboard", href: "/student/dashboard" },
  { name: "Assignments", href: "/student/assignments" },
  { name: "Submission History" },
];

const statsCards = computed(() => {
  const graded = submissions.value.filter((s) => s.grade).length;
  const total = submissions.value.length;
  return [
    {
      title: "Total Submissions",
      value: total,
      icon: "bi bi-check-circle",
      type: "student",
    },
    { title: "Graded", value: graded, icon: "bi bi-star", type: "teacher" },
    {
      title: "Pending",
      value: total - graded,
      icon: "bi bi-hourglass",
      type: "finance",
    },
    {
      title: "Success Rate",
      value: total > 0 ? Math.round((graded / total) * 100) + "%" : "0%",
      icon: "bi bi-graph-up",
      iconColor: "text-success",
    },
  ];
});

const filteredSubmissions = computed(() => {
  let f = submissions.value;
  if (filterStatus.value === "graded") f = f.filter((s) => s.grade);
  else if (filterStatus.value === "pending") f = f.filter((s) => !s.grade);

  if (searchQuery.value) {
    f = f.filter(s => smartSearch(s, searchQuery.value, ['assignment_title', 'assignment.title']));
  }
  return f.sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at));
});

const paginatedSubmissions = computed(() =>
  paginate(filteredSubmissions.value)
);

const loadData = async () => {
  if (!studentId.value) return;
  loading.value = true;
  try {
    const [profile, response] = await Promise.all([
      studentService.getStudent(studentId.value),
      api.get("/submissions/", {
        params: {
          ordering: "-submitted_at",
        },
      }),
    ]);
    studentName.value = profile.full_name;
    submissions.value = Array.isArray(response.data)
      ? response.data
      : response.data.results || [];
  } catch (err) {
    console.error("Error loading submissions:", err);
    error.value = "Failed to load submission history.";
  } finally {
    loading.value = false;
  }
};

const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id;
};

const resetFilters = () => {
  filterStatus.value = "";
  searchQuery.value = "";
  resetPagination();
};

const formatDate = (date) => (date ? formatDateUtil(date) : "N/A");

const downloadSubmission = (sub) => {
  const url = sub.file_upload || sub.file_url;
  if (!url) return;
  window.open(getFileUrl(url), "_blank");
};

onMounted(loadData);
</script>


