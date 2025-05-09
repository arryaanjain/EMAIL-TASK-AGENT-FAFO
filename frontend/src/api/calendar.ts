import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

// Fetch events from Microsoft Graph
export const fetchCalendarEvents = async () => {
  const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/calendar/events`, { withCredentials: true });
  return response.data;
};

// Create a new calendar event
export const createCalendarEvent = async (eventData: any) => {
  const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/calendar/events`, eventData, { withCredentials: true });
  return response.data;
};

// Trigger OAuth2 login flow
export const initiateOAuthLogin = () => {
  window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/login`;
};

// Logout
export const logout = async () => {
  await axios.post(`${import.meta.env.VITE_API_BASE_URL}/auth/logout`, {}, { withCredentials: true });
};
