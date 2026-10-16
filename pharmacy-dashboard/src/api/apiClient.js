import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Auto-inject JWT token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mediLoopToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Global response interceptor to handle authentication errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token on Unauthorized response
      localStorage.removeItem('mediLoopToken');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
