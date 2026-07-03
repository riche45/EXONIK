"""
===============================================================================
  Exonik - Plataforma de Diseño de Terapia Génica Personalizada
  CONFIGURACIÓN CENTRAL (cargador multi-enfermedad)
  Versión: 0.2.0 (Plataforma modular)
===============================================================================

Este archivo cumple dos funciones:

  1. CONSTANTES GENÉRICAS (independientes de la enfermedad): tablas de codones,
     nucleasas CRISPR, genes críticos, configuración de ARNm, etc.

  2. CARGADOR DE LA ENFERMEDAD ACTIVA: selecciona una enfermedad del paquete
     `diseases/` (según la variable de entorno EXONIK_DISEASE, por defecto
     "sca") y re-exporta sus datos bajo los MISMOS nombres que el pipeline ya
     usaba para la Anemia Falciforme (HBB_*, SCA_*, BCL11A_*).

Esto hace la plataforma modular por enfermedad SIN romper nada: si no defines
EXONIK_DISEASE, todo se comporta EXACTAMENTE igual que antes (SCA).

Cómo cambiar de enfermedad:
    # Windows PowerShell
    $env:EXONIK_DISEASE = "parkinson_gba1"; python fase_01_genomas_reales.py
    # Linux / macOS
    EXONIK_DISEASE=beta_thal python fase_01_genomas_reales.py
"""

import os

from diseases import get_disease

VERSION = "0.2.0-plataforma"
NOMBRE_PLATAFORMA = "Exonik - Plataforma de Diseño de Terapia Génica Personalizada"

# =============================================================================
# SELECCIÓN DE LA ENFERMEDAD ACTIVA
# =============================================================================

ENFERMEDAD_ACTIVA = os.environ.get("EXONIK_DISEASE", "sca")
DISEASE = get_disease(ENFERMEDAD_ACTIVA)

# =============================================================================
# RE-EXPORTACIÓN A NOMBRES LEGACY (compatibilidad total con el pipeline SCA)
# =============================================================================
# El pipeline (Fases 1-6, módulos 1-3) importa estos nombres. Aquí los
# apuntamos a la enfermedad activa. Para SCA son idénticos a los originales.

# --- Target primario (gen de la enfermedad) ---
HBB_CDS_NORMAL = DISEASE.cds_normal
HBB_CDS_SCA = DISEASE.cds_mutante          # "mutante" del gen activo
HBB_PROTEINA_NORMAL = DISEASE.proteina_normal
HBB_PROTEINA_SCA = DISEASE.proteina_mutante
HBB_REGION_GENOMICA = DISEASE.region_genomica
HBB_ATG_OFFSET = DISEASE.atg_offset
HBB_CROMOSOMA = DISEASE.cromosoma
HBB_POS_GENOMICA_MUTACION = DISEASE.pos_genomica_mutacion

# --- Variante patogénica ---
SCA_POS_CDS = DISEASE.variante_pos_cds
SCA_REF = DISEASE.variante_ref
SCA_ALT = DISEASE.variante_alt
SCA_CODON_NORMAL = DISEASE.codon_normal
SCA_CODON_MUTADO = DISEASE.codon_mutante
SCA_RS_ID = DISEASE.variante_rs_id

# --- Target secundario / estrategia alternativa (BCL11A en SCA) ---
# Si la enfermedad no tiene target secundario, se degrada al target primario
# para que los imports existentes no fallen (las fases que usan la estrategia
# alternativa solo aplican cuando la enfermedad la define).
BCL11A_REGION_ENHANCER = DISEASE.alt_region or DISEASE.region_genomica
BCL11A_CROMOSOMA = DISEASE.alt_cromosoma or DISEASE.cromosoma
BCL11A_POS_INICIO = DISEASE.alt_pos_inicio or DISEASE.pos_genomica_mutacion
BCL11A_POS_FIN = DISEASE.alt_pos_fin or DISEASE.pos_genomica_mutacion

# --- Nombres genéricos (recomendados para código nuevo/enfermedades nuevas) ---
GEN_NOMBRE = DISEASE.gene
CDS_NORMAL = DISEASE.cds_normal
CDS_MUTANTE = DISEASE.cds_mutante
CDS_TERAPEUTICO = DISEASE.cds_para_arnm
ESTRATEGIA_TERAPEUTICA = DISEASE.estrategia

# =============================================================================
# TABLA DE CODONES HUMANOS  (genérico — no depende de la enfermedad)
# =============================================================================

# Codón más frecuente por aminoácido en humanos
CODONES_OPTIMOS = {
    'A': 'GCC', 'R': 'CGG', 'N': 'AAC', 'D': 'GAC', 'C': 'TGC',
    'Q': 'CAG', 'E': 'GAG', 'G': 'GGC', 'H': 'CAC', 'I': 'ATC',
    'L': 'CTG', 'K': 'AAG', 'M': 'ATG', 'F': 'TTC', 'P': 'CCC',
    'S': 'AGC', 'T': 'ACC', 'W': 'TGG', 'Y': 'TAC', 'V': 'GTG',
    '*': 'TGA'
}

# Tabla completa: codón → aminoácido
TABLA_CODONES = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

# Frecuencia de uso de codones en humanos (por mil)
FRECUENCIAS_CODONES = {
    'TTT': 17.6, 'TTC': 20.3, 'TTA': 7.7,  'TTG': 12.9,
    'CTT': 13.2, 'CTC': 19.6, 'CTA': 7.2,  'CTG': 39.6,
    'ATT': 16.0, 'ATC': 20.8, 'ATA': 7.5,  'ATG': 22.0,
    'GTT': 11.0, 'GTC': 14.5, 'GTA': 7.1,  'GTG': 28.1,
    'TCT': 15.2, 'TCC': 17.7, 'TCA': 12.2, 'TCG': 4.4,
    'CCT': 17.5, 'CCC': 19.8, 'CCA': 16.9, 'CCG': 6.9,
    'ACT': 13.1, 'ACC': 18.9, 'ACA': 15.1, 'ACG': 6.1,
    'GCT': 18.4, 'GCC': 27.7, 'GCA': 15.8, 'GCG': 7.4,
    'TAT': 12.2, 'TAC': 15.3, 'TAA': 1.0,  'TAG': 0.8,
    'CAT': 10.9, 'CAC': 15.1, 'CAA': 12.3, 'CAG': 34.2,
    'AAT': 17.0, 'AAC': 19.1, 'AAA': 24.4, 'AAG': 31.9,
    'GAT': 21.8, 'GAC': 25.1, 'GAA': 29.0, 'GAG': 39.6,
    'TGT': 10.6, 'TGC': 12.6, 'TGA': 1.6,  'TGG': 13.2,
    'CGT': 4.5,  'CGC': 10.4, 'CGA': 6.2,  'CGG': 11.4,
    'AGT': 12.1, 'AGC': 19.5, 'AGA': 12.2, 'AGG': 12.0,
    'GGT': 10.8, 'GGC': 22.2, 'GGA': 16.5, 'GGG': 16.5,
}

# Aminoácido → lista de codones sinónimos
CODONES_POR_AMINOACIDO = {}
for codon, aa in TABLA_CODONES.items():
    if aa not in CODONES_POR_AMINOACIDO:
        CODONES_POR_AMINOACIDO[aa] = []
    CODONES_POR_AMINOACIDO[aa].append(codon)

# =============================================================================
# GENES CRÍTICOS (off-targets peligrosos que JAMÁS deben ser editados)
# =============================================================================

GENES_CRITICOS = {
    "TP53":  {"cromosoma": "chr17", "funcion": "Supresor tumoral (Guardian del genoma)"},
    "BRCA1": {"cromosoma": "chr17", "funcion": "Reparación ADN, supresor tumoral"},
    "BRCA2": {"cromosoma": "chr13", "funcion": "Reparación ADN, supresor tumoral"},
    "RB1":   {"cromosoma": "chr13", "funcion": "Supresor tumoral (retinoblastoma)"},
    "APC":   {"cromosoma": "chr5",  "funcion": "Supresor tumoral (poliposis)"},
    "PTEN":  {"cromosoma": "chr10", "funcion": "Supresor tumoral"},
    "MYC":   {"cromosoma": "chr8",  "funcion": "Proto-oncogén"},
    "KRAS":  {"cromosoma": "chr12", "funcion": "Proto-oncogén"},
    "BRAF":  {"cromosoma": "chr7",  "funcion": "Proto-oncogén"},
    "JAK2":  {"cromosoma": "chr9",  "funcion": "Señalización celular"},
    "BCL2":  {"cromosoma": "chr18", "funcion": "Regulador de apoptosis"},
    "HBA1":  {"cromosoma": "chr16", "funcion": "Hemoglobina alfa-1"},
    "HBA2":  {"cromosoma": "chr16", "funcion": "Hemoglobina alfa-2"},
    "HBG1":  {"cromosoma": "chr11", "funcion": "Hemoglobina gamma-1 (fetal)"},
    "HBG2":  {"cromosoma": "chr11", "funcion": "Hemoglobina gamma-2 (fetal)"},
}

# =============================================================================
# CONFIGURACIÓN DE CRISPR  (genérico)
# =============================================================================

CRISPR_NUCLEASAS = {
    "SpCas9": {
        "pam": "NGG",
        "longitud_guia": 20,
        "descripcion": "Cas9 de S. pyogenes (estándar)",
        "max_mismatches_off": 3,
        "corte_offset": -3,  # Corta 3 bp antes del PAM
    },
    "SpCas9-HiFi": {
        "pam": "NGG",
        "longitud_guia": 20,
        "descripcion": "Cas9 alta fidelidad (menos off-targets)",
        "max_mismatches_off": 2,
        "corte_offset": -3,
    },
    "ABE8e": {
        "pam": "NGG",
        "longitud_guia": 20,
        "descripcion": "Base Editor adenina (A→G, complementario T→C)",
        "max_mismatches_off": 2,
        "corte_offset": None,  # No corta, solo edita bases
        "ventana_edicion": (4, 8),  # Posiciones 4-8 de la guía (desde el extremo 5')
    },
}

# =============================================================================
# CONFIGURACIÓN DE ARNm TERAPÉUTICO  (genérico)
# =============================================================================

MRNM_CONFIG = {
    "5utr": "GCCACCAUGG",           # Secuencia Kozak (inicio de traducción eficiente)
    "3utr_tipo": "HBB_3UTR",        # UTR 3' del propio gen HBB (estabilidad)
    "3utr_seq": "AAUAAAGCAAUUUUAACUUUA",  # Señal de poliadenilación + estabilización
    "poly_a_longitud": 120,          # Cola poly-A (120 adeninas)
    "cap_tipo": "CleanCap-AG",       # Cap sintético (TriLink)
    "modificacion": "N1-metilpseudouridina",  # m1Ψ (como vacunas Moderna/BioNTech)
    "gc_min": 0.45,                  # GC content mínimo objetivo
    "gc_max": 0.65,                  # GC content máximo objetivo
}


OFF_TARGETS_DB = {
    # Sitios off-target genéricos (independientes de la guía específica)
    # Cada entrada: (cromosoma, posición, secuencia_similar, mismatches, gen_cercano)
    "zona_HBA": {
        "cromosoma": "chr16",
        "posicion": 176685,
        "gen_cercano": "HBA2",
        "distancia_gen": 0,
        "critico": True,
        "nota": "Homología con HBB por familia de hemoglobinas"
    },
    "zona_HBG1": {
        "cromosoma": "chr11",
        "posicion": 5250090,
        "gen_cercano": "HBG1",
        "distancia_gen": 500,
        "critico": True,
        "nota": "Cluster de beta-globina, hemoglobina fetal"
    },
    "zona_intergenica_chr3": {
        "cromosoma": "chr3",
        "posicion": 48291050,
        "gen_cercano": "Ninguno",
        "distancia_gen": 50000,
        "critico": False,
        "nota": "Región intergénica sin genes conocidos"
    },
    "zona_MYC": {
        "cromosoma": "chr8",
        "posicion": 127738500,
        "gen_cercano": "MYC",
        "distancia_gen": 2000,
        "critico": True,
        "nota": "Cercanía a proto-oncogén MYC"
    },
    "zona_intergenica_chr5": {
        "cromosoma": "chr5",
        "posicion": 98150300,
        "gen_cercano": "Ninguno",
        "distancia_gen": 80000,
        "critico": False,
        "nota": "Desierto génico"
    },
    "zona_TP53_distal": {
        "cromosoma": "chr17",
        "posicion": 7676500,
        "gen_cercano": "TP53",
        "distancia_gen": 15000,
        "critico": True,
        "nota": "Región distal a TP53"
    },
}
