# 🏢 SupplierHistory-AI: Historial Inteligente de Proveedores (UNI)

> **Desafío 6:** Historial de proveedores  
> **Tema Transversal 8:** IA propia con recursos limitados (RAG 100% Local)  
> **Evento:** Encar Build Night 2026

---

## 📖 1\. Descripción General

**ProvHistory-AI** es un prototipo funcional diseñado para unificar la "historia clínica" de los proveedores de la Universidad Nacional de Itapúa (UNI). El sistema centraliza contratos pasados, retrasos en entregas, multas, reclamos e historial de cumplimiento en un único panel interactivo.

Utiliza una arquitectura de **Recuperación Aumentada por Generación (RAG) 100% local**, garantizando privacidad absoluta de datos institucionales, cero costos recurrentes en dólares por consumo de APIs externas e independencia tecnológica total.

---

## 🎯 2\. Características Clave

* **Historia Clínica Unificada:** Visualización clara de métricas de cumplimiento, montos adjudicados, días de atraso acumulados y dictámenes por proveedor.  
* **Asistente en Lenguaje Natural (RAG Local):** Consultas directas mediante un chat inteligente (ej. *"¿Qué antecedentes de incumplimiento tiene el proveedor X?"*).  
* **Gestión Dinámica de Datos (Ingesta Interactiva):**  
  * **Actualizar historial existente:** Permite ingresar nuevos contratos, observaciones o reclamos a un proveedor registrado.  
  * **Registrar nuevos proveedores:** Formulario de alta para la creación de nuevos perfiles de empresas con re-indexación en tiempo real.  
* **Privacidad y Seguridad:** Sin conexión a servidores de terceros para procesamiento de datos sensibles.

---

## 🛠️ 3\. Stack Tecnológico

* **Lenguaje:** Python 3.10+  
* **Interfaz de Usuario:** Streamlit  
* **Motor de IA Local:** Ollama (`llama3:8b` / `mistral:7b`)  
* **Framework RAG:** LangChain / ChromaDB (Vector Store local)  
* **Gestión de Datos:** Pandas / JSON local

---

## 💻 4\. Propuesta de Hardware y Costos Operativos (Tema 8\)

Para un despliegue institucional dentro de la infraestructura de la universidad (On-Premise), la propuesta de costos es la siguiente:

### Hardware Recomendado (Servidor / Workstation de Oficina)

* **Procesador:** Intel Core i7 / AMD Ryzen 7 (8 núcleos o superior).  
* **Memoria RAM:** 32 GB DDR4 / DDR5.  
* **GPU (Aceleración de Inferencia):** NVIDIA RTX 3060 / 4060 con 12 GB VRAM.  
* **Almacenamiento:** SSD NVMe de 500 GB.

### Análisis de Costos (USD)

* **Inversión de Hardware (Única):** \~\$1,100 \- \$1,300 USD.  
* **Costo Operativo Mensual (Tokens/Servicios Cloud):** **\$0.00 USD** (Cero dependencias de APIs pagas).  
* **Consumo Eléctrico Estimado:** \~\$15 \- \$25 USD / mes (uso continuo).

---

## 🚀 5\. Instrucciones de Instalación y Ejecución

### Prerrequisitos

1. Tener instalado [Python 3.10+](https://www.python.org/).  
2. Tener instalado y corriendo [Ollama](https://ollama.ai/).  
3. Descargar el modelo local ejecutando en la terminal:

```sh
ollama pull llama3
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

---

## 📁 6\. Estructura de Datos de Prueba

El directorio `data/` contiene la estructura base de los expedientes:

* `data/database.json`: Registros consolidados de proveedores, contratos y evaluaciones.  
* `data/raw_docs/`: Documentos en texto/PDF anonimizados para la indexación RAG.

---

## 🛡️ 7\. Licencia y Seguridad

Este proyecto fue desarrollado bajo las normativas de la **Encar Build Night**. Todos los datos utilizados en las pruebas son sintéticos y/o anonimizados. No se incluyen ni requieren credenciales de servicios externos.