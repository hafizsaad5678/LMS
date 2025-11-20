<template>
  <router-view />
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Global Styling */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
}

/* Custom Gradient Backgrounds */
.bg-gradient-light {
  background: linear-gradient(135deg, #f0f5ff 0%, #f5f0ff 100%);
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #0d6efd 0%, #6610f2 100%);
}

.bg-gradient-success {
  background: linear-gradient(135deg, #198754 0%, #20c997 100%);
}

.bg-gradient-warning {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
}

/* Navbar Fixed Positioning */
.navbar.fixed-top {
  z-index: 1030;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
}

/* Add padding to body to account for fixed navbar */
body {
  padding-top: 56px;
}

/* Admin Navbar - Orange/Red */
.bg-danger {
  background-color: #dc3545 !important;
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%) !important;
}

/* Teacher Navbar - Blue (Primary) */
.bg-primary {
  background-color: #0d6efd !important;
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%) !important;
}

/* Student Navbar - Green (Success) */
.bg-success {
  background-color: #198754 !important;
  background: linear-gradient(135deg, #198754 0%, #157347 100%) !important;
}
</style>