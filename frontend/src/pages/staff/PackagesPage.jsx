import { useEffect, useState } from "react";
import { api } from "../../api/client";

// Fecha local de hoy en formato YYYY-MM-DD (el que usa <input type="date">).
const today = () => new Date().toLocaleDateString("en-CA");

const emptyForm = () => ({
  student: "",
  package_type: "",
  payment_method: "efectivo",
  purchase_date: today(),
});

export default function PackagesPage() {
  const [students, setStudents] = useState([]);
  const [packageTypes, setPackageTypes] = useState([]);
  const [packages, setPackages] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  // Paquete cuya fecha de compra se está corrigiendo en la tabla.
  const [editing, setEditing] = useState(null);

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
      setForm(emptyForm());
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSaveDate = async () => {
    setError("");
    setSuccess("");
    try {
      const updated = await api.patch(`/packages/${editing.id}/`, {
        purchase_date: editing.purchase_date,
      });
      setSuccess(
        `Fecha de compra actualizada para ${updated.student}: ahora vence el ${updated.expires_at}.`
      );
      setEditing(null);
      load();
    } catch (err) {
      setError(err.data?.purchase_date?.[0] || err.message);
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
        <label>
          Fecha de compra
          <input
            type="date"
            required
            value={form.purchase_date}
            onChange={(e) => setForm({ ...form, purchase_date: e.target.value })}
          />
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
            <th></th>
          </tr>
        </thead>
        <tbody>
          {packages.map((p) => {
            const isEditing = editing?.id === p.id;
            return (
              <tr key={p.id}>
                <td>{p.student}</td>
                <td>{p.package_type_name}</td>
                <td>
                  {isEditing ? (
                    <input
                      type="date"
                      required
                      value={editing.purchase_date}
                      onChange={(e) => setEditing({ ...editing, purchase_date: e.target.value })}
                    />
                  ) : (
                    p.purchase_date
                  )}
                </td>
                <td>{p.expires_at}</td>
                <td>{p.credits_remaining ?? "Ilimitado"}</td>
                <td>{p.status}</td>
                <td className="row-actions">
                  {isEditing ? (
                    <>
                      <button
                        className="btn btn-small btn-primary"
                        onClick={handleSaveDate}
                        disabled={!editing.purchase_date}
                      >
                        Guardar
                      </button>
                      <button className="btn btn-small" onClick={() => setEditing(null)}>
                        Cancelar
                      </button>
                    </>
                  ) : (
                    <button
                      className="btn btn-small"
                      onClick={() => setEditing({ id: p.id, purchase_date: p.purchase_date })}
                    >
                      Editar fecha
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
