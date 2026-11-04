# Proposal

## Why

En la pantalla "Alumnos" del panel solo se puede registrar alumnos y ver el listado; si un nombre quedó mal escrito, el teléfono cambió o el alumno olvidó su PIN, hoy no hay forma de corregirlo desde el panel (solo desde el admin de Django). Recepción y administración necesitan corregir estos datos sin depender del admin técnico.

## What Changes

- En el listado de "Alumnos" cada fila tendrá un botón "Editar" que abre un formulario con los datos del alumno.
- Admin y recepcionista podrán editar: nombres, apellidos, teléfono, correo, cédula y categoría (Social / Líneas).
- Se podrá restablecer el PIN del alumno escribiendo uno nuevo; si se deja vacío, el PIN no cambia. El PIN actual nunca se muestra.
- Validaciones: nombres, apellidos y teléfono obligatorios; el teléfono no puede repetirse con el de otro alumno; el PIN nuevo debe tener entre 4 y 8 caracteres. Los errores se muestran en español junto al formulario.
- El listado mostrará también la cédula, para poder verificarla y editarla.

Fuera de alcance: desactivar o eliminar alumnos, editar los paquetes del alumno al cambiar su categoría, historial de cambios (quién editó qué).

## Capabilities

### New Capabilities
- `student-records`: datos de los alumnos en el panel de recepción (consultarlos y corregirlos, incluido restablecer el PIN).

### Modified Capabilities
<!-- Ninguna: package-validity y staff-session no cambian. -->

## Impact

- Backend `apps/accounts`: nuevo serializer de staff para listar/editar alumnos (incluye cédula y PIN opcional de solo escritura); `StudentListCreateView` (GET) y `StudentDetailView` lo usan. El endpoint `PATCH /api/accounts/students/<id>/` ya existe y ya exige recepción/admin; cambia lo que acepta.
- `CheckinMeView`/`CheckinLoginView` siguen usando `StudentPublicSerializer` sin cambios (el alumno no ve su cédula ni nada nuevo).
- Frontend `StudentsPage.jsx`: botón "Editar", formulario de edición y manejo de errores por campo; `styles.css` si hace falta.
- Si se cambia el teléfono, el alumno debe usar el número nuevo para entrar al check-in; su sesión ya abierta en el celular sigue funcionando.
- Sin migración de base de datos.
