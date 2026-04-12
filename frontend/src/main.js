import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Bootstrap CSS & JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/js/dist/collapse'
import 'bootstrap/js/dist/dropdown'

// Custom CSS (consolidated from SCSS - no build step required)
import './assets/css/custom.css'
// Component styles
import './assets/css/components.css'
// Dashboard styles
import './assets/css/dashboard.css'
// Student panel shared styles
import './assets/css/student-panel.css'
// Shared homepage styles
import './assets/css/home-screen.css'

// Ensure reloads always start at the top of the page (avoids browser restoring bottom scroll)
if ('scrollRestoration' in window.history) {
	window.history.scrollRestoration = 'manual'
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
