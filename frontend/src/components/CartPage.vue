<template>
    <div class="cart-container">
        <ToastNotification ref="toast" />
        <h2 class="cart-title">Корзина</h2>
        
        <!-- Индикатор загрузки -->
        <div v-if="isLoading" class="loading-spinner-container">
            <div class="loading-spinner"></div>
            <p>Загрузка корзины...</p>
        </div>
        
        <div v-else-if="cart.items && cart.items.length > 0" class="cart-items">
            <div class="cart-header">
                <div class="select-all-container">
                    <input 
                        type="checkbox" 
                        :checked="isAllSelected" 
                        @change="toggleSelectAll" 
                        id="select-all" 
                        class="select-all-checkbox"
                    />
                    <label for="select-all">Выбрать все</label>
                </div>
                <button @click="clearCart" class="clear-cart-btn">
                    Очистить корзину
                </button>
            </div>
            <div v-for="item in cart.items" :key="item.id" class="cart-item">
                <input type="checkbox" v-model="selectedItems" :value="item.id" class="item-checkbox" />
                <div class="cart-item-image-wrapper">
                    <img v-if="item.product.image" :src="`${$apiBaseUrl}${item.product.image}`" alt="Product Image"
                        class="cart-item-image" />
                </div>
                <div class="cart-item-details">
                    <router-link :to="`/product/${item.product.id}`" class="cart-item-name">
                        {{ item.product.name }}
                    </router-link>
                    <p class="cart-item-sku">Артикул: {{ item.product.sku }}</p>
                    <p class="cart-item-category">Категория: {{ item.product.category.name }}</p>
                    <div v-if="item.product.specifications" class="specifications">
                        <span v-for="(value, key) in item.product.specifications" :key="key" class="spec-item">
                            <strong>{{ key.replace(/_/g, ' ') }}:</strong> {{ value }}
                        </span>
                    </div>

                    <div class="quantity-control">
                        <button @click="decrementQuantity(item)" class="quantity-button">
                            -
                            <span class="sr-only">Уменьшить количество</span>
                        </button>
                        <input type="number" v-model.number="item.quantity" @change="validateAndUpdateQuantity(item)" min="1"
                            class="quantity-input" />
                        <button @click="incrementQuantity(item)" class="quantity-button">
                            +
                            <span class="sr-only">Увеличить количество</span>
                        </button>
                    </div>
                    <div class="price-container">
                        <span v-if="item.product.discount > 0" class="original-price">{{ formatPrice(item.product.price) }}</span>
                        <span class="current-price">{{ formatPrice(item.product.discounted_price) }}</span>
                        <span v-if="item.product.discount > 0" class="discount-badge">-{{ item.product.discount }}%</span>
                    </div>
                </div>
                <div class="cart-item-actions">
                    <button @click="toggleWishlist(item.product)"
                        :class="['wishlist-button', { 'active': isInWishlist(item.product.id) }]">
                        <span class="heart-icon">❤️</span>
                        <span class="sr-only">{{ isInWishlist(item.product.id) ? 'Удалить из избранного' : 'Добавить в избранное' }}</span>
                    </button>
                    <button @click="removeItem(item.id)" class="remove-button">
                        <span class="trash-icon">🗑️</span>
                        <span class="sr-only">Удалить из корзины</span>
                    </button>
                </div>
            </div>
            <div class="cart-total">
                <div class="cart-summary">
                    <h3>Итого</h3>
                    <div class="summary-content">
                        <div class="summary-row">
                            <span>Товары ({{ getSelectedItemsCount }})</span>
                            <span>{{ formatPrice(calculateSelectedOriginalTotal()) }}</span>
                        </div>
                        <div v-if="calculateTotalDiscount() > 0" class="summary-row discount">
                            <span>Скидка</span>
                            <span>-{{ formatPrice(calculateTotalDiscount()) }}</span>
                        </div>
                        <div class="summary-row total">
                            <span>Итого к оплате</span>
                            <span>{{ formatPrice(calculateSelectedTotal()) }}</span>
                        </div>
                        <button 
                            class="checkout-button" 
                            :disabled="selectedItems.length === 0"
                            @click="checkout"
                        >
                            Оформить заказ
                        </button>
                    </div>
                </div>
                <div class="promo-code-container">
                    <div class="promo-input-group">
                        <input 
                            type="text" 
                            v-model="promoCode" 
                            placeholder="Введите промокод" 
                            class="promo-input"
                            :disabled="isPromoLoading" 
                        />
                        <button 
                            @click="applyPromoCode" 
                            class="apply-promo-btn"
                            :disabled="!promoCode || isPromoLoading"
                        >
                            <span v-if="isPromoLoading" class="promo-spinner"></span>
                            <span v-else>Применить</span>
                        </button>
                    </div>
                    <p v-if="promoError" class="promo-error">{{ promoError }}</p>
                    <p v-if="promoDiscount > 0" class="promo-success">Промокод применен! Скидка: {{ formatPrice(promoDiscount) }} ₽</p>
                </div>
                <div class="cart-buttons">
                    <router-link to="/catalog" class="continue-shopping-btn">
                        Продолжить покупки
                    </router-link>
                </div>
            </div>
        </div>
        <div v-else class="no-data">
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <h3>Корзина пуста</h3>
                <p>Ваша корзина пуста. Добавьте товары, чтобы сделать заказ.</p>
                <router-link to="/catalog" class="continue-shopping-btn">
                    Перейти в каталог
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { inject } from 'vue';
import ToastNotification from './ToastNotification.vue';
import { useRouter } from 'vue-router';

const $apiBaseUrl = inject('$apiBaseUrl', 'http://127.0.0.1:8000');
const router = useRouter();

const cart = ref({ items: [], total_price: 0 });
const selectedItems = ref([]);
const wishlist = ref([]);
const toast = ref(null);
const currentUser = ref(null);
const isLoading = ref(true);
const promoCode = ref('');
const promoDiscount = ref(0);
const promoError = ref('');
const isPromoLoading = ref(false);

const loadCurrentUser = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get(`${$apiBaseUrl}/users/profile/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            currentUser.value = response.data;
            console.log('Текущий пользователь:', currentUser.value);
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
        toast.value.showToast('Ошибка при загрузке данных пользователя', 'error');
    }
};

const loadLocalCart = () => {
    try {
        const localCartStr = localStorage.getItem('localCart');
        console.log('Получены данные из localStorage:', localCartStr ? 'данные есть' : 'данные отсутствуют');
        
        if (!localCartStr) {
            console.log('Локальная корзина пуста');
            return { items: [], total_price: 0 };
        }
        
        let parsedCart;
        try {
            parsedCart = JSON.parse(localCartStr);
            console.log('Данные корзины успешно разобраны из JSON');
        } catch (parseError) {
            console.error('Ошибка парсинга JSON корзины:', parseError);
            return { items: [], total_price: 0 };
        }
        
        // Проверка корректности данных
        if (!parsedCart || typeof parsedCart !== 'object') {
            console.error('Некорректные данные в localStorage:', parsedCart);
            return { items: [], total_price: 0 };
        }
        
        // Убедимся, что свойство items является массивом
        const items = Array.isArray(parsedCart.items) ? parsedCart.items : [];
        
        // Проверим и восстановим каждый элемент корзины
        const validItems = items.filter(item => {
            // Базовая проверка элемента
            if (!item || typeof item !== 'object') {
                console.warn('Некорректный элемент корзины:', item);
                return false;
            }
            
            // Проверка наличия идентификатора продукта
            if (!item.product_id) {
                console.warn('У элемента корзины отсутствует product_id:', item);
                return false;
            }
            
            // Проверка количества
            const quantity = parseInt(item.quantity);
            if (isNaN(quantity) || quantity <= 0) {
                console.warn('Некорректное количество товара:', item);
                return false;
            }
            item.quantity = quantity; // Нормализация количества
            
            // Проверка и нормализация продукта
            if (!item.product) {
                console.warn('У элемента корзины отсутствует продукт:', item);
                // Создаем минимальный объект продукта
                item.product = {
                    id: item.product_id,
                    name: 'Неизвестный товар',
                    price: 0
                };
            } else if (typeof item.product !== 'object') {
                console.warn('Некорректный объект продукта:', item.product);
                item.product = {
                    id: item.product_id,
                    name: 'Некорректный товар',
                    price: 0
                };
            }
            
            // Проверка наличия категории
            if (!item.product.category) {
                item.product.category = { name: 'Без категории' };
            }
            
            return true;
        });
        
        console.log(`Загружено ${validItems.length} товаров из локального хранилища`);
        
        // Проверим возраст данных - если старше 7 дней, выдаем предупреждение
        if (parsedCart.updated_at) {
            const updateDate = new Date(parsedCart.updated_at);
            const now = new Date();
            const diffDays = Math.floor((now - updateDate) / (1000 * 60 * 60 * 24));
            
            if (diffDays > 7) {
                console.warn(`Данные корзины устарели (${diffDays} дней)`);
            }
        }
        
        return {
            items: validItems,
            total_price: typeof parsedCart.total_price === 'number' ? parsedCart.total_price : 0
        };
    } catch (error) {
        console.error('Критическая ошибка загрузки локальной корзины:', error);
        return { items: [], total_price: 0 };
    }
};

const loadCartData = async () => {
    isLoading.value = true;
    console.log('Начало загрузки данных корзины');
    
    try {
        const token = localStorage.getItem('token');
        if (token) {
            console.log('Авторизованный пользователь, загрузка с сервера');
            try {
                const [cartResponse, wishlistResponse] = await Promise.all([
                    axios.get(`${$apiBaseUrl}/main/cart/`, {
                        headers: { Authorization: `Bearer ${token}` }
                    }),
                    axios.get(`${$apiBaseUrl}/main/wishlist/check/`, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                ]);
                
                console.log('Данные корзины получены с сервера:', cartResponse.data);
                
                // Проверка структуры ответа
                if (!cartResponse.data || (cartResponse.data.items === undefined)) {
                    console.error('Неверная структура ответа:', cartResponse.data);
                    throw new Error('Неверная структура ответа от сервера');
                }

                const cartData = {
                    ...cartResponse.data,
                    total_price: typeof cartResponse.data.total_price === 'number' 
                        ? cartResponse.data.total_price 
                        : parseFloat(cartResponse.data.total_price) || 0,
                    items: Array.isArray(cartResponse.data.items) ? cartResponse.data.items : []
                };
                
                // Сохраняем оригинальное количество для каждого элемента
                cartData.items.forEach(item => {
                    item._originalQuantity = item.quantity;
                });
                
                cart.value = cartData;
                wishlist.value = wishlistResponse.data.wishlist || [];

                // Проверка и синхронизация с локальной корзиной
                const localCart = loadLocalCart();
                if (localCart.items && localCart.items.length > 0) {
                    console.log('Найдена локальная корзина, выполняем слияние');
                    await mergeLocalCartWithServer(localCart);
                    localStorage.removeItem('localCart');
                }
            } catch (serverError) {
                console.error('Ошибка получения данных с сервера:', serverError);
                throw serverError;
            }
        } else {
            console.log('Неавторизованный пользователь, загрузка из локального хранилища');
            const localCartData = loadLocalCart();
            console.log('Данные локальной корзины:', localCartData);
            cart.value = localCartData;
        }
    } catch (error) {
        console.error('Ошибка загрузки данных корзины:', error);
        console.error('Детали ошибки:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при загрузке данных корзины', 'error');
        
        // В случае ошибки загружаем из локального хранилища
        try {
            const localCartData = loadLocalCart();
            console.log('Аварийная загрузка из локального хранилища:', localCartData);
            cart.value = localCartData;
        } catch (localError) {
            console.error('Ошибка загрузки из локального хранилища:', localError);
            // В крайнем случае инициализируем пустую корзину
            cart.value = { items: [], total_price: 0 };
        }
    } finally {
        isLoading.value = false;
        console.log('Завершение загрузки данных корзины');
    }
};

const mergeLocalCartWithServer = async (localCart) => {
    try {
        const token = localStorage.getItem('token');
        if (!token || !localCart.items.length) return;

        const promises = localCart.items.map(item => {
            return axios.post(`${$apiBaseUrl}/main/cart/add/`, {
                product_id: item.product_id,
                quantity: item.quantity
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
        });

        await Promise.all(promises);
        
        const cartResponse = await axios.get(`${$apiBaseUrl}/main/cart/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        const cartData = {
            ...cartResponse.data,
            total_price: typeof cartResponse.data.total_price === 'number' ? cartResponse.data.total_price : parseFloat(cartResponse.data.total_price) || 0,
            items: cartResponse.data.items || []
        };
        
        cartData.items.forEach(item => {
            item._originalQuantity = item.quantity;
        });
        
        cart.value = cartData;
        
        toast.value.showToast('Корзина синхронизирована с сервером', 'success');
    } catch (error) {
        console.error('Ошибка объединения корзин:', error);
    }
};

// Функции уже не используются, заменены на incrementQuantity и decrementQuantity

const updateQuantity = async (item, change) => {
    try {
        const token = localStorage.getItem('token');
        
        let newQuantity = change !== undefined ? item.quantity + change : item.quantity;

        if (newQuantity <= 0) {
            await removeItem(item.id);
            return;
        }

        if (item.product && item.product.stock && newQuantity > item.product.stock) {
            toast.value.showToast('Нельзя добавить больше, чем есть в наличии!', 'warning');
            item.quantity = Math.min(item.quantity, item.product.stock);
            return;
        }

        if (token) {
            if (!canEditCartItem(item)) {
                toast.value.showToast('У вас нет прав на редактирование этого товара', 'error');
                await loadCartData();
                return;
            }

            const quantityDifference = change !== undefined ? change : newQuantity - item._originalQuantity;
            
            await axios.post(`${$apiBaseUrl}/main/cart/add/`, {
                product_id: item.product.id,
                quantity: quantityDifference
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            await loadCartData();
        } else {
            item.quantity = newQuantity;
            
            // Сохраняем изменения в localStorage
            saveLocalCart();
        }
    } catch (error) {
        console.error('Ошибка обновления количества:', error);
        toast.value.showToast('Ошибка при обновлении количества', 'error');
    }
};

const canEditCartItem = (item) => {
    if (!currentUser.value) return true;
    
    if (currentUser.value.is_superuser) return true;
    
    // Если у товара нет user_id, то считаем его доступным
    if (!item.user_id) return true;
    
    return item.user_id === currentUser.value.id;
};

const canDeleteFromCart = (item) => {
    // Для неавторизованных пользователей (локальная корзина)
    // всегда разрешаем удаление
    if (!localStorage.getItem('token')) {
        console.log('Неавторизованный пользователь - разрешаем удаление');
        return true;
    }
    
    // Товары без user_id считаем локальными и разрешаем удаление
    if (!item.user_id) {
        console.log('Товар без user_id (локальный) - разрешаем удаление');
        return true;
    }
    
    // Админ может удалять любые товары
    if (currentUser.value && currentUser.value.is_superuser) {
        console.log('Пользователь является администратором - разрешаем удаление');
        return true;
    }
    
    // Важно: если у товара не указан user_id, или если текущий пользователь не загружен,
    // считаем товар принадлежащим текущему пользователю
    if (!currentUser.value) {
        console.log('Пользователь не загружен, но авторизован - разрешаем удаление по умолчанию');
        return true;
    }
    
    // Явная проверка, принадлежит ли товар текущему пользователю
    const isOwner = (item.user_id === currentUser.value.id);
    
    if (isOwner) {
        console.log('Товар принадлежит текущему пользователю - разрешаем удаление');
        return true;
    }
    
    // Ключевое предположение: все товары в корзине принадлежат текущему пользователю
    // Если мы дошли сюда, то что-то пошло не так с данными user_id
    console.warn('Несоответствие ID пользователя:', {
        itemUserId: item.user_id, 
        currentUserId: currentUser.value ? currentUser.value.id : 'не загружен'
    });
    
    // По умолчанию разрешаем удаление - предполагаем, что все товары в корзине
    // принадлежат текущему пользователю
    return true;
};



const isInWishlist = computed(() => (productId) => {
    return wishlist.value.includes(productId);
});

const toggleWishlist = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
        toast.value.showToast('Пожалуйста, войдите в систему для управления списком желаемого.', 'warning');
        return;
    }

    try {
        if (isInWishlist.value(product.id)) {
            await axios.delete(`${$apiBaseUrl}/main/wishlist/remove/${product.id}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value = wishlist.value.filter(id => id !== product.id);
            toast.value.showToast(`Товар "${product.name}" удален из желаемого!`, 'success');
        } else {
            await axios.post(`${$apiBaseUrl}/main/wishlist/add/`, {
                product_id: product.id
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value.push(product.id);
            toast.value.showToast(`Товар "${product.name}" добавлен в желаемое!`, 'success');
        }
    } catch (error) {
        console.error('Ошибка управления желаемым:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при управлении желаемым.', 'error');
    }
};

const isAllSelected = computed(() => {
    return cart.value.items.length > 0 && selectedItems.value.length === cart.value.items.length;
});

const toggleSelectAll = () => {
    if (isAllSelected.value) {
        selectedItems.value = [];
    } else {
        selectedItems.value = cart.value.items.map(item => item.id);
    }
};

const getSelectedItemsCount = computed(() => {
    let count = 0;
    cart.value.items.forEach(item => {
        if (selectedItems.value.includes(item.id)) {
            count += item.quantity;
        }
    });
    return count;
});

const getSubtotal = computed(() => {
    let total = 0;
    cart.value.items.forEach(item => {
        if (selectedItems.value.includes(item.id)) {
            total += item.product.price * item.quantity;
        }
    });
    return total;
});

const getTotal = computed(() => {
    return getSubtotal.value - promoDiscount.value;
});

const formatPrice = (price) => {
    return Number(price).toLocaleString('ru-RU', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + ' ₽';
};

const calculateSelectedOriginalTotal = () => {
    let total = 0;
    cart.value.items.forEach(item => {
        if (selectedItems.value.includes(item.id)) {
            total += item.product.price * item.quantity;
        }
    });
    return total;
};

const calculateSelectedTotal = () => {
    let total = 0;
    cart.value.items.forEach(item => {
        if (selectedItems.value.includes(item.id)) {
            total += item.product.discounted_price * item.quantity;
        }
    });
    return total;
};

const calculateTotalDiscount = () => {
    return calculateSelectedOriginalTotal() - calculateSelectedTotal();
};

const clearCart = async () => {
    try {
        if (!selectedItems.value.length) {
            toast.value.showToast('Выберите товары для удаления', 'warning');
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) {
            toast.value.showToast('Необходимо авторизоваться', 'warning');
            return;
        }

        const confirmClear = confirm('Вы уверены, что хотите удалить выбранные товары из корзины?');
        if (!confirmClear) return;

        const promises = selectedItems.value.map(itemId => {
            const item = cart.value.items.find(i => i.id === itemId);
            if (item && canDeleteFromCart(item)) {
                return axios.delete(`${$apiBaseUrl}/main/cart/remove/${itemId}/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
            return Promise.resolve();
        });

        await Promise.all(promises);
        
        selectedItems.value = [];
        await loadCartData();
        toast.value.showToast('Выбранные товары удалены из корзины', 'success');
    } catch (error) {
        console.error('Ошибка очистки корзины:', error);
        toast.value.showToast('Ошибка при удалении товаров из корзины', 'error');
    }
};

const checkout = async () => {
    try {
        console.log('Начало оформления заказа');
        const token = localStorage.getItem('token');
        if (!token) {
            console.log('Пользователь не авторизован');
            toast.value.showToast('Пожалуйста, войдите в систему для оформления заказа', 'warning');
            return;
        }

        if (selectedItems.value.length === 0) {
            console.log('Не выбраны товары для оформления заказа');
            toast.value.showToast('Выберите товары для оформления заказа', 'warning');
            return;
        }

        // Перенаправляем пользователя на страницу оформления заказа
        router.push('/checkout');
    } catch (error) {
        console.error('Ошибка перехода к оформлению заказа:', error);
        toast.value.showToast('Ошибка при переходе к оформлению заказа', 'error');
    }
};

const applyPromoCode = async () => {
    if (!promoCode.value) return;
    
    isPromoLoading.value = true;
    promoError.value = '';
    
    try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const validPromoCodes = {
            'WELCOME10': 0.1,
            'SUMMER20': 0.2,
            'SALE30': 0.3,
            'DISCOUNT5': 500
        };
        
        const discount = validPromoCodes[promoCode.value.toUpperCase()];
        
        if (discount) {
            if (discount < 1) {
                promoDiscount.value = getSubtotal.value * discount;
            } else {
                promoDiscount.value = Math.min(discount, getSubtotal.value);
            }
            
            toast.value.showToast('Промокод успешно применен!', 'success');
        } else {
            promoError.value = 'Недействительный промокод';
            promoDiscount.value = 0;
        }
    } catch (error) {
        console.error('Ошибка применения промокода:', error);
        promoError.value = 'Ошибка при применении промокода';
        promoDiscount.value = 0;
    } finally {
        isPromoLoading.value = false;
    }
};

const saveLocalCart = () => {
    try {
        console.log('Начало сохранения локальной корзины');
        
        // Если корзина пуста, просто удаляем запись из localStorage
        if (!cart.value.items || cart.value.items.length === 0) {
            localStorage.removeItem('localCart');
            console.log('Локальная корзина пуста, удаляем из localStorage');
            return;
        }
        
        // Подготавливаем данные для сохранения, удаляя ненужные или слишком большие поля
        const localCart = {
            items: cart.value.items.map(item => {
                // Очищаем продукт от лишних данных, чтобы уменьшить размер хранилища
                const simplifiedProduct = {
                    id: item.product.id,
                    name: item.product.name,
                    price: item.product.price,
                    sku: item.product.sku,
                    image: item.product.image,
                    stock: item.product.stock,
                    discount: item.product.discount
                };
                
                // Если есть категория, добавляем базовую информацию
                if (item.product.category) {
                    simplifiedProduct.category = {
                        id: item.product.category.id,
                        name: item.product.category.name
                    };
                }
                
                return {
                    id: item.id,
                    product_id: item.product.id,
                    product: simplifiedProduct,
                    quantity: item.quantity
                };
            }),
            total_price: getTotal.value,
            updated_at: new Date().toISOString()
        };
        
        // Сохраняем в localStorage с обработкой ошибок
        try {
            const serialized = JSON.stringify(localCart);
            localStorage.setItem('localCart', serialized);
            console.log(`Локальная корзина сохранена (${localCart.items.length} товаров, ${serialized.length} байт)`);
        } catch (storageError) {
            // Если произошла ошибка при сохранении (например, превышен лимит localStorage)
            console.error('Ошибка при записи в localStorage:', storageError);
            
            // Пытаемся сохранить упрощенную версию без детальной информации о продукте
            const simplifiedCart = {
                items: localCart.items.map(item => ({
                    id: item.id,
                    product_id: item.product_id,
                    quantity: item.quantity
                })),
                total_price: localCart.total_price,
                updated_at: localCart.updated_at
            };
            
            try {
                localStorage.setItem('localCart', JSON.stringify(simplifiedCart));
                console.log('Сохранена упрощенная версия корзины');
            } catch (fallbackError) {
                console.error('Не удалось сохранить даже упрощенную версию:', fallbackError);
            }
        }
    } catch (error) {
        console.error('Критическая ошибка сохранения локальной корзины:', error);
    }
};

const validateAndUpdateQuantity = async (item) => {
    try {
        // Получаем актуальную информацию о товаре для проверки доступного количества
        const token = localStorage.getItem('token');
        const response = await axios.get(`${$apiBaseUrl}/main/products/${item.product.id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        const availableStock = response.data.stock;
        
        // Проверяем, не превышает ли запрашиваемое количество доступное на складе
        if (item.quantity > availableStock) {
            // Устанавливаем максимально доступное количество
            item.quantity = availableStock;
            toast.value?.showToast(`Доступно только ${availableStock} шт. этого товара`, 'warning');
        }
        
        // Обновляем количество в корзине
        await updateQuantity(item);
    } catch (error) {
        console.error('Ошибка при валидации количества:', error);
        toast.value?.showToast('Ошибка при обновлении количества', 'error');
    }
};

const incrementQuantity = async (item) => {
    try {
        // Получаем актуальную информацию о товаре
        const token = localStorage.getItem('token');
        const response = await axios.get(`${$apiBaseUrl}/main/products/${item.product.id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        const availableStock = response.data.stock;
        
        // Проверяем, не превышает ли запрашиваемое количество доступное на складе
        if (item.quantity >= availableStock) {
            toast.value?.showToast(`Доступно только ${availableStock} шт. этого товара`, 'warning');
            return;
        }
        
        // Увеличиваем количество и обновляем корзину
        item.quantity++;
        await updateQuantity(item);
    } catch (error) {
        console.error('Ошибка при увеличении количества:', error);
        toast.value?.showToast('Ошибка при обновлении количества', 'error');
    }
};

const decrementQuantity = async (item) => {
    if (item.quantity > 1) {
        item.quantity--;
        await updateQuantity(item);
    }
};

const removeItem = async (itemId) => {
    try {
        const token = localStorage.getItem('token');
        await axios.delete(`${$apiBaseUrl}/main/cart/remove/${itemId}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        toast.value?.showToast('Товар удален из корзины', 'success');
        await loadCartData();
    } catch (err) {
        console.error('Ошибка при удалении товара из корзины:', err);
        toast.value?.showToast('Не удалось удалить товар из корзины', 'error');
    }
};

onMounted(async () => {
    promoCode.value = '';
    promoDiscount.value = 0;
    promoError.value = '';
    
    await loadCurrentUser();
    await loadCartData();
});
</script>

<style scoped>
.cart-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Arial', sans-serif;
    min-height: 100vh;
    position: relative;
    background-color: #f5f5f5;
}

.cart-title {
    font-size: 28px;
    color: #6b46c1;
    margin-bottom: 25px;
    text-align: center;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.cart-items {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.cart-item {
    background: #fff;
    border-radius: 16px;
    padding: 20px;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #ffffff, #f9f9f9);
}

.cart-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.item-checkbox {
    margin-right: 15px;
    width: 24px;
    height: 24px;
    accent-color: #6b46c1;
    cursor: pointer;
}

.cart-item-image-wrapper {
    position: relative;
    width: 120px;
    height: 120px;
    flex-shrink: 0;
    margin-right: 20px;
}

.cart-item-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    transition: transform 0.3s ease;
}

.cart-item:hover .cart-item-image {
    transform: scale(1.05);
}

.cart-item-details {
    flex-grow: 1;
    text-align: left;
    max-width: 60%;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.cart-item-details h3 {
    font-size: 20px;
    color: #2c3e50;
    margin: 0;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cart-item-sku {
    font-size: 14px;
    color: #7f8c8d;
    margin: 0;
}

.cart-item-category {
    font-size: 14px;
    color: #6b46c1;
    margin: 0;
    font-weight: 500;
}

.cart-item-specifications {
    background: #f8f9fa;
    padding: 8px 12px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 13px;
    color: #34495e;
}

.spec-item {
    display: flex;
    justify-content: space-between;
}

.spec-item strong {
    color: #2c3e50;
}

.quantity-control {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 10px 0;
}

.quantity-button {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    border: none;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    font-size: 18px;
    cursor: pointer;
    transition: background 0.3s ease, transform 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quantity-button:hover {
    background: linear-gradient(135deg, #2980b9, #1f6391);
    transform: scale(1.1);
}

.quantity-input {
    width: 70px;
    padding: 8px;
    text-align: center;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    background-color: #fff;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
    transition: border-color 0.3s ease;
}

.quantity-input:focus {
    border-color: #6b46c1;
    outline: none;
}

.price-container {
    display: flex;
    align-items: center;
    gap: 12px;
}

.original-price {
    font-size: 16px;
    color: #e74c3c;
    text-decoration: line-through;
    margin: 0;
}

.current-price {
    font-size: 22px;
    color: #27ae60;
    font-weight: 700;
    margin: 0;
}

.discount-badge {
    background-color: #e74c3c;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    margin-left: 5px;
}

.cart-item-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    margin-left: 20px;
}

.wishlist-button {
    background: #fff;
    color: #28a745;
    border: 2px solid #28a745;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.wishlist-button.active {
    background: #28a745;
    color: #fff;
    border-color: #28a745;
}

.wishlist-button:hover:not(.active) {
    background: #e6f4ea;
    color: #28a745;
}

.remove-button {
    background: #fff;
    color: #dc3545;
    border: 2px solid #dc3545;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.remove-button:hover {
    background: #dc3545;
    color: #fff;
    border-color: #dc3545;
}

.cart-total {
    margin-top: 25px;
    padding: 20px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 16px;
    text-align: right;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    position: sticky;
    bottom: 20px;
    z-index: 10;
    background: linear-gradient(to right, #fff, #f8f9fa);
}

.cart-total p {
    font-size: 26px;
    color: #2c3e50;
    font-weight: 700;
    margin: 0 0 10px 0;
}

.checkout-button {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    padding: 14px 35px;
    border: none;
    border-radius: 10px;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
    text-transform: uppercase;
    font-weight: 600;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.checkout-button:hover:not(:disabled) {
    background: linear-gradient(135deg, #0056b3, #003d82);
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.checkout-button:disabled {
    background: #cccccc;
    cursor: not-allowed;
    box-shadow: none;
}

.no-data {
    color: #7f8c8d;
    text-align: center;
    font-size: 18px;
    font-weight: 500;
    padding: 30px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
}

.cart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 10px 15px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.select-all-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.select-all-checkbox {
    width: 20px;
    height: 20px;
    accent-color: #6b46c1;
}

.select-all-container label {
    font-size: 16px;
    color: #333;
    font-weight: 500;
    cursor: pointer;
}

.clear-cart-btn {
    background: none;
    border: none;
    color: #dc3545;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 5px;
    transition: all 0.2s ease;
}

.clear-cart-btn:hover {
    background-color: rgba(220, 53, 69, 0.1);
}

.cart-summary {
    margin-bottom: 15px;
}

.summary-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.summary-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 16px;
    color: #555;
}

.summary-row.discount {
    color: #e74c3c;
}

.summary-row.total {
    font-size: 22px;
    font-weight: 600;
    color: #2c3e50;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #eee;
}

.promo-code-container {
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    border: 1px solid #eee;
}

.promo-input-group {
    display: flex;
    gap: 8px;
}

.promo-input {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
}

.promo-input:focus {
    outline: none;
    border-color: #6b46c1;
}

.apply-promo-btn {
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0 15px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.apply-promo-btn:hover:not(:disabled) {
    background-color: #553c9a;
}

.apply-promo-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.promo-error {
    color: #e74c3c;
    font-size: 13px;
    margin: 5px 0 0;
}

.promo-success {
    color: #27ae60;
    font-size: 13px;
    margin: 5px 0 0;
}

.promo-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* Адаптивность */
@media (max-width: 768px) {
    .cart-item {
        flex-direction: column;
        align-items: flex-start;
        padding: 15px;
    }
    
    .cart-item-image-wrapper {
        width: 100%;
        height: auto;
        margin-right: 0;
        margin-bottom: 15px;
    }
    
    .cart-item-details {
        max-width: 100%;
        width: 100%;
    }
    
    .cart-item-actions {
        flex-direction: row;
        margin-left: 0;
        margin-top: 15px;
        width: 100%;
        justify-content: flex-end;
    }
    
    .item-checkbox {
        position: absolute;
        top: 15px;
        right: 15px;
        margin-right: 0;
    }
    
    .cart-total {
        position: static;
        margin-top: 20px;
    }
}

@media (max-width: 480px) {
    .cart-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .select-all-container {
        width: 100%;
    }
    
    .clear-cart-btn {
        width: 100%;
    }
    
    .cart-item-details h3 {
        white-space: normal;
    }
    
    .price-container {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
    
    .cart-total p {
        font-size: 22px;
    }
    
    .checkout-button {
        padding: 12px;
        font-size: 16px;
    }
    
    .promo-input-group {
        flex-direction: column;
    }
    
    .apply-promo-btn {
        width: 100%;
        padding: 10px;
    }
}

.loading-spinner-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    text-align: center;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #6b46c1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.empty-cart {
    text-align: center;
    padding: 40px 20px;
    background-color: white;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
}

.empty-cart-icon {
    font-size: 60px;
    margin-bottom: 10px;
}

.empty-cart h3 {
    font-size: 24px;
    color: #2c3e50;
    margin: 0;
}

.empty-cart p {
    font-size: 16px;
    color: #7f8c8d;
    margin: 0;
}

.continue-shopping-btn {
    display: inline-block;
    background-color: #6b46c1;
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    text-align: center;
}

.continue-shopping-btn:hover {
    background-color: #553c9a;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.cart-buttons {
    display: flex;
    gap: 15px;
}

.cart-buttons .continue-shopping-btn {
    flex: 1;
}

.cart-buttons .checkout-button {
    flex: 2;
}

@media (max-width: 768px) {
    .cart-buttons {
        flex-direction: column;
    }
    
    .cart-buttons .continue-shopping-btn,
    .cart-buttons .checkout-button {
        width: 100%;
    }
}

@media (max-width: 480px) {
    .empty-cart-icon {
        font-size: 50px;
    }
    
    .empty-cart h3 {
        font-size: 20px;
    }
    
    .empty-cart p {
        font-size: 14px;
    }
}
</style>