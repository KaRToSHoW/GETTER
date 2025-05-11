<template>
    <div class="catalog-page">
        <ToastNotification ref="toast" />
        
        <!-- Мобильный фильтр кнопка -->
        <button class="mobile-filters-toggle" @click="showMobileFilters = !showMobileFilters">
            {{ showMobileFilters ? 'Скрыть фильтры' : 'Показать фильтры' }}
            <i class="filter-icon">🔍</i>
        </button>
        
        <div class="catalog-container">
            <!-- Сайдбар с фильтрами -->
            <aside class="filters-sidebar" :class="{ 'mobile-visible': showMobileFilters }">
                <div class="filters-header">
                    <h3 class="filters-title">Фильтры</h3>
                    <button class="close-filters" @click="showMobileFilters = false">×</button>
                </div>
                
                <!-- Фильтр по категориям -->
                <div class="filter-section">
                    <h4 class="filter-heading">Категории</h4>
                    <div class="category-list">
                        <label v-for="category in categories" :key="category.id" class="checkbox-label">
                            <input 
                                type="checkbox" 
                                :value="category.id" 
                                v-model="filters.categoryIds"
                                @change="applyFilters"
                            >
                            <span class="checkbox-text">{{ category.name }}</span>
                        </label>
                    </div>
                </div>
                
                <!-- Фильтр по цене -->
                <div class="filter-section">
                    <h4 class="filter-heading">Цена</h4>
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
                        <div class="price-slider-container">
                            <input 
                                type="range" 
                                v-model="filters.minPrice" 
                                :min="priceRange.min" 
                                :max="priceRange.max"
                                @input="updatePriceRange"
                                class="range-input min-range"
                            >
                            <input 
                                type="range" 
                                v-model="filters.maxPrice" 
                                :min="priceRange.min" 
                                :max="priceRange.max"
                                @input="updatePriceRange"
                                class="range-input max-range"
                            >
                            <div class="price-slider-track">
                                <div class="price-slider-progress" :style="priceRangeStyle"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Фильтр по наличию -->
                <div class="filter-section">
                    <h4 class="filter-heading">Наличие</h4>
                    <label class="checkbox-label">
                        <input 
                            type="checkbox" 
                            v-model="filters.inStock"
                            @change="applyFilters"
                        >
                        <span class="checkbox-text">В наличии</span>
                    </label>
                    <label class="checkbox-label">
                        <input 
                            type="checkbox" 
                            v-model="filters.hasDiscount"
                            @change="applyFilters"
                        >
                        <span class="checkbox-text">Со скидкой</span>
                    </label>
                </div>
                
                <!-- Фильтры по брендам -->
                <div class="filter-section">
                    <h4 class="filter-heading">Бренды</h4>
                    <div class="search-brands">
                        <input 
                            type="text" 
                            v-model="brandSearchQuery" 
                            placeholder="Найти бренд" 
                            class="brand-search-input"
                        >
                    </div>
                    <div class="brands-list">
                        <label v-for="brand in filteredBrands" :key="brand" class="checkbox-label">
                            <input 
                                type="checkbox" 
                                :value="brand" 
                                v-model="filters.brands"
                                @change="applyFilters"
                            >
                            <span class="checkbox-text">{{ brand }}</span>
                        </label>
                    </div>
                </div>
                
                <!-- Фильтры по характеристикам -->
                <div v-for="(values, key) in specifications" 
                     :key="key" 
                     class="filter-section"
                >
                    <h4 class="filter-heading">{{ key }}</h4>
                    <div class="spec-values">
                        <label 
                            v-for="value in values" 
                            :key="value.value" 
                            class="checkbox-label"
                        >
                            <input 
                                type="checkbox" 
                                :value="value.value" 
                                v-model="filters.specifications[key]"
                                @change="applyFilters"
                            >
                            <span class="checkbox-text">{{ value.value }} ({{ value.count }})</span>
                        </label>
                    </div>
                </div>
                
                <!-- Сортировка -->
                <div class="filter-section">
                    <h4 class="filter-heading">Сортировка</h4>
                    <select v-model="filters.sortBy" @change="applyFilters" class="sort-select">
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
                
                <!-- Кнопка сброса фильтров -->
                <button @click="resetFilters" class="reset-filters-btn">
                    Сбросить все фильтры
                </button>
            </aside>
            
            <!-- Основной контент -->
            <main class="catalog-content">
                <div class="catalog-header">
                    <h1 class="catalog-title">Каталог товаров</h1>
                    
                    <!-- Метрика товаров -->
                    <div class="products-count">
                        {{ filteredProducts.length }} {{ getProductsCountText(filteredProducts.length) }}
                    </div>
                    
                    <!-- Мобильная сортировка -->
                    <div class="mobile-sort">
                        <select v-model="filters.sortBy" @change="applyFilters" class="mobile-sort-select">
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
                    
                    <!-- Вид отображения товаров -->
                    <div class="view-controls">
                        <button 
                            @click="viewMode = 'grid'" 
                            :class="['view-btn', { active: viewMode === 'grid' }]" 
                            aria-label="Сетка"
                        >
                            <i class="grid-icon">▣</i>
                        </button>
                        <button 
                            @click="viewMode = 'list'" 
                            :class="['view-btn', { active: viewMode === 'list' }]" 
                            aria-label="Список"
                        >
                            <i class="list-icon">☰</i>
                        </button>
                    </div>
                    
                    <!-- Активные фильтры -->
                    <div v-if="hasActiveFilters" class="active-filters">
                        <div v-for="(filter, index) in activeFiltersDisplay" 
                             :key="index"
                             class="filter-tag"
                        >
                            <span class="filter-tag-text">{{ filter.label }}: {{ filter.value }}</span>
                            <button class="remove-filter" @click="removeFilter(filter.type, filter.key, filter.value)">×</button>
                        </div>
                        <button class="clear-all-filters" @click="resetFilters">Сбросить все</button>
                    </div>
                </div>
                
                <!-- Сетка товаров -->
                <div :class="['products-container', `view-${viewMode}`]">
                    <div v-if="loading" class="loading-spinner">
                        <div class="spinner"></div>
                        <p>Загрузка товаров...</p>
                    </div>
                    
                    <template v-else>
                        <div v-for="product in paginatedProducts" 
                             :key="product.id" 
                             :class="['product-item', `product-${viewMode}`, { new: product.isNew }]">
                            
                            <div class="product-image-container">
                                <router-link :to="`/product/${product.id}`">
                                    <img :src="product.image || defaultImage" :alt="product.name" class="product-image" />
                                    <div v-if="product.discount" class="discount-badge">-{{ product.discount }}%</div>
                                </router-link>
                                <button 
                                    :class="['wishlist-toggle', { 'in-wishlist': isInWishlist(product.id) }]"
                                    @click="toggleWishlist(product)"
                                    :aria-label="isInWishlist(product.id) ? 'Удалить из избранного' : 'Добавить в избранное'"
                                >
                                    <i class="heart-icon">❤</i>
                                </button>
                            </div>
                            
                            <div class="product-details">
                                <div class="product-category">{{ getCategoryName(product.category) }}</div>
                                <h3 class="product-name">
                                    <router-link :to="`/product/${product.id}`">{{ product.name }}</router-link>
                                </h3>
                                
                                <div class="product-rating">
                                    <div class="stars" v-if="product.average_rating">
                                        <span v-for="i in 5" :key="i" class="star">
                                            <span v-if="i <= Math.round(product.average_rating)" class="filled">★</span>
                                            <span v-else>☆</span>
                                        </span>
                                    </div>
                                    <div class="stars" v-else>
                                        <span v-for="i in 5" :key="i" class="star">☆</span>
                                    </div>
                                    <span class="rating-count" v-if="product.reviews_count > 0">({{ product.reviews_count }} {{ getReviewsCountText(product.reviews_count) }})</span>
                                    <span class="rating-count no-reviews" v-else>Нет отзывов</span>
                                </div>
                                
                                <div class="product-prices">
                                    <span v-if="product.discount > 0" class="old-price">{{ formatPrice(product.price) }} ₽</span>
                                    <span class="price">{{ formatPrice(product.discount > 0 ? product.discounted_price : product.price) }} ₽</span>
                                </div>
                                
                                <div class="product-availability" :class="{ 'out-of-stock': !product.is_available }">
                                    {{ product.is_available ? 'В наличии' : 'Нет в наличии' }}
                                    <span v-if="product.is_available" class="stock-count">{{ product.stock }} шт.</span>
                                </div>
                                
                                <div v-if="viewMode === 'list'" class="product-description">
                                    {{ product.description || 'Описание отсутствует' }}
                                </div>
                                
                                <div class="product-specs" v-if="viewMode === 'list' && product.specifications">
                                    <div v-for="(value, key) in limitSpecifications(product.specifications)" 
                                         :key="key" 
                                         class="spec-item">
                                        <span class="spec-name">{{ key }}:</span>
                                        <span class="spec-value">{{ value }}</span>
                                    </div>
                                </div>
                                
                                <div class="product-actions">
                                    <div v-if="cartItems[product.id]" class="quantity-controls">
                                        <button @click="decreaseQuantity(product)" class="quantity-btn">−</button>
                                        <span class="quantity-value">{{ cartItems[product.id] }}</span>
                                        <button @click="increaseQuantity(product)" class="quantity-btn">+</button>
                                    </div>
                                    <button 
                                        v-else
                                        @click="addToCart(product)" 
                                        class="add-to-cart-btn"
                                        :disabled="!product.is_available"
                                    >
                                        {{ product.is_available ? 'В корзину' : 'Недоступно' }}
                                    </button>
                                    
                                    <button 
                                        v-if="viewMode === 'list'"
                                        class="compare-btn"
                                        @click="addToCompare(product)"
                                        :disabled="isInCompare(product.id)"
                                    >
                                        {{ isInCompare(product.id) ? 'В сравнении' : 'Сравнить' }}
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div v-if="filteredProducts.length === 0" class="no-products">
                            <h3>Товары не найдены</h3>
                            <p>Попробуйте изменить параметры фильтрации или сбросить фильтры</p>
                            <button @click="resetFilters" class="reset-filters-btn">Сбросить все фильтры</button>
                        </div>
                    </template>
                </div>
                
                <!-- Кнопка "Показать больше" -->
                <div v-if="pageCount > 1" class="show-more-container">
                    <button 
                        v-if="currentPage < pageCount"
                        @click="showMoreProducts" 
                        class="show-more-btn"
                        :disabled="loadingMore"
                    >
                        <span v-if="loadingMore" class="loading-spinner-small"></span>
                        {{ loadingMore ? 'Загрузка...' : 'Показать больше' }}
                    </button>
                    <div v-else class="all-loaded">
                        <span>Все товары загружены</span>
                    </div>
                </div>
                
                <!-- Пагинация -->
                <div v-if="pageCount > 1" class="pagination">
                    <button 
                        @click="goToPage(currentPage - 1)" 
                        :disabled="currentPage === 1"
                        class="pagination-btn prev"
                    >
                        ←
                    </button>
                    
                    <template v-for="n in pageCount" :key="n">
                        <button 
                            v-if="showPageButton(n)"
                            @click="goToPage(n)" 
                            :class="['pagination-btn', { active: currentPage === n }]"
                        >
                            {{ n }}
                        </button>
                        <span v-else-if="showEllipsis(n)" class="pagination-ellipsis">...</span>
                    </template>
                    
                    <button 
                        @click="goToPage(currentPage + 1)" 
                        :disabled="currentPage === pageCount"
                        class="pagination-btn next"
                    >
                        →
                    </button>
                </div>
            </main>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import ToastNotification from './ToastNotification.vue';
import defaultImage from '@/assets/img/Default_product_foto.jpg';

// Константы
const API_BASE_URL = 'http://127.0.0.1:8000';
const ITEMS_PER_PAGE = 12;

// Состояния
const toast = ref(null);
const categories = ref([]);
const allProducts = ref([]);
const filteredProducts = ref([]);
const specifications = ref({});
const cartItems = ref({});
const wishlist = ref([]);
const compareList = ref([]);
const loading = ref(true);
const loadingMore = ref(false);
const showMobileFilters = ref(false);
const brandSearchQuery = ref('');
const viewMode = ref('grid'); // 'grid' или 'list'
const currentPage = ref(1);

// Диапазон цен
const priceRange = ref({
    min: 0,
    max: 100000
});

// Фильтры
const filters = ref({
    categoryIds: [],
    minPrice: null,
    maxPrice: null,
    inStock: false,
    hasDiscount: false,
    brands: [],
    specifications: {},
    sortBy: 'popular'
});

// Расчетные свойства
const priceRangeStyle = computed(() => {
    const min = filters.value.minPrice || priceRange.value.min;
    const max = filters.value.maxPrice || priceRange.value.max;
    const range = priceRange.value.max - priceRange.value.min;
    
    const left = ((min - priceRange.value.min) / range) * 100;
    const right = 100 - ((max - priceRange.value.min) / range) * 100;
    
    return {
        left: `${left}%`,
        right: `${right}%`
    };
});

const allBrands = computed(() => {
    const brandsSet = new Set();
    allProducts.value.forEach(product => {
        if (product.brand) brandsSet.add(product.brand);
    });
    return Array.from(brandsSet).sort();
});

const filteredBrands = computed(() => {
    if (!brandSearchQuery.value) return allBrands.value;
    return allBrands.value.filter(brand => 
        brand.toLowerCase().includes(brandSearchQuery.value.toLowerCase())
    );
});

const hasActiveFilters = computed(() => {
    return (
        filters.value.categoryIds.length > 0 ||
        filters.value.minPrice !== null ||
        filters.value.maxPrice !== null ||
        filters.value.inStock ||
        filters.value.hasDiscount ||
        filters.value.brands.length > 0 ||
        Object.values(filters.value.specifications).some(arr => arr.length > 0)
    );
});

const activeFiltersDisplay = computed(() => {
    const activeFilters = [];
    
    // Категории
    if (filters.value.categoryIds.length > 0) {
        const categoryNames = filters.value.categoryIds.map(id => {
            const category = categories.value.find(c => c.id === id);
            return category ? category.name : 'Unknown';
        }).join(', ');
        
        activeFilters.push({
            type: 'category',
            key: 'category',
            value: categoryNames,
            label: 'Категория'
        });
    }
    
    // Цена
    if (filters.value.minPrice !== null) {
        activeFilters.push({
            type: 'price',
            key: 'minPrice',
            value: `от ${filters.value.minPrice} ₽`,
            label: 'Цена'
        });
    }
    
    if (filters.value.maxPrice !== null) {
        activeFilters.push({
            type: 'price',
            key: 'maxPrice',
            value: `до ${filters.value.maxPrice} ₽`,
            label: 'Цена'
        });
    }
    
    // Наличие
    if (filters.value.inStock) {
        activeFilters.push({
            type: 'availability',
            key: 'inStock',
            value: 'В наличии',
            label: 'Наличие'
        });
    }
    
    // Скидки
    if (filters.value.hasDiscount) {
        activeFilters.push({
            type: 'discount',
            key: 'hasDiscount',
            value: 'Со скидкой',
            label: 'Скидки'
        });
    }
    
    // Бренды
    if (filters.value.brands.length > 0) {
        activeFilters.push({
            type: 'brand',
            key: 'brands',
            value: filters.value.brands.join(', '),
            label: 'Бренд'
        });
    }
    
    // Характеристики
    Object.entries(filters.value.specifications).forEach(([key, values]) => {
        if (values.length > 0) {
            activeFilters.push({
                type: 'specification',
                key: key,
                value: values.join(', '),
                label: key
            });
        }
    });
    
    return activeFilters;
});

const pageCount = computed(() => {
    return Math.ceil(filteredProducts.value.length / ITEMS_PER_PAGE);
});

const paginatedProducts = computed(() => {
    const endIndex = currentPage.value * ITEMS_PER_PAGE;
    return filteredProducts.value.slice(0, endIndex);
});

// Методы
const loadData = async () => {
    loading.value = true;
    
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        // Загружаем категории и продукты
        const [categoriesResponse, productsResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/main/categories/`, { headers }),
            axios.get(`${API_BASE_URL}/main/products/`, { headers })
        ]);

        categories.value = categoriesResponse.data;
        allProducts.value = productsResponse.data.map(product => ({
            ...product,
            discount: product.discount !== undefined ? product.discount : 0
        }));
        
        // Отладочный вывод
        console.log('Структура данных продукта:', allProducts.value[0]);
        
        // Инициализация диапазона цен
        if (allProducts.value.length > 0) {
            const prices = allProducts.value.map(p => p.price);
            priceRange.value.min = Math.floor(Math.min(...prices));
            priceRange.value.max = Math.ceil(Math.max(...prices));
        }
        
        // Извлекаем характеристики для фильтрации
        extractSpecifications();
        
        // Применяем фильтры для начального отображения
        applyFilters();
        
        // Загружаем вишлист и корзину если пользователь авторизован
        if (token) {
            try {
                // Загрузка списка желаемого
                const wishlistResponse = await axios.get(`${API_BASE_URL}/main/wishlist/check/`, { headers });
                wishlist.value = wishlistResponse.data.wishlist || [];
                
                // Загрузка корзины
                const cartResponse = await axios.get(`${API_BASE_URL}/main/cart/`, { headers });
                const cartData = cartResponse.data;
                
                // Обработка данных корзины
                if (Array.isArray(cartData)) {
                    cartData.forEach(item => {
                        cartItems.value[item.product.id] = item.quantity;
                    });
                } else if (cartData && cartData.items && Array.isArray(cartData.items)) {
                    cartData.items.forEach(item => {
                        cartItems.value[item.product.id] = item.quantity;
                    });
                }
            } catch (authError) {
                console.error('Ошибка загрузки персональных данных:', authError);
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        toast.value.showToast('Ошибка при загрузке данных каталога', 'error');
    } finally {
        loading.value = false;
    }
};

const extractSpecifications = () => {
    const specsObj = {};
    
    allProducts.value.forEach(product => {
        if (product.specifications) {
            Object.entries(product.specifications).forEach(([key, value]) => {
                if (!specsObj[key]) {
                    specsObj[key] = {};
                }
                
                // Подсчитываем количество продуктов с этим значением характеристики
                if (!specsObj[key][value]) {
                    specsObj[key][value] = 1;
                } else {
                    specsObj[key][value]++;
                }
                
                // Инициализируем массив для фильтрации, если его еще нет
                if (!filters.value.specifications[key]) {
                    filters.value.specifications[key] = [];
                }
            });
        }
    });
    
    // Преобразуем структуру для удобного отображения
    Object.entries(specsObj).forEach(([key, valueObj]) => {
        specifications.value[key] = Object.entries(valueObj).map(([value, count]) => ({
            value,
            count
        }));
    });
};

const applyFilters = () => {
    // Сбрасываем на первую страницу при изменении фильтров
    currentPage.value = 1;
    
    // Фильтруем продукты
    filteredProducts.value = allProducts.value.filter(product => {
        // Фильтр по категории
        if (filters.value.categoryIds.length > 0 && !filters.value.categoryIds.includes(product.category.id)) {
            return false;
        }
        
        // Фильтр по цене
        if (filters.value.minPrice && product.price < filters.value.minPrice) {
            return false;
        }
        
        if (filters.value.maxPrice && product.price > filters.value.maxPrice) {
            return false;
        }
        
        // Фильтр по наличию
        if (filters.value.inStock && (!product.is_available || product.stock === 0)) {
            return false;
        }
        
        // Фильтр по скидкам
        if (filters.value.hasDiscount && product.discount <= 0) {
            return false;
        }
        
        // Фильтр по брендам
        if (filters.value.brands.length > 0 && !filters.value.brands.includes(product.brand)) {
            return false;
        }
        
        // Фильтр по характеристикам
        for (const [key, values] of Object.entries(filters.value.specifications)) {
            if (values.length > 0) {
                // Если у продукта нет этой характеристики или значение не входит в выбранные
                if (!product.specifications || 
                    !product.specifications[key] || 
                    !values.includes(product.specifications[key])) {
                    return false;
                }
            }
        }
        
        return true;
    });
    
    // Сортировка
    sortProducts();
};

const debouncedApplyFilters = (() => {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            applyFilters();
        }, 300);
    };
})();

const sortProducts = () => {
    switch (filters.value.sortBy) {
        case 'popular':
            // Сортировка по популярности (по среднему рейтингу)
            filteredProducts.value.sort((a, b) => {
                const ratingA = a.average_rating || 0;
                const ratingB = b.average_rating || 0;
                return ratingB - ratingA;
            });
            break;
            
        case 'price-asc':
            // Сортировка по возрастанию цены
            filteredProducts.value.sort((a, b) => a.price - b.price);
            break;
            
        case 'price-desc':
            // Сортировка по убыванию цены
            filteredProducts.value.sort((a, b) => b.price - a.price);
            break;
            
        case 'new':
            // Сортировка по новизне (временно по ID, предполагая, что новые имеют больший ID)
            filteredProducts.value.sort((a, b) => b.id - a.id);
            break;
            
        case 'rating':
            // Сортировка по рейтингу
            filteredProducts.value.sort((a, b) => {
                const ratingA = a.average_rating || 0;
                const ratingB = b.average_rating || 0;
                return ratingB - ratingA;
            });
            break;
            
        case 'discount':
            // Сортировка по размеру скидки
            filteredProducts.value.sort((a, b) => {
                const discountA = a.discount || 0;
                const discountB = b.discount || 0;
                return discountB - discountA;
            });
            break;
            
        case 'name-asc':
            // Сортировка по названию А-Я
            filteredProducts.value.sort((a, b) => a.name.localeCompare(b.name));
            break;
            
        case 'name-desc':
            // Сортировка по названию Я-А
            filteredProducts.value.sort((a, b) => b.name.localeCompare(a.name));
            break;
    }
};

const resetFilters = () => {
    filters.value = {
        categoryIds: [],
        minPrice: null,
        maxPrice: null,
        inStock: false,
        hasDiscount: false,
        brands: [],
        specifications: {},
        sortBy: 'popular'
    };
    
    // Восстанавливаем пустые массивы для характеристик
    Object.keys(specifications.value).forEach(key => {
        filters.value.specifications[key] = [];
    });
    
    // Сбрасываем на первую страницу
    currentPage.value = 1;
    
    applyFilters();
    showMobileFilters.value = false;
};

const removeFilter = (type, key) => {
    if (type === 'category') {
        filters.value.categoryIds = [];
    } else if (type === 'price') {
        if (key === 'minPrice') filters.value.minPrice = null;
        if (key === 'maxPrice') filters.value.maxPrice = null;
    } else if (type === 'availability') {
        filters.value.inStock = false;
    } else if (type === 'discount') {
        filters.value.hasDiscount = false;
    } else if (type === 'brand') {
        filters.value.brands = [];
    } else if (type === 'specification') {
        filters.value.specifications[key] = [];
    }
    
    applyFilters();
};

const updatePriceRange = () => {
    // Проверка, чтобы минимальная цена не превышала максимальную
    if (filters.value.minPrice > filters.value.maxPrice) {
        filters.value.minPrice = filters.value.maxPrice;
    }
    
    debouncedApplyFilters();
};

const getCategoryName = (category) => {
    return category ? category.name : 'Без категории';
};

const formatPrice = (price) => {
    return price.toLocaleString('ru-RU');
};

const getProductsCountText = (count) => {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;
    
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
        return 'товаров';
    }
    
    if (lastDigit === 1) {
        return 'товар';
    }
    
    if (lastDigit >= 2 && lastDigit <= 4) {
        return 'товара';
    }
    
    return 'товаров';
};

const getReviewsCountText = (count) => {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;
    
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
        return 'отзывов';
    }
    
    if (lastDigit === 1) {
        return 'отзыв';
    }
    
    if (lastDigit >= 2 && lastDigit <= 4) {
        return 'отзыва';
    }
    
    return 'отзывов';
};

const limitSpecifications = (specs, limit = 5) => {
    const result = {};
    const entries = Object.entries(specs);
    
    for (let i = 0; i < Math.min(limit, entries.length); i++) {
        const [key, value] = entries[i];
        result[key] = value;
    }
    
    return result;
};

// Пагинация
const goToPage = (page) => {
    currentPage.value = page;
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

const showPageButton = (page) => {
    // Всегда показываем первую, последнюю и текущую страницы
    if (page === 1 || page === pageCount.value || page === currentPage.value) {
        return true;
    }
    
    // Показываем соседние страницы с текущей
    if (Math.abs(page - currentPage.value) <= 1) {
        return true;
    }
    
    return false;
};

const showEllipsis = (page) => {
    // Показываем многоточие между группами страниц
    if ((page === 2 && currentPage.value > 3) || 
        (page === pageCount.value - 1 && currentPage.value < pageCount.value - 2)) {
        return true;
    }
    
    return false;
};

// Функции работы с корзиной и списком желаемого
const addToCart = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
        toast.value.showToast('Пожалуйста, войдите в систему для добавления в корзину', 'warning');
        return;
    }

    if (!product.is_available) {
        toast.value.showToast('Товар недоступен для добавления в корзину', 'error');
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
        toast.value.showToast(`Товар "${product.name}" добавлен в корзину`, 'success');
    } catch (error) {
        console.error('Ошибка добавления в корзину:', error);
        toast.value.showToast('Не удалось добавить товар в корзину', 'error');
    }
};

const increaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const newQuantity = (cartItems.value[product.id] || 0) + 1;
        if (newQuantity > product.stock) {
            toast.value.showToast('Нельзя добавить больше, чем есть в наличии', 'warning');
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
        console.error('Ошибка увеличения количества:', error);
        toast.value.showToast('Не удалось изменить количество товара', 'error');
    }
};

const decreaseQuantity = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const newQuantity = (cartItems.value[product.id] || 0) - 1;
        
        if (newQuantity <= 0) {
            // Получаем ID элемента корзины
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
        console.error('Ошибка уменьшения количества:', error);
        toast.value.showToast('Не удалось изменить количество товара', 'error');
    }
};

const toggleWishlist = async (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
        toast.value.showToast('Пожалуйста, войдите в систему для управления списком желаемого', 'warning');
        return;
    }

    try {
        if (isInWishlist(product.id)) {
            await axios.delete(`${API_BASE_URL}/main/wishlist/remove/${product.id}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value = wishlist.value.filter(id => id !== product.id);
            toast.value.showToast('Товар удален из списка желаемого', 'success');
        } else {
            await axios.post(`${API_BASE_URL}/main/wishlist/add/`, {
                product_id: product.id
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            wishlist.value.push(product.id);
            toast.value.showToast('Товар добавлен в список желаемого', 'success');
        }
    } catch (error) {
        console.error('Ошибка управления списком желаемого:', error);
        toast.value.showToast('Ошибка при обновлении списка желаемого', 'error');
    }
};

const isInWishlist = (productId) => {
    return wishlist.value.includes(productId);
};

const addToCompare = (product) => {
    if (compareList.value.length >= 4) {
        toast.value.showToast('В списке сравнения может быть не более 4 товаров', 'warning');
        return;
    }
    
    if (isInCompare(product.id)) return;
    
    compareList.value.push(product.id);
    toast.value.showToast(`Товар "${product.name}" добавлен к сравнению`, 'success');
};

const isInCompare = (productId) => {
    return compareList.value.includes(productId);
};

// Функция для показа большего количества товаров
const showMoreProducts = () => {
    if (currentPage.value < pageCount.value) {
        loadingMore.value = true;
        
        // Запоминаем текущее количество товаров перед загрузкой
        const currentProductsCount = paginatedProducts.value.length;
        
        // Показываем следующую порцию товаров
        currentPage.value++;
        
        // Имитация загрузки для лучшего UX
        setTimeout(() => {
            // Находим первый новый товар
            const productItems = document.querySelectorAll('.product-item');
            if (productItems.length > currentProductsCount) {
                const firstNewProduct = productItems[currentProductsCount];
                if (firstNewProduct) {
                    // Плавно прокручиваем к первому новому товару
                    firstNewProduct.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                    
                    // Добавляем эффект появления для новых товаров
                    for (let i = currentProductsCount; i < productItems.length; i++) {
                        productItems[i].classList.add('new-product-animation');
                    }
                }
            }
            loadingMore.value = false;
        }, 800); // Имитируем время загрузки
    }
};

// Отслеживаем изменения для сохранения в localStorage
watch(viewMode, (newValue) => {
    localStorage.setItem('catalogViewMode', newValue);
});

// Загрузка данных при монтировании компонента
onMounted(() => {
    // Восстанавливаем режим просмотра из localStorage
    const savedViewMode = localStorage.getItem('catalogViewMode');
    if (savedViewMode) {
        viewMode.value = savedViewMode;
    }
    
    loadData();
});
</script>

<style scoped>
/* Основные стили каталога */
.catalog-page {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    font-family: var(--font-family);
}

.catalog-container {
    display: flex;
    gap: 30px;
    min-height: 600px;
}

/* Стили для сайдбара с фильтрами */
.filters-sidebar {
    flex: 0 0 280px;
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    height: fit-content;
    position: sticky;
    top: 80px;
}

.filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.filters-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin: 0;
}

.close-filters {
    display: none;
    background: none;
    border: none;
    font-size: 24px;
    color: #888;
    cursor: pointer;
}

.filter-section {
    margin-bottom: 24px;
    border-bottom: 1px solid #eee;
    padding-bottom: 20px;
}

.filter-section:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.filter-heading {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin: 0 0 12px;
}

/* Стили для чекбоксов */
.checkbox-label {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    cursor: pointer;
    position: relative;
    padding-left: 30px;
    font-size: 14px;
    user-select: none;
}

.checkbox-label input[type="checkbox"] {
    position: absolute;
    opacity: 0;
}

.checkbox-label input[type="checkbox"] + .checkbox-text::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 18px;
    height: 18px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: white;
    transition: all 0.2s ease;
}

.checkbox-label input[type="checkbox"]:checked + .checkbox-text::before {
    background-color: #6b46c1;
    border-color: #6b46c1;
}

.checkbox-label input[type="checkbox"]:checked + .checkbox-text::after {
    content: '✓';
    position: absolute;
    left: 4px;
    top: 50%;
    transform: translateY(-50%);
    color: white;
    font-size: 13px;
}

.checkbox-text {
    color: #333;
    font-size: 14px;
    transition: all 0.2s ease;
}

.checkbox-label:hover .checkbox-text {
    color: #6b46c1;
}

/* Стили для фильтра цены */
.price-range {
    margin-top: 12px;
}

.price-inputs {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.price-input {
    width: 100px;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    color: #333;
}

.price-separator {
    margin: 0 10px;
    color: #777;
}

.price-slider-container {
    position: relative;
    height: 40px;
}

.range-input {
    position: absolute;
    top: 0;
    width: 100%;
    -webkit-appearance: none;
    pointer-events: none;
    background: none;
    z-index: 10;
}

.range-input::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #6b46c1;
    border: 2px solid white;
    cursor: pointer;
    pointer-events: auto;
    margin-top: -7px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.range-input::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #6b46c1;
    border: 2px solid white;
    cursor: pointer;
    pointer-events: auto;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.price-slider-track {
    position: absolute;
    top: 8px;
    width: 100%;
    height: 4px;
    background: #ddd;
    border-radius: 4px;
}

.price-slider-progress {
    position: absolute;
    height: 100%;
    background: #6b46c1;
    border-radius: 4px;
    top: 0;
}

/* Стили для поиска брендов */
.search-brands {
    margin-bottom: 12px;
}

.brand-search-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    color: #333;
}

.brands-list {
    max-height: 200px;
    overflow-y: auto;
    padding-right: 5px;
}

.brands-list::-webkit-scrollbar {
    width: 4px;
}

.brands-list::-webkit-scrollbar-thumb {
    background-color: #ccc;
    border-radius: 4px;
}

.brands-list::-webkit-scrollbar-track {
    background-color: #f5f5f5;
}

/* Стили для сортировки */
.sort-select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    color: #333;
    background-color: white;
    cursor: pointer;
}

.reset-filters-btn {
    width: 100%;
    padding: 10px;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 6px;
    color: #555;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.reset-filters-btn:hover {
    background-color: #eee;
    color: #333;
}

/* Стили для основного контента */
.catalog-content {
    flex: 1;
    min-width: 0; /* Для корректной работы flex */
}

.catalog-header {
    margin-bottom: 20px;
}

.catalog-title {
    font-size: 28px;
    font-weight: 700;
    color: #333;
    margin: 0 0 15px;
}

.products-count {
    font-size: 14px;
    color: #777;
    margin-bottom: 15px;
}

.mobile-sort {
    display: none;
}

.view-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.view-btn {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #ddd;
    border-radius: 6px;
    background-color: white;
    color: #777;
    cursor: pointer;
    transition: all 0.2s ease;
}

.view-btn.active {
    background-color: #6b46c1;
    color: white;
    border-color: #6b46c1;
}

.view-btn:hover:not(.active) {
    background-color: #f5f5f5;
}

/* Стили для активных фильтров */
.active-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 20px;
}

.filter-tag {
    display: flex;
    align-items: center;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 6px 12px;
    font-size: 13px;
}

.filter-tag-text {
    margin-right: 8px;
}

.remove-filter {
    background: none;
    border: none;
    color: #777;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    line-height: 1;
}

.clear-all-filters {
    background: none;
    border: none;
    color: #6b46c1;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    padding: 6px 10px;
    text-decoration: underline;
}

/* Стили для сетки товаров */
.products-container {
    position: relative;
    min-height: 400px;
}

.view-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.view-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.product-grid {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    transition: all 0.3s ease;
    position: relative;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.product-grid:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.product-list {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    padding: 20px;
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 20px;
    position: relative;
}

.product-image-container {
    position: relative;
    aspect-ratio: 1 / 1;
    overflow: hidden;
}

.product-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: all 0.3s ease;
}

.product-grid:hover .product-image,
.product-list:hover .product-image {
    transform: scale(1.05);
}

.discount-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    background-color: #ff5252;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.wishlist-toggle {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: white;
    border: none;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 5;
    transition: all 0.2s ease;
}

.wishlist-toggle .heart-icon {
    font-size: 18px;
    color: #ddd;
    transition: all 0.2s ease;
}

.wishlist-toggle.in-wishlist .heart-icon {
    color: #ff5252;
}

.wishlist-toggle:hover {
    transform: scale(1.1);
}

.product-details {
    padding: 15px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.product-category {
    font-size: 12px;
    color: #777;
    margin-bottom: 5px;
}

.product-name {
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 10px;
    line-height: 1.3;
}

.product-name a {
    color: #333;
    text-decoration: none;
    transition: color 0.2s ease;
}

.product-name a:hover {
    color: #6b46c1;
}

.product-rating {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.stars {
    display: flex;
    margin-right: 5px;
}

.star {
    font-size: 14px;
    color: #ccc;
}

.star .filled {
    color: #ffb800;
}

.rating-count {
    font-size: 12px;
    color: #777;
}

.rating-count.no-reviews {
    color: #aaa;
    font-style: italic;
    font-size: 11px;
}

.product-prices {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.old-price {
    font-size: 14px;
    color: #999;
    text-decoration: line-through;
}

.current-price {
    font-size: 18px;
    font-weight: 700;
    color: #333;
}

.product-availability {
    font-size: 14px;
    color: #27ae60;
    margin-bottom: 10px;
}

.product-availability.out-of-stock {
    color: #e74c3c;
}

.stock-count {
    font-size: 12px;
    color: #777;
    margin-left: 5px;
}

.product-description {
    font-size: 14px;
    color: #555;
    margin: 10px 0;
    line-height: 1.4;
    max-height: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}

.product-specs {
    margin: 10px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px 15px;
}

.spec-item {
    font-size: 13px;
    color: #555;
}

.spec-name {
    font-weight: 600;
    color: #666;
}

.product-actions {
    margin-top: auto;
    display: flex;
    gap: 10px;
    padding-top: 10px;
}

.add-to-cart-btn {
    flex: 1;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.add-to-cart-btn:hover {
    background-color: #553c9a;
}

.add-to-cart-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.quantity-controls {
    display: flex;
    align-items: center;
    flex: 1;
    background-color: #f5f5f5;
    border-radius: 6px;
    overflow: hidden;
}

.quantity-btn {
    width: 36px;
    height: 36px;
    background-color: #e0e0e0;
    border: none;
    color: #333;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.quantity-btn:hover {
    background-color: #d0d0d0;
}

.quantity-value {
    flex: 1;
    text-align: center;
    font-size: 14px;
    font-weight: 600;
}

.compare-btn {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 0 15px;
    color: #555;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.compare-btn:hover:not(:disabled) {
    background-color: #e8e8e8;
}

.compare-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Стили для отсутствия товаров */
.no-products {
    text-align: center;
    padding: 40px 20px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.no-products h3 {
    font-size: 20px;
    color: #333;
    margin-bottom: 10px;
}

.no-products p {
    font-size: 14px;
    color: #777;
    margin-bottom: 20px;
}

.no-products .reset-filters-btn {
    width: auto;
    display: inline-block;
    padding: 10px 20px;
    background-color: #6b46c1;
    color: white;
    border: none;
}

.no-products .reset-filters-btn:hover {
    background-color: #553c9a;
}

/* Стили для пагинации */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
    gap: 5px;
}

.pagination-btn {
    min-width: 36px;
    height: 36px;
    border: 1px solid #ddd;
    background-color: white;
    border-radius: 6px;
    font-size: 14px;
    color: #555;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.pagination-btn:hover:not(:disabled) {
    background-color: #f5f5f5;
}

.pagination-btn.active {
    background-color: #6b46c1;
    color: white;
    border-color: #6b46c1;
}

.pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-ellipsis {
    margin: 0 5px;
    color: #777;
}

/* Стили для кнопки "Показать больше" */
.show-more-container {
    display: flex;
    justify-content: center;
    margin-top: 30px;
}

.show-more-btn {
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.2);
    min-width: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.show-more-btn:hover:not(:disabled) {
    background-color: #553c9a;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(107, 70, 193, 0.3);
}

.show-more-btn:disabled {
    background-color: #8a70c9;
    cursor: not-allowed;
    opacity: 0.8;
}

.loading-spinner-small {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid #ffffff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 8px;
}

.all-loaded {
    font-size: 14px;
    color: #888;
    padding: 10px;
    text-align: center;
}

/* Стили для загрузки */
.loading-spinner {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.8);
    z-index: 5;
}

.spinner {
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

/* Кнопка мобильного фильтра */
.mobile-filters-toggle {
    display: none;
    width: 100%;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 15px;
    transition: background-color 0.2s ease;
    align-items: center;
    justify-content: center;
}

.mobile-filters-toggle .filter-icon {
    margin-left: 8px;
}

.mobile-filters-toggle:hover {
    background-color: #553c9a;
}

/* Адаптивные стили */
@media (max-width: 992px) {
    .catalog-container {
        gap: 20px;
    }
    
    .filters-sidebar {
        flex: 0 0 240px;
    }
    
    .view-grid {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    }
}

@media (max-width: 768px) {
    .catalog-page {
        padding: 15px;
    }
    
    .mobile-filters-toggle {
        display: flex;
    }
    
    .catalog-container {
        flex-direction: column;
    }
    
    .filters-sidebar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1000;
        overflow-y: auto;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        box-shadow: none;
        border-radius: 0;
    }
    
    .filters-sidebar.mobile-visible {
        transform: translateX(0);
    }
    
    .close-filters {
        display: block;
    }
    
    .mobile-sort {
        display: block;
        margin-bottom: 15px;
    }
    
    .mobile-sort-select {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
        color: #333;
        background-color: white;
    }
    
    .view-list .product-list {
        grid-template-columns: 100px 1fr;
        gap: 15px;
        padding: 10px;
    }
    
    .product-list .product-description,
    .product-list .product-specs {
        display: none;
    }
    
    .compare-btn {
        display: none;
    }
    
    .show-more-btn {
        width: 100%;
    }
}

@media (max-width: 480px) {
    .catalog-page {
        padding: 10px;
    }
    
    .catalog-title {
        font-size: 24px;
    }
    
    .view-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 10px;
    }
    
    .view-list .product-list {
        grid-template-columns: 80px 1fr;
        gap: 10px;
        padding: 8px;
    }
    
    .product-details {
        padding: 10px;
    }
    
    .product-name {
        font-size: 14px;
    }
    
    .current-price {
        font-size: 16px;
    }
    
    .product-actions {
        flex-direction: column;
        gap: 5px;
    }
    
    .wishlist-toggle {
        width: 30px;
        height: 30px;
    }
    
    .wishlist-toggle .heart-icon {
        font-size: 16px;
    }
    
    .discount-badge {
        padding: 2px 6px;
        font-size: 10px;
    }
    
    .show-more-container {
        margin-top: 20px;
    }
    
    .show-more-btn {
        padding: 10px 20px;
        font-size: 14px;
    }
    
    .pagination {
        margin-top: 15px;
    }
}

/* Анимация для новых товаров */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.new-product-animation {
    animation: fadeInUp 0.6s ease forwards;
}
</style> 