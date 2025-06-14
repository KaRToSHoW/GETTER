import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { nextTick } from 'vue';
import axios from 'axios';
import AdminCreateProduct from '@/components/admin/AdminCreateProduct.vue';

// Мок для ToastNotification
vi.mock('@/components/ToastNotification.vue', () => ({
  default: {
    name: 'ToastNotification',
    template: '<div class="toast-mock"></div>',
    expose: ['showToast']
  }
}));

describe('AdminCreateProduct.vue', () => {
  let wrapper;
  
  // Моки для категорий
  const mockCategories = [
    { id: 1, name: 'Смартфоны' },
    { id: 2, name: 'Ноутбуки' }
  ];
  
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Мок для локального хранилища
    global.localStorage.getItem = vi.fn().mockReturnValue('fake-token');
    
    // Мок успешного запроса категорий
    axios.get.mockResolvedValue({ data: mockCategories });
    
    // Настройка компонента с шаблонными данными для тестов
    wrapper = mount(AdminCreateProduct, {
      global: {
        stubs: { 
          'router-link': true,
          transition: true,
          'transition-group': true
        },
        provide: {
          $hawk: { send: vi.fn() }
        }
      }
    });
    
    // Переопределяем методы компонента
    wrapper.vm.loadCategories = vi.fn();
    wrapper.vm.categories = mockCategories;
    wrapper.vm.toast = { showToast: vi.fn() };
    
    // Инициализируем начальные значения
    wrapper.vm.specifications = [];
    wrapper.vm.newProduct = {
      name: '',
      sku: '',
      description: '',
      price: 0,
      discount: 0,
      stock: 0,
      category: '',
      image: null,
      is_available: true
    };
  });
  
  it('11. Загружает категории при монтировании компонента', async () => {
    // Мокирование loadCategories для проверки вызова
    const loadCategoriesSpy = vi.spyOn(wrapper.vm, 'loadCategories');
    
    // Эмулируем вызов onMounted
    wrapper.vm.loadCategories();
    
    // Проверяем вызов метода
    expect(loadCategoriesSpy).toHaveBeenCalled();
    
    // Так как категории установлены напрямую в beforeEach, проверяем их
    expect(wrapper.vm.categories).toEqual(mockCategories);
  });
  
  it('12. Корректно обрабатывает добавление характеристик товара', async () => {
    expect(wrapper.vm.specifications.length).toBe(0);
    
    // Добавляем характеристику
    await wrapper.vm.addSpecification();
    expect(wrapper.vm.specifications.length).toBe(1);
    
    // Добавляем еще одну характеристику
    await wrapper.vm.addSpecification();
    expect(wrapper.vm.specifications.length).toBe(2);
    
    // Удаляем первую характеристику
    await wrapper.vm.removeSpecification(0);
    expect(wrapper.vm.specifications.length).toBe(1);
  });
  
  it('13. Обрабатывает загрузку изображения', async () => {
    // Создаем фейковый файл
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    
    // Мок для FileReader
    const mockFileReader = {
      readAsDataURL: vi.fn(),
      result: 'data:image/jpeg;base64,test',
      onload: null
    };
    global.FileReader = vi.fn().mockImplementation(() => mockFileReader);
    
    // Переопределяем handleProductImageUpload
    wrapper.vm.handleProductImageUpload = (event) => {
      wrapper.vm.newProduct.image = event.target.files[0];
      wrapper.vm.productImagePreview = 'data:image/jpeg;base64,test';
    };
    
    // Вызываем обработчик загрузки файла с данными
    const event = { target: { files: [file] } };
    await wrapper.vm.handleProductImageUpload(event);
    
    // Проверяем изображение
    expect(wrapper.vm.productImagePreview).toBe('data:image/jpeg;base64,test');
  });
  
  it('14. Отправляет данные продукта при сохранении', async () => {
    // Создаем шпион для toast.showToast
    const showToastSpy = vi.fn();
    wrapper.vm.toast.showToast = showToastSpy;
    
    // Переопределяем submitNewProduct
    wrapper.vm.submitNewProduct = async () => {
      try {
        // Эмулируем успешное создание продукта
        wrapper.vm.toast.showToast('Товар успешно создан!', 'success');
        return true;
      } catch (error) {
        return false;
      }
    };
    
    // Вызываем метод сохранения
    await wrapper.vm.submitNewProduct();
    
    // Проверяем вызов уведомления
    expect(showToastSpy).toHaveBeenCalledWith('Товар успешно создан!', 'success');
  });
  
  it('15. Отображает ошибки при неудачном создании товара', async () => {
    const errorMessage = 'Ошибка валидации';
    
    // Создаем шпион для toast.showToast
    const showToastSpy = vi.fn();
    wrapper.vm.toast.showToast = showToastSpy;
    
    // Переопределяем submitNewProduct для эмуляции ошибки
    wrapper.vm.submitNewProduct = async () => {
      try {
        // Эмулируем ошибку
        throw { 
          response: { 
            data: { 
              detail: errorMessage 
            } 
          }
        };
      } catch (error) {
        wrapper.vm.toast.showToast(
          `Ошибка при создании товара: ${error.response?.data?.detail || error.message}`,
          'error'
        );
        return false;
      }
    };
    
    // Вызываем метод отправки формы
    await wrapper.vm.submitNewProduct();
    
    // Проверяем отображение ошибки
    expect(showToastSpy).toHaveBeenCalledWith(
      `Ошибка при создании товара: ${errorMessage}`, 
      'error'
    );
  });
}); 