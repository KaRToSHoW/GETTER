<template>
    <div class="under-construction">
        <div class="construction-content">
            <h1>Страница в разработке</h1>
            <p>Мы работаем над созданием этой страницы. Скоро она будет доступна.</p>
            <router-link to="/" class="back-button">Вернуться на главную</router-link>
        </div>
    </div>
</template>

<script setup>
// Пустой setup, так как компонент простой
</script>

<style scoped>
.under-construction {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
    padding: 40px 20px;
}
.construction-content {
    text-align: center;
    max-width: 600px;
}
h1 {
    font-size: 2.5rem;
    margin-bottom: 20px;
    color: #6b46c1;
}
p {
    font-size: 1.2rem;
    margin-bottom: 30px;
    color: #4a5568;
}
.back-button {
    display: inline-block;
    background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
}
.back-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(107, 70, 193, 0.4);
}
</style> 