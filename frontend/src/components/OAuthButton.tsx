import React from 'react';

const OAuthButton: React.FC = () => {
  // This will redirect to the backend route for Microsoft OAuth2 authentication
  const handleOAuthLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/api/auth/login`; 
  };

  return (
    <button 
      onClick={handleOAuthLogin} 
      className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-200"
    >
      Login with Microsoft
    </button>
  );
};

export default OAuthButton;
