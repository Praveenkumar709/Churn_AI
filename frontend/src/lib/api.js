const API_BASE_URL = 'http://127.0.0.1:8000';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getAuthHeaders() {
    const token = localStorage.getItem('access_token');

    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const config = {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: response.statusText }));

        throw new Error(error.detail || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async upload(endpoint, formData) {
    const url = `${this.baseURL}${endpoint}`;
    const token = localStorage.getItem('access_token');

    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: response.statusText }));

        throw new Error(error.detail || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API upload failed: ${url}`, error);
      throw error;
    }
  }

  async download(endpoint, formData) {
    const url = `${this.baseURL}${endpoint}`;
    const token = localStorage.getItem('access_token');

    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: response.statusText }));

        throw new Error(error.detail || 'Download failed');
      }

      const blob = await response.blob();

      const downloadUrl = window.URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = 'churn_analysis_results.csv';

      document.body.appendChild(a);
      a.click();

      document.body.removeChild(a);

      window.URL.revokeObjectURL(downloadUrl);

      return {
        success: true,
      };
    } catch (error) {
      console.error(`API download failed: ${url}`, error);
      throw error;
    }
  }
}

export const apiClient = new ApiClient();

export const authApi = {
  login: async (email, password) => {
    return apiClient.post('/auth/login', {
      email,
      password,
    });
  },

  register: async (fullName, email, password) => {
    return apiClient.post('/auth/register', {
      full_name: fullName,
      email,
      password,
    });
  },
};

export const predictApi = {
  predictSingle: async (customerData) => {
    return apiClient.post('/predict', customerData);
  },
};

export const uploadApi = {
  uploadCsv: async (file) => {
    const formData = new FormData();

    formData.append('file', file);

    return apiClient.upload('/upload', formData);
  },

  getOverview: async () => {
    return apiClient.get('/upload/overview');
  },

  downloadResults: async (file) => {
    const formData = new FormData();

    formData.append('file', file);

    return apiClient.download('/upload/download', formData);
  },
};

export const reportApi = {
  getHistory: async () => {
    return apiClient.get('/report/history');
  },

  getSummary: async () => {
    return apiClient.get('/report/summary');
  },
};
