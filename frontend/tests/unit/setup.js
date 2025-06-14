import { config } from '@vue/test-utils';
import { vi } from 'vitest';

// Глобальные моки для Vue Test Utils
config.global.mocks = {
  $hawk: {
    send: vi.fn()
  }
};

// Мок для localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
};

// Мок для axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    defaults: {
      headers: {
        common: {}
      }
    },
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
})); 