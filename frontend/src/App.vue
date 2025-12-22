<template>
  <router-view />
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Global Styling - Minimal (most styles moved to custom.css) */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  padding-top: 56px;
}

/* Navbar Fixed Positioning */
.navbar.fixed-top {
  z-index: 1030;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>