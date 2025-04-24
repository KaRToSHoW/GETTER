<template>
  <div>
    <!-- Хедер -->
    <AppHeader />

    <!-- Основной контент -->
    <router-view></router-view>
  </div>
</template>

<style>
body {
  font-family: sans-serif;
}
</style>

<script>
import './assets/css/reset.css';

import { provide, ref, onMounted } from 'vue';
import AppHeader from './components/AppHeader.vue';
import { useRouter } from 'vue-router'; 

export default {
  name: 'App',
  components: {
    AppHeader
  },
  setup() {
    const isAuthenticated = ref(false);
    const router = useRouter(); 

    const checkAuthentication = () => {
      const token = localStorage.getItem('token');
      isAuthenticated.value = token !== null;
    };

    onMounted(() => {
      checkAuthentication();
    });

    // Метод для выхода
    const logout = () => {
      localStorage.removeItem('token');
      isAuthenticated.value = false; 
      router.push('/login'); 
    };

    // Передаем данные для использования в дочерних компонентах
    provide('isAuthenticated', isAuthenticated);
    provide('logout', logout);

    return {
      isAuthenticated,
      logout
    };
  }
};
</script>
