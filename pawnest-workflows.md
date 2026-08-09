---
type: reference
status: active
created: 2026-03-28
---

# Pawnest — n8n Workflows Index

> Ultima actualizacion: 2026-03-31
> Todos los workflows operativos de Pawnest Living en n8n.

| ID | Name | Trigger | Path | Description |
|----|------|---------|------|-------------|
| `Nhi7FZoBoCyAbg0h` | Pawnest — Order Pipeline (Telegram + Sheets + Meta CAPI) | Webhook `/shopify-orders-paid` | Order Processing | Cada vez que se paga una orden en Shopify: alerta Telegram, log en Google Sheets (LTV tracking), Purchase event a Meta CAPI como backup |
| `54l6nB9flzaCBmYG` | Pawnest — AI Email Classifier | Webhook `/email-classify` | Email Automation | Clasifica emails por keywords (WISMO, RETURNS, CANCELLATION, MARKETING, SUPPORT). WISMO dispara auto-lookup. Urgentes alertan por Telegram |
| `wOUhYn4q1FB27ZMs` | Pawnest — WISMO Order Status Lookup | Webhook `/wismo-lookup` | Email Automation | Busca orden del cliente en Shopify por email. Devuelve numero de orden, estado, tracking number/URL. Se dispara desde el Email Classifier |
| `xU6UvyrJbkt8d4cg` | Pawnest — Abandoned Cart Logger | Webhook `/abandoned-cart-check` | Cart Recovery | Recibe checkout de Shopify, espera 30 min, verifica si compro. Si no: alerta Telegram + log en Google Sheets tab "Abandoned" |
| `lbY22Tk1YkkSzxso` | Pawnest — Inventory Low Stock Alert | Schedule (every 6h) | Inventory | Obtiene token Shopify via client_credentials, consulta stock via GraphQL, alerta por Telegram si alguna variante tiene < 5 unidades |
| `SXeaF6ydOPxsq4dK` | Meta — Data Deletion Callback | Webhook `/meta-data-deletion` | Compliance | Endpoint requerido por Meta para GDPR. Responde a requests de eliminacion de datos de usuarios |
| `dD3Bu9V55y4QPpT3` | Alba — Instagram Daily Insights | Schedule (daily 9AM Madrid) | Alba Analytics | Fetch last 25 posts + insights (likes, comments, saved, reach, impressions), calculate engagement rate, append to Google Sheets, notify Telegram |
| `0XLkPLcB4qH0d5DG` | Pawnest — Ghost Checkout Filter | Webhook `/shopify-ghost-checkout-filter` | Anti-fraud | Score-based bot detection (spam domains, missing names, suspicious patterns). Score >= 40 = ghost → Telegram alert + log to LTV Tracker sheet |
| `03vHwoDzw3xurmEx` | Pawnest — Spam & Phishing Logger | Webhook `/pawnest-spam-logger` | Email Security | Classifies spam emails by pattern (6 categories). Logs to LTV Tracker sheet Spam Log tab. HIGH threat → Telegram alert |
| `zJueH8Ctk2mmL6i3` | Pawnest — WISMO Auto-Reply Draft | Webhook `/wismo-auto-reply` | Email Automation | Composes reply to WISMO emails. Looks up order in Shopify → drafts response → Telegram preview (human reviews before sending) |

## Diagrama de dependencias

```
Shopify Order Paid ──→ [Order Pipeline] ──→ Telegram + Sheets + Meta CAPI

Inbound Email ──→ [Email Classifier] ──┬──→ [WISMO Lookup] ──→ Shopify API ──→ Order Status
                                        ├──→ Telegram (urgentes)
                                        └──→ Clasificacion guardada

Shopify Checkout ──→ [Abandoned Cart] ──→ Wait 30m ──→ Check ──→ Telegram + Sheets

Schedule (6h) ──→ [Inventory Alert] ──→ Shopify GraphQL ──→ Check Stock ──→ Telegram (if < 5 units)

Meta Data Deletion Request ──→ [Data Deletion Callback] ──→ OK Response

Schedule (9AM Madrid) ──→ [Alba Insights] ──→ Meta Graph API ──→ Process ──→ Google Sheets + Telegram

Shopify Checkout ──→ [Ghost Checkout Filter] ──→ Score ──→ Ghost? → Telegram + Sheets / Legit → OK

Spam Email ──→ [Spam Logger] ──→ Classify ──→ Sheets + (HIGH → Telegram)

[Email Classifier] ──→ WISMO → [WISMO Auto-Reply Draft] ──→ Shopify Lookup ──→ Compose → Telegram Draft
```

## Notas

- Todos los workflows tienen sticky notes con descripcion visible en el canvas de n8n
- Error workflow recomendado: `Zuki — Error Alert Telegram` (`YMJ6QHuMkLZ9CEAJ`)
- Para detalle completo de cada workflow, ver `workflows-reference.md` en la raiz del repo
