<template>
  <div class="checkout-container">
    <ToastNotification ref="toast" />
    <h1 class="checkout-title">Оформление заказа</h1>

    <div class="checkout-content" v-if="!loading">
      <div class="checkout-form">
        <h2>Адрес доставки</h2>
        
        <form @submit.prevent="validateAndSubmitOrder">
          <div class="form-group">
            <label for="city">Город <span class="required">*</span></label>
            <input 
              type="text" 
              id="city" 
              v-model="addressData.city" 
              class="form-input"
              :class="{'invalid-input': validationErrors.city}"
              required
            >
            <p class="error-message" v-if="validationErrors.city">{{ validationErrors.city }}</p>
          </div>
          
          <div class="form-group">
            <label for="street">Улица <span class="required">*</span></label>
            <input 
              type="text" 
              id="street" 
              v-model="addressData.street" 
              class="form-input"
              :class="{'invalid-input': validationErrors.street}"
              required
            >
            <p class="error-message" v-if="validationErrors.street">{{ validationErrors.street }}</p>
          </div>
          
          <div class="form-row">
            <div class="form-group half">
              <label for="house">Дом <span class="required">*</span></label>
              <input 
                type="text" 
                id="house" 
                v-model="addressData.house" 
                class="form-input"
                :class="{'invalid-input': validationErrors.house}"
                required
              >
              <p class="error-message" v-if="validationErrors.house">{{ validationErrors.house }}</p>
            </div>
            
            <div class="form-group half">
              <label for="apartment">Квартира</label>
              <input 
                type="text" 
                id="apartment" 
                v-model="addressData.apartment" 
                class="form-input"
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="postalCode">Почтовый индекс <span class="required">*</span></label>
            <input 
              type="text" 
              id="postalCode" 
              v-model="addressData.postalCode" 
              class="form-input"
              :class="{'invalid-input': validationErrors.postalCode}"
              required
            >
            <p class="error-message" v-if="validationErrors.postalCode">{{ validationErrors.postalCode }}</p>
          </div>
          
          <div class="form-group">
            <label for="comment">Комментарий к заказу</label>
            <textarea 
              id="comment" 
              v-model="addressData.comment" 
              class="form-textarea"
              placeholder="Например, код домофона или предпочтительное время доставки"
            ></textarea>
          </div>
          
          <div class="order-summary">
            <h2>Ваш заказ</h2>
            <div class="order-items">
              <div v-for="item in cartItems" :key="item.id" class="order-item">
                <div class="item-info">
                  <span class="item-name">{{ item.product.name }}</span>
                  <span class="item-quantity">x {{ item.quantity }}</span>
                </div>
                <div class="item-price">{{ formatPrice(calculateItemTotal(item)) }} ₽</div>
              </div>
            </div>
            
            <div class="order-total">
              <div class="total-row">
                <span>Сумма товаров:</span>
                <span>{{ formatPrice(cartTotal) }} ₽</span>
              </div>
              <div class="total-row">
                <span>Доставка:</span>
                <span>{{ deliveryPrice > 0 ? `${formatPrice(deliveryPrice)} ₽` : 'Бесплатно' }}</span>
              </div>
              <div class="total-row grand-total">
                <span>Итого к оплате:</span>
                <span>{{ formatPrice(Number(cartTotal) + deliveryPrice) }} ₽</span>
              </div>
              
              <!-- Информация о минимальной и максимальной суммах заказа -->
              <div class="order-info">
                <p class="info-text" :class="{ 'warning': Number(cartTotal) < 500 }">
                  <i class="info-icon">ℹ️</i> 
                  Минимальная сумма заказа: 500 ₽
                  <span v-if="Number(cartTotal) < 500" class="warning-text">
                    (не достигнута)
                  </span>
                </p>
                <p class="info-text">
                  <i class="info-icon">ℹ️</i> 
                  Бесплатная доставка от 5000 ₽
                </p>
              </div>
            </div>
          </div>
          
          <button type="submit" class="checkout-button" :disabled="isSubmitting">
            <span v-if="isSubmitting">Оформляем заказ...</span>
            <span v-else>Оформить заказ</span>
          </button>
        </form>
      </div>
    </div>
    
    <div class="loading-container" v-else>
      <div class="loading-spinner"></div>
      <p>Загрузка информации о заказе...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import ToastNotification from './ToastNotification.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';
const toast = ref(null);
const router = useRouter();
const loading = ref(true);
const isSubmitting = ref(false);
const cartItems = ref([]);
const deliveryPrice = ref(0);

// Данные формы адреса
const addressData = ref({
  city: '',
  street: '',
  house: '',
  apartment: '',
  postalCode: '',
  comment: ''
});

// Объект для хранения ошибок валидации
const validationErrors = ref({
  city: '',
  street: '',
  house: '',
  postalCode: ''
});

onMounted(async () => {
  await fetchCartItems();
  await loadSavedAddress();
});

const fetchCartItems = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    
    const response = await axios.get(`${API_BASE_URL}/main/cart/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    cartItems.value = response.data.items;
    
    // Рассчитываем стоимость доставки (можно реализовать собственную логику)
    calculateDeliveryPrice();
    
    loading.value = false;
  } catch (err) {
    console.error('Ошибка при получении корзины:', err);
    toast.value?.showToast('Не удалось загрузить данные корзины', 'error');
    loading.value = false;
  }
};

// Расчет стоимости доставки
const calculateDeliveryPrice = () => {
  // Логика расчета стоимости доставки
  // Например, бесплатная доставка при заказе от 5000 рублей
  const total = Number(cartTotal.value);
  deliveryPrice.value = total >= 5000 ? 0 : 500;
};

// Вычисляем общую стоимость заказа
const cartTotal = computed(() => {
  return cartItems.value.reduce((total, item) => {
    const price = item.product.discount > 0 ? item.product.discounted_price : item.product.price;
    return total + (price * item.quantity);
  }, 0).toFixed(2);
});

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

// Валидация адреса доставки
const validateDeliveryAddress = () => {
  let isValid = true;
  validationErrors.value = {
    city: '',
    street: '',
    house: '',
    postalCode: ''
  };
  
  // Проверка города
  if (!addressData.value.city) {
    validationErrors.value.city = 'Пожалуйста, укажите город';
    isValid = false;
  } else if (!/^[А-Яа-я\s-]+$/i.test(addressData.value.city)) {
    validationErrors.value.city = 'Название города должно содержать только кириллические буквы';
    isValid = false;
  }
  
  // Проверка улицы
  if (!addressData.value.street) {
    validationErrors.value.street = 'Пожалуйста, укажите улицу';
    isValid = false;
  } else if (!/^[А-Яа-я0-9\s.,/-]+$/i.test(addressData.value.street)) {
    validationErrors.value.street = 'Название улицы содержит недопустимые символы';
    isValid = false;
  }
  
  // Проверка номера дома
  if (!addressData.value.house) {
    validationErrors.value.house = 'Пожалуйста, укажите номер дома';
    isValid = false;
  } else if (!/^[0-9А-Яа-я/-]+$/i.test(addressData.value.house)) {
    validationErrors.value.house = 'Недопустимый формат номера дома';
    isValid = false;
  }
  
  // Проверка почтового индекса (6 цифр для России)
  if (!addressData.value.postalCode) {
    validationErrors.value.postalCode = 'Пожалуйста, укажите почтовый индекс';
    isValid = false;
  } else if (!/^\d{6}$/.test(addressData.value.postalCode)) {
    validationErrors.value.postalCode = 'Почтовый индекс должен состоять из 6 цифр';
    isValid = false;
  }
  
  return isValid;
};

// Валидация минимальной и максимальной суммы заказа
const validateOrderAmount = () => {
  const MIN_ORDER_AMOUNT = 500; // Минимальная сумма заказа (в рублях)
  const MAX_ORDER_AMOUNT = 100000; // Максимальная сумма заказа (в рублях)
  
  const totalAmount = Number(cartTotal.value);
  
  if (totalAmount < MIN_ORDER_AMOUNT) {
    toast.value?.showToast(`Минимальная сумма заказа составляет ${MIN_ORDER_AMOUNT} ₽`, 'error');
    return false;
  }
  
  if (totalAmount > MAX_ORDER_AMOUNT) {
    toast.value?.showToast(`Максимальная сумма заказа составляет ${MAX_ORDER_AMOUNT} ₽`, 'error');
    return false;
  }
  
  return true;
};

// Функция для валидации и отправки заказа
const validateAndSubmitOrder = async () => {
  if (!validateDeliveryAddress()) {
    toast.value?.showToast('Пожалуйста, проверьте правильность ввода адреса доставки', 'error');
    return;
  }
  
  if (!validateOrderAmount()) {
    return;
  }
  
  // Если все валидации прошли успешно, отправляем заказ
  await submitOrder();
};

// Загрузка последнего использованного адреса
const loadSavedAddress = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    // Получаем список заказов пользователя
    const response = await axios.get(`${API_BASE_URL}/main/user/orders/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    // Ищем последний оформленный заказ (не корзину)
    const orders = response.data.orders || [];
    if (orders.length > 0) {
      // Берем первый заказ (самый новый, так как они отсортированы)
      const lastOrder = orders[0];
      
      // Проверяем, есть ли информация о доставке в заказе
      if (lastOrder.shipping_city || lastOrder.shipping_street) {
        addressData.value = {
          city: lastOrder.shipping_city || '',
          street: lastOrder.shipping_street || '',
          house: lastOrder.shipping_house || '',
          apartment: lastOrder.shipping_apartment || '',
          postalCode: lastOrder.shipping_postal_code || '',
          comment: ''  // Комментарий оставляем пустым для нового заказа
        };
        console.log('Загружен адрес из предыдущего заказа:', addressData.value);
      }
    } else {
      console.log('Не найдено предыдущих заказов с адресом доставки');
    }
  } catch (e) {
    console.error('Ошибка при загрузке адреса из заказов:', e);
    
    // Если не удалось загрузить с сервера, пробуем localStorage (для обратной совместимости)
    try {
      const savedAddress = localStorage.getItem('lastShippingAddress');
      if (savedAddress) {
        const parsedAddress = JSON.parse(savedAddress);
        addressData.value.city = parsedAddress.city || '';
        addressData.value.street = parsedAddress.street || '';
        addressData.value.house = parsedAddress.house || '';
        addressData.value.apartment = parsedAddress.apartment || '';
        addressData.value.postalCode = parsedAddress.postalCode || '';
        console.log('Загружен адрес из localStorage (совместимость):', addressData.value);
      }
    } catch (localError) {
      console.error('Ошибка при загрузке адреса из localStorage:', localError);
    }
  }
};

// Функция для отправки заказа на сервер
const submitOrder = async () => {
  isSubmitting.value = true;
  try {
    const token = localStorage.getItem('token');
    
    // Создаем объект для отправки с правильными полями доставки
    const orderData = {
      shipping_city: addressData.value.city,
      shipping_street: addressData.value.street,
      shipping_house: addressData.value.house,
      shipping_apartment: addressData.value.apartment,
      shipping_postal_code: addressData.value.postalCode,
      shipping_comment: addressData.value.comment || '',
      total_price: parseFloat(cartTotal.value) + deliveryPrice.value
    };
    
    console.log('Отправляемые данные заказа:', orderData);
    console.log('Общая стоимость заказа:', orderData.total_price);
    
    const response = await axios.post(`${API_BASE_URL}/main/orders/create/`, orderData, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    toast.value?.showToast('Заказ успешно оформлен!', 'success');
    
    // Перенаправляем на страницу успешного оформления заказа
    console.log('Данные созданного заказа:', response.data);
    
    // Создаем объект с деталями заказа для sessionStorage
    const orderDetails = {
      id: response.data.order_id,
      order_number: response.data.order_number,
      status: 'assembling',
      address: response.data.shipping_address || formatAddress(orderData),
      comment: orderData.shipping_comment || '',
      items: cartItems.value.map(item => ({
        id: item.id,
        product: item.product,
        quantity: item.quantity
      })),
      total: parseFloat(cartTotal.value),
      deliveryPrice: deliveryPrice.value,
      timestamp: new Date().toISOString()
    };
    
    // Сохраняем детали заказа в sessionStorage для использования на странице успеха
    sessionStorage.setItem('lastOrderDetails', JSON.stringify(orderDetails));
    
    // Используем order_number из ответа API
    const orderId = response.data.order_number || response.data.order_id || 'успешно';
    
    router.push({
      name: 'order-success',
      params: { orderId: orderId }
    });
    
  } catch (err) {
    console.error('Ошибка при оформлении заказа:', err);
    if (err.response && err.response.data) {
      console.error('Детали ошибки:', err.response.data);
      toast.value?.showToast('Ошибка при оформлении заказа: ' + JSON.stringify(err.response.data), 'error');
    } else {
      toast.value?.showToast('Ошибка при оформлении заказа: ' + err.message, 'error');
    }
  } finally {
    isSubmitting.value = false;
  }
};

// Функция для форматирования адреса доставки
const formatAddress = (addressData) => {
  const addressParts = [];
  
  if (addressData.shipping_postal_code) {
    addressParts.push(`индекс: ${addressData.shipping_postal_code}`);
  }
  
  if (addressData.shipping_city) {
    addressParts.push(`г. ${addressData.shipping_city}`);
  }
  
  if (addressData.shipping_street) {
    addressParts.push(`ул. ${addressData.shipping_street}`);
  }
  
  if (addressData.shipping_house) {
    addressParts.push(`д. ${addressData.shipping_house}`);
  }
  
  if (addressData.shipping_apartment) {
    addressParts.push(`кв. ${addressData.shipping_apartment}`);
  }
  
  return addressParts.join(', ');
};
</script>

<style scoped>
.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.checkout-title {
  font-size: 2.2rem;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
  font-weight: 600;
}

.checkout-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.checkout-form {
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
  padding: 30px;
}

.checkout-form h2 {
  font-size: 1.8rem;
  color: #444;
  margin-bottom: 20px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group.half {
  flex: 1;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  color: #333;
  transition: all 0.3s ease;
}

.form-input:focus, .form-textarea:focus {
  border-color: #6b46c1;
  outline: none;
  box-shadow: 0 0 0 2px rgba(107, 70, 193, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.invalid-input {
  border-color: #e53e3e;
  background-color: #fff5f5;
}

.error-message {
  color: #e53e3e;
  font-size: 14px;
  margin-top: 5px;
}

.required {
  color: #e53e3e;
}

.order-summary {
  margin-top: 40px;
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
}

.order-items {
  margin-bottom: 20px;
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

.order-total {
  margin-top: 20px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  color: #555;
}

.grand-total {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  border-top: 2px solid #eee;
  padding-top: 15px;
  margin-top: 10px;
}

.order-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f1f5f9;
  border-radius: 8px;
  font-size: 14px;
}

.info-text {
  display: flex;
  align-items: center;
  margin: 5px 0;
  color: #4b5563;
}

.info-icon {
  margin-right: 8px;
  font-size: 16px;
}

.warning {
  color: #e53e3e;
}

.warning-text {
  font-weight: 600;
  margin-left: 5px;
}

.checkout-button {
  background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 30px;
  box-shadow: 0 4px 10px rgba(107, 70, 193, 0.3);
}

.checkout-button:hover {
  background: linear-gradient(135deg, #805ad5 0%, #6b46c1 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(107, 70, 193, 0.4);
}

.checkout-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: translateY(0);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(107, 70, 193, 0.3);
  border-radius: 50%;
  border-top-color: #6b46c1;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg) }
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .checkout-form {
    padding: 20px;
  }
}
</style> 