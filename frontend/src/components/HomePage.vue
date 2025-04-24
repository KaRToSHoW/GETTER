<template>
    <div class="home-container">
        <ToastNotification ref="toast" />
        <!-- Административная панель -->
        <div v-if="currentUser && currentUser.is_superuser" class="admin-dashboard">
            <h2 class="admin-title">Панель администратора</h2>
            <div class="admin-actions">
                <button @click="createNewProduct" class="admin-button create">Добавить новый товар</button>
                <button @click="createNewCategory" class="admin-button create">Добавить новую категорию</button>
                <button @click="manageUsers" class="admin-button manage">Управление пользователями</button>
            </div>
        </div>
        <!-- Карусель с акцией -->
        <swiper :modules="modules" :pagination="{ clickable: true }" class="swiper-container" @swiper="onSwiper"
            @slideChange="onSlideChange">
            <swiper-slide>
                <div class="promo-banner">
                    <button class="nav-arrow left-arrow"></button>
                    <div class="promo-text">
                        <h2>Умная колонка</h2>
                        <p class="discount">СКИДКА 30% ПРИ ПОКУПКЕ ВТОРОГО ТОВАРА</p>
                    </div>
                    <img src="https://via.placeholder.com/150" alt="Promo Image" class="promo-image" />
                    <button class="nav-arrow right-arrow">></button>
                </div>
            </swiper-slide>
            <swiper-slide>
                <div class="promo-banner">
                    <button class="nav-arrow left-arrow"></button>
                    <div class="promo-text">
                        <h2>Наушники</h2>
                        <p class="discount">СКИДКА 20% НА ВСЕ АУДИО</p>
                    </div>
                    <img src="https://via.placeholder.com/150?text=Headphones" alt="Promo Image" class="promo-image" />
                    <button class="nav-arrow right-arrow">></button>
                </div>
            </swiper-slide>
            <swiper-slide>
                <div class="promo-banner">
                    <button class="nav-arrow left-arrow"></button>
                    <div class="promo-text">
                        <h2>Ноутбук</h2>
                        <p class="discount">СКИДКА 15% НА ТЕХНИКУ</p>
                    </div>
                    <img src="https://via.placeholder.com/150?text=Laptop" alt="Promo Image" class="promo-image" />
                    <button class="nav-arrow right-arrow">></button>
                </div>
            </swiper-slide>
            <div class="swiper-pagination"></div>
        </swiper>

        <h2 class="home-title">Каталог</h2>
        <div class="categories-grid">
            <div v-for="category in categories" :key="category.id" class="category-card">
                <router-link :to="`/category/${category.id}`" class="category-link">
                    <div class="category-image-wrapper">
                        <img :src="category.image || defaultCategoryImage" :alt="`Category ${category.name}`"
                            class="category-image" />
                    </div>
                    <h3 class="category-name">{{ category.name }}</h3>
                </router-link>
            </div>
            <p v-if="categories.length === 0" class="no-data">Нет доступных категорий.</p>
        </div>

        <h2 class="home-title">Различные товары</h2>
        <div class="products-grid">
            <div v-for="product in products" :key="product.id" class="product-card">
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
                        <ul class="specifications-list">
                            <li v-for="(value, key) in product.specifications.specifications" :key="key" class="spec-item">
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
            <p v-if="products.length === 0" class="no-data">Нет доступных товаров.</p>
        </div>

        <!-- Модальное окно для создания категории -->
        <div v-if="showCategoryForm" class="modal-overlay" @click.self="cancelCategoryCreate">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Создание новой категории</h3>
                    <button class="close-button" @click="cancelCategoryCreate">&times;</button>
                </div>
                <form @submit.prevent="submitNewCategory" class="create-form">
                    <div class="form-group">
                        <label>Название категории:</label>
                        <input 
                            v-model="newCategory.name" 
                            required 
                            class="form-input"
                            placeholder="Введите название категории"
                        />
                    </div>
                    <div class="form-group">
                        <label>Изображение категории:</label>
                        <div class="file-input-wrapper">
                            <input 
                                type="file" 
                                @change="handleCategoryImageUpload" 
                                accept="image/*"
                                class="file-input"
                                id="categoryImage"
                            />
                            <label for="categoryImage" class="file-input-label">
                                Выберите изображение
                            </label>
                        </div>
                        <div v-if="categoryImagePreview" class="image-preview">
                            <img :src="categoryImagePreview" alt="Preview" />
                        </div>
                    </div>
                    <div class="form-buttons">
                        <button type="button" @click="cancelCategoryCreate" class="cancel-button">Отмена</button>
                        <button type="submit" class="save-button">Создать</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Модальное окно для создания товара -->
        <div v-if="showCreateProductForm" class="modal-overlay" @click.self="cancelCreateProduct">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Создание нового товара</h3>
                    <button class="close-button" @click="cancelCreateProduct">&times;</button>
                </div>
                <form @submit.prevent="submitNewProduct" class="create-form">
                    <div class="form-group">
                        <label>Название товара:</label>
                        <input 
                            v-model="newProduct.name" 
                            required 
                            class="form-input"
                            placeholder="Введите название товара"
                        />
                    </div>
                    <div class="form-group">
                        <label>Артикул:</label>
                        <input 
                            v-model="newProduct.sku" 
                            required 
                            class="form-input"
                            placeholder="Введите артикул товара"
                        />
                    </div>
                    <div class="form-group">
                        <label>Описание:</label>
                        <textarea 
                            v-model="newProduct.description" 
                            class="form-input"
                            placeholder="Введите описание товара"
                            rows="3"
                        ></textarea>
                    </div>
                    <div class="form-group">
                        <label>Категория:</label>
                        <select v-model="newProduct.category" required class="form-input">
                            <option value="">Выберите категорию</option>
                            <option v-for="category in categories" :key="category.id" :value="category.id">
                                {{ category.name }}
                            </option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Цена:</label>
                        <input 
                            v-model.number="newProduct.price" 
                            type="number" 
                            min="0" 
                            step="0.01" 
                            required 
                            class="form-input"
                            placeholder="0.00"
                        />
                    </div>
                    <div class="form-group">
                        <label>Количество на складе:</label>
                        <input 
                            v-model.number="newProduct.stock" 
                            type="number" 
                            min="0" 
                            required 
                            class="form-input"
                            placeholder="0"
                        />
                    </div>
                    <div class="form-group">
                        <label>Изображение товара:</label>
                        <div class="file-input-wrapper">
                            <input 
                                type="file" 
                                @change="handleProductImageUpload" 
                                accept="image/*"
                                class="file-input"
                                id="productImage"
                            />
                            <label for="productImage" class="file-input-label">
                                Выберите изображение
                            </label>
                        </div>
                        <div v-if="productImagePreview" class="image-preview">
                            <img :src="productImagePreview" alt="Preview" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Характеристики:</label>
                        <button type="button" @click="addSpecification" class="add-spec-button">
                            Добавить характеристику
                        </button>
                        <div v-for="(spec, index) in specifications" :key="index" class="specification-item">
                            <input 
                                v-model="spec.key" 
                                placeholder="Название" 
                                class="form-input spec-input"
                            />
                            <input 
                                v-model="spec.value" 
                                placeholder="Значение" 
                                class="form-input spec-input"
                            />
                            <button type="button" @click="removeSpecification(index)" class="remove-spec-button">
                                &#10005;
                            </button>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Статус доступности:</label>
                        <select v-model="newProduct.is_available" class="form-input">
                            <option :value="true">Доступен</option>
                            <option :value="false">Недоступен</option>
                        </select>
                    </div>
                    <div class="form-buttons">
                        <button type="button" @click="cancelCreateProduct" class="cancel-button">Отмена</button>
                        <button type="submit" class="save-button">Создать</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Pagination } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/pagination';
import defaultImage from '@/assets/img/Default_product_foto.jpg';
import defaultCategoryImage from '@/assets/img/Default_product_foto.jpg'; // Добавляем дефолтное изображение для категорий
import ToastNotification from './ToastNotification.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

const categories = ref([]);
const products = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const modules = ref([Pagination]);
const swiperInstance = ref(null);
const toast = ref(null);
const currentUser = ref(null);
const showCategoryForm = ref(false);
const showCreateProductForm = ref(false);
const productImagePreview = ref(null);
const specifications = ref([]);
const newProduct = ref({
    name: '',
    sku: '',
    description: '',
    price: 0,
    stock: 0,
    category: '',
    image: null,
    is_available: true,
    specifications: {}
});

const newCategory = ref({
    name: '',
    image: null
});

const categoryImagePreview = ref(null);

onMounted(async () => {
    await loadCurrentUser();
    await loadData();
    await loadCategories();
});

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
        console.error('Ошибка загрузки профиля пользователя:', error);
    }
};

const loadData = async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const [categoriesResponse, productsResponse, wishlistResponse, cartResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/main/categories/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/`, { headers }),
            token ? axios.get(`${API_BASE_URL}/main/wishlist/check/`, { headers }) : Promise.resolve({ data: [] }),
            token ? axios.get(`${API_BASE_URL}/main/cart/`, { headers }) : Promise.resolve({ data: [] })
        ]);

        categories.value = categoriesResponse.data;
        products.value = productsResponse.data;
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
    } catch (error) {
        console.error('Ошибка загрузки данных:', error.response ? error.response.data : error.message);
        toast.value.showToast('Ошибка при загрузке данных. Проверьте консоль.', 'error');
    }
};

const loadCategories = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/main/categories/`);
        categories.value = response.data;
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
        toast.value.showToast('Ошибка при загрузке категорий', 'error');
    }
};

// Функции администратора
const createNewProduct = () => {
    if (!currentUser.value || !currentUser.value.is_superuser) {
        toast.value.showToast('У вас нет прав для создания товаров', 'error');
        return;
    }
    showCreateProductForm.value = true;
};

const createNewCategory = () => {
    if (!currentUser.value || !currentUser.value.is_superuser) {
        toast.value.showToast('У вас нет прав для создания категорий', 'error');
        return;
    }
    
    showCategoryForm.value = true;
};

const manageUsers = () => {
    if (!currentUser.value || !currentUser.value.is_superuser) {
        toast.value.showToast('У вас нет прав для управления пользователями', 'error');
        return;
    }
    
    // Здесь должен быть переход на страницу управления пользователями
    toast.value.showToast('Функция управления пользователями находится в разработке', 'info');
};

const onSwiper = (swiper) => {
    swiperInstance.value = swiper;
};

const onSlideChange = () => {
    console.log('Слайд изменен', swiperInstance.value.activeIndex);
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
        toast.value.showToast('Ошибка при управлении желаемым: ' + (error.response ? error.response.data.error : error.message), 'error');
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
        toast.value.showToast('Ошибка при добавлении в корзину.', 'error');
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
        toast.value.showToast('Ошибка при увеличении количества.', 'error');
    }
};

const decreaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    try {
        const newQuantity = (cartItems.value[product.id] || 0) - 1;
        if (newQuantity <= 0) {
            // Получаем ID элемента корзины из текущего заказа
            const cartResponse = await axios.get(`${API_BASE_URL}/main/cart/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const cartItem = cartResponse.data.items.find(item => item.product.id === product.id);
            if (!cartItem) {
                throw new Error('Товар не найден в корзине');
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
        toast.value.showToast('Ошибка при уменьшении количества.', 'error');
    }
};

const handleCategoryImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        newCategory.value.image = file;
        const reader = new FileReader();
        reader.onload = e => categoryImagePreview.value = e.target.result;
        reader.readAsDataURL(file);
    }
};

const cancelCategoryCreate = () => {
    newCategory.value = {
        name: '',
        image: null
    };
    categoryImagePreview.value = null;
    showCategoryForm.value = false;
};

const submitNewCategory = async () => {
    try {
        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('name', newCategory.value.name);
        if (newCategory.value.image) {
            formData.append('image', newCategory.value.image);
        }
        
        await axios.post(`${API_BASE_URL}/main/categories/`, formData, {
            headers: { 
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            }
        });
        
        await loadData();
        
        cancelCategoryCreate();
        toast.value.showToast('Категория успешно создана!', 'success');
    } catch (error) {
        console.error('Ошибка создания категории:', error);
        toast.value.showToast('Ошибка при создании категории: ' + (error.response?.data?.detail || error.message), 'error');
    }
};

const handleProductImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        newProduct.value.image = file;
        const reader = new FileReader();
        reader.onload = e => productImagePreview.value = e.target.result;
        reader.readAsDataURL(file);
    }
};

const addSpecification = () => {
    specifications.value.push({ key: '', value: '' });
};

const removeSpecification = (index) => {
    specifications.value.splice(index, 1);
};

const cancelCreateProduct = () => {
    newProduct.value = {
        name: '',
        sku: '',
        description: '',
        price: 0,
        stock: 0,
        category: '',
        image: null,
        is_available: true,
        specifications: {}
    };
    specifications.value = [];
    productImagePreview.value = null;
    showCreateProductForm.value = false;
};

const submitNewProduct = async () => {
    try {
        const token = localStorage.getItem('token');
        const formData = new FormData();

        // Add category_id instead of category
        formData.append('category_id', newProduct.value.category);

        // Add other fields
        formData.append('name', newProduct.value.name);
        formData.append('sku', newProduct.value.sku);
        formData.append('description', newProduct.value.description);
        formData.append('price', newProduct.value.price);
        formData.append('stock', newProduct.value.stock);
        formData.append('is_available', newProduct.value.is_available);

        if (newProduct.value.image) {
            formData.append('image', newProduct.value.image);
        }

        // Convert specifications to JSON and append
        const specs = {};
        specifications.value.forEach(spec => {
            if (spec.key && spec.value) {
                specs[spec.key] = spec.value;
            }
        });
        formData.append('specifications', JSON.stringify(specs));

        await axios.post(`${API_BASE_URL}/main/products/`, formData, {
            headers: { 
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            }
        });

        toast.value.showToast('Товар успешно создан!', 'success');
        cancelCreateProduct();
        await loadData(); // Перезагружаем список товаров
    } catch (error) {
        console.error('Ошибка создания товара:', error);
        toast.value.showToast('Ошибка при создании товара: ' + (error.response?.data?.detail || error.message), 'error');
    }
};
</script>

<style scoped>
.home-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Arial', sans-serif;
    background-color: #f5f5f5;
}

.swiper-container {
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
}

.promo-banner {
    background-color: #1a1a1a;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    min-height: 120px;
    position: relative;
}

.promo-text h2 {
    font-size: 20px;
    margin: 0;
    font-weight: 600;
}

.discount {
    font-size: 24px;
    color: #ffd700;
    font-weight: bold;
    margin: 5px 0;
}

.promo-image {
    width: 150px;
    height: auto;
    margin: 0 20px;
    border-radius: 8px;
}

.nav-arrow {
    background: none;
    border: none;
    color: #ccc;
    font-size: 24px;
    cursor: pointer;
    padding: 10px;
    transition: color 0.3s;
}

.nav-arrow:hover {
    color: white;
}

.swiper-pagination {
    bottom: 10px;
}

.swiper-pagination-bullet {
    background-color: #ccc;
    opacity: 0.7;
}

.swiper-pagination-bullet-active {
    background-color: #6b46c1;
    opacity: 1;
}

.home-title {
    font-size: 28px;
    color: #6b46c1;
    margin: 20px 0;
    text-align: center;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.categories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.category-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.category-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.category-link {
    text-decoration: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 15px;
}

.category-image-wrapper {
    width: 100%;
    height: 150px;
    overflow: hidden;
    position: relative;
}

.category-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.category-card:hover .category-image {
    transform: scale(1.05);
}

.category-name {
    font-size: 18px;
    color: #2c3e50;
    margin: 10px 0 0;
    font-weight: 600;
    text-align: center;
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

/* Стили для админ-панели */
.admin-dashboard {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    border-left: 4px solid #6b46c1;
}

.admin-title {
    color: #6b46c1;
    font-size: 20px;
    margin-bottom: 15px;
}

.admin-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.admin-button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.admin-button.create {
    background-color: #4caf50;
    color: white;
}

.admin-button.manage {
    background-color: #2196f3;
    color: white;
}

.admin-button:hover {
    opacity: 0.9;
}

.file-input {
    margin-top: 8px;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 100%;
}

.image-preview {
    margin-top: 12px;
    max-width: 200px;
    max-height: 200px;
    overflow: hidden;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.image-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* Стили для модального окна */
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
    max-width: 600px;
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

.create-form {
    padding: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #2c3e50;
    font-weight: 500;
}

.form-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.3s;
}

.form-input:focus {
    border-color: #6b46c1;
    outline: none;
}

textarea.form-input {
    resize: vertical;
    min-height: 100px;
}

.specification-item {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 10px;
    margin-bottom: 10px;
}

.spec-input {
    width: 100%;
}

.add-spec-button {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 10px;
}

.remove-spec-button {
    background-color: #ff4444;
    color: white;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.file-input-wrapper {
    position: relative;
}

.file-input {
    position: absolute;
    width: 0.1px;
    height: 0.1px;
    opacity: 0;
    overflow: hidden;
    z-index: -1;
}

.file-input-label {
    display: inline-block;
    padding: 10px 20px;
    background-color: #6b46c1;
    color: white;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.file-input-label:hover {
    background-color: #553c9a;
}

.image-preview {
    margin-top: 12px;
    max-width: 200px;
    max-height: 200px;
    overflow: hidden;
    border-radius: 8px;
    border: 2px solid #eee;
}

.image-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.form-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
    position: sticky;
    bottom: 0;
    background: white;
    padding-top: 12px;
    border-top: 1px solid #eee;
}

.cancel-button, .save-button {
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.cancel-button {
    background-color: #fff;
    border: 1px solid #ddd;
    color: #666;
}

.cancel-button:hover {
    background-color: #f8f9fa;
    border-color: #666;
}

.save-button {
    background-color: #6b46c1;
    border: none;
    color: white;
}

.save-button:hover {
    background-color: #553c9a;
}

.admin-button.create {
    background: linear-gradient(135deg, #6b46c1, #553c9a);
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.admin-button.create:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    background: linear-gradient(135deg, #553c9a, #4c3282);
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