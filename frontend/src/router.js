import { createRouter, createWebHistory } from 'vue-router'
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
import OrderSuccessPage from './components/OrderSuccessPage.vue'
import AdminPanel from './components/admin/AdminPanel.vue'
import AdminUserManagement from './components/admin/AdminUserManagement.vue'
import AdminUserDetails from './components/admin/AdminUserDetails.vue'
import AdminCreateCategory from './components/admin/AdminCreateCategory.vue'
import AdminCreateProduct from './components/admin/AdminCreateProduct.vue'
import AdminOrderManagement from './components/admin/AdminOrderManagement.vue'

const routes = [
    { path: '/login', component: LoginForm },
    { path: '/register', component: RegisterForm },
    { path: '/profile', name: 'Profile', component: ProfilePage, meta: { requiresAuth: true } },
    { path: '/home', name: 'home', component: HomePage },
    { path: '/cart', name: 'cart', component: CartPage },
    { path: '/category/:id', name: 'CategoryPage', component: CategoryPage, props: true },
    { path: '/product/:id', name: 'ProductPage', component: ProductPage, props: true },
    { path: '/favorites', name: 'favorites', component: FavoritesPage, meta: { requiresAuth: true } },
    { path: '/search', name: 'search', component: SearchResults },
    { path: '/catalog', name: 'catalog', component: CatalogPage },
    { path: '/checkout', name: 'checkout', component: CheckoutPage, meta: { requiresAuth: true } },
    { path: '/order-success/:orderId', name: 'order-success', component: OrderSuccessPage, props: true, meta: { requiresAuth: true } },
    { path: '/admin', name: 'AdminPanel', component: AdminPanel, meta: { requiresAuth: true, requiresAdmin: true }, children: [
        { path: 'users', name: 'AdminUserManagement', component: AdminUserManagement },
        { path: 'users/:id', name: 'AdminUserDetails', component: AdminUserDetails, props: true },
        { path: 'categories/create', name: 'AdminCreateCategory', component: AdminCreateCategory },
        { path: 'products/create', name: 'AdminCreateProduct', component: AdminCreateProduct },
        { path: 'orders', name: 'AdminOrderManagement', component: AdminOrderManagement }
    ] },
    { path: '/auth/yandex/callback', name: 'YandexCallback', component: LoginForm },
    { path: '/', redirect: '/home' },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Проверка авторизации перед переходом на защищенные маршруты
router.beforeEach((to, from, next) => {
    // Обработка OAuth токенов из хэша URL (для Яндекс авторизации)
    const hash = window.location.hash;
    if (hash && hash.includes('access_token=')) {
        // Извлекаем токен из хэша
        const accessToken = hash.match(/access_token=([^&]*)/)[1];
        if (accessToken) {
            console.log('Получен токен Яндекс:', accessToken);
            // Сохраняем токен и перенаправляем на главную страницу
            localStorage.setItem('yandex_token', accessToken);
            
            // Очищаем хэш из URL
            window.location.hash = '';
            
            // Перенаправляем на страницу логина для обработки токена
            next('/login');
            return;
        }
    }

    // Проверка авторизации для защищенных маршрутов
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);
    const token = localStorage.getItem('token');
    
    if (requiresAuth && !token) {
        next('/login');
    } else if (requiresAdmin) {
        // Здесь можно добавить проверку на права администратора
        // Для простоты предположим, что у нас есть метод для проверки
        const isAdmin = localStorage.getItem('isAdmin') === 'true';
        if (!isAdmin) {
            next('/');
        } else {
            next();
        }
    } else {
        next();
    }
});

export default router
