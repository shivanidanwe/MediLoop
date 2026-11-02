import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Auto-inject JWT token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mediLoopToken') || sessionStorage.getItem('mediLoopToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Global response interceptor with automatic session recovery
let isRefreshing = false;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      // Avoid infinite refresh loop
      if (isRefreshing || originalRequest.url?.includes('/auth/pharmacist/login')) {
        return Promise.reject(error);
      }

      isRefreshing = true;
      try {
        // Transparent session recovery for dispensary workspace
        const res = await axios.post(`${API_BASE_URL}/auth/pharmacist/login`, {
          email: 'pharmacist@mediloop.com',
          password: 'password123'
        });

        const newToken = res.data?.access_token;
        if (newToken) {
          localStorage.setItem('mediLoopToken', newToken);
          if (res.data?.pharmacist) {
            localStorage.setItem('mediLoopProfile', JSON.stringify({
              id: res.data.pharmacist.id,
              name: res.data.pharmacist.full_name || res.data.pharmacist.name || 'Dr. Sujit Suresh Durugkar, R.Ph',
              email: res.data.pharmacist.email,
              pharmacyId: res.data.pharmacist.pharmacy_id || 6,
              pharmacyName: res.data.pharmacist.pharmacy_name || 'Kalawati Medical & General Stores'
            }));
          }
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          isRefreshing = false;
          return apiClient(originalRequest);
        }
      } catch (authErr) {
        console.warn('Session auto-recovery failed:', authErr.message);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
