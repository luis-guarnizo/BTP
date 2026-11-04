# Design

## Context

- Ya existe `PATCH /api/accounts/students/<id>/` (`StudentDetailView`, `RetrieveUpdateAPIView`, permiso `IsReceptionistOrAdmin`), pero usa `StudentPublicSerializer`: no incluye cédula ni PIN, y el frontend no lo usa.
- `StudentPublicSerializer` también lo usan `CheckinLoginView` y `CheckinMeView` (lo que el alumno ve de sí mismo), así que no conviene ampliarlo.
- El listado (`GET /api/accounts/students/`) también usa `StudentPublicSerializer`, por eso hoy no trae la cédula.
- `LANGUAGE_CODE = "es"`: los mensajes de validación por defecto de DRF/Django ya salen en español, salvo el de teléfono único, que usa el nombre del campo ("Alumno con este teléfono ya existe.").
- `api/client.js` arma el mensaje de error con `detail`/`message`; con errores por campo (400 de DRF) solo muestra "Error 400 al conectar con el servidor.".

## Goals / Non-Goals

**Goals:**
- Un serializer de staff único para listar y editar alumnos.
- Mensajes de error por campo visibles en la pantalla de Alumnos.

**Non-Goals:**
- Cambiar el flujo de registro, salvo reutilizar el mismo mensaje de teléfono repetido.
- Cerrar sesiones de check-in ya abiertas cuando cambia el teléfono o el PIN.

## Decisions

1. **`StudentStaffSerializer`** con `id, first_name, last_name, phone, email, document_id, category` y `pin` (`write_only`, `required=False`, `allow_blank=True`, 4–8 caracteres si no está vacío). En `update`, si `pin` viene con valor se llama `set_pin`; si viene vacío o no viene, se ignora. `pin_hash` nunca está en `fields`. *Alternativa:* endpoint aparte para el PIN; se descarta porque el formulario es uno solo y el permiso es el mismo.

2. **Mensaje de teléfono repetido** con `UniqueValidator(queryset=Student.objects.all(), message="Ya existe un alumno con este teléfono.")` en el campo `phone` del serializer de staff y también en `StudentRegisterSerializer`, para que registrar y editar digan lo mismo.

3. **Vistas.** `StudentListCreateView` usa `StudentStaffSerializer` en GET (POST sigue con `StudentRegisterSerializer`). `StudentDetailView` usa `StudentStaffSerializer` y limita métodos a `get`, `patch`, `options` (sin `PUT`, que exigiría mandar todo). Permiso sin cambios: admin y recepcionista.

4. **Errores en el frontend.** En `StudentsPage.jsx` una función `formatErrors(err)` convierte `err.data` (objeto campo → lista de mensajes) en texto legible usando etiquetas en español ("Teléfono: Ya existe…"); si no hay `data` por campo, usa `err.message`. Se usa tanto en registrar como en editar. *Alternativa:* cambiar `api/client.js` para todas las pantallas; se descarta para no tocar comportamiento de otras pantallas en este cambio.

5. **Formulario de edición.** Botón "Editar" por fila. Al pulsarlo aparece, encima del listado, una tarjeta "Editar alumno" (reutiliza `.grid-form`) con los campos precargados y un campo "PIN nuevo (opcional)" vacío; botones Guardar y Cancelar. Se envía `PATCH` con todos los campos del formulario (y `pin` solo si tiene valor), se muestra el mensaje de éxito, se cierra y se recarga el listado. La página hace scroll a la tarjeta al abrirla, para que se vea en celular. *Alternativa:* edición en línea en la tabla; se descarta porque son 7 campos y en celular no cabe.

6. **Listado** agrega la columna "Cédula" y una columna de acciones con el botón "Editar".

## Risks / Trade-offs

- [Cambiar la categoría no cambia los paquetes ya vendidos] → Fuera de alcance; el vencimiento depende del plan vendido, no de la categoría del alumno. Se informa en la propuesta.
- [Cambiar el teléfono o el PIN no cierra la sesión de check-in ya abierta en el celular del alumno] → Aceptado: la sesión guarda el id del alumno, no el teléfono; el alumno sigue siendo el mismo.
- [Dos personas editando el mismo alumno a la vez: gana el último que guarda] → Aceptado por el volumen de uso de la academia.

## Migration Plan

- Sin migración de base de datos. Deploy normal (Render + Vercel). Rollback: revertir el commit.
