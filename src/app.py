"""
Interfaz principal de Streamlit para SupplierHistoryAI

Sistema de historial inteligente de proveedores con chat RAG 100% local.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Agregar src al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_manager import DataManager
from rag_engine import RAGEngine

# Configuración de la página
st.set_page_config(
    page_title="SupplierHistoryAI - Historial Inteligente de Proveedores",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar componentes
@st.cache_resource
def inicializar_data_manager():
    return DataManager()

@st.cache_resource
def inicializar_rag_engine():
    return RAGEngine()

# Inicializar sesion
def inicializar_sesion():
    if "data_manager" not in st.session_state:
        st.session_state.data_manager = inicializar_data_manager()
    
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = inicializar_rag_engine()
    
    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = []
    
    if "proveedor_seleccionado" not in st.session_state:
        st.session_state.proveedor_seleccionado = None

# Título y descripción
st.title("🏢 SupplierHistoryAI - Historial Inteligente de Proveedores")
st.markdown("""
**Universidad Nacional de Itapúa (UNI)** | **Desafío 6 + Tema Transversal 8** | **IA 100% Local con RAG**

Sistema para centralizar el historial, evaluación de proveedores y control de contratos utilizando inteligencia artificial local (Ollama + ChromaDB).
""")

# Inicializar sesión
inicializar_sesion()

# Barra lateral
with st.sidebar:
    st.header("Navegación")
    
    pagina = st.radio("Ir a:", [
        "📊 Dashboard General",
        "🏢 Gestión de Proveedores",
        "💬 Chat con IA RAG",
        "📋 Análisis Avanzado",
        "⚙️ Configuración"
    ])
    
    st.markdown("---")
    st.header("Datos del Sistema")
    
    data_manager = st.session_state.data_manager
    stats = data_manager.obtener_estadisticas()
    
    st.metric("Total Proveedores", stats["total_proveedores"])
    st.metric("Puntuación Promedio", f"{stats['promedio_puntuacion']:.1f}")
    
    col1, col2 = st.columns(2)
    col1.metric("🟢 Verde", stats["distribucion_semaforo"].get("🟢 Verde", 0))
    col2.metric("🟡 Amarillo", stats["distribucion_semaforo"].get("🟡 Amarillo", 0))
    
    st.metric("🔴 Rojo", stats["distribucion_semaforo"].get("🔴 Rojo", 0))
    
    st.markdown(f"**Última actualización:** {stats['fecha_ultimo_update']}")
    
    st.markdown("---")
    st.header("Estado del Motor RAG")
    
    rag_stats = st.session_state.rag_engine.obtener_estadisticas()
    
    if "error" in rag_stats:
        st.error(rag_stats["error"])
    else:
        st.metric("Documentos Cargados", rag_stats["total_documentos"])
        st.success("✅ Ollama: Disponible" if rag_stats.get("disponibilidad_ollama", False) else "❌ Ollama: No disponible")
    
    if st.button("🔄 Recargar Datos"):
        del st.session_state.data_manager
        st.rerun()

# Renderizar página según selección
if pagina == "📊 Dashboard General":
    renderizar_dashboard(data_manager)
elif pagina == "🏢 Gestión de Proveedores":
    renderizar_gestion_proveedores(data_manager)
elif pagina == "💬 Chat con IA RAG":
    renderizar_chat_rag(st.session_state.rag_engine, data_manager)
elif pagina == "📋 Análisis Avanzado":
    renderizar_analisis_avanzado(data_manager)
elif pagina == "⚙️ Configuración":
    renderizar_configuracion()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        margin: 0.5rem 0;
    }
    
    .provider-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #2a5298;
    }
    
    .semaforo-verde {
        border-left-color: #28a745 !important;
    }
    
    .semaforo-amarillo {
        border-left-color: #ffc107 !important;
    }
    
    .semaforo-rojo {
        border-left-color: #dc3545 !important;
    }
    
    .chat-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .mensaje-user {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: right;
    }
    
    .mensaje-bot {
        background: #f3e5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

def renderizar_dashboard(data_manager):
    """Renderiza el dashboard principal."""
    st.header("📊 Dashboard General - Visión General del Sistema")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Proveedores", data_manager.obtener_estadisticas()["total_proveedores"])
    
    with col2:
        promedio = data_manager.obtener_estadisticas()["promedio_puntuacion"]
        st.metric("Puntuación Promedio", f"{promedio:.1f}")
    
    with col3:
        semaforo_counts = data_manager.obtener_estadisticas()["distribucion_semaforo"]
        st.metric("🟢 Verde", semaforo_counts.get("🟢 Verde", 0))
    
    with col4:
        semaforo_counts = data_manager.obtener_estadisticas()["distribucion_semaforo"]
        st.metric("🔴 Rojo", semaforo_counts.get("🔴 Rojo", 0))
    
    # Gráfico de distribución de semáforos (simulado)
    st.subheader("Distribución de Proveedores por Semáforo")
    
    semaforo_counts = data_manager.obtener_estadisticas()["distribucion_semaforo"]
    total = sum(semaforo_counts.values())
    
    if total > 0:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Utilizar backend no interactivo
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colores = ['#28a745', '#ffc107', '#dc3545']
        etiquetas = ['Verde (Recomendable)', 'Amarillo (Seguimiento)', 'Rojo (Requiere Justificación)']
        valores = [semaforo_counts.get("🟢 Verde", 0), semaforo_counts.get("🟡 Amarillo", 0), semaforo_counts.get("🔴 Rojo", 0)]
        
        bars = ax.bar(etiquetas, valores, color=colores, alpha=0.8)
        ax.set_ylabel('Número de Proveedores')
        ax.set_title('Distribución de Proveedores por Nivel de Riesgo')
        
        # Agregar valores en las barras
        for bar, valor in zip(bars, valores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{valor}', ha='center', va='bottom')
        
        st.pyplot(fig)
    
    # Proveedores destacados
    st.subheader("🏢 Proveedores Destacados")
    
    proveedores = data_manager.obtener_todos_los_proveedores()
    
    # Ordenar por puntuación global
    proveedores_ordenados = sorted(proveedores, key=lambda x: x.puntuacion_global, reverse=True)[:3]
    
    for proveedor in proveedores_ordenados:
        with st.container():
            with st.columns([1, 3]):
                st.write(f"**{proveedor.id}** - {proveedor.nombre}")
                st.write(f"**Puntuación:** {proveedor.puntuacion_global:.1f}")
                st.write(f"**Semáforo:** {proveedor.semaforo}")
                if proveedor.alerta_contradiccion:
                    st.warning(f"⚠️ {proveedor.alerta_contradiccion}")

def renderizar_gestion_proveedores(data_manager):
    """Renderiza la gestión de proveedores."""
    st.header("🏢 Gestión de Proveedores")
    
    proveedores = data_manager.obtener_todos_los_proveedores()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_nombre = st.text_input("Filtrar por nombre")
    
    with col2:
        filtro_semaforo = st.selectbox("Filtrar por semáforo", ["Todos"] + [
            "🟢 Verde (Recomendable)",
            "🟡 Amarillo (Con seguimiento)",
            "🔴 Rojo (Requiere justificación especial)"
        ])
    
    with col3:
        ordenar_por = st.selectbox("Ordenar por", ["Puntuación Global (Mayor)", "Nombre (A-Z)", "Total Contratos (Mayor)"])
    
    # Aplicar filtros
    proveedores_filtrados = proveedores
    
    if filtro_nombre:
        proveedores_filtrados = [
            p for p in proveedores_filtrados 
            if filtro_nombre.lower() in p.nombre.lower()
        ]
    
    if filtro_semaforo != "Todos":
        proveedores_filtrados = [
            p for p in proveedores_filtrados 
            if p.semaforo == filtro_semaforo
        ]
    
    if ordenar_por == "Puntuación Global (Mayor)":
        proveedores_filtrados = sorted(proveedores_filtrados, key=lambda x: x.puntuacion_global, reverse=True)
    elif ordenar_por == "Nombre (A-Z)":
        proveedores_filtrados = sorted(proveedores_filtrados, key=lambda x: x.nombre)
    elif ordenar_por == "Total Contratos (Mayor)":
        proveedores_filtrados = sorted(proveedores_filtrados, key=lambda x: len(x.contratos), reverse=True)
    
    # Mostrar proveedores
    for proveedor in proveedores_filtrados:
        with st.container():
            clase_semaforo = "semaforo-verde" if "Verde" in proveedor.semaforo else "semaforo-amarillo" if "Amarillo" in proveedor.semaforo else "semaforo-rojo"
            
            st.markdown(f"""
            <div class="provider-card {clase_semaforo}">
                <h3>{proveedor.id} - {proveedor.nombre}</h3>
                <p><strong>RUCL:</strong> {proveedor.ruc}</p>
                <p><strong>Puntuación Global:</strong> {proveedor.puntuacion_global:.1f}</p>
                <p><strong>Semáforo:</strong> {proveedor.semaforo}</p>
                <p><strong>Total Contratos:</strong> {len(proveedor.contratos)}</p>
                <p><strong>Ultimo atraso:</strong> {max((c.dias_atraso for c in proveedor.contratos), default=0)} días</p>
            </div>
            """, unsafe_allow_html=True)
            
            if proveedor.alerta_contradiccion:
                st.warning(f"⚠️ {proveedor.alerta_contradiccion}")
            
            # Detalles del proveedor
            if st.button(f"Ver detalles de {proveedor.nombre}", key=proveedor.id):
                st.session_state.proveedor_seleccionado = proveedor
                st.rerun()
    
    # Modal de detalles del proveedor
    if st.session_state.proveedor_seleccionado:
        proveedor = st.session_state.proveedor_seleccionado
        
        st.header(f"Detalles del Proveedor - {proveedor.nombre}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**ID:** {proveedor.id}")
            st.write(f"**Nombre:** {proveedor.nombre}")
            st.write(f"**RUCL:** {proveedor.ruc}")
            st.write(f"**Puntuación Global:** {proveedor.puntuacion_global:.1f}")
            st.write(f"**Semáforo:** {proveedor.semaforo}")
        
        with col2:
            st.write(f"**Total Contratos:** {len(proveedor.contratos)}")
            
            # Estadísticas de contratos
            atrasos = [c.dias_atraso for c in proveedor.contratos]
            montos = [c.monto_adjudicado for c in proveedor.contratos]
            calidades = [c.calidad_tecnica for c in proveedor.contratos]
            
            st.write(f"**Promedio de Atraso:** {sum(atrasos)/len(atrasos) if atrasos else 0:.1f} días")
            st.write(f"**Monto Total Adjudicado:** ${sum(montos):,.0f}")
            st.write(f"**Calidad Técnica Promedio:** {sum(calidades)/len(calidades) if calidades else 0:.1f}")
        
        # Detalles de contratos
        st.subheader("Contratos")
        for contrato in proveedor.contratos:
            with st.expander(f"Contrato {contrato.contrato_id} - Atraso: {contrato.dias_atraso} días"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**ID Contrato:** {contrato.contrato_id}")
                    st.write(f"**Fecha Comprometida:** {contrato.fecha_comprometida}")
                    st.write(f"**Fecha Entrega Real:** {contrato.fecha_entrega_real}")
                    st.write(f"**Días de Atraso:** {contrato.dias_atraso}")
                
                with col2:
                    st.write(f"**Monto Adjudicado:** ${contrato.monto_adjudicado:,}")
                    st.write(f"**Multa Aplicada:** ${contrato.multa_aplicada:,}")
                    st.write(f"**Calidad Técnica:** {contrato.calidad_tecnica}/5")
                    st.write(f"**Satisfacción:** {contrato.satisfaccion}/5")
                
                with col3:
                    st.write(f"**Dependencia:** {contrato.dependencia_evaluadora}")
                    st.write(f"**Reclamos:** {len(contrato.reclamos)}")
                    st.write(f"**Observaciones Técnicas:** {len(contrato.observaciones_tecnicas)}")
                
                if contrato.reclamos:
                    st.write("**Reclamos:**")
                    for reclamo in contrato.reclamos:
                        st.write(f"  - {reclamo['fecha']}: {reclamo['descripcion']} ({reclamo['estado']})")
                
                if contrato.observaciones_tecnicas:
                    st.write("**Observaciones Técnicas:**")
                    for obs in contrato.observaciones_tecnicas:
                        st.write(f"  - {obs['fecha']} ({obs['autor']}): {obs['texto']} - **Hecho:** {obs['es_hecho']}")
        
        if st.button("❌ Cerrar Detalles"):
            st.session_state.proveedor_seleccionado = None
            st.rerun()

def renderizar_chat_rag(rag_engine, data_manager):
    """Renderiza el chat RAG."""
    st.header("💬 Chat con IA RAG - Consulta de Proveedores")
    
    # Cargar documentos si no están cargados
    if rag_engine.obtener_estadisticas().get("total_documentos", 0) == 0:
        st.info("Cargando documentos para RAG...")
        archivos_documentos = [
            "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_01.docx",
            "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_02.docx",
            "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_03.docx",
            "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_04.docx",
            "/opt/supplier_history_ai/DocumentosAnonimizados/Documentos Anonimizados/Documento_Anonimizado_05.docx"
        ]
        
        rag_engine.cargar_documentos(archivos_documentos)
    
    # Mostrar estado RAG
    rag_stats = rag_engine.obtener_estadisticas()
    if "error" not in rag_stats:
        st.success(f"✅ Base de datos vectorial cargada: {rag_stats['total_documentos']} documentos")
    
    # Área de chat
    st.subheader("Chat con IA Local")
    
    # Mostrar mensajes anteriores
    for mensaje in st.session_state.mensajes_chat:
        if mensaje["tipo"] == "usuario":
            st.markdown(f"""
            <div class="mensaje-user">
                <strong>👤 Tú:</strong> {mensaje["texto"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="mensaje-bot">
                <strong>🤖 IA RAG:</strong> {mensaje["texto"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Input para nueva consulta
    consulta = st.chat_input("¿Sobre qué proveedor o contrato deseas consultar?")
    
    if consulta:
        # Agregar mensaje del usuario
        st.session_state.mensajes_chat.append({
            "tipo": "usuario",
            "texto": consulta,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Mostrar mensaje del usuario
        st.markdown(f"""
        <div class="mensaje-user">
            <strong>👤 Tú:</strong> {consulta}
        </div>
        """, unsafe_allow_html=True)
        
        # Realizar búsqueda y generar respuesta
        with st.spinner("Buscando en documentos..."):
            resultados = rag_engine.buscar(consulta, top_k=3)
            
            if resultados:
                respuesta = rag_engine.generar_respuesta_contexto(consulta, resultados)
                
                # Agregar respuesta del bot
                st.session_state.mensajes_chat.append({
                    "tipo": "bot",
                    "texto": respuesta,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "resultados_encontrados": len(resultados)
                })
                
                # Mostrar respuesta
                st.markdown(f"""
                <div class="mensaje-bot">
                    <strong>🤖 IA RAG:</strong> {respuesta}
                    <br><small><em>Basado en {len(resultados)} documentos relevantes | {datetime.now().strftime("%H:%M")}</em></small>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar documentos relevantes
                if st.checkbox("Ver documentos fuente:"):
                    for i, resultado in enumerate(resultados):
                        with st.expander(f"📄 Documento {i+1}: {resultado.documento_id} (Relevancia: {resultado.relevancia:.2f})"):
                            st.write(resultado.texto)
                            if resultado.citas:
                                st.write("**Citas relevantes:**")
                                for cita in resultado.citas:
                                    st.write(f"  - Oración {cita['numero_oracion']}: {cita['texto_oracion']}")
            else:
                st.error("No se encontraron documentos relevantes para tu consulta.")
                
                # Agregar respuesta de fallback
                st.session_state.mensajes_chat.append({
                    "tipo": "bot",
                    "texto": "No tengo información suficiente en los documentos proporcionados para responder a tu consulta.",
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                st.markdown(f"""
                <div class="mensaje-bot">
                    <strong>🤖 IA RAG:</strong> No tengo información suficiente en los documentos proporcionados para responder a tu consulta.
                </div>
                """, unsafe_allow_html=True)
        
        st.rerun()

def renderizar_analisis_avanzado(data_manager):
    """Renderiza análisis avanzado."""
    st.header("📋 Análisis Avanzado - Insights y Tendencias")
    
    proveedores = data_manager.obtener_todos_los_proveedores()
    
    if not proveedores:
        st.info("No hay datos disponibles para análisis.")
        return
    
    # Análisis de correlaciones
    st.subheader("📊 Correlaciones entre Métricas")
    
    # Calcular correlaciones básicas
    retrasos = [sum(c.dias_atraso for c in p.contratos) / len(p.contratos) if p.contratos else 0 for p in proveedores]
    calidades = [sum(c.calidad_tecnica for c in p.contratos) / len(p.contratos) if p.contratos else 0 for p in proveedores]
    satisfacciones = [sum(c.satisfaccion for c in p.contratos) / len(p.contratos) if p.contratos else 0 for p in proveedores]
    
    # Crear DataFrame para análisis
    import pandas as pd
    df = pd.DataFrame({
        'proveedor': [p.nombre for p in proveedores],
        'retraso_promedio': retrasos,
        'calidad_promedio': calidades,
        'satisfaccion_promedio': satisfacciones,
        'puntuacion_global': [p.puntuacion_global for p in proveedores]
    })
    
    # Mostrar estadísticas descriptivas
    st.write("**Estadísticas Descriptivas:**")
    st.dataframe(df.describe(), use_container_width=True)
    
    # Gráfico de correlación (simplificado)
    st.subheader("Gráfico de Correlación (Matriz)")
    
    import numpy as np
    
    # Calcular matriz de correlación
    correlacion = df[['retraso_promedio', 'calidad_promedio', 'satisfaccion_promedio', 'puntuacion_global']].corr()
    
    # Mostrar matriz de correlación
    st.dataframe(correlacion, use_container_width=True)
    
    # Análisis de proveedores de alto rendimiento
    st.subheader("🏆 Proveedores de Alto Rendimiento")
    
    # Encontrar proveedores con mayor puntuación global
    mejores_proveedores = sorted(proveedores, key=lambda x: x.puntuacion_global, reverse=True)[:3]
    
    for proveedor in mejores_proveedores:
        with st.container():
            st.write(f"**{proveedor.id} - {proveedor.nombre}**")
            st.write(f"Puntuación: {proveedor.puntuacion_global:.1f}")
            st.write(f"Razón: Excelente en plazo ({all(c.dias_atraso == 0 for c in proveedor.contratos)}), "
                    f"calidad {sum(c.calidad_tecnica for c in proveedor.contratos)/len(proveedor.contratos):.1f}/5, "
                    f"satisfacción {sum(c.satisfaccion for c in proveedor.contratos)/len(proveedor.contratos):.1f}/5")
            
            # Mostrar contratos destacados
            st.write("**Contratos Destacados:**")
            for contrato in proveedor.contratos[:2]: n
            {
                st.write(f"  - {contrato.contrato_id}: {contrato.fecha_entrega_real} (Atraso: {contrato.dias_atraso} días)")
            }
            
            st.markdown("---")
    
    # Análisis de proveedores de riesgo
    st.subheader("⚠️ Proveedores de Alto Riesgo")
    
    # Proveedores con semáforo rojo
    proveedores_riesgo = [p for p in proveedores if p.semaforo and "Rojo" in p.semaforo]
    
    if proveedores_riesgo:
        for proveedor in proveedores_riesgo:
            with st.container():
                st.error(f"**{proveedor.id} - {proveedor.nombre}** - {proveedor.semaforo}")
                st.write(f"Puntuación Global: {proveedor.puntuacion_global:.1f}")
                
                # Identificar problemas
                total_atraso = sum(c.dias_atraso for c in proveedor.contratos)
                total_multa = sum(c.multa_aplicada for c in proveedor.contratos)
                
                st.write(f"Total de atrasos: {total_atraso} días")
                st.write(f"Total de multas aplicadas: ${total_multa:,}")
                
                st.write("**Contratos Problemáticos:**")
                for contrato in proveedor.contratos:
                    if contrato.dias_atraso > 5 or contrato.multa_aplicada > 0:
                        st.write(f"  - {contrato.contrato_id}: Atraso {contrato.dias_atraso} días, Multa ${contrato.multa_aplicada:,}")
    
    else:
        st.success("✅ No hay proveedores de alto riesgo en el sistema actual.")

def renderizar_configuracion():
    """Renderiza la configuración del sistema."""
    st.header("⚙️ Configuración del Sistema")
    
    st.subheader("Configuración del Motor RAG")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Modelo de Embedding:**")
        st.code("all-MiniLM-L6-v2")
    
    with col2:
        st.write("**Servidor Ollama:**")
        st.code("http://localhost:11434")
    
    st.write("**Modelo LLM:**")
    st.code("llama3:8b")
    
    st.subheader("Información del Sistema")
    
    import platform
    import sys
    
    st.write(f"**Sistema Operativo:** {platform.system()} {platform.release()}")
    st.write(f"**Versión Python:** {platform.python_version()}")
    st.write(f"**Arquitectura:** {platform.machine()}")
    st.write(f"**Python Path:** {sys.executable}")
    
    st.subheader("Controles de Sistema")
    
    if st.button("🔄 Reiniciar Motor RAG"):
        st.cache_resource.clear()
        st.success("Motor RAG reiniciado")
    
    if st.button("💾 Guardar Estado Actual"):
        st.success("Estado guardado (simulado)")
    
    if st.button("📊 Generar Reporte de Diagnóstico"):
        with st.spinner("Generando reporte..."):
            # Simular generación de reporte
            reporte = f"""
            # Reporte de Diagnóstico - SupplierHistoryAI
            # Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            # Estado: Operativo
            # Proveedores: {len(st.session_state.data_manager.obtener_todos_los_proveedores())}
            # Documentos RAG: {st.session_state.rag_engine.obtener_estadisticas().get('total_documentos', 0)}
            """
            st.code(reporte)
            st.success("Reporte generado")