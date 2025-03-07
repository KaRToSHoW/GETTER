<template>
    <div class="login-container">
        <div class="login-left">
            <div class="login-logo">
                <img src="https://via.placeholder.com/80" alt="Getter Logo" class="logo-image" />
                <h1 class="logo-text">GETTER</h1>
                <p class="welcome-text">
                    С возвращением в GETTER!<br />
                    Рады видеть вас снова.<br />
                    Мы подготовили для вас еще больше интересных предложений<br />
                    и новинок из мира техники!<br />
                    Откройте для себя новые возможности вместе с нами.<br />
                    Ваше удобство - наш приоритет.<br />
                    Доверьтесь профессионалам в мире электроники!
                </p>
            </div>
        </div>
        <div class="divider"></div>
        <div class="login-right">
            <h3 class="login-title">Вход в аккаунт</h3>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label for="username">Почта:</label>
                    <input type="text" id="username" v-model="username" required placeholder="Ваш email">
                </div>
                <div class="form-group">
                    <label for="password">Пароль:</label>
                    <input type="password" id="password" v-model="password" required placeholder="Ваш пароль">
                </div>
                <button type="submit" class="login-button">Войти</button>
            </form>
            <div class="social-login">
                <p>Или зарегистрироваться</p>
                <div class="social-icons">
                    <a href="#" class="social-icon google"><img src="https://via.placeholder.com/24" alt="Google" /></a>
                    <a href="#" class="social-icon vk"><img src="https://via.placeholder.com/24" alt="VK" /></a>
                </div>
            </div>
            <p class="register-link">Нет аккаунта? <router-link to="/register">Зарегистрируйтесь</router-link>.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const isAuthenticated = inject('isAuthenticated');
const router = useRouter();

const handleLogin = async () => {
    try {
        const response = await axios.post('http://127.0.0.1:8000/users/api/token/', {
            username: username.value,
            password: password.value
        });
        localStorage.setItem('token', response.data.access);
        isAuthenticated.value = true; // Обновляем состояние авторизации
        alert('Успешный вход!');
        router.push('/profile'); // Перенаправление на профиль
    } catch (error) {
        console.error('Ошибка при входе:', error);
        alert('Неверные данные для входа');
    }
};
</script>

<style scoped>
.login-container {
    display: flex;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    height: 400px; /* Фиксированная высота для симметрии */
}

.login-left {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    text-align: center;
}

.login-logo {
    margin-bottom: 20px;
}

.logo-image {
    width: 80px;
    height: 80px;
    background: linear-gradient(45deg, #6b46c1, #d53f8c);
    border-radius: 50%;
    padding: 10px;
    display: inline-block;
}

.logo-text {
    font-size: 24px;
    color: #6b46c1;
    margin: 10px 0 0;
    font-weight: bold;
}

.divider {
    width: 1px;
    background-color: #ddd;
    margin: 20px 0;
}

.login-right {
    flex: 2;
    padding: 20px;
    text-align: center;
}

.login-title {
    font-size: 24px;
    color: #6b46c1;
    margin: 10px 0;
}

.welcome-text {
    font-size: 14px;
    color: #666;
    line-height: 1.5;
    margin-bottom: 20px;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.form-group {
    text-align: left;
}

.form-group label {
    display: block;
    font-size: 14px;
    color: #333;
    margin-bottom: 5px;
}

.form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.login-button {
    background-color: #007bff;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
}

.login-button:hover {
    background-color: #0056b3;
}

.social-login {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.social-login p {
    font-size: 14px;
    color: #666;
    margin: 0;
}

.social-icons {
    display: flex;
    gap: 10px;
}

.social-icon {
    display: inline-block;
}

.social-icon img {
    width: 24px;
    height: 24px;
}

.register-link {
    font-size: 14px;
    color: #666;
    margin-top: 20px;
}

.register-link a {
    color: #6b46c1;
    text-decoration: none;
}

.register-link a:hover {
    text-decoration: underline;
}
</style>