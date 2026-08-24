import { useEffect, useState } from "react";
import { api } from "../../api/client";

export default function ReportsPage() {
  const [revenue, setRevenue] = useState([]);
  const [students, setStudents] = useState(null);
  const [attendance, setAttendance] = useState([]);

  useEffect(() => {
    api.get("/reports/revenue/").then(setRevenue);
    api.get("/reports/students/").then(setStudents);
    api.get("/reports/attendance/").then(setAttendance);
  }, []);

  return (
    <div>
      <h1>Reportes</h1>

      <h2>Alumnos</h2>
      {students && (
        <div className="stats-grid">
          <div className="stat-box">
            <span>Total</span>
            <strong>{students.total_alumnos}</strong>
          </div>
          <div className="stat-box stat-ok">
            <span>Activos</span>
            <strong>{students.activos}</strong>
          </div>
          <div className="stat-box stat-warning">
            <span>Vencidos</span>
            <strong>{students.vencidos}</strong>
          </div>
          <div className="stat-box stat-warning">
            <span>Agotados</span>
            <strong>{students.agotados}</strong>
          </div>
          <div className="stat-box">
            <span>Sin paquete</span>
            <strong>{students.sin_paquete}</strong>
          </div>
        </div>
      )}

      <h2>Ingresos por mes / categoría</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Mes</th>
            <th>Categoría</th>
            <th>Ventas</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {revenue.map((r, i) => (
            <tr key={i}>
              <td>{r.month?.slice(0, 10)}</td>
              <td>{r.package_type__category === "social" ? "Social" : "Líneas"}</td>
              <td>{r.sales}</td>
              <td>${Number(r.total).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Clases más populares</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Clase</th>
            <th>Asistencias totales</th>
          </tr>
        </thead>
        <tbody>
          {attendance.map((a, i) => (
            <tr key={i}>
              <td>{a.name}</td>
              <td>{a.total_asistencias}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
