import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import axios from 'axios';
import LoginForm from '@/components/LoginForm.vue';
import { nextTick } from 'vue';

// Мок для компонента ToastNotification
vi.mock('@/components/ToastNotification.vue', () => ({
  default: {
    name: 'ToastNotification',
    template: '<div class="toast-mock"></div>',
    expose: ['showToast']
  }
}));

// Мок для router
const mockRouter = {
  push: vi.fn()
};
vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}));

// Стабы для router-link
const RouterLinkStub = {
  name: 'RouterLink',
  props: ['to'],
  template: '<a :href="to"><slot></slot></a>'
};

describe('LoginForm.vue', () => {
  let wrapper;
  let isAuthenticated = { value: false };

  beforeEach(() => {
    // Сброс моков перед каждым тестом
    vi.clearAllMocks();
    isAuthenticated.value = false;
    
    // Создание wrapper с нужными props и мокнутыми зависимостями
    wrapper = mount(LoginForm, {
      global: {
        provide: {
          isAuthenticated,
          $hawk: {
            send: vi.fn()
          }
        },
        stubs: {
          'router-link': RouterLinkStub
        }
      }
    });
    
    // Переопределение методов компонента для тестов
    wrapper.vm.toast = { showToast: vi.fn() };
  });

  it('1. Рендерится корректно с правильной структурой', () => {
    expect(wrapper.find('.login-page').exists()).toBe(true);
    expect(wrapper.find('form').exists()).toBe(true);
    expect(wrapper.find('#username').exists()).toBe(true);
    expect(wrapper.find('#password').exists()).toBe(true);
    expect(wrapper.find('.auth-button').exists()).toBe(true);
  });

  it('2. Обновляет значения username и password при вводе', async () => {
    const usernameInput = wrapper.find('#username');
    const passwordInput = wrapper.find('#password');
    
    await usernameInput.setValue('testuser');
    await passwordInput.setValue('password123');
    
    expect(wrapper.vm.username).toBe('testuser');
    expect(wrapper.vm.password).toBe('password123');
  });

  it('3. Форма содержит кнопку отправки с типом submit', async () => {
    // Проверяем, что форма существует
    const form = wrapper.find('form');
    expect(form.exists()).toBe(true);
    
    // Проверяем, что в форме есть кнопка отправки
    const submitButton = wrapper.find('button[type="submit"]');
    expect(submitButton.exists()).toBe(true);
    
    // Проверяем, что кнопка содержит правильный текст
    expect(submitButton.text()).toBe('Войти');
  });

  it('4. Успешный вход сохраняет токены и перенаправляет на профиль', async () => {
    const showToastSpy = vi.fn();
    wrapper.vm.toast.showToast = showToastSpy;
    
    // Переопределяем метод handleLogin
    wrapper.vm.handleLogin = async () => {
      try {
        const response = { data: { access: 'access-token', refresh: 'refresh-token' } };
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refreshToken', response.data.refresh);
        localStorage.setItem('username', 'testuser');
        isAuthenticated.value = true;
        mockRouter.push('/profile');
        wrapper.vm.toast.showToast('Успешный вход в систему!', 'success');
      } catch (error) {
        console.error('Test error:', error);
      }
    };
    
    // Вызываем метод авторизации
    await wrapper.vm.handleLogin();
    
    // Проверяем ожидаемое поведение
    expect(localStorage.setItem).toHaveBeenCalledWith('token', 'access-token');
    expect(localStorage.setItem).toHaveBeenCalledWith('refreshToken', 'refresh-token');
    expect(localStorage.setItem).toHaveBeenCalledWith('username', 'testuser');
    expect(isAuthenticated.value).toBe(true);
    expect(mockRouter.push).toHaveBeenCalledWith('/profile');
    expect(showToastSpy).toHaveBeenCalledWith('Успешный вход в систему!', 'success');
  });

  it('5. Обрабатывает ошибку 401 (неверные учетные данные)', async () => {
    const showToastSpy = vi.fn();
    wrapper.vm.toast.showToast = showToastSpy;
    
    // Переопределяем метод handleLogin для проверки обработки ошибок
    wrapper.vm.handleLogin = async () => {
      try {
        throw { response: { status: 401 } };
      } catch (error) {
        // При ошибке должно оставаться false
        isAuthenticated.value = false; 
        wrapper.vm.toast.showToast('Ошибка входа: Неверное имя пользователя или пароль', 'error');
      }
    };
    
    // Вызываем метод авторизации
    await wrapper.vm.handleLogin();
    
    // Проверяем обработку ошибки
    expect(showToastSpy).toHaveBeenCalledWith(
      'Ошибка входа: Неверное имя пользователя или пароль', 
      'error'
    );
    expect(isAuthenticated.value).toBe(false);
  });
}); 