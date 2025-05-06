<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content user-management-modal">
            <ToastNotification ref="toast" />
            <div class="modal-header">
                <h3>Управление пользователями</h3>
                <button class="close-button" @click="$emit('close')">&times;</button>
            </div>
            <div class="users-container">
                <div v-for="user in users" :key="user.id" class="user-card" @click="$emit('user-selected', user)">
                    <div class="user-info">
                        <div class="user-avatar-wrapper">
                            <img :src="user.profile_image ? `${user.profile_image}` : defaultImage" 
                                :alt="user.username" 
                                class="user-avatar"/>
                        </div>
                        <div class="user-details">
                            <h4 class="user-username">{{ user.username }}</h4>
                            <p class="user-email">
                                <i class="fas fa-envelope"></i>
                                {{ user.email }}
                            </p>
                            <p class="user-name" v-if="user.first_name || user.last_name">
                                <i class="fas fa-user"></i>
                                {{ user.first_name }} {{ user.last_name }}
                            </p>
                            <div class="user-role">
                                <span class="role-badge" :class="{ 'admin': user.is_superuser }">
                                    {{ user.is_superuser ? 'Администратор' : 'Пользователь' }}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="user-actions">
                        <button 
                            @click.stop="toggleAdminStatus(user)"
                            :class="['admin-toggle', user.is_superuser ? 'remove' : 'add']"
                            :disabled="user.id === currentUser?.id"
                        >
                            <i :class="user.is_superuser ? 'fas fa-user-minus' : 'fas fa-user-shield'"></i>
                            {{ user.is_superuser ? 'Убрать права админа' : 'Сделать админом' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, defineEmits } from 'vue';
import axios from 'axios';
import ToastNotification from '../ToastNotification.vue';
import defaultImage from '@/assets/img/Default_product_foto.jpg';

const API_BASE_URL = 'http://127.0.0.1:8000';
const toast = ref(null);

const users = ref([]);
const currentUser = ref(null);

onMounted(async () => {
    await loadCurrentUser();
    await loadUsers();
});

const loadCurrentUser = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get(`${API_BASE_URL}/users/profile/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            currentUser.value = response.data;
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля пользователя:', error);
        toast.value?.showToast('Ошибка при загрузке профиля', 'error');
    }
};

const loadUsers = async () => {
    try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/users/api/users/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        users.value = response.data;
    } catch (error) {
        console.error('Ошибка загрузки пользователей:', error);
        toast.value?.showToast('Ошибка при загрузке списка пользователей', 'error');
    }
};

const toggleAdminStatus = async (user) => {
    if (user.id === currentUser.value?.id) {
        toast.value?.showToast('Вы не можете изменить свои права администратора', 'error');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        await axios.put(
            `${API_BASE_URL}/users/api/users/${user.id}/`,
            { ...user, is_superuser: !user.is_superuser },
            { headers: { Authorization: `Bearer ${token}` } }
        );
        await loadUsers();
        toast.value?.showToast(
            `${user.username} ${!user.is_superuser ? 'назначен администратором' : 'больше не администратор'}`,
            'success'
        );
    } catch (error) {
        console.error('Ошибка изменения прав администратора:', error);
        toast.value?.showToast(error.response?.data?.error || 'Ошибка изменения прав администратора', 'error');
    }
};

defineEmits(['close', 'user-selected']);
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 12px;
    padding: 0;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    animation: modalAppear 0.3s ease-out;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #eee;
    background-color: #f8f9fa;
    border-radius: 12px 12px 0 0;
    position: sticky;
    top: 0;
    z-index: 1;
}

.modal-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.5rem;
}

.close-button {
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.3s;
}

.close-button:hover {
    background-color: #eee;
}

.users-container {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.user-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
}

.user-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.user-info {
    display: flex;
    align-items: center;
    gap: 20px;
    flex: 1;
}

.user-avatar-wrapper {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    overflow: hidden;
    border: 3px solid #6b46c1;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.user-avatar-wrapper:hover .user-avatar {
    transform: scale(1.1);
}

.user-details {
    flex: 1;
}

.user-username {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 1.25rem;
    font-weight: 600;
}

.user-email, .user-name {
    margin: 4px 0;
    color: #666;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.user-email i, .user-name i {
    color: #6b46c1;
    font-size: 0.8rem;
}

.user-role {
    margin-top: 8px;
}

.role-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    background: #e2e8f0;
    color: #4a5568;
}

.role-badge.admin {
    background: #6b46c1;
    color: white;
}

.user-actions {
    display: flex;
    gap: 12px;
}

.admin-toggle {
    padding: 8px 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
}

.admin-toggle.add {
    background: #6b46c1;
    color: white;
}

.admin-toggle.remove {
    background: #e53e3e;
    color: white;
}

.admin-toggle:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.admin-toggle i {
    font-size: 0.9rem;
}

.admin-toggle:not(:disabled):hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.admin-toggle.add:not(:disabled):hover {
    background: #553c9a;
}

.admin-toggle.remove:not(:disabled):hover {
    background: #c53030;
}

@keyframes modalAppear {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>