# FASA Social Dashboard

Dashboard y backend para planificar, aprobar, publicar y medir contenido social de Ferreteria Avenida.

## Desarrollo local

### Requisitos

- Docker y Docker Compose.
- Python 3.12+ para validaciones locales del backend.
- Node.js 22+ para validaciones locales del frontend.

### Configuracion

1. Copiar `.env.example` a `.env`.
2. Ajustar valores locales si hace falta. No usar secretos reales en este repositorio.
3. Levantar el stack:

```bash
docker compose up --build
```

Servicios locales:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Healthcheck backend: `http://localhost:8000/health`
- MySQL: `localhost:3306`

Nota de despliegue validado en `fasa_195`: el backend puede publicarse con
`BACKEND_PORT=18080` si el puerto `8000` ya esta ocupado. En ese caso,
`VITE_API_BASE_URL` debe apuntar a `http://localhost:18080` para que el
frontend consulte el backend correcto. Estos valores viven en el `.env` local
del servidor y no se versionan.

### Validaciones basicas

Backend:

```bash
cd backend
python -m pytest
python -c "from app.main import app; print(app.title)"
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

Docker:

```bash
docker compose config
```

Migraciones de base de datos:

```bash
cd backend
alembic upgrade head
```

En Docker:

```bash
docker compose exec backend alembic upgrade head
```

Por decision de arquitectura, el dashboard no publica directo contra Meta Graph API. n8n publica y mide; los secretos Meta viven en n8n.

El objetivo no es solo subir fotos a Instagram o Facebook. La idea es construir un centro operativo y gerencial para redes sociales: cargar piezas, programarlas, publicarlas por n8n/Meta Graph API, guardar los IDs devueltos por Meta y medir rendimiento por canal, producto, campania y periodo.

## Estado actual

Ya existe una primera integracion operativa fuera de este repositorio, en `X:\n8n\instagram_fasa`:

- Publicacion Instagram via n8n y Meta Graph API.
- Publicacion Facebook Page via n8n y Meta Graph API.
- Credencial Meta guardada en n8n como `Meta Instagram - FASA`.
- Upload de imagenes al hosting por FTP.
- Primer flujo programado con script local y automatizacion Codex.
- Endpoints n8n iniciales:
  - `POST /webhook/fasa/instagram/publish`
  - `POST /webhook/fasa/facebook/publish`
  - `POST /webhook/fasa/instagram/metrics`
  - `POST /webhook/fasa/facebook/metrics`

Este repositorio nace para convertir esa prueba en un producto interno mantenible.

## Vision

Crear un sistema donde el equipo de FASA pueda:

- Cargar una pieza visual.
- Escribir copy por canal.
- Elegir Instagram, Facebook o ambos.
- Asociar la pieza a producto, rubro y campania.
- Programar fecha y hora de salida.
- Aprobar antes de publicar.
- Publicar automaticamente.
- Ver errores de Meta/n8n si ocurren.
- Medir rendimiento inicial y acumulado.
- Comparar publicaciones y tomar decisiones comerciales.

## Roles esperados

- Operador: carga imagenes, textos y propuestas de publicacion.
- Aprobador: revisa precio, texto, stock, validez y autoriza.
- Gerencia: mira calendario, rendimiento, productos destacados y evolucion.
- Sistema/n8n: ejecuta publicaciones y recolecta metricas.

## Flujo funcional

1. El operador carga una pieza.
2. El sistema sube la imagen al hosting publico.
3. Se cargan textos separados:
   - Instagram: copy con hashtags.
   - Facebook: texto mas directo y comercial.
4. Se eligen canales: Instagram, Facebook o ambos.
5. La pieza queda en estado `borrador` o `pendiente_aprobacion`.
6. Un aprobador cambia el estado a `aprobado`.
7. Si tiene `scheduled_for`, el scheduler la publica cuando corresponde.
8. n8n llama a Meta Graph API.
9. El sistema guarda resultados:
   - `instagram_media_id`
   - `facebook_photo_id`
   - `facebook_post_id`
   - permalink
   - fecha/hora de publicacion
10. Un recolector consulta metricas a las 2 h, 24 h, 3 dias, 7 dias y 15 dias.
11. El dashboard muestra rendimiento y comparativas.

## Modelo de datos inicial

### `social_assets`

Imagenes o videos subidos al sistema.

- `id`
- `file_name`
- `public_url`
- `mime_type`
- `width`
- `height`
- `size_bytes`
- `created_at`

### `social_posts`

Pieza conceptual. Puede publicarse en uno o mas canales.

- `id`
- `piece_id`
- `title`
- `asset_id`
- `product_name`
- `category`
- `campaign_id`
- `status`
- `scheduled_for`
- `created_by`
- `approved_by`
- `approved_at`
- `created_at`
- `updated_at`

Estados sugeridos:

- `borrador`
- `pendiente_aprobacion`
- `aprobado`
- `programado`
- `publicado`
- `error`
- `cancelado`

### `social_post_channels`

Contenido especifico por canal.

- `id`
- `social_post_id`
- `platform`
- `message`
- `hashtags`
- `status`
- `published_at`
- `meta_media_id`
- `meta_post_id`
- `meta_photo_id`
- `permalink`
- `last_error`
- `raw_publish_response`

Valores de `platform`:

- `instagram`
- `facebook`

### `social_metric_snapshots`

Metricas historicas por publicacion/canal.

- `id`
- `social_post_channel_id`
- `measured_at`
- `likes`
- `comments`
- `shares`
- `saves`
- `reactions`
- `reach`
- `impressions`
- `engagements`
- `raw_metrics_response`

### `social_campaigns`

Agrupacion comercial/gerencial.

- `id`
- `name`
- `description`
- `starts_at`
- `ends_at`
- `status`

Ejemplos:

- `Ceramicas`
- `Chapas`
- `Herramientas`
- `Pintura`
- `Mes aniversario`

## Dashboard gerencial

Vistas esperadas:

- Calendario de publicaciones.
- Cola de aprobacion.
- Publicaciones publicadas con permalink.
- Errores pendientes de resolver.
- Ranking de mejores publicaciones.
- Rendimiento por canal.
- Rendimiento por rubro/producto.
- Evolucion semanal/mensual.
- Comparacion Instagram vs Facebook.
- Publicaciones programadas para los proximos dias.

KPIs iniciales:

- Publicaciones realizadas.
- Publicaciones programadas.
- Tasa de error de publicacion.
- Likes/reacciones totales.
- Comentarios totales.
- Compartidos.
- Guardados de Instagram, cuando Meta lo devuelva.
- Alcance e impresiones, cuando permisos/API lo permitan.

## Arquitectura propuesta

```text
Dashboard web
  -> API propia
  -> Base MySQL
  -> n8n publica y mide
  -> Meta Graph API
  -> FTP/hosting publico de imagenes
```

Responsabilidades:

- Dashboard/API: experiencia de usuario, aprobaciones, historial y reportes.
- Base MySQL: fuente de verdad para piezas, programacion y metricas.
- n8n: integraciones operativas con Meta y jobs recurrentes.
- FTP/hosting: servir imagenes publicas para Meta Graph API.

## Decision inicial

No publicar directo desde el dashboard. El dashboard debe encolar y auditar. n8n debe ejecutar las integraciones externas.

Motivos:

- Los secretos Meta ya viven en credenciales n8n.
- n8n ya publica correctamente en Instagram y Facebook.
- n8n es buen lugar para reintentos, logs y jobs programados.
- El dashboard queda mas limpio y gerencial.

## Roadmap

### Fase 1 - Base operativa

- Crear esquema MySQL.
- Crear backend minimo.
- CRUD de piezas.
- Upload de imagen al FTP.
- Estados de aprobacion.
- Programacion por fecha/hora.
- Envio a endpoints n8n existentes.
- Guardado de resultados.

### Fase 2 - Scheduler y metricas

- Job que busca piezas aprobadas con `scheduled_for <= now`.
- Publicacion automatica por canal.
- Recoleccion de metricas a 2 h, 24 h, 3 d, 7 d y 15 d.
- Snapshots historicos.

### Fase 3 - Dashboard gerencial

- Calendario.
- Ranking.
- Filtros por fecha, canal, producto y campania.
- KPIs mensuales.
- Comparativas por rubro.
- Exportacion CSV/PDF.

### Fase 4 - Inteligencia comercial

- Recomendacion de horarios.
- Sugerencias de copy/hashtags.
- Deteccion de piezas con bajo rendimiento.
- Comparacion de ofertas por categoria.
- Reporte semanal automatico.

## Variables y secretos

No guardar secretos en este repositorio.

Secretos esperados en entorno o vault:

- Token/API key de n8n.
- Credenciales FTP.
- Credenciales MySQL.
- Tokens Meta dentro de n8n.

## Primeros proximos pasos

1. Elegir stack del dashboard.
2. Crear schema SQL inicial.
3. Crear API para piezas y canales.
4. Crear pantalla minima de carga/aprobacion.
5. Conectar con n8n usando los endpoints ya validados.
6. Persistir resultados y metricas.

Stack sugerido:

- Backend: FastAPI.
- Frontend: Vue 3 o React.
- Base: MySQL.
- Jobs de integracion: n8n.

La prioridad es que el sistema sea simple de operar y fuerte para auditar: que cada publicacion tenga imagen, copy, aprobacion, horario, resultado y metricas asociadas.
