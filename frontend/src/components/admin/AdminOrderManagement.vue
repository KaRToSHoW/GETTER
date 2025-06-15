<template>
  <div class="admin-order-management-modal">
    <div class="admin-order-management">
            <div class="modal-header">
        <h2>Управление заказами</h2>
        <button @click="$emit('close')" class="close-button">&times;</button>
      </div>

    <!-- Фильтры для заказов -->
    <div class="filters">
      <div class="filter-group">
        <label for="status-filter">Статус:</label>
        <select id="status-filter" v-model="statusFilter">
          <option value="">Все статусы</option>
          <option value="pending">Ожидает обработки</option>
          <option value="assembling">В сборке</option>
          <option value="shipped">Отправлен</option>
          <option value="delivered">Доставлен</option>
          <option value="canceled">Отменен</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="date-from">От:</label>
        <input type="date" id="date-from" v-model="dateFrom">
      </div>
      
      <div class="filter-group">
        <label for="date-to">До:</label>
        <input type="date" id="date-to" v-model="dateTo">
      </div>
      
      <button @click="applyFilters" class="filter-button">Применить фильтры</button>
      <button @click="resetFilters" class="reset-button">Сбросить</button>
    </div>

    <!-- Таблица заказов -->
    <div class="orders-table-container">
      <table class="orders-table">
        <thead>
          <tr>
            <th>№ заказа</th>
            <th>Клиент</th>
            <th>Дата</th>
            <th>Сумма</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id" @click="selectOrder(order)" :class="{ 'selected': selectedOrder && selectedOrder.id === order.id }">
            <td>{{ order.order_number }}</td>
            <td>{{ order.user_email || order.user_username }}</td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td>{{ formatPrice(order.total_price) }}</td>
            <td>
              <span class="status-badge" :class="`status-${order.status}`">
                {{ getStatusText(order.status) }}
              </span>
            </td>
            <td>
              <button @click.stop="openNotificationModal(order)" class="notify-btn">
                Уведомить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Детали выбранного заказа -->
    <div v-if="selectedOrder" class="order-details">
      <h3>Детали заказа #{{ selectedOrder.order_number }}</h3>
      
      <div class="details-grid">
        <div class="detail-group">
          <span class="detail-label">Клиент:</span>
          <span class="detail-value">{{ selectedOrder.user_email || selectedOrder.user_username }}</span>
        </div>
        
        <div class="detail-group">
          <span class="detail-label">Дата:</span>
          <span class="detail-value">{{ formatDate(selectedOrder.created_at) }}</span>
        </div>
        
        <div class="detail-group">
          <span class="detail-label">Статус:</span>
          <span class="detail-value status-badge" :class="`status-${selectedOrder.status}`">
            {{ getStatusText(selectedOrder.status) }}
          </span>
        </div>
        
        <div class="detail-group">
          <span class="detail-label">Сумма:</span>
          <span class="detail-value">{{ formatPrice(selectedOrder.total_price) }}</span>
        </div>
      </div>
      
      <h4>Товары в заказе</h4>
      <table class="items-table">
        <thead>
          <tr>
            <th>Товар</th>
            <th>Цена</th>
            <th>Кол-во</th>
            <th>Сумма</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in selectedOrder.items" :key="item.id">
            <td>{{ item.product.name }}</td>
            <td>{{ formatPrice(item.price) }}</td>
            <td>{{ item.quantity }}</td>
            <td>{{ formatPrice(item.price * item.quantity) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" class="total-label">Итого:</td>
            <td class="total-value">{{ formatPrice(selectedOrder.total_price) }}</td>
          </tr>
        </tfoot>
      </table>
      
      <h4>Адрес доставки</h4>
      <p v-if="selectedOrder.shipping_address">{{ selectedOrder.shipping_address }}</p>
      <p v-else class="no-data">Адрес доставки не указан</p>
      
      <div class="order-actions">
        <button @click="openNotificationModal(selectedOrder)" class="primary-button">
          Отправить уведомление
        </button>
        <button @click="updateOrderStatus(selectedOrder.id, 'assembling')" class="action-button" v-if="selectedOrder.status === 'pending'">
          Начать сборку
        </button>
        <button @click="updateOrderStatus(selectedOrder.id, 'shipped')" class="action-button" v-if="selectedOrder.status === 'assembling'">
          Отметить как отправленный
        </button>
        <button @click="updateOrderStatus(selectedOrder.id, 'delivered')" class="action-button" v-if="selectedOrder.status === 'shipped'">
          Отметить как доставленный
        </button>
        <button @click="updateOrderStatus(selectedOrder.id, 'canceled')" class="cancel-button" v-if="['pending', 'assembling'].includes(selectedOrder.status)">
          Отменить заказ
        </button>
      </div>
    </div>

    <!-- Модальное окно для отправки уведомлений -->
    <div v-if="showNotificationModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeNotificationModal">&times;</span>
        <h3>Отправить уведомление о статусе заказа</h3>
        
        <div class="form-group">
          <label for="notification-status">Статус заказа:</label>
          <select id="notification-status" v-model="notificationStatus">
            <option value="pending">Ожидает обработки</option>
            <option value="assembling">В сборке</option>
            <option value="shipped">Отправлен</option>
            <option value="delivered">Доставлен</option>
            <option value="canceled">Отменен</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="notification-comment">Комментарий (необязательно):</label>
          <textarea id="notification-comment" v-model="notificationComment" placeholder="Введите дополнительную информацию для клиента"></textarea>
        </div>
        
        <div class="modal-actions">
          <button @click="sendNotification" class="primary-button">Отправить</button>
          <button @click="closeNotificationModal" class="cancel-button">Отмена</button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, onMounted } from 'vue';
import { inject } from 'vue';

export default {
  name: 'AdminOrderManagement',
  emits: ['close'],
  setup() {
    const orders = ref([]);
    const selectedOrder = ref(null);
    const statusFilter = ref('');
    const dateFrom = ref('');
    const dateTo = ref('');
    const showNotificationModal = ref(false);
    const notificationStatus = ref('');
    const notificationComment = ref('');
    const notificationOrderId = ref(null);
    const apiBaseUrl = 'http://127.0.0.1:8000';
    const hawk = inject('hawk', null);

    // Загрузка всех заказов
    const loadOrders = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('Нет токена авторизации');
          return;
        }

        const response = await axios.get(`${apiBaseUrl}/main/user/orders/`, {
          headers: { Authorization: `Bearer ${token}` },
          params: {
            admin: true, // Специальный параметр для получения всех заказов (для админа)
            status: statusFilter.value || undefined,
            date_from: dateFrom.value || undefined,
            date_to: dateTo.value || undefined
          }
        });

        if (Array.isArray(response.data.orders)) {
          orders.value = response.data.orders;
        } else {
          console.error('Неверный формат данных заказов:', response.data);
        }
      } catch (error) {
        console.error('Ошибка при загрузке заказов:', error);
        if (hawk) {
          hawk.sendError(error, {
            type: 'admin_orders_load_error'
          });
        }
      }
    };

    // Выбор заказа для просмотра деталей
    const selectOrder = (order) => {
      selectedOrder.value = order;
    };

    // Форматирование даты
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    // Форматирование цены
    const formatPrice = (price) => {
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(price);
    };

    // Получение текстового представления статуса
    const getStatusText = (status) => {
      const statusMap = {
        'pending': 'Ожидает обработки',
        'assembling': 'В сборке',
        'shipped': 'Отправлен',
        'delivered': 'Доставлен',
        'canceled': 'Отменен'
      };
      return statusMap[status] || status;
    };

    // Применение фильтров
    const applyFilters = () => {
      loadOrders();
    };

    // Сброс фильтров
    const resetFilters = () => {
      statusFilter.value = '';
      dateFrom.value = '';
      dateTo.value = '';
      loadOrders();
    };

    // Обновление статуса заказа
    const updateOrderStatus = async (orderId, newStatus) => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('Нет токена авторизации');
          return;
        }

        const response = await axios.post(
          `${apiBaseUrl}/main/orders/${orderId}/notify/`,
          {
            status: newStatus,
            comment: `Статус заказа изменен на: ${getStatusText(newStatus)}`
          },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );

        // Обновляем статус в локальных данных
        if (selectedOrder.value && selectedOrder.value.id === orderId) {
          selectedOrder.value.status = newStatus;
        }

        // Обновляем статус в списке заказов
        const orderIndex = orders.value.findIndex(order => order.id === orderId);
        if (orderIndex !== -1) {
          orders.value[orderIndex].status = newStatus;
        }

        // Показываем уведомление об успешной отправке
        alert(response.data.message || 'Статус заказа успешно обновлен');
      } catch (error) {
        console.error('Ошибка при обновлении статуса заказа:', error);
        if (hawk) {
          hawk.sendError(error, {
            type: 'order_status_update_error',
            orderId,
            newStatus
          });
        }
        alert('Ошибка при обновлении статуса заказа');
      }
    };

    // Открытие модального окна для отправки уведомлений
    const openNotificationModal = (order) => {
      notificationOrderId.value = order.id;
      notificationStatus.value = order.status;
      notificationComment.value = '';
      showNotificationModal.value = true;
    };

    // Закрытие модального окна
    const closeNotificationModal = () => {
      showNotificationModal.value = false;
    };

    // Отправка уведомления
    const sendNotification = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('Нет токена авторизации');
          return;
        }

        const response = await axios.post(
          `${apiBaseUrl}/main/orders/${notificationOrderId.value}/notify/`,
          {
            status: notificationStatus.value,
            comment: notificationComment.value
          },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );

        // Обновляем статус в локальных данных
        if (selectedOrder.value && selectedOrder.value.id === notificationOrderId.value) {
          selectedOrder.value.status = notificationStatus.value;
        }

        // Обновляем статус в списке заказов
        const orderIndex = orders.value.findIndex(order => order.id === notificationOrderId.value);
        if (orderIndex !== -1) {
          orders.value[orderIndex].status = notificationStatus.value;
        }

        // Закрываем модальное окно
        closeNotificationModal();

        // Показываем уведомление об успешной отправке
        alert(response.data.message || 'Уведомление успешно отправлено');
      } catch (error) {
        console.error('Ошибка при отправке уведомления:', error);
        if (hawk) {
          hawk.sendError(error, {
            type: 'order_notification_error',
            orderId: notificationOrderId.value,
            status: notificationStatus.value
          });
        }
        alert('Ошибка при отправке уведомления');
      }
    };

    onMounted(() => {
      loadOrders();
    });

    return {
      orders,
      selectedOrder,
      statusFilter,
      dateFrom,
      dateTo,
      showNotificationModal,
      notificationStatus,
      notificationComment,
      loadOrders,
      selectOrder,
      formatDate,
      formatPrice,
      getStatusText,
      applyFilters,
      resetFilters,
      updateOrderStatus,
      openNotificationModal,
      closeNotificationModal,
      sendNotification
    };
  }
};
</script>

<style scoped>
.admin-order-management-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow-y: auto;
  z-index: 1000;
  padding: 20px;
}

.admin-order-management {
  background-color: white;
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin: 20px auto;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #edf2f7;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #718096;
  transition: color 0.2s;
}

.close-button:hover {
  color: #e53e3e;
}

h2 {
  margin-bottom: 20px;
  color: #333;
  font-size: 24px;
}

/* Фильтры */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 14px;
  color: #555;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filter-button,
.reset-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  align-self: flex-end;
}

.filter-button {
  background-color: #6b46c1;
  color: white;
}

.reset-button {
  background-color: #e2e8f0;
  color: #333;
}

/* Таблица заказов */
.orders-table-container {
  margin-bottom: 30px;
  overflow-x: auto;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.orders-table th,
.orders-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #edf2f7;
}

.orders-table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #4a5568;
}

.orders-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.orders-table tbody tr:hover {
  background-color: #f1f5f9;
}

.orders-table tr.selected {
  background-color: #edf2f7;
}

/* Статусы */
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background-color: #feebc8;
  color: #7b341e;
}

.status-assembling {
  background-color: #bee3f8;
  color: #2a4365;
}

.status-shipped {
  background-color: #c6f6d5;
  color: #22543d;
}

.status-delivered {
  background-color: #9ae6b4;
  color: #22543d;
}

.status-canceled {
  background-color: #fed7d7;
  color: #822727;
}

/* Детали заказа */
.order-details {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.order-details h3 {
  margin-bottom: 20px;
  color: #2d3748;
  font-size: 18px;
}

.order-details h4 {
  margin: 20px 0 10px;
  color: #4a5568;
  font-size: 16px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.detail-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-label {
  font-size: 14px;
  color: #718096;
}

.detail-value {
  font-size: 16px;
  color: #2d3748;
  font-weight: 500;
}

/* Таблица товаров */
.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  font-size: 14px;
}

.items-table th,
.items-table td {
  padding: 10px 15px;
  text-align: left;
  border-bottom: 1px solid #edf2f7;
}

.items-table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #4a5568;
}

.items-table tfoot td {
  font-weight: 600;
}

.total-label {
  text-align: right;
}

.total-value {
  color: #6b46c1;
  font-weight: 700;
}

.no-data {
  color: #a0aec0;
  font-style: italic;
}

/* Кнопки действий */
.order-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.primary-button,
.action-button,
.cancel-button,
.notify-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.primary-button {
  background-color: #6b46c1;
  color: white;
}

.primary-button:hover {
  background-color: #553c9a;
}

.action-button {
  background-color: #4299e1;
  color: white;
}

.action-button:hover {
  background-color: #3182ce;
}

.cancel-button {
  background-color: #e53e3e;
  color: white;
}

.cancel-button:hover {
  background-color: #c53030;
}

.notify-btn {
  background-color: #6b46c1;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

/* Модальное окно */
.modal {
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

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 100%;
  position: relative;
}

.close {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 24px;
  cursor: pointer;
  color: #718096;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #4a5568;
}

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .order-actions {
    flex-direction: column;
  }
  
  .primary-button,
  .action-button,
  .cancel-button {
    width: 100%;
  }
}
</style> 