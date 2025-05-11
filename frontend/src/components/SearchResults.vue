<template>
    <div class="search-results">
        <div class="search-header">
            <h2>Результаты поиска: "{{ searchQuery }}"</h2>
            <div class="search-filters">
                <select v-model="sortBy" class="sort-select">
                    <option value="relevance">По релевантности</option>
                    <option value="price-asc">Цена: по возрастанию</option>
                    <option value="price-desc">Цена: по убыванию</option>
                    <option value="name">По названию</option>
                </select>
                <div class="price-filter">
                    <input 
                        type="number" 
                        v-model.number="minPrice" 
                        placeholder="Мин. цена"
                    />
                    <input 
                        type="number" 
                        v-model.number="maxPrice" 
                        placeholder="Макс. цена"
                    />
                </div>
            </div>
        </div>

        <div v-if="loading" class="loading">
            Загрузка...
        </div>
        <div v-else-if="error" class="error">
            {{ error }}
        </div>
        <div v-else-if="filteredProducts.length === 0" class="no-results">
            По вашему запросу ничего не найдено
        </div>
        <div v-else class="products-grid">
            <div v-for="product in filteredProducts" :key="product.id" class="product-card">
                <router-link :to="'/product/' + product.id">
                    <div class="product-image">
                        <img :src="product.image || defaultImageProduct" :alt="product.name">
                    </div>
                    <div class="product-info">
                        <h3>{{ product.name }}</h3>
                        <p class="price">{{ product.price }} ₽</p>
                        <p class="category">{{ product.category.name }}</p>
                        <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                            {{ product.is_available ? 'В наличии' : 'Нет в наличии' }}
                        </div>
                    </div>
                </router-link>
            </div>
        </div>

        <div v-if="recommendedProducts.length > 0" class="recommended-section">
            <h2>Рекомендуемые товары</h2>
            <div class="products-grid">
                <div v-for="product in recommendedProducts" :key="product.id" class="product-card">
                    <router-link :to="'/product/' + product.id">
                        <div class="product-image">
                            <img :src="product.image || defaultImageProduct" :alt="product.name">
                        </div>
                        <div class="product-info">
                            <h3>{{ product.name }}</h3>
                            <p class="price">{{ product.price }} ₽</p>
                            <p class="category">{{ product.category.name }}</p>
                            <div class="availability" :class="{ 'out-of-stock': !product.is_available }">
                                {{ product.is_available ? 'В наличии' : 'Нет в наличии' }}
                            </div>
                        </div>
                    </router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import defaultImageProduct from '@/assets/img/Default_product_foto.jpg';

export default {
    name: 'SearchResults',
    setup() {
        const route = useRoute();
        const products = ref([]);
        const loading = ref(true);
        const error = ref(null);
        const sortBy = ref('relevance');
        const minPrice = ref(null);
        const maxPrice = ref(null);
        const recommendedProducts = ref([]);

        const searchQuery = computed(() => route.query.q || '');
        const API_BASE_URL = 'http://127.0.0.1:8000';

        const fetchProducts = async () => {
            loading.value = true;
            error.value = null;
            try {
                const response = await axios.get(`${API_BASE_URL}/main/products/search/advanced/`, {
                    params: {
                        search: searchQuery.value,
                        min_price: minPrice.value,
                        max_price: maxPrice.value,
                        category: route.query.category
                    }
                });
                products.value = response.data.products || [];
                // Сразу после получения результатов поиска загружаем рекомендации,
                // если результатов поиска мало или их нет
                if (products.value.length < 3) {
                    fetchRecommendedProducts();
                }
            } catch (err) {
                error.value = 'Ошибка при загрузке результатов поиска';
                console.error('Ошибка поиска:', err);
            } finally {
                loading.value = false;
            }
        };

        const fetchRecommendedProducts = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/main/products/popular-wishlist/`);
                recommendedProducts.value = response.data;
            } catch (err) {
                console.error('Ошибка загрузки рекомендаций:', err);
            }
        };

        const filteredProducts = computed(() => {
            let result = [...products.value];

            // Фильтрация по цене
            if (minPrice.value !== null) {
                result = result.filter(p => p.price >= minPrice.value);
            }
            if (maxPrice.value !== null) {
                result = result.filter(p => p.price <= maxPrice.value);
            }

            // Сортировка
            switch (sortBy.value) {
                case 'price-asc':
                    result.sort((a, b) => a.price - b.price);
                    break;
                case 'price-desc':
                    result.sort((a, b) => b.price - a.price);
                    break;
                case 'name':
                    result.sort((a, b) => a.name.localeCompare(b.name));
                    break;
                // По умолчанию оставляем порядок по релевантности
            }

            return result;
        });

        // Следим за изменениями параметров поиска
        watch(() => route.query.q, fetchProducts);
        watch([minPrice, maxPrice], () => {
            if (products.value.length > 0) {
                fetchProducts();
            }
        });

        onMounted(() => {
            fetchProducts();
            fetchRecommendedProducts();
        });

        return {
            searchQuery,
            products,
            loading,
            error,
            sortBy,
            minPrice,
            maxPrice,
            filteredProducts,
            recommendedProducts,
            defaultImageProduct
        };
    }
};
</script>

<style scoped>
.search-results {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.search-header {
    margin-bottom: 24px;
}

.search-header h2 {
    font-size: 24px;
    color: #333;
    margin-bottom: 16px;
}

.search-filters {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 20px;
}

.sort-select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    min-width: 200px;
}

.price-filter {
    display: flex;
    gap: 8px;
}

.price-filter input {
    width: 120px;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 24px;
}

.product-card {
    border: 1px solid #eee;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-card a {
    text-decoration: none;
    color: inherit;
}

.product-image {
    width: 100%;
    height: 200px;
    overflow: hidden;
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.product-info {
    padding: 16px;
}

.product-info h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
    color: #333;
}

.price {
    font-size: 18px;
    font-weight: bold;
    color: #6b46c1;
    margin: 8px 0;
}

.category {
    font-size: 14px;
    color: #666;
    margin: 4px 0;
}

.availability {
    font-size: 14px;
    color: #22c55e;
}

.availability.out-of-stock {
    color: #ef4444;
}

.loading {
    text-align: center;
    padding: 40px;
    font-size: 18px;
    color: #666;
}

.error {
    text-align: center;
    padding: 40px;
    color: #ef4444;
}

.no-results {
    text-align: center;
    padding: 40px;
    color: #666;
}

.recommended-section {
    margin-top: 60px;
    padding-top: 40px;
    border-top: 1px solid #eee;
}

.recommended-section h2 {
    font-size: 24px;
    color: #333;
    margin-bottom: 24px;
}

@media (max-width: 768px) {
    .search-filters {
        flex-direction: column;
        align-items: stretch;
    }

    .price-filter {
        flex-direction: row;
    }

    .products-grid {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
    }
}
</style>