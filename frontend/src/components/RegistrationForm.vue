<template>
    <div class="register-page">
        <div class="auth-container">
            <div class="auth-banner">
                <div class="logo-container">
                    <img src="https://via.placeholder.com/80" alt="Getter Logo" class="logo-image" />
                    <h1 class="logo-text">GETTER</h1>
                </div>
                <p class="welcome-text">
                    Рады приветствовать вас в GETTER! Наш интернет-магазин —<br />
                    это место, где новейшая техника становится доступной. Найдите<br />
                    себе, что нужно для дома, офиса и развлечений, с гарантией<br />
                    качества и выгодными ценами!
                </p>
            </div>
            
            <div class="auth-form-container">
                <div class="auth-form-wrapper">
                    <h2 class="auth-title">Регистрация</h2>
                    <p class="auth-subtitle">Создайте свой аккаунт для доступа ко всем возможностям</p>
                    
                    <form @submit.prevent="handleRegistration" class="auth-form">
                        <div class="form-group">
                            <label for="username">Имя пользователя</label>
                            <div class="input-wrapper">
                                <span class="input-icon">👤</span>
                                <input 
                                    type="text" 
                                    id="username" 
                                    v-model="username" 
                                    required 
                                    placeholder="Ваше имя"
                                    class="form-input"
                                >
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="email">Почта</label>
                            <div class="input-wrapper">
                                <span class="input-icon">✉️</span>
                                <input 
                                    type="email" 
                                    id="email" 
                                    v-model="email" 
                                    required 
                                    placeholder="Ваш email"
                                    class="form-input"
                                >
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Пароль</label>
                            <div class="input-wrapper">
                                <span class="input-icon">🔒</span>
                                <input 
                                    type="password" 
                                    id="password" 
                                    v-model="password" 
                                    required 
                                    placeholder="Ваш пароль"
                                    class="form-input"
                                >
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="password2">Подтверждение пароля</label>
                            <div class="input-wrapper">
                                <span class="input-icon">🔐</span>
                                <input 
                                    type="password" 
                                    id="password2" 
                                    v-model="password2" 
                                    required 
                                    placeholder="Повторите пароль"
                                    class="form-input"
                                >
                            </div>
                        </div>
                        
                        <div class="terms-agreement">
                            <label class="checkbox-container">
                                <input type="checkbox" required>
                                <span>Я принимаю <a href="#">условия использования</a> и <a href="#">политику конфиденциальности</a></span>
                            </label>
                        </div>
                        
                        <button type="submit" class="auth-button">Зарегистрироваться</button>
                    </form>
                    
                    <div class="divider">
                        <span class="divider-text">или</span>
                    </div>
                    
                    <div class="social-auth">
                        <button class="social-button google">
                            <img src="https://via.placeholder.com/24" alt="Google" />
                            <span>Зарегистрироваться через Google</span>
                        </button>
                        <button class="social-button vk">
                            <img src="https://via.placeholder.com/24" alt="VK" />
                            <span>Зарегистрироваться через VK</span>
                        </button>
                    </div>
                    
                    <p class="auth-redirect">
                        Уже есть аккаунт? <router-link to="/login">Войдите</router-link>
                    </p>
                </div>
            </div>
        </div>
        <ToastNotification ref="toast" />
    </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import ToastNotification from './ToastNotification.vue';

const username = ref('');
const email = ref('');
const password = ref('');
const password2 = ref('');
const toast = ref(null);
const router = useRouter();
const API_BASE_URL = inject('$apiBaseUrl', 'http://127.0.0.1:8000');

const handleRegistration = async () => {
    if (password.value !== password2.value) {
        toast.value.showToast('Пароли не совпадают!', 'error');
        return;
    }

    try {
        await axios.post(`${API_BASE_URL}/auth/register/`, {
            username: username.value,
            email: email.value,
            password: password.value
        });

        toast.value.showToast('Регистрация успешна! Теперь вы можете войти.', 'success');
        router.push('/login');
    } catch (error) {
        console.error('Ошибка регистрации:', error.response ? error.response.data : error.message);
        if (error.response && error.response.data) {
            const errors = Object.values(error.response.data).flat().join(', ');
            toast.value.showToast(`Ошибка регистрации: ${errors}`, 'error');
        } else {
            toast.value.showToast('Ошибка при регистрации. Попробуйте позже.', 'error');
        }
    }
};
</script>

<style scoped>
.register-page {
    min-height: 100vh;
    background-color: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    font-family: 'Arial', sans-serif;
}

.auth-container {
    display: flex;
    max-width: 1000px;
    width: 100%;
    background-color: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.auth-banner {
    flex: 0 0 45%;
    background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
    padding: 40px;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.logo-container {
    text-align: center;
    margin-bottom: 30px;
}

.logo-image {
    width: 80px;
    height: 80px;
    background-color: white;
    border-radius: 50%;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.logo-text {
    font-size: 28px;
    font-weight: 700;
    margin: 0;
    letter-spacing: 1px;
}

.welcome-text {
    font-size: 15px;
    line-height: 1.6;
    opacity: 0.9;
}

.auth-form-container {
    flex: 0 0 55%;
    padding: 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.auth-form-wrapper {
    max-width: 400px;
    width: 100%;
    margin: 0 auto;
}

.auth-title {
    font-size: 24px;
    color: #2d3748;
    font-weight: 700;
    margin: 0 0 10px;
}

.auth-subtitle {
    font-size: 16px;
    color: #718096;
    margin: 0 0 30px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-size: 14px;
    color: #4a5568;
    margin-bottom: 8px;
    font-weight: 600;
}

.input-wrapper {
    position: relative;
}

.input-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 16px;
    color: #718096;
}

.form-input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.2s ease;
}

.form-input:focus {
    outline: none;
    border-color: #6b46c1;
    box-shadow: 0 0 0 2px rgba(107, 70, 193, 0.2);
}

.terms-agreement {
    margin-bottom: 25px;
}

.checkbox-container {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 14px;
    color: #4a5568;
    cursor: pointer;
}

.checkbox-container input {
    margin-top: 3px;
}

.checkbox-container a {
    color: #6b46c1;
    text-decoration: none;
    transition: color 0.2s;
}

.checkbox-container a:hover {
    color: #553c9a;
    text-decoration: underline;
}

.auth-button {
    width: 100%;
    padding: 12px;
    background-color: #6b46c1;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}

.auth-button:hover {
    background-color: #553c9a;
}

.divider {
    position: relative;
    text-align: center;
    margin: 25px 0;
    height: 1px;
    background-color: #e2e8f0;
}

.divider-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: white;
    padding: 0 15px;
    color: #718096;
    font-size: 14px;
}

.social-auth {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 25px;
}

.social-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: white;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.social-button:hover {
    background-color: #f7fafc;
}

.social-button.google {
    color: #ea4335;
}

.social-button.vk {
    color: #4a76a8;
}

.auth-redirect {
    text-align: center;
    font-size: 14px;
    color: #4a5568;
    margin: 0;
}

.auth-redirect a {
    color: #6b46c1;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}

.auth-redirect a:hover {
    color: #553c9a;
    text-decoration: underline;
}

/* Адаптивность */
@media (max-width: 768px) {
    .auth-container {
        flex-direction: column;
        max-width: 500px;
    }
    
    .auth-banner {
        padding: 30px;
    }
    
    .welcome-text {
        display: none;
    }
    
    .logo-container {
        margin-bottom: 0;
    }
}

@media (max-width: 480px) {
    .auth-banner {
        padding: 20px;
    }
    
    .auth-form-container {
        padding: 20px;
    }
    
    .terms-agreement {
        font-size: 12px;
    }
}
</style>