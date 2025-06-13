export const msalConfig = {
  auth: {
    clientId: "98ed9568-7ba4-4bc6-a05c-51958943b03b",
    authority: "https://emailagentnew.b2clogin.com/emailagentnew.onmicrosoft.com/B2C_1_signup_signin",
    redirectUri: "http://localhost:5000/api/auth/callback",
    postLogoutRedirectUri: "http://localhost:5173",
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: [
    "openid",
    "offline_access",
    //"https://graph.microsoft.com/Mail.Read",
  ],
};
