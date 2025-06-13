import { msalInstance } from "./msalInstance";
import { loginRequest } from "./msalConfig";
import { AccountInfo } from "@azure/msal-browser";

export const acquireAccessToken = async (): Promise<string> => {
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length === 0) {
    throw new Error("No user account found. Ensure the user is signed in.");
  }

  const account: AccountInfo = accounts[0];

  const tokenResponse = await msalInstance.acquireTokenSilent({
    ...loginRequest,
    account,
  });

  return tokenResponse.accessToken;
};
