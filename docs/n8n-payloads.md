# Payloads n8n para publicacion y metricas

Este documento define el contrato entre el backend del dashboard FASA Social y
n8n. El dashboard no llama Meta Graph API directamente: el backend envia
payloads a n8n, n8n publica o mide en Meta, y el backend persiste la respuesta
operativa para auditoria.

Los ejemplos usan valores ficticios y no contienen tokens, cookies ni secretos.
Las credenciales de Meta, FTP y n8n deben vivir en variables de entorno o en el
vault/credenciales de n8n.

## Endpoints

- `POST /webhook/fasa/instagram/publish`
- `POST /webhook/fasa/facebook/publish`
- `POST /webhook/fasa/instagram/metrics`
- `POST /webhook/fasa/facebook/metrics`

## Publicacion Instagram

Objetivo: publicar una pieza aprobada en Instagram a partir de una URL publica
de imagen/video y devolver los IDs/permalink generados por Meta.

Request esperado:

```json
{
  "request_id": "post-channel-123-instagram-2026-06-22T15:00:00Z",
  "social_post_id": 123,
  "social_post_channel_id": 456,
  "piece_id": "FASA-2026-0001",
  "platform": "instagram",
  "public_url": "https://static.example.com/fasa/pieza-0001.jpg",
  "message": "Oferta especial de herramientas.",
  "hashtags": "#FASA #Herramientas",
  "scheduled_for": "2026-06-22T15:00:00Z"
}
```

Response exitosa esperada:

```json
{
  "ok": true,
  "platform": "instagram",
  "social_post_channel_id": 456,
  "meta_media_id": "17890000000000000",
  "permalink": "https://www.instagram.com/p/example/",
  "published_at": "2026-06-22T15:01:10Z",
  "raw": {
    "id": "17890000000000000"
  }
}
```

Response con error esperada:

```json
{
  "ok": false,
  "platform": "instagram",
  "social_post_channel_id": 456,
  "error_code": "META_PUBLISH_ERROR",
  "message": "Meta rechazo la publicacion.",
  "retryable": true,
  "raw": {
    "error": {
      "type": "OAuthException",
      "code": 190
    }
  }
}
```

Campos que el backend debe persistir: `status`, `published_at`,
`meta_media_id`, `permalink`, `last_error` y `raw_publish_response`.

## Publicacion Facebook

Objetivo: publicar una pieza aprobada en Facebook Page y devolver los IDs de
foto/post generados por Meta.

Request esperado:

```json
{
  "request_id": "post-channel-123-facebook-2026-06-22T15:00:00Z",
  "social_post_id": 123,
  "social_post_channel_id": 457,
  "piece_id": "FASA-2026-0001",
  "platform": "facebook",
  "public_url": "https://static.example.com/fasa/pieza-0001.jpg",
  "message": "Oferta especial de herramientas. Consultanos por stock.",
  "hashtags": "#FASA",
  "scheduled_for": "2026-06-22T15:00:00Z"
}
```

Response exitosa esperada:

```json
{
  "ok": true,
  "platform": "facebook",
  "social_post_channel_id": 457,
  "meta_photo_id": "100000000000001",
  "meta_post_id": "200000000000001_100000000000001",
  "permalink": "https://www.facebook.com/example/posts/100000000000001",
  "published_at": "2026-06-22T15:01:20Z",
  "raw": {
    "id": "100000000000001",
    "post_id": "200000000000001_100000000000001"
  }
}
```

Response con error esperada:

```json
{
  "ok": false,
  "platform": "facebook",
  "social_post_channel_id": 457,
  "error_code": "META_PUBLISH_ERROR",
  "message": "No se pudo publicar en la pagina.",
  "retryable": true,
  "raw": {
    "error": {
      "message": "Unsupported post request"
    }
  }
}
```

Campos que el backend debe persistir: `status`, `published_at`,
`meta_photo_id`, `meta_post_id`, `permalink`, `last_error` y
`raw_publish_response`.

## Metricas Instagram

Objetivo: obtener metricas disponibles para una publicacion Instagram ya
publicada. Algunas metricas pueden faltar por permisos, tipo de media o ventana
de disponibilidad.

Request esperado:

```json
{
  "request_id": "metrics-channel-456-2026-06-23T15:00:00Z",
  "social_post_channel_id": 456,
  "platform": "instagram",
  "meta_media_id": "17890000000000000",
  "published_at": "2026-06-22T15:01:10Z",
  "measured_at": "2026-06-23T15:00:00Z"
}
```

Response exitosa esperada:

```json
{
  "ok": true,
  "platform": "instagram",
  "social_post_channel_id": 456,
  "measured_at": "2026-06-23T15:00:02Z",
  "metrics": {
    "likes": 38,
    "comments": 4,
    "shares": 2,
    "saves": 6,
    "reach": 1200,
    "impressions": 1500,
    "engagements": 50
  },
  "missing_metrics": ["reactions"],
  "raw": {
    "data": []
  }
}
```

Response con error esperada:

```json
{
  "ok": false,
  "platform": "instagram",
  "social_post_channel_id": 456,
  "error_code": "META_METRICS_ERROR",
  "message": "Meta no devolvio metricas para el media indicado.",
  "retryable": true,
  "raw": {
    "error": {
      "code": 100
    }
  }
}
```

Campos que el backend debe persistir: una fila en `social_metric_snapshots` con
`measured_at`, metricas disponibles, valores ausentes como `null` y
`raw_metrics_response`.

## Metricas Facebook

Objetivo: obtener metricas disponibles para una publicacion Facebook ya
publicada. Las metricas pueden variar segun permisos y tipo de post.

Request esperado:

```json
{
  "request_id": "metrics-channel-457-2026-06-23T15:00:00Z",
  "social_post_channel_id": 457,
  "platform": "facebook",
  "meta_post_id": "200000000000001_100000000000001",
  "meta_photo_id": "100000000000001",
  "published_at": "2026-06-22T15:01:20Z",
  "measured_at": "2026-06-23T15:00:00Z"
}
```

Response exitosa esperada:

```json
{
  "ok": true,
  "platform": "facebook",
  "social_post_channel_id": 457,
  "measured_at": "2026-06-23T15:00:03Z",
  "metrics": {
    "likes": 12,
    "comments": 3,
    "shares": 1,
    "reactions": 18,
    "reach": 980,
    "impressions": 1300,
    "engagements": 34
  },
  "missing_metrics": ["saves"],
  "raw": {
    "data": []
  }
}
```

Response con error esperada:

```json
{
  "ok": false,
  "platform": "facebook",
  "social_post_channel_id": 457,
  "error_code": "META_METRICS_ERROR",
  "message": "No se pudieron obtener metricas del post.",
  "retryable": true,
  "raw": {
    "error": {
      "message": "Permissions error"
    }
  }
}
```

Campos que el backend debe persistir: una fila en `social_metric_snapshots` con
`measured_at`, metricas disponibles, valores ausentes como `null` y
`raw_metrics_response`.

## Idempotencia y duplicados

- `request_id` debe ser estable por intento logico y canal.
- n8n debe tratar `request_id` y `social_post_channel_id` como claves de
  idempotencia para evitar publicar dos veces el mismo canal.
- Si n8n detecta que el canal ya fue publicado, debe responder `ok: true` con
  los IDs existentes cuando los tenga, o `ok: false` con un error no retryable
  si no puede reconstruirlos con seguridad.
- El backend no debe reintentar publicaciones con `meta_media_id`,
  `meta_post_id` o `meta_photo_id` ya persistidos salvo operacion manual
  explicita.
- Las metricas son append-only: cada medicion crea un snapshot nuevo. Si una
  metrica falta, se guarda `null` y se conserva la respuesta cruda.

## Variables de entorno esperadas

Los nombres concretos pueden ajustarse por ambiente, pero el contrato requiere:

- URL base o webhook path de n8n para cada endpoint.
- Token/API key interno para invocar n8n, si se protege el webhook.
- Credenciales Meta guardadas en n8n, no en el dashboard.
- Configuracion FTP/hosting guardada en n8n o en el servicio responsable del
  upload, no en ejemplos versionados.

Los ejemplos versionados deben usar dominios y IDs ficticios. Nunca incluir
tokens reales, cookies, secretos Meta, credenciales FTP ni passwords MySQL.
