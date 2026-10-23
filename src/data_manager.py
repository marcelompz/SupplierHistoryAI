# coding=utf-8
"""
Gestor de datos para SupplierHistoryAI

Maneja la carga, actualización y cálculo de puntuaciones de proveedores.
Implementa la fórmula semáforo descrita en el plan de desarrollo.
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os

@dataclass
class Contrato:
    """Representa un contrato con sus métricas de evaluación."""
    contrato_id: str
    fecha_comprometida: str
    fecha_entrega_real: str
    dias_atraso: int
    monto_adjudicado: float
    multa_aplicada: float
    calidad_tecnica: int  # 1-5
    satisfaccion: int     # 1-5
    dependencia_evaluadora: str
    reclamos: List[Dict]
    observaciones_tecnicas: List[Dict]
    documento_origen: str

@dataclass
class Proveedor:
    """Representa un proveedor con sus contratos y puntuación global."""
    id: str
    nombre: str
    ruc: str
    contratos: List[Contrato]
    puntuacion_global: Optional[float] = None
    semaforo: Optional[str] = None
    alerta_contradiccion: Optional[str] = None

class DataManager:
    """Gestor central de datos de proveedores con lógica de negocio."""
    
    def __init__(self, archivo_datos: str = "data/database.json"):
        self.archivo_datos = archivo_datos
        self.proveedores: List[Proveedor] = []
        self.cargar_datos()
    
    def cargar_datos(self) -> None:
        """Carga los datos de proveedores desde archivo JSON."""
        try:
            if os.path.exists(self.archivo_datos):
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                self.proveedores = []
                for prov_data in datos.get("proveedores", []):
                    contratos = [
                        Contrato(
                            c["contrato_id"],
                            c["fecha_comprometida"], 
                            c["fecha_entrega_real"],
                            c["dias_atraso"],
                            c["monto_adjudicado"],
                            c["multa_aplicada"],
                            c["calidad_tecnica"],
                            c["satisfaccion"],
                            c["dependencia_evaluadora"],
                            c.get("reclamos", []),
                            c.get("observaciones_tecnicas", []),
                            c["documento_origen"]
                        ) for c in prov_data.get("contratos", [])
                    ]
                    
                    proveedor = Proveedor(
                        prov_data["id"],
                        prov_data["nombre"],
                        prov_data["ruc"],
                        contratos
                    )
                    
                    proveedor.puntuacion_global = self.calcular_puntuacion_global(proveedor)
                    proveedor.semaforo = self.determinar_semaforo(proveedor)
                    proveedor.alerta_contradiccion = self.verificar_contradiccion(proveedor)
                    
                    self.proveedores.append(proveedor)
            else:
                self._crear_datos_iniciales()
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self._crear_datos_iniciales()
    
    def _crear_datos_iniciales(self) -> None:
        """Crea datos iniciales de ejemplo si no existe archivo."""
        # Datos de ejemplo basados en el plan
        contrato1 = Contrato(
            "CONT-2025-012", "2025-06-15", "2025-06-14", 0, 45000000, 0,
            5, 5, "Dirección de Tecnologías de la Información", [],
            [{"fecha": "2025-06-16", "autor": "Ing. Carlos Gómez", 
              "tipo": "Soporte", "texto": "Equipamiento entregado en óptimas condiciones.",
              "es_hecho": True}],
            "data/raw_docs/contrato_012_soluciones.pdf"
        )
        
        contrato2 = Contrato(
            "CONT-2025-045", "2025-09-30", "2025-09-28", 0, 120000000, 0,
            2, 2, "Departamento de Infraestructura y Mantenimiento", [
                {"fecha": "2025-10-05", "tipo": "Calidad", 
                 "descripcion": "Defectos en terminaciones de pintura.",
                 "estado": "Resuelto con demora"}
            ], [
                {"fecha": "2025-10-02", "autor": "Arq. María Benítez", 
                 "tipo": "Calidad", "texto": "Cumplió en plazo formalmente, pero calidad deficiente.",
                 "es_hecho": False}
            ], "data/raw_docs/contrato_045_constructora.pdf"
        )
        
        contrato3 = Contrato(
            "CONT-2026-003", "2026-02-10", "2026-02-25", 15, 15000000, 750000,
            3, 2, "Dirección General Administrativa", [
                {"fecha": "2026-02-12", "tipo": "Plazo", 
                 "descripcion": "Demora injustificada.",
                 "estado": "Cerrado con multa"},
                {"fecha": "2026-02-20", "tipo": "Plazo",
                 "descripcion": "Segunda demora consecutiva.",
                 "estado": "Registrado"}
            ], [
                {"fecha": "2026-02-26", "autor": "Lic. Juan Pérez",
                 "tipo": "Plazo", "texto": "Proveedor reincidente en plazos.",
                 "es_hecho": True}
            ], "data/raw_docs/contrato_003_papelera.pdf"
        )
        
        proveedor1 = Proveedor("PROV-001", "Soluciones Tecnológicas S.A.", 
                              "80012345-6", [contrato1])
        proveedor2 = Proveedor("PROV-002", "Constructora e Inmobiliaria del Sur",
                              "80098765-4", [contrato2])
        proveedor3 = Proveedor("PROV-003", "Papelera y Librería Central",
                              "80055544-1", [contrato3])
        
        for proveedor in [proveedor1, proveedor2, proveedor3]:
            proveedor.puntuacion_global = self.calcular_puntuacion_global(proveedor)
            proveedor.semaforo = self.determinar_semaforo(proveedor)
            proveedor.alerta_contradiccion = self.verificar_contradiccion(proveedor)
            self.proveedores.append(proveedor)
        
        self.guardar_datos()
    
    def calcular_puntuacion_global(self, proveedor: Proveedor) -> float:
        """Calcula la puntuación global usando la fórmula del plan."""
        total_puntaje = 0.0
        
        for contrato in proveedor.contratos:
            # Componente plazo (peso 0.30)
            if contrato.dias_atraso == 0:
                puntaje_plazo = 100
            elif contrato.dias_atraso <= 5:
                puntaje_plazo = 80
            elif contrato.dias_atraso <= 10:
                puntaje_plazo = 60
            elif contrato.dias_atraso <= 20:
                puntaje_plazo = 40
            else:
                puntaje_plazo = 20
            
            # Componente calidad (peso 0.30)
            puntaje_calidad = contrato.calidad_tecnica * 20  # 1-5 se convierte a 20-100
            
            # Componente satisfacción (peso 0.25)
            puntaje_satisfaccion = contrato.satisfaccion * 20
            
            # Componente reclamos (peso 0.15)
            reclamos_graves = len([r for r in contrato.reclamos if r.get("estado") == "Cerrado con multa"])
            puntaje_reclamos = max(0, 100 - (reclamos_graves * 25))
            
            puntaje_contrato = (
                0.30 * puntaje_plazo +
                0.30 * puntaje_calidad +
                0.25 * puntaje_satisfaccion +
                0.15 * puntaje_reclamos
            )
            
            total_puntaje += puntaje_contrato
        
        return total_puntaje / len(proveedor.contratos) if proveedor.contratos else 0
    
    def determinar_semaforo(self, proveedor: Proveedor) -> str:
        """Determina el semáforo según la puntuación y reincidencias."""
        if proveedor.puntuacion_global >= 75:
            # Verificar reincidencias
            total_reincidencias = sum(
                1 for contrato in proveedor.contratos 
                for obs in contrato.observaciones_tecnicas
                if obs.get("es_hecho", False) and "reincidente" in obs.get("texto", "").lower()
            )
            
            if total_reincidencias == 0:
                return "🟢 Verde (Recomendable)"
            elif total_reincidencias == 1:
                return "🟡 Amarillo (Con seguimiento)"
        
        elif proveedor.puntuacion_global >= 50:
            return "🟡 Amarillo (Con seguimiento)"
        
        else:
            return "🔴 Rojo (Requiere justificación especial)"
    
    def verificar_contradiccion(self, proveedor: Proveedor) -> Optional[str]:
        """Verifica contradicción entre plazo y calidad."""
        for contrato in proveedor.contratos:
            if contrato.dias_atraso == 0 and contrato.calidad_tecnica < 50:
                return "Cumplió formalmente en plazo, pero con resultado deficiente"
        return None
    
    def agregar_nuevo_proveedor(self, nombre: str, ruc: str, 
                              contratos: List[Dict]) -> Proveedor:
        """Agrega un nuevo proveedor al sistema."""
        nuevo_id = f"PROV-{len(self.proveedores) + 1:03d}"
        
        contratos_obj = []
        for c in contratos:
            contratos_obj.append(Contrato(
                c["contrato_id"], c["fecha_comprometida"], c["fecha_entrega_real"],
                c["dias_atraso"], c["monto_adjudicado"], c["multa_aplicada"],
                c["calidad_tecnica"], c["satisfaccion"], c["dependencia_evaluadora"],
                c.get("reclamos", []), c.get("observaciones_tecnicas", []),
                c.get("documento_origen", "")
            ))
        
        nuevo_proveedor = Proveedor(nuevo_id, nombre, ruc, contratos_obj)
        nuevo_proveedor.puntuacion_global = self.calcular_puntuacion_global(nuevo_proveedor)
        nuevo_proveedor.semaforo = self.determinar_semaforo(nuevo_proveedor)
        nuevo_proveedor.alerta_contradiccion = self.verificar_contradiccion(nuevo_proveedor)
        
        self.proveedores.append(nuevo_proveedor)
        self.guardar_datos()
        
        return nuevo_proveedor
    
    def actualizar_contrato(self, id_proveedor: str, id_contrato: str, 
                           actualizaciones: Dict) -> bool:
        """Actualiza un contrato existente."""
        for proveedor in self.proveedores:
            if proveedor.id == id_proveedor:
                for contrato in proveedor.contratos:
                    if contrato.contrato_id == id_contrato:
                        # Aplicar actualizaciones
                        for campo, valor in actualizaciones.items():
                            if hasattr(contrato, campo):
                                setattr(contrato, campo, valor)
                        
                        # Recalcular puntuaciones
                        proveedor.puntuacion_global = self.calcular_puntuacion_global(proveedor)
                        proveedor.semaforo = self.determinar_semaforo(proveedor)
                        proveedor.alerta_contradiccion = self.verificar_contradiccion(proveedor)
                        
                        self.guardar_datos()
                        return True
        return False
    
    def buscar_proveedor(self, filtro: Dict) -> List[Proveedor]:
        """Busca proveedores según criterios de filtro."""
        resultados = []
        
        for proveedor in self.proveedores:
            coincide = True
            
            for campo, valor in filtro.items():
                if campo == "id" and proveedor.id != valor:
                    coincide = False
                    break
                elif campo == "nombre" and valor.lower() not in proveedor.nombre.lower():
                    coincide = False
                    break
                elif campo == "semaforo" and proveedor.semaforo != valor:
                    coincide = False
                    break
            
            if coincide:
                resultados.append(proveedor)
        
        return resultados
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema."""
        total_proveedores = len(self.proveedores)
        promedio_puntuacion = sum(p.puntuacion_global for p in self.proveedores) / total_proveedores if total_proveedores > 0 else 0
        
        semaforo_counts = {
            "🟢 Verde": len([p for p in self.proveedores if p.semaforo and "Verde" in p.semaforo]),
            "🟡 Amarillo": len([p for p in self.proveedores if p.semaforo and "Amarillo" in p.semaforo]),
            "🔴 Rojo": len([p for p in self.proveedores if p.semaforo and "Rojo" in p.semaforo])
        }
        
        return {
            "total_proveedores": total_proveedores,
            "promedio_puntuacion": round(promedio_puntuacion, 2),
            "distribucion_semaforo": semaforo_counts,
            "fecha_ultimo_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def guardar_datos(self) -> None:
        """Guarda los datos en archivo JSON."""
        datos = {
            "proveedores": [
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "ruc": p.ruc,
                    "contratos": [
                        {
                            "contrato_id": c.contrato_id,
                            "fecha_comprometida": c.fecha_comprometida,
                            "fecha_entrega_real": c.fecha_entrega_real,
                            "dias_atraso": c.dias_atraso,
                            "monto_adjudicado": c.monto_adjudicado,
                            "multa_aplicada": c.multa_aplicada,
                            "calidad_tecnica": c.calidad_tecnica,
                            "satisfaccion": c.satisfaccion,
                            "dependencia_evaluadora": c.dependencia_evaluadora,
                            "reclamos": c.reclamos,
                            "observaciones_tecnicas": c.observaciones_tecnicas,
                            "documento_origen": c.documento_origen
                        } for c in p.contratos
                    ],
                    "puntuacion_global": p.puntuacion_global,
                    "semaforo": p.semaforo,
                    "alerta_contradiccion": p.alerta_contradiccion
                } for p in self.proveedores
            ]
        }
        
        try:
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando datos: {e}")
    
    def obtener_proveedor(self, id_proveedor: str) -> Optional[Proveedor]:
        """Obtiene un proveedor por su ID."""
        for proveedor in self.proveedores:
            if proveedor.id == id_proveedor:
                return proveedor
        return None
    
    def obtener_todos_los_proveedores(self) -> List[Proveedor]:
        """Retorna todos los proveedores."""
        return self.proveedores.copy()

if __name__ == "__main__":
    # Ejemplo de uso
    manager = DataManager()
    print("Sistema de Gestión de Proveedores SupplierHistoryAI")
    print("=" * 50)
    
    # Mostrar estadísticas
    stats = manager.obtener_estadisticas()
    print(f"Total de proveedores: {stats['total_proveedores']}")
    print(f"Puntuación promedio: {stats['promedio_puntuacion']}")
    print(f"Distribución de semáforos: {stats['distribucion_semaforo']}")
    
    # Mostrar todos los proveedores
    print("\nProveedores:")
    for proveedor in manager.obtener_todos_los_proveedores():
        print(f"\n{proveedor.id}: {proveedor.nombre}")
        print(f"  Puntuación: {proveedor.puntuacion_global:.1f}")
        print(f"  Semáforo: {proveedor.semaforo}")
        if proveedor.alerta_contradiccion:
            print(f"  ⚠️  Advertencia: {proveedor.alerta_contradiccion}")
        print(f"  Contratos: {len(proveedor.contratos)}")
        for contrato in proveedor.contratos:
            print(f"    - {contrato.contrato_id} (Atraso: {contrato.dias_atraso} días)")