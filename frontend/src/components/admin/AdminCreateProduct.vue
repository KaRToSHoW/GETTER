<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content">
            <ToastNotification ref="toast" />
            <div class="modal-header">
                <h3>Создание нового товара</h3>
                <button class="close-button" @click="$emit('close')">&times;</button>
            </div>
            <form @submit.prevent="submitNewProduct" class="create-form">
                <div class="form-group">
                    <label>Название товара:</label>
                    <input 
                        v-model="newProduct.name" 
                        required 
                        class="form-input"
                        placeholder="Введите название товара"
                    />
                </div>
                <div class="form-group">
                    <label>Артикул:</label>
                    <input 
                        v-model="newProduct.sku" 
                        required 
                        class="form-input"
                        placeholder="Введите артикул товара"
                    />
                </div>
                <div class="form-group">
                    <label>Описание:</label>
                    <textarea 
                        v-model="newProduct.description" 
                        class="form-input"
                        placeholder="Введите описание товара"
                        rows="3"
                    ></textarea>
                </div>
                <div class="form-group">
                    <label>Категория:</label>
                    <select v-model="newProduct.category" required class="form-input">
                        <option value="">Выберите категорию</option>
                        <option v-for="category in categories" :key="category.id" :value="category.id">
                            {{ category.name }}
                        </option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Цена:</label>
                    <input 
                        v-model.number="newProduct.price" 
                        type="number" 
                        min="0" 
                        step="0.01" 
                        required 
                        class="form-input"
                        placeholder="0.00"
                    />
                </div>
                <div class="form-group">
                    <label>Количество на складе:</label>
                    <input 
                        v-model.number="newProduct.stock" 
                        type="number" 
                        min="0" 
                        required 
                        class="form-input"
                        placeholder="0"
                    />
                </div>
                <div class="form-group">
                    <label>Изображение товара:</label>
                    <div class="file-input-wrapper">
                        <input 
                            type="file" 
                            @change="handleProductImageUpload" 
                            accept="image/*"
                            class="file-input"
                            id="productImage"
                        />
                        <label for="productImage" class="file-input-label">
                            Выберите изображение
                        </label>
                    </div>
                    <div v-if="productImagePreview" class="image-preview">
                        <img :src="productImagePreview" alt="Preview" />
                    </div>
                </div>
                <div class="form-group">
                    <label>Характеристики:</label>
                    <button type="button" @click="addSpecification" class="add-spec-button">
                        Добавить характеристику
                    </button>
                    <div v-for="(spec, index) in specifications" :key="index" class="specification-item">
                        <input 
                            v-model="spec.key" 
                            placeholder="Название" 
                            class="form-input spec-input"
                        />
                        <input 
                            v-model="spec.value" 
                            placeholder="Значение" 
                            class="form-input spec-input"
                        />
                        <button type="button" @click="removeSpecification(index)" class="remove-spec-button">
                            &#10005;
                        </button>
                    </div>
                </div>
                <div class="form-group">
                    <label>Статус доступности:</label>
                    <select v-model="newProduct.is_available" class="form-input">
                        <option :value="true">Доступен</option>
                        <option :value="false">Недоступен</option>
                    </select>
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
import { ref, onMounted, defineEmits } from 'vue';
import axios from 'axios';
import ToastNotification from '../ToastNotification.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';
const toast = ref(null);

const categories = ref([]);
const productImagePreview = ref(null);
const specifications = ref([]);
const newProduct = ref({
    name: '',
    sku: '',
    description: '',
    price: 0,
    stock: 0,
    category: '',
    image: null,
    is_available: true,
    specifications: {}
});

onMounted(async () => {
    await loadCategories();
});

const loadCategories = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/main/categories/`);
        categories.value = response.data;
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
        toast.value?.showToast('Ошибка при загрузке категорий', 'error');
    }
};

const handleProductImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        newProduct.value.image = file;
        const reader = new FileReader();
        reader.onload = e => productImagePreview.value = e.target.result;
        reader.readAsDataURL(file);
    }
};

const addSpecification = () => {
    specifications.value.push({ key: '', value: '' });
};

const removeSpecification = (index) => {
    specifications.value.splice(index, 1);
};

const submitNewProduct = async () => {
    try {
        const token = localStorage.getItem('token');
        const formData = new FormData();

        formData.append('category_id', newProduct.value.category);
        formData.append('name', newProduct.value.name);
        formData.append('sku', newProduct.value.sku);
        formData.append('description', newProduct.value.description);
        formData.append('price', newProduct.value.price);
        formData.append('stock', newProduct.value.stock);
        formData.append('is_available', newProduct.value.is_available);

        if (newProduct.value.image) {
            formData.append('image', newProduct.value.image);
        }

        const specs = {};
        specifications.value.forEach(spec => {
            if (spec.key && spec.value) {
                specs[spec.key] = spec.value;
            }
        });
        formData.append('specifications', JSON.stringify(specs));

        await axios.post(`${API_BASE_URL}/main/products/`, formData, {
            headers: { 
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            }
        });

        toast.value?.showToast('Товар успешно создан!', 'success');
        emit('product-created');
    } catch (error) {
        console.error('Ошибка создания товара:', error);
        toast.value?.showToast('Ошибка при создании товара: ' + (error.response?.data?.detail || error.message), 'error');
    }
};

const emit = defineEmits(['close', 'product-created']);
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
    max-width: 600px;
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

textarea.form-input {
    resize: vertical;
    min-height: 100px;
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

.specification-item {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 10px;
    margin-bottom: 10px;
}

.spec-input {
    width: 100%;
}

.add-spec-button {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 10px;
    transition: background-color 0.3s;
}

.add-spec-button:hover {
    background-color: #388e3c;
}

.remove-spec-button {
    background-color: #ff4444;
    color: white;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.3s;
}

.remove-spec-button:hover {
    background-color: #cc0000;
}

.form-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
    position: sticky;
    bottom: 0;
    background: white;
    padding-top: 12px;
    border-top: 1px solid #eee;
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