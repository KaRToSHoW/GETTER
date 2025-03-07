<template>
    <div class="category-container">
        <h2 class="category-title">{{ categoryName }}</h2>
        <div class="products-grid">
            <div v-for="product in categoryProducts" :key="product.id" class="product-card">
                <router-link :to="`/product/${product.id}`" class="product-link">
                    <div class="image-wrapper">
                        <img :src="product.image || defaultImage" class="product-image" />
                        <div class="discount-tag">-4%</div>
                    </div>
                </router-link>
                <div class="product-content">
                    <h3>{{ product.name }}</h3>
                    <div class="price-container">
                        <p class="old-price"><s>{{ (product.price / 0.96).toFixed(2) }} ₽</s></p>
                        <p class="price">{{ product.price }} ₽</p>
                    </div>
                    <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                        <span>{{ product.is_available ? 'В наличии' : 'Нет в наличии' }}</span>
                        <span class="stock">Осталось: {{ product.stock }} шт.</span>
                    </div>
                    <div v-if="product.specifications" class="specifications">
                        <div v-for="(value, key) in product.specifications" :key="key" class="spec-item">
                            <span class="spec-key">{{ key }}:</span> {{ value }}
                        </div>
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
            <p v-if="categoryProducts.length === 0" class="no-data">В этой категории нет товаров.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import defaultImage from '@/assets/img/Default_product_foto.jpg';

const route = useRoute();
const API_BASE_URL = 'http://127.0.0.1:8000';

const categoryProducts = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const categoryName = ref('');

onMounted(async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const categoryId = route.params.id;
        console.log('Запрос товаров для категории ID:', categoryId); // Логируем ID категории
        const response = await axios.get(`${API_BASE_URL}/main/products/?category=${categoryId}`, { headers });
        console.log('Ответ API:', response.data); // Логируем ответ

        categoryProducts.value = response.data;
        wishlist.value = (await axios.get(`${API_BASE_URL}/main/wishlist/check/`, { headers })).data.wishlist || [];
        
        const cartResponse = await axios.get(`${API_BASE_URL}/main/cart/`, { headers });
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

        if (categoryProducts.value.length > 0) {
            const category = categoryProducts.value[0].category;
            categoryName.value = category ? category.name : 'Категория не найдена';
        }
    } catch (error) {
        console.error('Ошибка загрузки товаров категории:', error.response ? error.response.data : error.message);
        alert('Ошибка при загрузке товаров категории. Проверьте консоль.');
    }
});

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
        alert('Ошибка при управлении желаемым: ' + (error.response ? error.response.data.error : error.message));
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
        alert('Ошибка при добавлении в корзину.');
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
        alert('Ошибка при увеличении количества.');
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
        alert('Ошибка при уменьшении количества.');
    }
};
</script>

<style scoped>
.category-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Arial', sans-serif;
    background-color: #f5f5f5;
}

.category-title {
    font-size: 28px;
    color: #6b46c1;
    margin: 20px 0;
    text-align: center;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.product-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 0;
}

.product-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.image-wrapper {
    position: relative;
    width: 100%;
    height: 200px;
    overflow: hidden;
}

.product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.product-card:hover .product-image {
    transform: scale(1.05);
}

.discount-tag {
    position: absolute;
    top: 10px;
    left: 10px;
    background: linear-gradient(135deg, #ffd700, #ffcc00);
    color: #1a1a1a;
    padding: 5px 12px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.product-content {
    padding: 15px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.product-card h3 {
    font-size: 18px;
    color: #2c3e50;
    margin: 0;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.price-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.old-price {
    font-size: 14px;
    color: #e74c3c;
    text-decoration: line-through;
    margin: 0;
}

.price {
    font-size: 22px;
    color: #27ae60;
    font-weight: 700;
    margin: 0;
}

.availability {
    display: flex;
    flex-direction: column;
    align-items: center;
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

.specifications {
    font-size: 12px;
    color: #7f8c8d;
    background: #f8f9fa;
    padding: 8px;
    border-radius: 8px;
    margin-top: 10px;
}

.spec-item {
    display: flex;
    justify-content: space-between;
    margin: 4px 0;
}

.spec-key {
    font-weight: 600;
    color: #34495e;
}

.button-group {
    padding: 15px;
    display: flex;
    gap: 10px;
    border-top: 1px solid #eee;
    background: #fafafa;
    align-items: center;
}

.add-to-cart-button {
    flex: 1;
    background: #3498db;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
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
    gap: 5px;
    flex: 1;
}

.quantity-button {
    background: #3498db;
    color: white;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.quantity-button:hover {
    background: #2980b9;
}

.quantity {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    min-width: 30px;
    text-align: center;
}

.wishlist-button {
    background: #fff;
    border: 1px solid #27ae60;
    border-radius: 8px;
    padding: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #27ae60;
    cursor: pointer;
    transition: background 0.3s ease, color 0.3s ease;
}

.wishlist-button.active {
    background: #27ae60;
    color: #fff;
}

.wishlist-button:hover:not(.active) {
    background: #ecf0f1;
}

.heart-icon {
    font-size: 18px;
}

.no-data {
    color: #7f8c8d;
    text-align: center;
    font-size: 18px;
    font-weight: 500;
    padding: 20px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
</style>