"""
===============================================================================
  Exonik - Esquema común de una enfermedad (Disease)
===============================================================================

`Disease` es el contrato que cualquier enfermedad debe cumplir para que el
pipeline de Exonik (Fases 1-6) pueda procesarla sin cambios de código.

Contiene TODO lo que hoy estaba "cableado" a la Anemia Falciforme dentro de
`config.py`, pero con nombres genéricos (independientes del gen). `config.py`
se encarga de mapear estos campos genéricos a los nombres legacy que las
fases ya importan (HBB_*, SCA_*, BCL11A_*), de modo que el caso SCA sigue
funcionando idéntico.

Cómo añadir una enfermedad nueva:
  1. Crear diseases/<mi_enfermedad>.py
  2. Definir una instancia `DISEASE = Disease(...)`
  3. Registrarla en DISEASE_REGISTRY (abajo) o importarla en config.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import importlib


# =============================================================================
# ESTRATEGIAS TERAPÉUTICAS SOPORTADAS
# =============================================================================
# Determina cómo se interpreta el target y qué guías se buscan.
#   correccion   : corregir una mutación puntual (SNP) de vuelta a la referencia
#   knockout     : inactivar un alelo tóxico (ganancia de función)
#   enhancer     : disrumpir un enhancer regulatorio (ej. reactivar HbF)
#   augmentacion : aportar una copia funcional vía ARNm/vector (no se corta ADN)
ESTRATEGIAS = ("correccion", "knockout", "enhancer", "augmentacion")


@dataclass(frozen=True)
class Disease:
    """Definición completa de una enfermedad para el pipeline Exonik."""

    # --- Identidad ---
    key: str                       # identificador corto (ej. "sca")
    nombre: str                    # nombre legible (ej. "Anemia Falciforme")
    gene: str                      # gen target (ej. "HBB")
    cromosoma: str                 # cromosoma (ej. "chr11")
    herencia: str                  # patrón de herencia
    estrategia: str                # una de ESTRATEGIAS

    # --- Secuencias del gen (target primario) ---
    cds_normal: str                # CDS de referencia (proteína sana)
    cds_mutante: str               # CDS con la variante patogénica
    proteina_normal: str           # proteína de referencia
    proteina_mutante: str          # proteína con la variante

    # --- Variante patogénica en el CDS ---
    variante_pos_cds: int          # posición 0-indexed en el CDS
    variante_ref: str              # nucleótido de referencia
    variante_alt: str              # nucleótido mutado
    variante_rs_id: str            # rsID en dbSNP (o "" si no aplica)
    codon_normal: str              # codón de referencia
    codon_mutante: str             # codón mutado

    # --- Región genómica para diseño de guías CRISPR ---
    region_genomica: str           # ventana genómica (±flancos) alrededor de la mutación
    atg_offset: int                # posición del ATG dentro de region_genomica
    pos_genomica_mutacion: int     # coordenada genómica (GRCh38) de la variante

    # --- CDS a expresar como ARNm terapéutico (por defecto = cds_normal) ---
    # Para 'augmentacion' esto puede ser una copia optimizada del gen sano.
    cds_terapeutico: Optional[str] = None

    # --- Target secundario / estrategia alternativa (opcional) ---
    # En SCA: enhancer eritroide de BCL11A (reactiva HbF).
    # Enfermedades sin estrategia alternativa dejan esto en None.
    alt_nombre: Optional[str] = None
    alt_region: Optional[str] = None
    alt_cromosoma: Optional[str] = None
    alt_pos_inicio: Optional[int] = None
    alt_pos_fin: Optional[int] = None

    # --- Prefijos para nombrar guías CRISPR (compatibilidad con IDs existentes) ---
    # Por defecto el prefijo primario = gen. El alternativo = alt_nombre.
    # En SCA se fija alt_guide_prefix="BCL" para conservar los IDs ya validados.
    guide_prefix: Optional[str] = None
    alt_guide_prefix: Optional[str] = None

    # --- Metadatos para pitch / reportes ---
    prevalencia: str = ""          # texto libre (ej. "~20-25M en el mundo")
    terapia_aprobada: str = ""     # estado de terapia aprobada (para narrativa)
    uniprot_id: str = ""           # para AlphaFold / Fase 6
    poblaciones_interes: tuple = field(default_factory=tuple)

    # --- Etiquetas de presentacion para el reporte de ARNm (Fase 4) ---
    # Vacio => la Fase 4 usa un texto por defecto derivado del gen.
    proteina_nombre: str = ""      # ej. "Hemoglobina Beta (HBB) normal"
    proteina_funcion: str = ""     # ej. "Transporte de oxigeno en eritrocitos"
    terapia_objetivo: str = ""     # objetivo terapeutico (1 linea)
    tejido_objetivo: str = ""      # tejido/celula diana de la entrega
    targeting: str = ""            # ligando/estrategia de targeting
    nota_inmunogenicidad: str = "" # nota final de la seccion de inmunogenicidad

    def __post_init__(self):
        if self.estrategia not in ESTRATEGIAS:
            raise ValueError(
                f"Estrategia '{self.estrategia}' no válida para {self.key}. "
                f"Usar una de: {ESTRATEGIAS}"
            )

    @property
    def prefijo_guia(self) -> str:
        """Prefijo para nombrar guías del target primario (ej. 'HBB', 'GBA1')."""
        return self.guide_prefix or self.gene

    @property
    def prefijo_guia_alt(self) -> str:
        """Prefijo para nombrar guías del target secundario (ej. 'BCL')."""
        return self.alt_guide_prefix or (self.alt_nombre or "ALT")

    @property
    def cds_para_arnm(self) -> str:
        """CDS que se usará para diseñar el ARNm terapéutico."""
        return self.cds_terapeutico or self.cds_normal

    @property
    def tiene_target_secundario(self) -> bool:
        return self.alt_region is not None


# =============================================================================
# REGISTRO DE ENFERMEDADES
# =============================================================================
# Mapea la clave (EXONIK_DISEASE) al módulo que contiene la instancia DISEASE.
# Se cargan de forma perezosa (lazy) para no importar todo siempre.

DISEASE_REGISTRY = {
    "sca": "diseases.sca",
    "beta_thal": "diseases.beta_thal",
    "parkinson_gba1": "diseases.parkinson_gba1",
}


def get_disease(key: str) -> Disease:
    """Devuelve la instancia Disease para la clave dada."""
    key = (key or "sca").strip().lower()
    if key not in DISEASE_REGISTRY:
        disponibles = ", ".join(sorted(DISEASE_REGISTRY))
        raise ValueError(
            f"Enfermedad '{key}' no registrada. Disponibles: {disponibles}"
        )
    modulo = importlib.import_module(DISEASE_REGISTRY[key])
    disease = getattr(modulo, "DISEASE", None)
    if not isinstance(disease, Disease):
        raise TypeError(
            f"El módulo {DISEASE_REGISTRY[key]} no define una instancia "
            f"'DISEASE' de tipo Disease."
        )
    return disease
