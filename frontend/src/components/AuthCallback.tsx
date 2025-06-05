import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
  const handleCallback = async () => {
    try {
      const params = new URLSearchParams(location.search);
      const access_token = params.get('access_token');
      const id_token = params.get('id_token');

      if (!access_token || !id_token) {
        console.error('Missing tokens in callback URL');
        navigate('/login');
        return;
      }

      console.log('Token validation started...');
      await login({ access_token, id_token });
      console.log('Login successful, redirecting...');
      navigate('/dashboard');
    } catch (error) {
      console.error('Auth callback failed:', error);
      navigate('/login');
    }
  };

  handleCallback();
}, [location, login, navigate]);

  return <div>Completing authentication...</div>;
};

export default AuthCallback;