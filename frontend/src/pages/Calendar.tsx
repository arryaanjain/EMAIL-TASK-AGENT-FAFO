import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Event {
  id: string;
  subject: string;
  start: {
    dateTime: string;
    timeZone: string;
  };
  end: {
    dateTime: string;
    timeZone: string;
  };
}

const Calendar: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCalendarEvents = async () => {
      try {
        // Assuming your backend endpoint for fetching calendar events is /api/calendar/events
        const response = await axios.get('/api/calendar/events');
        setEvents(response.data);
      } catch (err) {
        setError('Failed to fetch calendar events');
      } finally {
        setLoading(false);
      }
    };

    fetchCalendarEvents();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h2 className="text-2xl font-semibold text-center mb-6">Your Calendar Events</h2>
      <div className="space-y-4">
        {events.map((event) => (
          <div key={event.id} className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-xl font-bold">{event.subject}</h3>
            <p className="text-sm text-gray-500">
              {new Date(event.start.dateTime).toLocaleString()} - {new Date(event.end.dateTime).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Calendar;
