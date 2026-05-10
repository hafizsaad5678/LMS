/**
 * Auth Routes
 * Public authentication and shared routes
 */

const Login = () => import('../../views/shared/auth/Login.vue')
const ForgotPassword = () => import('../../views/shared/auth/ForgotPassword.vue')
const ResetPassword = () => import('../../views/shared/auth/ResetPassword.vue')
// const HomeScreen = () => import('../../views/shared/HomeScreen.vue') // DISABLED: Single-college mode

export const authRoutes = [
    // SINGLE-COLLEGE MODE: Redirect root to institution profile
    // To re-enable multi-institution: uncomment HomeScreen import above and restore: { path: '/', name: 'Home', component: HomeScreen },
    { path: '/', redirect: '/i/ggca' },
    { path: '/login', name: 'Login', component: Login, meta: { requiresGuest: true } },
    { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword, meta: { requiresGuest: true } },
    { path: '/reset-password/:uidb64/:token', name: 'ResetPassword', component: ResetPassword, meta: { requiresGuest: true } }
]
