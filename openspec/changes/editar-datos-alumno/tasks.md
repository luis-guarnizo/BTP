# Tasks

## 1. Backend: serializer y vistas de alumnos

- [x] 1.1 Crear `StudentStaffSerializer` en `backend/apps/accounts/serializers.py` (campos de staff + `pin` opcional de solo escritura que llama `set_pin` solo si trae valor) y agregar el `UniqueValidator` con el mensaje "Ya existe un alumno con este teléfono." también en `StudentRegisterSerializer`; verificar con `python manage.py check`
- [x] 1.2 Usar `StudentStaffSerializer` en el GET de `StudentListCreateView` y en `StudentDetailView`, limitando esta a `get`/`patch`/`options`; dejar `CheckinLoginView` y `CheckinMeView` con `StudentPublicSerializer`
- [x] 1.3 Tests en `backend/apps/accounts/tests.py`: recepcionista y admin editan nombre/apellido/teléfono/correo/cédula/categoría; anónimo → 403; teléfono repetido → 400 con el mensaje en español y sin cambios; nombre/apellido/teléfono vacío → 400; correo inválido → 400; PIN nuevo "5678" permite `checkin-login` con él y rechaza el anterior; PIN vacío lo mantiene; PIN de 3 caracteres → 400; el listado y el detalle no incluyen `pin` ni `pin_hash`; tras cambiar el teléfono el login de check-in acepta el nuevo y rechaza el viejo; `PUT` → 405; `checkin-me` no expone `document_id`. Verificar con `python manage.py test`

## 2. Frontend: pantalla de Alumnos

- [x] 2.1 En `frontend/src/pages/staff/StudentsPage.jsx` agregar `formatErrors` para mostrar errores por campo en español y usarlo en registrar y editar; verificar en el navegador que registrar un teléfono repetido muestra "Teléfono: Ya existe un alumno con este teléfono."
- [x] 2.2 Agregar columna "Cédula", botón "Editar" por fila y la tarjeta "Editar alumno" (campos precargados, "PIN nuevo (opcional)", Guardar/Cancelar) que envía `PATCH /accounts/students/<id>/`, muestra éxito y recarga; verificar en el navegador que editar nombre y apellido se refleja en el listado y que Cancelar no cambia nada
- [x] 2.3 Verificar en el navegador a 375px que la tarjeta de edición se ve completa y que al abrirla la página se desplaza hasta ella
- [x] 2.4 Ejecutar `npm run lint` y `npm run build` en `frontend/` sin errores nuevos

## 3. Verificación integrada

- [x] 3.1 Con backend y frontend locales: como recepcionista cambiar teléfono y PIN de un alumno y comprobar en la página de check-in que entra con los datos nuevos y no con los anteriores; repetir una edición como administrador
- [x] 3.2 Ejecutar `openspec validate editar-datos-alumno --strict` sin errores

## Workflow follow-up

- Hacer commit y push a la rama de trabajo y abrir PR; desplegar cuando se apruebe.
- Archivar el cambio con `/opsx:archive` una vez desplegado y verificado.
