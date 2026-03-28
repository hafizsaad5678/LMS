/**
 * Auth Routes
 * Public authentication and shared routes
 */

const Login = () => import('../../views/shared/auth/Login.vue')
const ForgotPassword = () => import('../../views/shared/auth/ForgotPassword.vue')
const ResetPassword = () => import('../../views/shared/auth/ResetPassword.vue')
const HomeScreen = () => import('../../views/shared/HomeScreen.vue')

export const authRoutes = [
    { path: '/', name: 'Home', component: HomeScreen },
    { path: '/login', name: 'Login', component: Login, meta: { requiresGuest: true } },
    { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword, meta: { requiresGuest: true } },
    { path: '/reset-password/:uidb64/:token', name: 'ResetPassword', component: ResetPassword, meta: { requiresGuest: true } }
]
