<template>
    <div class="cart-container">
        <ToastNotification ref="toast" />
        <h2 class="cart-title">Корзина</h2>
        <div v-if="cart.items && cart.items.length > 0" class="cart-items">
            <div v-for="item in cart.items" :key="item.id" class="cart-item">
                <input type="checkbox" v-model="selectedItems" :value="item.id" class="item-checkbox" />
                <div class="cart-item-image-wrapper">
                    <img v-if="item.product.image" :src="`${$apiBaseUrl}${item.product.image}`" alt="Product Image"
                        class="cart-item-image" />
                </div>
                <div class="cart-item-details">
                    <h3>{{ item.product.name }}</h3>
                    <p class="cart-item-sku">Артикул: {{ item.product.sku }}</p>
                    <p class="cart-item-category">Категория: {{ item.product.category.name }}</p>
                    <div v-if="item.product.specifications.specifications" class="cart-item-specifications">
                        <span v-for="(value, key) in item.product.specifications.specifications" :key="key" class="spec-item">
                            <strong>{{ key.replace(/_/g, ' ') }}:</strong> {{ value }}
                        </span>
                    </div>

                    <div class="quantity-control">
                        <button @click="decreaseQuantity(item)" class="quantity-button">-</button>
                        <input type="number" v-model.number="item.quantity" @change="updateQuantity(item)" min="1"
                            class="quantity-input" />
                        <button @click="increaseQuantity(item)" class="quantity-button">+</button>
                    </div>
                    <div class="price-container">
                        <p class="old-price"><s>{{ (item.product.price / 0.96 * item.quantity).toFixed(2) }} ₽</s></p>
                        <p class="cart-item-price">{{ (item.product.price * item.quantity).toFixed(2) }} ₽</p>
                    </div>
                </div>
                <div class="cart-item-actions">
                    <button @click="toggleWishlist(item.product)"
                        :class="['wishlist-button', { 'active': isInWishlist(item.product.id) }]">
                        <span class="heart-icon">❤️</span>
                    </button>
                    <button @click="removeFromCart(item.id)" class="remove-button">
                        <span class="trash-icon">🗑️</span>
                    </button>
                </div>
            </div>
            <div class="cart-total">
                <p>Итого: {{ calculateTotal }} ₽</p>
                <button class="checkout-button" @click="checkout" :disabled="selectedItems.length === 0">Оформить
                    заказ</button>
            </div>
        </div>
        <p v-else class="no-data">Корзина пуста.</p>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { inject } from 'vue';
import ToastNotification from './ToastNotification.vue';

const $apiBaseUrl = inject('$apiBaseUrl', 'http://127.0.0.1:8000');

const cart = ref({ items: [], total_price: 0 });
const selectedItems = ref([]);
const wishlist = ref([]);
const toast = ref(null);

const loadCartData = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const [cartResponse, wishlistResponse] = await Promise.all([
                axios.get(`${$apiBaseUrl}/main/cart/`, {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                axios.get(`${$apiBaseUrl}/main/wishlist/check/`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);

            cart.value = {
                ...cartResponse.data,
                total_price: typeof cartResponse.data.total_price === 'number' ? cartResponse.data.total_price : parseFloat(cartResponse.data.total_price) || 0,
                items: cartResponse.data.items || []
            };
            wishlist.value = wishlistResponse.data.wishlist || [];
        }
    } catch (error) {
        console.error('Ошибка загрузки данных:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при загрузке данных. Проверьте консоль.', 'error');
    }
};

onMounted(async () => {
    await loadCartData();
});

const increaseQuantity = (item) => {
    updateQuantity(item, 1);
};

const decreaseQuantity = (item) => {
    if (item.quantity > 1) {
        updateQuantity(item, -1);
    }
};

const updateQuantity = async (item, change) => {
    try {
        const token = localStorage.getItem('token');
        const newQuantity = item.quantity + change;

        if (newQuantity <= 0) {
            await removeFromCart(item.id);
            return;
        }

        if (newQuantity > item.product.stock) {
            toast.value.showToast('Нельзя добавить больше, чем есть в наличии!', 'warning');
            return;
        }

        await axios.post(`${$apiBaseUrl}/main/cart/add/`, {
            product_id: item.product.id,
            quantity: change
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });

        await loadCartData();
    } catch (error) {
        console.error('Ошибка обновления количества:', error);
        toast.value.showToast('Ошибка при обновлении количества', 'error');
    }
};

const removeFromCart = async (itemId) => {
    try {
        const token = localStorage.getItem('token');
        await axios.delete(`${$apiBaseUrl}/main/cart/remove/${itemId}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        await loadCartData();
        toast.value.showToast('Товар удален из корзины', 'success');
    } catch (error) {
        console.error('Ошибка удаления из корзины:', error);
        toast.value.showToast('Ошибка при удалении товара из корзины', 'error');
    }
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

const calculateTotal = computed(() => {
    const total = cart.value.items.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
    return typeof total === 'number' ? total.toFixed(2) : '0.00';
});

const checkout = async () => {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            toast.value.showToast('Пожалуйста, войдите в систему для оформления заказа', 'warning');
            return;
        }

        // Здесь будет логика оформления заказа
        toast.value.showToast('Заказ успешно оформлен!', 'success');
    } catch (error) {
        console.error('Ошибка оформления заказа:', error);
        toast.value.showToast('Ошибка при оформлении заказа', 'error');
    }
};
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

.old-price {
    font-size: 16px;
    color: #e74c3c;
    text-decoration: line-through;
    margin: 0;
}

.cart-item-price {
    font-size: 22px;
    color: #27ae60;
    font-weight: 700;
    margin: 0;
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
</style>