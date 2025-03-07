import { createRouter, createWebHistory } from 'vue-router'
import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegistrationForm.vue'
import ProfilePage from './components/ProfilePage.vue'
import HomePage from './components/HomePage.vue'
import CartPage from './components/CartPage.vue'
import CategoryPage from './components/CategoryPage.vue'
import ProductPage from './components/ProductPage.vue'

const routes = [
    { path: '/login', component: LoginForm },
    { path: '/register', component: RegisterForm },
    { path: '/profile', name: 'Profile', component: ProfilePage},
    { path: '/home', name: 'home', component: HomePage},
    { path: '/cart', name: 'cart', component: CartPage},
    { path: '/category/:id', name: 'CategoryPage', component: CategoryPage, props: true },
    { path: '/product/:id', name: 'ProductPage', component: ProductPage, props: true },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
