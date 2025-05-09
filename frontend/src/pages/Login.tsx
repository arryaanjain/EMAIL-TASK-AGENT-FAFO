// src/pages/Login.tsx
import React from 'react';
import OAuthButton from '../components/OAuthButton';

const Login: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white px-4">
      <h2 className="text-3xl font-semibold mb-4">Sign in to Continue</h2>
      <p className="text-gray-600 mb-6 text-center">
        Connect your Microsoft account to access your Outlook calendar.
      </p>
      <OAuthButton />
    </div>
  );
};

export default Login;
