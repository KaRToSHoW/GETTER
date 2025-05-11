<template>
  <div>
    <!-- Хедер -->
    <AppHeader />

    <!-- Основной контент -->
    <router-view></router-view>
  </div>
</template>

<style>
:root {
    /* Базовые CSS переменные для настроек доступности */
    --font-size: 16px;
    --font-family: 'Arial', sans-serif;
    --letter-spacing: 0px;
    --line-height: 1.5;
    
    /* Дефолтные цвета */
    --bg-color: #ffffff;
    --text-color: #333333;
    --link-color: #6b46c1;
    --border-color: #dddddd;
    --heading-color: #222222;
}

/* Применяем переменные к основным элементам */
body {
    font-family: var(--font-family) !important;
    font-size: var(--font-size) !important;
    letter-spacing: var(--letter-spacing) !important;
    line-height: var(--line-height) !important;
    color: var(--text-color);
    background-color: var(--bg-color);
    transition: all 0.3s ease;
}

/* Основной текст - используем !important для переопределения */
p, div, span, li, td, th, button, input, textarea, select, option {
    font-family: var(--font-family) !important;
    font-size: var(--font-size) !important;
    letter-spacing: var(--letter-spacing) !important;
    line-height: var(--line-height) !important;
}

/* Заголовки */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-family) !important;
    letter-spacing: var(--letter-spacing) !important;
    color: var(--heading-color);
}

/* Глобальные стили для улучшения читаемости интерфейса */
.accessibility-text-large {
    font-size: calc(var(--font-size) * 1.25) !important;
}

.accessibility-text-larger {
    font-size: calc(var(--font-size) * 1.5) !important;
}

/* Определяем различные размеры текста для заголовков */
h1 { font-size: calc(var(--font-size) * 2) !important; }
h2 { font-size: calc(var(--font-size) * 1.75) !important; }
h3 { font-size: calc(var(--font-size) * 1.5) !important; }
h4 { font-size: calc(var(--font-size) * 1.25) !important; }
h5 { font-size: calc(var(--font-size) * 1.1) !important; }
h6 { font-size: var(--font-size) !important; }

/* Ссылки */
a {
    color: var(--link-color);
}

/* Цветовые схемы */
/* Тёмная (чёрно-белая) схема */
body.dark {
    --bg-color: #121212;
    --text-color: #ffffff;
    --link-color: #bb86fc;
    --border-color: #333333;
    --heading-color: #e0e0e0;
}

/* Бежевая схема */
body.beige {
    --bg-color: #f5f5dc;
    --text-color: #5c4033;
    --link-color: #8b4513;
    --border-color: #d2b48c;
    --heading-color: #654321;
}

/* Голубая схема */
body.blue {
    --bg-color: #e6f2ff;
    --text-color: #00008b;
    --link-color: #0000ff;
    --border-color: #add8e6;
    --heading-color: #000080;
}
</style>

<script>
import './assets/css/reset.css';

import { provide, ref, onMounted } from 'vue';
import AppHeader from './components/AppHeader.vue';
import { useRouter } from 'vue-router'; 
import axios from 'axios';

export default {
  name: 'App',
  components: {
    AppHeader
  },
  setup() {
    const isAuthenticated = ref(false);
    const router = useRouter(); 
    const API_BASE_URL = 'http://127.0.0.1:8000';

    // Функция для проверки токена
    const checkAuthentication = () => {
      const token = localStorage.getItem('token');
      isAuthenticated.value = token !== null;
      
      // Если токен есть, настраиваем перехватчик для всех запросов
      if (token) {
        setupAxiosInterceptors();
      }
    };
    
    // Настройка перехватчиков запросов для автоматической обработки ошибок аутентификации
    const setupAxiosInterceptors = () => {
      // Добавляем перехватчик ответов
      axios.interceptors.response.use(
        (response) => {
          return response; // Возвращаем успешный ответ без изменений
        },
        async (error) => {
          // Если ошибка 401 Unauthorized
          if (error.response && error.response.status === 401) {
            // Попытка обновить токен
            try {
              await refreshToken();
              
              // Если токен успешно обновлен, повторяем исходный запрос
              const originalRequest = error.config;
              originalRequest.headers['Authorization'] = `Bearer ${localStorage.getItem('token')}`;
              return axios(originalRequest);
            } catch (refreshError) {
              // Если не удалось обновить токен, выполняем выход
              console.error('Не удалось обновить токен:', refreshError);
              logout();
              return Promise.reject(error);
            }
          }
          return Promise.reject(error);
        }
      );
    };
    
    // Функция для обновления токена
    const refreshToken = async () => {
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('Нет refresh токена');
        }
        
        const response = await axios.post(`${API_BASE_URL}/users/token/refresh/`, {
          refresh: refreshToken
        });
        
        if (response.data && response.data.access) {
          localStorage.setItem('token', response.data.access);
          return true;
        } else {
          throw new Error('Неверный формат ответа при обновлении токена');
        }
      } catch (error) {
        console.error('Ошибка обновления токена:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        isAuthenticated.value = false;
        throw error;
      }
    };

    onMounted(() => {
      checkAuthentication();
    });

    // Метод для выхода
    const logout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      isAuthenticated.value = false; 
      router.push('/login'); 
    };

    // Передаем данные для использования в дочерних компонентах
    provide('isAuthenticated', isAuthenticated);
    provide('logout', logout);
    provide('refreshToken', refreshToken);

    return {
      isAuthenticated,
      logout
    };
  }
};
</script>
