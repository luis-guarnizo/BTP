# Spec Delta

## Purpose

Define cómo recepción y administración consultan y corrigen los datos de los alumnos en el panel, incluido el restablecimiento del PIN con el que el alumno hace check-in.

## ADDED Requirements

### Requirement: Editar datos del alumno
Recepción y administración SHALL poder editar desde el panel los nombres, apellidos, teléfono, correo, cédula y categoría de un alumno existente. Los cambios MUST verse en el listado de alumnos al guardar.

#### Scenario: Corregir nombre y apellido
- **WHEN** el recepcionista edita un alumno, cambia el nombre "Ana" por "Anna" y el apellido "Perez" por "Pérez" y guarda
- **THEN** el listado muestra "Anna Pérez" y el resto de sus datos sigue igual

#### Scenario: Administrador edita contacto y categoría
- **WHEN** el administrador cambia el correo, la cédula y la categoría de Social a Líneas de un alumno y guarda
- **THEN** el alumno queda con el nuevo correo, cédula y categoría Líneas

#### Scenario: Cancelar la edición
- **WHEN** el recepcionista abre la edición de un alumno, modifica campos y cancela
- **THEN** el alumno no cambia

#### Scenario: Usuario sin permisos
- **WHEN** alguien sin sesión de recepción o administración intenta editar un alumno
- **THEN** el sistema rechaza la petición y el alumno no cambia

### Requirement: Validación de los datos editados
Al editar un alumno, nombres, apellidos y teléfono MUST ser obligatorios y el teléfono MUST ser único entre alumnos. Si algo no es válido, el sistema SHALL rechazar el cambio completo y mostrar un mensaje en español que indique el problema.

#### Scenario: Teléfono repetido
- **WHEN** se cambia el teléfono de un alumno por uno que ya tiene otro alumno
- **THEN** el sistema rechaza el cambio con el mensaje "Ya existe un alumno con este teléfono." y el alumno no cambia

#### Scenario: Campo obligatorio vacío
- **WHEN** se deja vacío el nombre, el apellido o el teléfono y se guarda
- **THEN** el sistema rechaza el cambio, indica qué campo falta y el alumno no cambia

#### Scenario: Correo inválido
- **WHEN** se escribe un correo sin formato válido
- **THEN** el sistema rechaza el cambio e indica que el correo no es válido

### Requirement: Restablecer el PIN del alumno
Al editar un alumno, recepción y administración SHALL poder asignarle un PIN nuevo de 4 a 8 caracteres. Si el campo de PIN se deja vacío, el PIN actual MUST mantenerse. El PIN actual MUST NOT mostrarse ni devolverse nunca.

#### Scenario: Asignar un PIN nuevo
- **WHEN** el recepcionista escribe el PIN nuevo "5678" para un alumno y guarda
- **THEN** el alumno puede entrar al check-in con su teléfono y "5678", y ya no con su PIN anterior

#### Scenario: Editar sin tocar el PIN
- **WHEN** se edita el nombre de un alumno dejando vacío el campo de PIN
- **THEN** el alumno sigue entrando al check-in con su PIN anterior

#### Scenario: PIN demasiado corto
- **WHEN** se escribe un PIN nuevo de 3 caracteres
- **THEN** el sistema rechaza el cambio indicando que el PIN debe tener entre 4 y 8 caracteres

#### Scenario: El PIN no se expone
- **WHEN** el panel consulta el listado o el detalle de alumnos
- **THEN** la respuesta no incluye el PIN ni su valor cifrado

### Requirement: Teléfono nuevo para el check-in
Si se cambia el teléfono de un alumno, el check-in SHALL aceptar el teléfono nuevo y MUST rechazar el anterior.

#### Scenario: Ingreso con el teléfono nuevo
- **WHEN** se cambia el teléfono de un alumno de 3001112233 a 3009998877
- **THEN** el alumno entra al check-in con 3009998877 y su PIN, y con 3001112233 recibe "Teléfono o PIN incorrectos."
