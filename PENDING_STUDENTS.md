# Alumnos pendientes por agregar

Alumnos que aparecieron en los registros en papel pero **no se importaron**
porque falta el número de teléfono (campo obligatorio y único, se usa para
el check-in). En cuanto se consiga el número, agregarlos a
[import_students.py](backend/apps/accounts/management/commands/import_students.py)
y quitarlos de esta lista.

| Nombre | Línea | Nota |
|---|---|---|
| María Paula | Línea 3 Amateur | anotada como contacto de Isabella Rosero — falta su propio número |
| Maleja | Línea 3 Amateur | posible apodo de María Alejandra Cortés (esa sí se importó) — confirmar si es la misma persona o alguien distinto |
| Emily Mosquera | Línea 2 Semiprofesional | sin número en la libreta |
| Luis Miguel Espinosa | Línea 1 Profesional | sin número en la libreta |
