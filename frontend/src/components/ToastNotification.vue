<script setup>
import { ref, defineExpose, inject } from 'vue';

const toasts = ref([]);
let nextId = 0;
const $hawk = inject('$hawk', null); // Получаем Hawk из контекста приложения

const showToast = (message, type = 'info') => {
    try {
        const id = nextId++;
        const toast = {
            id,
            message,
            type
        };
        toasts.value.push(toast);
        
        // Отправляем в Hawk только сообщения об ошибках
        if (type === 'error' && $hawk) {
            $hawk.send(new Error(`Ошибка в приложении: ${message}`), {
                toastId: id,
                type: 'toast_error',
                component: 'ToastNotification'
            });
        }
        
        setTimeout(() => {
            const index = toasts.value.findIndex(t => t.id === id);
            if (index > -1) {
                toasts.value.splice(index, 1);
            }
        }, 3000);
    } catch (error) {
        console.error('Ошибка при отображении уведомления:', error);
        
        // Отправляем ошибку компонента в Hawk
        if ($hawk) {
            $hawk.send(error, {
                context: 'Ошибка в компоненте уведомлений', 
                message: message,
                toastType: type
            });
        }
    }
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