import Capabilities from '@/components/shared/home/Capabilities.vue'
import Solutions from '@/components/shared/home/Solutions.vue'
import Customers from '@/components/shared/home/Customers.vue'
import Contact from '@/components/shared/home/Contact.vue'
import Features from '@/components/shared/home/Features.vue'
import Pricing from '@/components/shared/home/Pricing.vue'
import Help from '@/components/shared/home/Help.vue'
import About from '@/components/shared/home/About.vue'
import Careers from '@/components/shared/home/Careers.vue'
import GetStarted from '@/components/shared/home/GetStarted.vue'
import Presentation from '@/views/shared/public/Presentation.vue'
import InstitutionLayout from '@/views/public/InstitutionLayout.vue'
import InstitutionHome from '@/views/public/institution/InstitutionHome.vue'

export const publicRoutes = [
    {
        path: '/i/:slug',
        component: InstitutionLayout,
        children: [
            { path: '', name: 'InstitutionPublicProfile', component: InstitutionHome },
            { path: 'programs', name: 'InstitutionPrograms', component: () => import('@/components/public/InstitutionDepartments.vue') },
            { path: 'faculty', name: 'InstitutionFaculty', component: () => import('@/components/public/InstitutionFaculty.vue') },
            { path: 'admissions', name: 'InstitutionAdmissions', component: () => import('@/components/public/InstitutionAdmissions.vue') },
            { path: 'events', name: 'InstitutionEvents', component: () => import('@/components/public/InstitutionEvents.vue') },
            { path: 'gallery', name: 'InstitutionGallery', component: () => import('@/components/public/InstitutionGallery.vue') }
        ]
    },
    { path: '/presentation', name: 'Presentation', component: Presentation },
    { path: '/capabilities', name: 'Capabilities', component: Capabilities },
    { path: '/solutions', name: 'Solutions', component: Solutions },
    { path: '/customers', name: 'Customers', component: Customers },
    { path: '/contact', name: 'Contact Sales', component: Contact },
    { path: '/get-started', name: 'GetStarted', component: GetStarted },
    { path: '/features', name: 'Features', component: Features },
    { path: '/pricing', name: 'Pricing', component: Pricing },
    { path: '/help', name: 'Help Center', component: Help },
    { path: '/about', name: 'About Us', component: About },
    { path: '/careers', name: 'Careers', component: Careers }
]
