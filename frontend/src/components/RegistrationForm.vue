<template>
    <div class="register-container">
        <div class="register-left">
            <div class="register-logo">
                <img src="https://via.placeholder.com/80" alt="Getter Logo" class="logo-image" />
                <h1 class="logo-text">GETTER</h1>
                <p class="welcome-text">
                Рады приветствовать вас в GETTER! Наш интернет-магазин —<br />
                это место, где новейшая техника становится доступной. Найдите<br />
                себе, что нужно для дома, офиса и развлечений, с гарантией<br />
                качества и выгодными ценами!
            </p>
            </div>
        </div>
        <div class="divider"></div>
        <div class="register-right">
            <h3 class="register-title">Регистрация</h3>
            <form @submit.prevent="handleRegistration" class="register-form">
                <div class="form-group">
                    <label for="username">Имя пользователя:</label>
                    <input type="text" id="username" v-model="username" required placeholder="Ваше имя">
                </div>
                <div class="form-group">
                    <label for="email">Почта:</label>
                    <input type="email" id="email" v-model="email" required placeholder="Ваш email">
                </div>
                <div class="form-group">
                    <label for="password">Пароль:</label>
                    <input type="password" id="password" v-model="password" required placeholder="Ваш пароль">
                </div>
                <div class="form-group">
                    <label for="password2">Пароль:</label>
                    <input type="password" id="password2" v-model="password2" required placeholder="Повторите пароль">
                </div>
                <button type="submit" class="register-button">Зарегистрироваться</button>
            </form>
            <div class="social-login">
                <p>Или войти</p>
                <div class="social-icons">
                    <a href="#" class="social-icon google"><img src="https://via.placeholder.com/24" alt="Google" /></a>
                    <a href="#" class="social-icon vk"><img src="https://via.placeholder.com/24" alt="VK" /></a>
                </div>
            </div>
            <p class="login-link">Уже есть аккаунт? <router-link to="/login">Войдите</router-link>.</p>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const username = ref('');
const email = ref('');
const password = ref('');
const password2 = ref('');

const handleRegistration = async () => {
    if (password.value !== password2.value) {
        alert('Пароли не совпадают!');
        return;
    }

    try {
        const response = await axios.post('http://127.0.0.1:8000/users/api/register/', {
            username: username.value,
            email: email.value,
            password: password.value,
        });
        alert(`Регистрация успешна! Код ответа: ${response.status}`);
    } catch (error) {
        console.error('Ошибка при регистрации:', error);
        alert('Ошибка регистрации');
    }
};
</script>

<style scoped>
.register-container {
    display: flex;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    height: 500px; /* Увеличена высота для размещения всех полей */
}

.register-left {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    text-align: center;
}

.register-logo {
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

.register-right {
    flex: 2;
    padding: 20px;
    text-align: center;
}

.register-title {
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

.register-form {
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

.register-button {
    background-color: #007bff;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
}

.register-button:hover {
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

.login-link {
    font-size: 14px;
    color: #666;
    margin-top: 20px;
}

.login-link a {
    color: #6b46c1;
    text-decoration: none;
}

.login-link a:hover {
    text-decoration: underline;
}
</style>