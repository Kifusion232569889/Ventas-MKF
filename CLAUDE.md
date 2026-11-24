# Ventas MKF — prospección B2B a consultoras de RRHH

## Qué es esto
Pipeline de prospección para vender a consultoras de RRHH españolas:
intervenciones, capacitación de equipos y neurocoaching ejecutivo de
Método KiFusion (MKF). No es venta B2C de KiFusion — es venta B2B a
empresas que ya hacen formación/consultoría a otras empresas.

## Infraestructura
- **Airtable**: base `appCO9VjtNmWej2IZ`, tabla `tblrC5iyTEdaIxQgR` — lista
  maestra de leads (63 registros). Campos clave: Contacto, Mensaje borrador,
  Notas, estado (Por contactar / Descartado).
- **Apollo.io**: plan gratuito, usado para research inicial de empresas.
- **Gmail**: conectado vía Composio (`pksdavidbosch@gmail.com`, cuenta PKS,
  no MKF — los borradores llevan firma MKF pero salen desde correo de
  logística; David lo acepta así por ahora).

## Reglas fijas
- CTA de marketing de MKF: nunca ofrecer sesión/consulta gratis. Solo Taller
  Reset Emocional, el libro, o sesión privada de pago. En B2B esto se
  traduce a "charla de 15 minutos" (no terapia gratis, es exploración
  comercial).
- Mensajes ≤60 palabras, un único CTA de bajo compromiso, señal específica
  de la empresa en el asunto (no genérico).
- Lenguaje general de "equipo"/"rendimiento", nunca específico de ventas
  (David lo pidió explícitamente tras rechazar versiones sales-only).
- Nunca generar oferta de agentes/skills de `Super Agentes` como si fueran
  software propietario — son archivos markdown genéricos (ver
  `agency-agents` repo público), no herramientas con ventaja de datos.

## Estilo de trabajo con David
- Cavernícola: respuestas mínimas, sin preámbulo, sin repetir la pregunta.
- Ejecución autónoma en pasos obvios, sin pedir permiso.
- Objetar solo si hay error factual, riesgo o contradicción real — una
  línea, y seguir.
- Español siempre.

## Cierre de sesión
Al terminar una sesión de trabajo en este proyecto: actualizar ESTADO.md
(qué se hizo) y TAREAS.md (qué queda), con fecha.

## Subproyecto prospeccion-auto/
Scripts Python semanales (centros/terapeutas y aliados estratégicos, Barcelona) -> tablas `Centros y Terapeutas` y `Aliados Estratégicos` de la misma base Airtable. Su estado y tareas viven en el ESTADO.md/TAREAS.md de esta carpeta (no hay docs/ propio). Detalle y decisiones ToS (no Maps/IG/LinkedIn) en cabeceras de los .py.
