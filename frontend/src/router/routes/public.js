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

export const publicRoutes = [
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
