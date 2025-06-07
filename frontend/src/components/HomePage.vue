<template>
    <div class="home-container">
        <ToastNotification ref="toast" />
        <!-- Административная панель -->
        <AdminPanel 
            v-if="currentUser && currentUser.is_superuser"
            @product-created="loadData"
            @category-created="loadData"
        />

        <!-- Улучшенная карусель с акциями -->
        <div class="promo-carousel-container">
            <swiper 
                :modules="modules" 
                :pagination="{ 
                    clickable: true,
                    dynamicBullets: true
                }" 
                :navigation="{
                    nextEl: '.promo-next',
                    prevEl: '.promo-prev'
                }"
                :autoplay="{
                    delay: 5000,
                    disableOnInteraction: false
                }"
                :effect="'creative'" 
                :creative-effect="{
                    prev: {
                        shadow: true,
                        translate: ['-20%', 0, -1]
                    },
                    next: {
                        translate: ['100%', 0, 0]
                    }
                }"
                :loop="true"
                class="promo-swiper" 
                @swiper="onPromoSwiper"
            @slideChange="onSlideChange">
                <swiper-slide class="promo-slide">
                <div class="promo-banner">
                        <div class="promo-content">
                            <span class="promo-label">Акция месяца</span>
                            <h2 class="promo-title">Умная колонка</h2>
                            <p class="promo-text">Мощный звук и современный дизайн</p>
                            <p class="promo-discount">СКИДКА 30% ПРИ ПОКУПКЕ КОМПЛЕКТА</p>
                            <button class="promo-button">Подробнее</button>
                    </div>
                        <div class="promo-image-container">
                            <div class="promo-icon-wrapper">
                                <div class="icon-speaker">
                                    <div class="speaker-body"></div>
                                    <div class="speaker-base"></div>
                                    <div class="speaker-waves speaker-wave-1"></div>
                                    <div class="speaker-waves speaker-wave-2"></div>
                                    <div class="speaker-waves speaker-wave-3"></div>
                                </div>
                                <div class="icon-glow"></div>
                            </div>
                            <div class="promo-badge">-30%</div>
                        </div>
                        <div class="promo-decoration promo-circles"></div>
                </div>
            </swiper-slide>
                <swiper-slide class="promo-slide">
                    <div class="promo-banner promo-banner-dark">
                        <div class="promo-content">
                            <span class="promo-label">Новинка</span>
                            <h2 class="promo-title">Беспроводные наушники</h2>
                            <p class="promo-text">Идеальное звучание в любом месте</p>
                            <p class="promo-discount">СКИДКА 20% НА ВСЕ АУДИО</p>
                            <button class="promo-button">Смотреть</button>
                    </div>
                        <div class="promo-image-container">
                            <div class="promo-icon-wrapper">
                                <div class="icon-headphones">
                                    <div class="headphone-band"></div>
                                    <div class="headphone-ear headphone-left">
                                        <div class="ear-pad"></div>
                                    </div>
                                    <div class="headphone-ear headphone-right">
                                        <div class="ear-pad"></div>
                                    </div>
                                    <div class="music-note note-1">♪</div>
                                    <div class="music-note note-2">♫</div>
                                    <div class="music-note note-3">♩</div>
                                </div>
                                <div class="icon-glow icon-glow-dark"></div>
                            </div>
                            <div class="promo-badge">-20%</div>
                        </div>
                        <div class="promo-decoration promo-waves"></div>
                </div>
            </swiper-slide>
                <swiper-slide class="promo-slide">
                    <div class="promo-banner promo-banner-gradient">
                        <div class="promo-content">
                            <span class="promo-label">Специальное предложение</span>
                            <h2 class="promo-title">Игровой ноутбук</h2>
                            <p class="promo-text">Максимальная производительность</p>
                            <p class="promo-discount">СКИДКА 15% + ИГРОВАЯ МЫШЬ В ПОДАРОК</p>
                            <button class="promo-button">Выбрать</button>
                    </div>
                        <div class="promo-image-container">
                            <div class="promo-icon-wrapper">
                                <div class="icon-laptop">
                                    <div class="laptop-base">
                                        <div class="laptop-keyboard"></div>
                                        <div class="laptop-touchpad"></div>
                                    </div>
                                    <div class="laptop-screen">
                                        <div class="laptop-display">
                                            <div class="laptop-code-line"></div>
                                            <div class="laptop-code-line"></div>
                                            <div class="laptop-code-line"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="icon-glow icon-glow-gradient"></div>
                            </div>
                            <div class="promo-badge">-15%</div>
                        </div>
                        <div class="promo-decoration promo-dots"></div>
                </div>
            </swiper-slide>
                <div class="swiper-button-next promo-next"></div>
                <div class="swiper-button-prev promo-prev"></div>
        </swiper>
        </div>

        <div class="advantages-section animated-section" data-section="advantages" :class="{ 'fade-in-up': sectionsVisible.advantages }">
            <h2 class="home-title">Наши преимущества</h2>
            <div class="advantages-container">
                <div class="advantage-card stagger-item">
                    <div class="advantage-icon">🚚</div>
                    <h3>Быстрая доставка</h3>
                    <p>Доставка на следующий день по всей России</p>
                </div>
                <div class="advantage-card stagger-item">
                    <div class="advantage-icon">🔄</div>
                    <h3>Возврат без вопросов</h3>
                    <p>30 дней на возврат без объяснения причин</p>
                </div>
                <div class="advantage-card stagger-item">
                    <div class="advantage-icon">🛡️</div>
                    <h3>Гарантия качества</h3>
                    <p>Все товары проходят тщательную проверку</p>
                </div>
                <div class="advantage-card stagger-item">
                    <div class="advantage-icon">📱</div>
                    <h3>Поддержка 24/7</h3>
                    <p>Наша служба поддержки всегда на связи</p>
                </div>
            </div>
        </div>

        <!-- Недавние отзывы (Новая секция) -->
        <h2 class="home-title">Недавние отзывы</h2>
        <div class="reviews-container animated-section" data-section="reviews" :class="{ 'fade-in-up': sectionsVisible.reviews }">
            <swiper class="reviews-swiper"
                :modules="modules"
                :slides-per-view="slidesPerView.reviews"
                :space-between="20"
                :loop="true"
                :autoplay="{
                    delay: 3000,
                    disableOnInteraction: false,
                    pauseOnMouseEnter: false,
                    waitForTransition: false
                }"
                :speed="600"
                :css-mode="false"
                :effect="'slide'"
                :allow-touch-move="false"
                :simulate-touch="false"
                :touch-ratio="0"
                :no-swiping="true"
                :resistance="false"
                :navigation="false"
                @swiper="onReviewsSwiper">
                <swiper-slide v-for="review in recentReviews" :key="review.id">
                    <div class="review-card">
                        <div class="review-header">
                            <div class="user-info">
                                <div class="user-avatar">
                                    <img :src="getImageUrl(review.user.profile_image)" :alt="review.user.username" />
                                </div>
                                <div class="user-name">{{ review.user.username }}</div>
                            </div>
                            <div class="review-date">{{ formatDate(review.created_at) }}</div>
                        </div>
                        <div class="product-info">
                            <router-link :to="`/product/${review.product.id}`" class="product-link">
                                <div class="product-image-small">
                                    <img :src="getImageUrl(review.product.image)" :alt="review.product.name" />
                                </div>
                                <div class="product-name-small">{{ review.product.name }}</div>
                            </router-link>
                        </div>
                        <div class="review-rating">
                            <span class="stars">
                                <span v-for="i in 5" :key="i" :class="['star', i <= Math.round(review.rating) ? 'filled' : '']">★</span>
                            </span>
                            <span class="rating-value">{{ review.rating }}</span>
                        </div>
                        <div v-if="review.pros" class="review-pros">
                            <strong>Плюсы:</strong> {{ review.pros }}
                        </div>
                        <div v-if="review.cons" class="review-cons">
                            <strong>Минусы:</strong> {{ review.cons }}
                        </div>
                        <div v-if="review.comment" class="review-text">{{ review.comment }}</div>
                    </div>
                </swiper-slide>
            </swiper>
        </div>

        <h2 class="home-title">Категории</h2>
        <div class="categories-container animated-section" data-section="categories" :class="{ 'fade-in-up': sectionsVisible.categories }">
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
        <div class="products-container animated-section" data-section="popularProducts" :class="{ 'fade-in-up': sectionsVisible.popularProducts }">
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
        <div class="products-container animated-section" data-section="newProducts" :class="{ 'fade-in-up': sectionsVisible.newProducts }">
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
        <div class="products-container animated-section" data-section="products" :class="{ 'fade-in-up': sectionsVisible.products }">
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
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Pagination, Navigation, Autoplay, EffectCreative } from 'swiper/modules';

import defaultImage from '@/assets/img/Default_product_foto.jpg';
import defaultCategoryImage from '@/assets/img/Default_product_foto.jpg';
import defaultProfileImage from '@/assets/img/default_profile_image.png';
import ToastNotification from './ToastNotification.vue';
import AdminPanel from './admin/AdminPanel.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

const categories = ref([]);
const products = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const modules = ref([Pagination, Navigation, Autoplay, EffectCreative]);

const promoSwiperInstance = ref(null);
const categoriesSwiperInstance = ref(null);
const productsSwiperInstance = ref(null);
const toast = ref(null);
const currentUser = ref(null);
const slidesPerView = ref({
    categories: 5,
    products: 4,
    reviews: 3
});

// Добавляем переменные для новых секций
const popularProducts = ref([]);
const newProducts = ref([]);
const recentReviews = ref([]);
const popularSwiperInstance = ref(null);
const newProductsSwiperInstance = ref(null);
const reviewsSwiperInstance = ref(null);

// Состояния для отслеживания анимаций секций
const sectionsVisible = ref({
    advantages: false,
    categories: false,
    popularProducts: false,
    newProducts: false,
    products: false,
    reviews: false
});

// Функция обновления slidesPerView в зависимости от размера экрана
const updateSlidesPerView = () => {
    const width = window.innerWidth;
    if (width < 480) {
        slidesPerView.value.categories = 1;
        slidesPerView.value.products = 1;
        slidesPerView.value.reviews = 1;
    } else if (width < 768) {
        slidesPerView.value.categories = 2;
        slidesPerView.value.products = 2;
        slidesPerView.value.reviews = 1;
    } else if (width < 992) {
        slidesPerView.value.categories = 3;
        slidesPerView.value.products = 3;
        slidesPerView.value.reviews = 2;
    } else {
        slidesPerView.value.categories = 5;
        slidesPerView.value.products = 4;
        slidesPerView.value.reviews = 3;
    }
};

// Функция для обработки анимаций при прокрутке (обновляем существующий код слушателя)
const setupIntersectionObserver = () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            // Используем флаг для предотвращения повторной обработки
            if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                // Помечаем элемент как анимированный для предотвращения повторной анимации
                entry.target.classList.add('animated');
                
                // Если это заголовок
                if (entry.target.classList.contains('home-title')) {
                    entry.target.classList.remove('title-hidden');
                    
                    // Добавляем анимацию свечения только после завершения анимации появления
                    setTimeout(() => {
                        entry.target.classList.add('animate-line');
                    }, 800);
                    
                    // Добавляем частицы для декоративного эффекта с задержкой
                    setTimeout(() => {
                        createParticles(entry.target);
                    }, 600);
                }
                // Если это секция
                else {
                    const sectionId = entry.target.dataset.section;
                    if (sectionId && Object.hasOwn(sectionsVisible.value, sectionId)) {
                        sectionsVisible.value[sectionId] = true;
                    }
                }
            }
        });
    }, {
        threshold: 0.2, // Показывать анимацию когда 20% элемента видно
        rootMargin: '0px' // Без дополнительных отступов
    });

    // Добавляем все секции под наблюдение
    document.querySelectorAll('.animated-section').forEach(section => {
        observer.observe(section);
    });

    // Наблюдаем за заголовками
    document.querySelectorAll('.home-title').forEach(title => {
        observer.observe(title);
        title.classList.add('title-hidden');
    });

    return observer;
};

let observer = null;

onMounted(async () => {
    await loadCurrentUser();
    await loadData();
    
    // Вызываем функцию обновления при загрузке страницы
    updateSlidesPerView();
    
    // Слушаем изменение размера окна
    window.addEventListener('resize', updateSlidesPerView);
    
    // Устанавливаем наблюдатель за скроллом
    observer = setupIntersectionObserver();
});

// Очистка слушателей при размонтировании компонента
onBeforeUnmount(() => {
    window.removeEventListener('resize', updateSlidesPerView);

    // Отключаем наблюдатель
    if (observer) {
        observer.disconnect();
    }
});

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
        
        // Загрузка последних отзывов
        try {
            const reviewsResponse = await axios.get(`${API_BASE_URL}/main/recent-reviews/`, { headers });
            recentReviews.value = reviewsResponse.data;
        } catch (reviewError) {
            console.error('Ошибка загрузки отзывов:', reviewError);
        }
        
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

// Форматирование даты
const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
};

// Функция для получения правильного URL изображения
const getImageUrl = (imageUrl) => {
    if (!imageUrl) return defaultProfileImage;
    if (imageUrl.startsWith('http')) return imageUrl;
    return `${API_BASE_URL}${imageUrl}`;
};

const onPromoSwiper = (swiper) => {
    promoSwiperInstance.value = swiper;
};

const onCategoriesSwiper = (swiper) => {
    categoriesSwiperInstance.value = swiper;
};

const onProductsSwiper = (swiper) => {
    productsSwiperInstance.value = swiper;
};

const onSlideChange = (swiper) => {
    // Проверяем, что экземпляр swiper существует
    if (swiper && typeof swiper.activeIndex !== 'undefined') {
        console.log('Слайд изменен', swiper.activeIndex);
    }
};

const onPopularSwiper = (swiper) => {
    popularSwiperInstance.value = swiper;
};

const onNewProductsSwiper = (swiper) => {
    newProductsSwiperInstance.value = swiper;
};

const onReviewsSwiper = (swiper) => {
    reviewsSwiperInstance.value = swiper;
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

// Создаем эффект частиц для заголовка
const createParticles = (titleElement) => {
    // Удалим существующие частицы, чтобы предотвратить их накопление
    titleElement.querySelectorAll('.particle').forEach(p => p.remove());
    
    // Количество частиц
    const particleCount = 5;
    
    // Создаем новые частицы
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('span');
        particle.classList.add('particle');
        
        // Добавляем случайное положение по ширине элемента
        const titleWidth = titleElement.offsetWidth;
        const offsetX = Math.random() * titleWidth - titleWidth/2;
        particle.style.left = `calc(50% + ${offsetX}px)`;
        
        // Добавляем случайную задержку
        particle.style.animationDelay = `${Math.random() * 2}s`;
        
        // Случайный размер
        const size = Math.random() * 3 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Добавляем частицу к заголовку
        titleElement.appendChild(particle);
    }
};
</script>

<style scoped>
.home-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Arial', sans-serif;
    background-color: transparent;
    width: 100%;
    box-sizing: border-box;
}

/* Анимации для появления секций */
.animated-section {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-in-up {
    opacity: 1;
    transform: translateY(0);
}

/* Восстановленные и улучшенные стили для заголовков */
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
    transition: all 0.6s ease-out;
}

.title-hidden {
    opacity: 0;
    transform: translateY(20px);
}

/* Восстанавливаем базовую структуру линий и добавляем улучшенные эффекты */
.home-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, 
        rgba(107,70,193,0.3) 0%, 
        #6b46c1 20%, 
        #805ad5 50%, 
        #6b46c1 80%, 
        rgba(107,70,193,0.3) 100%);
    border-radius: 2px;
    box-shadow: 
        0 0 5px rgba(107,70,193,0.5),
        0 0 10px rgba(107,70,193,0.3);
    opacity: 0;
    transform: scaleX(0);
    transform-origin: center;
    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.6s ease;
}

.home-title:not(.title-hidden)::after {
    opacity: 1;
    transform: scaleX(1);
}

.home-title:not(.title-hidden)::before {
    opacity: 1;
    transform: scaleX(1);
}

/* Класс для запуска дополнительных анимаций линий */
.home-title.animate-line::after {
    animation: lineBreathe 3s infinite;
    background-size: 200% 100%;
}

.home-title.animate-line::before {
    animation: lineShimmer 6s infinite linear;
    background-size: 200% 100%;
}

/* Анимации для заголовков */
@keyframes lineBreathe {
    0%, 100% {
        box-shadow: 
            0 0 5px rgba(107,70,193,0.5),
            0 0 10px rgba(107,70,193,0.3);
    }
    50% {
        box-shadow: 
            0 0 8px rgba(107,70,193,0.7),
            0 0 15px rgba(107,70,193,0.5),
            0 0 25px rgba(107,70,193,0.2);
    }
}

@keyframes lineShimmer {
    0% {
        background-position: 0% 0%;
    }
    100% {
        background-position: 100% 0%;
    }
}

/* Стили для "частиц" под линией */
.particle {
    position: absolute;
    bottom: 2px;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #805ad5;
    box-shadow: 0 0 5px #6b46c1;
    animation: particleDrift 2s ease-out forwards;
    opacity: 0;
    pointer-events: none; /* Чтобы частицы не мешали взаимодействию */
    z-index: 2;
}

@keyframes particleDrift {
    0% {
        transform: translateY(0px) translateX(0px);
        opacity: 0;
    }
    20% {
        opacity: 1;
    }
    80% {
        opacity: 0.8;
    }
    100% {
        transform: translateY(-20px) translateX(10px);
        opacity: 0;
    }
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
    
    .promo-carousel-container {
        margin: 20px 0 40px;
    }
    
    .promo-slide {
        height: auto;
    }
    
    .promo-banner {
        flex-direction: column;
        padding: 20px;
        height: auto;
        min-height: 500px;
    }
    
    .promo-content,
    .promo-image-container {
        max-width: 100%;
        width: 100%;
        text-align: center;
    }
    
    .promo-content {
        order: 2;
        padding: 20px 0 0;
    }
    
    .promo-image-container {
        order: 1;
        margin-bottom: 20px;
    }
    
    .promo-title {
        font-size: 24px;
    }
    
    .promo-text {
        font-size: 14px;
        max-width: 100%;
    }
    
    .promo-discount {
        font-size: 16px;
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

.reviews-container {
    position: relative;
    margin: 20px auto;
    max-width: calc(100% - 80px);
}

.reviews-swiper {
    width: 100%;
    margin: 0 auto;
    padding: 20px 0;
}

.review-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    height: 320px;
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
    overflow: hidden;
}

.review-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.user-info {
    display: flex;
    align-items: center;
}

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    margin-right: 10px;
}

.user-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.user-name {
    font-weight: 600;
    font-size: 0.9em;
}

.review-date {
    font-size: 0.8em;
    color: #777;
}

.product-info {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
    margin-bottom: 10px;
}

.product-link {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: inherit;
}

.product-image-small {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    overflow: hidden;
    margin-right: 10px;
}

.product-image-small img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.product-name-small {
    font-weight: 500;
    font-size: 0.9em;
    color: #333;
}

.review-rating {
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

.stars {
    display: inline-block;
    margin-right: 5px;
}

.star {
    color: #ddd;
    font-size: 1.2em;
}

.star.filled {
    color: #ffcc00;
}

.rating-value {
    font-weight: 600;
    font-size: 0.9em;
    color: #333;
}

.review-pros, .review-cons {
    font-size: 0.85em;
    margin-bottom: 8px;
}

.review-pros strong {
    color: #2ecc71;
}

.review-cons strong {
    color: #e74c3c;
}

.review-text {
    font-size: 0.9em;
    line-height: 1.5;
    color: #555;
    margin-top: 10px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}

.reviews-swiper .swiper-wrapper {
    transition-timing-function: linear !important;
    padding: 15px !important;
}

/* Стили для обновленной карусели с акциями */
.promo-carousel-container {
    margin: 20px 0 40px;
    position: relative;
    border-radius: 12px;
    overflow: visible;
}

.promo-swiper {
    width: 100%;
    height: auto;
    border-radius: 12px;
    overflow: hidden;
}

.promo-slide {
    height: 350px;
}

.promo-banner {
    position: relative;
    display: flex;
    height: 100%;
    padding: 30px;
    background: linear-gradient(110deg, #f0f4ff 0%, #e6f0ff 50%, #d4e4ff 100%);
    border-radius: 12px;
    overflow: hidden;
    align-items: center;
    justify-content: space-between;
    z-index: 1;
}

.promo-banner-dark {
    background: linear-gradient(110deg, #292f4c 0%, #1a1f35 50%, #131629 100%);
    color: white;
}

.promo-banner-gradient {
    background: linear-gradient(110deg, #6b46c1 0%, #9254de 50%, #b76eef 100%);
    color: white;
}

.promo-content {
    flex: 1;
    padding: 0 20px;
    max-width: 50%;
    position: relative;
    z-index: 2;
}

.promo-label {
    display: inline-block;
    padding: 5px 12px;
    background-color: rgba(107, 70, 193, 0.2);
    color: #6b46c1;
    font-weight: 600;
    font-size: 14px;
    border-radius: 20px;
    margin-bottom: 15px;
}

.promo-banner-dark .promo-label, .promo-banner-gradient .promo-label {
    background-color: rgba(255, 255, 255, 0.2);
    color: #ffffff;
}

.promo-title {
    font-size: 32px;
    font-weight: 800;
    margin: 0 0 10px;
    line-height: 1.2;
    letter-spacing: -0.5px;
}

.promo-text {
    font-size: 16px;
    opacity: 0.7;
    margin: 0 0 20px;
    font-weight: 500;
    max-width: 90%;
}

.promo-discount {
    font-size: 18px;
    font-weight: 700;
    margin: 10px 0 20px;
    color: #e53e3e;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: inline-block;
    padding: 5px 0;
    border-bottom: 2px dashed #e53e3e;
}

.promo-banner-dark .promo-discount, .promo-banner-gradient .promo-discount {
    color: #ffcc00;
    border-bottom-color: #ffcc00;
}

.promo-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 12px 24px;
    background-color: #6b46c1;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.3);
}

.promo-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(107, 70, 193, 0.4);
}

.promo-banner-dark .promo-button {
    background-color: #ffcc00;
    color: #1a1f35;
    box-shadow: 0 4px 12px rgba(255, 204, 0, 0.3);
}

.promo-banner-dark .promo-button:hover {
    box-shadow: 0 6px 16px rgba(255, 204, 0, 0.4);
}

.promo-banner-gradient .promo-button {
    background-color: white;
    color: #6b46c1;
    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

.promo-banner-gradient .promo-button:hover {
    box-shadow: 0 6px 16px rgba(255, 255, 255, 0.4);
}

.promo-image-container {
    position: relative;
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    max-width: 50%;
    z-index: 2;
}

.promo-image {
    max-width: 100%;
    max-height: 280px;
    object-fit: contain;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    transform: perspective(800px) rotateY(-5deg);
    transition: transform 0.5s ease;
}

.promo-image:hover {
    transform: perspective(800px) rotateY(0);
}

.promo-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background: #e53e3e;
    color: white;
    font-weight: 700;
    padding: 8px 12px;
    border-radius: 50%;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3);
    animation: pulse 2s infinite;
}

.promo-banner-dark .promo-badge {
    background: #ffcc00;
    color: #1a1f35;
    box-shadow: 0 4px 12px rgba(255, 204, 0, 0.3);
}

.promo-banner-gradient .promo-badge {
    background: white;
    color: #6b46c1;
    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}

/* Декоративные элементы */
.promo-decoration {
    position: absolute;
    z-index: 1;
    opacity: 0.4;
    pointer-events: none;
}

.promo-circles {
    width: 200px;
    height: 200px;
    right: 0;
    bottom: 0;
    background-image: radial-gradient(circle at center, #6b46c1 0%, transparent 10%),
                      radial-gradient(circle at 60% 40%, #6b46c1 0%, transparent 10%),
                      radial-gradient(circle at 40% 60%, #6b46c1 0%, transparent 10%),
                      radial-gradient(circle at 80% 20%, #6b46c1 0%, transparent 10%);
    background-size: 30% 30%;
    background-position: 0 0, 33% 33%, 66% 66%, 100% 100%;
    background-repeat: no-repeat;
}

.promo-waves {
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        45deg,
        rgba(255, 255, 255, 0.05),
        rgba(255, 255, 255, 0.05) 15px,
        transparent 15px,
        transparent 30px
    );
}

.promo-dots {
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: radial-gradient(white 1px, transparent 1px);
    background-size: 15px 15px;
}

/* Кнопки навигации */
.promo-swiper .swiper-button-prev,
.promo-swiper .swiper-button-next {
    width: 40px;
    height: 40px;
    background-color: white;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    color: #6b46c1;
    transform: translateY(-50%);
    opacity: 0;
    transition: all 0.3s ease;
}

.promo-carousel-container:hover .swiper-button-prev,
.promo-carousel-container:hover .swiper-button-next {
    opacity: 1;
}

.promo-swiper .swiper-button-prev:after,
.promo-swiper .swiper-button-next:after {
    font-size: 18px;
    font-weight: bold;
}

.promo-swiper .swiper-button-prev:hover,
.promo-swiper .swiper-button-next:hover {
    background-color: #6b46c1;
    color: white;
    transform: translateY(-50%) scale(1.1);
}

.promo-swiper .swiper-pagination {
    bottom: 15px !important;
}

.promo-swiper .swiper-pagination-bullet {
    width: 10px;
    height: 10px;
    background: rgba(255, 255, 255, 0.7);
    opacity: 0.7;
    transition: all 0.3s ease;
}

.promo-swiper .swiper-pagination-bullet-active {
    width: 20px;
    background: #6b46c1;
    border-radius: 5px;
    opacity: 1;
}

/* Стили для иконок акций */
.promo-icon-wrapper {
    position: relative;
    width: 220px;
    height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.icon-glow {
    position: absolute;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(107,70,193,0.3) 0%, rgba(107,70,193,0.1) 50%, rgba(255,255,255,0) 70%);
    filter: blur(15px);
    opacity: 0.8;
    z-index: 1;
    animation: pulse-gentle 4s infinite ease-in-out;
}

.icon-glow-dark {
    background: radial-gradient(circle, rgba(255,204,0,0.3) 0%, rgba(255,204,0,0.1) 50%, rgba(255,255,255,0) 70%);
}

.icon-glow-gradient {
    background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 70%);
}

@keyframes pulse-gentle {
    0%, 100% {
        transform: scale(1);
        opacity: 0.8;
    }
    50% {
        transform: scale(1.1);
        opacity: 0.6;
    }
}

/* Иконка колонки */
.icon-speaker {
    position: relative;
    width: 120px;
    height: 180px;
    z-index: 2;
}

.speaker-body {
    position: absolute;
    width: 100%;
    height: 75%;
    bottom: 0;
    background: linear-gradient(145deg, #6b46c1, #9254de);
    border-radius: 24px;
    box-shadow: 0 10px 20px rgba(107, 70, 193, 0.3);
    overflow: hidden;
}

.speaker-body::before {
    content: '';
    position: absolute;
    width: 60px;
    height: 60px;
    top: 25px;
    left: 30px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
}

.speaker-base {
    position: absolute;
    width: 80%;
    height: 10px;
    bottom: 0;
    left: 10%;
    background: #2d1b54;
    border-radius: 0 0 20px 20px;
}

.speaker-waves {
    position: absolute;
    border: 2px solid rgba(255, 255, 255, 0.5);
    border-radius: 50%;
    opacity: 0;
    transform: scale(0.5);
    animation: wave-emit 2s infinite;
}

.speaker-wave-1 {
    width: 30px;
    height: 30px;
    top: 40px;
    right: 20px;
    animation-delay: 0s;
}

.speaker-wave-2 {
    width: 20px;
    height: 20px;
    top: 45px;
    right: 25px;
    animation-delay: 0.5s;
}

.speaker-wave-3 {
    width: 10px;
    height: 10px;
    top: 50px;
    right: 30px;
    animation-delay: 1s;
}

@keyframes wave-emit {
    0% {
        opacity: 0.8;
        transform: scale(0.5);
    }
    100% {
        opacity: 0;
        transform: scale(1.5);
    }
}

/* Иконка наушников */
.icon-headphones {
    position: relative;
    width: 140px;
    height: 140px;
    z-index: 2;
}

.headphone-band {
    position: absolute;
    width: 120px;
    height: 60px;
    top: 0;
    left: 10px;
    border: 8px solid #ffcc00;
    border-bottom: none;
    border-radius: 60px 60px 0 0;
}

.headphone-ear {
    position: absolute;
    width: 40px;
    height: 60px;
    bottom: 15px;
    background: #ffcc00;
    border-radius: 8px;
}

.headphone-left {
    left: 10px;
}

.headphone-right {
    right: 10px;
}

.ear-pad {
    position: absolute;
    width: 30px;
    height: 30px;
    top: 15px;
    left: 5px;
    background: #1a1f35;
    border-radius: 50%;
}

.music-note {
    position: absolute;
    color: white;
    font-size: 24px;
    font-weight: bold;
    animation: float-note 3s infinite ease-in-out;
}

.note-1 {
    top: 20px;
    left: 60px;
    animation-delay: 0s;
}

.note-2 {
    top: 50px;
    left: 80px;
    font-size: 28px;
    animation-delay: 0.5s;
}

.note-3 {
    top: 30px;
    right: 60px;
    animation-delay: 1s;
}

@keyframes float-note {
    0%, 100% {
        transform: translateY(0);
        opacity: 0.7;
    }
    50% {
        transform: translateY(-15px);
        opacity: 1;
    }
}

/* Иконка ноутбука */
.icon-laptop {
    position: relative;
    width: 160px;
    height: 120px;
    z-index: 2;
    transform-style: preserve-3d;
    transform: perspective(500px) rotateX(10deg);
}

.laptop-base {
    position: absolute;
    width: 160px;
    height: 20px;
    bottom: 0;
    background: linear-gradient(to bottom, #b76eef, #9254de);
    border-radius: 6px;
}

.laptop-keyboard {
    position: absolute;
    width: 140px;
    height: 8px;
    top: 6px;
    left: 10px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
}

.laptop-touchpad {
    position: absolute;
    width: 40px;
    height: 6px;
    top: 7px;
    left: 60px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 3px;
}

.laptop-screen {
    position: absolute;
    width: 150px;
    height: 100px;
    bottom: 18px;
    left: 5px;
    background: #1a1f35;
    border-radius: 6px;
    transform-origin: bottom;
    transform: rotateX(-10deg);
    overflow: hidden;
}

.laptop-display {
    position: absolute;
    width: 140px;
    height: 90px;
    top: 5px;
    left: 5px;
    background: #000;
    overflow: hidden;
}

.laptop-code-line {
    position: absolute;
    height: 2px;
    left: 10px;
    background: #ffcc00;
    animation: type-code 2s infinite;
}

.laptop-code-line:nth-child(1) {
    top: 20px;
    width: 70%;
    animation-delay: 0s;
}

.laptop-code-line:nth-child(2) {
    top: 40px;
    width: 50%;
    animation-delay: 0.5s;
}

.laptop-code-line:nth-child(3) {
    top: 60px;
    width: 80%;
    animation-delay: 1s;
}

@keyframes type-code {
    0% {
        width: 0;
        opacity: 0.3;
    }
    50% {
        opacity: 1;
    }
    90%, 100% {
        opacity: 0.7;
    }
}

@media (max-width: 768px) {
    .promo-icon-wrapper {
        width: 180px;
        height: 180px;
    }
    
    .icon-speaker {
        transform: scale(0.8);
    }
    
    .icon-headphones {
        transform: scale(0.8);
    }
    
    .icon-laptop {
        transform: perspective(500px) rotateX(10deg) scale(0.8);
    }
}
</style>