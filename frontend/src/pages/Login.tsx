import React from 'react';

const Login = () => {
  const handleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/api/auth/login`;
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Welcome to Email Task Agent</h1>
        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
        >
          Sign in with Microsoft
        </button>
      </div>
    </div>
  );
};

export default Login;