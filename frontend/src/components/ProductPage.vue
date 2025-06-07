<!-- src/components/ProductPage.vue -->
<template>
    <div class="product-container" v-if="product">
        <ToastNotification ref="toast" />
        <div class="product-header">
            <button @click="goBack" class="back-button">Назад</button>
            <h2 class="product-title">{{ product.name }}</h2>
            <div v-if="currentUser && currentUser.is_superuser" class="admin-panel">
                <span class="admin-badge">Администратор</span>
                <div class="admin-buttons">
                <button @click="editProduct" class="admin-button edit">Редактировать</button>
                <button @click="deleteProduct" class="admin-button delete">Удалить</button>
                </div>
            </div>
        </div>
        <div class="product-content">
            <div class="product-image-wrapper">
                <img :src="product.image || defaultImageProduct" :alt="product.name" class="product-image" />
            </div>
            <div class="product-details">
                <div class="price-section">
                    <p v-if="product.discount > 0" class="old-price"><s>{{ product.price }} ₽</s></p>
                    <p class="product-price">{{ product.discounted_price }} ₽</p>
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
                            <li v-for="(value, key) in product.specifications" :key="key" class="spec-item">
                                <strong>{{ key.replace(/_/g, ' ') }}:</strong> {{ value }}
                            </li>
                        </ul>
                    </div>

                    <div class="documentation-section" v-if="product.documentation || currentUser?.is_superuser">
                        <h4>Документация:</h4>
                        <div v-if="product.documentation" class="documentation-link">
                            <a :href="product.documentation" target="_blank" class="download-doc">
                                Скачать документацию
                            </a>
                        </div>
                        <div v-if="currentUser?.is_superuser" class="upload-doc">
                            <input 
                                type="file" 
                                @change="handleDocumentUpload" 
                                accept=".pdf,.doc,.docx"
                                id="documentUpload"
                                class="file-input"
                            />
                            <label for="documentUpload" class="upload-label">
                                {{ product.documentation ? 'Изменить документацию' : 'Загрузить документацию' }}
                            </label>
                        </div>
                    </div>
                    <div class="button-group">
                        <div v-if="cartItems[product.id]" class="quantity-controls">
                            <button @click="decreaseQuantity(product)" class="quantity-button">
                                -
                                <span class="sr-only">Уменьшить количество</span>
                            </button>
                            <span class="quantity">{{ cartItems[product.id] }}</span>
                            <button @click="increaseQuantity(product)" class="quantity-button">
                                +
                                <span class="sr-only">Увеличить количество</span>
                            </button>
                        </div>
                        <button v-else @click="addToCart(product)" class="add-to-cart-button"
                            :disabled="!product.is_available">
                            {{ product.is_available ? 'В корзину' : 'Недоступно' }}
                        </button>
                        <button :class="['wishlist-button', { 'active': isInWishlist(product.id) }]"
                            @click="toggleWishlist(product)">
                            <span class="heart-icon">❤️</span>
                            <span class="sr-only">{{ isInWishlist(product.id) ? 'Удалить из избранного' : 'Добавить в избранное' }}</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div class="reviews-section">
            <div class="reviews-header">
                <h3 class="reviews-title">{{ reviews.length }} {{ getReviewsCountText(reviews.length) }}</h3>
                <div class="rating-summary">
                    <span class="rating-number">{{ averageRating.toFixed(1) }}</span>
                    <div class="stars">
                        <span v-for="i in 5" :key="i"
                            :class="['star', i <= Math.round(averageRating) ? 'filled' : '']">
                            <span v-if="i <= Math.round(averageRating)">★</span>
                            <span v-else>☆</span>
                        </span>
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
                        <span class="filter-label">Фильтр по рейтингу:</span>
                        <div class="rating-buttons">
                        <button v-for="rating in 5" :key="rating"
                            :class="['rating-filter-btn', { active: selectedRating === rating }]"
                            @click="toggleRatingFilter(rating)">
                            {{ rating }}★
                        </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="filteredReviews.length > 0" class="reviews-list">
                <div v-for="review in filteredReviews" :key="review.id" class="review-item">
                    <div class="review-header">
                        <img :src="review.user && review.user.profile_image_url ? `${API_BASE_URL}${review.user.profile_image_url}` : defaultImage"
                            alt="User avatar" class="user-avatar">
                        <div class="review-info">
                            <div class="user-name">{{ review.user ? review.user.username : 'Пользователь' }}</div>
                            <div class="review-date">{{ formatDate(review.created_at) }}</div>
                        </div>
                        <button 
                            v-if="canDeleteReview(review)" 
                            @click="deleteReview(review.id)" 
                            class="delete-review-button"
                        >
                            ✖
                            <span class="sr-only">Удалить отзыв</span>
                        </button>
                        <button 
                            v-if="canEditReview(review)" 
                            @click="startEditReview(review)" 
                            class="edit-review-button"
                        >
                            ✎
                            <span class="sr-only">Редактировать отзыв</span>
                        </button>
                    </div>
                    <div class="review-rating">
                        <div class="stars">
                            <span v-for="i in 5" :key="i" :class="['star', i <= review.rating ? 'filled' : '']">
                                <span v-if="i <= review.rating">★</span>
                                <span v-else>☆</span>
                            </span>
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
        
        <!-- Модальное окно для редактирования отзыва -->
        <div v-if="editingReview" class="edit-review-modal">
            <div class="edit-review-content">
                <h3>Редактирование отзыва</h3>
                <div class="rating-input">
                    <span v-for="i in 5" :key="i" :class="['star', i <= editingReview.rating ? 'filled' : '']"
                        @click="editingReview.rating = i">★</span>
                </div>
                <textarea v-model="editingReview.comment" placeholder="Ваш отзыв..." class="review-textarea"></textarea>
                <div class="review-fields">
                    <input v-model="editingReview.pros" placeholder="Плюсы" class="review-input" />
                    <input v-model="editingReview.cons" placeholder="Минусы" class="review-input" />
                </div>
                <div class="modal-buttons">
                    <button @click="cancelEditReview" class="cancel-button">Отмена</button>
                    <button @click="saveEditedReview" class="save-button">Сохранить</button>
                </div>
            </div>
        </div>
        
        <!-- Модальное окно для редактирования товара -->
        <div v-if="editingProduct" class="edit-product-modal">
            <div class="edit-product-content">
                <h3>Редактирование товара</h3>
                <form @submit.prevent="saveEditedProduct" class="edit-product-form">
                    <div class="form-group">
                        <label>Название товара:</label>
                        <input v-model="editingProduct.name" required />
                    </div>
                    <div class="form-group">
                        <label>Цена:</label>
                        <input v-model.number="editingProduct.price" type="number" min="0" step="0.01" required />
                    </div>
                    <div class="form-group">
                        <label>Скидка (%):</label>
                        <input v-model.number="editingProduct.discount" type="number" min="0" max="100" />
                    </div>
                    <div class="form-group">
                        <label>Количество на складе:</label>
                        <input v-model.number="editingProduct.stock" type="number" min="0" required />
                    </div>
                    <div class="form-group">
                        <label>Артикул:</label>
                        <input v-model="editingProduct.sku" />
                    </div>
                    <div class="form-group">
                        <label>Доступность:</label>
                        <select v-model="editingProduct.is_available">
                            <option :value="true">Доступен</option>
                            <option :value="false">Недоступен</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Категория:</label>
                        <select v-model="editingProduct.category.id">
                            <option v-for="category in categories" :key="category.id" :value="category.id">
                                {{ category.name }}
                            </option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Изображение товара:</label>
                        <input 
                            type="file" 
                            @change="handleProductImageUpload" 
                            accept="image/*"
                            class="form-input"
                        />
                        <div v-if="editingProduct?.image" class="image-preview">
                            <img :src="typeof editingProduct.image === 'string' ? editingProduct.image : URL.createObjectURL(editingProduct.image)" 
                                 alt="Preview" />
                        </div>
                    </div>
                    <div class="form-buttons">
                        <button type="button" @click="cancelEditProduct" class="cancel-button">Отмена</button>
                        <button type="submit" class="save-button">Сохранить</button>
                    </div>
                </form>
            </div>
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
const currentUser = ref(null);
const editingReview = ref(null);
const editingProduct = ref(null);
const categories = ref([]);

onMounted(async () => {
    await loadCurrentUser();
    await loadProductData();
    if (currentUser.value && currentUser.value.is_superuser) {
        await loadCategories();
    }
});

const loadProductData = async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const [productResponse, reviewsResponse, wishlistResponse, cartResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/main/products/${route.params.id}/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/${route.params.id}/reviews/`, { headers })
                .catch(error => {
                    console.error('Ошибка загрузки отзывов:', error);
                    return { data: [] };
                }),
            token ? axios.get(`${API_BASE_URL}/main/wishlist/check/`, { headers }) : Promise.resolve({ data: [] }),
            token ? axios.get(`${API_BASE_URL}/main/cart/`, { headers }) : Promise.resolve({ data: [] })
        ]);

        product.value = productResponse.data;
        
        // Проверяем, что отзывы имеют правильный формат
        if (Array.isArray(reviewsResponse.data)) {
            reviews.value = reviewsResponse.data;
            console.log('Загружено отзывов:', reviews.value.length);
        } else {
            console.error('Ошибка: отзывы не являются массивом:', reviewsResponse.data);
            reviews.value = [];
        }
        
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
        console.log('Загруженные отзывы:', JSON.stringify(reviews.value));
        
        // Отладочная информация о структуре отзывов
        if (reviews.value.length > 0) {
            console.log('Образец отзыва:', reviews.value[0]);
            console.log('Поля отзыва:');
            for (const key in reviews.value[0]) {
                console.log(`  ${key}: ${typeof reviews.value[0][key]}`);
            }
        } else {
            console.log('Отзывов нет или они не загрузились');
        }
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

// Функция для склонения слова "отзыв" в зависимости от числа
const getReviewsCountText = (count) => {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;
    
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
        return 'отзывов';
    }
    
    if (lastDigit === 1) {
        return 'отзыв';
    }
    
    if (lastDigit >= 2 && lastDigit <= 4) {
        return 'отзыва';
    }
    
    return 'отзывов';
};

// Фильтрация и сортировка отзывов
const filteredReviews = computed(() => {
    // Проверяем, что reviews - это массив
    if (!Array.isArray(reviews.value)) {
        console.error('reviews is not an array:', reviews.value);
        return [];
    }
    
    // Фильтруем только корректные отзывы, у которых есть id и rating
    let filtered = reviews.value.filter(review => review && review.id && typeof review.rating !== 'undefined');
    
    // Выводим сообщение, если отфильтровали какие-то отзывы
    if (filtered.length !== reviews.value.length) {
        console.warn(`Отфильтровано ${reviews.value.length - filtered.length} некорректных отзывов`);
    }

    // Фильтрация по рейтингу
    if (selectedRating.value) {
        filtered = filtered.filter(review => review.rating === selectedRating.value);
    }

    // Сортировка
    switch (sortBy.value) {
        case 'date-new':
            filtered.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
            break;
        case 'date-old':
            filtered.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0));
            break;
        case 'rating-high':
            filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
            break;
        case 'rating-low':
            filtered.sort((a, b) => (a.rating || 0) - (b.rating || 0));
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

// Загрузка информации о текущем пользователе
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
        console.error('Ошибка загрузки профиля:', error);
    }
};

// Функция для проверки прав на удаление отзыва
const canDeleteReview = (review) => {
    if (!currentUser.value) return false;
    if (!review || !review.user) return false;
    
    // Админ может удалять любые отзывы
    if (currentUser.value.is_superuser) return true;
    
    // Обычный пользователь может удалять только свои отзывы
    return review.user.id === currentUser.value.id;
};

// Функция для удаления отзыва
const deleteReview = async (reviewId) => {
    // Добавляем предупреждение перед удалением
    if (!confirm('Вы действительно хотите удалить этот отзыв?')) {
        return;
    }
    
    try {
        // Находим отзыв в списке
        const review = reviews.value.find(r => r.id === reviewId);
        if (!review) {
            toast.value.showToast('Отзыв не найден', 'error');
            return;
        }
        
        // Проверяем права доступа
        if (!canDeleteReview(review)) {
            toast.value.showToast('У вас нет прав на удаление этого отзыва', 'error');
            return;
        }
        
        const token = localStorage.getItem('token');
        
        // Отправляем запрос на удаление отзыва на сервер
        await axios.delete(
            `${API_BASE_URL}/main/products/${route.params.id}/reviews/${reviewId}/`, 
            {
                headers: { Authorization: `Bearer ${token}` }
            }
        );
        
        // Удаляем отзыв из списка после успешного запроса
        reviews.value = reviews.value.filter(review => review.id !== reviewId);
        toast.value.showToast('Отзыв успешно удален', 'success');
        
    } catch (error) {
        console.error('Ошибка удаления отзыва:', error);
        
        if (error.response) {
            // Если сервер вернул ошибку, показываем сообщение от сервера
            const errorMessage = error.response.data.error || 'Ошибка при удалении отзыва';
            toast.value.showToast(errorMessage, 'error');
        } else {
            toast.value.showToast('Ошибка при удалении отзыва: ' + error.message, 'error');
        }
    }
};

// Функция для редактирования товара (только для администраторов)
const editProduct = () => {
    if (!currentUser.value || !currentUser.value.is_superuser) {
        toast.value.showToast('У вас нет прав для редактирования товаров', 'error');
        return;
    }
    
    // Создаем копию товара и открываем модальное окно редактирования
    editingProduct.value = JSON.parse(JSON.stringify(product.value));
};

// Функция для удаления товара (только для администраторов)
const deleteProduct = async () => {
    if (!currentUser.value || !currentUser.value.is_superuser) {
        toast.value.showToast('У вас нет прав для удаления товаров', 'error');
        return;
    }
    
    if (confirm('Вы уверены, что хотите удалить этот товар?')) {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`${API_BASE_URL}/main/products/${route.params.id}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            toast.value.showToast('Товар успешно удален', 'success');
            router.push('/home');
        } catch (error) {
            console.error('Ошибка удаления товара:', error);
            toast.value.showToast('Ошибка при удалении товара: ' + (error.response?.data?.detail || error.message), 'error');
        }
    }
};

// Функция для определения, может ли пользователь редактировать отзыв
const canEditReview = (review) => {
    if (!currentUser.value) return false;
    if (!review || !review.user) return false;
    
    // Пользователь может редактировать только свои отзывы
    return review.user.id === currentUser.value.id;
};

// Функция начала редактирования отзыва
const startEditReview = (review) => {
    // Создаем копию отзыва для редактирования
    editingReview.value = { ...review };
};

// Функция отмены редактирования
const cancelEditReview = () => {
    editingReview.value = null;
};

// Функция сохранения отредактированного отзыва
const saveEditedReview = async () => {
    try {
        const token = localStorage.getItem('token');
        // Используем метод POST вместо PUT
        await axios.post(`${API_BASE_URL}/main/products/${route.params.id}/reviews/`, {
            action: 'update',
            review_id: editingReview.value.id,
            rating: editingReview.value.rating,
            comment: editingReview.value.comment,
            pros: editingReview.value.pros,
            cons: editingReview.value.cons
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        // Обновляем отзыв в списке
        const index = reviews.value.findIndex(r => r.id === editingReview.value.id);
        if (index !== -1) {
            reviews.value[index] = editingReview.value;
        }
        
        // Закрываем модальное окно
        editingReview.value = null;
        toast.value.showToast('Отзыв успешно обновлен', 'success');
    } catch (error) {
        console.error('Ошибка обновления отзыва:', error);
        toast.value.showToast('Ошибка при обновлении отзыва: ' + (error.response?.data?.detail || error.message), 'error');
    }
};

// Загрузка списка категорий для формы редактирования товара
const loadCategories = async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.get(`${API_BASE_URL}/main/categories/`, { headers });
        categories.value = response.data;
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
        toast.value.showToast('Ошибка при загрузке категорий', 'error');
    }
};

// Функция отмены редактирования товара
const cancelEditProduct = () => {
    editingProduct.value = null;
};

// Функция сохранения отредактированного товара
const saveEditedProduct = async () => {
    try {
        const token = localStorage.getItem('token');
        const formData = new FormData();

        // Add category_id
        formData.append('category_id', editingProduct.value.category.id);

        // Add basic fields
        formData.append('name', editingProduct.value.name);
        formData.append('sku', editingProduct.value.sku);
        formData.append('description', editingProduct.value.description || '');
        formData.append('price', editingProduct.value.price);
        formData.append('discount', editingProduct.value.discount || 0);
        formData.append('stock', editingProduct.value.stock);
        formData.append('is_available', editingProduct.value.is_available);

        // Add specifications if they exist
        if (editingProduct.value.specifications) {
            formData.append('specifications', JSON.stringify(editingProduct.value.specifications));
        }

        // Keep the existing image if no new one is uploaded
        if (editingProduct.value.image && editingProduct.value.image instanceof File) {
            formData.append('image', editingProduct.value.image);
        }

        const response = await axios.put(
            `${API_BASE_URL}/main/products/${editingProduct.value.id}/`, 
            formData,
            {
                headers: { 
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        
        // Update product data
        product.value = response.data;
        
        // Close modal
        editingProduct.value = null;
        toast.value.showToast('Товар успешно обновлен', 'success');
    } catch (error) {
        console.error('Ошибка обновления товара:', error);
        toast.value.showToast('Ошибка при обновлении товара: ' + (error.response?.data?.detail || error.message), 'error');
    }
};

// Функция для загрузки изображения товара
const handleProductImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        editingProduct.value.image = file;
    }
};

// Функция для загрузки документации
const handleDocumentUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
        const formData = new FormData();
        formData.append('documentation', file);
        const token = localStorage.getItem('token');

        const response = await axios.patch(
            `${API_BASE_URL}/main/products/${product.value.id}/`,
            formData,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            }
        );

        product.value = response.data;
        toast.value?.showToast('Документация успешно обновлена', 'success');
    } catch (error) {
        console.error('Ошибка загрузки документации:', error);
        toast.value?.showToast('Ошибка при загрузке документации', 'error');
    }
};
</script>

<style scoped>
.product-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 40px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #fafafa;
    min-height: 100vh;
    color: #2c3e50;
}

.product-header {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 30px;
    gap: 15px;
    position: relative;
}

.back-button {
    padding: 10px 20px;
    background-color: #f8f9fa;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    color: #5a6268;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.back-button:hover {
    background-color: #e9ecef;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.product-title {
    margin: 0;
    flex-grow: 1;
    font-size: 32px;
    color: #2c3e50;
    font-weight: 700;
    text-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.product-content {
    display: grid;
    grid-template-columns: minmax(500px, 40%) 1fr;
    gap: 40px;
    align-items: start;
    margin: 30px 0;
    background: #fff;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.product-content:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
}

.product-image-wrapper {
    position: relative;
    width: 100%;
    aspect-ratio: 1;
    border-radius: 24px;
    background: linear-gradient(145deg, #f6f8fc, #ffffff);
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.product-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 32px;
    transition: transform 0.5s ease;
}

.product-image:hover {
    transform: scale(1.05);
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
    padding: 30px;
    background: linear-gradient(145deg, #ffffff, #f5f7fa);
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
}

.old-price {
    font-size: 18px;
    color: #9ca3af;
    text-decoration: line-through;
    margin: 0;
}

.product-price {
    font-size: 48px;
    color: #2c3e50;
    font-weight: 800;
    margin: 0;
    line-height: 1;
    background: linear-gradient(45deg, #3498db, #8e44ad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
    color: #2c3e50;
}

.availability span:first-child {
    font-weight: 600;
}

.availability span:first-child::before {
    content: "";
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.out-of-stock span:first-child::before {
    background: #ef4444;
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.2);
    animation: none;
}

.stock {
    font-size: 14px;
    color: #64748b;
}

.product-specs {
    background: linear-gradient(145deg, #ffffff, #f5f7fa);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
}

.product-specs p {
    margin: 10px 0;
    line-height: 1.6;
}

.product-specs strong {
    color: #3b82f6;
}

.specifications {
    margin-top: 20px;
}

.specifications h4 {
    font-size: 18px;
    margin-bottom: 15px;
    color: #2c3e50;
    font-weight: 600;
}

.specifications-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 12px;
}

.spec-item {
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
    border-left: 3px solid #3b82f6;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.spec-item:hover {
    transform: translateX(5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.spec-item strong {
    display: block;
    margin-bottom: 4px;
    text-transform: capitalize;
    color: #3b82f6;
}

.button-group {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 16px;
    margin-top: 30px;
}

.quantity-controls {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px;
    background: linear-gradient(145deg, #ffffff, #f5f7fa);
    border-radius: 50px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    width: fit-content;
}

.quantity-button {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: none;
    background: white;
    color: #3b82f6;
    font-size: 20px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.quantity-button:hover {
    background: #3b82f6;
    color: white;
    transform: scale(1.1);
}

.quantity {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    min-width: 40px;
    text-align: center;
}

.add-to-cart-button {
    height: 56px;
    background: linear-gradient(45deg, #3b82f6, #6366f1);
    color: white;
    border: none;
    border-radius: 50px;
    font-size: 17px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.add-to-cart-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.add-to-cart-button:disabled {
    background: linear-gradient(45deg, #9ca3af, #d1d5db);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.wishlist-button {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    border: none;
    background: white;
    color: #ef4444;
    font-size: 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.wishlist-button:hover {
    background: #fef2f2;
    transform: translateY(-3px) scale(1.1);
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.2);
}

.wishlist-button.active {
    background: #fef2f2;
    color: #ef4444;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.wishlist-button .heart-icon {
    transition: transform 0.3s;
}

.wishlist-button:hover .heart-icon {
    transform: scale(1.2);
}

.wishlist-button.active .heart-icon {
    animation: heartBeat 1.3s ease-in-out;
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
    margin-top: 60px;
    padding: 40px;
    background: linear-gradient(145deg, #ffffff, #f5f7fa);
    border-radius: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.reviews-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.reviews-title {
    font-size: 24px;
    color: #2c3e50;
    font-weight: 700;
    margin: 0;
}

.rating-summary {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 20px;
    background: white;
    border-radius: 50px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.rating-number {
    font-size: 24px;
    font-weight: 700;
    color: #3b82f6;
}

.stars {
    display: flex;
    gap: 3px;
}

.star {
    color: #d1d5db;
    font-size: 20px;
    transition: color 0.3s ease, transform 0.3s ease;
}

.star.filled {
    color: #f59e0b;
}

.reviews-list {
    display: grid;
    gap: 20px;
}

.review-item {
    background: white;
    padding: 25px;
    border-radius: 16px;
    display: grid;
    gap: 15px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.03);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-left: 4px solid transparent;
}

.review-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    border-left-color: #3b82f6;
}

.review-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    position: relative;
}

.user-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #f3f4f6;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.review-info {
    margin-left: 15px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.user-name {
    font-weight: 600;
    color: #2c3e50;
    font-size: 16px;
}

.review-date {
    font-size: 13px;
    color: #9ca3af;
}

.review-rating {
    margin: 8px 0;
}

.review-content {
    display: grid;
    gap: 15px;
    color: #4b5563;
    font-size: 15px;
}

.review-pros,
.review-cons {
    margin: 0;
    padding: 15px;
    border-radius: 12px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
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
    color: #4b5563;
    font-size: 15px;
    line-height: 1.7;
    margin-top: 10px;
    padding: 20px;
    background: #f9fafb;
    border-radius: 12px;
    border-left: 3px solid #e5e7eb;
    position: relative;
}

.review-text::before {
    content: '"';
    position: absolute;
    top: 5px;
    left: 10px;
    font-size: 40px;
    color: #e5e7eb;
    font-family: Georgia, serif;
    line-height: 1;
}

.read-more {
    color: #3b82f6;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    margin-top: 10px;
    display: inline-block;
    transition: color 0.2s;
}

.read-more:hover {
    color: #2563eb;
    text-decoration: underline;
}

.add-review {
    background: white;
    padding: 30px;
    border-radius: 16px;
    margin-bottom: 30px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.03);
    border-top: 4px solid #3b82f6;
}

.add-review h4 {
    font-size: 18px;
    color: #2c3e50;
    margin-top: 0;
    margin-bottom: 20px;
    font-weight: 600;
}

.rating-input {
    display: flex;
    gap: 6px;
    margin-bottom: 20px;
}

.rating-input .star {
    cursor: pointer;
    transition: transform 0.2s ease, color 0.2s ease;
    font-size: 30px;
    color: #d1d5db;
}

.rating-input .star:hover,
.rating-input .star.filled {
    color: #f59e0b;
    transform: scale(1.2);
}

.review-textarea {
    padding: 15px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    font-size: 15px;
    min-height: 120px;
    resize: vertical;
    background: #f9fafb;
    width: 100%;
    margin-bottom: 20px;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.review-textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.review-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

.review-input {
    padding: 15px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    font-size: 15px;
    background: #f9fafb;
    width: 100%;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.review-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.submit-review-button {
    background: linear-gradient(45deg, #3b82f6, #6366f1);
    color: white;
    border: none;
    padding: 15px 30px;
    border-radius: 50px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.submit-review-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.reviews-filters {
    margin: 30px 0;
    display: flex;
    gap: 30px;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 15px;
}

.filter-group label {
    color: #2c3e50;
    font-size: 15px;
    font-weight: 500;
}

.filter-select {
    padding: 10px 15px;
    border: 1px solid #e5e7eb;
    border-radius: 50px;
    background: white;
    font-size: 14px;
    color: #4b5563;
    min-width: 180px;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.filter-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.rating-filter {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 15px;
}

.filter-label {
    font-weight: 500;
    color: #2c3e50;
}

.rating-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.rating-filter-btn {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 50px;
    padding: 8px 15px;
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
}

.rating-filter-btn:hover {
    background-color: #f3f4f6;
    transform: translateY(-2px);
}

.rating-filter-btn.active {
    background-color: #3b82f6;
    color: white;
    border-color: #3b82f6;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.no-reviews {
    padding: 30px;
    text-align: center;
    background: white;
    border-radius: 16px;
    color: #9ca3af;
    font-size: 16px;
}

.loading {
    text-align: center;
    font-size: 18px;
    color: #9ca3af;
    padding: 60px;
    animation: pulse 1.5s infinite;
}

.delete-review-button {
    position: absolute;
    right: 0;
    top: 0;
    background-color: #ef4444;
    color: white;
    border: none;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.delete-review-button:hover {
    background-color: #dc2626;
    transform: rotate(90deg) scale(1.1);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.edit-review-button {
    position: absolute;
    right: 35px;
    top: 0;
    background-color: #10b981;
    color: white;
    border: none;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.edit-review-button:hover {
    background-color: #059669;
    transform: rotate(15deg) scale(1.1);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.edit-review-modal,
.edit-product-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(5px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    animation: fadeIn 0.3s ease;
    overflow-y: auto;
    padding: 20px;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.edit-review-content,
.edit-product-content {
    background: linear-gradient(145deg, #ffffff, #f5f7fa);
    padding: 40px;
    border-radius: 24px;
    width: 90%;
    max-width: 600px;
    max-height: 85vh;
    overflow-y: auto;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
    animation: slideUp 0.4s ease;
    margin: auto;
}

@keyframes slideUp {
    from {
        transform: translateY(30px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.edit-review-content h3,
.edit-product-content h3 {
    margin-top: 0;
    color: #2c3e50;
    font-size: 24px;
    margin-bottom: 30px;
    font-weight: 700;
    text-align: center;
}

.modal-buttons,
.form-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 30px;
}

.cancel-button,
.save-button {
    padding: 12px 30px;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.3s;
}

.cancel-button {
    background-color: #f3f4f6;
    color: #4b5563;
}

.cancel-button:hover {
    background-color: #e5e7eb;
    transform: translateY(-2px);
}

.save-button {
    background: linear-gradient(45deg, #10b981, #059669);
    color: white;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.save-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.edit-product-form {
    display: grid;
    gap: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.form-group label {
    font-weight: 500;
    color: #4b5563;
    font-size: 15px;
}

.form-group input,
.form-group select {
    padding: 15px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    font-size: 15px;
    background: white;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.image-preview {
    margin-top: 15px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.image-preview img {
    max-width: 100%;
    max-height: 200px;
    display: block;
    margin: 0 auto;
    border-radius: 8px;
    transition: transform 0.3s ease;
}

.image-preview img:hover {
    transform: scale(1.03);
}

.admin-panel {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    margin-left: auto;
}

.admin-badge {
    background: linear-gradient(45deg, #6366f1, #8b5cf6);
    color: white;
    padding: 8px 16px;
    border-radius: 50px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.admin-buttons {
    display: flex;
    gap: 10px;
}

.admin-button {
    padding: 10px 20px;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    color: white;
    transition: all 0.3s;
}

.admin-button:hover {
    transform: translateY(-3px);
}

.admin-button.edit {
    background: linear-gradient(45deg, #10b981, #059669);
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.admin-button.edit:hover {
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.admin-button.delete {
    background: linear-gradient(45deg, #ef4444, #dc2626);
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.admin-button.delete:hover {
    box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

.documentation-section {
    margin-top: 30px;
    padding: 25px;
    background: linear-gradient(145deg, #ffffff, #f5f7fa);
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
}

.documentation-section h4 {
    margin: 0 0 15px 0;
    font-size: 18px;
    color: #2c3e50;
    font-weight: 600;
}

.documentation-link {
    margin-bottom: 15px;
}

.download-doc {
    display: inline-flex;
    align-items: center;
    padding: 12px 24px;
    background: linear-gradient(45deg, #3b82f6, #2563eb);
    color: white;
    text-decoration: none;
    border-radius: 50px;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.download-doc:hover {
    background: linear-gradient(45deg, #2563eb, #1d4ed8);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.upload-doc {
    position: relative;
    margin-top: 15px;
}

.file-input {
    position: absolute;
    width: 0.1px;
    height: 0.1px;
    opacity: 0;
    overflow: hidden;
    z-index: -1;
}

.upload-label {
    display: inline-block;
    padding: 12px 24px;
    background: linear-gradient(45deg, #6b7280, #4b5563);
    color: white;
    border-radius: 50px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(75, 85, 99, 0.3);
}

.upload-label:hover {
    background: linear-gradient(45deg, #4b5563, #374151);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(75, 85, 99, 0.4);
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
        padding: 25px;
        border-radius: 16px;
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

    .product-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }
    
    .back-button {
        padding: 8px 16px;
        font-size: 14px;
    }
    
    .product-title {
        font-size: 24px;
        width: 100%;
    }
    
    .admin-panel {
        width: 100%;
        justify-content: space-between;
        margin-left: 0;
    }
    
    .rating-filter {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .filter-label {
        margin-bottom: 10px;
    }
    
    .review-fields {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .product-container {
        padding: 15px;
    }

    .product-content {
        padding: 20px;
    }

    .quantity-controls {
        width: 100%;
        justify-content: space-between;
    }

    .admin-panel {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .admin-buttons {
        width: 100%;
    }
    
    .admin-button {
        flex: 1;
        text-align: center;
    }
    
    .rating-buttons {
        width: 100%;
        justify-content: space-between;
    }
    
    .reviews-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
    }
    
    .rating-summary {
        width: 100%;
    }
}
</style>