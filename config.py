"""
===============================================================================
  Exonik - Plataforma de Diseño de Terapia Génica Personalizada
  Configuración y Constantes para Anemia Falciforme (SCA)
  Versión: 0.1.0 (Prototipo)
===============================================================================

Este archivo contiene todas las secuencias de referencia, tablas de codones,
configuraciones de CRISPR y datos genómicos necesarios para el análisis.

La Anemia Falciforme (Sickle Cell Anemia, SCA) es causada por una mutación
puntual en el gen HBB (Hemoglobina Beta):
  - Mutación: c.20A>T (GAG → GTG en codón 7)
  - Efecto: Glu → Val (E7V) → Hemoglobina S (HbS) anormal
  - Herencia: Autosómica recesiva
  - Cromosoma: 11 (chr11:5,225,464-5,227,071 en GRCh38)
"""

VERSION = "0.1.0-prototipo"
NOMBRE_PLATAFORMA = "Exonik - Plataforma de Diseño de Terapia Génica Personalizada"

# =============================================================================
# SECUENCIAS DE REFERENCIA - GEN HBB (Hemoglobina Beta)
# =============================================================================

# CDS completa del gen HBB normal (NM_000518.5) - 444 nucleótidos
# Codifica 147 aminoácidos + codón de parada
HBB_CDS_NORMAL = (
    "ATGGTGCACCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTG"
    "AACGTGGATGAAGTTGGTGGTGAGGCCCTGGGCAGGCTGCTGGTGGTCTACCCTTG"
    "GACCCAGAGGTTCTTTGAGTCCTTTGGGGATCTGTCCACTCCTGATGCTGTTATGGG"
    "CAACCCTAAGGTGAAGGCTCATGGCAAGAAAGTGCTCGGTGCCTTTAGTGATGGCCT"
    "GGCTCACCTGGACAACCTCAAGGGCACCTTTGCTCACTGCAGTGAATTCTCACTGGA"
    "CAAAGCCTTTGAGGAACTGATGATGTGCTCGATGCCAGCCCATCACTTTGGCAAAGA"
    "ATTCACCCCACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAATGC"
    "CCTGGCCCACAAGTATCACTAA"
)

# CDS del gen HBB con mutación SCA (c.20A>T)
# Posición 19 (0-indexed): A → T, convierte GAG (Glu) → GTG (Val)
HBB_CDS_SCA = (
    "ATGGTGCACCTGACTCCTGTGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTG"
    "AACGTGGATGAAGTTGGTGGTGAGGCCCTGGGCAGGCTGCTGGTGGTCTACCCTTG"
    "GACCCAGAGGTTCTTTGAGTCCTTTGGGGATCTGTCCACTCCTGATGCTGTTATGGG"
    "CAACCCTAAGGTGAAGGCTCATGGCAAGAAAGTGCTCGGTGCCTTTAGTGATGGCCT"
    "GGCTCACCTGGACAACCTCAAGGGCACCTTTGCTCACTGCAGTGAATTCTCACTGGA"
    "CAAAGCCTTTGAGGAACTGATGATGTGCTCGATGCCAGCCCATCACTTTGGCAAAGA"
    "ATTCACCCCACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAATGC"
    "CCTGGCCCACAAGTATCACTAA"
)

# Posición exacta de la mutación SCA en el CDS
SCA_POS_CDS = 19          # 0-indexed en el CDS (nucleótido 20, c.20A>T)
SCA_REF = "A"             # Nucleótido normal
SCA_ALT = "T"             # Nucleótido mutado
SCA_CODON_NORMAL = "GAG"  # Glutámico (Glu, E)
SCA_CODON_MUTADO = "GTG"  # Valina (Val, V)
SCA_RS_ID = "rs334"       # ID en dbSNP

# Región genómica del gen HBB (incluye flancos para búsqueda de guías CRISPR)
# chr11:5,226,600-5,227,200 (GRCh38), ~600 bp centrados en el sitio de mutación
# (Cadena codificante, simplificada para el prototipo)
HBB_REGION_GENOMICA = (
    "TAAACTGCAGGCATGCAAGCTTGGCGTAATCATGGTCATAGCTGTTTCCTGTGTGAAATTGT"
    "TATCCGCTCACAATTCCACACAACATACGAGCCGGAAGCATAAAGTGTAAAGCCTGGGGTGC"
    "CTAATGAGTGAGCTAACTCACATTAATTGCGTTGCGCTCACTGCCCGCTTTCCAGTCGGGA"
    "AACCTGTCGTGCCAGCTGCATTAATGAATCGGCCAACGCGCGGGGAGAGGCGGTTTGCGTA"
    "TTGGGCGCTCTTCCGCTTCCTCGCTCACTGACTCGCTGCGCTCGGTCGTTCGGCTGCGGCG"
    "ACATTTGCTTCTGACACAACTGTGTTCACTAGCAACCTCAAACAGACACCATGGTGCACCTG"
    "ACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAACGTGGATGAAGTTG"
    "GTGGTGAGGCCCTGGGCAGGCTGCTGGTGGTCTACCCTTGGACCCAGAGGTTCTTTGAGTC"
    "CTTTGGGGATCTGTCCACTCCTGATGCTGTTATGGGCAACCCTAAGGTGAAGGCTCATGGCA"
    "AGAAAGTGCTCGGTGCCTTTAGTGATGGCCTGGCTCACCTGGACAACCTCAAGGGCACCTTT"
)

# Offset: la posición del ATG de inicio en HBB_REGION_GENOMICA
HBB_ATG_OFFSET = 339  # Posición aproximada del ATG en la región genómica

# Coordenadas genómicas (GRCh38)
HBB_CROMOSOMA = "chr11"
HBB_POS_GENOMICA_MUTACION = 5227002  # Posición genómica de c.20A>T

# =============================================================================
# BCL11A ENHANCER - Estrategia alternativa
# =============================================================================
# La disrupción del enhancer eritroide de BCL11A reactiva la hemoglobina
# fetal (HbF), que compensa el defecto de HbS.
# Esta es la estrategia usada por Casgevy (primera terapia CRISPR aprobada).

BCL11A_REGION_ENHANCER = (
    "CTAACAGTTGCTTTTATCACAGGCTCCAGGAAGGGTTTGGCCTCTGATTAGGGTGCAGCGATG"
    "CACTCATGATGGCACTGACTCTTTCAAGGGTCCTGAGTCCAGCAGTGTGAATCACTGTGTAA"
    "GCAGGATCCAGGGCGACTGTTTCTAGAGATAATCTGATAATTTGTGATTATGATGTAATCAGG"
    "CATCTCAGCAAAGACTAAACCTGCAATTGATGGCCCTGTCATTTCATCTGCAATACCTTGGCT"
    "TCTTGAAGACAGGGGCCAGTGTCCACTCCTGGTACCAGGATCCCTTTCCTGAAGGGATTTACT"
)
BCL11A_CROMOSOMA = "chr2"
BCL11A_POS_INICIO = 60716189
BCL11A_POS_FIN = 60728612

# =============================================================================
# PROTEÍNAS DE HEMOGLOBINA BETA
# =============================================================================

# Proteína HBB normal (147 aminoácidos)
HBB_PROTEINA_NORMAL = (
    "MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKV"
    "LGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVA"
    "GVANALAHKYH"
)

# Proteína HBB con mutación SCA (E7V)
HBB_PROTEINA_SCA = (
    "MVHLTPVEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKV"
    "LGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVA"
    "GVANALAHKYH"
)

# =============================================================================
# TABLA DE CODONES HUMANOS
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
# CONFIGURACIÓN DE CRISPR
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
# CONFIGURACIÓN DE ARNm TERAPÉUTICO
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

