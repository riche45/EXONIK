"""
===============================================================================
  Exonik - Paquete de módulos por enfermedad
===============================================================================

Cada enfermedad se define como una instancia de `Disease` (ver base.py) en su
propio módulo dentro de este paquete. Esto permite que el mismo pipeline
(Fases 1-6) se ejecute sobre distintas enfermedades sin tocar el código de
análisis: solo se cambia la enfermedad activa.

La selección de la enfermedad activa la hace `config.py` mediante la variable
de entorno `EXONIK_DISEASE` (por defecto: "sca").

Enfermedades disponibles:
  - sca            : Anemia falciforme (HBB, rs334)          [caso base]
  - beta_thal      : Beta-talasemia    (HBB, IVS/otras)      [mismo grupo]
  - parkinson_gba1 : Parkinson genético (GBA1)               [flagship]
"""

from .base import Disease, get_disease, DISEASE_REGISTRY

__all__ = ["Disease", "get_disease", "DISEASE_REGISTRY"]
