import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getMe, loginUser, logoutUser, registerUser } from "./auth.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
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
    setUser(data.user);
    return data;
  }

  async function register(payload) {
    const data = await registerUser(payload);
    setUser(data.user);
    return data;
  }

  async function logout() {
    await logoutUser();
    setUser(null);
    window.history.pushState({}, "", "/login");
    window.dispatchEvent(new PopStateEvent("popstate"));
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
