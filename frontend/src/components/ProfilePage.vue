<template>
    <div class="profile-page">
    <div class="profile-container">
            <div class="profile-header">
                <div class="header-content">
                    <h1 class="profile-title">Личный кабинет</h1>
                    <p class="profile-subtitle">Управляйте своим аккаунтом и просматривайте историю заказов</p>
            </div>
        </div>
            
            <div v-if="user" class="profile-content">
                <div class="profile-sidebar">
                    <div class="profile-image-wrapper">
                        <img 
                            :src="user.profile_image ? `${apiBaseUrl}${user.profile_image}` : defaultImage" 
                            alt="Фото профиля" 
                            class="profile-image" 
                        />
                        <div v-if="isEditing" class="image-controls">
                            <label for="profile-image-upload" class="image-upload-btn">
                                <span class="upload-icon">📷</span>
                                <span>Изменить фото</span>
                            </label>
                            <input 
                                id="profile-image-upload"
                                type="file" 
                                @change="uploadImage" 
                                accept="image/*" 
                                class="file-input" 
                            />
                            <button 
                                type="button" 
                                @click="removeImage" 
                                v-if="user.profile_image" 
                                class="remove-image-btn"
                            >
                                Удалить фото
                            </button>
                    </div>
                    </div>
                    
                    <div class="user-status">
                        <div class="status-badge" :class="{ 'admin-badge': user.is_superuser }">
                            {{ user.is_superuser ? 'Администратор' : 'Пользователь' }}
                    </div>
                        <p class="status-text">Аккаунт создан: {{ formatDate(user.date_joined || new Date()) }}</p>
                </div>
                    
                    <div class="sidebar-menu">
                        <button 
                            @click="setActiveTab('profile')" 
                            class="menu-item" 
                            :class="{ active: activeTab === 'profile' }"
                        >
                            <span class="menu-icon">👤</span>
                            <span class="menu-text">Профиль</span>
                        </button>
                        <button 
                            @click="setActiveTab('orders')" 
                            class="menu-item"
                            :class="{ active: activeTab === 'orders' }"
                        >
                            <span class="menu-icon">🛍️</span>
                            <span class="menu-text">История заказов</span>
                        </button>
                        <button 
                            @click="setActiveTab('favorites')" 
                            class="menu-item"
                            :class="{ active: activeTab === 'favorites' }"
                        >
                            <span class="menu-icon">❤️</span>
                            <span class="menu-text">Избранное</span>
                        </button>
                        <button 
                            @click="setActiveTab('notifications')" 
                            class="menu-item"
                            :class="{ active: activeTab === 'notifications' }"
                        >
                            <span class="menu-icon">🔔</span>
                            <span class="menu-text">Уведомления</span>
                        </button>
                        <button @click="logout" class="menu-item logout">
                            <span class="menu-icon">🚪</span>
                            <span class="menu-text">Выйти</span>
                        </button>
                    </div>
                </div>
                
                <div class="profile-main">
                    <!-- Профиль -->
                    <div v-if="activeTab === 'profile'">
                        <div class="profile-card">
                            <div class="card-header">
                                <h2 class="card-title">Личная информация</h2>
                                <button 
                                    v-if="!isEditing && canEditProfile()" 
                                    @click="startEditing" 
                                    class="edit-button"
                                >
                                    <span class="edit-icon">✏️</span> Редактировать
                                </button>
                            </div>
                            
                            <div v-if="!isEditing" class="profile-info">
                                <div class="info-row">
                                    <div class="info-label">Имя</div>
                                    <div class="info-value">{{ user.first_name || '—' }} {{ user.last_name || '—' }}</div>
                                </div>
                                <div class="info-row">
                                    <div class="info-label">Имя пользователя</div>
                                    <div class="info-value">{{ user.username }}</div>
                                </div>
                                <div class="info-row">
                                    <div class="info-label">Электронная почта</div>
                                    <div class="info-value email">{{ user.email }}</div>
                                </div>
                            </div>
                            
                            <form v-else @submit.prevent="updateProfile" class="profile-form">
                        <div class="form-group">
                                    <label for="first_name">Имя</label>
                                    <input type="text" id="first_name" v-model="user.first_name" placeholder="Введите имя">
                        </div>
                        <div class="form-group">
                                    <label for="last_name">Фамилия</label>
                                    <input type="text" id="last_name" v-model="user.last_name" placeholder="Введите фамилию">
                        </div>
                        <div class="form-group">
                                    <label for="username">Имя пользователя</label>
                                    <input type="text" id="username" v-model="user.username" required placeholder="Введите имя пользователя">
                        </div>
                        <div class="form-group">
                                    <label for="email">Электронная почта</label>
                                    <input type="email" id="email" v-model="user.email" required placeholder="Введите email">
                        </div>
                                <div class="form-actions">
                                    <button type="button" @click="cancelEditing" class="cancel-button">
                                        Отмена
                                    </button>
                                    <button type="submit" class="save-button">
                                        Сохранить изменения
                                    </button>
                    </div>
                </form>
            </div>
                        
                        <div class="profile-card">
                            <div class="card-header">
                                <h2 class="card-title">Статистика покупок</h2>
                            </div>
                            <div class="stats-container">
                                <div class="stat-item">
                                    <div class="stat-value">{{ statistics.orderCount }}</div>
                                    <div class="stat-label">Заказов</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{{ statistics.productCount }}</div>
                                    <div class="stat-label">Товаров</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{{ formatPrice(statistics.totalSpent) }}</div>
                                    <div class="stat-label">Покупок</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{{ statistics.favoritesCount }}</div>
                                    <div class="stat-label">В избранном</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- История заказов -->
                    <div v-if="activeTab === 'orders'">
                        <div class="profile-card">
                            <div class="card-header">
                                <h2 class="card-title">История заказов</h2>
                            </div>
                            
                            <div class="orders-list" v-if="orders.length > 0">
                                <div v-for="order in orders" :key="order.id" class="order-item">
                                    <div class="order-header">
                                        <div class="order-info">
                                            <div class="order-number">
                                                <span class="order-label">Заказ:</span>
                                                <span class="order-value">{{ order.number }}</span>
                                            </div>
                                            <div class="order-date">
                                                <span class="order-label">Дата:</span>
                                                <span class="order-value">{{ formatOrderDate(order.date) }}</span>
                                            </div>
                                        </div>
                                        <div class="order-status" :class="`status-${mapStatusClass(order.status)}`">
                                            {{ getOrderStatusText(order.status) }}
                                        </div>
                                    </div>
                                    
                                    <div class="order-products">
                                        <div v-for="item in order.items" :key="item.id" class="order-product">
                                            <div class="product-image" v-if="item.image">
                                                <img :src="`${apiBaseUrl}${item.image}`" :alt="item.name" />
                                            </div>
                                            <div class="product-info">
                                                <div class="product-name">{{ item.name }}</div>
                                                <div class="product-quantity">{{ item.quantity }} шт.</div>
                                            </div>
                                            <div class="product-price">{{ formatPrice(item.price * item.quantity) }}</div>
                                        </div>
                                    </div>
                                    
                                    <div class="order-footer">
                                        <div class="order-total">
                                            <span class="total-label">Итого:</span>
                                            <span class="total-value">{{ formatPrice(order.total) }}</span>
                                        </div>
                                        <button class="order-details-btn" @click="viewOrderDetails(order.id)">Подробнее</button>
                                    </div>
                                </div>
                            </div>
                            
                            <div v-else class="empty-state">
                                <div class="empty-icon">📦</div>
                                <h3 class="empty-title">У вас пока нет заказов</h3>
                                <p class="empty-text">Когда вы сделаете заказ, он появится здесь</p>
                                <button class="shop-btn" @click="goToShop">Перейти в каталог</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Избранное -->
                    <div v-if="activeTab === 'favorites'">
                        <div class="profile-card">
                            <div class="card-header">
                                <h2 class="card-title">Избранные товары</h2>
                            </div>
                            
                            <div class="favorites-list" v-if="favorites.length > 0">
                                <div v-for="product in favorites" :key="product.id" class="favorite-item">
                                    <div class="favorite-image">
                                        <img :src="product.image" :alt="product.name" />
                                    </div>
                                    <div class="favorite-details">
                                        <div class="favorite-name">{{ product.name }}</div>
                                        <div class="favorite-price">{{ formatPrice(product.price) }}</div>
                                    </div>
                                    <div class="favorite-actions">
                                        <button class="add-to-cart-btn" @click="addToCart(product.id)">В корзину</button>
                                        <button class="remove-favorite-btn" @click="removeFavorite(product.id)">❌</button>
                                    </div>
                                </div>
                            </div>
                            
                            <div v-else class="empty-state">
                                <div class="empty-icon">❤️</div>
                                <h3 class="empty-title">В избранном пока пусто</h3>
                                <p class="empty-text">Добавляйте товары в избранное, чтобы они отображались здесь</p>
                                <button class="shop-btn" @click="goToShop">Перейти в каталог</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Уведомления -->
                    <div v-if="activeTab === 'notifications'">
                        <div class="profile-card">
                            <div class="card-header">
                                <h2 class="card-title">Уведомления</h2>
                            </div>
                            
                            <div class="empty-state">
                                <div class="empty-icon">🔔</div>
                                <h3 class="empty-title">У вас нет новых уведомлений</h3>
                                <p class="empty-text">Здесь будут отображаться важные обновления и новости</p>
                                <button class="shop-btn" @click="goToShop">Перейти в каталог</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div v-else class="profile-content not-logged-in">
                <div class="login-card">
                    <h2 class="login-title">Требуется авторизация</h2>
                    <p class="login-text">Для доступа к личному кабинету необходимо войти в систему</p>
                    <div class="login-buttons">
                <button @click="goToLogin" class="login-button">Войти</button>
                        <button @click="goToRegister" class="register-button">Регистрация</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { inject } from 'vue';
import defaultImage from '@/assets/img/default_profile_image.png';

const user = ref(null);
const isEditing = ref(false);
const activeTab = ref('profile'); // Активная вкладка
const router = useRouter();
const route = useRoute();
const logout = inject('logout');
const currentUser = ref(null);
const apiBaseUrl = 'http://127.0.0.1:8000';

// Данные
const orders = ref([]);
const wishlist = ref([]);
const favorites = ref([]);
const statistics = ref({
    orderCount: 0,
    productCount: 0,
    totalSpent: 0,
    favoritesCount: 0
});

onMounted(async () => {
    // Проверяем URL-параметры для установки активной вкладки
    const tabParam = route.query.tab;
    if (tabParam && ['profile', 'orders', 'favorites', 'notifications'].includes(tabParam)) {
        activeTab.value = tabParam;
    }
    
    await loadCurrentUser();
    await loadUserProfile();
    await loadOrders();
    await loadFavorites();
    calculateStatistics();
});

// Получение текущего пользователя
const loadCurrentUser = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get(`${apiBaseUrl}/users/profile/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            currentUser.value = response.data;
        }
    } catch (error) {
        console.error('Ошибка загрузки текущего пользователя:', error);
    }
};

// Получение профиля пользователя
const loadUserProfile = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get(`${apiBaseUrl}/users/profile/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            user.value = response.data;
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
    }
};

// Получение заказов пользователя
const loadOrders = async () => {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            console.log('Отсутствует токен авторизации');
            return;
        }
        
        console.log(`Запрос к: ${apiBaseUrl}/main/user/orders/`);
        
        const response = await axios.get(`${apiBaseUrl}/main/user/orders/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log('Получены данные заказов:', response.data);
        
        // Проверяем наличие массива заказов в ответе
        if (response.data && Array.isArray(response.data.orders)) {
            orders.value = response.data.orders;
            
            // Обновляем статистику, если пришли данные о сумме покупок
            if (typeof response.data.total_spent === 'number') {
                statistics.value.totalSpent = response.data.total_spent;
            }
        } else {
            console.error('Данные заказов не в ожидаемом формате:', response.data);
            loadFallbackOrders();
        }
    } catch (error) {
        console.error('Ошибка загрузки заказов:', error);
        console.error('Детали ошибки:', error.response ? error.response.data : 'Нет данных ответа');
        loadFallbackOrders();
    }
};

// Загрузка тестовых данных заказов
const loadFallbackOrders = () => {
    orders.value = [
        {
            id: 1,
            number: 'ORD-2023-001',
            date: new Date(2023, 8, 15),
            status: 'Доставлен',
            total: 45990,
            items: [
                { id: 1, name: 'Смартфон Samsung Galaxy A54', price: 32990, quantity: 1 },
                { id: 2, name: 'Защитное стекло', price: 1000, quantity: 1 },
                { id: 3, name: 'Чехол защитный', price: 2000, quantity: 1 }
            ]
        },
        {
            id: 2,
            number: 'ORD-2023-002',
            date: new Date(2023, 9, 22),
            status: 'В пути',
            total: 89990,
            items: [
                { id: 4, name: 'Ноутбук ASUS VivoBook', price: 89990, quantity: 1 }
            ]
        },
        {
            id: 3,
            number: 'ORD-2023-003',
            date: new Date(2023, 10, 5),
            status: 'Обработка',
            total: 10470,
            items: [
                { id: 5, name: 'Мышь компьютерная Logitech', price: 3490, quantity: 3 }
            ]
        }
    ];
};

// Преобразование статуса заказа в CSS-класс
const mapStatusClass = (status) => {
    return status.toLowerCase().replace(/\s+/g, '-');
};

// Получение текстового представления статуса заказа
const getOrderStatusText = (status) => {
    const statusMap = {
        'pending': 'Ожидает',
        'assembling': 'В сборке',
        'shipped': 'В пути',
        'delivered': 'Доставлен',
        'canceled': 'Отменен'
    };
    return statusMap[status] || status;
};

// Получение списка избранных товаров
const loadFavorites = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            // Получаем сначала список ID избранных товаров
            const wishlistResponse = await axios.get(`${apiBaseUrl}/main/wishlist/check/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            wishlist.value = wishlistResponse.data.wishlist;
            
            // Затем получаем информацию о самих товарах
            const favoritesResponse = await axios.get(`${apiBaseUrl}/main/products/favorites/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            // Проверяем, что данные являются массивом
            if (Array.isArray(favoritesResponse.data)) {
                favorites.value = favoritesResponse.data.map(product => ({
                    id: product.id,
                    name: product.name,
                    price: parseFloat(product.price),
                    image: product.image ? `${apiBaseUrl}${product.image}` : 'https://via.placeholder.com/100',
                    discounted_price: product.get_discounted_price ? parseFloat(product.get_discounted_price) : parseFloat(product.price)
                }));
            } else {
                console.error('Данные избранного не в ожидаемом формате:', favoritesResponse.data);
                loadFallbackFavorites();
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки избранного:', error);
        loadFallbackFavorites();
    }
};

// Загрузка тестовых данных избранного
const loadFallbackFavorites = () => {
    favorites.value = [
        { id: 101, name: 'Смартфон iPhone 14 Pro', price: 89990, image: 'https://via.placeholder.com/100' },
        { id: 102, name: 'Наушники Sony WH-1000XM4', price: 27990, image: 'https://via.placeholder.com/100' },
        { id: 103, name: 'Умные часы Apple Watch Series 8', price: 36990, image: 'https://via.placeholder.com/100' }
    ];
};

// Расчет статистики
const calculateStatistics = () => {
    let totalItems = 0;
    let totalSpent = 0;
    
    // Считаем количество товаров и общую сумму
    orders.value.forEach(order => {
        if (order.status === 'shipped' || order.status === 'delivered') {
            order.items.forEach(item => {
                totalItems += item.quantity;
            });
            totalSpent += order.total;
        }
    });
    
    statistics.value = {
        orderCount: orders.value.length,
        productCount: totalItems,
        totalSpent: totalSpent || statistics.value.totalSpent, // Используем значение из API, если оно есть
        favoritesCount: favorites.value.length
    };
};

// Удаление товара из избранного
const removeFavorite = async (productId) => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            await axios.delete(`${apiBaseUrl}/main/wishlist/remove/${productId}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            // Обновляем список избранных товаров
            favorites.value = favorites.value.filter(product => product.id !== productId);
            // Обновляем статистику
            statistics.value.favoritesCount = favorites.value.length;
        }
    } catch (error) {
        console.error('Ошибка удаления из избранного:', error);
    }
};

// Добавление товара в корзину
const addToCart = async (productId) => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            await axios.post(`${apiBaseUrl}/main/cart/add/`, {
                product_id: productId,
                quantity: 1
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert('Товар добавлен в корзину!');
        }
    } catch (error) {
        console.error('Ошибка добавления в корзину:', error);
        alert('Ошибка при добавлении товара в корзину');
    }
};

// Форматирование даты
const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
};

// Вычисляемые свойства для отображения даты заказа
const formatOrderDate = (date) => {
    return new Date(date).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
};

// Функция для форматирования цены
const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(price);
};

// Проверка прав на редактирование профиля
const canEditProfile = () => {
    if (!currentUser.value || !user.value) return false;
    
    // Админ может редактировать любые профили
    if (currentUser.value.is_superuser) return true;
    
    // Обычный пользователь может редактировать только свой профиль
    return user.value.id === currentUser.value.id;
};

// Переключение активной вкладки
const setActiveTab = (tab) => {
    activeTab.value = tab;
    
    // Обновляем URL для возможности прямого доступа к вкладке
    router.replace({ query: { ...route.query, tab } });
};

// Переход на просмотр деталей заказа
const viewOrderDetails = (orderId) => {
    router.push(`/orders/${orderId}`);
};

// Навигация
const goToLogin = () => router.push('/login');
const goToRegister = () => router.push('/register');
const goToShop = () => router.push('/');

// Редактирование профиля
const startEditing = () => {
    isEditing.value = true;
};

const cancelEditing = () => {
    isEditing.value = false;
    loadUserProfile();
};

const updateProfile = async () => {
    try {
        const token = localStorage.getItem('token');
        const response = await axios.put(`${apiBaseUrl}/users/profile/`, {
            first_name: user.value.first_name,
            last_name: user.value.last_name,
            username: user.value.username,
            email: user.value.email
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        user.value = response.data;
        isEditing.value = false;
        alert('Профиль успешно обновлен!');
    } catch (error) {
        console.error('Ошибка обновления профиля:', error);
        alert('Ошибка при обновлении профиля');
    }
};

const uploadImage = async (event) => {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('profile_image', file);

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(`${apiBaseUrl}/users/profile/image/`, formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            user.value.profile_image = response.data.profile_image;
            alert('Изображение успешно загружено!');
        } catch (error) {
            console.error('Ошибка загрузки изображения:', error);
            alert('Ошибка при загрузке изображения');
        }
    }
};

const removeImage = async () => {
    try {
        const token = localStorage.getItem('token');
        await axios.delete(`${apiBaseUrl}/users/profile/image/remove/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        user.value.profile_image = null; // Удаляем локально
        alert('Изображение успешно удалено!');
    } catch (error) {
        console.error('Ошибка удаления изображения:', error);
        alert('Ошибка при удалении изображения');
    }
};
</script>

<style scoped>
/* Базовые стили */
.profile-page {
    font-family: 'Arial', sans-serif;
    color: #333;
    background-color: #f5f7fa;
    min-height: 100vh;
}

.profile-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Заголовок профиля */
.profile-header {
    background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
    padding: 40px 30px;
    border-radius: 12px;
    margin-bottom: 30px;
    color: white;
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.2);
}

.profile-title {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 10px 0;
}

.profile-subtitle {
    font-size: 16px;
    opacity: 0.8;
    margin: 0;
}

/* Содержимое профиля */
.profile-content {
    display: flex;
    gap: 30px;
}

/* Боковая панель */
.profile-sidebar {
    width: 300px;
    flex-shrink: 0;
}

.profile-image-wrapper {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.profile-image {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #6b46c1;
    background-color: #f0f0f0;
}

.image-controls {
    margin-top: 15px;
}

.image-upload-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    cursor: pointer;
    font-size: 14px;
    color: #6b46c1;
    margin-bottom: 10px;
}

.upload-icon {
    font-size: 20px;
}

.file-input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
    visibility: hidden;
}

.remove-image-btn {
    background: none;
    border: none;
    color: #e53e3e;
    font-size: 14px;
    cursor: pointer;
    text-decoration: underline;
    padding: 0;
}

.user-status {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
    text-align: center;
}

.status-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    background-color: #4299e1;
    color: white;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 10px;
}

.status-badge.admin-badge {
    background-color: #e53e3e;
}

.status-text {
    font-size: 14px;
    color: #718096;
    margin: 0;
}

.sidebar-menu {
    background-color: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 15px 20px;
    width: 100%;
    border: none;
    background: none;
    text-align: left;
    cursor: pointer;
    font-size: 16px;
    color: #4a5568;
    border-bottom: 1px solid #edf2f7;
    transition: all 0.2s ease;
}

.menu-item:hover {
    background-color: #f9fafb;
    color: #6b46c1;
}

.menu-item.active {
    background-color: #f9fafb;
    color: #6b46c1;
    font-weight: 600;
    border-left: 4px solid #6b46c1;
}

.menu-item.logout {
    color: #e53e3e;
}

.menu-icon {
    font-size: 20px;
}

/* Основная часть профиля */
.profile-main {
    flex-grow: 1;
}

.profile-card {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #edf2f7;
}

.card-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0;
    color: #2d3748;
}

.edit-button {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 12px;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.edit-button:hover {
    background-color: #553c9a;
}

.info-row {
    display: flex;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #edf2f7;
}

.info-row:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

.info-label {
    width: 180px;
    font-weight: 600;
    color: #718096;
}

.info-value {
    flex-grow: 1;
    color: #2d3748;
}

.info-value.email {
    color: #6b46c1;
}

/* Форма редактирования */
.profile-form {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.form-group {
    margin-bottom: 0;
}

.form-group label {
    display: block;
    font-size: 14px;
    color: #718096;
    margin-bottom: 5px;
}

.form-group input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 16px;
    transition: border-color 0.2s;
}

.form-group input:focus {
    outline: none;
    border-color: #6b46c1;
    box-shadow: 0 0 0 1px #6b46c1;
}

.form-actions {
    grid-column: 1 / -1;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.cancel-button {
    padding: 10px 16px;
    background-color: #e2e8f0;
    color: #4a5568;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.cancel-button:hover {
    background-color: #cbd5e0;
}

.save-button {
    padding: 10px 16px;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.save-button:hover {
    background-color: #553c9a;
}

/* Статистика */
.stats-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

.stat-item {
    text-align: center;
    padding: 20px 15px;
    background-color: #f9fafb;
    border-radius: 8px;
}

.stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #6b46c1;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 14px;
    color: #718096;
}

/* История заказов */
.orders-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.order-item {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
}

.order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background-color: #f9fafb;
    border-bottom: 1px solid #e2e8f0;
}

.order-info {
    display: flex;
    gap: 20px;
}

.order-number, .order-date {
    display: flex;
    align-items: center;
    gap: 5px;
}

.order-label {
    font-weight: 600;
    color: #718096;
    font-size: 14px;
}

.order-value {
    color: #2d3748;
    font-size: 14px;
}

.order-status {
    padding: 5px 10px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
}

.status-доставлен, .status-delivered {
    background-color: #c6f6d5;
    color: #22543d;
}

.status-в-пути, .status-shipped {
    background-color: #bee3f8;
    color: #2a4365;
}

.status-обработка, .status-assembling {
    background-color: #fed7d7;
    color: #822727;
}

.status-отменен, .status-canceled {
    background-color: #e2e8f0;
    color: #4a5568;
}

.status-pending {
    background-color: #feebc8;
    color: #7b341e;
}

.order-products {
    padding: 15px;
}

.order-product {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px dashed #e2e8f0;
}

.order-product:last-child {
    border-bottom: none;
}

.product-image {
    width: 50px;
    height: 50px;
    flex-shrink: 0;
    margin-right: 15px;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.product-info {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.product-name {
    font-weight: 500;
    color: #2d3748;
}

.product-quantity {
    font-size: 14px;
    color: #718096;
}

.product-price {
    font-weight: 600;
    color: #2d3748;
}

.order-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background-color: #f9fafb;
    border-top: 1px solid #e2e8f0;
}

.order-total {
    display: flex;
    align-items: center;
    gap: 10px;
}

.total-label {
    font-weight: 600;
    color: #4a5568;
}

.total-value {
    font-weight: 700;
    font-size: 18px;
    color: #6b46c1;
}

.order-details-btn {
    padding: 8px 16px;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.order-details-btn:hover {
    background-color: #553c9a;
}

/* Избранное */
.favorites-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.favorite-item {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
}

.favorite-image {
    height: 180px;
    overflow: hidden;
}

.favorite-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.favorite-item:hover .favorite-image img {
    transform: scale(1.05);
}

.favorite-details {
    padding: 15px;
}

.favorite-name {
    font-weight: 500;
    margin-bottom: 8px;
    color: #2d3748;
}

.favorite-price {
    font-weight: 700;
    color: #6b46c1;
}

.favorite-actions {
    display: flex;
    padding: 15px;
    border-top: 1px solid #e2e8f0;
    gap: 10px;
}

.add-to-cart-btn {
    flex: 1;
    padding: 8px;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.add-to-cart-btn:hover {
    background-color: #553c9a;
}

.remove-favorite-btn {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f9fafb;
    color: #e53e3e;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.remove-favorite-btn:hover {
    background-color: #fed7d7;
}

/* Пустое состояние */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    text-align: center;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 15px;
}

.empty-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #2d3748;
}

.empty-text {
    font-size: 16px;
    color: #718096;
    margin-bottom: 20px;
    max-width: 400px;
}

.shop-btn {
    padding: 10px 20px;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.shop-btn:hover {
    background-color: #553c9a;
}

/* Экран не-авторизованного пользователя */
.not-logged-in {
    justify-content: center;
    min-height: 400px;
}

.login-card {
    background-color: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    text-align: center;
    max-width: 400px;
    width: 100%;
}

.login-title {
    font-size: 24px;
    margin-bottom: 15px;
    color: #2d3748;
}

.login-text {
    color: #718096;
    margin-bottom: 30px;
}

.login-buttons {
    display: flex;
    gap: 10px;
}

.login-button,
.register-button {
    flex: 1;
    padding: 12px;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.login-button {
    background-color: #6b46c1;
    color: white;
}

.login-button:hover {
    background-color: #553c9a;
}

.register-button {
    background-color: #e2e8f0;
    color: #4a5568;
}

.register-button:hover {
    background-color: #cbd5e0;
}

/* Адаптивность */
@media (max-width: 768px) {
    .profile-content {
        flex-direction: column;
    }
    
    .profile-sidebar {
        width: 100%;
    }
    
    .profile-image-wrapper {
        display: flex;
        align-items: center;
        text-align: left;
        padding: 15px;
    }
    
    .profile-image {
        width: 120px;
        height: 120px;
        margin-right: 20px;
    }
    
    .image-controls {
        flex: 1;
        margin-top: 0;
    }
    
    .form-group {
        grid-column: 1 / -1;
    }
    
    .stats-container {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .order-header, .order-footer {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .order-info {
        flex-direction: column;
        gap: 5px;
    }
    
    .order-footer {
        padding-bottom: 20px;
    }
    
    .order-details-btn {
        width: 100%;
    }
    
    .favorites-list {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    }
}

@media (max-width: 480px) {
    .profile-header {
        padding: 30px 20px;
    }
    
    .profile-title {
        font-size: 24px;
    }
    
    .profile-image-wrapper {
        flex-direction: column;
        text-align: center;
    }
    
    .profile-image {
        margin-right: 0;
        margin-bottom: 15px;
    }
    
    .info-row {
        flex-direction: column;
    }
    
    .info-label {
        width: 100%;
        margin-bottom: 5px;
    }
    
    .stats-container {
        grid-template-columns: 1fr;
    }
    
    .profile-form {
        display: block;
    }
    
    .form-actions {
        flex-direction: column-reverse;
    }
    
    .cancel-button, .save-button {
        width: 100%;
    }
    
    .login-buttons {
        flex-direction: column;
    }
    
    .favorites-list {
        grid-template-columns: 1fr;
    }
}
</style>