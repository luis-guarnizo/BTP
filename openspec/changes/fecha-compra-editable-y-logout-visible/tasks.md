# Tasks

## 1. Regla de vencimiento en el modelo

- [ ] 1.1 Agregar `LINEAS_EXPIRY_DAY` (env, por defecto 5) en `backend/config/settings.py` junto a `SOCIAL_PACKAGE_VALIDITY_DAYS` y documentarlo en `backend/.env.example`; verificar con `python manage.py check`
- [ ] 1.2 Cambiar `Package._compute_expiry` para Líneas: día `LINEAS_EXPIRY_DAY` del mes siguiente al de compra (con salto de año); verificar con tests en `backend/apps/packages/tests.py` para compra 3, 5 y 20 de septiembre → 5 de octubre y 15 de diciembre → 5 de enero, y Social 15 oct → 14 nov
- [ ] 1.3 Recalcular `expires_at` en `Package.save()` cuando la instancia es nueva o cambió `purchase_date` (incluido `update_fields` con `purchase_date`), recordando la fecha original al cargar; verificar con tests que editar la fecha recalcula el vencimiento, que `consume_credit()` no lo altera y que los créditos no cambian
- [ ] 1.4 Ordenar `Student.active_package()` y el listado de paquetes por `-purchase_date, -created_at`; verificar con un test de dos paquetes con la misma fecha de compra

## 2. API de edición de fecha de compra

- [ ] 2.1 Crear `PackagePurchaseDateSerializer` (solo `purchase_date`, requerido) y `PackageDetailView` (solo `PATCH`, permiso `IsReceptionistOrAdmin`) que responde con `PackageStatusSerializer`; registrar `path("<int:pk>/", ...)` en `apps/packages/urls.py`
- [ ] 2.2 Tests de API en `backend/apps/packages/tests.py`: recepcionista edita la fecha y recibe el nuevo `expires_at`/`status`; sin sesión → 403; fecha vacía o inválida → 400 y el paquete no cambia; enviar `credits_remaining` o `package_type` no los modifica; `PUT` → 405
- [ ] 2.3 Test de creación: `POST /api/packages/` con `purchase_date` de ayer guarda esa fecha y calcula el vencimiento desde ella; sin `purchase_date` usa hoy. Verificar con `python manage.py test apps.packages`

## 3. Frontend de paquetes

- [ ] 3.1 En `frontend/src/pages/staff/PackagesPage.jsx` agregar el campo "Fecha de compra" (`type="date"`, valor inicial hoy local) al formulario de venta, enviarlo como `purchase_date` y volver a hoy al resetear; verificar en el navegador que una venta sin tocar el campo queda con fecha de hoy y otra con fecha de ayer queda con ayer
- [ ] 3.2 En la tabla "Últimos paquetes" agregar edición en línea de la fecha de compra (Editar fecha → input + Guardar/Cancelar) que llama `PATCH /packages/<id>/`, muestra éxito/error y recarga; verificar en el navegador que el vencimiento mostrado cambia tras guardar
- [ ] 3.3 Ejecutar `npm run lint` y `npm run build` en `frontend/` sin errores

## 4. Cerrar sesión visible

- [ ] 4.1 En `frontend/src/pages/staff/DashboardLayout.jsx` mover "Cerrar sesión" a una barra superior en el contenido, junto al usuario, con estilo de botón; quitar el botón del final del sidebar
- [ ] 4.2 En `frontend/src/styles.css` agregar estilos `.topbar` y una regla `@media (max-width: 768px)` que apile sidebar y contenido; verificar en el navegador a 375px y a escritorio que el botón se ve arriba sin desplazarse, y que al pulsarlo lleva a `/recepcion/login` y no deja volver al panel
- [ ] 4.3 Ejecutar `npm run lint` y `npm run build` en `frontend/` sin errores

## 5. Verificación integrada

- [ ] 5.1 Levantar backend y frontend en local y recorrer el flujo completo: vender con fecha de ayer, editar la fecha de un paquete vencido para reactivarlo, hacer check-in con ese alumno y cerrar sesión desde la barra superior
- [ ] 5.2 Ejecutar `openspec validate fecha-compra-editable-y-logout-visible --strict` sin errores

## Workflow follow-up

- Hacer commit y push a la rama de trabajo; desplegar (Render/Vercel) cuando se apruebe.
- Archivar el cambio con `/opsx:archive` una vez desplegado y verificado.
