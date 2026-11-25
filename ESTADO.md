# Estado — Ventas MKF

## 2026-11-24
- Airtable: 63 leads totales. 2 descartados (competencia), 61 "Por
  contactar" — cero contacto real hasta hoy.
- Filtrado a 10 leads "Alto" fit, Ángulo 1 (RRHH): Attittud, Valora RRHH,
  Proarcai, MENDIPS, Future of People Academy, Human Team Building,
  LBconsultores, Human Resources by Sede21, NKIP Consulting, ADEAS HR.
- 5 mensajes de primer contacto redactados y guardados en Airtable
  (campo "Mensaje borrador") + creados como borrador real en Gmail:
  - Attittud → info@attittud.com (asunto: "vuestra línea de Desarrollo")
  - LBconsultores → soporte@lb-consultores.com (asunto: premio liderazgo
    en ventas TTI 2024)
  - Human Resources by Sede21 → sede21@sede21.com (asunto: programas de
    liderazgo)
  - NKIP Consulting → info@nkipconsulting.com (asunto: jornadas team
    building DISC/TTI)
  - ADEAS HR → sin email público (solo teléfono/formulario web) — NO
    tiene borrador de email, pendiente contacto manual.
- 5 leads con bloqueo, flag en Notas de Airtable, sin mensaje aún:
  - Valora RRHH, Human Team Building: fetch bloqueado por robots.txt,
    necesita research manual/LinkedIn.
  - Future of People Academy: sin email/teléfono/formulario público,
    necesita LinkedIn.
  - Proarcai: más probable partner/prescriptor (executive search) que
    cliente directo — necesita ángulo de colaboración, no venta.
  - MENDIPS: oferta solapada (coaching/desarrollo) — más competidor que
    cliente. Contacto encontrado (info@mendips.net) pero NO enviar
    mensaje de venta tal cual.

## Pendiente de decisión de David
- Enviar o no los 4 borradores de Gmail ya creados (siguen sin enviar,
  esperando su OK).
- Qué hacer con ADEAS HR (llamar / formulario, no email).
- Si vale la pena escribir mensaje de partnership para Proarcai/MENDIPS
  en vez de descartarlos.


## 2026-11-24 — Unificación
mkf-prospeccion movido a `Ventas MKF\prospeccion-auto\`. Un solo proyecto, dos públicos: (A) consultoras RRHH = venta directa (lista maestra); (B) centros/terapeutas y aliados = derivación (scripts semanales). Misma base Airtable `appCO9VjtNmWej2IZ`. Estado original de B abajo (de 2026-09-21; rutas `C:\Users\David\...` obsoletas, ahora `prospeccion-auto\`).

### Subproyecto prospeccion-auto (centros/terapeutas + aliados, Barcelona)

Última actualización: 2026-09-21

#### Fase actual
Prospección B2B automatizada para Método KiFusion: centros/terapeutas afines y aliados
estratégicos de derivación bidireccional en Barcelona, con carga en Airtable.

#### Hecho
- [x] Base Airtable "MKF — Leads Prospección B2B" creada (workspace MKF), con tablas
      "Centros y Terapeutas" y "Aliados Estratégicos" y todos los campos pedidos (2026-09-21)
- [x] Primera extracción manual (vía WebSearch + Airtable MCP): 10 registros en Centros y
      Terapeutas + 10 en Aliados Estratégicos, dedupe validado contra la lista inicial (2026-09-21)
- [x] `prospecting_semanal.py` y `alianzas_semanal.py` escritos: scraping estático
      (Doctoralia con microdatos verificados en vivo, InfoIsInfo genérico), dedupe contra
      Airtable, límite de 10 nuevos/ejecución, logging (2026-09-21)
- [x] Tareas programadas en Windows Task Scheduler: MKF_Prospeccion_Centros (lunes 8:00),
      MKF_Alianzas_Estrategicas (martes 8:00) (2026-09-21)

#### En curso
- [ ] Ninguno abierto ahora mismo.

#### Pendiente (priorizado)
1. Generar el Personal Access Token de Airtable y ponerlo en `.env` — sin esto los scripts
   programados fallarán en silencio (el log dirá "falta variable de entorno"). Bloqueante
   para que el cron funcione de verdad.
2. Revisar tras la primera ejecución automática (lunes/martes) si los parsers genéricos
   (InfoIsInfo, Guía Consciente) están extrayendo candidatos razonables o solo ruido de
   navegación — son heurísticos, no selectores verificados uno a uno como Doctoralia.
3. Decidir si se quiere cubrir Google Maps con la Places API de pago (no se automatizó por
   ToS) o dejarlo como búsqueda manual puntual.
4. Decidir si se quiere subir este repo a GitHub remoto (por ahora solo está en git local).

#### Necesito de David
- **PAT de Airtable** (Personal Access Token) para que los scripts puedan escribir sin la
  sesión de Claude — generarlo en airtable.com/create/tokens y pegarlo en `.env`
  (ver `.env.example`). Es la única pieza que solo tú puedes crear.
- Confirmar si quieres repo remoto en GitHub (público/privado, nombre) o se queda solo local.

#### Decisiones tomadas (no re-discutir)
- [2026-09-21] No se automatiza scraping de Google Maps: viola los Términos de Servicio de
  Google. Alternativa si se quiere: Google Places API.
- [2026-09-21] No se automatiza scraping de Instagram/LinkedIn (hashtags, búsquedas): rompe
  ToS y requiere evasión de detección agresiva, especialmente en LinkedIn. Alternativa:
  APIs oficiales (Meta Graph API, LinkedIn API) con credenciales propias.
- [2026-09-21] Doctoralia no expone teléfono/email públicos (fuerza reserva vía su propia
  plataforma) — verificado en vivo. Para esos leads, el campo Web queda como el enlace de
  perfil de Doctoralia cuando no hay web propia detectada.
- [2026-09-21] Scheduling con Windows Task Scheduler (`schtasks`) en vez de cron — no hay
  cron nativo en Windows.

#### Siguiente acción exacta (OBSOLETA 2026-11-24 — ver "Siguiente acción exacta" al final)
Generar el PAT de Airtable y pegarlo en `C:\Users\David\Proyectos\mkf-prospeccion\.env`
(copiar desde `.env.example`). Después, probar en manual: `python prospecting_semanal.py`
desde esa carpeta, y revisar `prospecting_log.txt`.


## 2026-11-24 — Post-unificación
- Git local iniciado en `Ventas MKF` (rama `dev`, sin remoto). Historial antiguo `_OBSOLETO-mkf-prospeccion\.git` no existe en este equipo: se pierde.
- Scripts compilan (py_compile OK con Python 3.11). Faltan deps (bs4) en Python del sistema; crear `.venv` + `pip install` denegado por permisos en esta sesión.
- Tareas programadas `MKF_*` NO existen en este equipo: scripts semanales parados.

### Necesito de David (prospeccion-auto)
- PAT de Airtable en `prospeccion-auto\.env`.
- Permitir crear `prospeccion-auto\.venv` e instalar `requirements.txt` (requests, bs4, python-dotenv).
- OK para recrear tareas programadas (lunes/martes 8:00) apuntando a `.venv\Scripts\python.exe`.
- OK para crear repo GitHub privado.

## 2026-11-24 — Entorno prospeccion-auto
- Venv creado FUERA de Drive (Drive es demasiado lento para venv): `C:\Users\kineb\.venvs\mkf-prospeccion`. Deps OK (requests, bs4, python-dotenv).
- Prueba real: `prospecting_semanal.py` sale con exit 1 y `ERROR: falta variable de entorno 'AIRTABLE_API_KEY'` (esperado, sin PAT). Ojo: ese error va a stdout, no al log — con Task Scheduler se perdería.
- Registrar tareas programadas denegado por permisos de Claude: queda `prospeccion-auto\instalar_tareas.ps1` para que David lo ejecute.

## Cierre de sesión 2026-11-24
- Commits: `7468d8f` (unificación), `57d3697` (instalador tareas), + este checkpoint. Rama `dev`.
- Push: NO posible — repo sin remoto. Crear repo GitHub privado requiere OK de David.

## 2026-11-25
- Analizado PDF RelevX "Buscador de clientes" (lead magnet de @adriamora_). Veredicto: no instalar; copiar seguimientos día 3/7, columna "Señal", mensaje de recomendaciones, sin enlaces en 1er mensaje. Quitar su línea promo a relevx.com si se reutiliza. Tareas añadidas a TAREAS.md.
- **Corrección de remitente**: el correo de MKF es `contacto@metodokifusion.com`. Los 4 borradores de 2026-11-24 se crearon en `pksdavidbosch@gmail.com` (cuenta equivocada) y NO están enviados. Hay que recrearlos en contacto@.
- David conectó Gmail (contacto@) pero la sesión no cargó los conectores (se cargan al arrancar). Hace falta sesión nueva.
- Airtable/Gmail MCP no disponibles en esta sesión.
- Detectado: `origin` = github.com/Kifusion232569889/Ventas-MKF (antes no había remoto). Ver estado del push en cierre.

## Necesito de David (2026-11-25)
- Abrir sesión nueva (para cargar Gmail contacto@ y Airtable) y escribir "continúa".
- Si Gmail no aparece: conectarlo desde `/mcp` en sesión interactiva.
- PAT de Airtable en `prospeccion-auto\.env`; ejecutar `instalar_tareas.ps1`.

## Siguiente acción exacta
1. Sesión nueva → verificar que existen herramientas Gmail (contacto@) y Airtable (ToolSearch "gmail", "airtable").
2. Leer campo "Mensaje borrador" en Airtable (`appCO9VjtNmWej2IZ` / `tblrC5iyTEdaIxQgR`) de Attittud, LBconsultores, Sede21, NKIP; recrear los 4 borradores en contacto@metodokifusion.com; borrar los de la cuenta PKS; confirmar que existen.
3. Redactar seguimientos día 3 y día 7 (≤60 palabras, sin enlaces) para esos 4.
4. David: decide enviar los 4 borradores desde contacto@.
5. Pendientes heredados: PAT Airtable + `prospeccion-auto\instalar_tareas.ps1`; luego `C:\Users\kineb\.venvs\mkf-prospeccion\Scripts\python.exe prospecting_semanal.py` desde `prospeccion-auto\`.

## 2026-11-25 — Día 0 enviado
- Enviados desde contacto@metodokifusion.com (Gmail web en Chrome, 11:09-11:10): Attittud, LBconsultores, Sede21, NKIP. Textos en `secuencias-rrhh.md`; método en `guia-mensajes.md`.
- Gmail/Airtable: sin conectores MCP en esta sesión; se usa Chrome. Borradores viejos de pksdavidbosch@ obsoletos.
- Día 3 y día 7 PROGRAMADOS en Gmail (hilos de día 0): D3 lun 30 nov 9:00, D7 jue 3 dic 9:00 (28 nov era sábado, movido a laborable). Si un lead responde, cancelar sus programados en Gmail > Programados.

## Cierre de sesión 2026-11-25
- Hecho: guía de mensajes (`guia-mensajes.md`, regla en CLAUDE.md), secuencias D0/D3/D7 de 4 leads (`secuencias-rrhh.md`), D0 enviados 11:09-11:10 desde contacto@, D3 (lun 30 nov 9:00) y D7 (jue 3 dic 9:00) programados en Gmail.
- Remoto: origin = github.com/Kifusion232569889/Ventas-MKF, rama dev (el "sin remoto" de entradas 2024-11-24 está obsoleto).
- Fuera de alcance de esta sesión: sin conectores Gmail/Airtable (se usó Chrome); Airtable no se pudo leer.

## Siguiente acción exacta
1. 30 nov por la mañana: abrir Gmail contacto@ > Recibidos y buscar respuestas de Attittud, LBconsultores, Sede21, NKIP. Si alguien responde, cancelar sus D7 en Gmail > Programados y redactar respuesta con `guia-mensajes.md`.
2. David: dar OK al perfil del segmento "empresas que contratan formadores" (ver TAREAS) y decir quién es el tercer autor.
3. David: PAT Airtable en `prospeccion-auto\.env` + ejecutar `.\instalar_tareas.ps1`.
