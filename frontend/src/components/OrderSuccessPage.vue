<template>
  <div class="success-container">
    <div class="success-card">
      <!-- Индикатор загрузки -->
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
        <p>Загрузка информации о заказе...</p>
      </div>
      
      <!-- Сообщение об ошибке -->
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="loadOrderFromServer" class="btn primary">Повторить</button>
      </div>
      
      <div v-else>
        <div class="success-icon">{{ orderId === 'успешно' ? '✓' : '📋' }}</div>
        <h1>{{ orderId === 'успешно' ? 'Заказ успешно оформлен!' : 'Информация о заказе' }}</h1>
        <p class="order-number">Номер заказа: <strong>{{ orderDetails?.order_number || orderId }}</strong></p>
        
        <!-- Подробная информация о заказе -->
        <div class="order-details" v-if="orderDetails">
          <h2>Детали заказа</h2>
        
        <div class="detail-section">
          <h3>Адрес доставки</h3>
          <p>{{ orderDetails.address }}</p>
          <p v-if="orderDetails.comment" class="comment">Комментарий: {{ orderDetails.comment }}</p>
        </div>
        
        <div class="detail-section">
          <h3>Товары в заказе</h3>
          <div class="order-items">
            <div v-for="(item, index) in orderDetails.items" :key="index" class="order-item">
              <div class="item-info">
                <span class="item-name">{{ item.product.name }}</span>
                <span class="item-quantity">x {{ item.quantity }}</span>
              </div>
              <div class="item-price">{{ formatPrice(calculateItemTotal(item)) }} ₽</div>
            </div>
          </div>
        </div>
        
        <div class="order-summary">
          <div class="summary-row">
            <span>Сумма товаров:</span>
            <span>{{ formatPrice(orderDetails.total) }} ₽</span>
          </div>
          <div class="summary-row">
            <span>Доставка:</span>
            <span>{{ orderDetails.deliveryPrice > 0 ? `${formatPrice(orderDetails.deliveryPrice)} ₽` : 'Бесплатно' }}</span>
          </div>
          <div class="summary-row grand-total">
            <span>Итого к оплате:</span>
            <span>{{ formatPrice(Number(orderDetails.total) + Number(orderDetails.deliveryPrice)) }} ₽</span>
          </div>
        </div>
      </div>
      
              <p class="message">Благодарим вас за покупку! Информация о вашем заказе была отправлена на вашу электронную почту.</p>
        <div class="actions">
          <router-link to="/profile?tab=orders" class="btn primary">Мои заказы</router-link>
          <router-link to="/catalog" class="btn secondary">Продолжить покупки</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';
const route = useRoute();
const orderId = route.params.orderId;
const orderDetails = ref(null);
const loading = ref(false);
const error = ref(null);

// Загрузка сохраненных деталей заказа из sessionStorage
const loadLocalOrderDetails = () => {
  try {
    const orderData = sessionStorage.getItem('lastOrderDetails');
    if (orderData) {
      orderDetails.value = JSON.parse(orderData);
      return true;
    }
    return false;
  } catch (e) {
    console.error('Ошибка при загрузке деталей заказа из sessionStorage:', e);
    return false;
  }
};

// Загрузка деталей заказа с сервера
const loadOrderFromServer = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      error.value = 'Требуется авторизация для просмотра заказа';
      return;
    }
    
    // Если orderId содержит буквы (например ORD-...), считаем это номером заказа и ищем в списке заказов
    if (typeof orderId === 'string' && orderId.includes('ORD-')) {
      // Получаем список всех заказов пользователя
      const ordersResponse = await axios.get(`${API_BASE_URL}/main/user/orders/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Ищем заказ по номеру
      const foundOrder = ordersResponse.data.orders.find(order => order.order_number === orderId);
      
      if (foundOrder) {
        // Используем найденный заказ
        processOrderData(foundOrder);
      } else {
        error.value = `Заказ с номером ${orderId} не найден`;
      }
    } else {
      // Если это числовой ID, используем стандартный API для получения по ID
      const response = await axios.get(`${API_BASE_URL}/main/orders/${orderId}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      processOrderData(response.data);
    }
  } catch (e) {
    console.error('Ошибка при загрузке заказа с сервера:', e);
    error.value = 'Не удалось загрузить данные заказа';
  } finally {
    loading.value = false;
  }
};

// Функция для обработки данных заказа
const processOrderData = (orderData) => {
  // Теперь используем поля shipping_address или формируем адрес из отдельных полей
  let address = '';
  if (orderData.shipping_address) {
    // Если есть готовый адрес, используем его
    address = orderData.shipping_address;
  } else {
    // Иначе собираем из отдельных полей
    const addressParts = [];
    
    if (orderData.shipping_postal_code) {
      addressParts.push(`индекс: ${orderData.shipping_postal_code}`);
    }
    
    if (orderData.shipping_city) {
      addressParts.push(`г. ${orderData.shipping_city}`);
    }
    
    if (orderData.shipping_street) {
      addressParts.push(`ул. ${orderData.shipping_street}`);
    }
    
    if (orderData.shipping_house) {
      addressParts.push(`д. ${orderData.shipping_house}`);
    }
    
    if (orderData.shipping_apartment) {
      addressParts.push(`кв. ${orderData.shipping_apartment}`);
    }
    
    address = addressParts.join(', ');
  }
  
  orderDetails.value = {
    id: orderData.id,
    order_number: orderData.order_number,
    status: orderData.status,
    address: address,
    comment: orderData.shipping_comment || '',
    items: orderData.items || [],
    total: orderData.total_price,
    deliveryPrice: 0, // Получаем из данных или устанавливаем по умолчанию
    timestamp: orderData.created_at
  };
  
  console.log('Данные заказа загружены с сервера:', orderDetails.value);
};

// Основная функция загрузки деталей заказа
const loadOrderDetails = async () => {
  // Сначала пробуем загрузить из sessionStorage (если недавно оформили)
  const foundLocal = loadLocalOrderDetails();
  
  // Если не нашли в sessionStorage или перешли из истории заказов, загружаем с сервера
  if (!foundLocal && orderId !== 'успешно') {
    await loadOrderFromServer();
  }
};

// Вычисляем стоимость отдельного товара
const calculateItemTotal = (item) => {
  const price = item.product.discount > 0 ? item.product.discounted_price : item.product.price;
  return (price * item.quantity).toFixed(2);
};

// Форматирование цены
const formatPrice = (price) => {
  return Number(price).toLocaleString('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

onMounted(async () => {
  window.scrollTo(0, 0);
  await loadOrderDetails();
});
</script>

<style scoped>
.success-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.success-card {
  background-color: white;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  width: 100%;
  max-width: 600px;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin: 0 auto 20px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 20px;
}

.order-number {
  font-size: 18px;
  margin-bottom: 20px;
  color: #444;
}

.message {
  color: #666;
  margin-bottom: 30px;
  line-height: 1.6;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

/* Стили для индикатора загрузки */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(107, 70, 193, 0.3);
  border-radius: 50%;
  border-top-color: #6b46c1;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

.error-message {
  background-color: #fff5f5;
  border: 1px solid #fed7d7;
  color: #e53e3e;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

@keyframes spin {
  to { transform: rotate(360deg) }
}

.primary {
  background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
  color: white;
}

.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(107, 70, 193, 0.4);
}

.secondary {
  background-color: #f8f9fa;
  color: #6b46c1;
  border: 1px solid #e2e8f0;
}

.secondary:hover {
  background-color: #e2e8f0;
}

/* Стили для отображения деталей заказа */
.order-details {
  margin: 25px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 10px;
  text-align: left;
}

.order-details h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 10px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #555;
}

.comment {
  font-style: italic;
  color: #666;
  margin-top: 8px;
}

.order-items {
  margin-bottom: 15px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-name {
  font-weight: 500;
}

.item-quantity {
  color: #666;
  font-size: 14px;
}

.item-price {
  font-weight: 600;
}

.order-summary {
  margin-top: 20px;
  border-top: 1px solid #e2e8f0;
  padding-top: 15px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  color: #555;
}

.grand-total {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  border-top: 2px solid #eee;
  padding-top: 12px;
  margin-top: 8px;
}

@media (max-width: 600px) {
  .success-card {
    padding: 30px 20px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .order-details {
    padding: 15px;
  }
}
</style> 