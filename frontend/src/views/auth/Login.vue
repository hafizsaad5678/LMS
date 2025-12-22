<template>
  <div class="min-vh-100 bg-gradient-light d-flex align-items-center justify-content-center p-3">
    <div class="w-100" style="max-width: 1200px;">
      <div class="card shadow-lg border-0 overflow-hidden">
        <div class="row g-0">
          <!-- Left Side - Form -->
          <div class="col-lg-6 p-5 p-lg-5">
            <div class="text-center text-lg-start mb-5">
              <h1 class="h3 fw-bold text-dark mb-2">College LMS</h1>
              <p class="text-muted">Learning Management System</p>
            </div>

            <!-- Login Form Component -->
            <LoginForm 
              @login-success="handleLoginSuccess"
              @login-error="handleLoginError"
            />
          </div>

          <!-- Right Side - Illustration -->
          <div class="col-lg-6 bg-gradient-primary text-white d-none d-lg-flex align-items-center justify-content-center p-5">
            <div class="text-center">
              <div class="display-1 mb-4">
                <i class="bi bi-mortarboard"></i>
              </div>
              <h2 class="h3 fw-bold mb-4">Welcome Back!</h2>
              <p class="lead">
                Continue your learning journey with our comprehensive Learning Management System. 
                Access your courses, assignments, and resources all in one place.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LoginForm from '@/components/auth/LoginForm.vue'

export default {
  name: 'Login',
  components: {
    LoginForm
  },
  methods: {
    handleLoginSuccess(data) {
      // Get role from backend response - this is the ACTUAL role from database
      const userRole = data.role
      
      console.log('Login successful - User role:', userRole)
      
      // Store tokens and user info
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('user_role', userRole)
      localStorage.setItem('username', data.username)
      
      // Redirect based on actual database role
      switch (userRole) {
        case 'student':
          this.$router.push('/student-dashboard')
          break
        case 'teacher':
        case 'instructor':
          this.$router.push('/teacher-dashboard')
          break
        case 'admin':
          this.$router.push('/admin-dashboard')
          break
        default:
          console.warn('Unknown role:', userRole)
          // For unknown roles, show error but still allow access to a default dashboard
          alert('Your account does not have a specific role assigned. Please contact administrator.')
          // Redirect to admin dashboard if user is staff/superuser, otherwise show error
          if (data.is_staff || data.is_superuser) {
            this.$router.push('/admin-dashboard')
          }
      }
    },
    handleLoginError(error) {
      console.error('Login error:', error)
    }
  }
}
</script>
