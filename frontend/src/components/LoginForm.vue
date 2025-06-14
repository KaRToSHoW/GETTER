<template>
    <div class="login-page">
        <ToastNotification ref="toast" />
        <div class="auth-container">
            <div class="auth-banner">
                <div class="logo-container">
                <img src="https://via.placeholder.com/80" alt="Getter Logo" class="logo-image" />
                <h1 class="logo-text">GETTER</h1>
                </div>
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
            
            <div class="auth-form-container">
                <div class="auth-form-wrapper">
                    <h2 class="auth-title">Вход в аккаунт</h2>
                    <p class="auth-subtitle">Введите свои данные для входа</p>
                    
                    <form @submit.prevent="handleLogin" class="auth-form">
                        <div class="form-group">
                            <label for="username">Почта</label>
                            <div class="input-wrapper">
                                <span class="input-icon">✉️</span>
                                <input 
                                    type="text" 
                                    id="username" 
                                    v-model="username" 
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
                        
                        <div class="auth-options">
                            <label class="remember-me">
                                <input type="checkbox"> Запомнить меня
                            </label>
                            <a href="#" class="forgot-password">Забыли пароль?</a>
                </div>
                        
                        <button type="submit" class="auth-button">Войти</button>
            </form>
                    
                    <div class="divider">
                        <span class="divider-text">или</span>
                    </div>
                    
                    <div class="social-auth">
                        <button class="social-button google">
                            <img src="https://via.placeholder.com/24" alt="Google" />
                            <span>Войти через Google</span>
                        </button>
                        <button class="social-button vk">
                            <img src="https://via.placeholder.com/24" alt="VK" />
                            <span>Войти через VK</span>
                        </button>
                    </div>
                    
                    <p class="auth-redirect">
                        Нет аккаунта? <router-link to="/register">Зарегистрируйтесь</router-link>
                    </p>
                    
                    <!-- Кнопка для тестирования Hawk -->
                    <div v-if="isDevelopment" class="hawk-test-container">
                        <button @click.prevent="sendTestErrorToHawk" class="hawk-test-button">
                            Тест Hawk Error
                        </button>
                        <small>Только для разработки</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import ToastNotification from './ToastNotification.vue';

const username = ref('');
const password = ref('');
const isAuthenticated = inject('isAuthenticated');
const router = useRouter();
const toast = ref(null);
const $hawk = inject('$hawk', null); // Получаем экземпляр Hawk из глобальных свойств
const isDevelopment = ref(process.env.NODE_ENV === 'development'); // Определяем, находимся ли в режиме разработки

const handleLogin = async () => {
    try {
        const response = await axios.post('http://127.0.0.1:8000/users/api/token/', {
            username: username.value,
            password: password.value
        });
        
        // Проверяем наличие токенов в ответе
        if (response.data.access && response.data.refresh) {
            // Сохраняем токены
        localStorage.setItem('token', response.data.access);
            localStorage.setItem('refreshToken', response.data.refresh); // Используем единый формат имен
        localStorage.setItem('username', username.value);
            
            // Устанавливаем заголовок по умолчанию для всех будущих запросов
            axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
            
            // Обновляем состояние авторизации
            isAuthenticated.value = true;
            
            // Показываем сообщение об успехе
        toast.value.showToast('Успешный вход в систему!', 'success');
            
            // Перенаправление на профиль
            router.push('/profile');
        } else {
            throw new Error('Сервер не вернул необходимые токены');
        }
    } catch (error) {
        console.error('Ошибка входа:', error);
        
        // Отправляем информацию об ошибке в Hawk
        if ($hawk) {
            $hawk.send(error, {
                username: username.value,
                errorContext: 'Ошибка авторизации',
                location: 'LoginForm.vue',
                date: new Date().toISOString()
            });
        }
        
        let errorMessage = 'Ошибка входа: ';
        
        // Обрабатываем разные типы ошибок
        if (error.response) {
            // Сервер ответил со статусом, отличным от 2xx
            if (error.response.status === 401) {
                errorMessage += 'Неверное имя пользователя или пароль';
            } else if (error.response.data && error.response.data.detail) {
                errorMessage += error.response.data.detail;
            } else {
                errorMessage += `Ошибка сервера (${error.response.status})`;
            }
        } else if (error.request) {
            // Запрос был сделан, но ответ не получен
            errorMessage += 'Сервер недоступен, проверьте подключение к интернету';
        } else {
            // Ошибка при настройке запроса
            errorMessage += error.message || 'Неизвестная ошибка';
        }
        
        toast.value.showToast(errorMessage, 'error');
    }
};

// Функция для тестирования отправки ошибок в Hawk
const sendTestErrorToHawk = () => {
    if ($hawk) {
        // Создаем информативную тестовую ошибку
        const testError = new Error('Тестовая ошибка из LoginForm');
        testError.name = 'HawkTestError';
        
        const testContext = {
            type: 'manual_test',
            message: 'Тестовая ошибка для проверки работы Hawk',
            component: 'LoginForm',
            browser: navigator.userAgent,
            timestamp: new Date().toISOString(),
            custom_data: {
                resolution: `${window.innerWidth}x${window.innerHeight}`,
                platform: navigator.platform
            }
        };
        
        // Отправка события в Hawk
        $hawk.send(testError, testContext);
        
        // Подтверждение для пользователя
        console.log('[Hawk Test] ✅ Тестовая ошибка отправлена', testContext);
        toast.value.showToast('Ошибка успешно отправлена в Hawk', 'success');
        
        // Показываем сообщение о предупреждениях в консоли
        if (process.env.NODE_ENV === 'development') {
            setTimeout(() => {
                toast.value.showToast('Предупреждения в консоли - это нормально в режиме разработки', 'info');
            }, 2000);
        }
    } else {
        console.warn('[Hawk Test] ❌ Hawk не инициализирован');
        toast.value.showToast('Hawk не инициализирован, проверьте консоль', 'warning');
    }
};
</script>

<style scoped>
.login-page {
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

.auth-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    font-size: 14px;
}

.remember-me {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    color: #4a5568;
}

.forgot-password {
    color: #6b46c1;
    text-decoration: none;
    transition: color 0.2s;
}

.forgot-password:hover {
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

/* Стили для кнопки тестирования Hawk */
.hawk-test-container {
    margin-top: 20px;
    text-align: center;
    padding: 10px;
    border-top: 1px dashed #e2e8f0;
}

.hawk-test-button {
    background-color: #f97316;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 5px;
}

.hawk-test-button:hover {
    background-color: #ea580c;
    transform: translateY(-1px);
}

.hawk-test-container small {
    display: block;
    color: #94a3b8;
    font-size: 12px;
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
    
    .auth-options {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
}
</style>