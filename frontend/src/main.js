// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import '@fortawesome/fontawesome-free/css/all.css';
import HawkCatcher from '@hawk.so/javascript';

// Импорт стилей Swiper
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/navigation';

const app = createApp(App);
app.config.globalProperties.$apiBaseUrl = 'http://127.0.0.1:8000'; 

// Определяем окружение
const isDevMode = process.env.NODE_ENV === 'development';

// Инициализация Hawk 
const hawk = new HawkCatcher({
  token: 'eyJpbnRlZ3JhdGlvbklkIjoiN2QyYWFkNWMtYmEzMi00NWZhLWEzNzEtNzJlMjQwNDJjNWI0Iiwic2VjcmV0IjoiMWZjYTY1MzktOWVlZi00MTY4LWI3YmItMWZlYmYyOWFlOWVjIn0=',
  release: process.env.VUE_APP_VERSION || '1.0.0',
  vue: app,
  context: {
    environment: process.env.NODE_ENV
  },
  disableSourceMapsParsing: isDevMode,
  maxRequestSize: 2048 * 1024, 
  beforeSend(event) {
    if (event.user && event.user.email) {
      delete event.user.email;
    }
    
    // В режиме разработки добавляем пометку к сообщениям
    if (isDevMode) {
      event.context = event.context || {};
      event.context.devMode = true;
      
      // Только для консоли
      console.log('[Hawk Dev] Отправка ошибки в Hawk:', event.message);
    }
    
    return event;
  }
});

// Добавляем Hawk в глобальные свойства для доступа из компонентов
app.config.globalProperties.$hawk = hawk;

// Предоставляем Hawk через provide для внедрения в setup компоненты
app.provide('$hawk', hawk);

app.use(router).mount('#app');