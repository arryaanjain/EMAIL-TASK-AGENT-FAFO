import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ReactNode } from 'react';

const ProtectedRoute: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const token = localStorage.getItem('access_token');

  if (loading) {
    return <div>Loading authentication status...</div>;
  }

  if (!isAuthenticated || !token) {
    localStorage.clear();
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;