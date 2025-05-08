import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get("http://localhost:5000/api/process_emails")
      .then(res => setEmails(res.data))
      .catch(err => console.error("Error fetching:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">📧 Processed Emails</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        emails.map((email, idx) => (
          <div key={idx} className="bg-white p-4 rounded shadow mb-4">
            <h2 className="text-xl font-semibold">{email.subject}</h2>
            {email.error ? (
              <p className="text-red-500 mt-2">⚠️ {email.error}</p>
            ) : (
              <>
                <p className="mt-2">{email.summary}</p>
                <ul className="mt-2 list-disc list-inside">
                  {email.tasks.map((task, i) => (
                    <li key={i}>{task.description}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default App;
