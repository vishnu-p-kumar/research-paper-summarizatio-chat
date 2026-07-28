import { useMemo, useState } from "react";
import { authErrorMessage, forgotPassword, resetPassword } from "../auth.js";
import { useAuth } from "../AuthContext.jsx";

function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function validatePassword(password) {
  if (password.length < 8) return "Use at least 8 characters.";
  if (!/[A-Z]/.test(password)) return "Add at least one uppercase letter.";
  if (!/[a-z]/.test(password)) return "Add at least one lowercase letter.";
  if (!/\d/.test(password)) return "Add at least one number.";
  if (!/[^A-Za-z0-9]/.test(password)) return "Add at least one special character.";
  return "";
}

function AuthShell({ title, subtitle, children }) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-auto bg-fz-base px-4 py-8 text-fz-text">
      <div className="bg-blobs" />
      <div className="glass-panel relative z-10 w-full max-w-md rounded-2xl border border-fz-border p-6 shadow-2xl shadow-black/30">
        <div className="mb-6">
          <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-fz-primary to-fz-accent p-0.5 shadow-glow">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-fz-base text-sm font-black">
              AI
            </div>
          </div>
          <h1 className="font-display text-3xl font-black tracking-tight">{title}</h1>
          <p className="mt-2 text-sm leading-6 text-fz-textmuted">{subtitle}</p>
        </div>
        {children}
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-bold uppercase tracking-[0.14em] text-fz-textmuted">
        {label}
      </span>
      {children}
    </label>
  );
}

function PasswordInput({ value, onChange, placeholder = "Password" }) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="flex rounded-lg border border-fz-border bg-black/25 focus-within:border-fz-primary focus-within:ring-2 focus-within:ring-fz-primary/20">
      <input
        type={visible ? "text" : "password"}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="min-w-0 flex-1 bg-transparent px-3 py-2 text-sm text-fz-text placeholder:text-fz-textmuted focus:outline-none"
      />
      <button
        type="button"
        className="px-3 text-xs font-bold text-fz-primary"
        onClick={() => setVisible((v) => !v)}
      >
        {visible ? "Hide" : "Show"}
      </button>
    </div>
  );
}

function TextInput(props) {
  return (
    <input
      {...props}
      className="w-full rounded-lg border border-fz-border bg-black/25 px-3 py-2 text-sm text-fz-text placeholder:text-fz-textmuted transition focus:border-fz-primary focus:outline-none focus:ring-2 focus:ring-fz-primary/20"
    />
  );
}

function Message({ type, children }) {
  if (!children) return null;
  const cls =
    type === "error"
      ? "border-red-400/25 bg-red-500/10 text-red-200"
      : "border-emerald-400/25 bg-emerald-500/10 text-emerald-200";
  return <div className={`rounded-lg border p-3 text-sm leading-6 ${cls}`}>{children}</div>;
}

export function LoginPage() {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login({ ...form, remember_me: false });
      navigate("/");
    } catch (err) {
      setError(authErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Log in to summarize papers and chat with your research library.">
      <form className="space-y-4" onSubmit={submit}>
        <Field label="Email">
          <TextInput type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" required />
        </Field>
        <Field label="Password">
          <PasswordInput value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </Field>
        <div className="flex items-center justify-end gap-3 text-sm">
          <button type="button" className="font-bold text-fz-primary" onClick={() => navigate("/forgot-password")}>
            Forgot password?
          </button>
        </div>
        <Message type="error">{error}</Message>
        <button className="w-full rounded-lg bg-fz-primary px-4 py-2.5 text-sm font-black text-black shadow-glow transition hover:brightness-110 disabled:opacity-60" disabled={busy}>
          {busy ? "Logging in..." : "Log in"}
        </button>
        <p className="text-center text-sm text-fz-textmuted">
          New here?{" "}
          <button type="button" className="font-bold text-fz-primary" onClick={() => navigate("/register")}>
            Create account
          </button>
        </p>
      </form>
    </AuthShell>
  );
}

export function RegisterPage() {
  const { register } = useAuth();
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const passwordError = useMemo(() => (form.password ? validatePassword(form.password) : ""), [form.password]);

  async function submit(e) {
    e.preventDefault();
    if (passwordError) {
      setError(passwordError);
      return;
    }
    setBusy(true);
    setError("");
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      setError(authErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Create account" subtitle="Secure your papers, summaries, and research chats.">
      <form className="space-y-4" onSubmit={submit}>
        <Field label="Full name">
          <TextInput value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Your name" required />
        </Field>
        <Field label="Email">
          <TextInput type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" required />
        </Field>
        <Field label="Password">
          <PasswordInput value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </Field>
        {passwordError ? <p className="text-xs text-amber-200">{passwordError}</p> : null}
        <Message type="error">{error}</Message>
        <button className="w-full rounded-lg bg-fz-primary px-4 py-2.5 text-sm font-black text-black shadow-glow transition hover:brightness-110 disabled:opacity-60" disabled={busy}>
          {busy ? "Creating account..." : "Sign up"}
        </button>
        <p className="text-center text-sm text-fz-textmuted">
          Already have an account?{" "}
          <button type="button" className="font-bold text-fz-primary" onClick={() => navigate("/login")}>
            Log in
          </button>
        </p>
      </form>
    </AuthShell>
  );
}

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const data = await forgotPassword({ email });
      setMessage(data.message);
    } catch (err) {
      setError(authErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Reset access" subtitle="Enter your email and we will prepare password reset instructions.">
      <form className="space-y-4" onSubmit={submit}>
        <Field label="Email">
          <TextInput type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
        </Field>
        <Message type="success">{message}</Message>
        <Message type="error">{error}</Message>
        <button className="w-full rounded-lg bg-fz-primary px-4 py-2.5 text-sm font-black text-black shadow-glow transition hover:brightness-110 disabled:opacity-60" disabled={busy}>
          {busy ? "Sending..." : "Send reset instructions"}
        </button>
        <button type="button" className="w-full text-sm font-bold text-fz-primary" onClick={() => navigate("/login")}>
          Back to login
        </button>
      </form>
    </AuthShell>
  );
}

export function ResetPasswordPage() {
  const params = new URLSearchParams(window.location.search);
  const [form, setForm] = useState({ token: params.get("token") || "", password: "" });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const passwordError = useMemo(() => (form.password ? validatePassword(form.password) : ""), [form.password]);

  async function submit(e) {
    e.preventDefault();
    if (passwordError) {
      setError(passwordError);
      return;
    }
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const data = await resetPassword(form);
      setMessage(data.message);
    } catch (err) {
      setError(authErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Choose new password" subtitle="Paste your reset token and set a stronger password.">
      <form className="space-y-4" onSubmit={submit}>
        <Field label="Reset token">
          <TextInput value={form.token} onChange={(e) => setForm({ ...form, token: e.target.value })} placeholder="Reset token" required />
        </Field>
        <Field label="New password">
          <PasswordInput value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="New password" />
        </Field>
        {passwordError ? <p className="text-xs text-amber-200">{passwordError}</p> : null}
        <Message type="success">{message}</Message>
        <Message type="error">{error}</Message>
        <button className="w-full rounded-lg bg-fz-primary px-4 py-2.5 text-sm font-black text-black shadow-glow transition hover:brightness-110 disabled:opacity-60" disabled={busy}>
          {busy ? "Resetting..." : "Reset password"}
        </button>
        <button type="button" className="w-full text-sm font-bold text-fz-primary" onClick={() => navigate("/login")}>
          Back to login
        </button>
      </form>
    </AuthShell>
  );
}
