# Proposal

## Why

En recepción a veces se olvida registrar la venta de un paquete el mismo día del pago. Hoy la fecha de compra siempre queda como "hoy" y no se puede corregir desde el panel, así que el vencimiento queda mal calculado y el alumno puede quedar bloqueado antes o después de tiempo. Además, el botón "Cerrar sesión" del panel de recepción existe pero queda escondido al final del menú lateral y no se nota.

## What Changes

- Al vender/renovar un paquete, el recepcionista puede elegir la fecha de compra. Por defecto es la fecha de hoy; solo se cambia en casos especiales (p. ej. registrar al día siguiente una venta olvidada).
- El recepcionista puede editar la fecha de compra de un paquete ya vendido desde la tabla de paquetes. Al guardar, el sistema recalcula la fecha de vencimiento con base en la nueva fecha de compra.
- La fecha de vencimiento se recalcula siempre que cambie la fecha de compra, también si se edita desde el admin de Django.
- **BREAKING** (regla de negocio): los paquetes de Líneas pasan a vencer el día 5 del mes siguiente al mes de compra (antes: último día del mes de compra). Ej.: compra el 3, 5 o 20 de septiembre → vence el 5 de octubre. Social no cambia (compra + 30 días).
- El botón "Cerrar sesión" del panel de recepción pasa a estar siempre visible en la parte superior del panel, junto al nombre del usuario.

Fuera de alcance: validar que la fecha de compra no sea futura, registrar quién editó la fecha (auditoría), cambiar créditos o plan de un paquete ya vendido, y el cierre de sesión del check-in de alumnos (ya existe y no cambia).

## Capabilities

### New Capabilities
- `package-validity`: fecha de compra de un paquete (elegirla al vender, editarla después) y cómo se calcula su fecha de vencimiento según la categoría.
- `staff-session`: cierre de sesión del personal de recepción en el panel.

### Modified Capabilities
<!-- No hay specs existentes en openspec/specs/; todo es nuevo. -->

## Impact

- Backend `apps/packages`: modelo `Package` (cálculo de vencimiento y recálculo al cambiar la compra), serializers y un nuevo endpoint `PATCH /api/packages/<id>/` restringido a recepción/admin.
- Frontend `PackagesPage.jsx`: campo de fecha en el formulario de venta y edición de fecha en la tabla; `DashboardLayout.jsx` y `styles.css`: barra superior con "Cerrar sesión".
- Alertas de vencimiento (`check_expirations`) y check-in usan `expires_at`, así que reflejan automáticamente el nuevo vencimiento.
- Paquetes de Líneas existentes no se recalculan automáticamente; los del registro inicial ya están en compra 5 sept → vence 5 oct, que coincide con la nueva regla.
- Sin migración de base de datos.
