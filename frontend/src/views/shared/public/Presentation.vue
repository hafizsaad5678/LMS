<template>
  <div class="pres-wrapper homescreen-wrapper" @keydown="handleKey" tabindex="0" ref="wrapperRef" @mousemove="handleMouseMove">

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
          <p class="pres-meta">BSCS 8th Semester <br>
          Government Graduate College, Aroop Gujranwala <br>Affiliated with University of Gujrat</p>
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
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"Assalam-o-Alaikum, today we are presenting LearnMS, an AI-based LMS. I am Hafiz Saad, and with me are my teammates Muhammad Sarfaraz and Kamran."
          </div>
        </div>
      </section>

      <!-- SLIDE 2 - Introduction -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">02</span>
            <h2 class="pres-heading">What is LearnMS?</h2>
            <p class="text-muted mt-1 mb-0" style="font-size: 0.95rem;">Reduces teacher workload by automating quiz creation and provides students 24/7 course-based assistance.</p>
          </div>
          <div class="row g-4 mt-3">
            <div class="col-lg-7">
              <ul class="pres-list">
                <li><i class="bi bi-mortarboard-fill text-primary me-3"></i>Smart LMS designed for universities</li>
                <li><i class="bi bi-robot text-primary me-3"></i>AI integrated directly into learning</li>
                <li><i class="bi bi-people-fill text-primary me-3"></i>Three panels: Admin, Teacher, Student</li>
                <li><i class="bi bi-chat-dots-fill text-primary me-3"></i>AI Chatbot answers from your own materials</li>
                <li><i class="bi bi-file-earmark-check-fill text-primary me-3"></i>AI-Powered Quiz Generation</li>
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
            <i class="bi bi-mic-fill me-2"></i>"LearnMS is a smart Learning Management System designed for universities. Overall, LearnMS is not just an LMS — it is a complete intelligent learning ecosystem."
          </div>
        </div>
      </section>

      <!-- SLIDE 3 - Problem -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">03</span>
            <h2 class="pres-heading text-white">The Problem</h2>
            <p class="text-warning fw-semibold mt-2 mb-0" style="font-size: 1.05rem;">"Current LMS systems are static, manual, and lack intelligence."</p>
          </div>
          <div class="row g-4 mt-4 justify-content-center">
            <div class="col-md-3 col-6" v-for="(prob, i) in problems" :key="i">
              <div class="pres-problem-card">
                <i :class="[prob.icon, 'display-6 mb-3']" :style="{ color: prob.color }"></i>
                <h6 class="fw-bold text-white">{{ prob.title }}</h6>
                <p class="small text-white-50 mb-0">{{ prob.desc }}</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"Current LMS platforms have several limitations. They are mostly static, requiring teachers to manually create quizzes and manage content. Students often lack continuous guidance, and there is no intelligent support system. Additionally, systems are not reliable — issues like data loss during quizzes can occur. These problems reduce efficiency and learning effectiveness."
          </div>
        </div>
      </section>

      <!-- SLIDE 4 - Solution -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">04</span>
            <h2 class="pres-heading">Problem → Solution</h2>
            <p class="text-muted mt-1 mb-0">Every problem has a direct solution</p>
          </div>
          <div class="mt-4" style="max-width: 750px; margin: 0 auto;">
            <div class="pres-mapping-row" v-for="(map, i) in solutionMapping" :key="i">
              <div class="pres-map-problem">
                <i :class="map.probIcon" class="me-2" :style="{ color: '#ef4444' }"></i>
                {{ map.problem }}
              </div>
              <div class="pres-map-arrow">
                <i class="bi bi-arrow-right"></i>
              </div>
              <div class="pres-map-solution">
                <i :class="map.solIcon" class="me-2" :style="{ color: '#10b981' }"></i>
                {{ map.solution }}
              </div>
            </div>
          </div>
          <div class="pres-speaker-note">
            <i class="bi bi-mic-fill me-2"></i>"To solve these problems, we designed LearnMS with direct solutions. Lack of student support is solved through an intelligent assistant. Data loss is handled with a secure auto-save mechanism. Each problem we identified has a corresponding solution built into our system."
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
            <i class="bi bi-mic-fill me-2"></i>"The main objectives of our project are: To build a smart and efficient learning system, and improve the overall learning experience for students and teachers."
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
            <i class="bi bi-mic-fill me-2"></i>"Our system follows a decoupled architecture. The frontend is built using modern web technologies, while the backend handles APIs, database, and system logic. (Handover):
          </div>
        </div>
      </section>

      <!-- SLIDE 7 - Modules -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">07</span>
            <h2 class="pres-heading text-white">Core Modules</h2>
            <p class="text-white-50 mt-1 mb-0">Each module is isolated but connected through APIs</p>
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
            <i class="bi bi-mic-fill me-2"></i>"The system is divided into three main modules: Admin, Teacher, and Student. The Admin manages users, departments, and courses. The Teacher handles class management, quizzes, grading, and resources. The Student interacts with the system through quizzes, assignments, and learning materials. The quiz generation feature is implemented here, but its detailed working will be explained later by Saad."
          </div>
        </div>
      </section>

      <!-- SLIDE 8 - Tech Stack -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">08</span>
            <h2 class="pres-heading">Tech Stack</h2>
            <p class="text-muted mt-1 mb-0">Selected based on performance and AI compatibility</p>
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
            <i class="bi bi-mic-fill me-2"></i>"For backend development, we used Django and Django REST Framework to build secure and scalable APIs. The database is managed using SQLite, which is lightweight and portable. We also implemented authentication using JWT tokens."
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
            <i class="bi bi-mic-fill me-2"></i>"Key backend features include: Secure authentication system, Automated grading system, Quiz management and attempt tracking, Reliable data handling with auto-save functionality. (Handover): I invite Kamran to explain the frontend."
          </div>
        </div>
      </section>

      <!-- SLIDE 10 - Roles -->
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
            <i class="bi bi-mic-fill me-2"></i>"As shown here, each team member contributed to different parts of the system. I focused on the frontend design and user experience, especially for Teacher and Student panels. The goal was to make the system simple and intuitive."
          </div>
        </div>
      </section>

      <!-- SLIDE 11 - Demo -->
      <section class="pres-slide pres-slide-dark" id="slide-demo">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">11</span>
            <h2 class="pres-heading text-white">System Demo & UI</h2>
            <p class="text-white-50 mt-1 mb-0">Fully responsive and user-friendly interface</p>
          </div>
          
          <div class="pres-ui-gallery mt-4">
            <div class="pres-ui-card">
              <img src="@/assets/login.png" alt="Login Screen">
              <div class="pres-ui-label">Login System</div>
              <div class="pres-ui-preview" aria-hidden="true">
                <img src="@/assets/login.png" alt="Login Screen full preview">
              </div>
            </div>
            <div class="pres-ui-card">
              <img src="@/assets/studentdashboard.png" alt="Student Dashboard">
              <div class="pres-ui-label">Student Interface</div>
              <div class="pres-ui-preview" aria-hidden="true">
                <img src="@/assets/studentdashboard.png" alt="Student Dashboard full preview">
              </div>
            </div>
            <div class="pres-ui-card">
              <img src="@/assets/teacherdashboard.png" alt="Teacher Dashboard">
              <div class="pres-ui-label">Teacher Panel</div>
              <div class="pres-ui-preview" aria-hidden="true">
                <img src="@/assets/teacherdashboard.png" alt="Teacher Dashboard full preview">
              </div>
            </div>
          </div>

          <div class="text-center mt-4">
            <router-link to="/login" class="btn btn-warning rounded-pill px-5 py-2 fw-bold shadow">
              <i class="bi bi-play-circle-fill me-2"></i>Launch Live App
            </router-link>
          </div>

          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"This slide shows the main screens of our system. The interface is fully responsive and user-friendly. Features like chatbot and quiz interface are fully integrated. Now I invite Hafiz Saad to explain the core intelligence."
          </div>
        </div>
      </section>

      <!-- SLIDE 12 - AI Logic -->
      <section class="pres-slide pres-slide-accent" id="slide-ai-logic">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">12</span>
            <h2 class="pres-heading text-white">How Our AI Works</h2>
            <p class="text-warning fw-semibold mt-2 mb-0">"Our AI retrieves answers from actual course data."</p>
          </div>
          <div class="mt-4" style="max-width: 520px; margin: 0 auto;">
            <div class="pres-ai-step" v-for="(step, i) in aiSteps" :key="i">
              <div class="pres-ai-step-num">{{ String(i + 1).padStart(2, '0') }}</div>
              <div class="pres-ai-step-icon">
                <i :class="step.icon"></i>
              </div>
              <div>
                <h6 class="fw-bold text-white mb-1">{{ step.title }}</h6>
                <p class="small text-white-50 mb-0">{{ step.desc }}</p>
              </div>
            </div>
          </div>
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"This is our RAG pipeline. We don't use general internet data; we use course-specific embeddings stored in FAISS for 100% accuracy and zero hallucination."
          </div>
        </div>
      </section>

      <!-- SLIDE 13 - Admin Panel -->
      <section class="pres-slide pres-slide-dark pres-slide-admin">
        <div class="pres-slide-inner">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">13</span>
            <h2 class="pres-heading">Admin Panel - System Control Center</h2>
          </div>
          <div class="pres-admin-layout mt-4">
            <div class="pres-admin-left">
              <div class="row g-3 justify-content-center" style="max-width: 820px; margin: 0 auto;">
                <div class="col-md-6 col-12" v-for="(point, i) in adminControlPoints" :key="i">
                  <div class="pres-problem-card pres-admin-mini-card">
                    <i :class="[point.icon, 'display-6 mb-2']"></i>
                    <h6 class="fw-bold text-white mb-0">{{ point.title }}</h6>
                  </div>
                </div>
              </div>
              <div class="pres-admin-boundary"></div>
            </div>
            <div class="pres-admin-right">
              <div class="pres-ui-card pres-admin-image-card">
                <img src="@/assets/admindashboard.png" alt="Admin Dashboard">
                <div class="pres-ui-label">Admin Dashboard</div>
                <div class="pres-ui-preview" aria-hidden="true">
                  <img src="@/assets/admindashboard.png" alt="Admin Dashboard full preview">
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- SLIDE 14 - Future -->
      <section class="pres-slide pres-slide-light">
        <div class="pres-slide-inner">
          <div class="pres-slide-header">
            <span class="pres-slide-num">14</span>
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
            <i class="bi bi-mic-fill me-2"></i>"In the future, we aim to add native mobile support and predictive analytics to identify at-risk students before they fail."
          </div>
        </div>
      </section>

      <!-- SLIDE 15 - Q&A -->
      <section class="pres-slide pres-slide-dark">
        <div class="pres-slide-inner text-center">
          <div class="pres-slide-header text-center">
            <span class="pres-slide-num-light">15</span>
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
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"We are now open for any technical or functional questions regarding LearnMS."
          </div>
        </div>
      </section>

      <!-- SLIDE 16 - Thank You -->
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
          <div class="pres-speaker-note pres-note-dark">
            <i class="bi bi-mic-fill me-2"></i>"Thank you for your time. This concludes our presentation."
          </div>
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
const totalSlides = 16

// Fullscreen
const isFullscreen = ref(false)
const showControls = ref(true)
let controlsTimer = null

// Auto-play
const autoPlaying = ref(false)
const autoPlayInterval = 7000 
const autoPlayTick = ref(0)
let autoPlayTimer = null

const progressPercent = computed(() => ((activeSlide.value) / totalSlides) * 100)

// ─── Data ────────────────────────────────

const teamMembers = [
  { name: 'Hafiz Saad', role: 'AI & Admin', initial: 'A', color: '#f59e0b' },
  { name: 'Muhammad Sarfaraz', role: 'Backend & DB', initial: 'B', color: '#3b82f6' },
  { name: 'Kamran', role: 'Frontend & Docs', initial: 'C', color: '#10b981' },
]

const problems = [
  { icon: 'bi bi-file-earmark-x', title: 'Static Content', desc: 'No intelligence in learning delivery', color: '#ef4444' },
  { icon: 'bi bi-alarm', title: 'Manual Quizzes', desc: 'Teachers spend hours on assessments', color: '#f59e0b' },
  { icon: 'bi bi-wifi-off', title: 'Data Loss', desc: 'Browser crash = quiz progress gone', color: '#ef4444' },
  { icon: 'bi bi-robot', title: 'No AI Support', desc: 'No contextual learning assistant', color: '#f59e0b' },
]

const solutionMapping = [
  { problem: 'Manual quiz creation', probIcon: 'bi bi-alarm', solution: 'AI Quiz Generator', solIcon: 'bi bi-file-earmark-check' },
  { problem: 'No student guidance', probIcon: 'bi bi-question-circle', solution: 'AI RAG Chatbot', solIcon: 'bi bi-robot' },
  { problem: 'Quiz data loss', probIcon: 'bi bi-wifi-off', solution: 'Auto-Save Engine', solIcon: 'bi bi-shield-check' },
  { problem: 'No smart analytics', probIcon: 'bi bi-graph-down', solution: 'Weighted Grading', solIcon: 'bi bi-bar-chart-fill' },
]

const aiSteps = [
  { icon: 'bi bi-lightbulb', title: 'Core Intelligence: RAG', desc: 'The core intelligence of LearnMS is based on Retrieval-Augmented Generation (RAG).' },
  { icon: 'bi bi-scissors', title: 'Document Chunking', desc: 'First, documents are uploaded and divided into smaller chunks.' },
  { icon: 'bi bi-database-add', title: 'Vector Storage in FAISS', desc: 'These chunks are converted into vector representations and stored using FAISS.' },
  { icon: 'bi bi-search', title: 'Relevant Content Retrieval', desc: 'When a user asks a question, the system retrieves the most relevant content from these stored vectors.' },
  { icon: 'bi bi-chat-text', title: 'Response with LangChain', desc: 'Using LangChain, the system generates a response based only on this retrieved data.' },
  { icon: 'bi bi-shield-check', title: 'Course-Specific Accuracy', desc: 'The system does not rely on the internet and provides accurate, course-specific answers.' },
]

const adminControlPoints = [
  { icon: 'bi bi-people-fill', title: 'User Management (Students & Teachers)' },
  { icon: 'bi bi-diagram-3-fill', title: 'Department & Course Management' },
  { icon: 'bi bi-mortarboard-fill', title: 'Academic Structure (Semesters, Classes)' },
  { icon: 'bi bi-calendar3', title: 'Timetable & Scheduling' },
  { icon: 'bi bi-megaphone-fill', title: 'Event Management' },
  { icon: 'bi bi-journal-bookmark-fill', title: 'Digital Library Control' },
  { icon: 'bi bi-speedometer2', title: 'System Monitoring & Control' },
]

const objectives = [
  'Build an AI-powered learning ecosystem with personalized tutoring',
  'Automate assessment creation using LLMs',
  'Design a secure multi-role platform with JWT authentication',
  'Implement a crash-resilient quiz engine with zero data loss',
  'Create a comprehensive grading system with analytics',
]

const modules = [
  {
    icon: 'bi bi-gear-fill', title: 'Admin', color: '#ef4444',
    features: ['The Admin module handles overall system control and management.','User Management', 'Institutions & Departments', 'Courses & Semesters', 'Library & Timetables']
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
  { icon: 'bi bi-filetype-py', name: 'Django + DRF', purpose: 'APIs + AI in one codebase', color: '#092e20' },
  { icon: 'bi bi-database-fill', name: 'SQLite', purpose: 'Portable, zero-config DB', color: '#003b57' },
  { icon: 'bi bi-shield-lock-fill', name: 'JWT Auth', purpose: 'Tokens + rate limiting', color: '#dc2626' },
]

const features = [
  { icon: 'bi bi-shield-check text-warning', title: 'JWT Security', desc: 'Secure authentication system' },
  { icon: 'bi bi-speedometer2 text-warning', title: 'Automated Grading', desc: 'Components, weightage, audit' },
  { icon: 'bi bi-file-earmark-plus text-warning', title: 'Quiz Management', desc: 'Attempt, Review, Edit' },
  { icon: 'bi bi-cloud-check text-warning', title: 'Auto-Save Quiz', desc: 'Zero data loss guaranteed' },
]

const teamRoles = [
  {
    name: 'Hafiz Saad', initial: 'A', tag: 'AI & Admin', color: '#f59e0b',
    tasks: ['Hafiz Saad worked on AI systems and also contributed to the Admin module.','RAG Chatbot Pipeline', 'AI Quiz Generator', 'FAISS Vector Engine', 'Admin Portal (13 modules)']
  },
  {
    name: 'Muhammad Sarfaraz', initial: 'B', tag: 'Backend & DB', color: '#3b82f6',
    tasks: ['Database Architecture', 'REST APIs', 'Grading System', 'JWT Authentication']
  },
  {
    name: 'Kamran', initial: 'C', tag: 'Frontend & Docs', color: '#10b981',
    tasks: ['Teacher & Student UI', 'Shared Components', 'Landing Page', 'IEEE Documentation']
  },
]

const futureWork = [
  { icon: 'bi bi-phone', title: 'Mobile App', desc: 'Native mobile for learning on the go', color: '#3b82f6' },
  { icon: 'bi bi-lightning-fill', title: 'Multi-Institution Support', desc: 'Support for multiple institutions', color: '#f59e0b' },
  { icon: 'bi bi-search-heart', title: 'Plagiarism Check', desc: 'AI-powered similarity matching', color: '#ef4444' },
  { icon: 'bi bi-graph-up-arrow', title: 'Predictive Analytics', desc: 'Early warning for at-risk students', color: '#10b981' },
]

const qaItems = [
  { q: 'What is this project about?', a: 'An LMS that auto-generates quizzes from PDFs and provide a context-aware chatbot for students.' },
  { q: 'Why Django instead of Node.js?', a: 'Our system is AI-heavy (LangChain, FAISS). Python is native for AI — Django keeps it all together.' },
  { q: 'Will students cheat using the chatbot?', a: 'No. It only retrieves from teacher-uploaded docs — equivalent to searching your notes.' },
  { q: 'Why this project?', a: 'To solve inefficiency in e‑learning. Teachers spend too much time creating assessments; students lack 24/7 help.' },
  { q: 'How does auto-save work?', a: 'Vue sends PATCH on every answer. Browser crash = zero data loss.' },
  { q: 'How is this different from ChatGPT?', a: 'Our chatbot is bound to course-specific documents only, with zero hallucination.' },
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

const handleKey = (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
  switch (e.key) {
    case 'ArrowDown': case 'ArrowRight': case ' ': e.preventDefault(); goNext(); break;
    case 'ArrowUp': case 'ArrowLeft': e.preventDefault(); goPrev(); break;
    case 'f': case 'F': e.preventDefault(); toggleFullscreen(); break;
    case 'a': case 'A': e.preventDefault(); toggleAutoPlay(); break;
    case 'Escape': 
      if (isFullscreen.value) exitFullscreen()
      if (autoPlaying.value) stopAutoPlay()
      break
  }
  if (isFullscreen.value) flashControls()
}

// ─── Fullscreen ────────────────────────────

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

const toggleFullscreen = () => isFullscreen.value ? exitFullscreen() : enterFullscreen()

const flashControls = () => {
  showControls.value = true
  clearTimeout(controlsTimer)
  controlsTimer = setTimeout(() => { if (isFullscreen.value) showControls.value = false }, 3000)
}

const handleFullscreenChange = () => {
  if (!document.fullscreenElement && !document.webkitFullscreenElement) {
    isFullscreen.value = false
    showControls.value = true
  }
}

// ─── Auto-Play ────────────────────────────

const startAutoPlay = () => {
  autoPlaying.value = true
  autoPlayTick.value++
  autoPlayTimer = setInterval(() => { goNext(); autoPlayTick.value++ }, autoPlayInterval)
}

const stopAutoPlay = () => {
  autoPlaying.value = false
  clearInterval(autoPlayTimer)
  autoPlayTimer = null
}

const toggleAutoPlay = () => autoPlaying.value ? stopAutoPlay() : startAutoPlay()

watch(activeSlide, () => { if (autoPlaying.value) autoPlayTick.value++ })

const handleMouseMove = () => { if (isFullscreen.value) flashControls() }

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
   UI SHOWCASE GALLERY 
============================================ */
.pres-ui-gallery {
  display: flex !important;
  justify-content: center !important;
  gap: 15px !important;
  margin: 1.5rem auto !important;
  max-width: 900px !important;
}

.pres-ui-card {
  position: relative !important;
  flex: 0 0 160px !important;
  background: #111827 !important;
  border-radius: 10px !important;
  overflow: hidden !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4) !important;
  transition: transform 0.3s ease !important;
}

.pres-ui-card img {
  width: 160px !important;
  height: 100px !important;
  object-fit: contain !important;
  background: #0f172a !important; 
  display: block !important;
}

.pres-ui-preview {
  position: absolute !important;
  left: 50% !important;
  bottom: calc(100% + 12px) !important;
  transform: translateX(-50%) scale(0.92) !important;
  width: min(62vw, 580px) !important;
  background: #020617 !important;
  border: 1px solid rgba(255, 255, 255, 0.24) !important;
  border-radius: 12px !important;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.55) !important;
  opacity: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
  transition: opacity 0.25s ease, transform 0.25s ease !important;
  z-index: 30 !important;
  padding: 6px !important;
}

.pres-ui-preview img {
  width: 100% !important;
  height: auto !important;
  max-height: 68vh !important;
  object-fit: contain !important;
  border-radius: 8px !important;
  background: #0f172a !important;
}

.pres-ui-label {
  padding: 5px !important;
  text-align: center !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  color: #facc15 !important;
  background: rgba(0, 0, 0, 0.8) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.pres-ui-card:hover { transform: translateY(-8px) !important; overflow: visible !important; }
.pres-ui-card:hover .pres-ui-preview {
  opacity: 1 !important;
  visibility: visible !important;
  transform: translateX(-50%) scale(1) !important;
}

/* ============================================ 
   CORE 
============================================ */
.pres-wrapper { outline: none; background: #0b1120; min-height: 100vh; overflow-x: hidden; }
.pres-slides { scroll-snap-type: y mandatory; }

.pres-topbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  display: flex; align-items: center; gap: 1rem; padding: 0.6rem 1.5rem;
  background: rgba(11, 17, 32, 0.92); backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  transition: opacity 0.3s, transform 0.3s;
}

.pres-topbar-hidden { opacity: 0; transform: translateY(-100%); pointer-events: none; }
.pres-brand { color: #fff; font-weight: 700; text-decoration: none; }
.pres-brand i { color: #facc15; }
.pres-progress-wrap { flex: 1; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
.pres-progress-bar { height: 100%; background: linear-gradient(90deg, #facc15, #f59e0b); transition: width 0.4s; }
.pres-counter { color: rgba(255, 255, 255, 0.5); font-size: 0.8rem; font-weight: 600; min-width: 40px; text-align: right; }

.pres-controls { display: flex; gap: 0.4rem; }
.pres-ctrl-btn {
  background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7); border-radius: 8px; width: 34px; height: 34px;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
}

.pres-autoplay-bar { position: fixed; top: 52px; left: 0; right: 0; height: 3px; z-index: 999; }
.pres-autoplay-fill { height: 100%; background: #facc15; animation: pres-autoplay-progress linear forwards; width: 0; }
@keyframes pres-autoplay-progress { from { width: 0; } to { width: 100%; } }

/* ============================================ 
   SLIDE BASE 
============================================ */
.pres-slide { 
  min-height: 100vh; display: flex; align-items: center; justify-content: center; 
  padding: 4.5rem 2rem 3rem; scroll-snap-align: start;
}
.pres-slide-inner { width: 100%; max-width: 1000px; margin: 0 auto; }
.pres-slide-dark { background: linear-gradient(135deg, #0b1120 0%, #172554 50%, #0b1120 100%); color: #fff; }
.pres-slide-light { background: #f8fafc; color: #0f172a; }
.pres-slide-accent { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%); color: #fff; }

.pres-heading { font-size: 2.2rem; font-weight: 800; line-height: 1.15; margin-bottom: 0.5rem; }
.pres-slide-num { font-size: 0.75rem; font-weight: 700; color: #94a3b8; letter-spacing: 2px; }
.pres-slide-num-light { font-size: 0.75rem; font-weight: 700; color: rgba(255, 255, 255, 0.3); letter-spacing: 2px; }

.pres-title-xl { font-size: clamp(3rem, 8vw, 5.5rem); font-weight: 900; letter-spacing: -2px; color: #fff; line-height: 1; }
.pres-subtitle { font-size: 1.2rem; color: rgba(255, 255, 255, 0.5); margin-bottom: 0; }
.pres-badge { display: inline-block; padding: 0.35rem 1.2rem; background: rgba(250, 204, 21, 0.15); border: 1px solid rgba(250, 204, 21, 0.3); border-radius: 50px; color: #facc15; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }
.pres-divider { width: 60px; height: 3px; background: #facc15; border-radius: 3px; margin: 1.2rem auto; }
.pres-meta { color: rgba(255, 255, 255, 0.4); font-size: 0.9rem; }

.pres-member-chip { display: flex; align-items: center; gap: 0.7rem; padding: 0.6rem 0.9rem; background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; text-align: left; }
.pres-member-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #fff; }

.pres-list { list-style: none; padding: 0; }
.pres-list li { padding: 0.85rem 0; font-size: 1.05rem; font-weight: 500; border-bottom: 1px solid rgba(0, 0, 0, 0.06); display: flex; align-items: center; }
.pres-visual-card { padding: 2.5rem; background: #fff; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); text-align: center; }

.pres-speaker-note { margin-top: 2rem; padding: 0.8rem 1.2rem; background: rgba(0,0,0,0.04); border-left: 3px solid #facc15; font-size: 0.82rem; color: #64748b; font-style: italic; }
.pres-note-dark { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.4); }

.pres-problem-card, .pres-tech-card, .pres-feature-chip, .pres-future-card, .pres-qa-card { padding: 1.4rem; border-radius: 14px; text-align: center; height: 100%; border: 1px solid rgba(0,0,0,0.06); background: #fff; }
.pres-problem-card, .pres-feature-chip, .pres-qa-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); }

.pres-mapping-row { display: flex; align-items: center; gap: 0.8rem; padding: 0.9rem 1rem; border-bottom: 1px solid rgba(0,0,0,0.06); }
.pres-map-problem, .pres-map-solution { flex: 1; font-weight: 600; font-size: 0.95rem; display: flex; align-items: center; }
.pres-map-arrow { color: #facc15; font-size: 1.2rem; }

.pres-obj-row { display: flex; align-items: center; gap: 1rem; padding: 0.9rem 1.2rem; background: rgba(255,255,255,0.06); border-radius: 12px; margin-bottom: 0.5rem; }
.pres-obj-num { color: #facc15; font-weight: 800; font-size: 0.7rem; }

.pres-arch-diagram { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.pres-arch-layer { padding: 1rem; border-radius: 12px; font-weight: 600; text-align: center; width: 100%; max-width: 320px; }
.pres-arch-frontend { background: #dbeafe; color: #1e40af; }
.pres-arch-backend { background: #d1fae5; color: #065f46; }
.pres-arch-row { display: flex; gap: 0.6rem; width: 100%; max-width: 320px; }
.pres-arch-db { background: #e0e7ff; color: #3730a3; flex: 1; }
.pres-arch-ai { background: #fef3c7; color: #92400e; flex: 1; }

/* ============================================ 
   MODULE CARDS (Slide 7)
============================================ */
.pres-module-card { 
  padding: 2.2rem 1.8rem; 
  background: rgba(255, 255, 255, 0.04); 
  border-radius: 20px; 
  text-align: center; 
  height: 100%; 
  border: 1px solid rgba(255, 255, 255, 0.08); 
  backdrop-filter: blur(4px);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.pres-module-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 4px;
  background: inherit;
  opacity: 0.8;
}

.pres-module-card:hover {
  transform: translateY(-12px);
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.pres-mod-icon-ring {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  transition: transform 0.4s ease;
}

.pres-module-card:hover .pres-mod-icon-ring {
  transform: scale(1.1) rotate(5deg);
}

.pres-mod-list { 
  list-style: none; 
  padding: 0; 
  margin-top: 1.5rem; 
  text-align: left; 
  font-size: 0.85rem; 
  color: rgba(255, 255, 255, 0.6); 
}

.pres-mod-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.pres-mod-list li::before {
  content: '✦';
  color: #facc15;
  font-size: 0.7rem;
  margin-top: 2px;
}

/* ============================================ 
   TEAM ROLE CARDS (Slide 10)
============================================ */
.pres-role-card { 
  padding: 2.5rem 1.8rem; 
  background: #fff; 
  border-radius: 24px; 
  text-align: center; 
  height: 100%; 
  border: 1px solid rgba(0, 0, 0, 0.05); 
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
  transition: all 0.4s ease;
}

.pres-role-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.08);
  border-color: #facc15;
}

.pres-role-avatar { 
  width: 60px; 
  height: 60px; 
  border-radius: 18px; 
  display: inline-flex; 
  align-items: center; 
  justify-content: center; 
  font-weight: 800; 
  font-size: 1.4rem; 
  color: #fff; 
  margin: 0 auto; 
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
  transition: transform 0.4s ease;
}

.pres-role-card:hover .pres-role-avatar {
  transform: scale(1.1) rotate(-5deg);
}

.pres-role-list { 
  list-style: none; 
  padding: 0; 
  text-align: left; 
  font-size: 0.85rem; 
  color: #64748b; 
  margin-top: 1rem;
}

.pres-role-list li {
  padding: 0.6rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.pres-role-list li::before {
  content: '✔';
  color: #10b981;
  font-weight: 900;
}

.pres-ai-step { display: flex; align-items: center; gap: 0.75rem; padding: 0.65rem 0.8rem; background: rgba(255,255,255,0.04); border-radius: 10px; margin-bottom: 0.45rem; border: 1px solid rgba(255,255,255,0.06); }
.pres-ai-step-icon { width: 32px; height: 32px; border-radius: 8px; background: rgba(250,204,21,0.12); color: #facc15; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; }
.pres-ai-step h6 { font-size: 0.7rem; }
.pres-ai-step p { font-size: 0.56rem !important; }

.pres-slide-admin {
  background:
    radial-gradient(circle at 12% 18%, rgba(14, 165, 233, 0.14), transparent 35%),
    radial-gradient(circle at 88% 24%, rgba(34, 197, 94, 0.12), transparent 34%),
    linear-gradient(135deg, #0b1120 0%, #172554 50%, #0b1120 100%);
}

.pres-slide-admin .pres-heading {
  color: #ffffff;
}

.pres-admin-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
  gap: 1.25rem;
  align-items: stretch;
}

.pres-admin-left {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.pres-admin-right {
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
}

.pres-admin-image-card {
  flex: 0 0 320px !important;
  width: 320px !important;
  border-radius: 12px !important;
}

.pres-admin-image-card > img {
  width: 320px !important;
  height: 200px !important;
  object-fit: contain !important;
}

.pres-admin-image-card .pres-ui-preview {
  left: auto !important;
  right: 0 !important;
  bottom: calc(100% + 10px) !important;
  width: min(84vw, 980px) !important;
  transform: translateY(8px) scale(0.96) !important;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  border-radius: 16px !important;
  overflow: hidden !important;
}

.pres-admin-image-card:hover .pres-ui-preview {
  transform: translateY(0) scale(1) !important;
}

.pres-admin-image-card .pres-ui-preview img {
  width: 100% !important;
  max-height: 78vh !important;
  object-fit: contain !important;
  background: transparent !important;
  border-radius: 16px !important;
}

.pres-admin-boundary {
  height: 2px;
  width: 100%;
  margin-top: 1rem;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(250, 204, 21, 0.2), rgba(250, 204, 21, 0.7), rgba(250, 204, 21, 0.2));
}

.pres-admin-mini-card {
  min-height: 112px;
  padding: 1rem 0.9rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.15rem;
  text-align: center;
}

.pres-admin-mini-card i {
  color: #facc15;
  font-size: 1.55rem !important;
}

.pres-admin-mini-card h6 {
  font-size: 0.92rem;
  line-height: 1.28;
}

.pres-admin-point {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 14px;
  padding: 0.9rem 1rem;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 58px;
  box-shadow: 0 10px 20px rgba(2, 6, 23, 0.06);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.pres-admin-point:hover {
  transform: translateY(-4px);
  border-color: rgba(14, 165, 233, 0.35);
  box-shadow: 0 16px 28px rgba(2, 6, 23, 0.12);
}

.pres-admin-point-num {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  background: linear-gradient(135deg, #0ea5e9, #2563eb);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.4px;
  margin-right: 0.3rem;
  box-shadow: 0 8px 14px rgba(37, 99, 235, 0.26);
}

.pres-admin-point i {
  color: #16a34a;
  font-size: 1rem;
}

.pres-hint-bar { position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000; display: flex; justify-content: center; gap: 2rem; padding: 0.5rem 1rem; background: rgba(11, 17, 32, 0.85); backdrop-filter: blur(8px); font-size: 0.72rem; color: rgba(255,255,255,0.4); transition: 0.3s; }
.pres-hint-hidden { opacity: 0; transform: translateY(100%); }

@media (max-width: 768px) {
  .pres-heading { font-size: 1.6rem; }
  .pres-title-xl { font-size: 2.8rem; }
  .pres-ui-gallery { flex-direction: column; align-items: center; }
  .pres-ui-preview { display: none !important; }
  .pres-admin-layout { grid-template-columns: 1fr; gap: 1rem; }
  .pres-admin-right { justify-content: center; align-items: center; }
  .pres-admin-image-card { width: min(92vw, 360px) !important; flex-basis: auto !important; }
  .pres-admin-image-card > img { width: 100% !important; height: auto !important; max-height: 220px !important; }
  .pres-admin-mini-card { min-height: 98px; padding: 0.85rem 0.75rem; }
  .pres-admin-mini-card h6 { font-size: 0.86rem; }
  .pres-admin-point { min-height: 52px; padding: 0.78rem 0.86rem; }
  .pres-admin-point-num { width: 26px; height: 26px; font-size: 0.66rem; }
  .pres-mapping-row { flex-direction: column; align-items: flex-start; }
  .pres-map-arrow { transform: rotate(90deg); margin: 0.2rem 0; align-self: center; }
  .pres-hint-bar { gap: 1rem; font-size: 0.6rem; }
}
</style>
