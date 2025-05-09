// src/pages/Dashboard.tsx
import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-4xl font-bold mb-4">Welcome to Outlook Calendar Manager</h1>
      <p className="mb-8 text-lg text-gray-700">Manage your Outlook calendar tasks seamlessly.</p>
      <Link
        to="/calendar"
        className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
      >
        Go to Calendar
      </Link>
    </div>
  );
};

export default Dashboard;
