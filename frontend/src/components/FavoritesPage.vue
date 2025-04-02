<template>
    <div class="favorites-container">
        <h1 class="page-title">Понравившиеся товары</h1>
        
        <div v-if="loading" class="loading-container">
            <p>Загрузка понравившихся товаров...</p>
        </div>
        
        <div v-else-if="error" class="error-container">
            <p>{{ error }}</p>
            <button @click="fetchFavorites" class="retry-button">Попробовать снова</button>
        </div>
        
        <div v-else-if="favorites.length === 0" class="empty-favorites">
            <p>У вас еще нет понравившихся товаров</p>
            <router-link to="/home" class="browse-link">Перейти к каталогу товаров</router-link>
        </div>
        
        <div v-else class="favorites-grid">
            <div v-for="product in favorites" :key="product.id" class="product-card">
                <div class="product-card-inner">
                    <div class="favorite-icon" @click="toggleFavorite(product)">
                        <i class="fas fa-heart"></i>
                    </div>
                    <router-link :to="`/product/${product.id}`" class="product-link">
                        <div class="product-image">
                            <img :src="`${$apiBaseUrl}${product.main_image}`" :alt="product.name">
                        </div>
                        <div class="product-info">
                            <h3 class="product-name">{{ product.name }}</h3>
                            <p class="product-price">{{ product.price }} ₽</p>
                            <div class="product-rating">
                                <span v-for="i in 5" :key="i" class="star" 
                                    :class="{ 'filled': i <= Math.round(product.average_rating) }">★</span>
                                <span class="rating-count">({{ product.reviews_count || 0 }})</span>
                            </div>
                        </div>
                    </router-link>
                    <button @click="addToCart(product)" class="add-to-cart-button">
                        В корзину
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { inject } from 'vue';

const $apiBaseUrl = 'http://127.0.0.1:8000';
const favorites = ref([]);
const loading = ref(true);
const error = ref(null);
const router = useRouter();
const isAuthenticated = inject('isAuthenticated');
const showToast = inject('showToast', null);

onMounted(() => {
    if (!isAuthenticated.value) {
        router.push('/login');
        if (showToast) {
            showToast('Пожалуйста, авторизуйтесь, чтобы просмотреть понравившиеся товары', 'error');
        }
        return;
    }
    fetchFavorites();
});

const fetchFavorites = async () => {
    try {
        loading.value = true;
        error.value = null;
        
        const token = localStorage.getItem('token');
        const response = await axios.get(`${$apiBaseUrl}/main/products/favorites/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        favorites.value = response.data;
    } catch (err) {
        console.error('Ошибка при загрузке понравившихся товаров:', err);
        error.value = 'Не удалось загрузить понравившиеся товары. Пожалуйста, попробуйте позже.';
    } finally {
        loading.value = false;
    }
};

const toggleFavorite = async (product) => {
    try {
        const token = localStorage.getItem('token');
        await axios.delete(`${$apiBaseUrl}/main/wishlist/remove/${product.id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        // Удаляем продукт из списка
        favorites.value = favorites.value.filter(p => p.id !== product.id);
        
        if (showToast) {
            showToast('Товар удален из избранного', 'success');
        }
    } catch (err) {
        console.error('Ошибка при обновлении избранного:', err);
        if (showToast) {
            showToast('Ошибка при обновлении избранного', 'error');
        }
    }
};

const addToCart = async (product) => {
    try {
        const token = localStorage.getItem('token');
        await axios.post(`${$apiBaseUrl}/main/cart/add/`, {
            product_id: product.id,
            quantity: 1
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        if (showToast) {
            showToast('Товар добавлен в корзину', 'success');
        }
    } catch (err) {
        console.error('Ошибка при добавлении в корзину:', err);
        if (showToast) {
            showToast('Ошибка при добавлении в корзину', 'error');
        }
    }
};
</script>

<style scoped>
.favorites-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.page-title {
    font-size: 28px;
    color: #333;
    margin-bottom: 30px;
    text-align: center;
}

.loading-container, .error-container, .empty-favorites {
    text-align: center;
    padding: 40px;
    background-color: #f9f9f9;
    border-radius: 8px;
    margin: 20px 0;
}

.retry-button, .browse-link {
    display: inline-block;
    margin-top: 15px;
    padding: 10px 20px;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    text-decoration: none;
}

.retry-button:hover, .browse-link:hover {
    background-color: #5a32b0;
}

.favorites-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.product-card {
    border: 1px solid #eee;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s, box-shadow 0.3s;
    background-color: white;
}

.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.product-card-inner {
    position: relative;
}

.favorite-icon {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 1;
}

.favorite-icon i {
    color: #ff4d4d;
    font-size: 16px;
}

.product-link {
    text-decoration: none;
    color: inherit;
    display: block;
}

.product-image {
    height: 200px;
    overflow: hidden;
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.product-card:hover .product-image img {
    transform: scale(1.05);
}

.product-info {
    padding: 15px;
}

.product-name {
    font-size: 16px;
    margin: 0 0 10px;
    color: #333;
    height: 40px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.product-price {
    font-size: 18px;
    font-weight: bold;
    color: #6b46c1;
    margin: 10px 0;
}

.product-rating {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.star {
    color: #ddd;
    margin-right: 2px;
}

.star.filled {
    color: #ffc107;
}

.rating-count {
    margin-left: 5px;
    font-size: 12px;
    color: #777;
}

.add-to-cart-button {
    width: 100%;
    padding: 10px;
    background-color: #6b46c1;
    color: white;
    border: none;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.add-to-cart-button:hover {
    background-color: #5a32b0;
}
</style> 