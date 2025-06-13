import { acquireAccessToken } from "../auth/tokenService";

export const fetchUnreadEmails = async () => {
  try {
    const token = await acquireAccessToken();

    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/read-emails`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error("Failed to fetch unread emails:", error);
    throw error;
  }
};
