import { useEffect, useRef, useState } from "react";
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

const fieldLabels = {
  first_name: "Nombres",
  last_name: "Apellidos",
  phone: "Teléfono",
  email: "Correo",
  document_id: "Cédula",
  category: "Categoría",
  pin: "PIN",
};

// DRF responde los errores de validación como { campo: ["mensaje", ...] };
// los mostramos como "Teléfono: Ya existe un alumno con este teléfono.".
function formatErrors(err) {
  const data = err.data;
  if (!data || typeof data !== "object" || data.detail) return err.message;
  return Object.entries(data)
    .map(([field, messages]) => {
      const text = [].concat(messages).join(" ");
      return fieldLabels[field] ? `${fieldLabels[field]}: ${text}` : text;
    })
    .join(" ");
}

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  // Alumno que se está editando (copia de sus datos + PIN nuevo opcional).
  const [editing, setEditing] = useState(null);
  const [editError, setEditError] = useState("");
  const editCardRef = useRef(null);

  const load = () => {
    api.get("/accounts/students/").then((data) => setStudents(data.results ?? data));
  };

  useEffect(load, []);

  // Al abrir la edición, llevar la tarjeta a la vista (en celular queda
  // lejos de la fila pulsada).
  const editingId = editing?.id;
  useEffect(() => {
    const card = editCardRef.current;
    if (!editingId || !card) return;
    // Solo desplazamiento vertical: scrollIntoView también movería en
    // horizontal el contenido (la tabla es más ancha que el celular).
    const top = card.getBoundingClientRect().top + window.scrollY - 16;
    window.scrollTo({ top, behavior: "smooth" });
  }, [editingId]);

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
      setError(formatErrors(err));
    }
  };

  const startEditing = (student) => {
    setError("");
    setSuccess("");
    setEditError("");
    setEditing({
      id: student.id,
      first_name: student.first_name,
      last_name: student.last_name,
      phone: student.phone,
      email: student.email ?? "",
      document_id: student.document_id ?? "",
      category: student.category,
      pin: "",
    });
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setEditError("");
    const { id, pin, ...fields } = editing;
    try {
      const updated = await api.patch(`/accounts/students/${id}/`, pin ? { ...fields, pin } : fields);
      setSuccess(
        `Datos de ${updated.first_name} ${updated.last_name} actualizados.` +
          (pin ? ` PIN nuevo: ${pin}` : "")
      );
      setEditing(null);
      load();
    } catch (err) {
      setEditError(formatErrors(err));
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

      {editing && (
        <div ref={editCardRef} className="edit-card">
          <h2>Editar alumno</h2>
          <form onSubmit={handleEditSubmit} className="grid-form">
            <label>
              Nombres
              <input
                required
                value={editing.first_name}
                onChange={(e) => setEditing({ ...editing, first_name: e.target.value })}
              />
            </label>
            <label>
              Apellidos
              <input
                required
                value={editing.last_name}
                onChange={(e) => setEditing({ ...editing, last_name: e.target.value })}
              />
            </label>
            <label>
              Teléfono
              <input
                required
                value={editing.phone}
                onChange={(e) => setEditing({ ...editing, phone: e.target.value })}
              />
            </label>
            <label>
              Correo
              <input
                type="email"
                value={editing.email}
                onChange={(e) => setEditing({ ...editing, email: e.target.value })}
              />
            </label>
            <label>
              Cédula
              <input
                value={editing.document_id}
                onChange={(e) => setEditing({ ...editing, document_id: e.target.value })}
              />
            </label>
            <label>
              Categoría
              <select
                value={editing.category}
                onChange={(e) => setEditing({ ...editing, category: e.target.value })}
              >
                <option value="social">Social</option>
                <option value="lineas">Líneas (artístico)</option>
              </select>
            </label>
            <label>
              PIN nuevo (opcional)
              <input
                minLength={4}
                maxLength={8}
                placeholder="Dejar vacío para no cambiarlo"
                value={editing.pin}
                onChange={(e) => setEditing({ ...editing, pin: e.target.value })}
              />
            </label>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                Guardar
              </button>
              <button type="button" className="btn btn-small" onClick={() => setEditing(null)}>
                Cancelar
              </button>
            </div>
          </form>
          {editError && <div className="error-text">{editError}</div>}
        </div>
      )}

      <h2>Listado</h2>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              {/* Primera columna para que "Editar" se vea en celular sin deslizar. */}
              <th></th>
              <th>Nombre</th>
              <th>Teléfono</th>
              <th>Correo</th>
              <th>Cédula</th>
              <th>Categoría</th>
            </tr>
          </thead>
          <tbody>
            {students.map((s) => (
              <tr key={s.id}>
                <td className="row-actions">
                  <button className="btn btn-small" onClick={() => startEditing(s)}>
                    Editar
                  </button>
                </td>
                <td>
                  {s.first_name} {s.last_name}
                </td>
                <td>{s.phone}</td>
                <td>{s.email}</td>
                <td>{s.document_id}</td>
                <td>{s.category === "social" ? "Social" : "Líneas"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
