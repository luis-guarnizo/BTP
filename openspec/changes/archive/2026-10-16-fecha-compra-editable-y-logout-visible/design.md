# Design

## Context

- `Package.save()` calcula `expires_at` solo al crear (`_state.adding`). Si luego cambia `purchase_date` (admin de Django o el comando `fix_initial_package_dates`), el vencimiento no se recalcula solo.
- `PackageCreateSerializer` ya acepta `purchase_date`, pero `PackagesPage.jsx` no lo envía, así que siempre queda el default `timezone.localdate`.
- No hay endpoint de detalle de paquete: `apps/packages/urls.py` solo expone el listado/creación y los tipos.
- `Student.active_package()` elige el paquete "actual" ordenando por `-purchase_date`, y el check-in y `check_expirations` dependen de eso.
- El logout de staff (`POST /api/accounts/staff-logout/` + `StaffAuthContext.logout`) ya funciona; solo el botón está al final del sidebar, sin estilos responsive.
- El repo no tiene tests todavía (ni backend ni frontend).

## Goals / Non-Goals

**Goals:**
- Una sola regla de vencimiento en el modelo, aplicada al crear y cada vez que cambia la fecha de compra.
- Endpoint mínimo para editar solo la fecha de compra.
- Primeros tests del backend para la regla de vencimiento y el endpoint.

**Non-Goals:**
- Recalcular en lote los paquetes de Líneas ya existentes.
- Historial/auditoría de ediciones.
- Rediseñar la navegación del panel.

## Decisions

1. **Recalcular en `Package.save()` cuando cambia `purchase_date`.** Se guarda la fecha de compra original al cargar la instancia (`from_db`/`__init__`) y en `save()` se recalcula `expires_at` si es nuevo o si la fecha cambió; si se pasa `update_fields` con `purchase_date`, se agrega `expires_at`. Así cubre la API, el admin y cualquier script. *Alternativa:* recalcular solo en el serializer de edición; se descarta porque el admin seguiría dejando vencimientos incorrectos.
   - `consume_credit()` usa `update_fields=["credits_remaining"]` y no toca la fecha, así que no se ve afectado.
   - `QuerySet.update()` (como en `fix_initial_package_dates`) no pasa por `save()`; ese comando ya fija ambos campos a mano, se deja igual.

2. **Regla de Líneas: día 5 del mes siguiente.** En `_compute_expiry`, para Líneas: mes de compra + 1 (con salto de año en diciembre) y día = `settings.LINEAS_EXPIRY_DAY` (nuevo setting, por defecto 5, con el mismo patrón que `SOCIAL_PACKAGE_VALIDITY_DAYS`). Se usa solo aritmética de mes/año, sin dependencias nuevas. *Alternativa:* `dateutil.relativedelta`; se descarta para no añadir dependencia.

3. **Endpoint `PATCH /api/packages/<id>/`.** `generics.UpdateAPIView` (solo `PATCH`; `PUT` deshabilitado vía `http_method_names`) con permiso `IsReceptionistOrAdmin` y un `PackagePurchaseDateSerializer` cuyo único campo escribible es `purchase_date` (requerido). La respuesta usa `PackageStatusSerializer` para que el frontend reciba el `expires_at` y `status` nuevos. *Alternativa:* hacer el serializer de creación editable; se descarta para no permitir cambiar alumno/plan/pago.

4. **Desempate de `active_package()`.** Al poder retroceder fechas, dos paquetes pueden quedar con la misma `purchase_date`. Se ordena por `("-purchase_date", "-created_at")` para que gane el más reciente registrado, de forma determinista. Mismo orden en el listado de `PackageListCreateView`.

5. **Frontend de venta.** `PackagesPage.jsx` agrega un `<input type="date">` con valor inicial = fecha local de hoy (calculada en el navegador con `toLocaleDateString("en-CA")` → `YYYY-MM-DD`) y lo envía como `purchase_date`. Al resetear el formulario vuelve a hoy.

6. **Frontend de edición.** En la tabla "Últimos paquetes" cada fila tiene un botón "Editar fecha" que cambia la celda de compra por un `<input type="date">` con Guardar/Cancelar. Al guardar hace `api.patch(`/packages/${id}/`, { purchase_date })`, muestra el mensaje de éxito/error existente y recarga el listado. *Alternativa:* un modal; se descarta por ser más código sin necesidad.

7. **Logout visible.** `DashboardLayout.jsx` agrega una barra superior (`.topbar`) dentro de `.dashboard-content`, con el usuario y un botón "Cerrar sesión" con estilo de botón (no enlace). El botón del final del sidebar se quita. En pantallas angostas (`@media (max-width: 768px)`) el menú pasa arriba, la barra superior se oculta y en su lugar se muestra un botón compacto a la derecha del título del menú, con el usuario debajo del título, para no ocupar una fila propia.

## Risks / Trade-offs

- [Cambio de regla de Líneas afecta ventas nuevas desde el deploy] → Es lo pedido; los paquetes existentes se dejan como están y se recalculan solo si alguien edita su fecha.
- [Editar la fecha de un paquete viejo puede cambiar cuál es el "activo" del alumno] → Desempate determinista (decisión 4); la tabla muestra compra y vencimiento para verificarlo.
- [Alertas de vencimiento ya creadas pueden quedar desactualizadas tras editar] → Aceptado; `check_expirations` solo crea alertas nuevas sobre el estado actual.
- [Fecha de "hoy" calculada en el navegador puede diferir de la del servidor cerca de medianoche si el equipo tiene otra zona horaria] → Riesgo bajo (recepción está en Bogotá); el recepcionista ve y puede cambiar la fecha.

## Migration Plan

- Sin migración de base de datos (`expires_at` sigue siendo `editable=False` y se calcula en `save()`).
- Deploy normal: push → Render (backend) y Vercel (frontend). Opcional: definir `LINEAS_EXPIRY_DAY` en Render; por defecto 5.
- Rollback: revertir el commit; los datos editados mantienen fechas válidas.
