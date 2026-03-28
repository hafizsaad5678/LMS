# Frontend Architecture & Memory Map

This document serves as the "brain" for the frontend architecture of the LMS project. AI assistants should read this file to immediately understand project structure, rules, and module locations without needing to scan 100+ individual files.

## 🏗️ 1. Global Core Rules & Conventions

1. **Search & Filtering Standard:**
   - **DO NOT** use raw strings like `array.filter(a => a.name.toLowerCase().includes(query))`.
   - **ALWAYS** use the `smartSearch()` utility from `utils/search.js` for ANY object filtering.
   - Prefer using `useEntityList.js` or `useFilterLogic.js` to manage pagination/filtering states dynamically.
2. **API Standard:**
   - All backend calls must be routed through the dedicated domain services in `src/services/`. NEVER write `axios.get` or `api.get` directly inside `.vue` files unless strictly isolated.
3. **Framework Context:**
   - Vue 3 (Composition API `setup` script), Vite bundler, Bootstrap/Custom CSS for UI.
4. **Import Protocol (Barrel Pattern):**
   - **DO NOT** import deeply nested files directly if an `index.js` exists.
   - _Example:_ Instead of `import { StudentForm } from '@/components/shared/forms/StudentForm.vue'`, strictly use `import { StudentForm } from '@/components/shared/forms'`.
   - Maintain the `index.js` barrel files when creating new utilities, forms, or composables.

---

## 📁 2. Full Folder and File Structure Overview

```text
src/
├── App.vue
├── main.js
├── ARCHITECTURE.md
│
├── components/
│   ├── shared/
│   │   ├── auth/ (ForgotPasswordForm.vue, LoginForm.vue, ResetPasswordForm.vue)
│   │   ├── common/
│   │   │   ├── feedback/ (AlertMessage.vue, BaseModal.vue, ConfirmDialog.vue, DeleteConfirmation.vue, EmptyState.vue)
│   │   │   ├── layout/ (BaseCard.vue, DashboardStatCard.vue, DataTable.vue, Pagination.vue, SearchFilter.vue, StatCard.vue)
│   │   │   ├── specialized/ (ActionButtons.vue, ActivityFeed.vue, EntityFormModal.vue, GenericListView.vue, QuickActionCard.vue)
│   │   │   └── ui/ (BaseButton.vue, BaseInput.vue, LoadingSpinner.vue, SelectInput.vue)
│   │   ├── forms/ (CourseForm.vue, DepartmentForm.vue, InstitutionForm.vue, StudentForm.vue, SubjectForm.vue, TeacherForm.vue)
│   │   ├── panels/
│   │   │   ├── layout/ (BasePageTemplate.vue, Navbar.vue, Sidebar.vue)
│   │   │   └── roles/ (AdminPageTemplate.vue, StudentPageTemplate.vue, TeacherPageTemplate.vue)
│   │   └── profile/ (InfoCard.vue, ProfileHeader.vue, StatsGrid.vue, SubjectsTable.vue)
│   └── teacher/
│       ├── grades/ (GradeDistributionChart.vue, GradingTable.vue, TopPerformersList.vue)
│       └── shared/ (AnnouncementFormModal.vue, AssessmentFormModal.vue, AssessmentSidebar.vue, ClassFilterCard.vue, ExamFormModal.vue)
│
├── composables/ (Vue Composition API Hooks - `.js`)
│   ├── shared/
│   │   ├── data/ (useEntityList.js, usePagination.js, useCrudModal.js, useAsyncState.js)
│   │   ├── domain/ (useStudentId.js, useSubjectEnrollment.js)
│   │   └── form/ (useEntityForm.js, useCascadingDropdowns.js)
│   ├── student/ (useStudentBase.js)
│   └── teacher/ (useAttendanceData.js, useFilterLogic.js, useGradeManagement.js)
│
├── layouts/ (AdminLayout.vue, DashboardLayout.vue, StudentLayout.vue, TeacherLayout.vue)
├── panels/ (admin.js, student.js, teacher.js)
├── router/ (index.js, routes/admin.js, routes/auth.js, routes/student.js, routes/teacher.js)
│
├── services/ (API Axios endpoints - `.js`)
│   ├── admin/ (adminPanelService.js, managementService.js)
│   ├── shared/
│   │   ├── academic/ (assignmentService.js, institutionService.js, subjectService.js, etc.)
│   │   ├── core/ (api.js, apiWrapper.js)
│   │   └── users/ (departmentService.js, studentService.js, teacherService.js)
│   ├── student/ (studentPanelService.js)
│   └── teacher/ (aiService.js, teacherPanelService.js)
│
├── utils/ (search.js, security.js, formatters.js, constants/config.js, options.js)
│
└── views/ (Full Page Templates - `.vue`)
    ├── admin/
    │   ├── academic/ (Events.vue, ExamList.vue, TimeTable.vue)
    │   ├── assignment/ (Add, Delete, Edit, List)
    │   ├── course/ (Add, CourseProfile, Delete, Edit, List)
    │   ├── dashboard/ (AdminDashboard.vue)
    │   ├── department/ (Add, DepartmentProfile, List)
    │   ├── institution/ (Add, Edit, List)
    │   ├── library/ (BookBorrowing.vue, Library.vue, LibraryBooks.vue)
    │   ├── management/ (Accounts.vue, Expenses.vue, FeesCollection.vue)
    │   ├── student/ (Add, Edit, List, Profile)
    │   ├── subject/ (Add, Edit, List, Profile)
    │   └── teacher/ (Add, Edit, List, Profile)
    │
    ├── student/
    │   ├── assignment/ (SubmissionHistory.vue, SubmitAssignment.vue, ViewAssignments.vue)
    │   ├── attendance/ (MyAttendance.vue)
    │   ├── communication/ (Announcements.vue)
    │   ├── dashboard/ (StudentDashboard.vue)
    │   ├── grades/ (MyGrade.vue, StudentGradeReport.vue)
    │   ├── library/ (LibraryCatalog.vue, MyBooks.vue)
    │   ├── quizzes/ (QuizList.vue, TakeQuiz.vue)
    │   ├── resources/ (CourseMaterial.vue, MaterialPreview.vue)
    │   └── schedule/ (ClassSchedule.vue, ExamSchedule.vue)
    │
    └── teacher/
        ├── assignment/ (AssignmentList.vue, CreateAssignment.vue, Submissions.vue)
        ├── attendance/ (AttendanceReport.vue, MarkAttendance.vue, StudentAttendance.vue)
        ├── class/ (AnnouncementList.vue, ClassList.vue, StudentList.vue)
        ├── dashboard/ (TeacherDashboard.vue)
        ├── grades/ (GradeManagement.vue, GradeReport.vue, GradeStudents.vue)
        ├── profiles/ (StudentProfile.vue, SubjectProfile.vue)
        ├── quizzes/ (AiQuizGenerator.vue, QuizBuilder.vue, QuizList.vue)
        ├── resources/ (MaterialDownload.vue, MaterialUpload.vue)
        └── schedule/ (ClassSchedule.vue)
```

---

## 🏛️ 3. Core Directory Purpose

### `src/utils/` (The Helpers)

- `search.js` -> Central multi-word, cross-field fuzzy search engine (`smartSearch`).
- `security.js` -> Input sanitization, debouncing.
- `formatters.js` -> Date, text, and data formatting.
- `constants/...` -> Routing constants, system options, and config vars.

### `src/composables/` (The Brains / Logic Wrappers)

- `shared/data/useEntityList.js` -> The master composable used across almost all views to handle fetching, loading states, pagination, and `smartSearch` integration automatically.
- `teacher/useFilterLogic.js` / `useAttendanceData.js` -> Teacher-specific logic for parsing class lists and calculating stats.

### `src/services/` (The Data Layer)

- `shared/core/api.js` -> Axios instance setup & interceptors.
- `admin/adminPanelService.js` / `managementService.js` -> Admin endpoints.
- `teacher/teacherPanelService.js` / `aiService.js` -> Teacher endpoints (including LLM quizzing).
- `student/studentPanelService.js` -> Student endpoints.

### `src/components/` (Reusable UI)

- `shared/common/` -> Universal cards, modals, pagination, search inputs, empty states, and tables used heavily across the platform.

---

## 🧭 4. Module Breakdown (Routing & Views)

### 🍎 Admin Panel (`src/views/admin/`)

_Role: Standard CRUD operations, system onboarding, global management._

- **Academic:** Events, Exams, Holidays, TimeTable.
- **Assignments:** Add/Edit/List Assignments globally.
- **Organization Structure:** Course, Department, Institution, Semester, Session.
- **Users:** Student & Teacher (Add/Edit/List/Profiles).
- **Library:** BookBorrowing, Library.vue.
- **Management:** Accounts, Expenses, FeesCollection.

### 📚 Teacher Panel (`src/views/teacher/`)

_Role: Class execution, grading, attendance, assignment review, and AI._

- **Assignment:** AssignmentList, Create, Edit, **Submissions** (reviewing student uploads).
- **Attendance:** MarkAttendance, AttendanceReport.
- **Class Management:** ClassList, StudentList, AnnouncementList.
- **Grades:** GradeManagement, GradeStudents.
- **Quizzes:** QuizList, QuizBuilder, **AiQuizGenerator** (Connects to python `ai_core`).
- **Schedule:** ClassSchedule, ExamSchedule.

### 🎓 Student Panel (`src/views/student/`)

_Role: Consumption of materials, tracking status, uploading work._

- **Assignment:** ViewAssignments, SubmitAssignment, SubmissionHistory.
- **Attendance:** MyAttendance.
- **Grades:** StudentGradeReport, MyGrade.
- **Library:** LibraryCatalog, MyBooks.
- **Quizzes:** QuizList, TakeQuiz.
- **Resources:** CourseMaterial, EnrolledSubjects, MaterialPreview.
- **Schedule:** ClassSchedule, ExamSchedule.
- **Communication:** Announcements.

---

## 🔍 5. Feature-to-File Matrix (For Mass Updates)

_If asked to update a specific "Feature" across the whole panel, check these files:_

### 📋 List & Search Views (Requires `useEntityList.js` & `smartSearch`)

- **Admin:** `ListTeacher`, `ListStudent`, `ExamList`, `TimeTable`, `Accounts`, `Expenses`, `FeesCollection`, `ListCourse`, `ListDepartment`.
- **Teacher:** `StudentList`, `ClassList`, `AssignmentList`, `Submissions`, `GradeManagement`, `AnnouncementList`, `AttendanceReport`.
- **Student:** `ViewAssignments`, `LibraryCatalog`, `SubmissionHistory`, `ClassSchedule`, `ExamSchedule`, `CourseMaterial`.

### ✏️ Form & Input Views (Requires API POST/PUT)

- **Admin:** `AddTeacher`, `EditTeacher`, `AddStudent`, `EditStudent`, `AddCourse`, `AddAssignment`.
- **Teacher:** `CreateAssignment`, `MarkAttendance`, `GradeStudents`, `QuizBuilder`.
- **Student:** `SubmitAssignment`, `TakeQuiz`.

### 📊 Dashboard & Stats Views

- **Admin:** `AdminDashboard`
- **Teacher:** `TeacherDashboard`, `SubjectProfile`, `StudentProfile`
- **Student:** `StudentDashboard`, `StudentGradeReport`, `MyAttendance`

---

## 🔗 6. Data Flow Example (Mental Model)

If a user requests an update to "Teacher grading":

1. **View:** Open `views/teacher/grades/GradeManagement.vue`
2. **Logic/State:** Check `composables/teacher/useGradeManagement.js`
3. **API Call:** Check `services/teacher/teacherPanelService.js`
4. **Backend:** Re-route to standard Django `lms_cors/views/teacher.py` or similar.

---

## 🛠️ 7. Known Tech Debt & Required Refactors (TODO)

_If tasked to optimize or clean up the codebase, target these commonly duplicated patterns across the panels:_

### 1. Hardcoded Modals & State

- **Problem:** Many views (e.g., `Expenses.vue`, `Accounts.vue`, `AssignmentList.vue`) manually define `showModal = ref(false)`, `showDeleteModal = ref(false)`, `saving = ref(false)`, and `deleting = ref(false)` rather than using the centralized wrappers.
- **Refactor Goal:** Sweep through list views and replace these hardcoded refs with the built-in `useCrudModal()` composable.

### 2. Hardcoded Breadcrumbs

- **Problem:** Every `.vue` file manually reconstructs array objects for breadcrumbs: `const breadcrumbs = [{ name: 'Dashboard', href: ... }]`.
- **Refactor Goal:** Implement a DRY helper in `utils/navigation.js` (e.g., `generateBreadcrumbs(role, label)`) and inject it across all 50+ views to drastically reduce boilerplate code.

### 3. Redundant `onMounted` API Fetching

- **Problem:** Over 19+ files independently write `try/catch` wrappers inside `onMounted` to fetch initial data (like Select box options), while also manually toggling `loading.value = true/false` block booleans.
- **Refactor Goal:** Utilize or build a unified `useAsyncState` or `LoadInitialData` helper to automatically manage the loading boolean and errors for these standard page-load data fetches.

_Update this file if major directories or paradigms shift significantly._

---

## 🧾 8. Session Handoff Context (2026-03-18)

### Quiz System Refactor Status

The student quiz flow has been upgraded from a one-shot submit model to a stable attempt/session model.

Implemented features:

- Stable server-side quiz session with resumable attempt state.
- Next/Previous + jump palette navigation.
- Question status tracking (`not_visited`, `visited`, `answered`) + flagging.
- Debounced auto-save per question.
- Server-backed timer (`end_time`) with auto-submit on expiry.
- Submit summary modal (answered/not answered/flagged counts).
- Auto-evaluation at submit.
- Review mode with correct answer, user answer, explanation.
- Attempt lock after submission.

### Backend Files Changed (Quiz)

- `Project/lms_cors/models/grading.py`
  - `QuizAttempt` now includes persistent state fields: `user`, `answers` (JSON), `flagged_questions` (JSON), `start_time`, `end_time`, `status`, `is_submitted`.
  - `QuizAnswer` now includes: `status`, `is_flagged`, `updated_at`.
  - `start_time` is nullable for migration compatibility with existing rows.
- `Project/lms_cors/serializers/grading.py`
  - Added public/student-safe quiz serializers.
  - Added `QuizAttemptStateSerializer` and review serializer.
- `Project/lms_cors/views/grading.py`
  - Added attempt endpoints and logic for `state`, `autosave`, `summary`, `submit`, `review`, `force_end`.
  - Updated quiz queryset ordering to fix DRF pagination warning.
- `Project/lms_cors/migrations/0031_quizattempt_session_state_and_quizanswer_tracking.py`
  - Migration for session-state and tracking fields.

### Frontend Files Changed (Quiz)

- `frontend/src/views/student/quizzes/TakeQuiz.vue`
  - Rebuilt to use stable attempt workflow.
  - Added navigation guards and beforeunload handling.
  - Supports review mode after submit.
- `frontend/src/composables/student/useQuizAttempt.js`
  - Reusable attempt state + autosave queue/debounce logic.
- `frontend/src/services/student/studentPanelService.js`
  - Added API methods for `state`, `autosave`, `summary`, `submit by attempt id`, `review`.
- `frontend/src/components/shared/common/specialized/QuizQuestionPalette.vue`
- `frontend/src/components/shared/common/feedback/QuizSubmitSummaryModal.vue`
- `frontend/src/components/shared/common/index.js`
  - Exported new reusable quiz components.
- `frontend/src/assets/css/components.css`
  - Added shared quiz styles (palette, timer, review option states, summary modal).

### Recent Critical Fixes

- Fixed `TakeQuiz.vue` dynamic import failure caused by script syntax error (missing `)` in `onUnmounted` block).
- Fixed DRF warning:
  - `UnorderedObjectListWarning` on `Quiz` queryset by ordering in `QuizViewSet.get_queryset()`.
- Reset quiz attempts for testing:
  - All `QuizAttempt` rows deleted to make quizzes appear unattempted.

### Useful Test Command

To reset quiz attempts again during QA:

```powershell
Set-Location "E:\New folder\prac\Project"
python manage.py shell -c "from lms_cors.models.grading import QuizAttempt; total=QuizAttempt.objects.count(); QuizAttempt.objects.all().delete(); print('Deleted quiz attempts:', total)"
```

### Continuation Notes

- If quiz page errors again, check:
  1.  Browser console for Vite import/syntax errors in `TakeQuiz.vue`.
  2.  Django traceback for attempt serializer/view issues.
  3.  That migration `0031` is applied.
- Current architecture direction for quiz should remain backend-source-of-truth for timer/session state (avoid frontend-only timer authority).
