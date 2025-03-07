<template>
  <div>
    <!-- Хедер -->
    <AppHeader />

    <!-- Основной контент -->
    <router-view></router-view>
  </div>
</template>

<script>
import './assets/css/reset.css';

import { provide, ref, onMounted } from 'vue';
import AppHeader from './components/AppHeader.vue';
import { useRouter } from 'vue-router'; // Импортируйте useRouter

export default {
  name: 'App',
  components: {
    AppHeader
  },
  setup() {
    const isAuthenticated = ref(false);
    const router = useRouter(); // Получаем доступ к router

    const checkAuthentication = () => {
      const token = localStorage.getItem('token');
      isAuthenticated.value = token !== null;
    };

    // Проверка состояния авторизации при монтировании компонента
    onMounted(() => {
      checkAuthentication();
    });

    // Метод для выхода
    const logout = () => {
      localStorage.removeItem('token');
      isAuthenticated.value = false; // Обновляем состояние авторизации
      router.push('/login'); // Перенаправляем на страницу входа
    };

    // Передаем данные для использования в дочерних компонентах
    provide('isAuthenticated', isAuthenticated);
    provide('logout', logout);  // Передаем метод для выхода

    return {
      isAuthenticated,
      logout
    };
  }
};
</script>
