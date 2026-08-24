const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

// El frontend (Vercel) y el backend (Render) son dominios distintos, así
// que `document.cookie` no puede leer la cookie `csrftoken` que pone el
// backend (las cookies de otro dominio no son legibles por JS aunque el
// navegador sí las reenvíe). Por eso guardamos el token del body de la
// respuesta en vez de leerlo de la cookie.
let csrfToken = null;

async function ensureCsrfToken() {
  if (!csrfToken) {
    const response = await fetch(`${API_BASE}/accounts/csrf/`, { credentials: "include" });
    const data = await response.json();
    csrfToken = data.csrfToken;
  }
}

async function request(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (method !== "GET" && method !== "HEAD") {
    await ensureCsrfToken();
    headers["X-CSRFToken"] = csrfToken;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: "include",
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    const message =
      (data && (data.detail || data.message)) ||
      `Error ${response.status} al conectar con el servidor.`;
    const error = new Error(message);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  patch: (path, body) => request(path, { method: "PATCH", body }),
  del: (path) => request(path, { method: "DELETE" }),
};
