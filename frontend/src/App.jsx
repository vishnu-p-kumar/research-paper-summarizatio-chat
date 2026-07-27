import { useEffect, useState } from "react";
import { AuthProvider, useAuth } from "./AuthContext.jsx";
import {
  ForgotPasswordPage,
  LoginPage,
  RegisterPage,
  ResetPasswordPage
} from "./pages/AuthPages.jsx";
import Dashboard from "./pages/Dashboard.jsx";

function currentPath() {
  return window.location.pathname || "/";
}

function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function LoadingScreen() {
  return (
    <div className="relative flex min-h-screen items-center justify-center bg-fz-base text-fz-text">
      <div className="bg-blobs" />
      <div className="relative z-10 text-sm font-bold text-fz-primary">Loading...</div>
    </div>
  );
}

function DashboardShell() {
  const { user, logout } = useAuth();

  return (
    <div className="relative flex h-screen flex-col overflow-hidden bg-fz-base text-fz-text antialiased">
      <div className="bg-blobs" />

      <header className="glass-panel relative z-30 flex h-16 shrink-0 items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-3">
          <div className="hidden h-8 w-8 rounded-lg bg-gradient-to-br from-fz-primary to-fz-accent p-0.5 shadow-glow sm:block">
            <div className="flex h-full w-full items-center justify-center rounded-md bg-fz-base">
              <span className="text-sm font-black text-white">AI</span>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-display text-lg font-bold leading-none tracking-tight text-fz-text md:text-xl">
              RESEARCHAI
            </span>
            <span className="mt-0.5 text-[9px] font-semibold uppercase leading-none tracking-[0.24em] text-fz-primary md:text-[10px]">
              Paper Intelligence
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <div className="text-xs font-bold text-fz-text">{user?.full_name}</div>
            <div className="text-[10px] text-fz-textmuted">{user?.email}</div>
          </div>
          <button
            className="rounded-lg border border-fz-border bg-white/5 px-3 py-2 text-xs font-bold text-fz-textmuted transition hover:text-fz-text"
            onClick={logout}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="relative z-10 min-h-0 flex-1">
        <Dashboard />
      </main>
    </div>
  );
}

function AppRoutes() {
  const { authenticated, loading } = useAuth();
  const [path, setPath] = useState(currentPath());

  useEffect(() => {
    const onPopState = () => setPath(currentPath());
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    const authPath = ["/login", "/register", "/forgot-password", "/reset-password"].includes(path);
    if (!loading && !authenticated && !authPath) {
      navigate("/login");
    }
    if (!loading && authenticated && authPath) {
      navigate("/");
    }
  }, [authenticated, loading, path]);

  if (loading) return <LoadingScreen />;

  if (!authenticated) {
    if (path === "/register") return <RegisterPage />;
    if (path === "/forgot-password") return <ForgotPasswordPage />;
    if (path === "/reset-password") return <ResetPasswordPage />;
    return <LoginPage />;
  }

  return <DashboardShell />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
