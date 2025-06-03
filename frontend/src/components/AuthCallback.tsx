import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const access_token = params.get('access_token');
    const id_token = params.get('id_token');

    if (access_token && id_token) {
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('id_token', id_token);
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  }, [navigate, location]);

  return <div>Loading...</div>;
};

export default AuthCallback;