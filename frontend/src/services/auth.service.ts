import api from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  organization?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  organization?: string;
  role: string;
  created_at: string;
  disabled: boolean;
}

const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials);
    const data = response.data;
    
    // Store tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    return data;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post('/auth/register', data);
    const authData = response.data;
    
    // Store tokens
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('refresh_token', authData.refresh_token);
    
    return authData;
  },

  async logout(): Promise<void> {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (accessToken) {
      try {
        await api.post('/auth/logout', {
          access_token: accessToken,
          refresh_token: refreshToken,
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    
    // Clear tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async getProfile(): Promise<UserProfile> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  getToken(): string | null {
    return localStorage.getItem('access_token');
  },
};

export default authService;
