import { createRouter, createWebHashHistory } from 'vue-router'
import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegistrationForm.vue'
import ProfilePage from './components/ProfilePage.vue'
import HomePage from './components/HomePage.vue'
import CartPage from './components/CartPage.vue'
import CategoryPage from './components/CategoryPage.vue'
import ProductPage from './components/ProductPage.vue'
import FavoritesPage from './components/FavoritesPage.vue'
import SearchResults from './components/SearchResults.vue'
import CatalogPage from './components/CatalogPage.vue'
import CheckoutPage from './components/CheckoutPage.vue'

const routes = [
    { path: '/login', component: LoginForm },
    { path: '/register', component: RegisterForm },
    { path: '/profile', name: 'Profile', component: ProfilePage},
    { path: '/home', name: 'home', component: HomePage},
    { path: '/cart', name: 'cart', component: CartPage},
    { path: '/category/:id', name: 'CategoryPage', component: CategoryPage, props: true },
    { path: '/product/:id', name: 'ProductPage', component: ProductPage, props: true },
    { path: '/favorites', name: 'favorites', component: FavoritesPage },
    { path: '/search', name: 'search', component: SearchResults },
    { path: '/catalog', name: 'catalog', component: CatalogPage },
    { path: '/checkout', name: 'checkout', component: CheckoutPage },
    { path: '/order-success/:orderId', name: 'order-success', component: () => import('./components/OrderSuccessPage.vue'), props: true },
    { path: '/', redirect: '/home' },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router
