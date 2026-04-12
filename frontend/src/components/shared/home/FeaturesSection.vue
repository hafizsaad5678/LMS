<template>
  <div class="features-wrapper">
    <section id="features" class="py-5">
      <div class="container">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-5 fw-bold mb-3">Core SaaS Capabilities</h2>
            <p class="lead text-muted mb-0">Structured to help enterprises reduce manual work and scale learning operations effortlessly</p>
          </div>
        </div>
        <div class="row g-4">
          <div v-for="feature in features" :key="feature.title" class="col-lg-3 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm home-feature-card">
              <template #default>
                <div class="text-center p-4">
                  <div :class="['d-inline-flex align-items-center justify-content-center mx-auto mb-4 rounded-3 p-3', feature.iconBgClass]">
                    <i :class="[feature.icon, feature.iconClass, 'fs-2']"></i>
                  </div>
                  <h5 class="fw-bold mb-3">{{ feature.title }}</h5>
                  <p class="text-muted small mb-0 lh-lg">{{ feature.description }}</p>
                </div>
              </template>
            </BaseCard>
          </div>
        </div>
      </div>
    </section>

    <section id="workflow" class="py-5 bg-body-tertiary border-top border-bottom">
      <div class="container">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-6 fw-bold mb-3">How It Works</h2>
            <p class="text-muted mb-0">A simple flow your organization can adopt quickly without changing operations</p>
          </div>
        </div>
        <div class="row g-4">
          <div v-for="step in workflowSteps" :key="step.step" class="col-md-4">
            <div class="h-100 p-4 rounded-4 border bg-white home-step-card">
              <span class="badge text-bg-dark rounded-pill mb-3 px-3 py-2">Step {{ step.step }}</span>
              <h5 class="fw-bold mb-2">{{ step.title }}</h5>
              <p class="text-muted mb-0">{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { BaseCard } from '@/components/shared/common'

const features = [
  {
    title: 'Enterprise Management',
    description: 'Handle enrollment, multi-tenant billing, and user lifecycles seamlessly natively inside a SaaS wrapper.',
    icon: 'bi bi-people-fill',
    iconClass: 'text-primary',
    iconBgClass: 'bg-primary bg-opacity-10',
  },
  {
    title: 'Course Operations',
    description: 'Create scalable modules, assign materials interactively and reuse course blueprints.',
    icon: 'bi bi-journal-bookmark-fill',
    iconClass: 'text-success',
    iconBgClass: 'bg-success bg-opacity-10',
  },
  {
    title: 'Assessment Engine',
    description: 'Scale grading using our powerful assessment automation to set deadlines & dynamic reporting limits.',
    icon: 'bi bi-clipboard2-check-fill',
    iconClass: 'text-warning',
    iconBgClass: 'bg-warning bg-opacity-25',
  },
  {
    title: 'Communication Hub',
    description: 'Keep teachers, organizations, and end users aligned instantly through real-time notifications.',
    icon: 'bi bi-chat-dots-fill',
    iconClass: 'text-info',
    iconBgClass: 'bg-info bg-opacity-25',
  },
]

const workflowSteps = [
  {
    step: 1,
    title: 'Onboard Your Organization',
    description: 'Set up departments, custom branding, user tiers, and operational permissions instantly.',
  },
  {
    step: 2,
    title: 'Launch Learning Pipelines',
    description: 'Automate attendance, lessons rollouts, assignments generation, and internal communications.',
  },
  {
    step: 3,
    title: 'Analyze Business Outcomes',
    description: 'Use our advanced analytics suite specifically identifying overall B2B and ROI growth metrics.',
  },
]
</script>