<template>
    <div class="admin-dashboard">
        <ToastNotification ref="toast" />
        <h2 class="admin-title">Панель администратора</h2>
        <div class="admin-actions">
            <button @click="createNewProduct" class="admin-button create">Добавить новый товар</button>
            <button @click="createNewCategory" class="admin-button create">Добавить новую категорию</button>
            <button @click="manageUsers" class="admin-button manage">Управление пользователями</button>
        </div>

        <!-- Модальные окна -->
        <AdminUserManagement 
            v-if="showUserManagement"
            @close="closeUserManagement"
            @user-selected="showUserDetails"
        />

        <AdminUserDetails
            v-if="showUserDetailsModal"
            :user="selectedUser"
            :userActivity="userActivity"
            @close="closeUserDetails"
        />

        <AdminCreateProduct
            v-if="showCreateProductForm"
            @close="closeCreateProduct"
            @product-created="handleProductCreated"
        />

        <AdminCreateCategory
            v-if="showCategoryForm"
            @close="closeCategoryCreate"
            @category-created="handleCategoryCreated"
        />
    </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';
import AdminUserManagement from './AdminUserManagement.vue';
import AdminUserDetails from './AdminUserDetails.vue';
import AdminCreateProduct from './AdminCreateProduct.vue';
import AdminCreateCategory from './AdminCreateCategory.vue';
import ToastNotification from '../ToastNotification.vue';

const toast = ref(null);

// Reactive states for modal visibility
const showUserManagement = ref(false);
const showUserDetailsModal = ref(false);
const showCreateProductForm = ref(false);
const showCategoryForm = ref(false);

// User details state
const selectedUser = ref(null);
const userActivity = ref({
    totalOrders: 0,
    totalReviews: 0,
    wishlistCount: 0,
    totalSpent: 0,
    recentOrders: [],
    recentReviews: [],
    wishlistItems: []
});

// Event handlers
const createNewProduct = () => {
    showCreateProductForm.value = true;
};

const createNewCategory = () => {
    showCategoryForm.value = true;
};

const manageUsers = () => {
    showUserManagement.value = true;
};

const closeUserManagement = () => {
    showUserManagement.value = false;
};

const showUserDetails = (user) => {
    selectedUser.value = user;
    showUserDetailsModal.value = true;
};

const closeUserDetails = () => {
    showUserDetailsModal.value = false;
    selectedUser.value = null;
};

const closeCreateProduct = () => {
    showCreateProductForm.value = false;
};

const closeCategoryCreate = () => {
    showCategoryForm.value = false;
};

const handleProductCreated = () => {
    toast.value?.showToast('Товар успешно создан!', 'success');
    closeCreateProduct();
    emit('product-created');
};

const handleCategoryCreated = () => {
    toast.value?.showToast('Категория успешно создана!', 'success');
    closeCategoryCreate();
    emit('category-created');
};

// Emit events to parent
const emit = defineEmits(['product-created', 'category-created']);
</script>

<style scoped>
.admin-dashboard {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    border-left: 4px solid #6b46c1;
}

.admin-title {
    color: #6b46c1;
    font-size: 20px;
    margin-bottom: 15px;
}

.admin-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.admin-button {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.admin-button.create {
    background: linear-gradient(135deg, #6b46c1, #553c9a);
    color: white;
}

.admin-button.manage {
    background: linear-gradient(135deg, #2196f3, #1976d2);
    color: white;
}

.admin-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.admin-button.create:hover {
    background: linear-gradient(135deg, #553c9a, #4c3282);
}

.admin-button.manage:hover {
    background: linear-gradient(135deg, #1976d2, #1565c0);
}
</style>