import { useEffect, useState } from "react";
import { api } from "../../api/client";

const weekdays = [
  "Lunes",
  "Martes",
  "Miércoles",
  "Jueves",
  "Viernes",
  "Sábado",
  "Domingo",
];

const emptyForm = {
  name: "",
  weekday: 0,
  start_time: "18:00",
  end_time: "19:00",
  room: "Salón principal",
  instructor_name: "",
};

export default function SchedulePage() {
  const [classes, setClasses] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");

  const load = () => {
    api.get("/classes/").then((data) => setClasses(data.results ?? data));
  };

  useEffect(load, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/classes/", form);
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Horario de clases</h1>

      <form onSubmit={handleSubmit} className="grid-form">
        <label>
          Nombre
          <input
            required
            placeholder="Salsa, Bachata..."
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </label>
        <label>
          Día
          <select
            value={form.weekday}
            onChange={(e) => setForm({ ...form, weekday: Number(e.target.value) })}
          >
            {weekdays.map((w, i) => (
              <option key={i} value={i}>
                {w}
              </option>
            ))}
          </select>
        </label>
        <label>
          Hora inicio
          <input
            type="time"
            value={form.start_time}
            onChange={(e) => setForm({ ...form, start_time: e.target.value })}
          />
        </label>
        <label>
          Hora fin
          <input
            type="time"
            value={form.end_time}
            onChange={(e) => setForm({ ...form, end_time: e.target.value })}
          />
        </label>
        <label>
          Salón
          <input
            value={form.room}
            onChange={(e) => setForm({ ...form, room: e.target.value })}
          />
        </label>
        <label>
          Instructor
          <input
            value={form.instructor_name}
            onChange={(e) => setForm({ ...form, instructor_name: e.target.value })}
          />
        </label>
        <button type="submit" className="btn btn-primary">
          Agregar clase
        </button>
      </form>
      {error && <div className="error-text">{error}</div>}

      <table className="table">
        <thead>
          <tr>
            <th>Clase</th>
            <th>Día</th>
            <th>Horario</th>
            <th>Salón</th>
            <th>Instructor</th>
          </tr>
        </thead>
        <tbody>
          {classes.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.weekday_label}</td>
              <td>
                {c.start_time.slice(0, 5)} - {c.end_time.slice(0, 5)}
              </td>
              <td>{c.room}</td>
              <td>{c.instructor_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
