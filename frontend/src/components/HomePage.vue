<template>
    <div class="home-container">
        <ToastNotification ref="toast" />
        <!-- Карусель с акцией -->
        <swiper :modules="modules" :pagination="{ clickable: true }" class="swiper-container" @swiper="onSwiper"
            @slideChange="onSlideChange">
            <swiper-slide>
                <div class="promo-banner">
                    <button class="nav-arrow left-arrow"></button>
                    <div class="promo-text">
                        <h2>Умная колонка</h2>
                        <p class="discount">СКИДКА 30% ПРИ ПОКУПКЕ ВТОРОГО ТОВАРА</p>
                    </div>
                    <img src="https://via.placeholder.com/150" alt="Promo Image" class="promo-image" />
                    <button class="nav-arrow right-arrow">></button>
                </div>
            </swiper-slide>
            <swiper-slide>
                <div class="promo-banner">
                    <button class="nav-arrow left-arrow"></button>
                    <div class="promo-text">
                        <h2>Наушники</h2>
                        <p class="discount">СКИДКА 20% НА ВСЕ АУДИО</p>
                    </div>
                    <img src="https://via.placeholder.com/150?text=Headphones" alt="Promo Image" class="promo-image" />
                    <button class="nav-arrow right-arrow">></button>
                </div>
            </swiper-slide>
            <swiper-slide>
                <div class="promo-banner">
                    <button class="nav-arrow left-arrow"></button>
                    <div class="promo-text">
                        <h2>Ноутбук</h2>
                        <p class="discount">СКИДКА 15% НА ТЕХНИКУ</p>
                    </div>
                    <img src="https://via.placeholder.com/150?text=Laptop" alt="Promo Image" class="promo-image" />
                    <button class="nav-arrow right-arrow">></button>
                </div>
            </swiper-slide>
            <div class="swiper-pagination"></div>
        </swiper>

        <h2 class="home-title">Каталог</h2>
        <div class="categories-grid">
            <div v-for="category in categories" :key="category.id" class="category-card">
                <router-link :to="`/category/${category.id}`" class="category-link">
                    <div class="category-image-wrapper">
                        <img :src="category.image || defaultCategoryImage" :alt="`Category ${category.name}`"
                            class="category-image" />
                    </div>
                    <h3 class="category-name">{{ category.name }}</h3>
                </router-link>
            </div>
            <p v-if="categories.length === 0" class="no-data">Нет доступных категорий.</p>
        </div>

        <h2 class="home-title">Различные товары</h2>
        <div class="products-grid">
            <div v-for="product in products" :key="product.id" class="product-card">
                <router-link :to="`/product/${product.id}`" class="product-link">
                    <div class="image-wrapper">
                        <img :src="product.image || defaultImage" class="product-image" />
                        <div class="discount-tag">-4%</div>
                    </div>
                </router-link>
                <div class="product-content">
                    <h3>{{ product.name }}</h3>
                    <div class="price-container">
                        <p class="old-price"><s>{{ (product.price / 0.96).toFixed(2) }} ₽</s></p>
                        <p class="price">{{ product.price }} ₽</p>
                    </div>
                    <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                        <span>{{ product.is_available ? 'В наличии' : 'Нет в наличии' }}</span>
                        <span class="stock">Осталось: {{ product.stock }} шт.</span>
                    </div>
                    <div v-if="product.specifications" class="specifications">
                        <ul class="specifications-list">
                            <li v-for="(value, key) in product.specifications.specifications" :key="key" class="spec-item">
                                <strong>{{ key.replace(/_/g, ' ') }}:</strong> {{ value }}
                            </li>
                        </ul>
                    </div>

                </div>
                <div class="button-group">
                    <div v-if="cartItems[product.id]" class="quantity-controls">
                        <button @click="decreaseQuantity(product)" class="quantity-button">-</button>
                        <span class="quantity">{{ cartItems[product.id] }}</span>
                        <button @click="increaseQuantity(product)" class="quantity-button">+</button>
                    </div>
                    <button v-else @click="addToCart(product)" class="add-to-cart-button"
                        :disabled="!product.is_available">
                        {{ product.is_available ? 'В корзину' : 'Недоступно' }}
                    </button>
                    <button :class="['wishlist-button', { 'active': isInWishlist(product.id) }]"
                        @click="toggleWishlist(product)">
                        <span class="heart-icon">❤️</span>
                    </button>
                </div>
            </div>
            <p v-if="products.length === 0" class="no-data">Нет доступных товаров.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Pagination } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/pagination';
import defaultImage from '@/assets/img/Default_product_foto.jpg';
import defaultCategoryImage from '@/assets/img/Default_product_foto.jpg'; // Добавляем дефолтное изображение для категорий
import ToastNotification from './ToastNotification.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

const categories = ref([]);
const products = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const modules = ref([Pagination]);
const swiperInstance = ref(null);
const toast = ref(null);

onMounted(async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const [categoriesResponse, productsResponse, wishlistResponse, cartResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/main/categories/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/`, { headers }),
            token ? axios.get(`${API_BASE_URL}/main/wishlist/check/`, { headers }) : Promise.resolve({ data: [] }),
            token ? axios.get(`${API_BASE_URL}/main/cart/`, { headers }) : Promise.resolve({ data: [] })
        ]);

        categories.value = categoriesResponse.data;
        products.value = productsResponse.data;
        wishlist.value = wishlistResponse.data.wishlist || [];

        const cartData = cartResponse.data;
        if (Array.isArray(cartData)) {
            cartData.forEach(item => {
                cartItems.value[item.product.id] = item.quantity;
            });
        } else if (cartData && cartData.items && Array.isArray(cartData.items)) {
            cartData.items.forEach(item => {
                cartItems.value[item.product.id] = item.quantity;
            });
        }
    } catch (error) {
        console.error('Ошибка загрузки данных:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при загрузке данных. Проверьте консоль.', 'error');
    }
});

const onSwiper = (swiper) => {
    swiperInstance.value = swiper;
};

const onSlideChange = () => {
    console.log('Слайд изменен', swiperInstance.value.activeIndex);
};

const isInWishlist = computed(() => (productId) => {
    return wishlist.value.includes(productId);
});

const toggleWishlist = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
        toast.value.showToast('Пожалуйста, войдите в систему для добавления в желаемое.', 'warning');
        return;
    }

    try {
        if (isInWishlist.value(product.id)) {
            await axios.delete(`${API_BASE_URL}/main/wishlist/remove/${product.id}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value = wishlist.value.filter(id => id !== product.id);
            toast.value.showToast('Товар удален из желаемого', 'success');
        } else {
            await axios.post(`${API_BASE_URL}/main/wishlist/add/`, {
                product_id: product.id
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value.push(product.id);
            toast.value.showToast('Товар добавлен в желаемое', 'success');
        }
    } catch (error) {
        console.error('Ошибка управления желаемым:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при управлении желаемым: ' + (error.response ? error.response.data.error : error.message), 'error');
    }
};

const addToCart = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
        toast.value.showToast('Пожалуйста, войдите в систему для добавления в корзину.', 'warning');
        return;
    }

    if (!product.is_available) {
        toast.value.showToast('Товар недоступен для добавления в корзину.', 'error');
        return;
    }

    try {
        await axios.post(`${API_BASE_URL}/main/cart/add/`, {
            product_id: product.id,
            quantity: 1
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        cartItems.value[product.id] = 1;
        toast.value.showToast(`Товар "${product.name}" добавлен в корзину!`, 'success');
    } catch (error) {
        console.error('Ошибка добавления в корзину:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при добавлении в корзину.', 'error');
    }
};

const increaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    try {
        const newQuantity = (cartItems.value[product.id] || 0) + 1;
        if (newQuantity > product.stock) {
            toast.value.showToast('Нельзя добавить больше, чем есть в наличии!', 'warning');
            return;
        }
        await axios.post(`${API_BASE_URL}/main/cart/add/`, {
            product_id: product.id,
            quantity: 1
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        cartItems.value[product.id] = newQuantity;
    } catch (error) {
        console.error('Ошибка увеличения количества:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при увеличении количества.', 'error');
    }
};

const decreaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    try {
        const newQuantity = (cartItems.value[product.id] || 0) - 1;
        if (newQuantity <= 0) {
            // Получаем ID элемента корзины из текущего заказа
            const cartResponse = await axios.get(`${API_BASE_URL}/main/cart/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const cartItem = cartResponse.data.items.find(item => item.product.id === product.id);
            if (!cartItem) {
                throw new Error('Товар не найден в корзине');
            }
            await axios.delete(`${API_BASE_URL}/main/cart/remove/${cartItem.id}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            delete cartItems.value[product.id];
        } else {
            await axios.post(`${API_BASE_URL}/main/cart/add/`, {
                product_id: product.id,
                quantity: -1
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            cartItems.value[product.id] = newQuantity;
        }
    } catch (error) {
        console.error('Ошибка уменьшения количества:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при уменьшении количества.', 'error');
    }
};
</script>

<style scoped>
.home-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Arial', sans-serif;
    background-color: #f5f5f5;
}

.swiper-container {
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
}

.promo-banner {
    background-color: #1a1a1a;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    min-height: 120px;
    position: relative;
}

.promo-text h2 {
    font-size: 20px;
    margin: 0;
    font-weight: 600;
}

.discount {
    font-size: 24px;
    color: #ffd700;
    font-weight: bold;
    margin: 5px 0;
}

.promo-image {
    width: 150px;
    height: auto;
    margin: 0 20px;
    border-radius: 8px;
}

.nav-arrow {
    background: none;
    border: none;
    color: #ccc;
    font-size: 24px;
    cursor: pointer;
    padding: 10px;
    transition: color 0.3s;
}

.nav-arrow:hover {
    color: white;
}

.swiper-pagination {
    bottom: 10px;
}

.swiper-pagination-bullet {
    background-color: #ccc;
    opacity: 0.7;
}

.swiper-pagination-bullet-active {
    background-color: #6b46c1;
    opacity: 1;
}

.home-title {
    font-size: 28px;
    color: #6b46c1;
    margin: 20px 0;
    text-align: center;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.categories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.category-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.category-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.category-link {
    text-decoration: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 15px;
}

.category-image-wrapper {
    width: 100%;
    height: 150px;
    overflow: hidden;
    position: relative;
}

.category-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.category-card:hover .category-image {
    transform: scale(1.05);
}

.category-name {
    font-size: 18px;
    color: #2c3e50;
    margin: 10px 0 0;
    font-weight: 600;
    text-align: center;
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.product-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 0;
}

.product-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.image-wrapper {
    position: relative;
    width: 100%;
    height: 200px;
    overflow: hidden;
}

.product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.product-card:hover .product-image {
    transform: scale(1.05);
}

.discount-tag {
    position: absolute;
    top: 10px;
    left: 10px;
    background: linear-gradient(135deg, #ffd700, #ffcc00);
    color: #1a1a1a;
    padding: 5px 12px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.product-content {
    padding: 15px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.product-card h3 {
    font-size: 18px;
    color: #2c3e50;
    margin: 0;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.price-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.old-price {
    font-size: 14px;
    color: #e74c3c;
    text-decoration: line-through;
    margin: 0;
}

.price {
    font-size: 22px;
    color: #27ae60;
    font-weight: 700;
    margin: 0;
}

.availability {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 14px;
    color: #27ae60;
    font-weight: 500;
}

.availability.out-of-stock {
    color: #e74c3c;
}

.stock {
    font-size: 12px;
    color: #7f8c8d;
}

.specifications {
    font-size: 12px;
    color: #7f8c8d;
    background: #f8f9fa;
    padding: 8px;
    border-radius: 8px;
    margin-top: 10px;
}

.spec-item {
    display: flex;
    justify-content: space-between;
    margin: 4px 0;
}

.spec-key {
    font-weight: 600;
    color: #34495e;
}

.button-group {
    padding: 15px;
    display: flex;
    gap: 10px;
    border-top: 1px solid #eee;
    background: #fafafa;
    align-items: center;
}

.add-to-cart-button {
    flex: 1;
    background: #3498db;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.3s ease, transform 0.2s ease;
}

.add-to-cart-button:hover:not(:disabled) {
    background: #2980b9;
    transform: translateY(-2px);
}

.add-to-cart-button:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
}

.quantity-controls {
    display: flex;
    align-items: center;
    gap: 5px;
    flex: 1;
}

.quantity-button {
    background: #3498db;
    color: white;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.quantity-button:hover {
    background: #2980b9;
}

.quantity {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    min-width: 30px;
    text-align: center;
}

.wishlist-button {
    background: #fff;
    border: 1px solid #27ae60;
    border-radius: 8px;
    padding: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #27ae60;
    cursor: pointer;
    transition: background 0.3s ease, color 0.3s ease;
}

.wishlist-button.active {
    background: #27ae60;
    color: #fff;
}

.wishlist-button:hover:not(.active) {
    background: #ecf0f1;
}

.heart-icon {
    font-size: 18px;
}

.no-data {
    color: #7f8c8d;
    text-align: center;
    font-size: 18px;
    font-weight: 500;
    padding: 20px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
</style>