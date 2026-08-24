import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStaffAuth } from "../../context/StaffAuthContext";

export default function StaffLoginPage() {
  const { login } = useStaffAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(form.username, form.password);
      navigate("/recepcion");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="checkin-page">
      <h1>Recepción</h1>
      <p className="subtitle">Ingresa con tu usuario de administración.</p>
      <form onSubmit={handleSubmit} className="stack-form">
        <label>
          Usuario
          <input
            required
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </label>
        {error && <div className="error-text">{error}</div>}
        <button type="submit" className="btn btn-primary btn-big">
          Ingresar
        </button>
      </form>
    </div>
  );
}
