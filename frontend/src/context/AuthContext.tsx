import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient from '../utils/axiosInterceptor';

interface AuthContextType {
  isAuthenticated: boolean;
  loading: boolean;
  login: (tokens: { access_token: string; id_token: string }) => Promise<boolean>;
  logout: () => Promise<void>;
  user: any | null;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  loading: false,
  login: async () => false,
  logout: async () => {},
  user: null
});

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

const login = async (tokens: { access_token: string; id_token: string }): Promise<boolean> => {
  try {
    console.log('Starting login process...');
    
    // Store tokens
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('id_token', tokens.id_token);

    // Configure axios for the status check
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;

    // Check authentication status
    const { data } = await apiClient.get('/api/auth/status');
    console.log('Status check response:', data);
    
    if (!data.isAuthenticated) {
      throw new Error('Backend authentication failed');
    }

    setUser(data.user);
    setIsAuthenticated(true);
    return true;
  } catch (error) {
    console.error('Login process failed:', error);
    localStorage.clear();
    delete apiClient.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    throw error;
  }
};

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No token found');
      }

      const { data } = await apiClient.get('/api/auth/status');
      console.log('Auth check response:', data);

      if (!data.isAuthenticated) {
        throw new Error('Not authenticated');
      }

      setIsAuthenticated(true);
      setUser(data.user);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.clear();
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    console.log('Logging out...');
    try {
      await apiClient.get('/api/auth/logout');
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      localStorage.clear();
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);
  
  return (
    <AuthContext.Provider value={{ isAuthenticated, loading, login, logout, user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};