<template>
    <header>
        <div class="header-content">
            
            <router-link to="/home" class="logo-container"><h1 class="logo">GETTER</h1></router-link>
            
            <!-- Мобильная кнопка меню -->
            <button class="mobile-menu-toggle" @click="toggleMobileMenu" aria-label="Открыть меню">
                <div class="menu-icon-wrapper">
                    <span class="mobile-menu-icon" :class="{ 'open': mobileMenuOpen }"></span>
                </div>
            </button>
            
            <!-- Кнопка поиска для мобильных -->
            <button class="mobile-search-toggle" @click="toggleSearchBar" aria-label="Поиск">
                <i class="search-icon">🔍</i>
            </button>
            
            <div class="search-bar" :class="{ 'mobile-visible': searchBarVisible }">
                <div class="search-container">
                    <input 
                        type="text" 
                        v-model="searchQuery" 
                        @input="handleInput"
                        @keyup.enter="handleSearch"
                        @focus="showDropdown = true"
                        placeholder="Поиск" 
                    />
                    <button @click="handleSearch" class="search-button">
                        🔍
                    </button>
                    
                    <!-- Выпадающий список с результатами -->
                    <div v-if="showDropdown && searchResults.length > 0" class="search-dropdown">
                        <div 
                            v-for="product in searchResults" 
                            :key="product.id" 
                            class="search-item"
                            @click="goToProduct(product)"
                        >
                            <div class="search-item-image">
                                <img :src="product.image ? `${API_BASE_URL}/media/${product.image}` : defaultImageProduct" :alt="product.name">
                            </div>
                            <div class="search-item-info">
                                <div class="search-item-name">{{ product.name }}</div>
                                <div class="search-item-price">{{ product.price }} ₽</div>
                                <div class="search-item-category">{{ product.category.name }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Десктопная навигация с дропдауном -->
            <nav class="desktop-nav">
                <ul>
                    <li><router-link to="/catalog">Каталог</router-link></li>
                    <li><router-link to="/cart">Корзина</router-link></li>
                    <li class="profile-dropdown">
                        <router-link to="/profile">Профиль</router-link>
                        <div class="dropdown-menu">
                            <ul>
                                <li v-if="!isAuthenticated"><router-link to="/login">Войти</router-link></li>
                                <li v-if="!isAuthenticated"><router-link to="/register">Регистрация</router-link></li>
                                <li v-if="isAuthenticated"><router-link to="/profile">Профиль</router-link></li>
                                <li v-if="isAuthenticated"><router-link to="/favorites">Понравившиеся товары</router-link></li>
                                <li v-if="isAuthenticated"><a href="#" @click.prevent="logout">Выйти</a></li>
                            </ul>
                        </div>
                    </li>
                    <li class="accessibility-item">
                        <!-- Кнопка доступности -->
                        <div class="accessibility-toggle">
                            <button @click="toggleAccessibilityMenu" aria-label="Настройки доступности" class="accessibility-button">
                                <i class="accessibility-icon">👁️</i>
                            </button>
                            
                            <!-- Выпадающее меню настроек доступности -->
                            <div v-if="showAccessibilityMenu" class="accessibility-menu">
                                <h3>Настройки доступности</h3>
                                
                                <!-- Тип шрифта -->
                                <div class="accessibility-section">
                                    <label>Тип шрифта:</label>
                                    <div class="select-group">
                                        <select v-model="accessibilitySettings.fontType" @change="updateFontFamily">
                                            <option value="sans-serif">Без засечек</option>
                                            <option value="serif">С засечками</option>
                                            <option value="monospace">Моноширинный</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <!-- Размер шрифта -->
                                <div class="accessibility-section">
                                    <label>Размер шрифта:</label>
                                    <div class="select-group">
                                        <select v-model="accessibilitySettings.fontSizePreset" @change="setFontSizeFromPreset">
                                            <option value="small">Маленький</option>
                                            <option value="medium">Средний</option>
                                            <option value="large">Большой</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <!-- Интервал между буквами -->
                                <div class="accessibility-section">
                                    <label>Интервал между буквами:</label>
                                    <div class="select-group">
                                        <select v-model="accessibilitySettings.letterSpacingPreset" @change="setLetterSpacingFromPreset">
                                            <option value="tight">Плотный</option>
                                            <option value="normal">Обычный</option>
                                            <option value="wide">Широкий</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <!-- Междустрочный интервал -->
                                <div class="accessibility-section">
                                    <label>Междустрочный интервал:</label>
                                    <div class="select-group">
                                        <select v-model="accessibilitySettings.lineHeightPreset" @change="setLineHeightFromPreset">
                                            <option value="compact">Компактный</option>
                                            <option value="normal">Обычный</option>
                                            <option value="spacious">Просторный</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <!-- Кнопки управления -->
                                <div class="accessibility-buttons">
                                    <button class="reset-btn" @click="resetAccessibilitySettings">Сбросить настройки</button>
                                </div>
                            </div>
                        </div>
                    </li>
                </ul>
            </nav>
            
            <!-- Мобильная навигация без дропдауна -->
            <nav class="mobile-nav" :class="{ 'mobile-open': mobileMenuOpen }">
                <div class="mobile-nav-header">
                    <button class="mobile-close" @click="toggleMobileMenu">&times;</button>
                </div>
                <ul>
                    <li><router-link to="/catalog" @click="closeMobileMenu">Каталог</router-link></li>
                    <li><router-link to="/cart" @click="closeMobileMenu">Корзина</router-link></li>
                    <li><router-link to="/profile" @click="closeMobileMenu">Профиль</router-link></li>
                    <li v-if="!isAuthenticated"><router-link to="/login" @click="closeMobileMenu">Войти</router-link></li>
                    <li v-if="!isAuthenticated"><router-link to="/register" @click="closeMobileMenu">Регистрация</router-link></li>
                    <li v-if="isAuthenticated"><router-link to="/favorites" @click="closeMobileMenu">Понравившиеся товары</router-link></li>
                    <li v-if="isAuthenticated"><a href="#" @click.prevent="logoutAndCloseMenu">Выйти</a></li>
                    <li class="mobile-accessibility">
                        <a href="#" @click.prevent="toggleAccessibilityMenu">Настройки доступности</a>
                    </li>
                </ul>
            </nav>
        </div>
    </header>
</template>

<script>
import { inject, ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import defaultImageProduct from '@/assets/img/Default_product_foto.jpg';

export default {
    name: 'AppHeader',
    setup() {
        const isAuthenticated = inject('isAuthenticated');
        const logout = inject('logout');
        const router = useRouter();
        const searchQuery = ref('');
        const searchResults = ref([]);
        const showDropdown = ref(false);
        const searchTimeout = ref(null);
        const API_BASE_URL = 'http://127.0.0.1:8000';
        
        // Мобильные состояния
        const mobileMenuOpen = ref(false);
        const searchBarVisible = ref(false);

        // Настройки доступности
        const showAccessibilityMenu = ref(false);
        const accessibilitySettings = ref({
            fontSize: 16,
            fontSizePreset: 'medium',
            fontFamily: "'Arial', sans-serif",
            fontType: 'sans-serif',
            letterSpacing: 0,
            letterSpacingPreset: 'normal',
            lineHeight: 1.5,
            lineHeightPreset: 'normal'
        });

        // Загрузка настроек доступности из localStorage при монтировании
        onMounted(() => {
            document.addEventListener('click', handleClickOutside);
            
            // Загрузка сохраненных настроек
            const savedSettings = localStorage.getItem('accessibilitySettings');
            if (savedSettings) {
                const parsed = JSON.parse(savedSettings);
                // Проверяем, есть ли новые поля в сохраненных настройках
                if (!parsed.fontType || !parsed.fontSizePreset) {
                    // Если нет, определяем их на основе fontFamily
                    parsed.fontType = determineFontType(parsed.fontFamily);
                    parsed.fontSizePreset = determineFontSizePreset(parsed.fontSize);
                }
                accessibilitySettings.value = parsed;
                applyAccessibilitySettings();
            }
            
            // Добавляем слушатель для закрытия меню при изменении размера экрана
            window.addEventListener('resize', handleResize);
        });

        onUnmounted(() => {
            document.removeEventListener('click', handleClickOutside);
            window.removeEventListener('resize', handleResize);
            
            // Убираем класс с body при размонтировании
            document.body.classList.remove('menu-open');
            document.body.style.overflow = '';
        });
        
        // Обработчик изменения размера окна
        const handleResize = () => {
            if (window.innerWidth > 768) {
                closeMobileMenu();
                searchBarVisible.value = false;
            }
        };

        // Функция для переключения меню доступности
        const toggleAccessibilityMenu = () => {
            showAccessibilityMenu.value = !showAccessibilityMenu.value;
        };
        
        // Функция для переключения мобильного меню
        const toggleMobileMenu = () => {
            mobileMenuOpen.value = !mobileMenuOpen.value;
            
            // Управляем классом на body для оверлея
            if (mobileMenuOpen.value) {
                document.body.classList.add('menu-open');
                document.body.style.overflow = 'hidden'; // Блокируем прокрутку
            } else {
                document.body.classList.remove('menu-open');
                document.body.style.overflow = ''; // Возвращаем прокрутку
            }
        };
        
        // Закрытие мобильного меню
        const closeMobileMenu = () => {
            mobileMenuOpen.value = false;
            document.body.classList.remove('menu-open');
            document.body.style.overflow = '';
        };
        
        // Переключение видимости строки поиска на мобильных
        const toggleSearchBar = () => {
            searchBarVisible.value = !searchBarVisible.value;
            
            // Если открываем поиск, фокусируемся на поле ввода
            if (searchBarVisible.value) {
                setTimeout(() => {
                    const searchInput = document.querySelector('.search-bar input');
                    if (searchInput) searchInput.focus();
                }, 100);
            }
        };
        
        // Комбинированный выход и закрытие меню
        const logoutAndCloseMenu = () => {
            logout();
            closeMobileMenu();
        };

        // Определение типа шрифта на основе fontFamily
        const determineFontType = (fontFamily) => {
            if (fontFamily.includes('serif') && !fontFamily.includes('sans-serif')) {
                return 'serif';
            } else if (fontFamily.includes('monospace')) {
                return 'monospace';
            } else {
                return 'sans-serif';
            }
        };

        // Определяем пресет размера шрифта на основе числового значения
        const determineFontSizePreset = (fontSize) => {
            if (fontSize <= 14) {
                return 'small';
            } else if (fontSize <= 18) {
                return 'medium';
            } else {
                return 'large';
            }
        };

        // Обновление семейства шрифта при изменении типа
        const updateFontFamily = () => {
            // Устанавливаем дефолтное значение для каждого типа
            switch (accessibilitySettings.value.fontType) {
                case 'sans-serif':
                    accessibilitySettings.value.fontFamily = "'Arial', sans-serif";
                    break;
                case 'serif':
                    accessibilitySettings.value.fontFamily = "'Times New Roman', serif";
                    break;
                case 'monospace':
                    accessibilitySettings.value.fontFamily = "'Courier New', monospace";
                    break;
            }
            applyAccessibilitySettings();
        };

        // Установка размера шрифта на основе выбранного пресета
        const setFontSizeFromPreset = () => {
            switch (accessibilitySettings.value.fontSizePreset) {
                case 'small':
                    accessibilitySettings.value.fontSize = 14;
                    break;
                case 'medium':
                    accessibilitySettings.value.fontSize = 16;
                    break;
                case 'large':
                    accessibilitySettings.value.fontSize = 20;
                    break;
            }
            applyAccessibilitySettings();
        };
        
        // Установка интервала между буквами на основе выбранного пресета
        const setLetterSpacingFromPreset = () => {
            switch (accessibilitySettings.value.letterSpacingPreset) {
                case 'tight':
                    accessibilitySettings.value.letterSpacing = 0;
                    break;
                case 'normal':
                    accessibilitySettings.value.letterSpacing = 1;
                    break;
                case 'wide':
                    accessibilitySettings.value.letterSpacing = 3;
                    break;
            }
            applyAccessibilitySettings();
        };
        
        // Установка междустрочного интервала на основе выбранного пресета
        const setLineHeightFromPreset = () => {
            switch (accessibilitySettings.value.lineHeightPreset) {
                case 'compact':
                    accessibilitySettings.value.lineHeight = 1.2;
                    break;
                case 'normal':
                    accessibilitySettings.value.lineHeight = 1.5;
                    break;
                case 'spacious':
                    accessibilitySettings.value.lineHeight = 2;
                    break;
            }
            applyAccessibilitySettings();
        };

        // Применение настроек доступности
        const applyAccessibilitySettings = () => {
            const root = document.documentElement;
            
            // Применяем настройки к корневому элементу
            root.style.setProperty('--font-size', `${accessibilitySettings.value.fontSize}px`);
            root.style.setProperty('--font-family', accessibilitySettings.value.fontFamily);
            root.style.setProperty('--letter-spacing', `${accessibilitySettings.value.letterSpacing}px`);
            root.style.setProperty('--line-height', accessibilitySettings.value.lineHeight);
            
            // Если открыто мобильное меню, нужно добавить класс menu-open обратно
            if (mobileMenuOpen.value) {
                document.body.classList.add('menu-open');
            }
            
            // Сохраняем настройки в localStorage
            localStorage.setItem('accessibilitySettings', JSON.stringify(accessibilitySettings.value));
        };

        // Сброс настроек доступности
        const resetAccessibilitySettings = () => {
            accessibilitySettings.value = {
                fontSize: 16,
                fontSizePreset: 'medium',
                fontFamily: "'Arial', sans-serif",
                fontType: 'sans-serif',
                letterSpacing: 0,
                letterSpacingPreset: 'normal',
                lineHeight: 1.5,
                lineHeightPreset: 'normal'
            };
            applyAccessibilitySettings();
        };

        // Отслеживаем клик вне меню доступности для его закрытия
        const handleClickOutside = (event) => {
            const accessibilityContainer = document.querySelector('.accessibility-toggle');
            const searchContainer = document.querySelector('.search-container');
            
            if (accessibilityContainer && !accessibilityContainer.contains(event.target)) {
                showAccessibilityMenu.value = false;
            }
            
            if (searchContainer && !searchContainer.contains(event.target)) {
                showDropdown.value = false;
            }
        };

        // Обработчик ввода с дебаунсом
        const handleInput = async () => {
            if (searchTimeout.value) clearTimeout(searchTimeout.value);
            
            if (searchQuery.value.trim()) {
                showDropdown.value = true;
                searchTimeout.value = setTimeout(async () => {
                    try {
                        const response = await axios.get(`${API_BASE_URL}/main/products/search/advanced/`, {
                            params: { 
                                search: searchQuery.value,
                                dropdown: 'true'  // Указываем, что это запрос для выпадающего списка
                            }
                        });
                        searchResults.value = response.data.products || [];
                        showDropdown.value = searchResults.value.length > 0;
                    } catch (error) {
                        console.error('Ошибка поиска:', error);
                        searchResults.value = [];
                        showDropdown.value = false;
                    }
                }, 300);
            } else {
                searchResults.value = [];
                showDropdown.value = false;
            }
        };

        const handleSearch = () => {
            if (searchQuery.value.trim()) {
                router.push({
                    name: 'search',
                    query: { q: searchQuery.value.trim() }
                });
                showDropdown.value = false;
                searchBarVisible.value = false; // Скрываем поиск после поиска на мобильных
            }
        };

        const goToProduct = (product) => {
            router.push(`/product/${product.id}`);
            showDropdown.value = false;
            searchQuery.value = '';
            searchBarVisible.value = false; // Скрываем поиск после выбора продукта на мобильных
        };

        return {
            isAuthenticated,
            logout,
            searchQuery,
            searchResults,
            showDropdown,
            handleInput,
            handleSearch,
            goToProduct,
            defaultImageProduct,
            API_BASE_URL,
            // Доступность
            showAccessibilityMenu,
            accessibilitySettings,
            toggleAccessibilityMenu,
            applyAccessibilitySettings,
            resetAccessibilitySettings,
            setFontSizeFromPreset,
            setLetterSpacingFromPreset,
            setLineHeightFromPreset,
            updateFontFamily,
            // Мобильное меню
            mobileMenuOpen,
            searchBarVisible,
            toggleMobileMenu,
            toggleSearchBar,
            closeMobileMenu,
            logoutAndCloseMenu
        };
    },
};
</script>

<style scoped>
/* Стили для хедера */
header {
    background-color: #ffffff;
    color: #333;
    padding: 15px 0;
    border-bottom: none;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    background: rgba(255, 255, 255, 0.92);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 25px;
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
}

.logo-container {
    text-decoration: none;
    position: relative;
    overflow: hidden;
    padding: 2px 8px;
    border-radius: 8px;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.logo-container:hover {
    transform: translateY(-2px) scale(1.03);
}

.logo-container:before {
    content: '';
    position: absolute;
    left: -10px;
    top: 0;
    width: 10px;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
    animation: shimmer 3s infinite;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.logo-container:hover:before {
    opacity: 1;
}

@keyframes shimmer {
    0% { left: -10px; }
    100% { left: 100%; }
}

.logo {
    font-size: 26px;
    margin: 0;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #6b46c1 0%, #9f7aea 50%, #805ad5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 2px 4px rgba(107, 70, 193, 0.3));
    position: relative;
    display: inline-block;
    padding-right: 8px;
}

.logo:after {
    content: '';
    position: absolute;
    right: 0;
    top: 25%;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f687b3 0%, #fc8181 100%);
    box-shadow: 0 0 8px rgba(246, 135, 179, 0.6);
}

.search-bar {
    flex-grow: 1;
    margin: 0 30px;
    position: relative;
    display: flex;
    align-items: center;
}

.search-container {
    position: relative;
    flex-grow: 1;
    max-width: 500px;
    margin: 0 auto;
}

.search-bar input {
    width: 100%;
    padding: 12px 45px 12px 18px;
    border: 1px solid #e4e4e7;
    border-radius: 16px;
    font-size: 14px;
    box-sizing: border-box;
    background-color: #f9f9fb;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.search-bar input:focus {
    border-color: #8b5cf6;
    outline: none;
    box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15);
    background-color: #fff;
    transform: translateY(-1px);
}

.search-button {
    background: none;
    border: none;
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    cursor: pointer;
    padding: 8px;
    font-size: 18px;
    color: #8b5cf6;
    transition: all 0.2s ease;
}

.search-button:hover {
    transform: translateY(-50%) scale(1.1) rotate(5deg);
    color: #6b46c1;
}

.search-dropdown {
    position: absolute;
    top: 110%;
    left: 0;
    right: 0;
    background: white;
    border: none;
    border-radius: 16px;
    margin-top: 8px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    z-index: 1000;
    max-height: 400px;
    overflow-y: auto;
    padding: 10px 0;
    animation: fadeInDown 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.search-item {
    display: flex;
    padding: 14px 16px;
    cursor: pointer;
    transition: all 0.25s ease;
    border-radius: 12px;
    margin: 0 8px 4px;
    border: 1px solid transparent;
}

.search-item:hover {
    background-color: #f5f3ff;
    transform: translateX(4px) scale(1.01);
    border-color: #e9d8fd;
}

.search-item-image {
    width: 50px;
    height: 50px;
    margin-right: 16px;
    flex-shrink: 0;
    border-radius: 12px;
    overflow: hidden;
    background-color: #f5f5f7;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(0, 0, 0, 0.04);
    transform: rotate(-2deg);
    transition: transform 0.3s ease;
}

.search-item:hover .search-item-image {
    transform: rotate(0deg) scale(1.05);
}

.search-item-image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.search-item-info {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.search-item-name {
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 4px;
    font-size: var(--font-size);
}

.search-item-price {
    color: #8b5cf6;
    font-weight: 700;
    font-size: var(--font-size);
}

.search-item-category {
    color: #86868b;
    font-size: calc(var(--font-size) - 2px);
    margin-top: 4px;
}

/* Десктопная навигация */
.desktop-nav {
    position: static;
    display: flex;
    align-items: center;
}

.desktop-nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
}

.desktop-nav ul li {
    margin-left: 20px;
    position: relative;
}

.desktop-nav ul li a {
    color: #333;
    text-decoration: none;
    font-size: var(--font-size);
    padding: 8px 14px;
    display: block;
    border-radius: 12px;
    transition: all 0.3s ease;
    font-weight: 500;
    position: relative;
    overflow: hidden;
    z-index: 1;
}

.desktop-nav ul li a:before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #8b5cf6, #d8b4fe);
    transition: all 0.3s ease;
    transform: translateX(-50%);
    z-index: -1;
}

.desktop-nav ul li a:hover:before {
    width: 100%;
}

.desktop-nav ul li a:hover {
    color: #6b46c1;
    background-color: rgba(107, 70, 193, 0.05);
    transform: translateY(-2px);
}

/* Стили для выпадающего меню с плавностью при наведении */
.desktop-nav .profile-dropdown {
    position: relative;
}

.desktop-nav .profile-dropdown .dropdown-menu {
    position: absolute;
    top: 120%;
    right: 0;
    background-color: #fff;
    border: none;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
    min-width: 200px;
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px) scale(0.95);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    transform-origin: top right;
    overflow: hidden;
}

.desktop-nav .profile-dropdown .dropdown-menu ul {
    display: flex;
    flex-direction: column;
    list-style: none;
    padding: 10px 0;
    margin: 0;
}

.desktop-nav .profile-dropdown .dropdown-menu ul li {
    margin: 0;
}

.desktop-nav .profile-dropdown .dropdown-menu ul li a {
    padding: 12px 20px;
    color: #333;
    display: block;
    font-weight: 400;
    border-radius: 0;
    transition: all 0.2s ease;
}

.desktop-nav .profile-dropdown .dropdown-menu ul li a:hover {
    background-color: #f5f3ff;
    color: #6b46c1;
    padding-left: 24px;
}

.desktop-nav .profile-dropdown .dropdown-menu ul li a:before {
    display: none;
}

/* Показываем меню при наведении */
.desktop-nav .profile-dropdown:hover .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0) scale(1);
}

/* Стили для компонента доступности */
.accessibility-toggle {
    order: 0;
    position: relative;
    margin-right: 15px;
}

.accessibility-button {
    background: linear-gradient(135deg, #f5f3ff 0%, #e9d8fd 100%);
    color: #6b46c1;
    border: none;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(107, 70, 193, 0.2);
}

.accessibility-button:hover {
    transform: scale(1.1) rotate(5deg);
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.3);
}

.accessibility-icon {
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.accessibility-menu {
    width: 320px;
    position: absolute;
    top: 120%;
    right: -70px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    padding: 25px;
    margin-top: 12px;
    z-index: 1000;
    animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    transform-origin: top right;
    border: 1px solid rgba(107, 70, 193, 0.1);
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.9);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.accessibility-menu h3 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #333;
    font-size: 20px;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 15px;
    text-align: center;
    font-weight: 600;
    background: linear-gradient(135deg, #6b46c1 0%, #9f7aea 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.accessibility-section {
    margin-bottom: 22px;
}

.accessibility-section label {
    display: block;
    margin-bottom: 10px;
    font-weight: 500;
    color: #444;
    font-size: 15px;
}

.accessibility-section select {
    width: 100%;
    padding: 12px 15px;
    border-radius: 12px;
    border: 1px solid #e9d8fd;
    background-color: #f9f9fb;
    font-size: 14px;
    color: #333;
    transition: all 0.3s ease;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b46c1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 15px center;
}

.accessibility-section select:focus {
    border-color: #8b5cf6;
    outline: none;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.select-group {
    margin-bottom: 10px;
    position: relative;
}

.accessibility-buttons {
    display: flex;
    justify-content: center;
    margin-top: 25px;
}

.reset-btn {
    background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(244, 63, 94, 0.2);
}

.reset-btn:hover {
    background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(244, 63, 94, 0.3);
}

/* Мобильная кнопка меню */
.mobile-menu-toggle {
    display: none;
    background: linear-gradient(135deg, #f5f3ff 0%, #e9d8fd 100%);
    border: none;
    width: 42px;
    height: 42px;
    padding: 5px;
    cursor: pointer;
    position: relative;
    z-index: 1002;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(107, 70, 193, 0.2);
    transition: all 0.3s ease;
}

.mobile-menu-toggle:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.3);
}

.menu-icon-wrapper {
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mobile-menu-icon {
    display: block;
    width: 24px;
    height: 2px;
    background-color: #6b46c1;
    position: relative;
    transition: background-color 0.3s, transform 0.3s;
}

.mobile-menu-icon::before,
.mobile-menu-icon::after {
    content: '';
    position: absolute;
    width: 24px;
    height: 2px;
    background-color: #6b46c1;
    transition: transform 0.3s;
    left: 0;
}

.mobile-menu-icon::before {
    top: -8px;
}

.mobile-menu-icon::after {
    bottom: -8px;
}

/* Анимация иконки меню */
.mobile-menu-icon.open {
    background-color: transparent;
}

.mobile-menu-icon.open::before {
    transform: rotate(45deg) translate(5px, 5px);
}

.mobile-menu-icon.open::after {
    transform: rotate(-45deg) translate(5px, -5px);
}

/* Кнопка поиска для мобильных */
.mobile-search-toggle {
    display: none;
    background: linear-gradient(135deg, #f5f3ff 0%, #e9d8fd 100%);
    color: #6b46c1;
    border: none;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    cursor: pointer;
    font-size: 18px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(107, 70, 193, 0.2);
}

.mobile-search-toggle:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(107, 70, 193, 0.3);
}

.search-icon {
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Скрываем мобильную навигацию по умолчанию */
.mobile-nav {
    display: none;
}

/* Мобильная навигация */
.mobile-nav-header {
    display: flex;
    background: linear-gradient(135deg, #f5f3ff 0%, #e9d8fd 100%);
    padding: 20px;
    border-bottom: 1px solid #e9d8fd;
    justify-content: flex-end;
    align-items: center;
    border-radius: 20px 0 0 0;
}

.mobile-close {
    background: transparent;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #6b46c1;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.mobile-close:hover {
    background-color: rgba(107, 70, 193, 0.1);
    transform: rotate(90deg);
}

/* Стили для мобильных устройств */
@media (max-width: 768px) {
    .header-content {
        padding: 0 15px;
        height: 70px;
    }
    
    .desktop-nav {
        display: none;
    }
    
    .mobile-menu-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
        order: 3;
        margin-left: 15px;
    }
    
    .menu-icon-wrapper {
        width: 20px;
        height: 20px;
    }

    .mobile-menu-icon,
    .mobile-menu-icon::before,
    .mobile-menu-icon::after {
        height: 2px;
        width: 20px;
    }
    
    .accessibility-toggle {
        display: none;
    }
    
    .mobile-search-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
        order: 2;
        margin-left: 15px;
    }
    
    .logo-container {
        order: 1;
        flex-grow: 1;
        text-align: center;
    }
    
    /* Обновленные стили для поиска на мобильных */
    .search-bar {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 18px;
        margin: 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        display: none;
        z-index: 10;
        border-radius: 0 0 20px 20px;
    }
    
    .search-bar.mobile-visible {
        display: block;
        animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .mobile-nav {
        display: block;
        position: fixed;
        top: 0;
        right: -100%;
        width: 85%;
        max-width: 360px;
        height: 100vh;
        background: white;
        z-index: 1001;
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: -5px 0 30px rgba(0,0,0,0.15);
        overflow-y: auto;
        border-radius: 20px 0 0 20px;
    }
    
    .mobile-nav.mobile-open {
        transform: translateX(-100%);
    }
    
    .mobile-nav ul {
        flex-direction: column;
        padding: 10px 0;
        margin: 0;
    }
    
    .mobile-nav ul li {
        margin: 5px 15px;
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .mobile-nav ul li:hover {
        border-color: #e9d8fd;
        background-color: #f5f3ff;
    }
    
    .mobile-nav ul li a {
        padding: 16px 20px;
        font-size: 16px;
        display: block;
        color: #333;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .mobile-nav ul li a:hover {
        color: #6b46c1;
        transform: translateX(5px);
    }
    
    /* Обновленное меню доступности для мобильных */
    .accessibility-menu {
        width: calc(100vw - 60px);
        max-width: 320px;
        left: 15px;
        right: 15px;
        top: 70px;
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    /* Для очень маленьких экранов */
    @media (max-width: 480px) {
        .accessibility-menu {
            width: calc(100vw - 40px);
            padding: 20px;
        }
    }
    
    @keyframes slideDown {
        from { 
            opacity: 0;
            transform: translateY(-20px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Стили для пункта доступности в мобильном меню */
    .mobile-nav .mobile-accessibility a {
        display: flex;
        align-items: center;
    }
    
    .mobile-nav .mobile-accessibility a::before {
        content: '👁️';
        margin-right: 10px;
        font-size: 18px;
    }
}

/* Стили для body при открытом меню */
:global(body.menu-open) {
    overflow: hidden;
}

:global(body.menu-open::before) {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    z-index: 999;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Для очень маленьких экранов */
@media (max-width: 480px) {
    .logo {
        font-size: 24px;
    }
    
    .header-content {
        padding: 0 10px;
    }
    
    .search-dropdown {
        max-height: 300px;
    }
}

/* Стили для пункта с кнопкой доступности */
.desktop-nav .accessibility-item {
    display: flex;
    align-items: center;
}

.desktop-nav .accessibility-item .accessibility-toggle {
    margin: 0;
    position: relative;
}

.desktop-nav .accessibility-item .accessibility-button {
    margin: 0 0 0 10px;
}

/* Добавление красивых эффектов для активных элементов навигации */
.desktop-nav ul li a.router-link-active {
    color: #6b46c1;
    background-color: rgba(107, 70, 193, 0.08);
    font-weight: 600;
}

.desktop-nav ul li a.router-link-active:before {
    width: 70%;
    height: 3px;
}

/* Улучшенные эффекты при наведении для элементов хедера */
.profile-dropdown > a:hover + .dropdown-menu,
.dropdown-menu:hover {
    opacity: 1;
    visibility: visible;
    transform: translateY(0) scale(1);
}
</style>