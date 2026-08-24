import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "../api/client";

const StaffAuthContext = createContext(null);

export function StaffAuthProvider({ children }) {
  const [staff, setStaff] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await api.get("/accounts/staff-me/");
      setStaff(data.authenticated ? data : null);
    } catch {
      setStaff(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = async (username, password) => {
    const data = await api.post("/accounts/staff-login/", { username, password });
    setStaff({ authenticated: true, ...data });
    return data;
  };

  const logout = async () => {
    await api.post("/accounts/staff-logout/");
    setStaff(null);
  };

  return (
    <StaffAuthContext.Provider value={{ staff, loading, login, logout, refresh }}>
      {children}
    </StaffAuthContext.Provider>
  );
}

export function useStaffAuth() {
  const ctx = useContext(StaffAuthContext);
  if (!ctx) throw new Error("useStaffAuth debe usarse dentro de StaffAuthProvider");
  return ctx;
}
