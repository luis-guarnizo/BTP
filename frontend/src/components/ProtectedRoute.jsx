import { Navigate, Outlet } from "react-router-dom";
import { useStaffAuth } from "../context/StaffAuthContext";

export default function ProtectedRoute() {
  const { staff, loading } = useStaffAuth();

  if (loading) return <div className="center-page">Cargando...</div>;
  if (!staff) return <Navigate to="/recepcion/login" replace />;

  return <Outlet />;
}
