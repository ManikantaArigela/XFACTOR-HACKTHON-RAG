/**
 * Arudhra Mobile Stores - Authentication Client Helper
 * Provides session management, login, registration, and token validation.
 */
(() => {
  const API_BASE = window.ARUDHRA_API_BASE_URL || "http://127.0.0.1:5000/api";
  const USER_KEY = "arudhra_user";
  const TOKEN_KEY = "arudhra_token";

  window.ArudhraAuth = {
    getUser() {
      try {
        const raw = localStorage.getItem(USER_KEY);
        return raw ? JSON.parse(raw) : null;
      } catch (_e) {
        return null;
      }
    },

    getToken() {
      return localStorage.getItem(TOKEN_KEY) || "";
    },

    setSession(user, token) {
      if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
      if (token) localStorage.setItem(TOKEN_KEY, token);
      window.dispatchEvent(new CustomEvent("arudhra:auth-changed", { detail: { user, token } }));
    },

    clearSession() {
      localStorage.removeItem(USER_KEY);
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem("arudhra-cart");
      localStorage.removeItem("arudhra_cart");
      window.dispatchEvent(new CustomEvent("arudhra:auth-changed", { detail: { user: null, token: null } }));
    },

    isAuthenticated() {
      return Boolean(this.getToken() && this.getUser());
    },

    async login(email, password) {
      const res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.message || "Login failed. Please check credentials.");
      }
      this.setSession(data.user, data.token);
      return data;
    },

    async register(email, password, fullName) {
      const res = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password, full_name: fullName.trim() })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.message || "Registration failed. Please check details.");
      }
      this.setSession(data.user, data.token);
      return data;
    },

    async getCurrentUser() {
      const token = this.getToken();
      if (!token) return null;
      try {
        const res = await fetch(`${API_BASE}/me`, {
          method: "GET",
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) {
          this.clearSession();
          return null;
        }
        const data = await res.json();
        if (data.success && data.user) {
          localStorage.setItem(USER_KEY, JSON.stringify(data.user));
          return data.user;
        }
      } catch (_e) {
        return this.getUser();
      }
      return null;
    },

    async logout() {
      try {
        const token = this.getToken();
        if (token) {
          await fetch(`${API_BASE}/logout`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` }
          });
        }
      } catch (_e) {
        // Continue clearing client state regardless
      }
      this.clearSession();
    }
  };
})();
