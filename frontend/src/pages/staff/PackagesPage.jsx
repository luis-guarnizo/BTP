import { useEffect, useState } from "react";
import { api } from "../../api/client";

export default function PackagesPage() {
  const [students, setStudents] = useState([]);
  const [packageTypes, setPackageTypes] = useState([]);
  const [packages, setPackages] = useState([]);
  const [form, setForm] = useState({ student: "", package_type: "", payment_method: "efectivo" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = () => {
    api.get("/accounts/students/").then((data) => setStudents(data.results ?? data));
    api.get("/packages/types/").then((data) => setPackageTypes(data.results ?? data));
    api.get("/packages/").then((data) => setPackages(data.results ?? data));
  };

  useEffect(load, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      await api.post("/packages/", form);
      setSuccess("Paquete/mensualidad registrado.");
      setForm({ student: "", package_type: "", payment_method: "efectivo" });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Vender / renovar paquete</h1>

      <form onSubmit={handleSubmit} className="grid-form">
        <label>
          Alumno
          <select
            required
            value={form.student}
            onChange={(e) => setForm({ ...form, student: e.target.value })}
          >
            <option value="">Selecciona...</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.first_name} {s.last_name} ({s.phone})
              </option>
            ))}
          </select>
        </label>
        <label>
          Plan
          <select
            required
            value={form.package_type}
            onChange={(e) => setForm({ ...form, package_type: e.target.value })}
          >
            <option value="">Selecciona...</option>
            {packageTypes.map((pt) => (
              <option key={pt.id} value={pt.id}>
                {pt.name} - ${Number(pt.price).toLocaleString()}
              </option>
            ))}
          </select>
        </label>
        <label>
          Forma de pago
          <select
            value={form.payment_method}
            onChange={(e) => setForm({ ...form, payment_method: e.target.value })}
          >
            <option value="efectivo">Efectivo</option>
            <option value="transferencia">Transferencia</option>
          </select>
        </label>
        <button type="submit" className="btn btn-primary">
          Registrar pago
        </button>
      </form>
      {error && <div className="error-text">{error}</div>}
      {success && <div className="success-text">{success}</div>}

      <h2>Últimos paquetes</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Alumno</th>
            <th>Plan</th>
            <th>Compra</th>
            <th>Vence</th>
            <th>Créditos</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {packages.map((p) => (
            <tr key={p.id}>
              <td>{p.student}</td>
              <td>{p.package_type_name}</td>
              <td>{p.purchase_date}</td>
              <td>{p.expires_at}</td>
              <td>{p.credits_remaining ?? "Ilimitado"}</td>
              <td>{p.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
