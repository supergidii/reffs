import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth services
export const authService = {
  login: async (phone, password) => {
    try {
      console.log("API Service: Sending login request for", phone);
      const response = await api.post('/login/', { phone_number: phone, password });
      console.log("API Service: Login response received:", response.data);
      
      if (response.data.access) {
        // Log the token BEFORE storing
        console.log("API Service: Access Token Received:", response.data.access);
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      } else {
        console.warn("API Service: Login successful but no access token in response.");
      }
      return response.data;
    } catch (error) {
      console.error("API Service: Login failed:", error);
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Login failed';
      console.error("API Service: Throwing error:", errorMessage);
      throw new Error(errorMessage);
    }
  },

  register: async (userData) => {
    try {
      const response = await api.post('/register/', userData);
      if (response.data.access) {
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      // Handle validation errors
      if (error.response?.data) {
        const errors = error.response.data;
        if (typeof errors === 'object') {
          const errorMessages = Object.entries(errors)
            .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
            .join('\n');
          throw new Error(errorMessages);
        }
      }
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  }
};

export default api; 