# coding=utf-8
"""
Motor RAG (Recuperación Aumentada por Generación) para SupplierHistoryAI

Implementa conexión con ChromaDB y Ollama para búsqueda semántica local
con citas de fuente en el contexto de los documentos.
"""

import chromadb
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
from sentence_transformers import SentenceTransformer
import torch
import os

@dataclass
class ChunkDocumento:
    """Representa un chunk de documento con metadatos."""
    id: str
    documento_id: str
    texto: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

@dataclass
class ResultadoBusqueda:
    """Resultado de búsqueda RAG con contexto relevante."""
    documento_id: str
    texto: str
    metadata: Dict[str, Any]
    relevancia: float
    citas: List[Dict[str, Any]]

class RAGEngine:
    """Motor RAG para búsqueda semántica en documentos locales."""
    
    def __init__(self, 
                 db_path: str = "./chroma_db",
                 modelo_embedding: str = "all-MiniLM-L6-v2",
                 servidor_ollama: str = "http://localhost:11434",
                 modelo_ollama: str = "llama3:8b"):
        self.db_path = db_path
        self.servidor_ollama = servidor_ollama
        self.modelo_ollama = modelo_ollama
        
        # Inicializar cliente ChromaDB
        os.makedirs(db_path, exist_ok=True)
        self.client_chroma = chromadb.PersistentClient(path=db_path)
        self.collection_documentos = self.client_chroma.get_or_create_collection(
            name="documentos_contratos",
            metadata={"description": "Documentos de contratos de proveedores"}
        )
        
        # Inicializar modelo de embeddings
        self.modelo_embedding = SentenceTransformer(
            modelo_embedding,
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
    
    def _generar_embedding(self, texto: str) -> List[float]:
        """Genera embedding vectorial para un texto dado."""
        try:
            embedding = self.modelo_embedding.encode(texto, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generando embedding: {e}")
            return []
    
    def cargar_documentos(self, archivos_documentos: List[str]) -> None:
        """Carga y procesa múltiples archivos de documentos."""
        print(f"Cargando {len(archivos_documentos)} documentos...")
        
        for archivo in archivos_documentos:
            try:
                if not os.path.exists(archivo):
                    print(f"Archivo no encontrado: {archivo}")
                    continue
                
                # Determinar tipo de archivo y procesar
                if archivo.endswith('.docx'):
                    contenido = self._extraer_texto_docx(archivo)
                elif archivo.endswith('.pdf'):
                    contenido = self._extraer_texto_pdf(archivo)
                elif archivo.endswith('.txt'):
                    with open(archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                else:
                    print(f"Tipo de archivo no soportado: {archivo}")
                    continue
                
                # Dividir en chunks
                chunks = self._dividir_en_chunks(contenido)
                
                # Procesar cada chunk
                for i, chunk_texto in enumerate(chunks):
                    chunk_id = f"{archivo}_{i}"
                    embedding = self._generar_embedding(chunk_texto)
                    
                    metadatos = {
                        "archivo": archivo,
                        "tipo": "chunk",
                        "tamano": len(chunk_texto),
                        "fecha_carga": datetime.now().isoformat(),
                        "relevancia": self._calcular_relevancia_chunk(chunk_texto)
                    }
                    
                    self.collection_documentos.add(
                        documents=[chunk_texto],
                        metadatas=[metadatos],
                        ids=[chunk_id]
                    )
                    
                    print(f"Procesado chunk {i+1}/{len(chunks)} de {archivo}")
                    
            except Exception as e:
                print(f"Error procesando archivo {archivo}: {e}")
        
        print("Carga de documentos completada.")
    
    def _extraer_texto_docx(self, archivo: str) -> str:
        """Extrae texto de archivo DOCX."""
        try:
            from docx import Document
            doc = Document(archivo)
            texto_completo = ""
            for paragraph in doc.paragraphs:
                texto_completo += paragraph.text + "\n"
            return texto_completo.strip()
        except ImportError:
            print("Para extraer DOCX, instala python-docx: pip install python-docx")
            return ""
        except Exception as e:
            print(f"Error extrayendo DOCX {archivo}: {e}")
            return ""
    
    def _extraer_texto_pdf(self, archivo: str) -> str:
        """Extrae texto de archivo PDF."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(archivo)
            texto = ""
            for pagina in doc:
                texto += pagina.get_text()
            doc.close()
            return texto
        except ImportError:
            print("Para extraer PDF, instala PyMuPDF: pip install PyMuPDF")
            return ""
        except Exception as e:
            print(f"Error extrayendo PDF {archivo}: {e}")
            return ""
    
    def _dividir_en_chunks(self, texto: str, tamano_chunk: int = 500) -> List[str]:
        """Divide texto largo en chunks más pequeños."""
        if not texto or len(texto.strip()) == 0:
            return []
        
        texto = texto.strip()
        if len(texto) <= tamano_chunk:
            return [texto]
        
        chunks = []
        for i in range(0, len(texto), tamano_chunk):
            chunk = texto[i:i + tamano_chunk]
            chunks.append(chunk)
        
        return chunks
    
    def _calcular_relevancia_chunk(self, texto: str) -> float:
        """Calcula relevancia heurística de un chunk."""
        palabras_clave = [
            "contrato", "entrega", "calidad", "plazo", "multa", "reclamo",
            "proveedor", "suministro", "material", "servicio", "aviso",
            "fecha", "pago", "incumplimiento", "tiempo", "retardo"
        ]
        
        texto = texto.lower()
        puntuacion = 0
        
        for palabra in palabras_clave:
            if palabra in texto:
                puntuacion += 1
        
        return min(puntuacion / len(palabras_clave), 1.0)
    
    def buscar(self, consulta: str, top_k: int = 5) -> List[ResultadoBusqueda]:
        """Realiza búsqueda semántica por consulta."""
        try:
            # Generar embedding de la consulta
            consulta_embedding = self._generar_embedding(consulta)
            
            if not consulta_embedding:
                return []
            
            # Buscar en ChromaDB
            resultados = self.collection_documentos.query(
                query_embeddings=[consulta_embedding],
                n_results=min(top_k, 10),
                include=["documents", "metadatas", "distances"]
            )
            
            resultados_busqueda = []
            
            for i, documento in enumerate(resultados.get("documents", [])):
                metadatos = resultados.get("metadatas", [{}])[i] if resultados.get("metadatas") else {}
                distancia = resultados.get("distances", [{}])[i] if resultados.get("distances") else {}
                
                relevancia = 1.0 - distancia if distancia else 0.5
                
                # Generar citas si es posible
                citas = self._generar_citas_documento(documento, consulta)
                
                resultado = ResultadoBusqueda(
                    documento_id=metadatos.get("archivo", "desconocido"),
                    texto=documento,
                    metadata=metadatos,
                    relevancia=relevancia,
                    citas=citas
                )
                
                resultados_busqueda.append(resultado)
            
            return resultados_busqueda
            
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            return []
    
    def _generar_citas_documento(self, texto_documento: str, consulta: str) -> List[Dict[str, Any]]:
        """Genera citas basadas en el texto del documento."""
        citas = []
        
        try:
            # Buscar frases relevantes
            oraciones = texto_documento.split(".")
            for i, oracion in enumerate(oraciones):
                if len(oracion.strip()) > 20:  # Solo oraciones significativas
                    # Calcular relevancia heurística
                    relevancia_oracion = 0
                    if "contrato" in oracion.lower():
                        relevancia_oracion += 0.3
                    if "entrega" in oracion.lower():
                        relevancia_oracion += 0.2
                    if "calidad" in oracion.lower():
                        relevancia_oracion += 0.2
                    if "plazo" in oracion.lower():
                        relevancia_oracion += 0.2
                    if "multa" in oracion.lower():
                        relevancia_oracion += 0.1
                    
                    if relevancia_oracion > 0.3:
                        cita = {
                            "texto_oracion": oracion.strip() + ".",
                            "numero_oracion": i + 1,
                            "relevancia": relevancia_oracion,
                            "posicion": texto_documento.find(oracion) if oracion in texto_documento else 0
                        }
                        citas.append(cita)
            
        except Exception as e:
            print(f"Error generando citas: {e}")
        
        return citas[:3]  # Retornar máximo 3 citas
    
    def generar_respuesta_contexto(self, consulta: str, 
                                  resultados_busqueda: List[ResultadoBusqueda],
                                  max_tokens: int = 1000) -> str:
        """Genera respuesta usando contexto de búsqueda y Ollama."""
        
        # Construir contexto
        contexto = "\n\n".join([
            f"Documento: {r.documento_id}\n"
            f"Relevancia: {r.relevancia:.2f}\n"
            f"Contenido: {r.texto[:500]}...\n"
            for r in resultados_busqueda
        ])
        
        # Preparar prompt para Ollama
        prompt = f"""
Eres un asistente especializado en análisis de contratos de proveedores.

Consulta del usuario: {consulta}

Contexto relevante extraído de documentos:
{contexto}

Basándote en el contexto anterior, responde a la consulta del usuario.
Incluye citas cuando sea posible, y explica tu razonamiento.
Si la información no está en el contexto, indica: "No tengo información suficiente en los documentos proporcionados."

Responde en español y de manera concisa.
"""
        
        try:
            respuesta = self._consultar_ollama(prompt, max_tokens)
            return respuesta
        except Exception as e:
            print(f"Error consultando Ollama: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
    def _consultar_ollama(self, prompt: str, max_tokens: int = 1000) -> str:
        """Consulta el modelo Ollama local."""
        try:
            payload = {
                "model": self.modelo_ollama,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": max_tokens,
                    "temperature": 0.1
                }
            }
            
            response = requests.post(
                f"{self.servidor_ollama}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                print(f"Error Ollama: {response.status_code} - {response.text}")
                return "Error generando respuesta."
                
        except requests.exceptions.ConnectionError:
            print("No se puede conectar a Ollama. Asegúrate de que esté corriendo:")
            print("ollama run llama3:8b")
            return "Servicio Ollama no está disponible."
        except Exception as e:
            print(f"Error consultando Ollama: {e}")
            return "Error consultando el modelo de IA."
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del motor RAG."""
        try:
            total_documentos = self.collection_documentos.count()
            return {
                "total_documentos": total_documentos,
                "coleccion_nombre": "documentos_contratos",
                "modelo_embedding": "all-MiniLM-L6-v2",
                "modelo_ollama": self.modelo_ollama,
                "servidor_ollama": self.servidor_ollama,
                "disponibilidad_ollama": self._verificar_ollama()
            }
        except Exception as e:
            return {
                "error": f"Error obteniendo estadísticas: {e}",
                "total_documentos": 0
            }
    
    def _verificar_ollama(self) -> bool:
        """Verifica si Ollama está disponible."""
        try:
            response = requests.get(f"{self.servidor_ollama}/api/tags", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def cerrar(self) -> None:
        """Cierra conexiones y recursos."""
        print("Motor RAG cerrado.")

if __name__ == "__main__":
    # Ejemplo de uso
    print("Motor RAG - Sistema de Búsqueda SupplierHistoryAI")
    print("=" * 50)
    
    # Inicializar motor RAG
    rag = RAGEngine()
    
    # Cargar documentos de ejemplo (ajustar ruta según sistema)
    archivos_documentos = [
        "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_01.docx",
        "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_02.docx",
        "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_03.docx"
    ]
    
    print("Cargando documentos...")
    rag.cargar_documentos(archivos_documentos)
    
    # Realizar búsqueda de ejemplo
    print("\nBuscando por 'calidad técnica...")
    resultados = rag.buscar("calidad técnica incumplimiento", top_k=3)
    
    for i, resultado in enumerate(resultados):
        print(f"\nResultado {i+1}:")
        print(f"Archivo: {resultado.documento_id}")
        print(f"Relevancia: {resultado.relevancia:.2f}")
        print(f"Texto: {resultado.texto[:200]}...")
        print(f"Citas: {len(resultado.citas)} encontradas")
    
    # Generar respuesta con contexto
    if resultados:
        print("\nGenerando respuesta con contexto...")
        consulta = "¿Qué problemas de calidad técnica se mencionan en los contratos?"
        respuesta = rag.generar_respuesta_contexto(consulta, resultados)
        print(f"\nRespuesta: {respuesta}")
    
    # Mostrar estadísticas
    print("\nEstadísticas del Motor RAG:")
    stats = rag.obtener_estadisticas()
    for clave, valor in stats.items():
        print(f"{clave}: {valor}")
    
    # Cerrar motor
    rag.cerrar()