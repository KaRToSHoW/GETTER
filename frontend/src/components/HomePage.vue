<template>
    <div class="home-container">
        <ToastNotification ref="toast" />
        <!-- Административная панель -->
        <AdminPanel 
            v-if="currentUser && currentUser.is_superuser"
            @product-created="loadData"
            @category-created="loadData"
        />

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

        <div class="advantages-section">
            <h2 class="home-title">Наши преимущества</h2>
            <div class="advantages-container">
                <div class="advantage-card">
                    <div class="advantage-icon">🚚</div>
                    <h3>Быстрая доставка</h3>
                    <p>Доставка на следующий день по всей России</p>
                </div>
                <div class="advantage-card">
                    <div class="advantage-icon">🔄</div>
                    <h3>Возврат без вопросов</h3>
                    <p>30 дней на возврат без объяснения причин</p>
                </div>
                <div class="advantage-card">
                    <div class="advantage-icon">🛡️</div>
                    <h3>Гарантия качества</h3>
                    <p>Все товары проходят тщательную проверку</p>
                </div>
                <div class="advantage-card">
                    <div class="advantage-icon">📱</div>
                    <h3>Поддержка 24/7</h3>
                    <p>Наша служба поддержки всегда на связи</p>
                </div>
            </div>
        </div>

        <h2 class="home-title">Категории</h2>
        <div class="categories-container">
            <button class="nav-button prev-button categories-prev">❮</button>
            <swiper class="categories-swiper"
                :modules="modules"
                :slides-per-view="slidesPerView.categories"
                :space-between="20"
                :navigation="{
                    nextEl: '.categories-next',
                    prevEl: '.categories-prev'
                }"
                @swiper="onCategoriesSwiper">
                <swiper-slide v-for="category in categories" :key="category.id">
                    <div class="category-card">
                        <router-link :to="`/category/${category.id}`" class="category-link">
                            <div class="category-image-wrapper">
                                <img :src="category.image || defaultCategoryImage" :alt="`Category ${category.name}`"
                                    class="category-image" />
                            </div>
                            <h3 class="category-name">{{ category.name }}</h3>
                        </router-link>
                    </div>
                </swiper-slide>
            </swiper>
            <button class="nav-button next-button categories-next">❯</button>
            <p v-if="categories.length === 0" class="no-data">Нет доступных категорий.</p>
        </div>

        <h2 class="home-title" id="popular-products">Популярные товары</h2>
        <div class="products-container">
            <button class="nav-button prev-button popular-prev">❮</button>
            <swiper class="products-swiper"
                :modules="modules"
                :slides-per-view="slidesPerView.products"
                :space-between="20"
                :navigation="{
                    nextEl: '.popular-next',
                    prevEl: '.popular-prev'
                }"
                @swiper="onPopularSwiper">
                <swiper-slide v-for="product in popularProducts" :key="product.id">
                    <div class="product-card">
                        <div class="bestseller-badge">Хит продаж</div>
                        <router-link :to="`/product/${product.id}`" class="product-link">
                            <div class="image-wrapper">
                                <img :src="product.image || defaultImage" class="product-image" />
                                <div v-if="product.discount > 0" class="discount-tag">-{{ product.discount }}%</div>
                            </div>
                        </router-link>
                        <div class="product-content">
                            <h3>{{ product.name }}</h3>
                            <div class="rating" v-if="product.average_rating">
                                <span class="stars">
                                    <span v-for="i in 5" :key="i" :class="['star', i <= Math.round(product.average_rating) ? 'filled' : '']">★</span>
                                </span>
                                <span class="rating-value">{{ product.average_rating ? product.average_rating.toFixed(1) : '0.0' }}</span>
                            </div>
                            <div class="price-container">
                                <p v-if="product.discount > 0" class="old-price"><s>{{ product.price }} ₽</s></p>
                                <p class="price">{{ product.discounted_price }} ₽</p>
                            </div>
                            <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                                <span>{{ product.is_available ? 'В наличии' : 'Нет в наличии' }}</span>
                                <span class="stock">Осталось: {{ product.stock }} шт.</span>
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
                </swiper-slide>
            </swiper>
            <button class="nav-button next-button popular-next">❯</button>
            <p v-if="popularProducts.length === 0" class="no-data">Нет популярных товаров.</p>
        </div>

        <h2 class="home-title">Новинки</h2>
        <div class="products-container">
            <button class="nav-button prev-button new-prev">❮</button>
            <swiper class="products-swiper"
                :modules="modules"
                :slides-per-view="slidesPerView.products"
                :space-between="20"
                :navigation="{
                    nextEl: '.new-next',
                    prevEl: '.new-prev'
                }"
                @swiper="onNewProductsSwiper">
                <swiper-slide v-for="product in newProducts" :key="product.id">
                    <div class="product-card">
                        <div class="new-badge">Новинка</div>
                        <router-link :to="`/product/${product.id}`" class="product-link">
                            <div class="image-wrapper">
                                <img :src="product.image || defaultImage" class="product-image" />
                                <div v-if="product.discount > 0" class="discount-tag">-{{ product.discount }}%</div>
                            </div>
                        </router-link>
                        <div class="product-content">
                            <h3>{{ product.name }}</h3>
                            <div class="rating" v-if="product.average_rating">
                                <span class="stars">
                                    <span v-for="i in 5" :key="i" :class="['star', i <= Math.round(product.average_rating) ? 'filled' : '']">★</span>
                                </span>
                                <span class="rating-value">{{ product.average_rating ? product.average_rating.toFixed(1) : '0.0' }}</span>
                            </div>
                            <div class="price-container">
                                <p v-if="product.discount > 0" class="old-price"><s>{{ product.price }} ₽</s></p>
                                <p class="price">{{ product.discounted_price }} ₽</p>
                            </div>
                            <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                                <span>{{ product.is_available ? 'В наличии' : 'Нет в наличии' }}</span>
                                <span class="stock">Осталось: {{ product.stock }} шт.</span>
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
                </swiper-slide>
            </swiper>
            <button class="nav-button next-button new-next">❯</button>
            <p v-if="newProducts.length === 0" class="no-data">Нет новых поступлений.</p>
        </div>

        <h2 class="home-title">Различные товары</h2>
        <div class="products-container">
            <button class="nav-button prev-button products-prev">❮</button>
            <swiper class="products-swiper"
                :modules="modules"
                :slides-per-view="slidesPerView.products"
                :space-between="20"
                :navigation="{
                    nextEl: '.products-next',
                    prevEl: '.products-prev'
                }"
                @swiper="onProductsSwiper">
                <swiper-slide v-for="product in products" :key="product.id">
                    <div class="product-card">
                        <router-link :to="`/product/${product.id}`" class="product-link">
                            <div class="image-wrapper">
                                <img :src="product.image || defaultImage" class="product-image" />
                                <div v-if="product.discount > 0" class="discount-tag">-{{ product.discount }}%</div>
                            </div>
                        </router-link>
                        <div class="product-content">
                            <h3>{{ product.name }}</h3>
                            <div class="rating" v-if="product.average_rating">
                                <span class="stars">
                                    <span v-for="i in 5" :key="i" :class="['star', i <= Math.round(product.average_rating) ? 'filled' : '']">★</span>
                                </span>
                                <span class="rating-value">{{ product.average_rating ? product.average_rating.toFixed(1) : '0.0' }}</span>
                            </div>
                            <div class="price-container">
                                <p v-if="product.discount > 0" class="old-price"><s>{{ product.price }} ₽</s></p>
                                <p class="price">{{ product.discounted_price }} ₽</p>
                            </div>
                            <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                                <span>{{ product.is_available ? 'В наличии' : 'Нет в наличии' }}</span>
                                <span class="stock">Осталось: {{ product.stock }} шт.</span>
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
                </swiper-slide>
            </swiper>
            <button class="nav-button next-button products-next">❯</button>
            <p v-if="products.length === 0" class="no-data">Нет доступных товаров.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Pagination, Navigation } from 'swiper/modules';

import defaultImage from '@/assets/img/Default_product_foto.jpg';
import defaultCategoryImage from '@/assets/img/Default_product_foto.jpg';
import ToastNotification from './ToastNotification.vue';
import AdminPanel from './admin/AdminPanel.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

const categories = ref([]);
const products = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const modules = ref([Pagination, Navigation]);
const swiperInstance = ref(null);
const categoriesSwiperInstance = ref(null);
const productsSwiperInstance = ref(null);
const toast = ref(null);
const currentUser = ref(null);
const slidesPerView = ref({
    categories: 5,
    products: 4
});

// Добавляем переменные для новых секций
const popularProducts = ref([]);
const newProducts = ref([]);
const popularSwiperInstance = ref(null);
const newProductsSwiperInstance = ref(null);

// Функция обновления slidesPerView в зависимости от размера экрана
const updateSlidesPerView = () => {
    const width = window.innerWidth;
    if (width < 480) {
        slidesPerView.value.categories = 1;
        slidesPerView.value.products = 1;
    } else if (width < 768) {
        slidesPerView.value.categories = 2;
        slidesPerView.value.products = 2;
    } else if (width < 992) {
        slidesPerView.value.categories = 3;
        slidesPerView.value.products = 3;
    } else {
        slidesPerView.value.categories = 5;
        slidesPerView.value.products = 4;
    }
};

onMounted(async () => {
    await loadCurrentUser();
    await loadData();
    
    // Вызываем функцию обновления при загрузке страницы
    updateSlidesPerView();
    
    // Слушаем изменение размера окна
    window.addEventListener('resize', updateSlidesPerView);
});

// Очистка слушателя при размонтировании компонента


const loadCurrentUser = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get(`${API_BASE_URL}/users/profile/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            currentUser.value = response.data;
            console.log('Текущий пользователь:', currentUser.value);
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля пользователя:', error);
    }
};

const loadData = async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        // Базовые запросы на данные всегда выполняются
        const [categoriesResponse, productsResponse, popularProductsResponse, newProductsResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/main/categories/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/popular/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/new/`, { headers })
        ]);

        categories.value = categoriesResponse.data;
        products.value = productsResponse.data;
        
        // Используем данные из новых API-эндпоинтов
        popularProducts.value = popularProductsResponse.data;
        newProducts.value = newProductsResponse.data;
        
        // Запросы, зависящие от авторизации
        if (token) {
            try {
                // Загрузка списка желаемого
                const wishlistResponse = await axios.get(`${API_BASE_URL}/main/wishlist/check/`, { headers });
                wishlist.value = wishlistResponse.data.wishlist || [];
                
                // Загрузка корзины
                const cartResponse = await axios.get(`${API_BASE_URL}/main/cart/`, { headers });
                const cartData = cartResponse.data;
                
                // Обработка данных корзины
                if (Array.isArray(cartData)) {
                    cartData.forEach(item => {
                        cartItems.value[item.product.id] = item.quantity;
                    });
                } else if (cartData && cartData.items && Array.isArray(cartData.items)) {
                    cartData.items.forEach(item => {
                        cartItems.value[item.product.id] = item.quantity;
                    });
                }
            } catch (authError) {
                console.error('Ошибка загрузки данных для авторизованного пользователя:', authError);
                // Сбрасываем токен, если он недействителен
                if (authError.response && authError.response.status === 401) {
                    localStorage.removeItem('token');
                    toast.value.showToast('Сессия истекла, пожалуйста, войдите снова', 'warning');
                }
            }
        } else {
            // Если пользователь не авторизован, сбрасываем данные
            wishlist.value = [];
            cartItems.value = {};
        }
    } catch (error) {
        console.error('Ошибка загрузки данных:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при загрузке данных. Попробуйте позже.', 'error');
    }
};

const onSwiper = (swiper) => {
    swiperInstance.value = swiper;
};

const onCategoriesSwiper = (swiper) => {
    categoriesSwiperInstance.value = swiper;
};

const onProductsSwiper = (swiper) => {
    productsSwiperInstance.value = swiper;
};

const onSlideChange = () => {
    console.log('Слайд изменен', swiperInstance.value.activeIndex);
};

const onPopularSwiper = (swiper) => {
    popularSwiperInstance.value = swiper;
};

const onNewProductsSwiper = (swiper) => {
    newProductsSwiperInstance.value = swiper;
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
    width: 100%;
    box-sizing: border-box;
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
    font-size: 32px;
    color: #2c3e50;
    margin: 40px 0 30px;
    text-align: center;
    font-weight: 800;
    position: relative;
    padding-bottom: 15px;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.home-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #6b46c1 0%, #805ad5 100%);
    border-radius: 2px;
}

.home-title::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 1px;
    background: #e2e8f0;
}

.advantages-section {
    margin-bottom: 40px;
}

.advantages-container {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    padding: 20px 0;
    flex-wrap: wrap;
}

.advantage-card {
    background: linear-gradient(135deg, #ffffff, #f9f9f9);
    border-radius: 16px;
    padding: 30px 20px;
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.1);
    transition: all 0.3s ease;
    text-align: center;
    flex: 1;
    position: relative;
}

.advantage-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(107, 70, 193, 0.2);
}

.advantage-icon {
    font-size: 36px;
    margin-bottom: 15px;
}

.advantage-card h3 {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 10px;
}

.advantage-card p {
    font-size: 14px;
    color: #7f8c8d;
    margin: 0;
}

.categories-container, .products-container {
    position: relative;
    margin-bottom: 40px;
}

.categories-container .swiper, .products-container .swiper {
    padding: 0 10px;
    margin: 0 -10px;
}

.swiper-slide {
    height: auto;
}

.swiper-button-disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.nav-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #f0f0f0;
}

.nav-button {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    transition: background 0.3s ease, border-color 0.3s ease;
}

.nav-button:hover {
    background: #f0f0f0;
    border-color: #bbb;
}

.prev-button {
    left: -20px;
}

.next-button {
    right: -20px;
}

.categories-swiper, .products-swiper {
    padding: 20px 0;
    display: flex;
    flex-direction: row;
}

.category-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.1);
    transition: all 0.3s ease;
    position: relative;
    height: 220px;
    cursor: pointer;
}

.category-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 24px rgba(107, 70, 193, 0.2);
}

.category-card::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0) 100%);
    z-index: 1;
}

.category-link {
    text-decoration: none;
    display: block;
    height: 100%;
    position: relative;
    padding: 0;
}

.category-image-wrapper {
    width: 100%;
    height: 100%;
    position: relative;
    overflow: hidden;
}

.category-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.category-card:hover .category-image {
    transform: scale(1.1);
}

.category-name {
    position: absolute;
    bottom: 15px;
    left: 15px;
    right: 15px;
    color: #ffffff;
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    text-align: left;
    z-index: 2;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.categories-container {
    padding: 20px 0;
}

.categories-container .nav-button {
    background: rgba(255, 255, 255, 0.9);
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    width: 44px;
    height: 44px;
    transition: all 0.3s ease;
}

.categories-container .nav-button:hover {
    background: #6b46c1;
    color: white;
    transform: translateY(-50%) scale(1.1);
}

.categories-container .nav-button:disabled {
    background: rgba(255, 255, 255, 0.5);
    color: #999;
    box-shadow: none;
    transform: translateY(-50%);
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
    height: 100%;
    position: relative;
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

.product-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.product-card:hover .product-image {
    transform: scale(1.05);
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

/* Адаптивные стили для мобильных устройств */
@media (max-width: 992px) {
    .home-title {
        font-size: 28px;
        margin: 30px 0 20px;
    }
    
    .nav-button {
        width: 36px;
        height: 36px;
    }
    
    .prev-button {
        left: -10px;
    }
    
    .next-button {
        right: -10px;
    }
}

@media (max-width: 768px) {
    .home-container {
        padding: 15px;
    }
    
    .promo-banner {
        flex-direction: column;
        padding: 15px;
        text-align: center;
        min-height: auto;
    }
    
    .promo-text {
        order: 1;
        margin-bottom: 15px;
    }
    
    .promo-image {
        order: 2;
        margin: 0 0 15px 0;
    }
    
    .nav-arrow {
        display: none;
    }
    
    .home-title {
        font-size: 24px;
        margin: 25px 0 20px;
    }
    
    .home-title::after {
        width: 50px;
        height: 3px;
    }
    
    .home-title::before {
        width: 100px;
    }
    
    .category-card {
        height: 180px;
    }
    
    .category-name {
        font-size: 18px;
    }
    
    .product-card h3 {
        font-size: 16px;
    }
    
    .price {
        font-size: 20px;
    }
    
    .old-price {
        font-size: 12px;
    }
    
    .button-group {
        padding: 10px;
    }
    
    .add-to-cart-button, .wishlist-button {
        padding: 8px;
        font-size: 13px;
    }
    
    .quantity-button {
        width: 26px;
        height: 26px;
        font-size: 14px;
    }
    
    .advantages-container {
        flex-direction: column;
    }
    
    .advantage-card {
        margin-bottom: 10px;
    }
}

@media (max-width: 480px) {
    .home-container {
        padding: 10px;
    }
    
    .discount {
        font-size: 18px;
    }
    
    .promo-image {
        width: 120px;
    }
    
    .home-title {
        font-size: 20px;
        margin: 20px 0 15px;
        letter-spacing: 1px;
    }
    
    .categories-container, .products-container {
        margin-bottom: 25px;
    }
    
    .category-card {
        height: 160px;
    }
    
    .category-name {
        font-size: 16px;
        bottom: 10px;
        left: 10px;
    }
    
    .image-wrapper {
        height: 160px;
    }
    
    .product-content {
        padding: 10px;
    }
    
    .button-group {
        gap: 5px;
    }
    
    .wishlist-button {
        padding: 8px;
    }
    
    .heart-icon {
        font-size: 16px;
    }
    
    .no-data {
        font-size: 16px;
        padding: 15px;
    }
}

.bestseller-badge, .new-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 6px 12px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    z-index: 5;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.bestseller-badge {
    background: linear-gradient(135deg, #ff7700, #ff9900);
    color: white;
}

.new-badge {
    background: linear-gradient(135deg, #6b46c1, #9f7aea);
    color: white;
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

.rating {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 5px;
}

.stars {
    display: inline-flex;
    margin-right: 5px;
}

.star {
    color: #ccc;
    font-size: 18px;
}

.star.filled {
    color: #ffc107;
}

.rating-value {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}
</style>