import { api } from "./api.js";

export async function registerUser(payload) {
  const res = await api.post("/api/register", payload);
  return res.data;
}

export async function loginUser(payload) {
  const res = await api.post("/api/login", payload);
  return res.data;
}

export async function logoutUser() {
  const res = await api.post("/api/logout");
  return res.data;
}

export async function getMe() {
  const res = await api.get("/api/me");
  return res.data;
}

export async function forgotPassword(payload) {
  const res = await api.post("/api/forgot-password", payload);
  return res.data;
}

export async function resetPassword(payload) {
  const res = await api.post("/api/reset-password", payload);
  return res.data;
}

export function authErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(" ");
  }
  return detail || error?.message || "Something went wrong. Please try again.";
}
