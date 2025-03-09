<script setup>
import { ref, defineExpose } from 'vue';

const toasts = ref([]);
let nextId = 0;

const showToast = (message, type = 'info') => {
    const id = nextId++;
    const toast = {
        id,
        message,
        type
    };
    toasts.value.push(toast);
    setTimeout(() => {
        const index = toasts.value.findIndex(t => t.id === id);
        if (index > -1) {
            toasts.value.splice(index, 1);
        }
    }, 3000);
};

defineExpose({ showToast });
</script>

<template>
    <div class="toast-container">
        <transition-group name="toast">
            <div v-for="toast in toasts" :key="toast.id" 
                 :class="['toast', `toast-${toast.type}`]">
                {{ toast.message }}
            </div>
        </transition-group>
    </div>
</template>

<style scoped>
.toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.toast {
    padding: 15px 25px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    min-width: 200px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast-success {
    background-color: #10B981;
}

.toast-error {
    background-color: #EF4444;
}

.toast-info {
    background-color: #3B82F6;
}

.toast-warning {
    background-color: #F59E0B;
}

/* Анимации */
.toast-enter-active,
.toast-leave-active {
    transition: all 0.3s ease;
}

.toast-enter-from {
    transform: translateX(100%);
    opacity: 0;
}

.toast-leave-to {
    transform: translateX(100%);
    opacity: 0;
}
</style> 