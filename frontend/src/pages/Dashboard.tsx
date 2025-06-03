import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/api/auth/logout`;
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-800 to-gray-900">
      {/* Navigation Bar */}
      <nav className="bg-gray-900 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <span className="text-white text-xl font-bold">Email Task Agent</span>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Calendar Card */}
          <div className="bg-white rounded-lg shadow-xl p-6 transform hover:scale-105 transition-transform duration-300">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Calendar Management</h2>
            <p className="text-gray-600 mb-6">View and manage your upcoming meetings and appointments.</p>
            <Link
              to="/calendar"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
            >
              View Calendar
            </Link>
          </div>

          {/* Tasks Card */}
          <div className="bg-white rounded-lg shadow-xl p-6 transform hover:scale-105 transition-transform duration-300">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Task Management</h2>
            <p className="text-gray-600 mb-6">Organize and track your tasks and to-dos efficiently.</p>
            <Link
              to="/tasks"
              className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition"
            >
              Manage Tasks
            </Link>
          </div>

          {/* Email Analytics Card */}
          <div className="bg-white rounded-lg shadow-xl p-6 transform hover:scale-105 transition-transform duration-300">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Email Analytics</h2>
            <p className="text-gray-600 mb-6">Get insights into your email patterns and communication.</p>
            <Link
              to="/analytics"
              className="inline-block bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition"
            >
              View Analytics
            </Link>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 text-white">
            <h3 className="text-lg font-semibold">Upcoming Meetings</h3>
            <p className="text-3xl font-bold mt-2">12</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-white">
            <h3 className="text-lg font-semibold">Pending Tasks</h3>
            <p className="text-3xl font-bold mt-2">5</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-white">
            <h3 className="text-lg font-semibold">Unread Emails</h3>
            <p className="text-3xl font-bold mt-2">8</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;