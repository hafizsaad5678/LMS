<template>
  <div class="roles-testimonials-wrapper">
    <section id="users" class="py-5 bg-light-subtle">
      <div class="container">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-5 fw-bold mb-3">Multi-Tenant Solutions</h2>
            <p class="lead text-muted mb-0">Separate, customized portals for admins, teachers, and learners securely within your SaaS environment.</p>
          </div>
        </div>
        <div class="row g-4 justify-content-center">
          <div v-for="role in roleCards" :key="role.title" class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm home-role-card">
              <template #default>
                <div class="text-center p-4">
                  <div class="ratio ratio-16x9 mb-4 rounded-3 overflow-hidden">
                    <img :src="role.image" :alt="role.alt" class="w-100 h-100 object-fit-cover shadow-sm bg-light">
                  </div>
                  <div class="mb-3">
                    <span :class="['badge', role.badgeClass]">{{ role.badge }}</span>
                  </div>
                  <h4 class="fw-bold mb-3">{{ role.title }}</h4>
                  <ul class="list-unstyled text-start mb-0">
                    <li v-for="point in role.points" :key="point" class="mb-2">
                      <i :class="[role.pointIcon, role.pointColor, 'me-2 home-role-check']"></i>
                      <span class="small">{{ point }}</span>
                    </li>
                  </ul>
                </div>
              </template>
            </BaseCard>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5 bg-white">
      <div class="container">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-5 fw-bold mb-3">Trusted Worldwide</h2>
            <p class="lead text-muted mb-0">What other SaaS enterprises say about their scale.</p>
          </div>
        </div>
        <div class="row g-4">
          <div v-for="item in testimonials" :key="item.name" class="col-md-4">
            <div class="card border-0 shadow-sm h-100 home-testimonial-card position-relative overflow-hidden">
              <div v-if="item.bgImage" class="position-absolute w-100 h-100 opacity-25" :style="`background-image: url(${item.bgImage}); background-size: cover; background-position: center; border-radius: 8px; z-index: 0;`"></div>
              <div class="card-body p-4 position-relative" style="z-index: 1;">
                <div class="d-flex align-items-center mb-3">
                  <div class="flex-shrink-0">
                    <div :class="['rounded-circle d-flex align-items-center justify-content-center', item.avatarClass]" style="width: 50px; height: 50px;">
                      <span class="text-white fw-bold">{{ item.initials }}</span>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="mb-0 fw-bold">{{ item.name }}</h6>
                    <small class="text-dark bg-light px-2 py-1 rounded small">{{ item.role }}</small>
                  </div>
                </div>
                <p class="card-text text-dark fw-medium mb-3 bg-light bg-opacity-75 p-2 rounded">"{{ item.quote }}"</p>
                <div class="text-warning bg-dark d-inline-block px-2 py-1 rounded">
                  <i v-for="star in item.stars" :key="star" class="bi bi-star-fill"></i>
                  <i v-if="item.halfStar" class="bi bi-star-half"></i>
                </div>
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
    badgeClass: 'bg-info text-dark',
    title: 'Instructor Suite',
    pointIcon: 'bi bi-check-circle-fill',
    pointColor: 'text-info',
    points: ['Course material distribution', 'Fast grading automation', 'AI-assisted lesson planning', 'Group progression tracking'],
  },
  {
    image: adminImage,
    alt: 'Control Center',
    badge: 'For Enterprise',
    badgeClass: 'bg-warning text-dark',
    title: 'Control Center',
    pointIcon: 'bi bi-check-circle-fill',
    pointColor: 'text-warning',
    points: ['Manage organizational billing', 'White-labeled user tiers', 'High-level ROI dashboards', 'Set compliance constraints'],
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
    avatarClass: 'bg-info',
    name: 'HS Ansari',
    role: 'EdTech VP',
    quote: 'The level of insights through the real-time Control Center is exactly what out team needed.',
    stars: 5,
    halfStar: false,
  },
]
</script>