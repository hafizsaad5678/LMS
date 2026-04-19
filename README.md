# Student Management System with AI Integration

This project is a comprehensive Learning Management System (LMS) with an integrated AI Chatbot, Grading System, and Student/Teacher/Admin Panels.

## Project Structure
- `Project/`: Django Backend (REST API)
- `frontend/`: Vue.js 3 Frontend (Vite)

## Setup Instructions

### 1. Backend (Django)
```bash
cd Project
# Create virtual environment
python -m venv venv
# Activate venv (Windows)
.\venv\Scripts\activate
# Activate venv (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### 2. Frontend (Vue.js)
```bash
cd frontend
# Install dependencies
npm install

# Start development server
npm run dev
```

## Features
- AI Chatbot for student queries
- GPA/CGPA Calculator with custom grade sets
- Real-time Grading and Assignment Management
- Attendance Tracking
- Multi-role Dashboards (Admin, Teacher, Student)
