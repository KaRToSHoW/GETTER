<!-- src/components/ProductPage.vue -->
<template>
    <div class="product-container" v-if="product">
        <div class="product-header">
            <button @click="goBack" class="back-button">← Каталог товаров</button>
            <h2 class="product-title">{{ product.name }}</h2>
        </div>
        <div class="product-content">
            <div class="product-image-wrapper">
                <img :src="product.image || defaultImage" :alt="product.name" class="product-image" />
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
                        <p v-for="(value, key) in product.specifications" :key="key" class="spec-item">
                            <strong>{{ key }}:</strong> {{ value }}
                        </p>
                    </div>
                </div>
                <div class="button-group">
                    <div v-if="cartItems[product.id]" class="quantity-controls">
                        <button @click="decreaseQuantity(product)" class="quantity-button">-</button>
                        <span class="quantity">{{ cartItems[product.id] }}</span>
                        <button @click="increaseQuantity(product)" class="quantity-button">+</button>
                    </div>
                    <button 
                        v-else 
                        @click="addToCart(product)" 
                        class="add-to-cart-button" 
                        :disabled="!product.is_available"
                    >
                        {{ product.is_available ? 'В корзину' : 'Недоступно' }}
                    </button>
                    <button :class="['wishlist-button', { 'active': isInWishlist(product.id) }]" @click="toggleWishlist(product)">
                        <span class="heart-icon">❤️</span>
                    </button>
                </div>
            </div>
        </div>
        <div class="reviews-section">
            <h3 class="reviews-title">Отзывы</h3>
            <div v-if="reviews.length > 0" class="reviews-list">
                <div v-for="review in reviews" :key="review.id" class="review-item">
                    <p><strong>{{ review.user }}</strong> - {{ review.rating }} звезды</p>
                    <p>{{ review.comment || 'Без комментария' }}</p>
                    <small>{{ new Date(review.created_at).toLocaleDateString() }}</small>
                </div>
            </div>
            <p v-else class="no-reviews">Пока нет отзывов.</p>
            <div class="add-review">
                <h4>Оставить отзыв</h4>
                <select v-model="newRating" class="rating-select">
                    <option v-for="rating in [1, 2, 3, 4, 5]" :key="rating" :value="rating">{{ rating }} звезды</option>
                </select>
                <textarea v-model="newComment" placeholder="Ваш отзыв..." class="review-textarea"></textarea>
                <button @click="submitReview" class="submit-review-button">Отправить</button>
            </div>
        </div>
    </div>
    <div v-else class="loading">Загрузка...</div>
</template>
<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import defaultImage from '@/assets/img/Default_product_foto.jpg';

const route = useRoute();
const router = useRouter();
const API_BASE_URL = 'http://127.0.0.1:8000';

const product = ref(null);
const reviews = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const newRating = ref(5);
const newComment = ref('');

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
        alert('Ошибка при загрузке данных товара. Проверьте консоль.');
    }
};

watch(() => route.params.id, () => {
    product.value = null;
    loadProductData();
});

const goBack = () => {
    router.push('/');
};

const isInWishlist = computed(() => (productId) => {
    return wishlist.value.includes(productId);
});

const toggleWishlist = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Пожалуйста, войдите в систему для добавления в желаемое.');
        return;
    }

    try {
        if (isInWishlist.value(product.id)) {
            await axios.delete(`${API_BASE_URL}/main/wishlist/remove/${product.id}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value = wishlist.value.filter(id => id !== product.id);
            alert('Товар удален из желаемого');
        } else {
            await axios.post(`${API_BASE_URL}/main/wishlist/add/`, {
                product_id: product.id
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value.push(product.id);
            alert('Товар добавлен в желаемое');
        }
    } catch (error) {
        console.error('Ошибка управления желаемым:', error.response ? error.response.data : error.message);
        alert('Ошибка при управлении желаемым: ' + (error.response ? JSON.stringify(error.response.data) : error.message));
    }
};

const addToCart = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Пожалуйста, войдите в систему для добавления в корзину.');
        return;
    }

    if (!product.is_available) {
        alert('Товар недоступен для добавления в корзину.');
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
        alert(`Товар "${product.name}" добавлен в корзину!`);
    } catch (error) {
        console.error('Ошибка добавления в корзину:', error.response ? error.response.data : error.message);
        alert('Ошибка при добавлении в корзину: ' + (error.response ? JSON.stringify(error.response.data) : error.message));
    }
};

const increaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    try {
        const newQuantity = (cartItems.value[product.id] || 0) + 1;
        if (newQuantity > product.stock) {
            alert('Нельзя добавить больше, чем есть в наличии!');
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
        alert('Ошибка при увеличении количества: ' + (error.response ? JSON.stringify(error.response.data) : error.message));
    }
};

const decreaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    try {
        const newQuantity = (cartItems.value[product.id] || 0) - 1;
        if (newQuantity <= 0) {
            await axios.delete(`${API_BASE_URL}/main/cart/remove/${product.id}/`, {
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
        alert('Ошибка при уменьшении количества: ' + (error.response ? JSON.stringify(error.response.data) : error.message));
    }
};

const submitReview = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Пожалуйста, войдите в систему для оставления отзыва.');
        return;
    }

    try {
        console.log('Отправка отзыва:', { rating: newRating.value, comment: newComment.value });
        const response = await axios.post(`${API_BASE_URL}/main/products/${route.params.id}/reviews/`, {
            rating: newRating.value,
            comment: newComment.value
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        reviews.value = [response.data]; // Обновляем отзывы с данными ответа
        newRating.value = 5;
        newComment.value = '';
        alert('Отзыв успешно добавлен!');
    } catch (error) {
        console.error('Ошибка отправки отзыва:', error.response ? error.response.data : error.message);
        alert('Ошибка при отправке отзыва: ' + (error.response ? JSON.stringify(error.response.data) : error.message));
    }
};
</script>

<style scoped>
.product-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Arial', sans-serif;
    background-color: #f5f7fa;
}

.product-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
}

.back-button {
    background: #6b46c1;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.back-button:hover {
    background: #553c9a;
}

.product-title {
    font-size: 28px;
    color: #2c3e50;
    margin: 0;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.product-content {
    display: flex;
    gap: 20px;
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.product-image-wrapper {
    width: 300px;
    height: 400px;
    overflow: hidden;
    border-radius: 12px;
}

.product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.product-content:hover .product-image {
    transform: scale(1.05);
}

.product-details {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.price-section {
    display: flex;
    align-items: center;
    gap: 15px;
}

.old-price {
    font-size: 18px;
    color: #e74c3c;
    text-decoration: line-through;
    margin: 0;
}

.product-price {
    font-size: 28px;
    color: #27ae60;
    font-weight: 700;
    margin: 0;
}

.availability {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
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

.product-specs p {
    margin: 5px 0;
    color: #2c3e50;
    font-size: 14px;
}

.specifications {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
    color: #34495e;
}

.spec-item {
    margin: 5px 0;
}

.button-group {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.add-to-cart-button {
    flex: 1;
    background: #3498db;
    color: #fff;
    border: none;
    padding: 12px;
    border-radius: 8px;
    font-size: 16px;
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
    gap: 10px;
    flex: 1;
}

.quantity-button {
    background: #3498db;
    color: #fff;
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-size: 18px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.quantity-button:hover {
    background: #2980b9;
}

.quantity {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    min-width: 40px;
    text-align: center;
}

.wishlist-button {
    background: #fff;
    border: 2px solid #27ae60;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    font-size: 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.wishlist-button.active {
    background: #27ae60;
    color: #fff;
    border-color: #27ae60;
}

.wishlist-button:hover:not(.active) {
    background: #e6f4ea;
    color: #27ae60;
}

.reviews-section {
    margin-top: 20px;
    padding: 20px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.reviews-title {
    font-size: 24px;
    color: #2c3e50;
    margin-bottom: 15px;
    font-weight: 700;
}

.reviews-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.review-item {
    padding: 10px;
    border-bottom: 1px solid #eee;
}

.review-item p {
    margin: 5px 0;
    color: #2c3e50;
}

.review-item small {
    color: #7f8c8d;
    font-size: 12px;
}

.no-reviews {
    color: #7f8c8d;
    font-size: 16px;
    text-align: center;
}

.add-review {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.rating-select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
}

.review-textarea {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    min-height: 100px;
    resize: vertical;
}

.submit-review-button {
    background: #6b46c1;
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.submit-review-button:hover {
    background: #553c9a;
}

.loading {
    text-align: center;
    font-size: 18px;
    color: #7f8c8d;
    padding: 20px;
}
</style>