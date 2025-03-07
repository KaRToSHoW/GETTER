<template>
    <header>
        <div class="header-content">
            
            <router-link to="/home"><h1 class="logo">GETTER</h1></router-link>
            <div class="search-bar">
                <input type="text" placeholder="Поиск" />
            </div>
            <nav>
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
                                <li v-if="isAuthenticated"><a href="#" @click.prevent="logout">Выйти</a></li>
                            </ul>
                        </div>
                    </li>
                </ul>
            </nav>
        </div>
    </header>
</template>

<script>
import { inject } from 'vue';

export default {
    name: 'AppHeader',
    setup() {
        const isAuthenticated = inject('isAuthenticated');
        const logout = inject('logout'); // Убеждаемся, что метод logout инжектируется

        return {
            isAuthenticated,
            logout,
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
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    max-width: 1200px;
    margin: 0 auto;
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
}

.search-bar input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
}

nav ul li {
    margin-left: 20px;
    position: relative;
}

nav ul li a {
    color: #333;
    text-decoration: none;
    font-size: 14px;
    padding: 8px 12px;
    display: block;
}

nav ul li a:hover {
    text-decoration: underline;
    color: #6b46c1;
}

/* Стили для выпадающего меню с плавностью при наведении */
.profile-dropdown {
    position: relative;
}

.profile-dropdown .dropdown-menu {
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

.profile-dropdown .dropdown-menu ul {
    list-style: none;
    padding: 5px 0;
    margin: 0;
}

.profile-dropdown .dropdown-menu ul li {
    margin: 0;
}

.profile-dropdown .dropdown-menu ul li a {
    padding: 8px 16px;
    color: #333;
    display: block;
}

.profile-dropdown .dropdown-menu ul li a:hover {
    background-color: #f0f0f0;
    text-decoration: none;
}

/* Показываем меню при наведении */
.profile-dropdown:hover .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
    transition: opacity 0.2s ease, transform 0.2s ease;
}
</style>