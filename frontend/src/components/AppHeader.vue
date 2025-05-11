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
    background-color: #f0f0f0;
    color: #333;
    padding: 10px 0;
    border-bottom: 1px solid #ddd;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
}

.logo-container {
    text-decoration: none;
}

.logo {
    font-size: 24px;
    margin: 0;
    color: #6b46c1;
    font-weight: bold;
}

.search-bar {
    flex-grow: 1;
    margin: 0 20px;
    position: relative;
    display: flex;
    align-items: center;
}

.search-container {
    position: relative;
    flex-grow: 1;
}

.search-bar input {
    width: 100%;
    padding: 8px 40px 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.search-button {
    background: none;
    border: none;
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    cursor: pointer;
    padding: 4px;
    font-size: 16px;
}

.search-button:hover {
    opacity: 0.7;
}

.search-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #eaeaea;
    border-radius: 8px;
    margin-top: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    max-height: 400px;
    overflow-y: auto;
    padding: 8px 0;
}

.search-item {
    display: flex;
    padding: 12px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    border-radius: 4px;
    margin: 0 8px;
}

.search-item:hover {
    background-color: #f5f5f7;
    transform: translateX(4px);
}

.search-item-image {
    width: 48px;
    height: 48px;
    margin-right: 16px;
    flex-shrink: 0;
    border-radius: 8px;
    overflow: hidden;
    background-color: #f5f5f7;
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
    font-weight: 500;
    color: #1d1d1f;
    margin-bottom: 4px;
    font-size: var(--font-size);
}

.search-item-price {
    color: #6b46c1;
    font-weight: 600;
    font-size: var(--font-size);
}

.search-item-category {
    color: #86868b;
    font-size: calc(var(--font-size) - 2px);
    margin-top: 2px;
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
    padding: 8px 12px;
    display: block;
}

.desktop-nav ul li a:hover {
    text-decoration: underline;
    color: #6b46c1;
}

/* Стили для выпадающего меню с плавностью при наведении */
.desktop-nav .profile-dropdown {
    position: relative;
}

.desktop-nav .profile-dropdown .dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    min-width: 150px;
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: opacity 0.2s ease, transform 0.2s ease, visibility 0s linear 0.2s;
}

.desktop-nav .profile-dropdown .dropdown-menu ul {
    display: flex;
    flex-direction: column;
    list-style: none;
    padding: 5px 0;
    margin: 0;
}

.desktop-nav .profile-dropdown .dropdown-menu ul li {
    margin: 0;
}

.desktop-nav .profile-dropdown .dropdown-menu ul li a {
    padding: 8px 16px;
    color: #333;
    display: block;
}

.desktop-nav .profile-dropdown .dropdown-menu ul li a:hover {
    background-color: #f0f0f0;
    text-decoration: none;
}

/* Показываем меню при наведении */
.desktop-nav .profile-dropdown:hover .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
    transition: opacity 0.2s ease, transform 0.2s ease;
}

/* Стили для компонента доступности */
.accessibility-toggle {
    order: 0;
    position: relative;
    margin-right: 15px;
}

.accessibility-button {
    background: #f2f2f2;
    color: #555;
    border: none;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.accessibility-button:hover {
    background: #e0e0e0;
    transform: scale(1.05);
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}

.accessibility-icon {
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.accessibility-menu {
    width: 280px;
    position: absolute;
    top: 100%;
    right: -70px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 16px;
    margin-top: 8px;
    z-index: 1000;
}

.accessibility-menu h3 {
    margin-top: 0;
    margin-bottom: 16px;
    color: #333;
    font-size: 18px;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
}

.accessibility-section {
    margin-bottom: 16px;
}

.accessibility-section label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: #444;
}

.accessibility-section select {
    width: 100%;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ddd;
    background-color: #f9f9f9;
}

.select-group {
    margin-bottom: 8px;
}

.accessibility-buttons {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
}

.reset-btn {
    background-color: #f44336;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.reset-btn:hover {
    background-color: #d32f2f;
}

/* Мобильная кнопка меню */
.mobile-menu-toggle {
    display: none;
    background: transparent;
    border: none;
    width: 40px;
    height: 40px;
    padding: 5px;
    cursor: pointer;
    position: relative;
    z-index: 1002;
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
    background-color: #333;
    position: relative;
    transition: background-color 0.3s, transform 0.3s;
}

.mobile-menu-icon::before,
.mobile-menu-icon::after {
    content: '';
    position: absolute;
    width: 24px;
    height: 2px;
    background-color: #333;
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
    background: #f2f2f2;
    color: #555;
    border: none;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 18px;
    transition: all 0.2s ease;
}

.mobile-search-toggle:hover {
    background: #e0e0e0;
    transform: scale(1.05);
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
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
    background-color: #f5f5f7;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    justify-content: flex-end;
    align-items: center;
    border-radius: 12px 0 0 0;
}

.mobile-close {
    background: transparent;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #333;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.3s;
}

.mobile-close:hover {
    background-color: rgba(0,0,0,0.05);
}

/* Стили для мобильных устройств */
@media (max-width: 768px) {
    .header-content {
        padding: 0 15px;
        height: 60px;
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
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #f2f2f2;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }

    .mobile-menu-toggle:hover {
        background: #e0e0e0;
        transform: scale(1.05);
        box-shadow: 0 3px 8px rgba(0,0,0,0.15);
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
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
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
        background: #f5f5f7;
        padding: 15px;
        margin: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        display: none;
        z-index: 10;
        border-radius: 0 0 12px 12px;
    }
    
    .search-bar.mobile-visible {
        display: block;
        animation: slideDown 0.3s ease-out;
    }
    
    .mobile-nav {
        display: block;
        position: fixed;
        top: 0;
        right: -300px;
        width: 300px;
        height: 100vh;
        background: white;
        z-index: 1001;
        transition: transform 0.3s ease;
        box-shadow: -2px 0 15px rgba(0,0,0,0.15);
        overflow-y: auto;
        border-radius: 12px 0 0 12px;
    }
    
    .mobile-nav.mobile-open {
        transform: translateX(-300px);
        animation: slideSidebarIn 0.3s ease-out;
    }
    
    .mobile-nav ul {
        flex-direction: column;
        padding: 0;
        margin: 0;
    }
    
    .mobile-nav ul li {
        margin: 0;
        border-bottom: 1px solid #eee;
    }
    
    .mobile-nav ul li a {
        padding: 15px 20px;
        font-size: 16px;
        display: block;
        color: #333;
        transition: background-color 0.3s;
    }
    
    .mobile-nav ul li a:hover {
        background-color: #f5f5f7;
        text-decoration: none;
    }
    
    /* Обновленное меню доступности для мобильных */
    .accessibility-menu {
        width: 280px;
        left: -10px;
        right: auto;
        top: 50px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Для очень маленьких экранов */
    @media (max-width: 480px) {
        .accessibility-menu {
            width: 260px;
            left: -10px;
            right: auto;
        }
    }
    
    @keyframes slideDown {
        from { 
            opacity: 0;
            transform: translateY(-10px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideSidebarIn {
        from { 
            transform: translateX(0);
        }
        to { 
            transform: translateX(-300px);
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
    background: rgba(0,0,0,0.5);
    z-index: 999;
}

/* Для очень маленьких экранов */
@media (max-width: 480px) {
    .logo {
        font-size: 20px;
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
</style>