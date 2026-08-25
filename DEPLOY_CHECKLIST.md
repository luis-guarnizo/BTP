# Guía de despliegue — nueva instalación por cliente

Checklist para desplegar una copia nueva de BTP para otra academia (una
instalación independiente por cliente: su propio backend, su propia base
de datos, su propio frontend — sin multi-tenancy).

Basada en los problemas reales que se presentaron en el primer despliegue;
seguirla en orden evita repetir esa depuración.

## 0. Antes de empezar

- [ ] Crea un repo de GitHub para este cliente (fork o copia del repo base).
- [ ] Ten a mano: nombre del cliente/academia, un dominio si va a usar uno propio.

## 1. Base de datos — Neon

- [ ] Crea un proyecto nuevo en [neon.tech](https://neon.tech) (uno por cliente, no reutilices el de otro).
- [ ] Copia el connection string (`postgres://user:pass@host/db`).

## 2. Backend — Render

1. **New → Web Service**, conecta el repo del cliente. Root directory: `backend`.
2. **Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_staff_user && python manage.py seed_initial_data
   ```
   > ⚠️ No olvides `seed_initial_data` — sin esto el catálogo de planes
   > (`PackageType`) queda vacío y no se puede vender ningún paquete.
3. **Start Command:**
   ```bash
   gunicorn config.wsgi:application
   ```
4. **Environment variables** — al pegarlas en Render, cada una va en su propio
   campo **Key** / **Value**. **Nunca pegues `NOMBRE=valor` completo dentro
   del campo Value** — es el error más común y causa fallos silenciosos
   (ej. `ALLOWED_HOSTS` pareciendo correcto pero rechazando todo con 400).

   | Key | Value | Notas |
   |---|---|---|
   | `SECRET_KEY` | (genera una nueva, única por cliente) | nunca reutilices la de otro cliente |
   | `DEBUG` | `False` | solo `True` temporalmente para diagnosticar un error, revertir de inmediato |
   | `ALLOWED_HOSTS` | `tu-app.onrender.com` | sin `https://`, sin `/` final |
   | `DATABASE_URL` | el connection string de Neon | |
   | `CORS_ALLOWED_ORIGINS` | `https://tu-frontend.vercel.app` | sin `/` final, debe ser el dominio ESTABLE de Vercel (ver paso 3) |
   | `CSRF_TRUSTED_ORIGINS` | mismo valor que arriba | |
   | `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` | credenciales del staff/admin de este cliente | |
   | `EMAIL_*` | según el proveedor de correo que uses | opcional |

5. Anota la URL que Render asigna (`https://<nombre>.onrender.com`) — la necesitas en el paso 3.

## 3. Frontend — Vercel

1. **Add New → Project → Import Git Repository** (¡no lo subas manualmente!
   Debe quedar conectado a GitHub desde el inicio para que cada `git push`
   redespliegue solo — si no, hay que reconectarlo después manualmente en
   Account Settings → Git).
2. Root Directory: `frontend`.
3. Variable de entorno:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://tu-backend.onrender.com/api` (con `/api` al final, sin el cual todo da 404)
   - Visibilidad: **Plain Text** (no "Sensitive/Secret" — Vite la incrusta en el bundle público de todos modos, Vercel no deja marcarla como secreta)
4. Deploy.
5. Confirma el **dominio de producción estable** con el botón **Visit** en el
   Overview del proyecto (NO la URL de un deployment individual, que trae un
   hash aleatorio y cambia en cada deploy — ej. `proyecto-a1b2c3.vercel.app`
   es de un deploy específico, `proyecto.vercel.app` o
   `proyecto-usuario.vercel.app` es la estable).
6. Si ya tenías la URL estable de antemano y no coincide con lo que pusiste
   en el paso 2 de Render, actualiza `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS`
   con la URL real.

## 4. Verificación end-to-end

- [ ] Abre `https://tu-backend.onrender.com/api/accounts/csrf/` directo — debe devolver JSON, no "Bad Request".
- [ ] Entra a `https://tu-frontend.vercel.app/recepcion/login` con las credenciales `ADMIN_USERNAME`/`ADMIN_PASSWORD`.
- [ ] Crea un alumno de prueba.
- [ ] Vende un paquete de prueba (confirma que el catálogo de planes aparece — si no, revisa que `seed_initial_data` haya corrido).
- [ ] Prueba el check-in de alumno (QR / teléfono + PIN) desde `/`.

## 5. Notas de arquitectura (por qué el código ya no debería fallar aquí)

El código de `frontend/src/api/client.js` ya está preparado para el escenario
cross-domain (frontend y backend en dominios distintos):
- El token CSRF se lee del **body** de la respuesta de `/accounts/csrf/`,
  no de la cookie (`document.cookie` no puede leer cookies de otro dominio).
- Se pide un token fresco en cada petición mutante (no se cachea), porque
  Django rota el token CSRF al hacer login.

Si en un cliente nuevo vuelve a aparecer un error de CSRF, es casi seguro un
problema de configuración (dominio mal puesto en `CORS_ALLOWED_ORIGINS`/
`CSRF_TRUSTED_ORIGINS`, o `VITE_API_URL` desactualizado sin redeploy) y no
del código — revisa la sección 2 y 3 primero.
