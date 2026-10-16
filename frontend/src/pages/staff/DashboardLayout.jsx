import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useStaffAuth } from "../../context/StaffAuthContext";

const links = [
  { to: "/recepcion/alertas", label: "Alertas" },
  { to: "/recepcion/alumnos", label: "Alumnos" },
  { to: "/recepcion/paquetes", label: "Paquetes" },
  { to: "/recepcion/horario", label: "Horario" },
  { to: "/recepcion/reportes", label: "Reportes" },
  { to: "/recepcion/qr", label: "Código QR" },
];

export default function DashboardLayout() {
  const { staff, logout } = useStaffAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/recepcion/login");
  };

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div>
            <h2>Bachatea Team Project</h2>
            <span className="sidebar-user">{staff?.username}</span>
          </div>
          {/* En celular el botón vive aquí, compacto, en vez de la barra superior. */}
          <button className="btn btn-logout-compact" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
        <nav>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="dashboard-content">
        <header className="topbar">
          <span className="topbar-user">{staff?.username}</span>
          <button className="btn btn-logout" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
