<!-- src/components/ProductPage.vue -->
<template>
    <div class="product-container" v-if="product">
        <ToastNotification ref="toast" />
        <div class="product-header">
            <button @click="goBack" class="back-button">Назад</button>
            <h2 class="product-title">{{ product.name }}</h2>
        </div>
        <div class="product-content">
            <div class="product-image-wrapper">
                <img :src="product.image || defaultImageProduct" :alt="product.name" class="product-image" />
            </div>
            <div class="product-details">
                <div class="price-section">
                    <p class="old-price"><s>{{ (product.price / 0.96).toFixed(2) }} ₽</s></p>
                    <p class="product-price">{{ product.price }} ₽</p>
                    <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                        <span>{{ product.is_available ? 'В наличии' : 'Нет в наличии' }}</span>
                        <span class="stock">Осталось: {{ product.stock }} шт.</span>
                    </div>
                </div>
                <div class="product-specs">
                    <p><strong>Артикул:</strong> {{ product.sku || 'N/A' }}</p>
                    <p><strong>Категория:</strong> {{ product.category ? product.category.name : 'Не указана' }}</p>
                    <div v-if="product.specifications" class="specifications">
                        <h4>Характеристики:</h4>
                        <ul class="specifications-list">
                            <li v-for="(value, key) in product.specifications.specifications" :key="key"
                                class="spec-item">
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
        </div>
        <div class="reviews-section">
            <div class="reviews-header">
                <h3 class="reviews-title">{{ reviews.length }} отзывов</h3>
                <div class="rating-summary">
                    <span class="rating-number">{{ averageRating.toFixed(1) }}</span>
                    <div class="stars">
                        <span v-for="i in 5" :key="i"
                            :class="['star', i <= Math.round(averageRating) ? 'filled' : '']">★</span>
                    </div>
                </div>
            </div>

            <div class="add-review">
                <h4>Оставить отзыв</h4>
                <div class="rating-input">
                    <span v-for="i in 5" :key="i" :class="['star', i <= newRating ? 'filled' : '']"
                        @click="newRating = i">★</span>
                </div>
                <textarea v-model="newComment" placeholder="Ваш отзыв..." class="review-textarea"></textarea>
                <div class="review-fields">
                    <input v-model="reviewPros" placeholder="Плюсы" class="review-input" />
                    <input v-model="reviewCons" placeholder="Минусы" class="review-input" />
                </div>
                <button @click="submitReview" class="submit-review-button">Отправить</button>
            </div>

            <div class="reviews-filters">
                <div class="filter-group">
                    <label>Сортировать по:</label>
                    <select v-model="sortBy" class="filter-select">
                        <option value="date-new">Сначала новые</option>
                        <option value="date-old">Сначала старые</option>
                        <option value="rating-high">Высокий рейтинг</option>
                        <option value="rating-low">Низкий рейтинг</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Фильтр по оценке:</label>
                    <div class="rating-filter">
                        <button v-for="rating in 5" :key="rating"
                            :class="['rating-filter-btn', { active: selectedRating === rating }]"
                            @click="toggleRatingFilter(rating)">
                            {{ rating }}★
                        </button>
                    </div>
                </div>
            </div>

            <div v-if="filteredReviews.length > 0" class="reviews-list">
                <div v-for="review in filteredReviews" :key="review.id" class="review-item">
                    <div class="review-header">
                        <img :src="review.user.profile_image_url ? `${API_BASE_URL}${review.user.profile_image_url}` : defaultImage"
                            alt="User avatar" class="user-avatar">
                        <div class="review-info">
                            <div class="user-name">{{ review.user.username }}</div>
                            <div class="review-date">{{ formatDate(review.created_at) }}</div>
                        </div>
                    </div>
                    <div class="review-rating">
                        <div class="stars">
                            <span v-for="i in 5" :key="i" :class="['star', i <= review.rating ? 'filled' : '']">★</span>
                        </div>
                    </div>
                    <div class="review-content">
                        <div class="review-pros" v-if="review.pros">
                            <strong>Плюсы:</strong> {{ review.pros }}
                        </div>
                        <div class="review-cons" v-if="review.cons">
                            <strong>Минусы:</strong> {{ review.cons }}
                        </div>
                        <div class="review-text">{{ review.comment }}</div>
                        <a href="#" class="read-more" v-if="review.comment && review.comment.length > 200">Читать
                            полностью</a>
                    </div>
                </div>
            </div>
            <p v-else class="no-reviews">{{ selectedRating ? 'Нет отзывов с такой оценкой' : 'Пока нет отзывов' }}</p>
        </div>
    </div>
    <div v-else class="loading">Загрузка...</div>
</template>
<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import defaultImage from '@/assets/img/default_profile_image.png';
import defaultImageProduct from '@/assets/img/Default_product_foto.jpg';
import ToastNotification from './ToastNotification.vue';

const route = useRoute();
const router = useRouter();
const API_BASE_URL = 'http://127.0.0.1:8000';

const product = ref(null);
const reviews = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const newRating = ref(5);
const newComment = ref('');
const toast = ref(null);
const reviewPros = ref('');
const reviewCons = ref('');
const sortBy = ref('date-new');
const selectedRating = ref(null);

onMounted(async () => {
    await loadProductData();
});

const loadProductData = async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const [productResponse, reviewsResponse, wishlistResponse, cartResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/main/products/${route.params.id}/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/${route.params.id}/reviews/`, { headers }).catch(() => ({ data: [] })),
            token ? axios.get(`${API_BASE_URL}/main/wishlist/check/`, { headers }) : Promise.resolve({ data: [] }),
            token ? axios.get(`${API_BASE_URL}/main/cart/`, { headers }) : Promise.resolve({ data: [] })
        ]);

        product.value = productResponse.data;
        reviews.value = reviewsResponse.data || [];
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

        console.log('Загруженный продукт:', product.value);
    } catch (error) {
        console.error('Ошибка загрузки данных товара:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при загрузке данных товара. Проверьте консоль.', 'error');
    }
};

watch(() => route.params.id, () => {
    product.value = null;
    loadProductData();
});

const goBack = () => {
    router.back();
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
        toast.value.showToast('Ошибка при управлении желаемым: ' + (error.response ? JSON.stringify(error.response.data) : error.message), 'error');
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
        toast.value.showToast('Ошибка при добавлении в корзину: ' + (error.response ? JSON.stringify(error.response.data) : error.message), 'error');
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
        toast.value.showToast('Ошибка при увеличении количества: ' + (error.response ? JSON.stringify(error.response.data) : error.message), 'error');
    }
};

const decreaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    try {
        const newQuantity = (cartItems.value[product.id] || 0) - 1;
        if (newQuantity <= 0) {
            // Получаем текущую корзину для определения item_id
            const cartResponse = await axios.get(`${API_BASE_URL}/main/cart/`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            const cartItem = cartResponse.data.items.find(item => item.product.id === product.id);
            if (!cartItem) {
                throw new Error('Позиция не найдена в корзине');
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
        toast.value.showToast('Ошибка при уменьшении количества: ' + (error.response?.data?.error || error.message), 'error');
    }
};

// Вычисление среднего рейтинга
const averageRating = computed(() => {
    if (!reviews.value.length) return 0;
    const sum = reviews.value.reduce((acc, review) => acc + review.rating, 0);
    return sum / reviews.value.length;
});

// Фильтрация и сортировка отзывов
const filteredReviews = computed(() => {
    let filtered = [...reviews.value];

    // Фильтрация по рейтингу
    if (selectedRating.value) {
        filtered = filtered.filter(review => review.rating === selectedRating.value);
    }

    // Сортировка
    switch (sortBy.value) {
        case 'date-new':
            filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            break;
        case 'date-old':
            filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
            break;
        case 'rating-high':
            filtered.sort((a, b) => b.rating - a.rating);
            break;
        case 'rating-low':
            filtered.sort((a, b) => a.rating - b.rating);
            break;
    }

    return filtered;
});

const toggleRatingFilter = (rating) => {
    selectedRating.value = selectedRating.value === rating ? null : rating;
};

const formatDate = (date) => {
    return new Date(date).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
};

// Обновляем функцию отправки отзыва
const submitReview = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        toast.value.showToast('Пожалуйста, войдите в систему для оставления отзыва.', 'warning');
        return;
    }

    try {
        const response = await axios.post(`${API_BASE_URL}/main/products/${route.params.id}/reviews/`, {
            rating: newRating.value,
            comment: newComment.value,
            pros: reviewPros.value,
            cons: reviewCons.value
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        reviews.value = [...reviews.value, response.data];
        newRating.value = 5;
        newComment.value = '';
        reviewPros.value = '';
        reviewCons.value = '';
        toast.value.showToast('Отзыв успешно добавлен!', 'success');
    } catch (error) {
        console.error('Ошибка отправки отзыва:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при отправке отзыва: ' + (error.response ? JSON.stringify(error.response.data) : error.message), 'error');
    }
};
</script>

<style scoped>
.product-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 40px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #fff;
    min-height: 100vh;
}

.product-header {
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 40px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e5e5e5;
}

.back-button {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #666;
    font-size: 15px;
    font-weight: 500;
    text-decoration: none;
    transition: color 0.2s;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
}

.back-button:before {
    content: "←";
    font-size: 18px;
}

.back-button:hover {
    color: #000;
}

.product-title {
    font-size: 32px;
    color: #1d1d1f;
    margin: 0;
    font-weight: 600;
    letter-spacing: -0.5px;
}

.product-content {
    display: grid;
    grid-template-columns: minmax(500px, 45%) 1fr;
    gap: 60px;
    align-items: start;
    margin: 40px 0;
    background: #fff;
    border-radius: 24px;
    padding: 32px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.product-image-wrapper {
    position: relative;
    width: 100%;
    aspect-ratio: 1;
    border-radius: 24px;
    background: #f5f5f7;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.product-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 32px;
    transition: transform 0.3s ease;
}

.product-image:hover {
    transform: scale(1.02);
}

.product-details {
    display: flex;
    flex-direction: column;
    gap: 32px;
    padding: 0;
}

.price-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 24px;
    background: #f5f5f7;
    border-radius: 16px;
}

.old-price {
    font-size: 18px;
    color: #86868b;
    text-decoration: line-through;
    margin: 0;
}

.product-price {
    font-size: 48px;
    color: #1d1d1f;
    font-weight: 700;
    margin: 0;
    line-height: 1;
}

.availability {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.availability span {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    color: #1d1d1f;
}

.availability span:first-child {
    font-weight: 500;
}

.availability span:first-child::before {
    content: "";
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #30d158;
    box-shadow: 0 0 0 2px rgba(48, 209, 88, 0.2);
}

.out-of-stock span:first-child::before {
    background: #ff3b30;
    box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.2);
}

.stock {
    font-size: 14px;
    color: #86868b;
}

.product-info {
    display: grid;
    gap: 16px;
    padding: 24px;
    background: #f5f5f7;
    border-radius: 16px;
}

.product-info-item {
    display: flex;
    gap: 16px;
    padding: 12px;
    background: white;
    border-radius: 12px;
    transition: background-color 0.2s;
}

.product-info-item:hover {
    background: #f9f9f9;
}

.button-group {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 16px;
    margin-top: auto;
}

.quantity-controls {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 8px;
    background: #f5f5f7;
    border-radius: 12px;
    width: fit-content;
}

.quantity-button {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: none;
    background: white;
    color: #1d1d1f;
    font-size: 20px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.quantity-button:hover {
    background: #f0f0f0;
    transform: scale(1.05);
}

.quantity {
    font-size: 18px;
    font-weight: 600;
    color: #1d1d1f;
    min-width: 40px;
    text-align: center;
}

.add-to-cart-button {
    height: 56px;
    background: #0071e3;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 17px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.wishlist-button {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    border: none;
    background: #f5f5f7;
    color: #ff3b30;
    font-size: 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.specifications {
    margin-top: 10px;
    padding: 3px 0 10px 0;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.wishlist-button:hover {
    background: #fef2f2;
    transform: translateY(-1px);
}

.wishlist-button.active {
    background: #fef2f2;
    color: #ff3b30;
}

.wishlist-button .heart-icon {
    transition: transform 0.3s;
}

.wishlist-button:hover .heart-icon {
    transform: scale(1.1);
}

.wishlist-button.active .heart-icon {
    animation: heartBeat 1.2s ease-in-out;
}

@keyframes heartBeat {
    0% {
        transform: scale(1);
    }

    14% {
        transform: scale(1.3);
    }

    28% {
        transform: scale(1);
    }

    42% {
        transform: scale(1.3);
    }

    70% {
        transform: scale(1);
    }
}

.reviews-section {
    margin-top: 40px;
    padding: 24px;
    background: #eef1ff;
    border-radius: 12px;
}

.reviews-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.reviews-title {
    font-size: 20px;
    color: #1d1d1f;
    font-weight: 600;
    margin: 0;
}

.rating-summary {
    display: flex;
    align-items: center;
    gap: 8px;
}

.rating-number {
    font-size: 20px;
    font-weight: 600;
    color: #1d1d1f;
}

.stars {
    display: flex;
    gap: 2px;
}

.star {
    color: #d2d2d7;
    font-size: 20px;
}

.star.filled {
    color: #8b5cf6;
}

.reviews-list {
    display: grid;
    gap: 16px;
}

.review-item {
    background: white;
    padding: 16px;
    border-radius: 12px;
    display: grid;
    gap: 12px;
}

.review-header {
    display: flex;
    gap: 12px;
    align-items: center;
}

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.review-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.user-name {
    font-weight: 500;
    color: #1d1d1f;
}

.review-date {
    font-size: 12px;
    color: #86868b;
}

.review-rating {
    margin: 8px 0;
}

.review-content {
    display: grid;
    gap: 12px;
    color: #1d1d1f;
    font-size: 14px;
}

.review-pros,
.review-cons {
    margin: 0;
    padding: 12px;
    border-radius: 8px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.review-pros {
    background: #f0fdf4;
    color: #166534;
}

.review-cons {
    background: #fef2f2;
    color: #991b1b;
}

.review-pros::before,
.review-cons::before {
    content: '';
    display: inline-block;
    width: 20px;
    height: 20px;
    background-size: contain;
    background-repeat: no-repeat;
    flex-shrink: 0;
}

.review-pros::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23166534'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z'/%3E%3C/svg%3E");
}

.review-cons::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23991b1b'%3E%3Cpath d='M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z'/%3E%3C/svg%3E");
}

.review-text {
    color: #1d1d1f;
    font-size: 14px;
    line-height: 1.5;
    margin-top: 8px;
    padding: 12px;
    background: #f5f5f7;
    border-radius: 8px;
}

.read-more {
    color: #8b5cf6;
    text-decoration: none;
    font-size: 14px;
    margin-top: 8px;
}

.read-more:hover {
    text-decoration: underline;
}

.rating-input {
    display: flex;
    gap: 4px;
}

.rating-input .star {
    cursor: pointer;
    transition: transform 0.2s;
}

.rating-input .star:hover {
    transform: scale(1.2);
}

.review-textarea {
    padding: 12px;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    font-size: 14px;
    min-height: 120px;
    resize: vertical;
    background: white;
    width: 100%;
}

.submit-review-button {
    background: #8b5cf6;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
}

.submit-review-button:hover {
    background: #7c3aed;
}

.loading {
    text-align: center;
    font-size: 16px;
    color: #86868b;
    padding: 40px;
}

.reviews-filters {
    margin: 24px 0;
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 12px;
}

.filter-group label {
    color: #1d1d1f;
    font-size: 14px;
    font-weight: 500;
}

.filter-select {
    padding: 8px 12px;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    background: white;
    font-size: 14px;
    color: #1d1d1f;
}

.rating-filter {
    display: flex;
    gap: 8px;
}

.rating-filter-btn {
    padding: 6px 12px;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    background: white;
    color: #1d1d1f;
    cursor: pointer;
    transition: all 0.2s;
}

.rating-filter-btn.active {
    background: #8b5cf6;
    color: white;
    border-color: #8b5cf6;
}

.review-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
}

.review-input {
    padding: 12px;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    font-size: 14px;
    width: 100%;
}

.add-review {
    background: white;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
}

@media (max-width: 1200px) {
    .product-content {
        grid-template-columns: 1fr;
        gap: 40px;
    }

    .product-image-wrapper {
        max-width: 600px;
        margin: 0 auto;
    }

    .product-details {
        max-width: 600px;
        margin: 0 auto;
        width: 100%;
    }
}

@media (max-width: 768px) {
    .product-container {
        padding: 20px;
    }

    .product-content {
        padding: 20px;
    }

    .button-group {
        grid-template-columns: 1fr;
    }

    .wishlist-button {
        width: 100%;
    }

    .product-price {
        font-size: 36px;
    }
}

@media (max-width: 480px) {
    .product-container {
        padding: 16px;
    }

    .product-content {
        padding: 16px;
    }

    .quantity-controls {
        width: 100%;
        justify-content: space-between;
    }
}
</style>