<template>
  <div class="roles-testimonials-wrapper">
    <section id="users" class="py-5 bg-white border-top border-bottom border-light-subtle">
      <div class="container py-4">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-5 fw-bold mb-3 text-dark">Multi-Tenant Solutions</h2>
            <p class="lead text-secondary mb-0">Separate, customized portals for admins, teachers, and learners securely within your SaaS environment.</p>
          </div>
        </div>
        <div class="row g-4 justify-content-center">
          <div v-for="role in roleCards" :key="role.title" class="col-lg-4 col-md-6">
            <div class="card h-100 border-0 shadow-sm bg-light home-card-compact transition-all">
              <div class="p-4 text-center">
                <div class="ratio ratio-16x9 mb-4 rounded-3 overflow-hidden shadow-sm bg-white border">
                  <img :src="role.image" :alt="role.alt" class="w-100 h-100 object-fit-cover">
                </div>
                <div class="mb-3">
                  <span :class="['badge rounded-pill px-3 py-2', role.badgeClass]" style="font-size: 0.75rem;">{{ role.badge }}</span>
                </div>
                <h4 class="fw-bold mb-3 text-dark">{{ role.title }}</h4>
                <ul class="list-unstyled text-start mb-0 ps-2">
                  <li v-for="point in role.points" :key="point" class="mb-2 d-flex align-items-start">
                    <i :class="[role.pointIcon, role.pointColor, 'me-2 mt-1']"></i>
                    <span class="small text-secondary fw-medium">{{ point }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5 bg-light">
      <div class="container py-4">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="fw-bold mb-2 text-dark">Trusted Worldwide</h2>
            <p class="text-secondary small mb-0">What other SaaS enterprises say about their scale.</p>
          </div>
        </div>
        <div class="row g-4 justify-content-center">
          <div v-for="item in testimonials" :key="item.name" class="col-md-4">
            <div class="card border-0 shadow-sm h-100 position-relative overflow-hidden home-card-compact transition-all" 
                 style="min-height: 200px;">
              
              <!-- Background Image -->
              <div class="position-absolute top-0 start-0 w-100 h-100" 
                   :style="{ 
                     backgroundImage: `url(${commentBg})`, 
                     backgroundSize: 'cover', 
                     backgroundPosition: 'center',
                     opacity: '0.15'
                   }">
              </div>

              <div class="card-body p-3 pt-4 position-relative z-1">
                <div class="d-flex align-items-center mb-2">
                  <div class="flex-shrink-0">
                    <div :class="['rounded-circle d-flex align-items-center justify-content-center border shadow-sm', item.avatarClass]" style="width: 36px; height: 36px;">
                      <span class="text-white fw-bold" style="font-size: 0.7rem;">{{ item.initials }}</span>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-2">
                    <h6 class="mb-0 fw-bold text-dark" style="font-size: 0.8rem;">{{ item.name }}</h6>
                    <small class="text-primary fw-semibold" style="font-size: 0.65rem;">{{ item.role }}</small>
                  </div>
                </div>
                <div class="mb-2">
                  <i v-for="star in item.stars" :key="star" class="bi bi-star-fill text-warning me-1" style="font-size: 0.6rem;"></i>
                  <i v-if="item.halfStar" class="bi bi-star-half text-warning me-1" style="font-size: 0.6rem;"></i>
                </div>
                <p class="card-text text-secondary lh-sm home-italic mb-0" style="font-size: 0.8rem; letter-spacing: 0.2px;">"{{ item.quote }}"</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { BaseCard } from '@/components/shared/common'
import adminImage from '@/assets/admindashboard.png'
import teacherImage from '@/assets/teacherdashboard.png'
import studentImage from '@/assets/studentdashboard.png'
import motivationQuote from '@/assets/motivation q.png'
import motivationQuote2 from '@/assets/motivation 1oute.png'
import motivationQuote3 from '@/assets/q.png'
import commentBg from '@/assets/comment bg.png'

const roleCards = [
  {
    image: studentImage,
    alt: 'Learner App Interface',
    badge: 'For End-Users',
    badgeClass: 'bg-success',
    title: 'Learner Portal',
    pointIcon: 'bi bi-check-circle-fill',
    pointColor: 'text-success',
    points: ['Track personal assignments metrics', 'Mobile-first interactions', 'Real-time teacher messaging', 'Secure curriculum access'],
  },
  {
    image: teacherImage,
    alt: 'Instructor Suite',
    badge: 'For Mentors',
    badgeClass: 'bg-warning text-dark',
    title: 'Instructor Suite',
    pointIcon: 'bi bi-check-circle-fill',
    pointColor: 'text-primary',
    points: ['Course material distribution', 'Fast grading automation', 'AI-assisted lesson planning', 'Group progression tracking'],
  },
  {
    image: adminImage,
    alt: 'Control Center',
    badge: 'For Enterprise',
    badgeClass: 'bg-warning text-dark',
    title: 'Control Center',
    pointIcon: 'bi bi-check-circle-fill',
    pointColor: 'text-primary',
    points: ['Tenant lifecycle management', 'Customizable white-labeling', 'Role-based access control', 'Usage analytics & billing'],
  },
]

const testimonials = [
  {
    bgImage: motivationQuote,
    initials: 'ML',
    avatarClass: 'bg-primary',
    name: 'Vicky Kamran',
    role: 'Operations Director',
    quote: 'Deploying this solution cut our SaaS enterprise onboarding pipeline in half.',
    stars: 5,
    halfStar: false,
  },
  {
    bgImage: motivationQuote2,
    initials: 'EJ',
    avatarClass: 'bg-success',
    name: 'Sefraz Chugtai',
    role: 'Corporate Trainer',
    quote: 'Moving from a traditional LMS to this multi-tier ecosystem made our global rollouts 3x faster.',
    stars: 4,
    halfStar: true,
  },
  {
    bgImage: motivationQuote3,
    initials: 'RD',
    avatarClass: 'bg-warning text-dark',
    name: 'HS Ansari',
    role: 'EdTech VP',
    quote: 'The level of insights through the real-time Control Center is exactly what out team needed.',
    stars: 5,
    halfStar: false,
  },
]
</script>