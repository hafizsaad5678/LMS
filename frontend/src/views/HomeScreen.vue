<template>
  <div class="home-container">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top border-bottom border-secondary shadow-sm">
      <div class="container">
        <a class="navbar-brand fw-bold fs-4 d-flex align-items-center" href="#">
          <i class="bi bi-mortarboard-fill me-2 text-info"></i><span class="text-info">LMS</span> Portal
        </a>
        <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item"><a class="nav-link active" href="#hero">Home</a></li>
            <li class="nav-item"><a class="nav-link" href="#features">Features</a></li>
            <li class="nav-item"><a class="nav-link" href="#users">For Users</a></li>
            <li class="nav-item"><a class="nav-link" href="#stats">Stats</a></li>
          </ul>
          <div class="d-flex align-items-center">
            <button @click="router.push('/login')" class="btn btn-outline-light btn-sm px-4 rounded-pill fw-semibold me-2">
              <i class="bi bi-box-arrow-in-right me-2"></i>Login
            </button>
            <button @click="router.push('/register')" class="btn btn-info btn-sm px-4 rounded-pill fw-semibold">
              <i class="bi bi-person-plus me-2"></i>Register
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="hero" class="py-5 pt-5" style="background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);">
      <div class="container">
        <div class="row align-items-center g-5 py-5">
          <div class="col-lg-6">
            <div class="ps-md-4">
              <div class="mb-4">
                <span class="badge bg-info text-dark mb-3 px-3 py-2">Welcome to Education Platform</span>
              </div>
              <h1 class="display-3 fw-bold mb-4 text-white">
                Transform Your <br>
                <span class="text-warning">Educational Experience</span>
              </h1>
              <p class="lead text-white mb-5 opacity-85 lh-lg">
                A comprehensive Learning Management System designed to streamline education. Manage students, teachers, courses, and assignments all in one unified platform with ease.
              </p>
              <div class="d-flex flex-wrap gap-3 mb-5">
                <button @click="router.push('/login')" class="btn btn-warning btn-lg px-5 rounded-pill fw-semibold shadow">
                  <i class="bi bi-rocket-fill me-2"></i>Get Started Now
                </button>
                <button @click="scrollTo('features')" class="btn btn-outline-light btn-lg px-5 rounded-pill fw-semibold">
                  <i class="bi bi-arrow-down-circle me-2"></i>Learn More
                </button>
              </div>
              <div class="row g-4">
                <div class="col-md-6">
                  <h6 class="text-light fw-bold">Trusted by</h6>
                  <p class="text-light opacity-75 small">500+ Educational Institutions</p>
                </div>
                <div class="col-md-6">
                  <h6 class="text-light fw-bold">24/7 Support</h6>
                  <p class="text-light opacity-75 small">Expert help always available</p>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-6 text-center pe-md-4">
            <div class="position-relative">
              <img src="@/assets/Lmspic1.png" alt="LMS Dashboard" class="img-fluid rounded-4 shadow-lg" style="max-height: 450px; object-fit: cover;">
              <div class="position-absolute top-0 start-0 mt-3 ms-3">
                <span class="badge bg-success bg-opacity-90 text-white px-3 py-2">Live Demo Available</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Stats Banner -->
    <section class="py-4 bg-dark text-light">
      <div class="container">
        <div class="row g-4 text-center">
          <div class="col-md-3 col-6">
            <div>
              <h5 class="text-info fw-bold">500+</h5>
              <small class="text-muted">Active Students</small>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div>
              <h5 class="text-warning fw-bold">50+</h5>
              <small class="text-muted">Expert Teachers</small>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div>
              <h5 class="text-success fw-bold">100+</h5>
              <small class="text-muted">Courses</small>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div>
              <h5 class="text-purple fw-bold">24/7</h5>
              <small class="text-muted">Support</small>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-5">
      <div class="container">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-5 fw-bold mb-3">Powerful Features</h2>
            <p class="lead text-muted mb-0">Everything you need to manage education effectively and efficiently</p>
          </div>
        </div>
        <div class="row g-4">
          <!-- Feature 1 -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm feature-card">
              <template #default>
                <div class="text-center p-4">
                  <div class="d-flex align-items-center justify-content-center mx-auto mb-4 rounded-3 feature-icon" style="width: 80px; height: 80px; background: rgba(13, 110, 253, 0.15);">
                    <i class="bi bi-people-fill text-primary fs-2"></i>
                  </div>
                  <h5 class="fw-bold mb-3">Student Management</h5>
                  <p class="text-muted small mb-0 lh-lg">
                    Comprehensive student enrollment, tracking, and performance monitoring system
                  </p>
                </div>
              </template>
            </BaseCard>
          </div>
          <!-- Feature 2 -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm feature-card">
              <template #default>
                <div class="text-center p-4">
                  <div class="d-flex align-items-center justify-content-center mx-auto mb-4 rounded-3 feature-icon" style="width: 80px; height: 80px; background: rgba(25, 135, 84, 0.15);">
                    <i class="bi bi-book-fill text-success fs-2"></i>
                  </div>
                  <h5 class="fw-bold mb-3">Course Management</h5>
                  <p class="text-muted small mb-0 lh-lg">
                    Create, organize, and manage courses with materials, assignments, and assessments
                  </p>
                </div>
              </template>
            </BaseCard>
          </div>
          <!-- Feature 3 -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm feature-card">
              <template #default>
                <div class="text-center p-4">
                  <div class="d-flex align-items-center justify-content-center mx-auto mb-4 rounded-3 feature-icon" style="width: 80px; height: 80px; background: rgba(255, 193, 7, 0.15);">
                    <i class="bi bi-graph-up text-warning fs-2"></i>
                  </div>
                  <h5 class="fw-bold mb-3">Analytics & Reports</h5>
                  <p class="text-muted small mb-0 lh-lg">
                    Track progress with detailed analytics, reports, and performance insights
                  </p>
                </div>
              </template>
            </BaseCard>
          </div>
          <!-- Feature 4 -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm feature-card">
              <template #default>
                <div class="text-center p-4">
                  <div class="d-flex align-items-center justify-content-center mx-auto mb-4 rounded-3 feature-icon" style="width: 80px; height: 80px; background: rgba(23, 162, 184, 0.15);">
                    <i class="bi bi-chat-dots-fill text-info fs-2"></i>
                  </div>
                  <h5 class="fw-bold mb-3">Communication Hub</h5>
                  <p class="text-muted small mb-0 lh-lg">
                    Built-in messaging, announcements, and collaboration tools for students and teachers
                  </p>
                </div>
              </template>
            </BaseCard>
          </div>
          <!-- Feature 5 -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm feature-card">
              <template #default>
                <div class="text-center p-4">
                  <div class="d-flex align-items-center justify-content-center mx-auto mb-4 rounded-3 feature-icon" style="width: 80px; height: 80px; background: rgba(220, 53, 69, 0.15);">
                    <i class="bi bi-shield-check text-danger fs-2"></i>
                  </div>
                  <h5 class="fw-bold mb-3">Secure & Reliable</h5>
                  <p class="text-muted small mb-0 lh-lg">
                    Enterprise-grade security with role-based access control and data protection
                  </p>
                </div>
              </template>
            </BaseCard>
          </div>
          <!-- Feature 6 -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm feature-card">
              <template #default>
                <div class="text-center p-4">
                  <div class="d-flex align-items-center justify-content-center mx-auto mb-4 rounded-3 feature-icon" style="width: 80px; height: 80px; background: rgba(111, 66, 193, 0.15);">
                    <i class="bi bi-cloud-fill text-purple fs-2"></i>
                  </div>
                  <h5 class="fw-bold mb-3">Cloud-Based</h5>
                  <p class="text-muted small mb-0 lh-lg">
                    Access anywhere, anytime from any device with automatic backups and updates
                  </p>
                </div>
              </template>
            </BaseCard>
          </div>
        </div>
      </div>
    </section>

    <!-- User Roles Section -->
    <section id="users" class="py-5 bg-light">
      <div class="container">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-5 fw-bold mb-3">Built for Everyone</h2>
            <p class="lead text-muted mb-0">Tailored experiences designed for different user types</p>
          </div>
        </div>
        <div class="row g-4">
          <!-- Students -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm user-card">
              <template #default>
                <div class="text-center p-4">
                  <img src="@/assets/Lmspic2.png" alt="Students" class="img-fluid mb-4 rounded-3" style="height: 200px; width: 100%; object-fit: cover;">
                  <div class="mb-3">
                    <span class="badge bg-success">For Students</span>
                  </div>
                  <h4 class="fw-bold mb-3">Student Portal</h4>
                  <ul class="list-unstyled text-start">
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i><span class="small">Track assignments & grades</span></li>
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i><span class="small">Submit work online</span></li>
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i><span class="small">Interact with teachers</span></li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i><span class="small">Access course materials</span></li>
                  </ul>
                </div>
              </template>
            </BaseCard>
          </div>
          <!-- Teachers -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm user-card">
              <template #default>
                <div class="text-center p-4">
                  <img src="@/assets/Lmspic1.png" alt="Teachers" class="img-fluid mb-4 rounded-3" style="height: 200px; width: 100%; object-fit: cover;">
                  <div class="mb-3">
                    <span class="badge bg-info text-dark">For Teachers</span>
                  </div>
                  <h4 class="fw-bold mb-3">Teacher Portal</h4>
                  <ul class="list-unstyled text-start">
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-info me-2"></i><span class="small">Create & manage courses</span></li>
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-info me-2"></i><span class="small">Grade assignments</span></li>
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-info me-2"></i><span class="small">Communicate with class</span></li>
                    <li><i class="bi bi-check-circle-fill text-info me-2"></i><span class="small">Track student progress</span></li>
                  </ul>
                </div>
              </template>
            </BaseCard>
          </div>
          <!-- Admins -->
          <div class="col-lg-4 col-md-6">
            <BaseCard class="h-100 border-0 shadow-sm user-card">
              <template #default>
                <div class="text-center p-4">
                  <img src="@/assets/Lmspic3.png" alt="Administrators" class="img-fluid mb-4 rounded-3" style="height: 200px; width: 100%; object-fit: cover;">
                  <div class="mb-3">
                    <span class="badge bg-warning text-dark">For Admins</span>
                  </div>
                  <h4 class="fw-bold mb-3">Admin Dashboard</h4>
                  <ul class="list-unstyled text-start">
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-warning me-2"></i><span class="small">Manage users & roles</span></li>
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-warning me-2"></i><span class="small">Oversee all courses</span></li>
                    <li class="mb-2"><i class="bi bi-check-circle-fill text-warning me-2"></i><span class="small">View analytics & reports</span></li>
                    <li><i class="bi bi-check-circle-fill text-warning me-2"></i><span class="small">System configuration</span></li>
                  </ul>
                </div>
              </template>
            </BaseCard>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="py-5 bg-white">
      <div class="container">
        <div class="row mb-5 text-center">
          <div class="col-lg-8 mx-auto">
            <h2 class="display-5 fw-bold mb-3">What Our Users Say</h2>
            <p class="lead text-muted mb-0">Hear from educators and students using our platform</p>
          </div>
        </div>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4">
                <div class="d-flex align-items-center mb-3">
                  <div class="flex-shrink-0">
                    <div class="rounded-circle bg-primary d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                      <span class="text-white fw-bold">JS</span>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="mb-0 fw-bold">John Smith</h6>
                    <small class="text-muted">Mathematics Teacher</small>
                  </div>
                </div>
                <p class="card-text text-muted">"This LMS has transformed how I manage my classes. Grading assignments is now a breeze, and my students love the intuitive interface."</p>
                <div class="text-warning">
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4">
                <div class="d-flex align-items-center mb-3">
                  <div class="flex-shrink-0">
                    <div class="rounded-circle bg-success d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                      <span class="text-white fw-bold">EJ</span>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="mb-0 fw-bold">Emily Johnson</h6>
                    <small class="text-muted">College Student</small>
                  </div>
                </div>
                <p class="card-text text-muted">"As a student, I appreciate how easy it is to track my assignments and grades. The mobile access means I can study anywhere, anytime."</p>
                <div class="text-warning">
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-half"></i>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4">
                <div class="d-flex align-items-center mb-3">
                  <div class="flex-shrink-0">
                    <div class="rounded-circle bg-info d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                      <span class="text-white fw-bold">RD</span>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="mb-0 fw-bold">Robert Davis</h6>
                    <small class="text-muted">School Administrator</small>
                  </div>
                </div>
                <p class="card-text text-muted">"The analytics and reporting features have given us unprecedented insight into student performance. Our institution's efficiency has improved dramatically."</p>
                <div class="text-warning">
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                  <i class="bi bi-star-fill"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section id="about" class="py-5" style="background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);">
      <div class="container">
        <div class="row align-items-center g-4">
          <div class="col-lg-8">
            <h3 class="display-5 fw-bold mb-3 text-white">Ready to Transform Your Institution?</h3>
            <p class="lead text-white mb-0 opacity-85">
              Join hundreds of educational institutions already using our LMS. Sign in to your account or create a new one to get started today.
            </p>
          </div>
          <div class="col-lg-4 text-lg-end">
            <div class="d-flex flex-column flex-md-row gap-3 justify-content-lg-end">
              <button @click="router.push('/login')" class="btn btn-light btn-lg px-4 rounded-pill fw-semibold shadow">
                <i class="bi bi-box-arrow-in-right me-2"></i>Login Now
              </button>
              <button @click="router.push('/register')" class="btn btn-outline-light btn-lg px-4 rounded-pill fw-semibold">
                <i class="bi bi-person-plus me-2"></i>Register
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section id="stats" class="py-5 bg-light">
      <div class="container">
        <div class="row g-4">
          <div class="col-md-3 col-6">
            <div class="text-center">
              <h3 class="display-6 fw-bold text-primary mb-2">500+</h3>
              <p class="text-muted">Active Students</p>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-center">
              <h3 class="display-6 fw-bold text-success mb-2">50+</h3>
              <p class="text-muted">Expert Teachers</p>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-center">
              <h3 class="display-6 fw-bold text-warning mb-2">100+</h3>
              <p class="text-muted">Courses Available</p>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-center">
              <h3 class="display-6 fw-bold text-info mb-2">99.9%</h3>
              <p class="text-muted">Uptime Guarantee</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Footer -->
    <footer class="bg-dark text-light py-5">
      <div class="container">
        <div class="row g-4 mb-4">
          <div class="col-lg-3">
            <h6 class="fw-bold mb-3">
              <i class="bi bi-mortarboard-fill me-2"></i>LMS Portal
            </h6>
            <p class="text-muted small">
              Empowering education through technology with a comprehensive learning management solution.
            </p>
            <div class="d-flex gap-3 mt-3">
              <a href="#" class="text-muted"><i class="bi bi-facebook fs-5"></i></a>
              <a href="#" class="text-muted"><i class="bi bi-twitter fs-5"></i></a>
              <a href="#" class="text-muted"><i class="bi bi-linkedin fs-5"></i></a>
              <a href="#" class="text-muted"><i class="bi bi-instagram fs-5"></i></a>
            </div>
          </div>
          <div class="col-lg-3">
            <h6 class="fw-bold mb-3">Quick Links</h6>
            <ul class="list-unstyled small">
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">About Us</a></li>
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">Features</a></li>
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">Contact</a></li>
              <li><a href="#" class="text-muted text-decoration-none">Blog</a></li>
            </ul>
          </div>
          <div class="col-lg-3">
            <h6 class="fw-bold mb-3">Support</h6>
            <ul class="list-unstyled small">
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">Help Center</a></li>
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">Documentation</a></li>
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">FAQ</a></li>
              <li><a href="#" class="text-muted text-decoration-none">Community</a></li>
            </ul>
          </div>
          <div class="col-lg-3">
            <h6 class="fw-bold mb-3">Legal</h6>
            <ul class="list-unstyled small">
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">Privacy Policy</a></li>
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">Terms of Service</a></li>
              <li class="mb-2"><a href="#" class="text-muted text-decoration-none">Cookie Policy</a></li>
              <li><a href="#" class="text-muted text-decoration-none">GDPR Compliance</a></li>
            </ul>
          </div>
        </div>
        <hr class="border-secondary">
        <div class="row align-items-center">
          <div class="col-md-6 text-center text-md-start">
            <small class="text-muted">&copy; 2024 LMS Portal. All rights reserved.</small>
          </div>
          <div class="col-md-6 text-center text-md-end">
            <small class="text-muted">
              <a href="#" class="text-muted text-decoration-none me-3">Privacy</a>
              <a href="#" class="text-muted text-decoration-none me-3">Terms</a>
              <a href="#" class="text-muted text-decoration-none">Sitemap</a>
            </small>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'

const router = useRouter()

const scrollTo = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

