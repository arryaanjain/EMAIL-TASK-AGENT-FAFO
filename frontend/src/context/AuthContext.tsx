import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  loading: boolean;
  login: (tokens: { access_token: string; id_token: string }) => void;
  logout: () => void;
  user: any | null;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  loading: false,
  login: () => {},
  logout: () => {},
  user: null
});

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  const login = async (tokens: { access_token: string; id_token: string }) => {
    try {
      // Store tokens
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('id_token', tokens.id_token);

      // Verify tokens immediately
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/status`, {
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Token validation failed');
      }

      const data = await response.json();
      if (!data.isAuthenticated || !data.user) {
        throw new Error('Invalid authentication response');
      }

      setUser(data.user);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login failed:', error);
      // Clean up on failure
      localStorage.removeItem('access_token');
      localStorage.removeItem('id_token');
      setIsAuthenticated(false);
      setUser(null);
      throw error; // Re-throw to handle in UI
    }
  };

  const logout = async () => {
    try {
      // Call backend logout endpoint
      await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/logout`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
    } finally {
      // Clear local storage regardless of logout API success
      localStorage.removeItem('access_token');
      localStorage.removeItem('id_token');
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const checkAuthStatus = async () => {
    try {
      const access_token = localStorage.getItem('access_token');
      if (!access_token) {
        setIsAuthenticated(false);
        setUser(null);
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/status`, {
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Status check failed');
      }

      const data = await response.json();
      if (data.isAuthenticated && data.user) {
        setIsAuthenticated(true);
        setUser(data.user);
      } else {
        throw new Error('Invalid auth status');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      await logout();
    } finally {
      setLoading(false);
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