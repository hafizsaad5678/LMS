<template>
  <section id="contact" class="py-5 bg-light border-top">
    <div class="container">
      <div class="row mb-5 text-center">
        <div class="col-lg-8 mx-auto">
          <h2 class="display-6 fw-bold mb-3">Enterprise Sales & Support</h2>
          <p class="text-muted mb-0">Partner with our platform team to map out your infrastructure needs, or send us real-time feedback</p>
        </div>
      </div>
      <div class="row g-5">
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm rounded-4 h-100">
            <div class="card-body p-5">
              <h4 class="fw-bold mb-4">Request a Consultation</h4>
              <form @submit.prevent="submitContact">
                <div class="mb-3">
                  <label class="form-label fw-medium">Work Email</label>
                  <input type="email" class="form-control border-secondary-subtle px-3 py-2" v-model="contact.email" required placeholder="name@company.com">
                </div>
                <div class="mb-3">
                  <label class="form-label fw-medium">Company Name</label>
                  <input type="text" class="form-control border-secondary-subtle px-3 py-2" v-model="contact.company" required placeholder="SaaS Inc.">
                </div>
                <div class="mb-4">
                  <label class="form-label fw-medium">How can we help?</label>
                  <textarea class="form-control border-secondary-subtle px-3 py-2" rows="4" v-model="contact.message" required placeholder="Tell us about your scale and use-case..."></textarea>
                </div>
                <button type="submit" class="btn btn-warning w-100 fw-bold py-2 rounded-pill shadow-sm" :disabled="isSubmittingContact">
                  <span v-if="isSubmittingContact" class="spinner-border spinner-border-sm me-2"></span>
                  {{ contactSuccess ? 'Message Sent!' : 'Talk to Sales' }}
                </button>
              </form>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm rounded-4 h-100 bg-primary text-white bg-gradient">
            <div class="card-body p-5 d-flex flex-column justify-content-center">
              <div class="mb-5 text-center">
                <i class="bi bi-rocket-takeoff-fill display-3 text-warning mb-3"></i>
                <h3 class="fw-bold">Platform Feedback</h3>
                <p class="opacity-75">Send real-time feature requests straight to our engineering team.</p>
              </div>
              <form @submit.prevent="submitFeedback">
                <div class="mb-3 position-relative">
                  <input type="text" class="form-control form-control-lg pe-5 rounded-pill border-0 shadow-sm" v-model="feedbackText" required placeholder="I'd love to see a feature for...">
                  <button type="submit" class="btn btn-primary position-absolute top-50 end-0 translate-middle-y rounded-circle me-1" style="height: 38px; width: 38px; padding: 0;" :disabled="isSubmittingFeedback">
                    <i class="bi bi-send-fill" v-if="!isSubmittingFeedback"></i>
                    <span v-else class="spinner-grow spinner-grow-sm"></span>
                  </button>
                </div>
                <div v-if="feedbackSuccess" class="text-center text-success-emphasis bg-white rounded-pill py-1 px-3 mt-3 shadow-sm d-inline-block mx-auto fw-bold" style="font-size: 0.85rem">
                  <i class="bi bi-check-circle-fill me-1"></i>Feedback delivered!
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { API_BASE_URL } from '@/utils/constants/config'

const buildApiUrl = (path) => {
  const cleanBase = String(API_BASE_URL || '').replace(/\/$/, '')
  const cleanPath = String(path || '').replace(/^\//, '')
  return `${cleanBase}/${cleanPath}`
}

const contact = ref({ email: '', company: '', message: '' })
const isSubmittingContact = ref(false)
const contactSuccess = ref(false)

const feedbackText = ref('')
const isSubmittingFeedback = ref(false)
const feedbackSuccess = ref(false)

const submitContact = async () => {
  if (!contact.value.email || !contact.value.message) return
  isSubmittingContact.value = true
  try {
    const res = await fetch(buildApiUrl('/public/contact/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contact.value)
    })
    if (res.ok) {
      contactSuccess.value = true
      setTimeout(() => { 
        contactSuccess.value = false; 
        contact.value = { email: '', company: '', message: '' } 
      }, 3000)
    }
  } catch (e) {
    console.error('Contact error', e)
  } finally {
    isSubmittingContact.value = false
  }
}

const submitFeedback = async () => {
  if (!feedbackText.value.trim()) return
  isSubmittingFeedback.value = true
  try {
    const res = await fetch(buildApiUrl('/public/feedback/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback: feedbackText.value })
    })
    if (res.ok) {
      feedbackSuccess.value = true
      feedbackText.value = ''
      setTimeout(() => { feedbackSuccess.value = false }, 3000)
    }
  } catch (e) {
    console.error('Feedback error', e)
  } finally {
    isSubmittingFeedback.value = false
  }
}
</script>