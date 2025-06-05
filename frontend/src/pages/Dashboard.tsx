import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../utils/axiosInterceptor';

interface Email {
  id: string;
  subject: string;
  from: string;
  date: string;
  snippet: string;
  isRead: boolean;
  labels?: string[];
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('inbox');

  useEffect(() => {
    fetchEmails();
  }, [selectedTab]);

  const fetchEmails = async () => {
    try {
      const response = await apiClient.get(`${import.meta.env.VITE_API_BASE_URL}/api/email/${selectedTab}`);
      setEmails(response.data);
    } catch (error) {
      console.error('Failed to fetch emails:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/api/auth/logout`;
  };

  const EmailTabs = () => (
    <div className="flex space-x-4 mb-6 border-b border-gray-700">
      {['inbox', 'important', 'sent', 'drafts'].map((tab) => (
        <button
          key={tab}
          onClick={() => setSelectedTab(tab)}
          className={`py-2 px-4 ${
            selectedTab === tab
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-400 hover:text-gray-200'
          } capitalize`}
        >
          {tab}
        </button>
      ))}
    </div>
  );

  const EmailItem: React.FC<{ email: Email }> = ({ email }) => (
    <div className={`p-4 border-b border-gray-700 hover:bg-gray-800 cursor-pointer ${
      !email.isRead ? 'bg-gray-750' : ''
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <input type="checkbox" className="rounded bg-gray-700 border-gray-600" />
          {!email.isRead && (
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          )}
        </div>
        <div className="flex-1 ml-4">
          <div className="flex justify-between">
            <span className="font-medium text-gray-200">{email.from}</span>
            <span className="text-sm text-gray-400">{email.date}</span>
          </div>
          <div className="text-gray-200 font-medium">{email.subject}</div>
          <p className="text-sm text-gray-400 truncate">{email.snippet}</p>
        </div>
      </div>
      {email.labels && (
        <div className="mt-2 flex gap-2">
          {email.labels.map((label) => (
            <span key={label} className="px-2 py-1 text-xs rounded-full bg-gray-700 text-gray-300">
              {label}
            </span>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation Bar */}
      <nav className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <span className="text-white text-xl font-bold">Email Task Agent</span>
              <span className="text-gray-300 text-sm">{user?.email}</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                onClick={() => navigate('/compose')}
              >
                Compose
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-6">
          {/* Sidebar */}
          <div className="w-64 space-y-4">
            <button
              onClick={() => navigate('/compose')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
              Compose Email
            </button>
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-white font-medium mb-2">Quick Stats</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Unread</span>
                  <span className="text-white">12</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Tasks</span>
                  <span className="text-white">5</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Meetings Today</span>
                  <span className="text-white">3</span>
                </div>
              </div>
            </div>
          </div>

          {/* Email List */}
          <div className="flex-1 bg-gray-800 rounded-lg">
            <div className="p-4">
              <EmailTabs />
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                </div>
              ) : (
                <div className="divide-y divide-gray-700">
                  {emails.map((email) => (
                    <EmailItem key={email.id} email={email} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;