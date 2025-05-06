<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content">
            <ToastNotification ref="toast" />
            <div class="modal-header">
                <h3>Создание новой категории</h3>
                <button class="close-button" @click="$emit('close')">&times;</button>
            </div>
            <form @submit.prevent="submitNewCategory" class="create-form">
                <div class="form-group">
                    <label>Название категории:</label>
                    <input 
                        v-model="categoryName" 
                        required 
                        class="form-input"
                        placeholder="Введите название категории"
                    />
                </div>
                <div class="form-group">
                    <label>Изображение категории:</label>
                    <div class="file-input-wrapper">
                        <input 
                            type="file" 
                            @change="handleImageUpload" 
                            accept="image/*"
                            class="file-input"
                            id="categoryImage"
                        />
                        <label for="categoryImage" class="file-input-label">
                            Выберите изображение
                        </label>
                    </div>
                    <div v-if="imagePreview" class="image-preview">
                        <img :src="imagePreview" alt="Preview" />
                    </div>
                </div>
                <div class="form-buttons">
                    <button type="button" @click="$emit('close')" class="cancel-button">Отмена</button>
                    <button type="submit" class="save-button">Создать</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';
import axios from 'axios';
import ToastNotification from '../ToastNotification.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';
const toast = ref(null);
const categoryName = ref('');
const categoryImage = ref(null);
const imagePreview = ref(null);

const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        categoryImage.value = file;
        const reader = new FileReader();
        reader.onload = e => imagePreview.value = e.target.result;
        reader.readAsDataURL(file);
    }
};

const submitNewCategory = async () => {
    try {
        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('name', categoryName.value);
        
        if (categoryImage.value) {
            formData.append('image', categoryImage.value);
        }

        await axios.post(`${API_BASE_URL}/main/categories/`, formData, {
            headers: { 
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            }
        });

        toast.value?.showToast('Категория успешно создана!', 'success');
        emit('category-created');
        emit('close');
    } catch (error) {
        console.error('Ошибка создания категории:', error);
        toast.value?.showToast('Ошибка при создании категории: ' + (error.response?.data?.detail || error.message), 'error');
    }
};

const emit = defineEmits(['close', 'category-created']);
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
    width: 90%;
    max-width: 500px;
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

.create-form {
    padding: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #2c3e50;
    font-weight: 500;
}

.form-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.3s;
}

.form-input:focus {
    border-color: #6b46c1;
    outline: none;
}

.file-input-wrapper {
    position: relative;
}

.file-input {
    position: absolute;
    width: 0.1px;
    height: 0.1px;
    opacity: 0;
    overflow: hidden;
    z-index: -1;
}

.file-input-label {
    display: inline-block;
    padding: 10px 20px;
    background-color: #6b46c1;
    color: white;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.file-input-label:hover {
    background-color: #553c9a;
}

.image-preview {
    margin-top: 12px;
    max-width: 200px;
    max-height: 200px;
    overflow: hidden;
    border-radius: 8px;
    border: 2px solid #eee;
}

.image-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.form-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
}

.cancel-button, .save-button {
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.cancel-button {
    background-color: #fff;
    border: 1px solid #ddd;
    color: #666;
}

.cancel-button:hover {
    background-color: #f8f9fa;
    border-color: #666;
}

.save-button {
    background-color: #6b46c1;
    border: none;
    color: white;
}

.save-button:hover {
    background-color: #553c9a;
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