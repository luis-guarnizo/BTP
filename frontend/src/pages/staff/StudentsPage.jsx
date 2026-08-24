import { useEffect, useState } from "react";
import { api } from "../../api/client";

const emptyForm = {
  first_name: "",
  last_name: "",
  phone: "",
  email: "",
  document_id: "",
  category: "social",
  pin: "",
};

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = () => {
    api.get("/accounts/students/").then((data) => setStudents(data.results ?? data));
  };

  useEffect(load, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      await api.post("/accounts/students/", form);
      setSuccess(`Alumno registrado. PIN asignado: ${form.pin}`);
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Alumnos</h1>

      <form onSubmit={handleSubmit} className="grid-form">
        <label>
          Nombres
          <input
            required
            value={form.first_name}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })}
          />
        </label>
        <label>
          Apellidos
          <input
            required
            value={form.last_name}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })}
          />
        </label>
        <label>
          Teléfono
          <input
            required
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
          />
        </label>
        <label>
          Correo
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </label>
        <label>
          Cédula
          <input
            value={form.document_id}
            onChange={(e) => setForm({ ...form, document_id: e.target.value })}
          />
        </label>
        <label>
          Categoría
          <select
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
          >
            <option value="social">Social</option>
            <option value="lineas">Líneas (artístico)</option>
          </select>
        </label>
        <label>
          PIN (4 dígitos)
          <input
            required
            minLength={4}
            maxLength={8}
            value={form.pin}
            onChange={(e) => setForm({ ...form, pin: e.target.value })}
          />
        </label>
        <button type="submit" className="btn btn-primary">
          Registrar alumno
        </button>
      </form>
      {error && <div className="error-text">{error}</div>}
      {success && <div className="success-text">{success}</div>}

      <h2>Listado</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Teléfono</th>
            <th>Correo</th>
            <th>Categoría</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr key={s.id}>
              <td>
                {s.first_name} {s.last_name}
              </td>
              <td>{s.phone}</td>
              <td>{s.email}</td>
              <td>{s.category === "social" ? "Social" : "Líneas"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
