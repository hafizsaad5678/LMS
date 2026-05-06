# Project Overview

## Structure
The project is divided into an AI-enhanced backend (Django) and a frontend SPA (Vue/Vite).

### Backend (`prac/Project`)
- **Django Applications:**
  - `ai_core`: Handles AI services, integrations (Langchain, OpenAI/HuggingFace/Cohere, Sentence Transformers), and ML operations.
  - `authapp`: Authentication schemas, user management, and authorization using JWTs.
  - `institution_profile`: Management of institution details, configurations, and profiles.
  - `lms_cors`: Learning Management System features, coursework, CORS permissions, and integrations.
  - `myproject`: The core Django configuration/settings folder.

### Frontend (`prac/frontend`)
- **Framework:** Vue 3 via Vite.
- **State Management:** Pinia.
- **Routing:** Vue Router.
- **Components & Layouts:** Divided into generic shared UI, and specific panels for `admin`, `teacher`, and `student` layouts and pages.
- **Assets/Styling:** Bootstrap 5, Bootstrap Icons, SCSS/SASS styling.

## Dependencies

### Backend Requirements (Python)
*(See `prac/requirements.txt` for exact versions)*
- **Core:** Django, Django REST Framework, djangorestframework-simplejwt, django-cors-headers
- **Database:** psycopg2-binary, SQLAlchemy
- **AI & NLP:** langchain, langchain-core, huggingface_hub, openai, cohere, sentence-transformers, faiss-cpu, torch, transformers
- **Document Processing:** pdfplumber, pdfminer.six, pypdfium2

### Frontend Requirements (Node/Vue)
- **Dependencies:** 
  - `vue` (^3.5.22)
  - `vue-router` (^4.6.3)
  - `pinia` (^3.0.4)
  - `axios` (^1.13.2)
  - `bootstrap` & `bootstrap-icons`
  - `vuedraggable`, `sweetalert2`, `jspdf`, `@vuepic/vue-datepicker`
- **DevDependencies:** `vite`, `@vitejs/plugin-vue`, `sass`, `sharp`