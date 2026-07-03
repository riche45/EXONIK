"""
===============================================================================
  Exonik - Módulo de enfermedad: Parkinson asociado a GBA1  
===============================================================================

Enfermedad de Parkinson (EP) asociada a variantes en GBA1 — el mayor factor de
riesgo genético conocido para Parkinson. SIN terapia modificadora aprobada a
julio de 2026 (los enfoques GBA1 —p.ej. LY-3884961/PR001— siguen en ensayos).

  - Gen:       GBA1 (glucocerebrosidasa / GCasa), cromosoma 1
  - Variante:  N370S  (nomenclatura clásica, madura) = N409S (precursor)
               HBGVS: HBB... no; GBA1 c.1226A>G, p.Asn409Ser
  - dbSNP:     rs76763715  (GRCh38: chr1:155,235,843; T>C en la hebra +,
               equivalente a A>G en la hebra codificante: AAC → AGC)
  - Herencia:  Factor de riesgo (autosómico, penetrancia incompleta)
  - Efecto:    GCasa con función lisosomal reducida → acumulación de
               glucosilceramida → riesgo de Parkinson.

EL GANCHO TÉCNICO — GBAP1 (pseudogén):
  GBA1 tiene un pseudogén, GBAP1, a ~16 kb, con ~96% de identidad de secuencia.
  Cualquier guía CRISPR para GBA1 se parece muchísimo a regiones de GBAP1 →
  el pseudogén es un "campo minado" natural de off-targets casi idénticos.
  Aquí es donde el motor de personalización de Exonik (off-targets sobre el
  genoma real del paciente + cruce de SNPs) aporta el mayor valor diferencial.

Estrategia Exonik:
  - 'correccion' para explotar el pipeline CRISPR + análisis off-target (demo
    del diferenciador frente a GBAP1).
  - Modalidad clínica primaria = AUGMENTACIÓN (aportar GCasa funcional vía ARNm
    / vector); Exonik también diseña ese ARNm en la Fase 4 (cds_terapeutico).

Nota: la región genómica para escaneo de guías se toma como el CDS completo
(exones codificantes) con atg_offset=0. El análisis off-target real (Fase 2)
busca contra TODO el genoma GRCh38, por lo que GBAP1 aparecerá de forma natural.
Las coordenadas para la Fase 1 se afinan al parametrizar las fases (Pista B).
"""

from .base import Disease

# --- CDS canónico de GBA1 (NM_000157.4 / NP_000148.2), 1611 nt ---
_GBA1_CDS_NORMAL = (
    "ATGGAGTTTTCAAGTCCTTCCAGAGAGGAATGTCCCAAGCCTTTGAGTAGGGTAAGCATCATGGCTGGCA"
    "GCCTCACAGGATTGCTTCTACTTCAGGCAGTGTCGTGGGCATCAGGTGCCCGCCCCTGCATCCCTAAAAG"
    "CTTCGGCTACAGCTCGGTGGTGTGTGTCTGCAATGCCACATACTGTGACTCCTTTGACCCCCCGACCTTT"
    "CCTGCCCTTGGTACCTTCAGCCGCTATGAGAGTACACGCAGTGGGCGACGGATGGAGCTGAGTATGGGGC"
    "CCATCCAGGCTAATCACACGGGCACAGGCCTGCTACTGACCCTGCAGCCAGAACAGAAGTTCCAGAAAGT"
    "GAAGGGATTTGGAGGGGCCATGACAGATGCTGCTGCTCTCAACATCCTTGCCCTGTCACCCCCTGCCCAA"
    "AATTTGCTACTTAAATCGTACTTCTCTGAAGAAGGAATCGGATATAACATCATCCGGGTACCCATGGCCA"
    "GCTGTGACTTCTCCATCCGCACCTACACCTATGCAGACACCCCTGATGATTTCCAGTTGCACAACTTCAG"
    "CCTCCCAGAGGAAGATACCAAGCTCAAGATACCCCTGATTCACCGAGCCCTGCAGTTGGCCCAGCGTCCC"
    "GTTTCACTCCTTGCCAGCCCCTGGACATCACCCACTTGGCTCAAGACCAATGGAGCGGTGAATGGGAAGG"
    "GGTCACTCAAGGGACAGCCCGGAGACATCTACCACCAGACCTGGGCCAGATACTTTGTGAAGTTCCTGGA"
    "TGCCTATGCTGAGCACAAGTTACAGTTCTGGGCAGTGACAGCTGAAAATGAGCCTTCTGCTGGGCTGTTG"
    "AGTGGATACCCCTTCCAGTGCCTGGGCTTCACCCCTGAACATCAGCGAGACTTCATTGCCCGTGACCTAG"
    "GTCCTACCCTCGCCAACAGTACTCACCACAATGTCCGCCTACTCATGCTGGATGACCAACGCTTGCTGCT"
    "GCCCCACTGGGCAAAGGTGGTACTGACAGACCCAGAAGCAGCTAAATATGTTCATGGCATTGCTGTACAT"
    "TGGTACCTGGACTTTCTGGCTCCAGCCAAAGCCACCCTAGGGGAGACACACCGCCTGTTCCCCAACACCA"
    "TGCTCTTTGCCTCAGAGGCCTGTGTGGGCTCCAAGTTCTGGGAGCAGAGTGTGCGGCTAGGCTCCTGGGA"
    "TCGAGGGATGCAGTACAGCCACAGCATCATCACGAACCTCCTGTACCATGTGGTCGGCTGGACCGACTGG"
    "AACCTTGCCCTGAACCCCGAAGGAGGACCCAATTGGGTGCGTAACTTTGTCGACAGTCCCATCATTGTAG"
    "ACATCACCAAGGACACGTTTTACAAACAGCCCATGTTCTACCACCTTGGCCACTTCAGCAAGTTCATTCC"
    "TGAGGGCTCCCAGAGAGTGGGGCTGGTTGCCAGTCAGAAGAACGACCTGGACGCAGTGGCACTGATGCAT"
    "CCCGATGGCTCTGCTGTTGTGGTCGTGCTAAACCGCTCCTCTAAGGATGTGCCTCTTACCATCAAGGATC"
    "CTGCTGTGGGCTTCCTGGAGACAATCTCACCTGGCTACTCCATTCACACCTACCTGTGGCGTCGCCAGTG"
    "A"
)

# Variante N370S (N409S precursor): c.1226A>G → 0-indexed 1225. AAC (Asn) → AGC (Ser).
_POS_CDS = 1225
assert len(_GBA1_CDS_NORMAL) == 1611, len(_GBA1_CDS_NORMAL)
assert _GBA1_CDS_NORMAL[_POS_CDS] == "A", _GBA1_CDS_NORMAL[_POS_CDS]
assert _GBA1_CDS_NORMAL[1224:1227] == "AAC", _GBA1_CDS_NORMAL[1224:1227]

_GBA1_CDS_MUTANTE = (
    _GBA1_CDS_NORMAL[:_POS_CDS] + "G" + _GBA1_CDS_NORMAL[_POS_CDS + 1:]
)

# Proteína canónica GCasa (536 aa, precursor NP_000148.2)
_GBA1_PROTEINA_NORMAL = (
    "MEFSSPSREECPKPLSRVSIMAGSLTGLLLLQAVSWASGARPCIPKSFGYSSVVCVCNATYCDSFDPPTF"
    "PALGTFSRYESTRSGRRMELSMGPIQANHTGTGLLLTLQPEQKFQKVKGFGGAMTDAAALNILALSPPAQ"
    "NLLLKSYFSEEGIGYNIIRVPMASCDFSIRTYTYADTPDDFQLHNFSLPEEDTKLKIPLIHRALQLAQRP"
    "VSLLASPWTSPTWLKTNGAVNGKGSLKGQPGDIYHQTWARYFVKFLDAYAEHKLQFWAVTAENEPSAGLL"
    "SGYPFQCLGFTPEHQRDFIARDLGPTLANSTHHNVRLLMLDDQRLLLPHWAKVVLTDPEAAKYVHGIAVH"
    "WYLDFLAPAKATLGETHRLFPNTMLFASEACVGSKFWEQSVRLGSWDRGMQYSHSIITNLLYHVVGWTDW"
    "NLALNPEGGPNWVRNFVDSPIIVDITKDTFYKQPMFYHLGHFSKFIPEGSQRVGLVASQKNDLDAVALMH"
    "PDGSAVVVVLNRSSKDVPLTIKDPAVGFLETISPGYSIHTYLWRRQ"
)
# Proteína mutante: Asn409 → Ser (índice 0-based 408)
_GBA1_PROTEINA_MUTANTE = (
    _GBA1_PROTEINA_NORMAL[:408] + "S" + _GBA1_PROTEINA_NORMAL[409:]
)


DISEASE = Disease(
    key="parkinson_gba1",
    nombre="Parkinson asociado a GBA1 (N370S)",
    gene="GBA1",
    cromosoma="chr1",
    herencia="Factor de riesgo (penetrancia incompleta)",
    estrategia="correccion",

    cds_normal=_GBA1_CDS_NORMAL,
    cds_mutante=_GBA1_CDS_MUTANTE,
    proteina_normal=_GBA1_PROTEINA_NORMAL,
    proteina_mutante=_GBA1_PROTEINA_MUTANTE,

    variante_pos_cds=_POS_CDS,
    variante_ref="A",             # hebra codificante
    variante_alt="G",
    variante_rs_id="rs76763715",
    codon_normal="AAC",           # Asparagina (Asn, N)
    codon_mutante="AGC",          # Serina (Ser, S)

    # Región para escaneo de guías = CDS completo (off-targets reales vs genoma
    # completo en Fase 2 → GBAP1 aparece de forma natural).
    region_genomica=_GBA1_CDS_NORMAL,
    atg_offset=0,
    pos_genomica_mutacion=155235843,   # GRCh38, rs76763715

    # ARNm terapéutico para la modalidad de AUGMENTACIÓN (GCasa funcional)
    cds_terapeutico=_GBA1_CDS_NORMAL,

    # GBA1 no tiene estrategia de "enhancer alternativo" tipo BCL11A.
    alt_nombre=None,
    alt_region=None,
    alt_cromosoma=None,
    alt_pos_inicio=None,
    alt_pos_fin=None,

    prevalencia="~10M con Parkinson; GBA1 = mayor factor de riesgo genético (~5-15%)",
    terapia_aprobada="Ninguna terapia modificadora aprobada (jul-2026); GBA1 en ensayos",
    uniprot_id="P04062",          # GCasa humana
    poblaciones_interes=("CEU", "TSI", "GIH", "ASW", "MXL"),

    # Etiquetas de presentacion para el reporte de ARNm (Fase 4)
    proteina_nombre="Glucocerebrosidasa (GCasa / GBA1) funcional",
    proteina_funcion="Hidrolisis lisosomal de glucosilceramida (GlcCer)",
    terapia_objetivo="Restaurar actividad de GCasa (augmentacion de GBA1)",
    tejido_objetivo="Neuronas y microglia del SNC; macrofagos",
    targeting="Ligandos de paso de barrera hematoencefalica (BHE)",
    nota_inmunogenicidad="GCasa es proteina endogena; vigilar respuesta anti-GCasa en deficit severo",
)
