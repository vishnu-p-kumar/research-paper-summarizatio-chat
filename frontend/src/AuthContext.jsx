import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { AUTH_TOKEN_KEY } from "./api.js";
import { getMe, loginUser, logoutUser, registerUser } from "./auth.js";

const AuthContext = createContext(null);
const AUTH_SESSION_KEY = "research_ai_auth_session";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    if (!sessionStorage.getItem(AUTH_SESSION_KEY)) {
      logoutUser().catch(() => {});
      setUser(null);
      setLoading(false);
      return () => {
        mounted = false;
      };
    }
    getMe()
      .then((data) => {
        if (mounted) setUser(data);
      })
      .catch(() => {
        if (mounted) setUser(null);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  async function login(payload) {
    const data = await loginUser(payload);
    sessionStorage.setItem(AUTH_SESSION_KEY, "1");
    sessionStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
    setUser(data.user);
    return data;
  }

  async function register(payload) {
    const data = await registerUser(payload);
    sessionStorage.setItem(AUTH_SESSION_KEY, "1");
    sessionStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
    setUser(data.user);
    return data;
  }

  async function logout() {
    try {
      await logoutUser();
    } finally {
      localStorage.removeItem("ai_paper_doc_id");
      localStorage.removeItem("ai_paper_preview");
      sessionStorage.removeItem(AUTH_SESSION_KEY);
      sessionStorage.removeItem(AUTH_TOKEN_KEY);
      setUser(null);
      window.history.pushState({}, "", "/login");
      window.dispatchEvent(new PopStateEvent("popstate"));
    }
  }

  const value = useMemo(
    () => ({ user, loading, authenticated: Boolean(user), login, register, logout }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
