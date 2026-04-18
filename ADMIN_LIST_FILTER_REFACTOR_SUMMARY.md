# Admin List Filter Refactor Summary

## Goal
Standardize admin list filtering and stats logic across pages to reduce repeated code and keep behavior consistent.

## Shared Building Blocks

### 1) `useEntityList` (enhanced)
Location: `src/composables/shared/data/useEntityList.js`

New capabilities:
- `filterSchema` support for schema-driven filters.
- `resetToDefaults` support for reset policy.
- `forceFreshOnMount` support for stale-cache-sensitive pages.
- `refresh(fetchFn, { reset })` and `refreshAndReset(fetchFn)` helpers.

### 2) `useFilterOptions`
Location: `src/composables/shared/data/useFilterOptions.js`

Purpose:
- Build unique option lists from source data.
- Supports primitive or object options.
- Supports custom keying/sorting.

### 3) `useListStats`
Location: `src/composables/shared/data/useListStats.js`

Purpose:
- Reusable stats helpers: `count`, `sum`, `average`, `uniqueCount`, `summary`.

### 4) `SearchFilter` presets
Location: `src/components/shared/common/layout/SearchFilter.vue`

Added preset support:
- `admin-list`
- `teacher-list`
- `student-list`

Usage:
- `preset="admin-list"` for standardized search/actions layout and theme.

## UI Input Reuse Improvements

### `SelectInput` expanded
Location: `src/components/shared/common/ui/SelectInput.vue`

Enhancements:
- Works with primitive or object options.
- `optionValueKey` and `optionLabelKey` support.
- `colClass` support for filter grid layout.

## Migrated Pages

Core admin lists migrated to shared pattern:
- `src/views/admin/teacher/ListTeacher.vue`
- `src/views/admin/subject/ListSubject.vue`
- `src/views/admin/assignment/ListAssignment.vue`
- `src/views/admin/semester/ListSemester.vue`
- `src/views/admin/course/ListCourse.vue`
- `src/views/admin/management/FeesCollection.vue`
- `src/views/admin/library/LibraryBooks.vue`
- `src/views/admin/library/BookBorrowing.vue`
- `src/views/admin/student/ListStudent.vue`
- `src/views/admin/department/ListDepartment.vue`
- `src/views/admin/institution/ListInstitution.vue`
- `src/views/admin/session/ListSessions.vue`
- `src/views/admin/academic/ExamList.vue`
- `src/views/admin/academic/Events.vue`

Consistency polish also applied:
- `src/views/admin/management/Accounts.vue`
- `src/views/admin/management/Expenses.vue`

## Constants Centralization
Location: `src/utils/constants/options.js`

Added reusable option constants used by filters:
- expense approval
- fee status
- semester number
- book category
- borrowing status
- course duration

## New List Page Checklist

For any new admin list page:
1. Use `SearchFilter` with `preset="admin-list"`.
2. Use `useEntityList` for data, filtering, reset, refresh.
3. Prefer `filterSchema` for standard filter rules.
4. Use `useFilterOptions` for options derived from list data.
5. Use `useListStats` for total/active/unique/sum style cards.
6. Avoid page-level watch blocks for manual filtering when composable handles it.
7. Use named refresh handlers (avoid inline lambdas in template where practical).

## Notes
- Existing `customFilter` in `useEntityList` remains available for complex page-specific rules.
- Keep sorting logic in `customFilter` if it is view-specific.
- This refactor intentionally keeps UI behavior unchanged while reducing JS duplication.
