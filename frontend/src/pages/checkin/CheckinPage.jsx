import { useEffect, useState } from "react";
import { api } from "../../api/client";

function PackageStatusCard({ pkg }) {
  if (!pkg) {
    return (
      <div className="card card-warning">
        <strong>No tienes un paquete activo.</strong>
        <p>Pasa por recepción para comprar tu paquete o mensualidad.</p>
      </div>
    );
  }

  const isUnlimited = pkg.credits_remaining === null;
  const statusLabel = { activo: "Activo", vencido: "Vencido", agotado: "Agotado" }[pkg.status];
  const cardClass = pkg.is_usable ? "card card-ok" : "card card-warning";

  return (
    <div className={cardClass}>
      <div className="card-row">
        <span>Paquete</span>
        <strong>{pkg.package_type_name}</strong>
      </div>
      <div className="card-row">
        <span>Estado</span>
        <strong>{statusLabel}</strong>
      </div>
      {!isUnlimited && (
        <div className="card-row">
          <span>Clases restantes</span>
          <strong>{pkg.credits_remaining}</strong>
        </div>
      )}
      <div className="card-row">
        <span>Vence</span>
        <strong>{pkg.expires_at}</strong>
      </div>
    </div>
  );
}

export default function CheckinPage() {
  const [phase, setPhase] = useState("loading");
  const [me, setMe] = useState(null);
  const [classes, setClasses] = useState([]);
  const [form, setForm] = useState({ phone: "", pin: "" });
  const [loginError, setLoginError] = useState("");
  const [checkinResult, setCheckinResult] = useState(null);
  const [busyClassId, setBusyClassId] = useState(null);

  const loadMe = async () => {
    const data = await api.get("/accounts/me/");
    setMe(data);
    setPhase(data.authenticated ? "checkin" : "login");
    if (data.authenticated) {
      const list = await api.get("/classes/today/");
      setClasses(list.results ?? list);
    }
  };

  useEffect(() => {
    loadMe().catch(() => setPhase("login"));
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError("");
    try {
      await api.post("/accounts/checkin-login/", form);
      await loadMe();
    } catch (err) {
      setLoginError(err.message);
    }
  };

  const handleLogout = async () => {
    await api.post("/accounts/checkin-logout/");
    setMe(null);
    setForm({ phone: "", pin: "" });
    setCheckinResult(null);
    setPhase("login");
  };

  const handleCheckin = async (classOffering) => {
    setBusyClassId(classOffering.id);
    setCheckinResult(null);
    try {
      const result = await api.post("/attendance/checkin/", {
        class_offering_id: classOffering.id,
      });
      setCheckinResult({ ok: true, className: classOffering.name, ...result });
      const refreshed = await api.get("/accounts/me/");
      setMe(refreshed);
    } catch (err) {
      setCheckinResult({ ok: false, message: err.message, reason: err.data?.reason });
    } finally {
      setBusyClassId(null);
    }
  };

  if (phase === "loading") {
    return <div className="center-page">Cargando...</div>;
  }

  if (phase === "login") {
    return (
      <div className="checkin-page">
        <h1>Bachatea Team Project</h1>
        <p className="subtitle">Ingresa con tu teléfono y PIN para registrar tu asistencia.</p>
        <form onSubmit={handleLogin} className="stack-form">
          <label>
            Teléfono
            <input
              type="tel"
              required
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              placeholder="3001234567"
            />
          </label>
          <label>
            PIN
            <input
              type="password"
              inputMode="numeric"
              required
              value={form.pin}
              onChange={(e) => setForm({ ...form, pin: e.target.value })}
              placeholder="****"
            />
          </label>
          {loginError && <div className="error-text">{loginError}</div>}
          <button type="submit" className="btn btn-primary btn-big">
            Ingresar
          </button>
        </form>
        <p className="hint">¿Primera vez? Recepción te asigna tu PIN al registrarte.</p>
      </div>
    );
  }

  return (
    <div className="checkin-page">
      <h1>Hola, {me.student.first_name} 👋</h1>
      <PackageStatusCard pkg={me.package} />

      <h2>Clases de hoy</h2>
      {classes.length === 0 && <p>No hay clases programadas para hoy.</p>}
      <div className="class-list">
        {classes.map((c) => (
          <button
            key={c.id}
            className="btn btn-class"
            disabled={busyClassId === c.id}
            onClick={() => handleCheckin(c)}
          >
            <span className="class-name">{c.name}</span>
            <span className="class-time">
              {c.start_time.slice(0, 5)} - {c.end_time.slice(0, 5)} · {c.room}
            </span>
          </button>
        ))}
      </div>

      {checkinResult && (
        <div className={`card ${checkinResult.ok ? "card-ok" : "card-warning"}`}>
          {checkinResult.ok ? (
            <>
              <strong>¡Asistencia registrada en {checkinResult.className}!</strong>
              {checkinResult.credit_deducted && (
                <p>Te quedan {checkinResult.credits_remaining} clase(s).</p>
              )}
            </>
          ) : (
            <strong>{checkinResult.message}</strong>
          )}
        </div>
      )}

      <button className="btn btn-link" onClick={handleLogout}>
        Cerrar sesión
      </button>
    </div>
  );
}
