import { Navigate, Route, Routes } from "react-router-dom";
import { StaffAuthProvider } from "./context/StaffAuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import CheckinPage from "./pages/checkin/CheckinPage";
import StaffLoginPage from "./pages/staff/StaffLoginPage";
import DashboardLayout from "./pages/staff/DashboardLayout";
import AlertsPage from "./pages/staff/AlertsPage";
import StudentsPage from "./pages/staff/StudentsPage";
import PackagesPage from "./pages/staff/PackagesPage";
import SchedulePage from "./pages/staff/SchedulePage";
import ReportsPage from "./pages/staff/ReportsPage";
import QrPage from "./pages/staff/QrPage";

export default function App() {
  return (
    <StaffAuthProvider>
      <Routes>
        <Route path="/" element={<CheckinPage />} />

        <Route path="/recepcion/login" element={<StaffLoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/recepcion" element={<DashboardLayout />}>
            <Route index element={<Navigate to="alertas" replace />} />
            <Route path="alertas" element={<AlertsPage />} />
            <Route path="alumnos" element={<StudentsPage />} />
            <Route path="paquetes" element={<PackagesPage />} />
            <Route path="horario" element={<SchedulePage />} />
            <Route path="reportes" element={<ReportsPage />} />
            <Route path="qr" element={<QrPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </StaffAuthProvider>
  );
}
