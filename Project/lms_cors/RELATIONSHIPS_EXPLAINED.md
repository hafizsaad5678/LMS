# LMS Database Relationships Explained

This document details the data models and their relationships within the `lms_cors` application. The system is built around a core academic structure, user profiles, and academic management features.

## 1. Core Academic Structure

The academic hierarchy forms the backbone of the LMS.

### **Department**
- **Description**: Represents an academic department (e.g., "Computer Science").
- **Relationships**:
  - **Programs**: One Department has many Programs (`1:N`). Related name: `programs`.
  - **Teachers**: One Department employs many Teachers (`1:N`). Related name: `teachers`.

### **Program**
- **Description**: A specific degree or course of study (e.g., "BS Computer Science") offered by a Department.
- **Relationships**:
  - **Department**: Belongs to one Department (`Foreign Key`).
  - **Semesters**: One Program consists of multiple Semesters (`1:N`). Related name: `semesters`.
  - **Students**: One Program has many Students enrolled (`1:N`). Related name: `students`.

### **Semester**
- **Description**: A specific term within a Program (e.g., "Semester 1").
- **Relationships**:
  - **Program**: Belongs to one Program (`Foreign Key`).
  - **Subjects**: One Semester contains multiple Subjects (`1:N`). Related name: `subjects`.
  - **Student Enrollments**: Linked to many Student enrollment records (`1:N`).

### **Subject**
- **Description**: A specific course taught within a Semester (e.g., "Introduction to Programming").
- **Relationships**:
  - **Semester**: Belongs to one Semester (`Foreign Key`).
  - **Teachers**: Assigned to Teachers via `TeacherSubject` (`M:N`).
  - **Students**: Enrolled by Students via `StudentSubject` (`M:N`).
  - **Assignments**: Has many Assignments (`1:N`).
  - **Attendance**: Has many Attendance records (`1:N`).

---

## 2. User Profiles

All user profiles (Student, Teacher, Admin) inherit from a `BaseProfile` and are linked to the standard Django `User` model.

### **BaseProfile (Abstract)**
- **Description**: Contains shared fields like `full_name`, `email`, `phone`, `cnic`, `address`, `profile_image`, etc.
- **Relationships**:
  - **User**: One-to-One relationship with Django's built-in `User` model for authentication.

### **Student**
- **Extends**: `BaseProfile`
- **Relationships**:
  - **Program**: Belongs to one Program (`Foreign Key`).
  - **Enrolled Subjects**: Many-to-Many with Subject through `StudentSubject`.
  - **Submissions**: Has many Assignment Submissions (`1:N`).
  - **Attendance**: Has many Attendance records (`1:N`).

### **Teacher**
- **Extends**: `BaseProfile`
- **Relationships**:
  - **Department**: Belongs to one Department (`Foreign Key`).
  - **Teaching Subjects**: Many-to-Many with Subject through `TeacherSubject`.
  - **Created Assignments**: created many Assignments (`1:N`).
  - **Graded Assignments**: grades many Submissions (`1:N` via Grade model).
  - **Marked Attendance**: marks many Attendance records (`1:N`).

### **Admin**
- **Extends**: `BaseProfile`
- **Relationships**:
  - **Events**: Creates many Events (`1:N`).

---

## 3. Junction Tables (Enrollments & Assignments)

These models handle the Many-to-Many relationships with additional metadata.

### **TeacherSubject**
- **Purpose**: Links a **Teacher** to a **Subject**.
- **Constraint**: A teacher cannot be assigned to the same subject twice (`unique_together`).

### **StudentSubject**
- **Purpose**: Links a **Student** to a **Subject** for a specific Semester.
- **Relationships**:
  - **Student**: Linked Student.
  - **Subject**: Linked Subject.
  - **Semester**: The term in which the student takes the subject.
- **Constraint**: Unique combination of Student, Subject, and Semester.

---

## 4. Academic Management

### **Assignment**
- **Description**: A task created by a teacher for a subject.
- **Relationships**:
  - **Subject**: Belongs to one Subject (`Foreign Key`).
  - **Created By**: Created by one Teacher (`Foreign Key`).
  - **Submissions**: Has many Student Submissions (`1:N`).

### **SubmissionHistory**
- **Description**: A student's submission for an assignment.
- **Relationships**:
  - **Assignment**: Belongs to one Assignment (`Foreign Key`).
  - **Student**: Submitted by one Student (`Foreign Key`).
  - **Grade**: Has one Grade (`One-to-One`).

### **Grade**
- **Description**: The grade and marks given to a submission.
- **Relationships**:
  - **Submission**: Linked to one Submission (`One-to-One`).
  - **Graded By**: Graded by one Teacher (`Foreign Key`).

### **Attendance**
- **Description**: Daily attendance record.
- **Relationships**:
  - **Subject**: For a specific Subject (`Foreign Key`).
  - **Student**: For a specific Student (`Foreign Key`).
  - **Marked By**: Marked by a Teacher (`Foreign Key`).
- **Constraint**: Unique record per Student per Subject per Date.

---

## 5. Administration

### **Event**
- **Description**: Calendar events (Holidays, Exams, etc.).
- **Relationships**:
  - **Created By**: Created by an Admin (`Foreign Key`).
