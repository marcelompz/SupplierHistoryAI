# 🏢 ProvHistory-AI: Historial Inteligente de Proveedores (UNI)

> **Desafío 6:** Historial inteligente de proveedores UNI  
> **Tema Transversal 8:** IA propia con recursos limitados (RAG 100% Local)  
> **Evento:** Encar Build Night 2026

---

## 📖 1\. Descripción General

**ProvHistory-AI** es un prototipo funcional que unifica la "historia clínica" de los proveedores de la Universidad Nacional de Itapúa (UNI). Centraliza en un único panel interactivo los contratos ejecutados, los tiempos de entrega, la calidad de lo entregado, la satisfacción de la unidad solicitante, los reclamos, las reincidencias y una evaluación final explicable.

El problema que resuelve: una empresa puede haber **cumplido formalmente** un contrato y aun así haber entregado un resultado técnicamente deficiente. Esa experiencia suele quedar dispersa entre dependencias. ProvHistory-AI la registra, la mide y la hace consultable.

Utiliza una arquitectura de **Recuperación Aumentada por Generación (RAG) 100% local**, con privacidad total de los datos institucionales, cero costo recurrente por APIs externas e independencia tecnológica.

---

## 🎯 2\. Características Clave

* **Historia clínica unificada:** contratos ejecutados, montos adjudicados, días de atraso, multas, reclamos, observaciones técnicas, calidad, satisfacción y evaluación final por proveedor.  
* **Calidad real vs. cumplimiento formal:** el panel cruza el cumplimiento de plazos con la calidad técnica y muestra la alerta *"cumplió formalmente, resultado deficiente"* cuando ambos divergen.  
* **Evaluación final explicable:** puntaje ponderado de 0 a 100 con semáforo (verde / amarillo / rojo) y desglose por criterio. Se calcula con código determinista, no con el LLM.  
* **Detección automática de reincidencias:** alerta cuando un proveedor acumula 2 o más atrasos o reclamos del mismo tipo.  
* **Asistente en lenguaje natural (RAG local) con fuentes:** consultas como *"¿Qué antecedentes de incumplimiento tiene el proveedor X?"*. Cada respuesta cita los contratos y documentos de origen.  
* **Hechos separados de opiniones:** los registros objetivos (fechas, montos) se distinguen de las observaciones subjetivas de las dependencias, en el panel y en el chat.  
* **Cálculos exactos:** totales, promedios y rankings se calculan con Pandas; el LLM solo redacta el resultado.  
* **Gestión dinámica de datos (ingesta interactiva):**  
  * **Actualizar historial existente:** ingresar nuevos contratos, evaluaciones, observaciones o reclamos a un proveedor registrado.  
  * **Registrar nuevos proveedores:** formulario de alta con re-indexación en tiempo real.  
* **Roles de acceso:** *administrador* (carga y edita) y *consulta* (solo lectura).  
* **Privacidad y seguridad:** sin conexión a servidores de terceros para procesar datos sensibles.

---

## 🛠️ 3\. Stack Tecnológico

* **Lenguaje:** Python 3.10+  
* **Interfaz de usuario:** Streamlit  
* **Motor de IA local:** Ollama  
  * Modelo principal: `llama3.1:8b` (buen desempeño en español)  
  * Alternativa: `qwen2.5:7b`  
  * Modelo de respaldo (equipos modestos y demo): `llama3.2:3b` o `qwen2.5:3b`  
* **Embeddings locales:** `nomic-embed-text` vía Ollama  
* **Framework RAG:** LangChain + ChromaDB (vector store local, con metadatos de fuente)  
* **Cálculos y datos:** Pandas / JSON local

> Los modelos se fijan por versión exacta para que la instalación sea reproducible.

---

## 🧮 4\. Modelo de Evaluación

### 4.1 Datos registrados por contrato

| Campo | Tipo | Escala o formato | Naturaleza |
| :---- | :---- | :---- | :---- |
| `fecha_comprometida` / `fecha_entrega_real` | fecha | AAAA-MM-DD | Hecho |
| `dias_atraso` | entero | calculado de las dos fechas | Hecho |
| `monto_adjudicado` | número | Guaraníes | Hecho |
| `multa_aplicada` | número | Guaraníes | Hecho |
| `calidad_tecnica` | entero | 1 a 5 | Evaluación |
| `satisfaccion` | entero | 1 a 5 | Evaluación |
| `dependencia_evaluadora` | texto | nombre de la unidad | Hecho |
| `reclamos` | lista | fecha, tipo, descripción, estado | Hecho |
| `observaciones_tecnicas` | lista | fecha, autor, tipo, texto, `es_hecho` (sí/no) | Mixta |
| `documento_origen` | texto | ruta dentro de `data/raw_docs/` | Hecho |

Los tipos de reclamo y de observación salen de una lista cerrada (plazo, calidad, documentación, soporte), de modo que la detección de reincidencias compare categorías iguales.

### 4.2 Puntaje final

El puntaje de cada proveedor se calcula en Pandas con una fórmula fija; el LLM solo redacta la explicación a partir del desglose.

```
P = 0.30 · S_plazo + 0.30 · S_calidad + 0.25 · S_satisfaccion + 0.15 · S_reclamos
```

Cada componente se normaliza de 0 a 100: plazo según días de atraso, calidad y satisfacción desde la escala 1-5, y reclamos según cantidad y estado. La calidad pesa tanto como el plazo porque el desafío trata del cumplimiento formal con resultado deficiente. **Los pesos son una propuesta inicial, configurable.**

| Semáforo | Condición | Lectura |
| :---- | :---- | :---- |
| 🟢 Verde | P de 75 a 100 y sin reincidencia | Recomendable |
| 🟡 Amarillo | P de 50 a 74, o una reincidencia | Usar con seguimiento |
| 🔴 Rojo | P menor a 50, o reincidencia en calidad | Requiere justificación para contratar |

### 4.3 Reglas de alerta

* **Reincidencia:** 2 o más atrasos o reclamos del mismo tipo para un mismo proveedor.  
* **Cumplió formalmente, resultado deficiente:** `S_plazo` mayor a 80 y `S_calidad` menor a 50, aunque el puntaje total sea aceptable.

---

## 💻 5\. Propuesta de Hardware y Costos Operativos (Tema 8\)

Despliegue institucional On-Premise, con dos escenarios para mostrar que la solución funciona con recursos limitados.

| | Mínimo | Recomendado |
| :---- | :---- | :---- |
| Procesador | 4 a 8 núcleos | Intel Core i7 / AMD Ryzen 7 (8 núcleos o más) |
| Memoria RAM | 16 GB | 32 GB DDR4 / DDR5 |
| GPU | Sin GPU, o con 8 GB de VRAM | NVIDIA RTX 3060 / 4060 con 12 GB de VRAM |
| Almacenamiento | SSD de 256 GB | SSD NVMe de 500 GB |
| Modelo | `llama3.2:3b` / `qwen2.5:3b` | `llama3.1:8b` / `qwen2.5:7b` |
| Respuesta | Más lenta (inferencia en CPU) | Fluida |
| Inversión de hardware (única vez) | Por definir según el equipo disponible | ~USD 1.100 a 1.300 |

### Costos operativos

* **Servicios y tokens en la nube:** **USD 0,00 / mes** (sin dependencia de APIs de pago).  
* **Consumo eléctrico estimado:** ~USD 15 a 25 / mes en el escenario recomendado.  
  * *Supuesto:* consumo medio de 250 a 300 W, uso continuo 24 h/día y tarifa de USD 0,08 a 0,11 por kWh. Debe validarse con la tarifa real vigente.

---

## 🔐 6\. Privacidad, Permisos y Anonimización

* El procesamiento es 100% local: ningún dato se envía a servicios externos.  
* **Roles:** *administrador* puede cargar y editar registros; *consulta* solo lee el panel y usa el chat.  
* Los datos de prueba son sintéticos y están anonimizados.

---

## 🚀 7\. Instrucciones de Instalación y Ejecución

### Prerrequisitos

1. Tener instalado [Python 3.10+](https://www.python.org/).  
2. Tener instalado y corriendo [Ollama](https://ollama.ai/).  
3. Descargar los modelos locales:

```sh
# Modelo principal
ollama pull llama3.1:8b

# Embeddings para el RAG
ollama pull nomic-embed-text

# Opcional: modelo de respaldo para equipos modestos
ollama pull llama3.2:3b
```

### Pasos para ejecutar la aplicación

```sh
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/provhistory-ai.git
cd provhistory-ai

# 2. Crear y activar entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (si aplica)
cp .env.example .env

# 5. Iniciar la aplicación
streamlit run app.py
```

Para usar el modelo de respaldo, definir en `.env` el nombre del modelo (por ejemplo `OLLAMA_MODEL=llama3.2:3b`).

---

## 📁 8\. Estructura de Datos de Prueba

El directorio `data/` contiene la estructura base de los expedientes:

* `data/database.json`: registros consolidados de proveedores, contratos, evaluaciones, reclamos y observaciones, según el modelo de la sección 4.1.  
* `data/raw_docs/`: documentos en texto/PDF anonimizados para la indexación RAG. Cada fragmento indexado conserva como metadatos el proveedor, el contrato y el archivo de origen, que el chat usa para citar sus fuentes.

### Proveedores de demostración

Los datos sintéticos incluyen tres casos pensados para mostrar el valor del sistema:

1. **Ejemplar:** sin atrasos, calidad 5, semáforo verde.  
2. **Cumplió formalmente, mala calidad:** entregó en plazo pero con calidad 2; dispara la alerta de contradicción.  
3. **Reincidente:** tres atrasos del mismo tipo, semáforo rojo; el chat responde citando los contratos.

---

## 🛡️ 9\. Licencia y Seguridad

Este proyecto fue desarrollado bajo las normativas de la **Encar Build Night**. Todos los datos utilizados en las pruebas son sintéticos y/o anonimizados. No se incluyen ni requieren credenciales de servicios externos.
