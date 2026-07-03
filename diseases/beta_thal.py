"""
===============================================================================
  Exonik - Módulo de enfermedad: Beta-Talasemia (β0-talasemia)
===============================================================================

MISMO GEN que la Anemia Falciforme (HBB, cromosoma 11) → demuestra la
transferencia "nativa" del pipeline dentro del grupo monogénico de SCA.

  - Gen:       HBB (Hemoglobina Beta), cromosoma 11
  - Mutación:  CD39 (β39) — HBB:c.118C>T  (CAG → TAG, Gln40 → Stop)
               Una de las causas más frecuentes de β0-talasemia (Mediterráneo).
  - dbSNP:     rs11549407  (GRCh38: chr11:5,226,774; G>A en la hebra +)
  - Herencia:  Autosómica recesiva
  - Efecto:    codón de parada prematuro → NO se produce β-globina funcional
  - Estrategia Exonik: corrección del nonsense (T→C) o reactivación de HbF
                       vía BCL11A (misma diana alternativa que SCA).

Nota: el CDS aquí es el CANÓNICO completo de HBB (NM_000518.5, 444 nt), obtenido
de NCBI. La región genómica para escaneo de guías se reutiliza de SCA (mismo
gen). Las coordenadas para la Fase 1 (descarga de genomas) se cablearán al
parametrizar las fases (Pista B).
"""

from .base import Disease
# Reutilizamos la región genómica del gen HBB y el enhancer de BCL11A definidos
# en el módulo de SCA (es exactamente el mismo locus / misma diana alternativa).
from .sca import _HBB_REGION_GENOMICA, _BCL11A_REGION_ENHANCER

# --- CDS canónico de HBB (NM_000518.5 / NP_000509.1), 444 nt ---
_HBB_CDS_CANONICO = (
    "ATGGTGCATCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAACGTGGATGAAG"
    "TTGGTGGTGAGGCCCTGGGCAGGCTGCTGGTGGTCTACCCTTGGACCCAGAGGTTCTTTGAGTCCTTTGG"
    "GGATCTGTCCACTCCTGATGCTGTTATGGGCAACCCTAAGGTGAAGGCTCATGGCAAGAAAGTGCTCGGT"
    "GCCTTTAGTGATGGCCTGGCTCACCTGGACAACCTCAAGGGCACCTTTGCCACACTGAGTGAGCTGCACT"
    "GTGACAAGCTGCACGTGGATCCTGAGAACTTCAGGCTCCTGGGCAACGTGCTGGTCTGTGTGCTGGCCCA"
    "TCACTTTGGCAAAGAATTCACCCCACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAAT"
    "GCCCTGGCCCACAAGTATCACTAA"
)

# Variante CD39: c.118C>T → posición 0-indexed 117 del CDS. CAG (Gln) → TAG (Stop).
_POS_CDS = 117
assert _HBB_CDS_CANONICO[_POS_CDS] == "C", _HBB_CDS_CANONICO[_POS_CDS]
assert _HBB_CDS_CANONICO[_POS_CDS - 0:_POS_CDS + 3] == "CAG", _HBB_CDS_CANONICO[_POS_CDS:_POS_CDS + 3]

# CDS mutante calculado (evita transcripción manual)
_HBB_CDS_MUTANTE = (
    _HBB_CDS_CANONICO[:_POS_CDS] + "T" + _HBB_CDS_CANONICO[_POS_CDS + 1:]
)

# Proteína canónica (147 aa, NP_000509.1)
_HBB_PROTEINA_NORMAL = (
    "MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKV"
    "LGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVA"
    "GVANALAHKYH"
)
# La proteína mutante se trunca en el codón 40 (Gln40→Stop): quedan 39 residuos.
_HBB_PROTEINA_MUTANTE = "MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWT"


DISEASE = Disease(
    key="beta_thal",
    nombre="Beta-Talasemia (β0, CD39)",
    gene="HBB",
    cromosoma="chr11",
    herencia="Autosómica recesiva",
    estrategia="correccion",

    cds_normal=_HBB_CDS_CANONICO,
    cds_mutante=_HBB_CDS_MUTANTE,
    proteina_normal=_HBB_PROTEINA_NORMAL,
    proteina_mutante=_HBB_PROTEINA_MUTANTE,

    variante_pos_cds=_POS_CDS,
    variante_ref="C",             # hebra codificante
    variante_alt="T",
    variante_rs_id="rs11549407",
    codon_normal="CAG",           # Glutamina (Gln, Q)
    codon_mutante="TAG",          # Codón de parada (Stop)

    # Reutilizamos la ventana genómica del gen HBB (mismo locus que SCA)
    region_genomica=_HBB_REGION_GENOMICA,
    atg_offset=339,
    pos_genomica_mutacion=5226774,   # GRCh38, rs11549407

    # Beta-talasemia también responde a reactivación de HbF (BCL11A) → Casgevy
    # está aprobada tanto para SCA como para β-talasemia dependiente de transfusión.
    alt_nombre="BCL11A",
    alt_region=_BCL11A_REGION_ENHANCER,
    alt_cromosoma="chr2",
    alt_pos_inicio=60716189,
    alt_pos_fin=60728612,

    prevalencia="~60,000 nacimientos/año con talasemia mayor a nivel mundial",
    terapia_aprobada="Casgevy/Zynteglo (TDT) — no cubren todas las variantes/países",
    uniprot_id="P68871",
    poblaciones_interes=("TSI", "IBS", "CEU", "BEB", "STU"),  # Mediterráneo/Sur de Asia
)
