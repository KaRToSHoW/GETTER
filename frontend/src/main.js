// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import '@fortawesome/fontawesome-free/css/all.css';

// Импорт стилей Swiper
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/navigation';

const app = createApp(App);
app.config.globalProperties.$apiBaseUrl = 'http://127.0.0.1:8000'; // Убедитесь, что совпадает с вашим бэкэндом
app.use(router).mount('#app');