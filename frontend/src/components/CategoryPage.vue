<template>
    <div class="page-layout">
        <!-- Сайдбар с фильтрами -->
        <aside class="filters-sidebar">
            <h3 class="filters-title">Фильтры</h3>
            
            <!-- Фильтр по цене -->
            <div class="filter-section">
                <h4>Цена</h4>
                <div class="price-range">
                    <div class="price-inputs">
                        <input 
                            type="number" 
                            v-model="filters.minPrice" 
                            placeholder="От" 
                            @input="debouncedApplyFilters"
                            class="price-input"
                        >
                        <span class="price-separator">—</span>
                        <input 
                            type="number" 
                            v-model="filters.maxPrice" 
                            placeholder="До" 
                            @input="debouncedApplyFilters"
                            class="price-input"
                        >
                    </div>
                    <div class="price-slider">
                        <div class="slider-track"></div>
                        <input 
                            type="range" 
                            v-model="filters.minPrice" 
                            :min="minAvailablePrice" 
                            :max="maxAvailablePrice"
                            @input="debouncedApplyFilters"
                            class="range-input"
                        >
                        <input 
                            type="range" 
                            v-model="filters.maxPrice" 
                            :min="minAvailablePrice" 
                            :max="maxAvailablePrice"
                            @input="debouncedApplyFilters"
                            class="range-input"
                        >
                    </div>
                </div>
            </div>

            <!-- Фильтр по наличию -->
            <div class="filter-section">
                <h4>Наличие</h4>
                <label class="checkbox-label">
                    <input 
                        type="checkbox" 
                        v-model="filters.inStock"
                        @change="debouncedApplyFilters"
                    >
                    <span class="checkbox-text">В наличии</span>
                </label>
                <label class="checkbox-label">
                    <input 
                        type="checkbox" 
                        v-model="filters.hasDiscount"
                        @change="debouncedApplyFilters"
                    >
                    <span class="checkbox-text">Со скидкой</span>
                </label>
            </div>

            <!-- Фильтры по характеристикам -->
            <div v-for="(values, key) in availableSpecifications" 
                 :key="key" 
                 class="filter-section"
            >
                <h4>{{ key }}</h4>
                <div class="spec-values">
                    <label 
                        v-for="value in values" 
                        :key="value" 
                        class="checkbox-label"
                        :style="{ borderColor: getSpecificationColor(key) }"
                    >
                        <input 
                            type="checkbox" 
                            v-model="filters.specifications[key]" 
                            :value="value"
                            @change="debouncedApplyFilters"
                        >
                        <span class="checkbox-text">{{ value }} ({{ getFilterValueCount(key, value) }})</span>
                    </label>
                </div>
            </div>

            <!-- Сортировка -->
            <div class="filter-section">
                <h4>Сортировка</h4>
                <select v-model="filters.sortBy" @change="debouncedApplyFilters" class="sort-select">
                    <option value="popular">По популярности</option>
                    <option value="price-asc">Сначала дешевле</option>
                    <option value="price-desc">Сначала дороже</option>
                    <option value="new">Сначала новые</option>
                    <option value="rating">По рейтингу</option>
                    <option value="discount">По размеру скидки</option>
                    <option value="name-asc">По названию А-Я</option>
                    <option value="name-desc">По названию Я-А</option>
                </select>
            </div>

            <button @click="resetFilters" class="reset-filters-btn">
                Сбросить все фильтры
            </button>
        </aside>

        <!-- Основной контент -->
        <main class="main-content">
            <div class="category-header">
                <h2 class="category-title">{{ categoryName }}</h2>
                
                <!-- Административная панель -->
                <div v-if="currentUser && currentUser.is_superuser" class="admin-actions">
                    <button @click="createNewProduct" class="admin-button">
                        <span class="plus-icon">+</span> Добавить товар
                    </button>
                </div>

                <!-- Активные фильтры -->
                <div v-if="activeFilters.length > 0" class="active-filters">
                    <div v-for="filter in activeFilters" 
                         :key="filter.type + (filter.key || '') + (filter.value || '')"
                         class="filter-tag"
                         :style="filter.type === 'spec' ? { borderColor: getSpecificationColor(filter.key) } : {}"
                    >
                        <span class="filter-tag-text">
                            <template v-if="filter.type === 'spec'">
                                {{ filter.key }}: {{ filter.values.join(', ') }}
                            </template>
                            <template v-else>
                                {{ filter.value }}
                            </template>
                        </span>
                        <button class="remove-filter" @click="removeFilter(filter)">×</button>
                    </div>
                </div>
            </div>

            <!-- Сетка товаров -->
            <div class="products-grid">
                <div v-for="product in categoryProducts" :key="product.id" class="product-card">
                    <!-- Кнопка удаления для администратора -->
                    <button v-if="currentUser && currentUser.is_superuser" 
                           @click="deleteProduct(product.id)" 
                           class="admin-delete-btn">✖</button>
                    <!-- Кнопка редактирования для администратора -->
                    <button v-if="currentUser && currentUser.is_superuser" 
                           @click="editProduct(product)" 
                           class="admin-edit-btn">✎</button>
                    <router-link :to="`/product/${product.id}`" class="product-link">
                        <div class="image-wrapper">
                            <img :src="product.image || defaultImage" class="product-image" />
                            <div v-if="product.discount > 0" class="discount-tag">-{{ product.discount }}%</div>
                        </div>
                    </router-link>
                    <div class="product-content">
                        <h3>{{ product.name }}</h3>
                        <div class="rating" v-if="product.average_rating">
                            <span class="stars">
                                <span v-for="i in 5" :key="i" :class="['star', i <= Math.round(product.average_rating) ? 'filled' : '']">★</span>
                            </span>
                            <span class="rating-value">{{ product.average_rating ? product.average_rating.toFixed(1) : '0.0' }}</span>
                        </div>
                        <div class="price-container">
                            <p v-if="product.discount > 0" class="old-price"><s>{{ product.price }} ₽</s></p>
                            <p class="price">{{ product.discounted_price }} ₽</p>
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
        </main>

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

        <!-- Модальное окно для добавления товаров -->
        <div v-if="isAddingProducts" class="edit-product-modal">
            <div class="edit-product-content">
                <h3>Добавление товаров в категорию</h3>
                <form @submit.prevent="addSelectedProducts" class="edit-product-form">
                    <div class="form-group">
                        <label>Выберите товары:</label>
                        <select v-model="selectedProducts" multiple>
                            <option v-for="product in availableProducts" :key="product.id" :value="product.id">
                                {{ product.name }}
                            </option>
                        </select>
                    </div>
                    <div class="form-buttons">
                        <button type="button" @click="cancelAddingProducts" class="cancel-button">Отмена</button>
                        <button type="submit" class="save-button">Добавить</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { debounce } from 'lodash';
import defaultImage from '@/assets/img/Default_product_foto.jpg';

const route = useRoute();
const router = useRouter();
const API_BASE_URL = 'http://127.0.0.1:8000';

const originalProducts = ref([]); // Добавляем хранение оригинального списка
const categoryProducts = ref([]);
const wishlist = ref([]);
const cartItems = ref({});
const categoryName = ref('');
const currentUser = ref(null);
const editingProduct = ref(null);
const categories = ref([]);
const isLoading = ref(false);
const isFiltering = ref(false);

const isAddingProducts = ref(false);
const availableProducts = ref([]);
const selectedProducts = ref([]);

const filters = ref({
    minPrice: '',
    maxPrice: '',
    inStock: false,
    hasDiscount: false,
    sortBy: 'popular',
    specifications: {}
});

const availableSpecifications = ref({});
const minAvailablePrice = ref(0);
const maxAvailablePrice = ref(10000);

const resetFilters = () => {
    filters.value = {
        minPrice: '',
        maxPrice: '',
        inStock: false,
        hasDiscount: false,
        sortBy: 'popular',
        specifications: {}
    };
    applyFilters();
};

// Создаем debounced версию функции применения фильтров
const debouncedApplyFilters = debounce(() => {
    applyFilters();
    updateUrlWithFilters();
}, 300);

const applyFilters = () => {
    let filtered = [...originalProducts.value]; // Используем оригинальный список

    // Фильтр по цене
    if (filters.value.minPrice) {
        filtered = filtered.filter(product => product.price >= filters.value.minPrice);
    }
    if (filters.value.maxPrice) {
        filtered = filtered.filter(product => product.price <= filters.value.maxPrice);
    }

    // Фильтр по наличию
    if (filters.value.inStock) {
        filtered = filtered.filter(product => product.is_available && product.stock > 0);
    }

    // Фильтр по скидке
    if (filters.value.hasDiscount) {
        filtered = filtered.filter(product => product.discount > 0);
    }

    // Фильтр по характеристикам
    Object.entries(filters.value.specifications).forEach(([key, values]) => {
        if (values && values.length > 0) {
            filtered = filtered.filter(product => {
                return product.specifications && 
                       values.includes(product.specifications[key]);
            });
        }
    });

    // Сортировка
    switch (filters.value.sortBy) {
        case 'price-asc':
            filtered.sort((a, b) => a.price - b.price);
            break;
        case 'price-desc':
            filtered.sort((a, b) => b.price - a.price);
            break;
        case 'new':
            filtered.sort((a, b) => new Date(b.creation_date) - new Date(a.creation_date));
            break;
        case 'rating':
            filtered.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0));
            break;
        case 'discount':
            filtered.sort((a, b) => {
                return (b.discount || 0) - (a.discount || 0);
            });
            break;
        case 'name-asc':
            filtered.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'name-desc':
            filtered.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case 'popular':
        default:
            // По умолчанию оставляем текущую сортировку
            break;
    }

    categoryProducts.value = filtered;
    isFiltering.value = false;
};

// Функция обновления URL с текущими фильтрами
const updateUrlWithFilters = () => {
    const query = {};
    if (filters.value.minPrice) query.minPrice = filters.value.minPrice;
    if (filters.value.maxPrice) query.maxPrice = filters.value.maxPrice;
    if (filters.value.inStock) query.inStock = 'true';
    if (filters.value.hasDiscount) query.hasDiscount = 'true';
    if (filters.value.sortBy !== 'popular') query.sort = filters.value.sortBy;

    Object.entries(filters.value.specifications).forEach(([key, values]) => {
        if (values && values.length > 0) {
            query[`spec_${key}`] = values.join(',');
        }
    });

    router.replace({ query });
};

// Функция загрузки фильтров из URL
const loadFiltersFromUrl = () => {
    const query = route.query;
    
    filters.value = {
        minPrice: query.minPrice || '',
        maxPrice: query.maxPrice || '',
        inStock: query.inStock === 'true',
        hasDiscount: query.hasDiscount === 'true',
        sortBy: query.sort || 'popular',
        specifications: {}
    };

    // Загружаем спецификации из URL
    Object.entries(query).forEach(([key, value]) => {
        if (key.startsWith('spec_')) {
            const specKey = key.replace('spec_', '');
            filters.value.specifications[specKey] = value.split(',');
        }
    });
};

const updateAvailableSpecifications = () => {
    const specs = {};
    const prices = [];

    categoryProducts.value.forEach(product => {
        // Собираем все возможные характеристики
        if (product.specifications) {
            Object.entries(product.specifications).forEach(([key, value]) => {
                if (!specs[key]) {
                    specs[key] = new Set();
                }
                specs[key].add(value);
            });
        }
        // Собираем все цены
        prices.push(product.price);
    });

    // Преобразуем множества в массивы
    Object.keys(specs).forEach(key => {
        specs[key] = Array.from(specs[key]).sort();
    });

    availableSpecifications.value = specs;
    if (prices.length > 0) {
        minAvailablePrice.value = Math.floor(Math.min(...prices));
        maxAvailablePrice.value = Math.ceil(Math.max(...prices));
    }
};

const activeFilters = computed(() => {
    const active = [];
    if (filters.value.minPrice) active.push({ type: 'minPrice', value: `От ${filters.value.minPrice} ₽` });
    if (filters.value.maxPrice) active.push({ type: 'maxPrice', value: `До ${filters.value.maxPrice} ₽` });
    if (filters.value.inStock) active.push({ type: 'inStock', value: 'В наличии' });
    if (filters.value.hasDiscount) active.push({ type: 'hasDiscount', value: 'Со скидкой' });
    
    Object.entries(filters.value.specifications).forEach(([key, values]) => {
        if (values && values.length > 0) {
            active.push({ type: 'spec', key, values });
        }
    });
    return active;
});

const removeFilter = (filter) => {
    switch (filter.type) {
        case 'minPrice':
            filters.value.minPrice = '';
            break;
        case 'maxPrice':
            filters.value.maxPrice = '';
            break;
        case 'inStock':
            filters.value.inStock = false;
            break;
        case 'hasDiscount':
            filters.value.hasDiscount = false;
            break;
        case 'spec':
            filters.value.specifications[filter.key] = [];
            break;
    }
    applyFilters();
};

// Функция для определения цветовой категории для спецификации
const getSpecificationColor = (key) => {
    const colors = {
        'brand': '#4299e1',
        'color': '#48bb78',
        'size': '#ed8936',
        'material': '#9f7aea',
        'default': '#718096'
    };
    return colors[key.toLowerCase()] || colors.default;
};

// Получение количества товаров для каждого значения фильтра
const getFilterValueCount = (filterKey, filterValue) => {
    return originalProducts.value.filter(product => {
        if (filterKey === 'inStock') {
            return product.is_available && product.stock > 0;
        }
        if (filterKey === 'hasDiscount') {
            return product.discount > 0;
        }
        if (product.specifications && product.specifications[filterKey]) {
            return product.specifications[filterKey] === filterValue;
        }
        return false;
    }).length;
};

onMounted(async () => {
    await loadCurrentUser();
    await loadCategoryData();
    if (currentUser.value && currentUser.value.is_superuser) {
        await loadCategories();
    }
});

const loadCurrentUser = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get(`${API_BASE_URL}/users/profile/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            currentUser.value = response.data;
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля пользователя:', error);
    }
};

// Модифицируем функцию загрузки данных категории
const loadCategoryData = async () => {
    isLoading.value = true;
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const categoryId = route.params.id;
        console.log('Запрос товаров для категории ID:', categoryId); // Логируем ID категории
        const response = await axios.get(`${API_BASE_URL}/main/products/?category=${categoryId}`, { headers });
        console.log('Ответ API:', response.data); // Логируем ответ

        originalProducts.value = response.data; // Сохраняем оригинальный список
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

        updateAvailableSpecifications();

        // Загружаем фильтры из URL после получения данных
        loadFiltersFromUrl();
        // Применяем фильтры, если они есть в URL
        if (Object.keys(route.query).length > 0) {
            applyFilters();
        }
    } catch (error) {
        console.error('Ошибка загрузки товаров категории:', error.response ? error.response.data : error.message);
        alert('Ошибка при загрузке товаров категории. Проверьте консоль.');
    } finally {
        isLoading.value = false;
    }
};

// Функции администратора
const createNewProduct = async () => {
    if (!currentUser.value || !currentUser.value.is_superuser) {
        alert('У вас нет прав для добавления товаров');
        return;
    }
    
    await loadAvailableProducts();
    isAddingProducts.value = true;
};

const deleteProduct = async (productId) => {
    if (!currentUser.value || !currentUser.value.is_superuser) {
        alert('У вас нет прав для удаления товаров');
        return;
    }
    
    if (confirm('Вы уверены, что хотите удалить этот товар?')) {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`${API_BASE_URL}/main/products/${productId}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            alert('Товар успешно удален');
            // Обновляем список товаров после удаления
            loadCategoryData();
        } catch (error) {
            console.error('Ошибка удаления товара:', error);
            alert('Ошибка при удалении товара. ' + (error.response?.data?.detail || error.message));
        }
    }
};

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

// Функция для загрузки категорий
const loadCategories = async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.get(`${API_BASE_URL}/main/categories/`, { headers });
        categories.value = response.data;
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
    }
};

// Функция начала редактирования товара
const editProduct = (product) => {
    // Создаем копию товара для редактирования
    editingProduct.value = JSON.parse(JSON.stringify(product));
};

// Функция отмены редактирования
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
        
        console.log('Ответ сервера:', response.data);
        
        // Обновляем товар в списке
        await loadCategoryData();
        
        // Закрываем модальное окно
        editingProduct.value = null;
        alert('Товар успешно обновлен');
    } catch (error) {
        console.error('Ошибка обновления товара:', error);
        alert('Ошибка при обновлении товара. ' + (error.response?.data?.detail || error.message));
    }
};

// Функция для загрузки доступных товаров
const loadAvailableProducts = async () => {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.get(`${API_BASE_URL}/main/products/`, { headers });
        // Фильтруем товары, которые еще не в текущей категории
        availableProducts.value = response.data.filter(product => 
            !categoryProducts.value.some(catProduct => catProduct.id === product.id)
        );
    } catch (error) {
        console.error('Ошибка загрузки товаров:', error);
        alert('Ошибка при загрузке доступных товаров');
    }
};

// Функция добавления выбранных товаров в категорию
const addSelectedProducts = async () => {
    try {
        const token = localStorage.getItem('token');
        const categoryId = route.params.id;

        for (const productId of selectedProducts.value) {
            const product = availableProducts.value.find(p => p.id === productId);
            if (product) {
                // Создаем правильный объект для обновления
                const updateData = {
                    category_id: parseInt(categoryId), // Убедимся, что ID - число
                    name: product.name,
                    sku: product.sku,
                    price: product.price,
                    stock: product.stock,
                    is_available: product.is_available,
                    description: product.description || '',
                    specifications: product.specifications || {}
                };

                await axios.put(
                    `${API_BASE_URL}/main/products/${productId}/`,
                    updateData,
                    { headers: { Authorization: `Bearer ${token}` } }
                );
            }
        }

        // Обновляем список товаров
        await loadCategoryData();
        
        // Сбрасываем состояние
        selectedProducts.value = [];
        isAddingProducts.value = false;
        alert('Товары успешно добавлены в категорию');
    } catch (error) {
        console.error('Ошибка добавления товаров:', error);
        alert('Ошибка при добавлении товаров в категорию: ' + (error.response?.data?.detail || error.message));
    }
};

// Функция отмены добавления товаров
const cancelAddingProducts = () => {
    selectedProducts.value = [];
    isAddingProducts.value = false;
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
    border-radius: 8px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
    position: relative;
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

.admin-delete-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 5;
}

.admin-delete-btn:hover {
    background-color: #ff0000;
}

.admin-actions {
    margin-bottom: 20px;
    display: flex;
    justify-content: flex-end;
}

.admin-button {
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.admin-button:hover {
    background-color: #45a049;
}

.admin-edit-btn {
    position: absolute;
    top: 10px;
    right: 40px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 5;
}

.admin-edit-btn:hover {
    background-color: #45a049;
}

/* Стили для модального окна редактирования */
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
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.form-group label {
    font-weight: bold;
}

.form-group input, .form-group select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.form-buttons {
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

.page-layout {
    display: flex;
    gap: 30px;
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    min-height: calc(100vh - 60px);
}

.filters-sidebar {
    width: 280px;
    height: fit-content;
    position: sticky;
    top: 20px;
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.filters-title {
    font-size: 20px;
    color: #1a1a1a;
    margin: 0 0 24px;
    font-weight: 600;
}

.filter-section {
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 20px;
    margin-bottom: 20px;
}

.filter-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.filter-section h4 {
    font-size: 16px;
    color: #4a5568;
    margin: 0 0 16px;
    font-weight: 500;
}

.price-range {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.price-inputs {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 8px;
    align-items: center;
}

.price-separator {
    color: #718096;
    font-weight: 500;
}

.price-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    color: #2d3748;
}

.price-slider {
    position: relative;
    height: 4px;
    background: #e2e8f0;
    border-radius: 2px;
    margin: 10px 0;
}

.slider-track {
    position: absolute;
    height: 100%;
    background: #6b46c1;
    border-radius: 2px;
}

.range-input {
    position: absolute;
    width: 100%;
    height: 100%;
    appearance: none;
    background: none;
    pointer-events: none;
}

.range-input::-webkit-slider-thumb {
    appearance: none;
    width: 16px;
    height: 16px;
    background: #6b46c1;
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    pointer-events: auto;
    transition: transform 0.2s;
}

.range-input::-webkit-slider-thumb:hover {
    transform: scale(1.2);
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
}

.checkbox-label:hover {
    background: #f7fafc;
}

.checkbox-label input[type="checkbox"] {
    width: 18px;
    height: 18px;
    border: 2px solid #cbd5e0;
    border-radius: 4px;
    cursor: pointer;
}

.checkbox-text {
    font-size: 14px;
    color: #4a5568;
}

.spec-values {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 200px;
    overflow-y: auto;
    padding-right: 8px;
}

.spec-values::-webkit-scrollbar {
    width: 4px;
}

.spec-values::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.spec-values::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 2px;
}

.sort-select {
    width: 100%;
    padding: 10px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    color: #2d3748;
    cursor: pointer;
    transition: all 0.2s;
}

.sort-select:hover {
    border-color: #6b46c1;
}

.reset-filters-btn {
    width: 100%;
    padding: 12px;
    margin-top: 20px;
    background: #e53e3e;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.reset-filters-btn:hover {
    background: #c53030;
    transform: translateY(-2px);
}

.main-content {
    flex: 1;
    min-width: 0;
}

.category-header {
    background: white;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.active-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
}

.filter-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    font-size: 14px;
    color: #4a5568;
    transition: all 0.2s;
}

.filter-tag:hover {
    background: #edf2f7;
}

.remove-filter {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: none;
    color: #a0aec0;
    cursor: pointer;
    padding: 0;
    font-size: 16px;
    transition: all 0.2s;
}

.remove-filter:hover {
    color: #e53e3e;
}

.form-group select[multiple] {
    height: 300px;
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    color: #2d3748;
    background-color: #f8fafc;
}

.form-group select[multiple] option {
    padding: 8px 12px;
    margin: 2px 0;
    border-radius: 4px;
    cursor: pointer;
}

.form-group select[multiple] option:checked {
    background: linear-gradient(0deg, #6b46c1 0%, #6b46c1 100%);
    color: white;
}

.form-group select[multiple] option:hover {
    background-color: #edf2f7;
}

.rating {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 5px;
}

.stars {
    display: inline-flex;
    margin-right: 5px;
}

.star {
    color: #ccc;
    font-size: 18px;
}

.star.filled {
    color: #ffc107;
}

.rating-value {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}
</style>