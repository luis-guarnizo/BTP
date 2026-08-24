import { useRef, useState } from "react";
import { QRCodeCanvas } from "qrcode.react";

export default function QrPage() {
  const [url, setUrl] = useState(window.location.origin + "/");
  const canvasRef = useRef(null);

  const download = () => {
    const canvas = canvasRef.current?.querySelector("canvas");
    if (!canvas) return;
    const link = document.createElement("a");
    link.download = "qr-check-in.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  };

  return (
    <div>
      <h1>Código QR para imprimir</h1>
      <p className="subtitle">
        Este es el QR fijo que pegas en la entrada del salón. Cualquier alumno lo escanea con la
        cámara de su celular, ingresa con su teléfono y PIN, y elige la clase a la que está
        asistiendo.
      </p>

      <label>
        URL del check-in (cámbiala si publicas el sitio en un dominio propio)
        <input value={url} onChange={(e) => setUrl(e.target.value)} style={{ width: "100%" }} />
      </label>

      <div className="qr-preview" ref={canvasRef}>
        <QRCodeCanvas value={url} size={280} includeMargin />
      </div>

      <button className="btn btn-primary" onClick={download}>
        Descargar PNG para imprimir
      </button>
    </div>
  );
}
