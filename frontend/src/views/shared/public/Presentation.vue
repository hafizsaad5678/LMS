<template>
  <div class="pres-wrapper homescreen-wrapper" @keydown="handleKey" tabindex="0" ref="wrapperRef">

    <!-- Floating Top Bar -->
    <nav class="pres-topbar" :class="{ 'pres-topbar-hidden': isFullscreen && !showControls }">
      <router-link to="/" class="pres-brand">
        <i class="bi bi-hexagon-fill"></i> LearnMS
      </router-link>
      <div class="pres-progress-wrap">
        <div class="pres-progress-bar" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="pres-counter">{{ activeSlide }} / {{ totalSlides }}</span>

      <!-- Controls -->
      <div class="pres-controls">
        <button class="pres-ctrl-btn" @click="toggleAutoPlay" :title="autoPlaying ? 'Pause Auto-Play' : 'Start Auto-Play'">
          <i :class="autoPlaying ? 'bi bi-pause-fill' : 'bi bi-play-fill'"></i>
        </button>
        <button class="pres-ctrl-btn" @click="toggleFullscreen" :title="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'">
          <i :class="isFullscreen ? 'bi bi-fullscreen-exit' : 'bi bi-arrows-fullscreen'"></i>
        </button>
      </div>
    </nav>

    <!-- Auto-Play Timer Indicator -->
    <div v-if="autoPlaying" class="pres-autoplay-bar">
      <div class="pres-autoplay-fill" :style="{ animationDuration: autoPlayInterval + 'ms' }" :key="autoPlayTick"></div>
    </div>

    <!-- Slide Container -->
    <div class="pres-slides" ref="slidesRef">

      <!-- SLIDE 1 - Title -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner text-center">
          <div class="pres-badge mb-4">Final Year Project</div>
          <h1 class="pres-title-xl">Learn<span class="text-warning">MS</span></h1>
          <p class="pres-subtitle">AI-Based Learning Management System</p>
          <div class="pres-divider mx-auto"></div>
          <p class="pres-meta">BS Computer Science &middot; University of Gujrat</p>
          <div class="row g-3 justify-content-center mt-4" style="max-width: 700px; margin: 0 auto;">
            <div class="col-md-4" v-for="member in teamMembers" :key="member.name">
              <div class="pres-member-chip">
                <div class="pres-member-icon" :style="{ background: member.color }">
                  {{ member.initial }}
                </div>
                <div>
                  <div class="fw-semibold small">{{ member.name }}</div>
                  <div class="text-white-50" style="font-size: 0.7rem;">{{ member.role }}</div>
                </div>
              </div>
            </div>
          </div>
          <p class="pres-meta mt-4"><i class="bi bi-person-workspace me-2"></i>Supervisor: _______________</p>
        </div>
      </section>

      <!-- SLIDE 2 - Introduction -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">02</span>
            <h2 class="pres-heading">What is LearnMS?</h2>
          </div>
          <div class="row g-4 mt-3">
            <div class="col-lg-7">
              <ul class="pres-list">
                <li><i class="bi bi-mortarboard-fill text-primary me-3"></i>Smart LMS designed for universities</li>
                <li><i class="bi bi-robot text-primary me-3"></i>AI integrated directly into learning</li>
                <li><i class="bi bi-people-fill text-primary me-3"></i>Three panels: Admin, Teacher, Student</li>
                <li><i class="bi bi-chat-dots-fill text-primary me-3"></i>AI Chatbot answers from your own materials</li>
                <li><i class="bi bi-file-earmark-check-fill text-primary me-3"></i>Auto Quiz Generation from documents</li>
              </ul>
            </div>
            <div class="col-lg-5 d-flex align-items-center justify-content-center">
              <div class="pres-visual-card">
                <i class="bi bi-stars display-1 text-warning"></i>
                <p class="mt-3 fw-semibold text-dark">Not just an LMS — <br>an AI Learning Ecosystem</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"Unlike traditional LMS, our system integrates AI directly into learning."
          </div>
        </div>
      </section>

      <!-- SLIDE 3 - Problem -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">03</span>
            <h2 class="pres-heading text-white">The Problem</h2>
            <p class="text-white-50 mb-0">Issues in existing LMS platforms</p>
          </div>
          <div class="row g-3 mt-4 justify-content-center">
            <div class="col-md-4" v-for="(prob, i) in problems" :key="i">
              <div class="pres-problem-card">
                <i :class="[prob.icon, 'display-6 mb-3']" :style="{ color: prob.color }"></i>
                <h6 class="fw-bold text-white">{{ prob.title }}</h6>
                <p class="small text-white-50 mb-0">{{ prob.desc }}</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"Current systems lack intelligence and require excessive manual effort."
          </div>
        </div>
      </section>

      <!-- SLIDE 4 - Solution -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">04</span>
            <h2 class="pres-heading">Our Solution</h2>
          </div>
          <div class="row g-3 mt-3 justify-content-center">
            <div class="col-md-4 col-6" v-for="(sol, i) in solutions" :key="i">
              <div class="pres-solution-card">
                <div class="pres-sol-icon" :style="{ background: sol.bg }">
                  <i :class="sol.icon" style="font-size: 1.4rem;"></i>
                </div>
                <h6 class="fw-bold mt-3">{{ sol.title }}</h6>
                <p class="small text-muted mb-0">{{ sol.desc }}</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"We solved these problems using AI, automation, and secure architecture."
          </div>
        </div>
      </section>

      <!-- SLIDE 5 - Objectives -->
      <section class="pres-slide pres-slide-accent">
        <div class="pres-slide-inner text-center">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">05</span>
            <h2 class="pres-heading text-white">Project Objectives</h2>
          </div>
          <div class="row g-3 mt-4 justify-content-center" style="max-width: 800px; margin: 0 auto;">
            <div class="col-12" v-for="(obj, i) in objectives" :key="i">
              <div class="pres-obj-row">
                <div class="pres-obj-num">{{ String(i + 1).padStart(2, '0') }}</div>
                <p class="mb-0 text-white fw-medium text-start">{{ obj }}</p>
                <i class="bi bi-check-circle-fill text-warning ms-auto"></i>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"Our goal was to make learning intelligent, automated, and reliable."
          </div>
        </div>
      </section>

      <!-- SLIDE 6 - Architecture -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">06</span>
            <h2 class="pres-heading">System Architecture</h2>
          </div>
          <div class="row g-4 mt-2 align-items-center">
            <div class="col-lg-6">
              <ul class="pres-list">
                <li><i class="bi bi-window-desktop text-success me-3"></i><strong>Frontend:</strong> Vue 3 + Vite</li>
                <li><i class="bi bi-server text-primary me-3"></i><strong>Backend:</strong> Django REST Framework</li>
                <li><i class="bi bi-database-fill text-info me-3"></i><strong>Database:</strong> SQLite</li>
                <li><i class="bi bi-cpu-fill text-danger me-3"></i><strong>AI Engine:</strong> LangChain + FAISS</li>
                <li><i class="bi bi-arrow-left-right text-warning me-3"></i><strong>Communication:</strong> REST + SSE</li>
              </ul>
            </div>
            <div class="col-lg-6">
              <div class="pres-arch-diagram">
                <div class="pres-arch-layer pres-arch-frontend">
                  <i class="bi bi-window-stack me-2"></i>Vue 3 SPA
                  <div class="pres-arch-sublabel">Admin · Teacher · Student</div>
                </div>
                <div class="pres-arch-arrow"><i class="bi bi-arrow-down-up"></i> REST API + SSE</div>
                <div class="pres-arch-layer pres-arch-backend">
                  <i class="bi bi-gear-wide-connected me-2"></i>Django + DRF
                  <div class="pres-arch-sublabel">Auth · APIs · Views</div>
                </div>
                <div class="pres-arch-row">
                  <div class="pres-arch-layer pres-arch-db">
                    <i class="bi bi-database me-1"></i>SQLite
                  </div>
                  <div class="pres-arch-layer pres-arch-ai">
                    <i class="bi bi-cpu me-1"></i>LangChain + FAISS
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"Our system follows a decoupled architecture — frontend and backend communicate via APIs."
          </div>
        </div>
      </section>

      <!-- SLIDE 7 - Modules -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">07</span>
            <h2 class="pres-heading text-white">Core Modules</h2>
          </div>
          <div class="row g-4 mt-3 justify-content-center">
            <div class="col-md-4" v-for="(mod, i) in modules" :key="i">
              <div class="pres-module-card" :style="{ borderTop: `4px solid ${mod.color}` }">
                <div class="pres-mod-icon-ring" :style="{ background: mod.color + '20', color: mod.color }">
                  <i :class="mod.icon" style="font-size: 1.6rem;"></i>
                </div>
                <h5 class="fw-bold mt-3 text-white">{{ mod.title }}</h5>
                <ul class="pres-mod-list">
                  <li v-for="(feat, j) in mod.features" :key="j">{{ feat }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"The system is divided into three main modules with specific roles."
          </div>
        </div>
      </section>

      <!-- SLIDE 8 - Tech Stack -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">08</span>
            <h2 class="pres-heading">Tech Stack</h2>
          </div>
          <div class="row g-3 mt-3 justify-content-center">
            <div class="col-md-4 col-6" v-for="(tech, i) in techStack" :key="i">
              <div class="pres-tech-card">
                <i :class="tech.icon" :style="{ color: tech.color }" style="font-size: 2rem;"></i>
                <h6 class="fw-bold mt-2 mb-1">{{ tech.name }}</h6>
                <p class="small text-muted mb-0">{{ tech.purpose }}</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"We used modern technologies chosen for scalability and performance."
          </div>
        </div>
      </section>

      <!-- SLIDE 9 - Features -->
      <section class="pres-slide pres-slide-accent">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">09</span>
            <h2 class="pres-heading text-white">Key Features</h2>
          </div>
          <div class="row g-3 mt-4 justify-content-center">
            <div class="col-md-4 col-6" v-for="(feat, i) in features" :key="i">
              <div class="pres-feature-chip">
                <i :class="feat.icon" class="display-6 mb-2"></i>
                <h6 class="fw-bold">{{ feat.title }}</h6>
                <p class="small mb-0 opacity-75">{{ feat.desc }}</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"These features make our system intelligent and user-friendly."
          </div>
        </div>
      </section>

      <!-- SLIDE 10 - Team Roles -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">10</span>
            <h2 class="pres-heading">Team Contributions</h2>
          </div>
          <div class="row g-4 mt-3 justify-content-center">
            <div class="col-md-4" v-for="(role, i) in teamRoles" :key="i">
              <div class="pres-role-card">
                <div class="pres-role-avatar" :style="{ background: role.color }">
                  {{ role.initial }}
                </div>
                <h6 class="fw-bold mt-3">{{ role.name }}</h6>
                <span class="badge rounded-pill mb-3" :style="{ background: role.color + '20', color: role.color }">{{ role.tag }}</span>
                <ul class="pres-role-list">
                  <li v-for="(task, j) in role.tasks" :key="j">{{ task }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"We followed a modular approach with clear role distribution."
          </div>
        </div>
      </section>

      <!-- SLIDE 11 - Demo -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner text-center">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">11</span>
            <h2 class="pres-heading text-white">Live Demo</h2>
          </div>
          <div class="row g-3 mt-4 justify-content-center" style="max-width: 700px; margin: 0 auto;">
            <div class="col-6 col-md-4" v-for="(demo, i) in demoScreens" :key="i">
              <div class="pres-demo-card">
                <i :class="demo.icon" style="font-size: 1.8rem;" :style="{ color: demo.color }"></i>
                <p class="small fw-semibold text-white mt-2 mb-0">{{ demo.label }}</p>
              </div>
            </div>
          </div>
          <router-link to="/login" class="btn btn-warning rounded-pill px-5 py-2 fw-bold mt-5 shadow">
            <i class="bi bi-play-circle-fill me-2"></i>Launch Live App
          </router-link>
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"Now we will demonstrate how the system works in real-time."
          </div>
        </div>
      </section>

      <!-- SLIDE 12 - Future Work -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">12</span>
            <h2 class="pres-heading">Future Enhancements</h2>
          </div>
          <div class="row g-3 mt-3 justify-content-center">
            <div class="col-md-4 col-6" v-for="(fw, i) in futureWork" :key="i">
              <div class="pres-future-card">
                <i :class="fw.icon" style="font-size: 1.6rem;" :style="{ color: fw.color }"></i>
                <h6 class="fw-bold mt-2">{{ fw.title }}</h6>
                <p class="small text-muted mb-0">{{ fw.desc }}</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"We plan to enhance scalability and intelligence in the future."
          </div>
        </div>
      </section>

      <!-- SLIDE 13 - Q&A -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner text-center">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">13</span>
            <h2 class="pres-heading text-white">Common Questions</h2>
          </div>
          <div class="row g-3 mt-4 justify-content-center" style="max-width: 800px; margin: 0 auto;">
            <div class="col-md-6" v-for="(qa, i) in qaItems" :key="i">
              <div class="pres-qa-card">
                <h6 class="fw-bold text-warning mb-2" style="font-size: 0.85rem;">Q: {{ qa.q }}</h6>
                <p class="small text-white-50 mb-0">{{ qa.a }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- SLIDE 14 - Thank You -->
      <section class="pres-slide pres-slide-accent">
        <div class="pres-slide-inner text-center">
          <h1 class="display-3 fw-bold text-white mb-3">Thank You!</h1>
          <div class="pres-divider mx-auto" style="background: rgba(255,255,255,0.3);"></div>
          <div class="d-flex flex-wrap gap-3 justify-content-center mt-4 mb-5">
            <span class="pres-thanks-chip" v-for="(chip, i) in thanksChips" :key="i">
              <i :class="chip.icon" class="me-2"></i>{{ chip.label }}
            </span>
          </div>
          <p class="display-6 text-white mt-4">Questions? <span class="text-warning">🎤</span></p>
          <router-link to="/" class="btn btn-outline-light rounded-pill px-5 py-2 fw-semibold mt-4">
            <i class="bi bi-house-door me-2"></i>Back to Home
          </router-link>
        </div>
      </section>

    </div>

    <!-- Bottom Hint Bar -->
    <div class="pres-hint-bar" :class="{ 'pres-hint-hidden': isFullscreen && !showControls }">
      <span><i class="bi bi-arrow-up-short"></i> ↑ Previous</span>
      <span><i class="bi bi-arrow-down-short"></i> ↓ / Space Next</span>
      <span><i class="bi bi-arrows-fullscreen"></i> F — Fullscreen</span>
      <span v-if="!autoPlaying"><i class="bi bi-play"></i> A — Auto-Play</span>
      <span v-else class="text-warning"><i class="bi bi-pause"></i> A — Pause</span>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'

const wrapperRef = ref(null)
const slidesRef = ref(null)
const activeSlide = ref(1)
const totalSlides = 14

// Fullscreen
const isFullscreen = ref(false)
const showControls = ref(true)
let controlsTimer = null

// Auto-play
const autoPlaying = ref(false)
const autoPlayInterval = 7000 // 7 seconds
const autoPlayTick = ref(0)
let autoPlayTimer = null

const progressPercent = computed(() => ((activeSlide.value) / totalSlides) * 100)

// ─── Data ────────────────────────────────

const teamMembers = [
  { name: 'Member A', role: 'AI & Admin', initial: 'A', color: '#f59e0b' },
  { name: 'Member B', role: 'Backend & DB', initial: 'B', color: '#3b82f6' },
  { name: 'Member C', role: 'Frontend & Docs', initial: 'C', color: '#10b981' },
]

const problems = [
  { icon: 'bi bi-file-earmark-x', title: 'Static Content', desc: 'No intelligence in content delivery', color: '#ef4444' },
  { icon: 'bi bi-shield-x', title: 'Privacy Risk', desc: 'Students use external AI, data leaks', color: '#f59e0b' },
  { icon: 'bi bi-alarm', title: 'Manual Quizzes', desc: 'Hours wasted creating assessments', color: '#ef4444' },
  { icon: 'bi bi-wifi-off', title: 'Data Loss', desc: 'Browser crash = quiz progress gone', color: '#f59e0b' },
  { icon: 'bi bi-graph-down', title: 'No Smart Grading', desc: 'No analytics or automated insights', color: '#ef4444' },
  { icon: 'bi bi-robot', title: 'No AI Support', desc: 'No built-in learning assistant', color: '#f59e0b' },
]

const solutions = [
  { icon: 'bi bi-robot', title: 'AI Chatbot', desc: 'Context-aware RAG answers', bg: '#dbeafe' },
  { icon: 'bi bi-file-earmark-check', title: 'Auto Quiz', desc: 'Generate from documents', bg: '#fef3c7' },
  { icon: 'bi bi-shield-check', title: 'Crash-Safe', desc: 'Auto-save everything', bg: '#d1fae5' },
  { icon: 'bi bi-bar-chart-fill', title: 'Smart Grading', desc: 'Weighted components', bg: '#e0e7ff' },
  { icon: 'bi bi-lock-fill', title: 'Secure Auth', desc: 'JWT with rate limiting', bg: '#fce7f3' },
]

const objectives = [
  'Build an AI-powered learning ecosystem with personalized tutoring',
  'Automate assessment creation from documents using LLMs',
  'Design a secure multi-role platform with JWT authentication',
  'Implement a crash-resilient quiz engine with zero data loss',
  'Create a comprehensive grading system with analytics',
]

const modules = [
  {
    icon: 'bi bi-gear-fill', title: 'Admin', color: '#ef4444',
    features: ['User Management', 'Institutions & Departments', 'Courses & Semesters', 'Library & Timetables']
  },
  {
    icon: 'bi bi-easel-fill', title: 'Teacher', color: '#f59e0b',
    features: ['Class Management', 'AI Quiz Generator', 'Gradebook System', 'Attendance & Resources']
  },
  {
    icon: 'bi bi-mortarboard-fill', title: 'Student', color: '#10b981',
    features: ['AI Learning Chatbot', 'Quiz Participation', 'Assignments & Grades', 'Library & GPA Calculator']
  },
]

const techStack = [
  { icon: 'bi bi-filetype-py', name: 'Vue 3 + Vite', purpose: 'Frontend SPA', color: '#42b883' },
  { icon: 'bi bi-filetype-py', name: 'Django + DRF', purpose: 'Backend REST API', color: '#092e20' },
  { icon: 'bi bi-database-fill', name: 'SQLite', purpose: 'Database', color: '#003b57' },
  { icon: 'bi bi-cpu-fill', name: 'LangChain', purpose: 'AI Orchestration', color: '#059669' },
  { icon: 'bi bi-search', name: 'FAISS', purpose: 'Vector Search', color: '#7c3aed' },
  { icon: 'bi bi-shield-lock-fill', name: 'JWT Auth', purpose: 'Security', color: '#dc2626' },
]

const features = [
  { icon: 'bi bi-chat-dots-fill text-warning', title: 'RAG Chatbot', desc: 'Answers from your materials only' },
  { icon: 'bi bi-file-earmark-plus text-warning', title: 'Quiz Generator', desc: 'MCQ, Short & Long Answer' },
  { icon: 'bi bi-speedometer2 text-warning', title: 'Smart Grading', desc: 'Components, weightage, audit' },
  { icon: 'bi bi-cloud-check text-warning', title: 'Auto-Save Quiz', desc: 'Zero data loss guaranteed' },
  { icon: 'bi bi-shield-check text-warning', title: 'JWT Security', desc: 'Token rotation + rate limit' },
  { icon: 'bi bi-people-fill text-warning', title: 'Multi-Role', desc: 'Admin, Teacher, Student' },
]

const teamRoles = [
  {
    name: 'Member A', initial: 'A', tag: 'AI & Admin', color: '#f59e0b',
    tasks: ['RAG Chatbot Pipeline', 'AI Quiz Generator', 'FAISS Vector Engine', 'Admin Portal (13 modules)']
  },
  {
    name: 'Member B', initial: 'B', tag: 'Backend & DB', color: '#3b82f6',
    tasks: ['Database Architecture', 'REST APIs', 'Grading System', 'JWT Authentication']
  },
  {
    name: 'Member C', initial: 'C', tag: 'Frontend & Docs', color: '#10b981',
    tasks: ['Teacher & Student UI', 'Shared Components', 'Landing Page', 'IEEE Documentation']
  },
]

const demoScreens = [
  { icon: 'bi bi-house-door-fill', label: 'Landing Page', color: '#facc15' },
  { icon: 'bi bi-box-arrow-in-right', label: 'Login', color: '#3b82f6' },
  { icon: 'bi bi-speedometer2', label: 'Admin Panel', color: '#ef4444' },
  { icon: 'bi bi-robot', label: 'AI Chatbot', color: '#10b981' },
  { icon: 'bi bi-file-earmark-check', label: 'Quiz Generator', color: '#f59e0b' },
  { icon: 'bi bi-clock-history', label: 'Student Quiz', color: '#8b5cf6' },
]

const futureWork = [
  { icon: 'bi bi-phone', title: 'Mobile App', desc: 'Native mobile for learning on the go', color: '#3b82f6' },
  { icon: 'bi bi-lightning-fill', title: 'Multi-Institution Support', desc: 'Support for multiple institutions', color: '#f59e0b' },
  { icon: 'bi bi-search-heart', title: 'Plagiarism Check', desc: 'AI-powered similarity matching', color: '#ef4444' },
  { icon: 'bi bi-graph-up-arrow', title: 'Predictive Analytics', desc: 'Early warning for at-risk students', color: '#10b981' },
  { icon: 'bi bi-cloud-arrow-up', title: 'Cloud Scaling', desc: 'Cloud vector DB for multi-institution', color: '#8b5cf6' },
]

const qaItems = [
  { q: 'What is this project about?', a: 'An LMS that uses local AI to auto-generate quizzes from PDFs and provide a context-aware chatbot for students.' },
  { q: 'Why Django instead of Node.js?', a: 'Our system is AI-heavy (LangChain, FAISS). Python is native for AI — Django keeps backend and AI together.' },
  { q: 'Will students cheat using the chatbot?', a: 'No. It only retrieves from teacher-uploaded docs — equivalent to searching your notes, but faster.' },
  { q: 'Why SQLite + FAISS?', a: 'Zero-config portability. FAISS runs locally — no cloud cost, complete data privacy.' },
  { q: 'How does auto-save work?', a: 'QuizAttempt stores a JSON object. Vue sends PATCH on every answer. Browser crash = zero data loss.' },
  { q: 'How is this different from ChatGPT?', a: 'ChatGPT uses internet data and can hallucinate. Our chatbot is bound to course-specific documents only.' },
]

const thanksChips = [
  { icon: 'bi bi-robot', label: 'AI Chatbot' },
  { icon: 'bi bi-file-earmark-check', label: 'Auto Quiz' },
  { icon: 'bi bi-bar-chart-fill', label: 'Smart Grading' },
  { icon: 'bi bi-shield-check', label: 'Secure Platform' },
]

// ─── Navigation ────────────────────────────

const scrollToSlide = (n) => {
  const slides = slidesRef.value?.querySelectorAll('.pres-slide')
  if (slides && slides[n - 1]) {
    slides[n - 1].scrollIntoView({ behavior: 'smooth' })
  }
}

const goNext = () => {
  if (activeSlide.value < totalSlides) {
    scrollToSlide(activeSlide.value + 1)
  } else if (autoPlaying.value) {
    stopAutoPlay()
  }
}

const goPrev = () => {
  if (activeSlide.value > 1) scrollToSlide(activeSlide.value - 1)
}

// ─── Scroll Tracking ────────────────────────

const handleScroll = () => {
  if (!slidesRef.value) return
  const slides = slidesRef.value.querySelectorAll('.pres-slide')
  const scrollTop = window.scrollY + window.innerHeight / 2
  slides.forEach((slide, index) => {
    if (scrollTop >= slide.offsetTop && scrollTop < slide.offsetTop + slide.offsetHeight) {
      activeSlide.value = index + 1
    }
  })
}

// ─── Keyboard ────────────────────────────

const handleKey = (e) => {
  // Ignore if user is typing somewhere
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return

  switch (e.key) {
    case 'ArrowDown':
    case 'ArrowRight':
    case ' ':
      e.preventDefault()
      goNext()
      break
    case 'ArrowUp':
    case 'ArrowLeft':
      e.preventDefault()
      goPrev()
      break
    case 'f':
    case 'F':
      e.preventDefault()
      toggleFullscreen()
      break
    case 'a':
    case 'A':
      e.preventDefault()
      toggleAutoPlay()
      break
    case 'Escape':
      if (isFullscreen.value) exitFullscreen()
      if (autoPlaying.value) stopAutoPlay()
      break
  }

  // Show controls briefly on any keypress in fullscreen
  if (isFullscreen.value) flashControls()
}

// ─── Fullscreen ────────────────────────────

const toggleFullscreen = () => {
  if (isFullscreen.value) {
    exitFullscreen()
  } else {
    enterFullscreen()
  }
}

const enterFullscreen = () => {
  const el = wrapperRef.value
  if (!el) return
  if (el.requestFullscreen) el.requestFullscreen()
  else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen()
  isFullscreen.value = true
  flashControls()
}

const exitFullscreen = () => {
  if (document.exitFullscreen) document.exitFullscreen()
  else if (document.webkitExitFullscreen) document.webkitExitFullscreen()
  isFullscreen.value = false
  showControls.value = true
}

const flashControls = () => {
  showControls.value = true
  clearTimeout(controlsTimer)
  controlsTimer = setTimeout(() => {
    if (isFullscreen.value) showControls.value = false
  }, 3000)
}

const handleFullscreenChange = () => {
  if (!document.fullscreenElement && !document.webkitFullscreenElement) {
    isFullscreen.value = false
    showControls.value = true
  }
}

// ─── Auto-Play ────────────────────────────

const toggleAutoPlay = () => {
  if (autoPlaying.value) {
    stopAutoPlay()
  } else {
    startAutoPlay()
  }
}

const startAutoPlay = () => {
  autoPlaying.value = true
  autoPlayTick.value++
  autoPlayTimer = setInterval(() => {
    goNext()
    autoPlayTick.value++
  }, autoPlayInterval)
}

const stopAutoPlay = () => {
  autoPlaying.value = false
  clearInterval(autoPlayTimer)
  autoPlayTimer = null
}

// Stop auto-play if user manually scrolls or navigates
watch(activeSlide, () => {
  if (autoPlaying.value) {
    // Reset the tick to restart the timer bar animation
    autoPlayTick.value++
  }
})

// ─── Mouse move (show controls in fullscreen) ────

const handleMouseMove = () => {
  if (isFullscreen.value) flashControls()
}

// ─── Lifecycle ────────────────────────────

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  wrapperRef.value?.focus()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  clearInterval(autoPlayTimer)
  clearTimeout(controlsTimer)
})
</script>

<style scoped>
/* ============================================
   CORE
============================================ */
.pres-wrapper {
  outline: none;
}

/* ============================================
   TOP BAR
============================================ */
.pres-topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.6rem 1.5rem;
  background: rgba(11, 17, 32, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.pres-topbar-hidden {
  opacity: 0;
  transform: translateY(-100%);
  pointer-events: none;
}

.pres-brand {
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  text-decoration: none;
  white-space: nowrap;
}

.pres-brand i { color: #facc15; }

.pres-progress-wrap {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.pres-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #facc15, #f59e0b);
  transition: width 0.4s ease;
  border-radius: 4px;
}

.pres-counter {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

/* Controls */
.pres-controls {
  display: flex;
  gap: 0.4rem;
}

.pres-ctrl-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.9rem;
}

.pres-ctrl-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* Auto-play bar */
.pres-autoplay-bar {
  position: fixed;
  top: 52px;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 999;
  background: transparent;
}

.pres-autoplay-fill {
  height: 100%;
  background: #facc15;
  animation: pres-autoplay-progress linear forwards;
  width: 0;
}

@keyframes pres-autoplay-progress {
  from { width: 0; }
  to { width: 100%; }
}

/* ============================================
   SLIDE BASE
============================================ */
.pres-slide {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4.5rem 2rem 3rem;
}

.pres-slide-inner {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

.pres-slide-dark {
  background: linear-gradient(135deg, #0b1120 0%, #172554 50%, #0b1120 100%);
  color: #fff;
}

.pres-slide-light {
  background: #f8fafc;
  color: #0f172a;
}

.pres-slide-accent {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
  color: #fff;
}

/* ============================================
   SLIDE HEADER
============================================ */
.pres-slide-header { margin-bottom: 1rem; }

.pres-slide-num {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 2px;
  display: block;
  margin-bottom: 0.5rem;
}

.pres-slide-num-light {
  font-size: 0.75rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.3);
  letter-spacing: 2px;
  display: block;
  margin-bottom: 0.5rem;
}

.pres-heading {
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1.15;
}

/* ============================================
   TITLE SLIDE
============================================ */
.pres-title-xl {
  font-size: clamp(3rem, 8vw, 5.5rem);
  font-weight: 900;
  letter-spacing: -2px;
  color: #fff;
  line-height: 1;
}

.pres-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
  margin-bottom: 0;
}

.pres-badge {
  display: inline-block;
  padding: 0.35rem 1.2rem;
  background: rgba(250, 204, 21, 0.15);
  border: 1px solid rgba(250, 204, 21, 0.3);
  border-radius: 50px;
  color: #facc15;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.pres-divider {
  width: 60px;
  height: 3px;
  background: #facc15;
  border-radius: 3px;
  margin: 1.2rem auto;
}

.pres-meta {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.9rem;
}

.pres-member-chip {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.6rem 0.9rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  text-align: left;
}

.pres-member-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.9rem;
  color: #fff;
  flex-shrink: 0;
}

/* ============================================
   LIST
============================================ */
.pres-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.pres-list li {
  padding: 0.85rem 0;
  font-size: 1.05rem;
  font-weight: 500;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
}

.pres-list li:last-child { border-bottom: none; }

/* ============================================
   VISUAL CARD
============================================ */
.pres-visual-card {
  padding: 2.5rem;
  background: #fff;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  text-align: center;
}

/* ============================================
   SPEAKER NOTE
============================================ */
.pres-speaker-note {
  margin-top: 2rem;
  padding: 0.8rem 1.2rem;
  background: rgba(0, 0, 0, 0.04);
  border-left: 3px solid #facc15;
  border-radius: 0 8px 8px 0;
  font-size: 0.82rem;
  color: #64748b;
  font-style: italic;
}

.pres-note-dark {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.4);
}

/* ============================================
   CARDS — Lightweight (no hover animations)
============================================ */
.pres-problem-card,
.pres-solution-card,
.pres-tech-card,
.pres-feature-chip,
.pres-future-card,
.pres-demo-card,
.pres-qa-card {
  padding: 1.4rem;
  border-radius: 14px;
  text-align: center;
  height: 100%;
}

.pres-problem-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.pres-solution-card {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.pres-sol-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.pres-tech-card {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.pres-feature-chip {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #fff;
}

.pres-future-card {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.pres-demo-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.pres-qa-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  text-align: left;
}

/* ============================================
   OBJECTIVE ROWS
============================================ */
.pres-obj-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.2rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

.pres-obj-num {
  font-size: 0.7rem;
  font-weight: 800;
  color: #facc15;
  min-width: 28px;
}

/* ============================================
   ARCHITECTURE DIAGRAM
============================================ */
.pres-arch-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.pres-arch-layer {
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  text-align: center;
  width: 100%;
  max-width: 320px;
}

.pres-arch-frontend { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.pres-arch-backend { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.pres-arch-db { background: #e0e7ff; color: #3730a3; border: 1px solid #a5b4fc; flex: 1; }
.pres-arch-ai { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; flex: 1; }

.pres-arch-arrow {
  color: #94a3b8;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0;
}

.pres-arch-row {
  display: flex;
  gap: 0.6rem;
  width: 100%;
  max-width: 320px;
}

.pres-arch-sublabel {
  font-size: 0.7rem;
  font-weight: 400;
  opacity: 0.7;
  margin-top: 0.2rem;
}

/* ============================================
   MODULE CARDS
============================================ */
.pres-module-card {
  padding: 1.8rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  text-align: center;
  height: 100%;
}

.pres-mod-icon-ring {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.pres-mod-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0;
  text-align: left;
}

.pres-mod-list li {
  padding: 0.35rem 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.pres-mod-list li::before {
  content: '→ ';
  color: rgba(255, 255, 255, 0.25);
}

/* ============================================
   TEAM ROLES
============================================ */
.pres-role-card {
  padding: 2rem 1.5rem;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  text-align: center;
  height: 100%;
}

.pres-role-avatar {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  color: #fff;
  margin: 0 auto;
}

.pres-role-list {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
}

.pres-role-list li {
  padding: 0.35rem 0;
  font-size: 0.85rem;
  color: #64748b;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.pres-role-list li::before {
  content: '✓ ';
  color: #10b981;
  font-weight: 700;
}

/* ============================================
   THANK YOU CHIPS
============================================ */
.pres-thanks-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.55rem 1.2rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 50px;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
}

/* ============================================
   BOTTOM HINT BAR
============================================ */
.pres-hint-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  justify-content: center;
  gap: 2rem;
  padding: 0.5rem 1rem;
  background: rgba(11, 17, 32, 0.85);
  backdrop-filter: blur(8px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 500;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.pres-hint-hidden {
  opacity: 0;
  transform: translateY(100%);
  pointer-events: none;
}

.pres-hint-bar i {
  font-size: 0.8rem;
  margin-right: 0.3rem;
}

/* ============================================
   RESPONSIVE
============================================ */
@media (max-width: 768px) {
  .pres-heading { font-size: 1.6rem; }
  .pres-title-xl { font-size: 2.8rem; }
  .pres-slide { padding: 4rem 1rem 2.5rem; }
  .pres-list li { font-size: 0.92rem; }
  .pres-arch-layer { padding: 0.8rem 1.2rem; font-size: 0.85rem; }
  .pres-hint-bar { gap: 1rem; font-size: 0.65rem; }
}
</style>
