<template>
    <div class="profile-container">
        <div class="profile-left">
            <div class="profile-logo">
                <img src="https://via.placeholder.com/80" alt="Getter Logo" class="logo-image" />
                <h1 class="logo-text">GETTER</h1>
            </div>
        </div>
        <div class="divider"></div>
        <div class="profile-right">
            <h3 class="profile-title">Профиль пользователя</h3>
            <div v-if="user" class="profile-content">
                <div v-if="!isEditing" class="profile-view">
                    <div class="profile-image-section">
                        <img 
                            :src="user.profile_image ? `${$apiBaseUrl}${user.profile_image}` : defaultImage" 
                            alt="Profile Image" 
                            class="profile-image" 
                        />
                    </div>
                    <div class="profile-info">
                        <p><strong>Имя:</strong> {{ user.first_name }} {{ user.last_name }}</p>
                        <p><strong>Имя пользователя:</strong> {{ user.username }}</p>
                        <p><strong>Электронная почта:</strong> {{ user.email }}</p>
                    </div>
                    <div class="button-group">
                        <button @click="startEditing" class="edit-button">Редактировать</button>
                        <button @click="goToFavorites" class="favorites-button">Понравившиеся товары</button>
                        <button @click="logout" class="logout-button">Выйти</button>
                    </div>
                </div>
                <form v-else @submit.prevent="updateProfile" class="profile-form">
                    <div class="profile-image-section">
                        <img 
                            :src="user.profile_image ? `${$apiBaseUrl}${user.profile_image}` : defaultImage" 
                            alt="Profile Image" 
                            class="profile-image" 
                        />
                        <input type="file" @change="uploadImage" accept="image/*" class="file-input" />
                        <button type="button" @click="removeImage" v-if="user.profile_image" class="remove-button">Удалить изображение</button>
                    </div>
                    <div class="profile-info">
                        <div class="form-group">
                            <label for="first_name">Имя:</label>
                            <input type="text" id="first_name" v-model="user.first_name" required>
                        </div>
                        <div class="form-group">
                            <label for="last_name">Фамилия:</label>
                            <input type="text" id="last_name" v-model="user.last_name" required>
                        </div>
                        <div class="form-group">
                            <label for="username">Имя пользователя:</label>
                            <input type="text" id="username" v-model="user.username" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Электронная почта:</label>
                            <input type="email" id="email" v-model="user.email" required>
                        </div>
                        <button type="submit" class="save-button">Сохранить изменения</button>
                        <button type="button" @click="cancelEditing" class="cancel-button">Отмена</button>
                    </div>
                </form>
            </div>
            <div v-else class="profile-content">
                <p>Может сначала войдете?</p>
                <button @click="goToLogin" class="login-button">Войти</button>
                <button @click="goToRegister" class="register-button">Зарегистрироваться</button>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { inject } from 'vue';
import defaultImage from '@/assets/img/default_profile_image.png';

const user = ref(null);
const isEditing = ref(false);
const router = useRouter();
const logout = inject('logout');

onMounted(async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get('http://127.0.0.1:8000/users/profile/', {
                headers: { Authorization: `Bearer ${token}` }
            });
            user.value = response.data;
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
    }
});

const goToLogin = () => router.push('/login');
const goToRegister = () => router.push('/register');
const goToFavorites = () => router.push('/favorites');

const startEditing = () => {
    isEditing.value = true;
};

const cancelEditing = () => {
    isEditing.value = false;
    loadUserProfile();
};

const loadUserProfile = async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const response = await axios.get('http://127.0.0.1:8000/users/profile/', {
                headers: { Authorization: `Bearer ${token}` }
            });
            user.value = response.data;
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
    }
};

const updateProfile = async () => {
    try {
        const token = localStorage.getItem('token');
        const response = await axios.put('http://127.0.0.1:8000/users/profile/', {
            first_name: user.value.first_name,
            last_name: user.value.last_name,
            username: user.value.username,
            email: user.value.email,
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        user.value = response.data;
        isEditing.value = false;
        alert('Профиль успешно обновлен!');
    } catch (error) {
        console.error('Ошибка обновления профиля:', error);
        alert('Ошибка при обновлении профиля');
    }
};

const uploadImage = async (event) => {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('profile_image', file);

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('http://127.0.0.1:8000/users/profile/image/', formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            user.value.profile_image = response.data.profile_image;
            alert('Изображение успешно загружено!');
        } catch (error) {
            console.error('Ошибка загрузки изображения:', error);
            alert('Ошибка при загрузке изображения');
        }
    }
};

const removeImage = async () => {
    try {
        const token = localStorage.getItem('token');
        await axios.delete('http://127.0.0.1:8000/users/profile/image/remove/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        user.value.profile_image = null; // Удаляем локально
        alert('Изображение успешно удалено!');
    } catch (error) {
        console.error('Ошибка удаления изображения:', error);
        alert('Ошибка при удалении изображения');
    }
};
</script>

<style scoped>
.profile-container {
    display: flex;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    height: 600px;
}

.profile-left {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    text-align: center;
}

.profile-logo {
    margin-bottom: 20px;
}

.logo-image {
    width: 80px;
    height: 80px;
    background: linear-gradient(45deg, #6b46c1, #d53f8c);
    border-radius: 50%;
    padding: 10px;
    display: inline-block;
}

.logo-text {
    font-size: 24px;
    color: #6b46c1;
    margin: 10px 0 0;
    font-weight: bold;
}

.divider {
    width: 1px;
    background-color: #ddd;
    margin: 20px 0;
}

.profile-right {
    flex: 2;
    padding: 20px;
    text-align: center;
}

.profile-title {
    font-size: 24px;
    color: #6b46c1;
    margin: 10px 0;
}

.profile-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}

.profile-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}

.profile-image-section {
    text-align: center;
}

.profile-image {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 10px;
}

.file-input {
    margin-top: 10px;
    padding: 5px;
}

.no-image-text {
    font-size: 14px;
    color: #666;
    margin-top: 10px;
}

.profile-info {
    text-align: left;
    width: 100%;
}

.profile-info p {
    font-size: 16px;
    color: #333;
    margin: 5px 0;
}

.button-group {
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: 10px;
}

.profile-form {
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: 15px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    font-size: 14px;
    color: #333;
    margin-bottom: 5px;
}

.form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.edit-button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
}

.edit-button:hover {
    background-color: #0056b3;
}

.favorites-button {
    background-color: #f0ad4e;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
}

.favorites-button:hover {
    background-color: #ec971f;
}

.save-button {
    background-color: #28a745;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
}

.save-button:hover {
    background-color: #218838;
}

.cancel-button {
    background-color: #dc3545;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
    margin-top: 10px;
}

.cancel-button:hover {
    background-color: #c82333;
}

.logout-button {
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
}

.logout-button:hover {
    background-color: #c82333;
}

.login-button, .register-button {
    padding: 10px 20px;
    margin-top: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
}

.login-button:hover, .register-button:hover {
    background-color: #0056b3;
}

.remove-button {
    background-color: #dc3545;
    color: white;
    padding: 5px 10px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    margin-top: 10px;
}

.remove-button:hover {
    background-color: #c82333;
}
</style>