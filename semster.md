# LMS Technical Fixes Summary - May 2026

This document records the critical fixes applied to the Subject Management, Semester Promotion, and Teacher Profile systems to ensure data integrity and a smooth user experience.

---

## 1. Subject & Enrollment Fixes (`lms_cors/views/academic.py`)

### Subject-Semester Association

**Issue:** New subjects created via the UI were failing to link with their selected semester because the backend was directly mutating an immutable `request.data` object.
**Fix:** Refactored `SubjectViewSet.create` to use a mutable copy of the data, ensuring the `semester` ID is correctly extracted and passed to the serializer.

### Auto-Enrollment for New Subjects

**Issue:** Students already in an active semester were not being enrolled in subjects added _after_ the semester was started.
**Fix:** Integrated `_enroll_students_in_subject` into the `create` method. Now, adding a subject to an active semester automatically creates enrollment records for all eligible students.

### Manual Sync Action

**New Feature:** Added `@action(detail=True, url_path='sync-enrollments')`. Admins can now click a "Sync" button (or call the API) to manually enroll students into an existing subject if data becomes out of sync.

---

## 2. Semester Promotion Enhancements (`lms_cors/views/academic.py`)

**Issue:** Promotion was moving students but leaving old teacher assignments, timetables, and exams "Active," causing cluttered dashboards and data leakage.
**Fix:** Enhanced `AcademicSessionViewSet.promote_semester` with an atomic cleanup and activation block:

- **Deactivation (Outgoing Semester):**
  - `TeacherSubject` links set to `is_active=False`.
  - `Timetable` slots set to `is_active=False`.
  - `Exam` records marked as `status='completed'`.
- **Activation (Incoming Semester):**
  - New `TeacherSubject` links set to `is_active=True`.
  - New `Timetable` slots set to `is_active=True`.
  - Promoted students automatically enrolled in all next-semester subjects.

---

## 3. Teacher Profile Image Fix (`frontend/src/views/admin/teacher/EditTeacher.vue`)

**Issue:** Updating a teacher profile resulted in a `400 Bad Request` error if the profile image was not changed. This happened because the frontend was sending back the existing image URL string, which the backend's `ImageField` rejected as an invalid upload.
**Fix:** Updated `handleSubmit` logic:

1. If `profile_image` is a **File**: Use `FormData` to upload the new image.
2. If `profile_image` is **null**: Send `null` to clear the image.
3. If `profile_image` is a **string (URL)**: Remove it from the payload entirely so the backend keeps the existing file without re-validating it.

---

**Implementation Date:** May 13, 2026
**Status:** Verified & Deployed

# LMS Academic and Teacher Fixes Summary

This document summarizes the technical fixes implemented for Subject management, Semester promotion, and Teacher profile updates.

---

## 1. Academic Module Fixes (`academic.py`)

### Subject-Semester Association & Auto-Enrollment

**Problem:** Newly created subjects weren't properly linking to semesters, and students weren't being enrolled in subjects added to an active semester.
**Fix:** Refactored `SubjectViewSet.create` to handle mutable data and added logic to automatically enroll students in active semesters.

```python
# lms_cors/views/academic.py

def create(self, request, *args, **kwargs):
    # Fix: Create mutable copy of request data to ensure semester association
    data = request.data.copy()
    if 'semester' in data and isinstance(data['semester'], list) and len(data['semester']) > 0:
        data['semester'] = data['semester'][0]

    serializer = self.get_serializer(data=data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)

    # New: Auto-enroll students if the semester is already active
    subject = serializer.instance
    if subject.semester and subject.semester.status == 'active':
        self._enroll_students_in_subject(subject)

    return Response(serializer.data, status=status.HTTP_201_CREATED)

# New: Sync Enrollment Action
@action(detail=True, methods=['post'], url_path='sync-enrollments')
def sync_enrollments(self, request, pk=None):
    """Manually trigger enrollment for existing subjects"""
    subject = self.get_object()
    count = self._enroll_students_in_subject(subject)
    return Response({'message': f'Sync completed. {count} students enrolled.'})
```

### Semester Promotion Workflow

**Problem:** Promoting a semester didn't deactivate old timetables, teacher assignments, or exams.
**Fix:** Enhanced `AcademicSessionViewSet.promote_semester` to systematically update related entities.

```python
# lms_cors/views/academic.py

with transaction.atomic():
    # 1. Update Semester Statuses
    active_semester.status = 'completed'
    next_semester.status = 'active'

    # 2. Deactivate Old Records
    TeacherSubject.objects.filter(subject_id__in=outgoing_subject_ids).update(is_active=False)
    Timetable.objects.filter(semester=active_semester).update(is_active=False)
    Exam.objects.filter(subject_id__in=outgoing_subject_ids, status='scheduled').update(status='completed')

    # 3. Activate New Records
    next_semester_subject_ids = list(Subject.objects.filter(semester=next_semester).values_list('id', flat=True))
    TeacherSubject.objects.filter(subject_id__in=next_semester_subject_ids).update(is_active=True)
    Timetable.objects.filter(semester=next_semester).update(is_active=True)
```

---

## 2. Teacher Profile Fixes (`EditTeacher.vue`)

### Profile Image Update Bug (400 Bad Request)

**Problem:** Updating a teacher profile failed with a 400 error because the frontend was sending the existing image URL string back to the API, which DRF's `ImageField` rejected.
**Fix:** Modified the payload logic to filter out existing image URLs while still allowing new file uploads or image removal.

```javascript
// frontend/src/views/admin/teacher/EditTeacher.vue

const handleSubmit = async () => {
  const teacherData = {
    full_name: form.value.full_name,
    // ... other fields ...
    is_active: form.value.is_active,
  };

  // FIX: Handle profile_image specially
  let payload = teacherData;

  if (form.value.profile_image instanceof File) {
    // If it's a new file, use FormData
    teacherData.profile_image = form.value.profile_image;
    payload = toFormData(teacherData);
  } else if (form.value.profile_image === null) {
    // If it's null, we want to clear the image
    teacherData.profile_image = null;
    payload = teacherData;
  }
  // Else: it's a string (URL), so we leave it out of the payload
  // entirely so the backend keeps the existing image.

  await teacherService.patchTeacher(teacherId.value, payload);
  // ...
};
```

---

**Status:** All fixes deployed and verified.

- Subject enrollments are now synchronized.
- Promotions are clean and systematic.
- Teacher profile edits (with or without image changes) are now working correctly.

---

# LMS Semester Isolation Fixes Summary

This section documents the semester isolation fixes applied to ensure students and teachers only see current/active semester data by default, while keeping historical data intact.

## 1. Dashboard and Stats Filtering

**File:** `Project/lms_cors/views/statistics.py`

- **Teacher Dashboard:** Filtered `TeacherSubject` and `Assignment` queries by `subject__semester__status='active'`.
- **Student Dashboard:** Filtered enrolled subjects, grades, attendance, announcements, and assignments by `subject__semester__number=student.current_semester`.

## 2. Student and Teacher Subject/Assignment Views

**File:** `Project/lms_cors/views/people.py`

- **teacher_my_classes:** Applied `subject__semester__status='active'` to teacher subjects and timetable subjects.
- **teacher_my_assignments:** Applied `subject__semester__status='active'` to assignments.
- **grades + grade_report:** Filtered `Grade`, `StudentMark`, and `QuizAttempt` by `subject__semester__number=student.current_semester`.
- **assignments (student action):** Filtered enrolled subjects by `subject__semester__number=student.current_semester`.
- **enrolled_subjects (student action):** Default now returns current semester only. Added optional `?history=true` to include all.
- **\_current_enrollments helper:** Updated to use `subject__semester__number=student.current_semester` to avoid mismatch between StudentSubject.semester and Subject.semester.

## 3. Attendance Isolation

**File:** `Project/lms_cors/views/attendance.py`

- Student attendance list now filters by `subject__semester__number=student.current_semester`.

## 4. Grading and Quizzes

**File:** `Project/lms_cors/views/grading.py`

- Student quiz lists and attempts now filtered by `quiz__subject__semester__number=student.current_semester`.
- Grade components and marks filtered by `subject__semester__number=student.current_semester`.
- Legacy `Grade` records in the mark list are filtered by the current semester for students.

## 5. Materials and Announcements

**File:** `Project/lms_cors/views/materials.py`

- Student materials filtered by `subject__semester__number=student.current_semester`.
- Teacher materials filtered by `subject__semester__status='active'` (subject-level items only).

## 6. Assignments and Submissions

**File:** `Project/lms_cors/views/assignments.py`

- Teacher assignment listing restricted to active semester subjects.
- Student submission and grade views restricted to `subject__semester__number=student.current_semester`.
- `_current_enrollments_for_student` updated to use `subject__semester__number=student.current_semester`.

## 7. Student Profile Serializer

**File:** `Project/lms_cors/serializers/people.py`

- `StudentDetailSerializer.enrolled_subjects` now returns only current semester subjects.
- `StudentDetailSerializer.submissions` now returns only current semester assignment submissions.

---

**Status:** Applied and tested via `manage.py check`. No schema changes and historical data is preserved.

---

# Code Before vs After (Key Diffs)

This appendix shows the exact before/after code diffs for the fixes listed above.

## AcademicSessionViewSet Promotion Cleanup (`lms_cors/views/academic.py`)

```diff
 with transaction.atomic():
+    # Mark all currently active semesters in this session as completed
     Semester.objects.filter(session=session, status='active').exclude(id=active_semester.id).update(status='completed')

     active_semester.status = 'completed'
     active_semester.save(update_fields=['status', 'updated_at'])

     next_semester.status = 'active'
     next_semester.save(update_fields=['status', 'updated_at'])

+    # Identify subjects from the outgoing semester to deactivate related items
+    outgoing_subjects = Subject.objects.filter(semester=active_semester)
+    outgoing_subject_ids = list(outgoing_subjects.values_list('id', flat=True))
+
+    # Deactivate teacher assignments for the outgoing semester
+    from .people import TeacherSubject
+    TeacherSubject.objects.filter(subject_id__in=outgoing_subject_ids).update(is_active=False)
+
+    # Deactivate timetable slots for the outgoing semester
+    from .scheduling import Timetable, Exam
+    Timetable.objects.filter(semester=active_semester).update(is_active=False)
+
+    # Mark exams for outgoing subjects as completed
+    Exam.objects.filter(subject_id__in=outgoing_subject_ids, status='scheduled').update(status='completed')
+
+    # --- Activate Next Semester Items ---
+    # Identify subjects for the incoming semester
+    next_semester_subject_ids = list(Subject.objects.filter(semester=next_semester).values_list('id', flat=True))
+
+    # Ensure teacher assignments for the next semester are active
+    TeacherSubject.objects.filter(subject_id__in=next_semester_subject_ids).update(is_active=True)
+
+    # Ensure timetable slots for the next semester are active
+    Timetable.objects.filter(semester=next_semester).update(is_active=True)
```

## Subject Create + Auto-Enrollment (`lms_cors/views/academic.py`)

```diff
 class SubjectViewSet(BaseViewSet):
     queryset = Subject.objects.select_related(
         'semester', 'semester__program', 'semester__session',
         'semester__program__department', 'semester__program__department__institution'
     )
+    pagination_class = None
+
+    def create(self, request, *args, **kwargs):
+        # Create a mutable copy of the data
+        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
+        semester_ids = data.get('semester')
+
+        if isinstance(semester_ids, list):
+            if len(semester_ids) > 1:
+                # Handle bulk creation for multiple semesters
+                created_subjects = []
+                for sem_id in semester_ids:
+                    item_data = data.copy()
+                    item_data['semester'] = sem_id
+                    serializer = self.get_serializer(data=item_data)
+                    serializer.is_valid(raise_exception=True)
+                    self.perform_create(serializer)
+                    created_subjects.append(serializer.data)
+                return Response(created_subjects, status=status.HTTP_201_CREATED)
+            elif len(semester_ids) == 1:
+                # If it's a list of one, normalize to a single ID
+                data['semester'] = semester_ids[0]
+
+        # Standard creation logic using the mutable data
+        serializer = self.get_serializer(data=data)
+        serializer.is_valid(raise_exception=True)
+        self.perform_create(serializer)
+
+        # Auto-enroll students if the semester is active
+        subject = serializer.instance
+        if subject.semester and subject.semester.status == 'active':
+            self._enroll_students_in_subject(subject)
+
+        headers = self.get_success_headers(serializer.data)
+        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
+
+    @action(detail=True, methods=['post'], url_path='sync-enrollments')
+    def sync_enrollments(self, request, pk=None):
+        """Manually trigger enrollment of all eligible students into this subject."""
+        subject = self.get_object()
+        if not subject.semester:
+            return Response({'detail': 'Subject is not linked to a semester.'}, status=status.HTTP_400_BAD_REQUEST)
+
+        count = self._enroll_students_in_subject(subject)
+        return Response({
+            'message': f'Enrollment sync completed. {count} students enrolled.',
+            'total_students': StudentSubject.objects.filter(subject=subject).count()
+        })
```

## Teacher Profile Image Update (`frontend/src/views/admin/teacher/EditTeacher.vue`)

```diff
 const handleSubmit = async () => {
   const teacherData = {
     full_name: form.value.full_name,
     // ... other fields ...
     is_active: form.value.is_active
   }

-  const payload = teacherData.profile_image instanceof File ? toFormData(teacherData) : teacherData
+  // Handle profile_image specially
+  // 1. If it's a File, we must use FormData
+  // 2. If it's null, we want to clear the image (send null)
+  // 3. If it's a string (existing URL), we don't send it at all to avoid validation errors
+  let payload = teacherData
+
+  if (form.value.profile_image instanceof File) {
+    teacherData.profile_image = form.value.profile_image
+    payload = toFormData(teacherData)
+  } else if (form.value.profile_image === null) {
+    teacherData.profile_image = null
+    payload = teacherData
+  }
+  // Else: it's a string (URL), so we leave it out of teacherData/payload entirely

   await teacherService.patchTeacher(teacherId.value, payload)
 }
```

## Dashboard Stats Isolation (`lms_cors/views/statistics.py`)

```diff
-classes = TeacherSubject.objects.filter(teacher=teacher, subject__isnull=False)
+classes = TeacherSubject.objects.filter(teacher=teacher, subject__isnull=False, subject__semester__status='active')

-assignments = Assignment.objects.filter(created_by=teacher).annotate(
+assignments = Assignment.objects.filter(
+    created_by=teacher,
+    subject__semester__status='active'
+).annotate(
```

```diff
-enrolled_subjects = student.enrolled_subjects.all().annotate(
+enrolled_subjects = student.enrolled_subjects.filter(
+    subject__semester__number=student.current_semester
+).annotate(

-assignment_grades = Grade.objects.filter(submission__student=student)
-component_marks = StudentMark.objects.filter(student=student, component__is_visible_to_students=True)
+assignment_grades = Grade.objects.filter(
+    submission__student=student,
+    submission__assignment__subject__semester__number=student.current_semester
+
+component_marks = StudentMark.objects.filter(
+    student=student,
+    component__is_visible_to_students=True,
+    component__subject__semester__number=student.current_semester
+
-attendance_records = student.attendance_records.all()
+attendance_records = student.attendance_records.filter(
+    subject__semester__number=student.current_semester
+
```

## People Endpoints (`lms_cors/views/people.py`)

```diff
-teacher_subjects = TeacherSubject.objects.filter(
-    teacher=teacher,
-    subject__isnull=False
-)
+teacher_subjects = TeacherSubject.objects.filter(
+    teacher=teacher,
+    subject__isnull=False,
+    subject__semester__status='active'
+
```

```diff
-timetable_subject_ids = Timetable.objects.filter(
-    teacher=teacher,
-    subject__isnull=False,
-    is_active=True
-).values_list('subject_id', flat=True).distinct()
+timetable_subject_ids = Timetable.objects.filter(
+    teacher=teacher,
+    subject__isnull=False,
+    is_active=True,
+    subject__semester__status='active'
+).values_list('subject_id', flat=True).distinct()
```

```diff
-assignments = Assignment.objects.filter(
-    created_by=teacher
-).exclude(
+assignments = Assignment.objects.filter(
+    created_by=teacher,
+    subject__semester__status='active'
+).exclude(
```

```diff
-queryset = queryset.filter(semester__number=student.current_semester)
+queryset = queryset.filter(subject__semester__number=student.current_semester)
```

```diff
-enrolled_subject_ids = student.enrolled_subjects.values_list('subject_id', flat=True)
+enrolled_subject_ids = student.enrolled_subjects.filter(
+    subject__semester__number=student.current_semester
+).values_list('subject_id', flat=True)
```

```diff
-assignment_grades = Grade.objects.filter(submission__student=student).select_related(
+assignment_grades = Grade.objects.filter(
+    submission__student=student,
+    submission__assignment__subject__semester__number=student.current_semester
+).select_related(

-component_marks = StudentMark.objects.filter(
-    student=student
-).select_related('component', 'component__subject')
+component_marks = StudentMark.objects.filter(
+    student=student,
+    component__subject__semester__number=student.current_semester
+).select_related('component', 'component__subject')
```

```diff
-quiz_attempts = QuizAttempt.objects.filter(student=student).select_related(
+quiz_attempts = QuizAttempt.objects.filter(
+    student=student,
+    quiz__subject__semester__number=student.current_semester
+).select_related(

-component_marks = StudentMark.objects.filter(
-    student=student
-).select_related('component', 'component__subject', 'component__linked_quiz')
+component_marks = StudentMark.objects.filter(
+    student=student,
+    component__subject__semester__number=student.current_semester
+).select_related('component', 'component__subject', 'component__linked_quiz')
```

```diff
-queryset = student.enrolled_subjects.all().select_related('subject', 'semester')
+# Default to only returning current semester subjects unless history=true is requested
+if request.query_params.get('history') == 'true':
+    queryset = student.enrolled_subjects.all().select_related('subject', 'semester')
+else:
+    queryset = self._current_enrollments(student).select_related('subject', 'semester')

-if request.query_params.get('current_only') == 'true':
-    current_qs = self._current_enrollments(student).values_list('id', flat=True)
-    queryset = queryset.filter(id__in=current_qs)
```

## Attendance Isolation (`lms_cors/views/attendance.py`)

```diff
-# Students only see their own attendance
-queryset = queryset.filter(student=user.student_profile)
+# Students only see their own attendance from current semester
+student = user.student_profile
+queryset = queryset.filter(
+    student=student,
+    subject__semester__number=student.current_semester
+)
```

## Grading and Quizzes (`lms_cors/views/grading.py`)

```diff
-queryset = queryset.filter(
-    is_published=True,
-    subject_id__in=enrolled_subject_ids
-)
+queryset = queryset.filter(
+    is_published=True,
+    subject_id__in=enrolled_subject_ids,
+    subject__semester__number=student.current_semester
+)
```

```diff
-queryset = queryset.filter(student=user.student_profile)
+student = user.student_profile
+queryset = queryset.filter(
+    student=student,
+    quiz__subject__semester__number=student.current_semester
+)
```

```diff
-queryset = GradeComponent.objects.filter(subject_id__in=enrolled_subjects, is_visible_to_students=True)
+queryset = GradeComponent.objects.filter(
+    subject_id__in=enrolled_subjects,
+    is_visible_to_students=True,
+    subject__semester__number=student.current_semester
+)
```

```diff
-queryset = queryset.filter(student=user.student_profile)
+student = user.student_profile
+queryset = queryset.filter(
+    student=student,
+    component__subject__semester__number=student.current_semester
+)
```

```diff
-legacy_grades_qs = legacy_grades_qs.filter(submission__student=user.student_profile)
+student = user.student_profile
+legacy_grades_qs = legacy_grades_qs.filter(
+    submission__student=student,
+    submission__assignment__subject__semester__number=student.current_semester
+)
```

## Materials Isolation (`lms_cors/views/materials.py`)

```diff
 return self.queryset.filter(
     Q(uploaded_by=teacher) | Q(subject__in=teacher_subjects),
     is_active=True
+).filter(
+    Q(subject__isnull=True) | Q(subject__semester__status='active')
 ).distinct()
```

```diff
 qs = self.queryset.filter(
     Q(is_active=True),
     Q(access_level='public') | Q(access_level='class_only', subject__in=student_subjects)
+).filter(
+    Q(subject__isnull=True) | Q(subject__semester__number=student.current_semester)
 ).distinct()
```

```diff
 materials = Material.objects.filter(
     Q(uploaded_by=teacher) | (Q(subject__in=teacher_subjects) & Q(is_active=True))
+).filter(
+    Q(subject__isnull=True) | Q(subject__semester__status='active')
 ).select_related('subject', 'uploaded_by').order_by('-uploaded_at').distinct()
```

## Assignments + Submissions (`lms_cors/views/assignments.py`)

```diff
-queryset = queryset.filter(semester__number=student.current_semester)
+queryset = queryset.filter(subject__semester__number=student.current_semester)
```

```diff
-assigned_subjects = TeacherSubject.objects.filter(
-    teacher=teacher,
-    is_active=True
-)
+assigned_subjects = TeacherSubject.objects.filter(
+    teacher=teacher,
+    is_active=True,
+    subject__semester__status='active'
+)
```

```diff
-return qs.filter(student=user.student_profile).select_related(
+student = user.student_profile
+return qs.filter(
+    student=student,
+    assignment__subject__semester__number=student.current_semester
+).select_related(
```

```diff
 return qs.filter(
     Q(assignment__created_by=teacher) | Q(assignment__subject_id__in=teacher_subjects)
+).filter(
+    Q(assignment__subject__isnull=True) | Q(assignment__subject__semester__status='active')
 ).select_related(
```

```diff
-return qs.filter(submission__student=user.student_profile).order_by('-graded_at')
+student = user.student_profile
+return qs.filter(
+    submission__student=student,
+    submission__assignment__subject__semester__number=student.current_semester
+).order_by('-graded_at')
```

```diff
+# If teacher, limit to their active subjects
+if hasattr(user, 'teacher_profile') and not user.is_staff:
+    return qs.filter(
+        Q(submission__assignment__subject__isnull=True) |
+        Q(submission__assignment__subject__semester__status='active')
+    ).order_by('-graded_at')
```

## Student Detail Serializer (`lms_cors/serializers/people.py`)

```diff
-enrolled_subjects = StudentSubjectSerializer(many=True, read_only=True)
-submissions = SubmissionHistorySerializer(many=True, read_only=True)
+enrolled_subjects = serializers.SerializerMethodField()
+submissions = serializers.SerializerMethodField()
+
+def get_enrolled_subjects(self, obj):
+    qs = obj.enrolled_subjects.filter(
+        subject__semester__number=obj.current_semester
+    )
+    return StudentSubjectSerializer(qs, many=True, context=self.context).data
+
+def get_submissions(self, obj):
+    qs = obj.submissions.filter(
+        assignment__subject__semester__number=obj.current_semester
+    )
+    return SubmissionHistorySerializer(qs, many=True, context=self.context).data
```
