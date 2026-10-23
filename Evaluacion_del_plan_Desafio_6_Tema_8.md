# Evaluación del plan: Desafío 6 + Tema 8

Proyecto: Historial inteligente de proveedores UNI (Encar Build Night 2026)

## Veredicto general

El plan es sólido y está bien alineado con el desafío. Cubre el núcleo (la "historia clínica" del proveedor) y suma el tema transversal con una propuesta de hardware y costos. Tiene algunas brechas que conviene cerrar antes de la presentación.

## Lo que está bien

- **Alineación con el problema central.** El desafío habla de cumplimiento formal vs. resultado técnico deficiente. El enfoque de "historia clínica" captura esa idea.
- **Combinación con el Desafío 8.** El PDF pide indicar cuánto hardware, qué modelos y cuánto cuesta operar. El README responde las tres cosas, y eso suma puntos.
- **RAG local.** Es coherente con la recomendación del propio PDF: usar un modelo existente + documentos + RAG, no entrenar desde cero.
- **Ingesta interactiva.** Permitir actualizar y dar de alta proveedores demuestra que no es solo una demo estática.
- **Datos sintéticos.** Evitan problemas de privacidad y son lo correcto para un hackatón.

## Brechas respecto al PDF

El desafío lista qué podría mostrar el sistema. Contrastado con el README:

| Requisito del PDF | Estado en el plan |
| --- | --- |
| Contratos ejecutados | ✅ Cubierto |
| Tiempos de entrega / cumplimiento de plazos | ✅ Cubierto (días de atraso) |
| Reclamos | ✅ Cubierto |
| Observaciones técnicas | ⚠️ Mencionado vagamente ("observaciones") |
| Calidad de productos/servicios | ❌ No aparece explícito |
| Satisfacción de la unidad solicitante | ❌ No aparece |
| Reincidencias | ❌ No aparece |
| Evaluación final | ⚠️ Solo "dictamen", sin criterio claro |

La gran omisión es la **calidad real vs. cumplimiento formal**, que es el corazón del problema. Si el panel solo muestra plazos y multas, no resuelve el caso "cumplió formalmente pero entregó algo deficiente".

## Recomendaciones concretas

1. **Agregar al modelo de datos** un campo de calidad técnica (ej. escala 1-5), satisfacción de la unidad solicitante (1-5) y la dependencia que evalúa. Es lo más importante.
2. **Detectar reincidencias automáticamente.** Por ejemplo, alertar si un proveedor tiene 2 o más atrasos o reclamos del mismo tipo.
3. **Definir una evaluación final transparente.** Un puntaje ponderado (plazo, calidad, satisfacción, reclamos) con semáforo verde/amarillo/rojo. Explicable, no una caja negra del LLM.
4. **Que el RAG cite fuentes.** El chat debería indicar de qué contrato o documento sale cada respuesta. Reduce alucinaciones y es muy valorado en contexto institucional.
5. **Separar hechos de opiniones.** Distinguir registros objetivos (fechas, montos) de observaciones subjetivas de las dependencias.

## Riesgos técnicos

- **Consultas numéricas con RAG.** Preguntas como "¿cuál proveedor tiene más atraso total?" fallan con RAG puro. Los cálculos agregados deben salir de Pandas/JSON y el LLM solo redacta.
- **Rendimiento del hardware.** El mínimo real para llama3:8b es menor que lo propuesto (funciona con 8 GB de VRAM o incluso CPU, más lento). La propuesta es conservadora, lo cual está bien, pero convendría ofrecer **dos escenarios** (mínimo y recomendado) para mostrar que se piensa en recursos limitados.
- **Tiempo de respuesta en la demo.** Hacer una prueba previa; un 8B en CPU puede tardar bastante. Tener un modelo más chico de respaldo (ej. `llama3.2:3b` o `qwen2.5:3b`).
- **Idioma.** Mistral 7B y Llama3 8B rinden más flojo en español que otros. Probar `qwen2.5:7b` o `llama3.1:8b`, que suelen manejar mejor el español.

## Detalles menores del README

- **Inconsistencia de nombre:** el título dice "SupplierHistory-AI" y el cuerpo "ProvHistory-AI". Unificarlo.
- **Inconsistencia de modelo:** el stack menciona `llama3:8b`, pero el comando es `ollama pull llama3`. Especificar la versión exacta.
- **Datos:** el README menciona `raw_docs/` con PDFs. Verificar que realmente existan en el repo.
- **Seguridad:** el PDF del Desafío 8 menciona gestión de permisos y anonimización. Agregar roles simples (ej. administrador vs. consulta) cubre más puntos del tema transversal.
- **Costo eléctrico:** el estimado de USD 15-25/mes es razonable, pero conviene aclarar la suposición (horas de uso, tarifa).

## Prioridades si queda poco tiempo

1. **Campos de calidad, satisfacción y reincidencia** (cierra la brecha con el PDF).
2. **Puntaje final explicable con semáforo.**
3. **Citas de fuente en el chat.**
4. **Demo fluida y ensayada**, con 2 o 3 proveedores de prueba que cuenten una historia clara: uno ejemplar, uno que cumplió formalmente pero con mala calidad, y uno reincidente.

El tercer caso de la lista es el que mejor muestra el valor del sistema ante el jurado.

## Plan ajustado: cada brecha tiene su solución

Las secciones siguientes convierten las brechas detectadas en cambios concretos al plan; los pesos y umbrales son una propuesta inicial que el equipo puede calibrar.

| Brecha detectada | Cambio al plan | Dónde se implementa |
| --- | --- | --- |
| Calidad de productos/servicios | Campo `calidad_tecnica` (1-5) por contrato | `database.json` y formulario de ingesta |
| Satisfacción de la unidad solicitante | Campos `satisfaccion` (1-5) y `dependencia_evaluadora` | `database.json` y formulario de ingesta |
| Observaciones técnicas | Lista de observaciones con fecha, autor, tipo y marca hecho/opinión | `database.json` |
| Reincidencias | Regla automática: 2 o más atrasos o reclamos del mismo tipo disparan alerta | Función en Pandas |
| Evaluación final | Puntaje ponderado de 0 a 100 con semáforo y desglose | Función en Pandas, no el LLM |
| Cumplió formalmente pero con mala calidad | Alerta cuando plazo es alto y calidad es baja | Regla de contradicción en el puntaje |
| Respuestas sin respaldo | El chat cita contrato o documento de origen | Metadatos en ChromaDB |
| Consultas numéricas fallan con RAG | Los agregados se calculan en Pandas y el LLM solo redacta | Capa de consulta |
| Hardware único | Dos escenarios: mínimo y recomendado | README |
| Permisos y anonimización | Roles administrador y consulta | Streamlit |

## Modelo de datos ampliado

Cada contrato guarda hechos verificables y evaluaciones subjetivas en campos separados, para que el panel y el chat nunca los mezclen.

| Campo | Tipo | Escala o formato | Naturaleza |
| --- | --- | --- | --- |
| `fecha_comprometida` / `fecha_entrega_real` | fecha | AAAA-MM-DD | Hecho |
| `dias_atraso` | entero | calculado de las dos fechas | Hecho |
| `monto_adjudicado` | número | Guaraníes | Hecho |
| `multa_aplicada` | número | Guaraníes | Hecho |
| `calidad_tecnica` | entero | 1 a 5 | Evaluación |
| `satisfaccion` | entero | 1 a 5 | Evaluación |
| `dependencia_evaluadora` | texto | nombre de la unidad | Hecho |
| `reclamos` | lista | fecha, tipo, descripción, estado | Hecho |
| `observaciones_tecnicas` | lista | fecha, autor, tipo, texto, `es_hecho` (sí/no) | Mixta |
| `documento_origen` | texto | ruta en `raw_docs/` | Hecho |

Los tipos de reclamo y de observación salen de una lista cerrada (por ejemplo: plazo, calidad, documentación, soporte), para que la detección de reincidencias compare categorías iguales.

## Evaluación final explicable

El puntaje de cada proveedor sale de una fórmula fija calculada en Pandas; el LLM solo redacta la explicación a partir del desglose.

```latex
P = 0.30 \cdot S_{plazo} + 0.30 \cdot S_{calidad} + 0.25 \cdot S_{satisfaccion} + 0.15 \cdot S_{reclamos}
```

Cada componente se normaliza de 0 a 100: plazo según días de atraso, calidad y satisfacción desde la escala 1-5, y reclamos según cantidad y estado. La calidad pesa tanto como el plazo porque el desafío trata justamente del cumplimiento formal con resultado deficiente.

| Semáforo | Condición | Lectura |
| --- | --- | --- |
| Verde | P de 75 a 100 y sin reincidencia | Recomendable |
| Amarillo | P de 50 a 74, o una reincidencia | Usar con seguimiento |
| Rojo | P menor a 50, o reincidencia en calidad | Requiere justificación para contratar |

Si el componente de plazo supera 80 y el de calidad es menor a 50, el panel muestra la alerta "cumplió formalmente, resultado deficiente", aunque el puntaje total sea aceptable.

## Chat con fuentes, reincidencias y hardware

El chat deja de ser una caja negra: cada respuesta separa los datos calculados de los documentos recuperados.

- **Cálculos en Pandas.** Totales, promedios, rankings y días de atraso se calculan en código; el LLM recibe el resultado y lo redacta.
- **Citas de fuente.** Cada fragmento indexado en ChromaDB lleva como metadatos el proveedor, el contrato y el archivo de `raw_docs/`; la respuesta termina con la lista de fuentes usadas.
- **Hechos y opiniones.** El chat etiqueta cada dato como registro objetivo u observación de una dependencia.
- **Reincidencias.** Al cargar un reclamo o atraso, el sistema cuenta los previos del mismo proveedor y tipo; con dos o más muestra una alerta en el panel.
- **Roles.** Administrador (carga y edita) y consulta (solo lee); los datos de prueba permanecen anonimizados.

La propuesta de hardware pasa a dos escenarios, para mostrar que la solución funciona con recursos limitados:

|  | Mínimo | Recomendado |
| --- | --- | --- |
| Procesador | 4 a 8 núcleos | Intel Core i7 / AMD Ryzen 7 |
| RAM | 16 GB | 32 GB |
| GPU | Sin GPU o 8 GB de VRAM | NVIDIA RTX 3060 / 4060 de 12 GB |
| Modelo | `qwen2.5:3b` o `llama3.2:3b` | `llama3.1:8b` o `qwen2.5:7b` |
| Velocidad de respuesta | Más lenta, en CPU | Fluida para uso en demo |
| Costo | Por definir con el equipo | USD 1.100 a 1.300 (única vez) |

El costo eléctrico de USD 15 a 25 por mes debe indicar su suposición de horas de uso y tarifa. El modelo de respaldo para la demo es el de 3B.

## Checklist y guion de demo

El orden sigue el impacto sobre el desafío: primero lo que cierra las brechas del PDF, al final el pulido.

- [ ] Ampliar `database.json` con calidad, satisfacción, dependencia y observaciones tipificadas
- [ ] Actualizar los dos formularios de ingesta con los campos nuevos
- [ ] Implementar el puntaje ponderado y el semáforo en Pandas
- [ ] Implementar la regla de reincidencia y la alerta "cumplió formalmente, resultado deficiente"
- [ ] Agregar metadatos de fuente en ChromaDB y citas en las respuestas del chat
- [ ] Mover los cálculos agregados a Pandas
- [ ] Agregar roles administrador y consulta
- [ ] Corregir el README: nombre único del proyecto, versión exacta del modelo, dos escenarios de hardware, supuesto del costo eléctrico
- [ ] Verificar que `data/raw_docs/` exista con los documentos citados
- [ ] Probar la demo con el modelo principal y con el de respaldo

La demo usa tres proveedores sintéticos, cada uno con una historia clara:

1. **Ejemplar:** sin atrasos, calidad 5, semáforo verde.
2. **Cumplió formalmente, mala calidad:** entregó en plazo, calidad 2, dispara la alerta de contradicción.
3. **Reincidente:** tres atrasos del mismo tipo, semáforo rojo, con respuesta del chat citando los contratos.
