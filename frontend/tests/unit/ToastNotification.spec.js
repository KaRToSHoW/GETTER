import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { nextTick } from 'vue';
import ToastNotification from '@/components/ToastNotification.vue';

describe('ToastNotification.vue', () => {
  let wrapper;
  const hawkMock = { send: vi.fn() };
  
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    
    wrapper = mount(ToastNotification, {
      global: {
        provide: {
          $hawk: hawkMock
        }
      }
    });
  });
  
  it('6. Отображает toast-уведомление при вызове showToast', async () => {
    const message = 'Тестовое сообщение';
    const type = 'success';
    
    wrapper.vm.showToast(message, type);
    await nextTick();
    
    // Проверяем, что toast добавлен в массив
    expect(wrapper.vm.toasts.length).toBe(1);
    expect(wrapper.vm.toasts[0].message).toBe(message);
    expect(wrapper.vm.toasts[0].type).toBe(type);
    
    // Проверяем рендеринг
    const toast = wrapper.find('.toast');
    expect(toast.exists()).toBe(true);
    expect(toast.text()).toBe(message);
    expect(toast.classes()).toContain('toast-success');
  });
  
  it('7. Удаляет toast-уведомление через 3 секунды', async () => {
    wrapper.vm.showToast('Временное сообщение');
    await nextTick();
    
    expect(wrapper.vm.toasts.length).toBe(1);
    
    // Перематываем таймер на 3 секунды вперед
    vi.advanceTimersByTime(3000);
    await nextTick();
    
    // Toast должен быть удален
    expect(wrapper.vm.toasts.length).toBe(0);
  });
  
  it('8. Поддерживает несколько уведомлений одновременно', async () => {
    wrapper.vm.showToast('Первое сообщение', 'info');
    wrapper.vm.showToast('Второе сообщение', 'success');
    wrapper.vm.showToast('Третье сообщение', 'error');
    await nextTick();
    
    // Проверяем, что все три сообщения отображаются
    const toasts = wrapper.findAll('.toast');
    expect(toasts.length).toBe(3);
    expect(toasts[0].text()).toBe('Первое сообщение');
    expect(toasts[1].text()).toBe('Второе сообщение');
    expect(toasts[2].text()).toBe('Третье сообщение');
    
    expect(toasts[0].classes()).toContain('toast-info');
    expect(toasts[1].classes()).toContain('toast-success');
    expect(toasts[2].classes()).toContain('toast-error');
  });
  
  it('9. Отправляет ошибки в Hawk при типе error', async () => {
    const errorMessage = 'Ошибка тестирования';
    wrapper.vm.showToast(errorMessage, 'error');
    await nextTick();
    
    // Проверяем вызов Hawk.send
    expect(hawkMock.send).toHaveBeenCalled();
    
    // Проверяем аргументы вызова
    const callArgs = hawkMock.send.mock.calls[0];
    expect(callArgs[0] instanceof Error).toBe(true);
    expect(callArgs[0].message).toContain(errorMessage);
    expect(callArgs[1].type).toBe('toast_error');
  });
  
  it('10. Не отправляет в Hawk при типах, не являющихся ошибками', async () => {
    wrapper.vm.showToast('Информационное сообщение', 'info');
    wrapper.vm.showToast('Сообщение об успехе', 'success');
    await nextTick();
    
    // Hawk.send не должен вызываться
    expect(hawkMock.send).not.toHaveBeenCalled();
  });
}); 