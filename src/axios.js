import axios from 'axios';
import store from './store/index'
import router from './router';

const axiosInstance = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor
axiosInstance.interceptors.request.use(config => {
  const token = store.getters.getAccessToken;
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Add a response interceptor
axiosInstance.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    if (error.response && error.response.status === 401) {
      router.push({ name: 'Login' });
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
