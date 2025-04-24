<!-- src/components/ProductPage.vue -->
<template>
    <div class="product-container" v-if="product">
        <ToastNotification ref="toast" />
        <div class="product-header">
            <button @click="goBack" class="back-button">Назад</button>
            <h2 class="product-title">{{ product.name }}</h2>
            <div v-if="currentUser && currentUser.is_superuser" class="admin-panel">
                <span class="admin-badge">Администратор</span>
                <button @click="editProduct" class="admin-button edit">Редактировать</button>
                <button @click="deleteProduct" class="admin-button delete">Удалить</button>
            </div>
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
                        <button 
                            v-if="canDeleteReview(review)" 
                            @click="deleteReview(review.id)" 
                            class="delete-review-button"
                        >
                            ✖
                        </button>
                        <button 
                            v-if="canEditReview(review)" 
                            @click="startEditReview(review)" 
                            class="edit-review-button"
                        >
                            ✎
                        </button>
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
        const response = await axios.put(`${API_BASE_URL}/main/products/${editingProduct.value.id}/`, editingProduct.value, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        // Обновляем данные товара
        product.value = response.data;
        
        // Закрываем модальное окно
        editingProduct.value = null;
        toast.value.showToast('Товар успешно обновлен', 'success');
    } catch (error) {
        console.error('Ошибка обновления товара:', error);
        toast.value.showToast('Ошибка при обновлении товара: ' + (error.response?.data?.detail || error.message), 'error');
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
    align-items: center;
    margin-bottom: 10px;
    position: relative;
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

.delete-review-button {
    position: absolute;
    right: 0;
    top: 0;
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.3s;
}

.delete-review-button:hover {
    background-color: #ff0000;
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

.admin-panel {
    display: flex;
    align-items: center;
    margin-left: auto;
    gap: 10px;
}

.admin-badge {
    background-color: #6b46c1;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.admin-button {
    padding: 5px 10px;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.admin-button.edit {
    background-color: #4caf50;
    color: white;
}

.admin-button.delete {
    background-color: #f44336;
    color: white;
}

.admin-button:hover {
    opacity: 0.8;
}

/* Стили для кнопки редактирования отзыва */
.edit-review-button {
    position: absolute;
    right: 30px;
    top: 0;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.3s;
}

.edit-review-button:hover {
    background-color: #45a049;
}

/* Стили для модального окна редактирования */
.edit-review-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.edit-review-content {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    width: 90%;
    max-width: 600px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.cancel-button, .save-button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.cancel-button {
    background-color: #f44336;
    color: white;
}

.save-button {
    background-color: #4caf50;
    color: white;
}

/* Стили для модального окна редактирования товара */
.edit-product-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.edit-product-content {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    width: 90%;
    max-width: 600px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.edit-product-form {
    display: grid;
    gap: 16px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-weight: 500;
    margin-bottom: 8px;
}

.form-group input {
    padding: 12px;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    font-size: 14px;
}

.form-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}
</style>