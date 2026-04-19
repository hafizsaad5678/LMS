<template>
  <StudentPageTemplate
    title="My Assignments"
    subtitle="View and manage your subject assignments"
    icon="bi bi-clipboard-check"
    :breadcrumbs="breadcrumbs"
  >
    <!-- Filters Area -->
    <template #filters>
      <div class="px-2 pt-1 pb-2">
        <SearchFilter
          v-model="searchQuery"
          :status-value="statusFilter"
          :show-card="false"
          search-placeholder="Search assignments..."
          theme="student"
          @update:statusValue="onStatusFilterChange"
          @refresh="loadData"
          @reset="resetFilters"
        >
          <template #filters>
            <div class="col-md-4">
              <SelectInput
                v-model="filterStatus"
                :options="ASSIGNMENT_FILTER_OPTIONS"
                placeholder="All Assignments"
                :no-margin="true"
                @change="resetPagination"
              />
            </div>
          </template>
        </SearchFilter>
      </div>
    </template>

    <!-- Content Area -->
    <div v-if="loading" class="text-center py-5">
      <LoadingSpinner color="primary" message="Loading assignments..." />
    </div>

    <AlertMessage
      v-else-if="error"
      type="error"
      :message="error"
      title="Error"
    />

    <EmptyState
      v-else-if="filteredAssignments.length === 0"
      title="No Assignments Found"
      :message="
        searchQuery || filterStatus
          ? 'Try adjusting your filters'
          : 'No assignments available at the moment'
      "
    />

    <div v-else class="row g-4">
      <div
        v-for="assignment in paginatedAssignments"
        :key="assignment.id"
        class="col-md-6 col-lg-4"
      >
        <div class="assignment-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
          <StudentStatusCardHeader
            :header-class="getStatusBgClass(assignment)"
            :icon-class="`bi bi-${getStatusIcon(assignment)}`"
            :badge-class="`bg-${getStatusColor(assignment)} text-white`"
            :badge-text="getStatusText(assignment)"
            :title-class="'text-' + getStatusColor(assignment)"
            :subtitle-class="'text-' + getStatusColor(assignment) + '-50'"
          >
            <template #title>{{ assignment.title }}</template>
            <template #subtitle>
              <i class="bi bi-book me-1"></i>{{ assignment.subject_name || assignment.subject?.name }}
            </template>
          </StudentStatusCardHeader>

          <!-- Card Body -->
          <div class="card-body p-4 d-flex flex-column">
            <div class="assignment-meta d-flex flex-wrap gap-3 mb-3">
              <div class="meta-item">
                <i class="bi bi-calendar-event text-muted me-1"></i>
                <span class="small text-muted" :class="getDueDateClass(assignment)">
                  {{ formatDate(assignment.due_date) }}
                </span>
              </div>
              <div class="meta-item">
                <i class="bi bi-award text-muted me-1"></i>
                <span class="small text-muted">{{ assignment.total_marks }} Marks</span>
              </div>
            </div>

            <p class="description-preview text-muted small mb-4 flex-grow-1">
              {{
                assignment.description?.replace(/<[^>]*>/g, "").slice(0, 100) + (assignment.description?.length > 100 ? '...' : '') ||
                "No instructions provided."
              }}
            </p>

            <!-- Action Buttons -->
            <div class="d-flex gap-2">
              <button class="btn btn-outline-light text-dark border-secondary-subtle flex-grow-1 rounded-3 py-2 small" @click="viewDetails(assignment)">
                <i class="bi bi-info-circle me-1"></i> Details
              </button>

              <button
                v-if="assignment.material_file_url"
                class="btn btn-outline-primary rounded-3 py-2 small"
                @click="openMaterial(assignment)"
                title="Download material"
              >
                <i class="bi bi-paperclip"></i>
              </button>

              <button 
                v-if="!isSubmitted(assignment)"
                class="btn flex-grow-1 rounded-3 py-2 fw-bold" 
                :class="isOverdue(assignment) ? 'btn-danger disabled' : 'btn-student'"
                @click="submitAssignment(assignment)"
                :disabled="isOverdue(assignment)"
              >
                <i class="bi bi-cloud-upload me-1"></i>
                {{ isOverdue(assignment) ? 'Overdue' : 'Submit' }}
              </button>

              <button 
                v-else
                class="btn btn-outline-success flex-grow-1 rounded-3 py-2 fw-bold" 
                disabled
              >
                <i class="bi bi-check2-circle me-1"></i> Turned In
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <BaseModal
      v-model="showDetailsModal"
      :title="selectedAssignment?.title || 'Assignment Details'"
      size="lg"
      variant="student"
    >
      <div v-if="selectedAssignment" class="assignment-details-modal p-2 p-md-3">
        <div class="row g-3 mb-3">
          <div class="col-6 col-md-3">
            <div class="detail-chip card border-0 bg-light h-100">
              <div class="card-body p-3">
                <small class="text-muted d-block mb-1">Due Date</small>
                <div class="fw-semibold" :class="getDueDateClass(selectedAssignment)">
                  <i class="bi bi-calendar-event me-1"></i>{{ formatDate(selectedAssignment.due_date) }}
                </div>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="detail-chip card border-0 bg-light h-100">
              <div class="card-body p-3">
                <small class="text-muted d-block mb-1">Total Marks</small>
                <div class="fw-semibold">
                  <i class="bi bi-award text-student me-1"></i>{{ selectedAssignment.total_marks || 100 }}
                </div>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="detail-chip card border-0 bg-light h-100">
              <div class="card-body p-3">
                <small class="text-muted d-block mb-1">Status</small>
                <span class="badge rounded-pill px-3 py-2" :class="`bg-${getStatusColor(selectedAssignment)}`">
                  {{ getStatusText(selectedAssignment) }}
                </span>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="detail-chip card border-0 bg-light h-100">
              <div class="card-body p-3">
                <small class="text-muted d-block mb-1">Subject</small>
                <div class="fw-semibold text-truncate">
                  <i class="bi bi-book text-student me-1"></i>{{ selectedAssignment.subject_name || selectedAssignment.subject?.name }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-3 align-items-stretch">
          <div class="col-lg-8">
            <div class="card border-0 bg-light h-100">
              <div class="card-body p-3 p-md-4">
                <h6 class="text-uppercase text-muted fw-bold small mb-3">
                  <i class="bi bi-file-text me-2"></i>Description & Instructions
                </h6>
                <div
                  class="description-content text-break"
                  v-html="selectedAssignment.description || '<p class=\'text-muted fst-italic mb-0\'>No description provided.</p>'"
                ></div>
              </div>
            </div>
          </div>

          <div class="col-lg-4">
            <div class="card border-0 bg-light h-100">
              <div class="card-body p-3 p-md-4 d-flex flex-column">
                <h6 class="text-uppercase text-muted fw-bold small mb-3">
                  <i class="bi bi-paperclip me-2"></i>Resources
                </h6>

                <div v-if="selectedAssignment.material_file_url" class="mt-1">
                  <button
                    class="btn btn-outline-primary btn-sm w-100 text-start d-flex align-items-center justify-content-between"
                    @click="openMaterial(selectedAssignment)"
                  >
                    <span class="text-truncate me-2">
                      {{ selectedAssignment.material_file_name || 'Download Material' }}
                    </span>
                    <i class="bi bi-download"></i>
                  </button>
                </div>

                <div v-else class="text-muted small fst-italic">No attachment available.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="d-flex gap-2 w-100 justify-content-end">
          <BaseButton variant="secondary-outline" @click="showDetailsModal = false">
            Close
          </BaseButton>
          <BaseButton
            v-if="
              selectedAssignment &&
              !isSubmitted(selectedAssignment) &&
              !isOverdue(selectedAssignment)
            "
            variant="student"
            @click="submitAssignment(selectedAssignment)"
          >
            <i class="bi bi-send me-2"></i>Submit Now
          </BaseButton>
        </div>
      </template>
    </BaseModal>

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
import { useRouter } from "vue-router";
import { studentService } from "@/services/shared";
import { StudentPageTemplate } from "@/components/shared/panels";
import {
  BaseModal,
  AlertMessage,
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
import { ASSIGNMENT_FILTER_OPTIONS } from "@/utils/constants/options";
import { STUDENT_ROUTES } from "@/utils/constants/routes";
import {
  isAssignmentSubmitted as isSubmitted,
  isAssignmentOverdue as isOverdue,
  getAssignmentStatusText as getStatusText,
  getAssignmentStatusColor as getStatusColor,
  getAssignmentStatusBgClass as getStatusBgClass,
  getAssignmentStatusIcon as getStatusIcon,
  getDueDateClass,
} from "@/utils/badgeHelpers";

const router = useRouter();
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
const assignments = ref([]);
const filterStatus = ref("");
const statusFilter = ref("");
const searchQuery = ref("");
const showDetailsModal = ref(false);
const selectedAssignment = ref(null);

const breadcrumbs = [
  { name: "Dashboard", href: STUDENT_ROUTES.DASHBOARD.path },
  { name: "Assignments" },
];

const filteredAssignments = computed(() => {
  let filtered = [...assignments.value];

  const applyStatusFilter = (list, statusValue) => {
    if (!statusValue || statusValue === "all") return list;

    return list.filter((a) => {
      if (statusValue === "pending" || statusValue === "active") {
        return !isSubmitted(a) && !isOverdue(a);
      }
      if (statusValue === "submitted") return isSubmitted(a);
      if (statusValue === "overdue") return isOverdue(a) && !isSubmitted(a);
      if (statusValue === "inactive") return isSubmitted(a) || isOverdue(a);
      return true;
    });
  };

  filtered = applyStatusFilter(filtered, filterStatus.value);
  filtered = applyStatusFilter(filtered, statusFilter.value);

  if (searchQuery.value) {
    filtered = filtered.filter(a => smartSearch(a, searchQuery.value, ['title', 'subject_name']));
  }
  return filtered;
});

const paginatedAssignments = computed(() =>
  paginate(filteredAssignments.value)
);

const loadData = async () => {
  if (!studentId.value) return;
  loading.value = true;
  try {
    const response = await studentService.getAssignments(studentId.value);
    assignments.value = Array.isArray(response)
      ? response
      : response.results || [];
  } catch (err) {
    console.error("Error loading assignments:", err);
    error.value = "Failed to load assignments.";
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  filterStatus.value = "";
  statusFilter.value = "";
  searchQuery.value = "";
  resetPagination();
};

const onStatusFilterChange = (value) => {
  statusFilter.value = value;
  resetPagination();
};

const formatDate = (date) => (date ? formatDateUtil(date) : "No due date");

const submitAssignment = (assignment) => {
  showDetailsModal.value = false;
  setTimeout(() => {
    router.push({
      path: STUDENT_ROUTES.SUBMIT_ASSIGNMENT.path,
      query: { assignmentId: assignment.id },
    });
  }, 300);
};

const viewDetails = (assignment) => {
  selectedAssignment.value = assignment;
  showDetailsModal.value = true;
};

const getDownloadName = (assignment) => {
  if (assignment?.material_file_name) return assignment.material_file_name;

  const rawUrl = String(assignment?.material_file_url || "");
  const fromUrl = rawUrl.split("?")[0].split("#")[0].split("/").pop();
  if (fromUrl) return decodeURIComponent(fromUrl);

  return "assignment-material";
};

const openMaterial = async (assignment) => {
  const url = assignment?.material_file_url;
  if (!url) return;

  try {
    const response = await fetch(url, { method: "GET", credentials: "include" });
    if (!response.ok) throw new Error("Download request failed");

    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = getDownloadName(assignment);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(objectUrl);
  } catch (error) {
    console.error("Attachment download failed:", error);
    // Fallback to direct navigation if blob download fails.
    window.open(url, "_blank", "noopener");
  }
};

onMounted(loadData);
</script>

<style scoped>
.assignment-details-modal .description-content {
  min-height: 180px;
  line-height: 1.6;
}

.assignment-details-modal .detail-chip {
  border: 1px solid rgba(0, 0, 0, 0.04);
}
</style>



