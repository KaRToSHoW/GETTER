<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content user-details-modal">
            <ToastNotification ref="toast" />
            <div class="modal-header">
                <h3>Активность пользователя {{ user?.username }}</h3>
                <button class="close-button" @click="$emit('close')">&times;</button>
            </div>
            <div v-if="loading" class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                Загрузка данных...
            </div>
            <div v-else-if="error" class="error-message">
                {{ error }}
            </div>
            <div v-else class="user-activity-container">
                <!-- Общая статистика -->
                <div class="activity-stats">
                    <div class="stat-card">
                        <i class="fas fa-shopping-cart"></i>
                        <div class="stat-info">
                            <span class="stat-value">{{ userActivity.totalOrders }}</span>
                            <span class="stat-label">Всего заказов</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-star"></i>
                        <div class="stat-info">
                            <span class="stat-value">{{ userActivity.totalReviews }}</span>
                            <span class="stat-label">Отзывов</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-heart"></i>
                        <div class="stat-info">
                            <span class="stat-value">{{ userActivity.wishlistCount }}</span>
                            <span class="stat-label">В избранном</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-ruble-sign"></i>
                        <div class="stat-info">
                            <span class="stat-value">{{ userActivity.totalSpent }} ₽</span>
                            <span class="stat-label">Потрачено</span>
                        </div>
                    </div>
                </div>

                <!-- Последние заказы -->
                <div class="activity-section">
                    <h4><i class="fas fa-shopping-bag"></i> Последние заказы</h4>
                    <div class="activity-list" v-if="userActivity.recentOrders?.length">
                        <div v-for="order in userActivity.recentOrders" :key="order.id" class="activity-item">
                            <div class="activity-content">
                                <span class="activity-title">Заказ #{{ order.order_number }}</span>
                                <span class="activity-info">{{ order.total_price }} ₽</span>
                                <span :class="['order-status', order.status]">{{ getOrderStatus(order.status) }}</span>
                            </div>
                            <span class="activity-date">{{ formatDate(order.created_at) }}</span>
                        </div>
                    </div>
                    <p v-else class="no-data">Нет заказов</p>
                </div>

                <!-- Последние отзывы -->
                <div class="activity-section">
                    <h4><i class="fas fa-comment"></i> Последние отзывы</h4>
                    <div class="activity-list" v-if="userActivity.recentReviews?.length">
                        <div v-for="review in userActivity.recentReviews" :key="review.id" class="activity-item">
                            <div class="activity-content">
                                <span class="activity-title">{{ review.product.name }}</span>
                                <div class="review-rating">
                                    <span v-for="n in 5" :key="n" class="star">
                                        <i :class="['fas', n <= review.rating ? 'fa-star' : 'fa-star-o']"></i>
                                    </span>
                                </div>
                                <p class="review-comment" v-if="review.comment">{{ review.comment }}</p>
                                <div class="review-details" v-if="review.pros || review.cons">
                                    <p v-if="review.pros" class="pros"><strong>Достоинства:</strong> {{ review.pros }}</p>
                                    <p v-if="review.cons" class="cons"><strong>Недостатки:</strong> {{ review.cons }}</p>
                                </div>
                            </div>
                            <span class="activity-date">{{ formatDate(review.created_at) }}</span>
                        </div>
                    </div>
                    <p v-else class="no-data">Нет отзывов</p>
                </div>

                <!-- Избранные товары -->
                <div class="activity-section">
                    <h4><i class="fas fa-heart"></i> Избранные товары</h4>
                    <div class="activity-list" v-if="userActivity.wishlistItems?.length">
                        <div v-for="item in userActivity.wishlistItems" :key="item.id" class="activity-item">
                            <div class="activity-content">
                                <span class="activity-title">{{ item.product.name }}</span>
                                <span class="activity-info">{{ item.product.price }} ₽</span>
                            </div>
                            <span class="activity-date">{{ formatDate(item.added_at) }}</span>
                        </div>
                    </div>
                    <p v-else class="no-data">Нет товаров в избранном</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, onMounted } from 'vue';
import axios from 'axios';
import ToastNotification from '../ToastNotification.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';
const toast = ref(null);
const loading = ref(false);
const error = ref(null);
const userActivity = ref({
    totalOrders: 0,
    totalReviews: 0,
    wishlistCount: 0,
    totalSpent: 0,
    recentOrders: [],
    recentReviews: [],
    wishlistItems: []
});

const props = defineProps({
    user: {
        type: Object,
        required: true
    }
});

onMounted(async () => {
    await loadUserActivity();
});

const loadUserActivity = async () => {
    loading.value = true;
    error.value = null;
    try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/main/api/user-activity/${props.user.id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        userActivity.value = response.data;
    } catch (err) {
        error.value = 'Ошибка при загрузке данных пользователя';
        toast.value?.showToast('Ошибка при загрузке данных пользователя', 'error');
        console.error('Error loading user activity:', err);
    } finally {
        loading.value = false;
    }
};

const formatDate = (dateString) => {
    try {
        return new Date(dateString).toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        toast.value?.showToast('Ошибка форматирования даты', 'error');
        return dateString;
    }
};

const getOrderStatus = (status) => {
    const statuses = {
        'pending': 'Ожидает',
        'assembling': 'В сборке',
        'shipped': 'Отправлен',
        'delivered': 'Доставлен',
        'canceled': 'Отменен'
    };
    return statuses[status] || status;
};

defineEmits(['close']);
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 12px;
    padding: 0;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    animation: modalAppear 0.3s ease-out;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #eee;
    background-color: #f8f9fa;
    border-radius: 12px 12px 0 0;
    position: sticky;
    top: 0;
    z-index: 1;
}

.modal-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.5rem;
}

.close-button {
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.3s;
}

.close-button:hover {
    background-color: #eee;
}

.user-activity-container {
    padding: 20px;
    overflow-y: auto;
}

.activity-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    border-radius: 12px;
    padding: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card i {
    font-size: 24px;
    color: #6b46c1;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stat-info {
    display: flex;
    flex-direction: column;
}

.stat-value {
    font-size: 20px;
    font-weight: 600;
    color: #2d3748;
}

.stat-label {
    font-size: 14px;
    color: #718096;
}

.activity-section {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.activity-section h4 {
    font-size: 18px;
    color: #2d3748;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.activity-section h4 i {
    color: #6b46c1;
}

.activity-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.activity-item {
    padding: 12px;
    border-radius: 8px;
    background: #f8fafc;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.2s ease;
}

.activity-item:hover {
    transform: translateX(4px);
    background: #f1f5f9;
}

.activity-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.activity-title {
    font-weight: 500;
    color: #2d3748;
}

.activity-info {
    color: #718096;
    font-size: 14px;
}

.activity-date {
    color: #a0aec0;
    font-size: 14px;
}

.review-rating {
    margin: 4px 0;
}

.review-rating .star {
    color: #f6ad55;
    margin-right: 2px;
}

.review-rating .star.fa-star-o {
    color: #cbd5e0;
}

.review-comment {
    color: #718096;
    font-size: 14px;
    margin: 4px 0;
}

.order-status {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.order-status.pending {
    background: #fed7aa;
    color: #9a3412;
}

.order-status.assembling {
    background: #dbeafe;
    color: #1e40af;
}

.order-status.shipped {
    background: #dcfce7;
    color: #166534;
}

.order-status.delivered {
    background: #e0e7ff;
    color: #3730a3;
}

.order-status.canceled {
    background: #fee2e2;
    color: #991b1b;
}

.no-data {
    text-align: center;
    color: #a0aec0;
    padding: 20px;
    font-style: italic;
}

.loading-spinner {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    font-size: 1.1rem;
    color: #666;
    gap: 10px;
}

.loading-spinner i {
    color: #6b46c1;
}

.error-message {
    padding: 1rem;
    color: #e53e3e;
    text-align: center;
    background-color: #fff5f5;
    border-radius: 8px;
    margin: 1rem;
}

.review-details {
    margin-top: 8px;
    font-size: 0.9rem;
}

.review-details p {
    margin: 4px 0;
}

.pros {
    color: #38a169;
}

.cons {
    color: #e53e3e;
}

@keyframes modalAppear {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>