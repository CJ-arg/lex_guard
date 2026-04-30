Documento de Definición de Producto (Seed Spec)
Nombre en Clave del Proyecto: LexGuard (Anti-Hallucination Guardrail)

1. Resumen Ejecutivo de la Herramienta
LexGuard es una herramienta de auditoría preventiva diseñada para estudios jurídicos. Actúa como un filtro de seguridad antes de subir cualquier escrito al sistema Lex100. El sistema procesa un documento legal (PDF o Docx), aísla todas las referencias a jurisprudencia y verifica de forma autónoma dos factores críticos: la existencia real del fallo citado en los registros oficiales (CSJN y Cortes Supremas Provinciales) y la consistencia semántica entre lo que el abogado afirma que dice el fallo y lo que el fallo resolvió verdaderamente.

2. Flujo de Experiencia del Usuario (UX Flow)
Carga Segura: El usuario sube su borrador final del escrito a la plataforma.

Escaneo Automático: El sistema procesa el texto e identifica de inmediato todas las afirmaciones que estén respaldadas por una cita jurisprudencial (ej. "...tal como resolvió la CSJN en 'Halabi', donde se estableció que...").

Auditoría en Tiempo Real: El usuario ve un panel de progreso donde las citas van pasando por el "estrado" de validación.

Reporte de Veredicto: El sistema devuelve el documento original con un panel lateral (o reporte adjunto) categorizando las citas mediante un sistema de semáforo:

🟢 Aprobado: El fallo existe y la interpretación es correcta.

🟡 Advertencia: El fallo existe, pero la interpretación semántica es dudosa o el fallo trata sobre un tema tangencial.

🔴 Peligro (Alucinación/Error): El fallo no existe en la base de datos, los autos son incorrectos, o el contenido del fallo contradice la afirmación del escrito.

3. Mecánica Interna y Lógica de Negocio (Comportamiento del Sistema)
El corazón de la aplicación funcionará mediante una orquestación de agentes especializados con roles muy marcados, garantizando que el proceso sea auditable paso a paso:

Agente Extractor: Su única responsabilidad es leer el texto y separar la "Afirmación del abogado" de la "Cita del fallo" (carátula, fecha, tribunal, tomo/folio).

Agente Investigador: Toma los metadatos de la cita y busca coincidencias exactas o aproximadas en los repositorios oficiales (InfoLeg, SAIJ o bases indexadas propias de las Cortes). Su salida es binaria: el texto original del fallo encontrado o un error de "Fallo Inexistente".

Agente Juez (Evaluación Semántica): Recibe la afirmación original del abogado y el texto real del fallo recuperado por el Investigador. Su tarea es estrictamente evaluar si la doctrina del fallo respalda la afirmación.

Trazabilidad: El sistema debe documentar internamente cómo llegó a cada conclusión. Si marca una cita en rojo, debe proporcionar al abogado la justificación exacta (ej. "Se encontró un fallo con esta carátula, pero trata sobre reajuste de haberes, no sobre amparo ambiental").

el resultado se mostrara en un dashboard web que se podra guardar si el usuario lo solicita

4. Casos Límite a Considerar (Edge Cases)
Errores tipográficos de buena fe: El abogado escribió mal el año o invirtió los nombres en la carátula, pero el fallo existe. El sistema debe ser lo suficientemente inteligente para encontrar el fallo real y sugerir la corrección, en lugar de marcarlo como una "alucinación" directa.

Citas encadenadas: Escritos que citan múltiples fallos en un solo párrafo para sostener un único argumento.

Límites de procesamiento: Escritos masivos (ej. un recurso extraordinario de 120 páginas) que requieran fraccionar la lectura para no saturar la memoria del sistema.

