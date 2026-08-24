import { useEffect, useState } from "react";
import { api } from "../../api/client";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState(null);
  const [error, setError] = useState("");

  const load = () => {
    api
      .get("/reports/alerts/")
      .then(setAlerts)
      .catch((err) => setError(err.message));
  };

  useEffect(load, []);

  const resolve = async (id) => {
    await api.post(`/reports/alerts/${id}/resolve/`);
    load();
  };

  return (
    <div>
      <h1>Alertas pendientes</h1>
      <p className="subtitle">
        Alumnos que agotaron o vencieron su paquete/mensualidad: cóbrales la clase suelta o
        renuévales el plan.
      </p>
      {error && <div className="error-text">{error}</div>}
      {alerts && alerts.length === 0 && <p>No hay alertas pendientes. 🎉</p>}
      <table className="table">
        <tbody>
          {alerts?.map((a) => (
            <tr key={a.id}>
              <td>
                <strong>{a.student}</strong>
                <div className="muted">{a.type}</div>
                <div className="muted">{a.message}</div>
              </td>
              <td>{new Date(a.sent_at).toLocaleString()}</td>
              <td>
                <button className="btn btn-primary" onClick={() => resolve(a.id)}>
                  Marcar resuelto
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
