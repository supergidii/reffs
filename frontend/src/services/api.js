import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to add the auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add a response interceptor to handle common errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized access
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth services
export const authService = {
  login: async (phone, password) => {
    try {
      console.log("API Service: Starting login process");
      console.log("API Service: Login data:", { phone_number: phone });
      
      // Log the API configuration
      console.log("API Service: Base URL:", api.defaults.baseURL);
      console.log("API Service: Headers:", api.defaults.headers);
      
      const response = await api.post('/api/login/', { phone_number: phone, password });
      console.log("API Service: Login response received:", response.data);
      
      if (response.data.access) {
        console.log("API Service: Access Token Received:", response.data.access);
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        console.log("API Service: Token and user data stored in localStorage");
      } else {
        console.warn("API Service: Login successful but no access token in response");
      }
      return response.data;
    } catch (error) {
      console.error("API Service: Login error details:", {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          headers: error.config?.headers,
          data: error.config?.data
        }
      });

      // Handle network errors
      if (!error.response) {
        console.error("API Service: Network error - No response received");
        throw new Error('Network error. Please check your internet connection and try again.');
      }

      // Handle validation errors
      if (error.response?.data) {
        const errors = error.response.data;
        if (typeof errors === 'object') {
          // Format validation errors
          const errorMessages = Object.entries(errors)
            .map(([field, messages]) => {
              // Convert field name to readable format
              const readableField = field
                .split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
              return `${readableField}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            })
            .join('\n');
          throw new Error(errorMessages);
        }
      }

      // Handle server errors
      if (error.response.status >= 500) {
        console.error("API Service: Server error occurred");
        throw new Error('Server error. Please try again later.');
      }

      // Handle other errors
      throw new Error(error.response?.data?.detail || 'Login failed. Please try again.');
    }
  },

  register: async (userData) => {
    try {
      console.log("API Service: Starting registration process");
      console.log("API Service: Registration data:", userData);
      
      // Log the API configuration
      console.log("API Service: Base URL:", api.defaults.baseURL);
      console.log("API Service: Headers:", api.defaults.headers);
      
      const response = await api.post('/api/register/', userData);
      console.log("API Service: Registration response:", response.data);
      
      if (response.data.access) {
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        console.log("API Service: Registration successful - Token stored");
      } else {
        console.warn("API Service: Registration successful but no access token received");
      }
      return response.data;
    } catch (error) {
      console.error("API Service: Registration error details:", {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          headers: error.config?.headers,
          data: error.config?.data
        }
      });

      // Handle network errors
      if (!error.response) {
        console.error("API Service: Network error - No response received");
        throw new Error('Network error. Please check your internet connection and try again.');
      }

      // Handle validation errors
      if (error.response?.data) {
        const errors = error.response.data;
        if (typeof errors === 'object') {
          // Format validation errors
          const errorMessages = Object.entries(errors)
            .map(([field, messages]) => {
              // Convert field name to readable format
              const readableField = field
                .split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
              return `${readableField}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            })
            .join('\n');
          throw new Error(errorMessages);
        }
      }

      // Handle server errors
      if (error.response.status >= 500) {
        console.error("API Service: Server error occurred");
        throw new Error('Server error. Please try again later.');
      }

      // Handle other errors
      throw new Error(error.response?.data?.detail || 'Registration failed. Please try again.');
    }
  },

  logout: () => {
    console.log("Logging out - Clearing auth data"); // Debug log
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getCurrentUser: async () => {
    const user = localStorage.getItem('user');
    if (!user) {
      return null;
    }
    try {
      // Verify the token is still valid by making a request
      await api.get('/api/user/me/');
      return JSON.parse(user);
    } catch (error) {
      // If the token is invalid, clear the storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return null;
    }
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    console.log("Checking authentication - Token exists:", !!token); // Debug log
    return !!token;
  }
};

export default api; 