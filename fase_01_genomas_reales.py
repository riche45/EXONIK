"""
===============================================================================
  Exonik - Fase 1: Obtencion de Genomas Reales
  Proyecto 1000 Genomes - Cromosoma 11 (Region HBB)
===============================================================================

Este script descarga datos genomicos REALES del Proyecto 1000 Genomes
(~2,504 personas de 26 poblaciones del mundo) y extrae portadores REALES
de la mutacion de Anemia Falciforme (rs334).

Pasos:
  1. Descargar el panel de muestras (~100KB) -> mapeo muestra a poblacion
  2. Descargar el VCF del cromosoma 11 (~290MB) -> variantes geneticas
  3. Extraer variantes de la region del gen HBB
  4. Identificar portadores reales de rs334
  5. Generar perfiles de pacientes compatibles con Exonik

Coordenadas:
  - El VCF de 1000 Genomes usa GRCh37/hg19
  - HBB gene en GRCh37: chr11:5,246,696-5,248,301
  - rs334 en GRCh37: chr11:5,248,232 (ref=T, alt=A, cadena +)
  - Convertimos a GRCh38 para compatibilidad con Exonik

"""

import gzip
import json
import os
import sys
import time
import urllib.request
import urllib.error

# =============================================================================
# CONFIGURACION
# =============================================================================

# URLs del Proyecto 1000 Genomes (Fase 3, GRCh37/hg19)
VCF_URL = (
    "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"
    "ALL.chr11.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
)
# URL alternativa (NCBI mirror) por si EBI esta lento
VCF_URL_ALT = (
    "https://ftp.ncbi.nlm.nih.gov/1000genomes/ftp/release/20130502/"
    "ALL.chr11.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
)
PANEL_URL = (
    "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"
    "integrated_call_samples_v3.20130502.ALL.panel"
)

# Region del gen HBB en GRCh37 (con +-3kb para cubrir off-targets cercanos)
REGION_INICIO = 5244000
REGION_FIN = 5250500
RS334_POS = 5248232  # Posicion de la mutacion SCA en GRCh37

# Conversion GRCh37 -> GRCh38: restar este offset
# rs334: GRCh37=5,248,232 -> GRCh38=5,227,002 -> diff=21,230
OFFSET_37_A_38 = 21230

# Directorios de salida
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_DESCARGAS = os.path.join(DIR_BASE, "datos_1000genomes")
DIR_PACIENTES_REALES = os.path.join(DIR_BASE, "datos_pacientes_reales")

# Info de poblaciones del 1000 Genomes
POBLACIONES = {
    "YRI": {"nombre": "Yoruba (Ibadan, Nigeria)", "region": "Africa Occidental", "etnia": "Africana"},
    "LWK": {"nombre": "Luhya (Webuye, Kenia)", "region": "Africa Oriental", "etnia": "Africana"},
    "GWD": {"nombre": "Gambianos (Div. Occidental)", "region": "Africa Occidental", "etnia": "Africana"},
    "MSL": {"nombre": "Mende (Sierra Leona)", "region": "Africa Occidental", "etnia": "Africana"},
    "ESN": {"nombre": "Esan (Nigeria)", "region": "Africa Occidental", "etnia": "Africana"},
    "ACB": {"nombre": "Afrocaribenos (Barbados)", "region": "Caribe", "etnia": "Afrodescendiente"},
    "ASW": {"nombre": "Afroamericanos (SO EEUU)", "region": "Norteamerica", "etnia": "Afrodescendiente"},
    "CLM": {"nombre": "Colombianos (Medellin)", "region": "Sudamerica", "etnia": "Hispano/Latino"},
    "MXL": {"nombre": "Mexicanos (Los Angeles)", "region": "Norteamerica", "etnia": "Hispano/Latino"},
    "PUR": {"nombre": "Puertorriquenos", "region": "Caribe", "etnia": "Hispano/Latino"},
    "PEL": {"nombre": "Peruanos (Lima)", "region": "Sudamerica", "etnia": "Hispano/Latino"},
    "TSI": {"nombre": "Toscanos (Italia)", "region": "Europa del Sur", "etnia": "Mediterranea"},
    "IBS": {"nombre": "Ibericos (Espana)", "region": "Europa del Sur", "etnia": "Mediterranea"},
    "GBR": {"nombre": "Britanicos", "region": "Europa del Norte", "etnia": "Europea"},
    "CEU": {"nombre": "Utah (asc. europea)", "region": "Norteamerica", "etnia": "Europea"},
    "FIN": {"nombre": "Finlandeses", "region": "Europa del Norte", "etnia": "Europea"},
    "CHB": {"nombre": "Han (Beijing, China)", "region": "Asia Oriental", "etnia": "Asiatica"},
    "JPT": {"nombre": "Japoneses (Tokio)", "region": "Asia Oriental", "etnia": "Asiatica"},
    "CHS": {"nombre": "Han del Sur (China)", "region": "Asia Oriental", "etnia": "Asiatica"},
    "CDX": {"nombre": "Dai (China)", "region": "Asia Oriental", "etnia": "Asiatica"},
    "KHV": {"nombre": "Kinh (Vietnam)", "region": "Sureste Asiatico", "etnia": "Asiatica"},
    "GIH": {"nombre": "Gujarati (Houston)", "region": "Sur de Asia", "etnia": "Sudasiatica"},
    "PJL": {"nombre": "Punjabis (Lahore)", "region": "Sur de Asia", "etnia": "Sudasiatica"},
    "BEB": {"nombre": "Bengalies (Bangladesh)", "region": "Sur de Asia", "etnia": "Sudasiatica"},
    "STU": {"nombre": "Tamil (Sri Lanka)", "region": "Sur de Asia", "etnia": "Sudasiatica"},
    "ITU": {"nombre": "Telugu (India)", "region": "Sur de Asia", "etnia": "Sudasiatica"},
}


# =============================================================================
# FUNCIONES DE DESCARGA
# =============================================================================

def descargar_con_progreso(url, destino, descripcion="archivo"):
    """
    Descarga un archivo mostrando progreso en consola.
    Si el archivo ya existe, lo salta.
    """
    if os.path.exists(destino):
        tamano = os.path.getsize(destino)
        print(f"  [OK] {descripcion} ya descargado ({tamano / 1024 / 1024:.1f} MB)")
        return True

    print(f"  Descargando {descripcion}...")
    print(f"  URL: {url[:80]}...")
    print(f"  Destino: {destino}")

    try:
        # Obtener tamano total
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Exonik/0.1 (bioinformatics research)')
        response = urllib.request.urlopen(req, timeout=30)
        tamano_total = int(response.headers.get('content-length', 0))

        descargado = 0
        tamano_bloque = 1024 * 1024  # 1 MB por bloque
        inicio = time.time()

        with open(destino, 'wb') as f:
            while True:
                bloque = response.read(tamano_bloque)
                if not bloque:
                    break
                f.write(bloque)
                descargado += len(bloque)

                # Mostrar progreso
                if tamano_total > 0:
                    porcentaje = (descargado / tamano_total) * 100
                    mb_desc = descargado / 1024 / 1024
                    mb_total = tamano_total / 1024 / 1024
                    velocidad = descargado / (time.time() - inicio) / 1024 / 1024
                    sys.stdout.write(
                        f"\r  [{porcentaje:5.1f}%] {mb_desc:.1f}/{mb_total:.1f} MB "
                        f"({velocidad:.1f} MB/s)    "
                    )
                    sys.stdout.flush()

        elapsed = time.time() - inicio
        print(f"\n  [OK] Descarga completada en {elapsed:.0f} segundos")
        return True

    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"\n  [ERROR] Fallo en descarga: {e}")
        # Limpiar archivo parcial
        if os.path.exists(destino):
            os.remove(destino)
        return False


# =============================================================================
# FUNCIONES DE PARSING
# =============================================================================

def cargar_panel_poblaciones(ruta_panel):
    """
    Carga el panel de muestras del 1000 Genomes.
    Formato: sample\tpop\tsuper_pop\tgender
    
    Returns:
        dict: {sample_id: {"pop": "YRI", "super_pop": "AFR", "sexo": "male"}}
    """
    panel = {}
    with open(ruta_panel, 'r') as f:
        header = f.readline()  # Saltar encabezado
        for linea in f:
            campos = linea.strip().split('\t')
            if len(campos) >= 4:
                panel[campos[0]] = {
                    "pop": campos[1],
                    "super_pop": campos[2],
                    "sexo": campos[3],
                }
    return panel


def parsear_vcf_region_hbb(ruta_vcf):
    """
    Parsea el VCF gzipped extrayendo SOLO las variantes en la region HBB.
    
    Lee el archivo linea por linea (streaming) para no cargar 290MB en RAM.
    Solo parsea completamente las lineas que caen en nuestra region de interes.
    
    Returns:
        tuple: (nombres_muestras, lista_variantes)
        - nombres_muestras: list de sample IDs (2504 muestras)
        - lista_variantes: list de dicts con info de cada variante
    """
    nombres_muestras = []
    variantes = []
    lineas_procesadas = 0
    en_region = False
    inicio_tiempo = time.time()

    print(f"\n  Parseando VCF (esto puede tomar 1-3 minutos)...")
    print(f"  Buscando region HBB: chr11:{REGION_INICIO:,}-{REGION_FIN:,} (GRCh37)")

    with gzip.open(ruta_vcf, 'rt', encoding='utf-8') as f:
        for linea in f:
            # Lineas de encabezado
            if linea.startswith('##'):
                continue

            # Linea de nombres de muestras
            if linea.startswith('#CHROM'):
                campos = linea.strip().split('\t')
                # Las muestras empiezan en la columna 9 (indice 9)
                nombres_muestras = campos[9:]
                print(f"  Muestras encontradas: {len(nombres_muestras)}")
                continue

            # Lineas de datos (variantes)
            lineas_procesadas += 1

            # Progreso cada 500,000 lineas
            if lineas_procesadas % 500000 == 0:
                elapsed = time.time() - inicio_tiempo
                sys.stdout.write(
                    f"\r  Escaneando... {lineas_procesadas:,} variantes revisadas "
                    f"({elapsed:.0f}s) | Region HBB: {len(variantes)} variantes     "
                )
                sys.stdout.flush()

            # Extraer posicion rapidamente (sin split completo)
            # Formato VCF: CHROM\tPOS\t...
            tab1 = linea.index('\t')
            tab2 = linea.index('\t', tab1 + 1)
            posicion = int(linea[tab1 + 1:tab2])

            # Verificar si estamos en la region de interes
            if posicion < REGION_INICIO:
                continue  # Aun no llegamos
            
            if posicion > REGION_FIN:
                # Ya pasamos la region - podemos terminar!
                print(f"\r  [OK] Region HBB encontrada y procesada.                          ")
                break

            # Estamos en la region HBB! Parsear la linea completa
            en_region = True
            campos = linea.strip().split('\t')

            variante = {
                "cromosoma": campos[0],
                "posicion_grch37": int(campos[1]),
                "posicion_grch38": int(campos[1]) - OFFSET_37_A_38,
                "id": campos[2],
                "ref": campos[3],
                "alt": campos[4],
                "qual": campos[5],
                "filtro": campos[6],
                "info": campos[7],
                "formato": campos[8],
                "genotipos": campos[9:],  # Todos los genotipos de las 2504 muestras
                "es_rs334": campos[2] == "rs334" or int(campos[1]) == RS334_POS,
            }
            variantes.append(variante)

    elapsed_total = time.time() - inicio_tiempo
    print(f"  Tiempo de parseo: {elapsed_total:.1f} segundos")
    print(f"  Variantes totales escaneadas: {lineas_procesadas:,}")
    print(f"  Variantes en region HBB: {len(variantes)}")

    return nombres_muestras, variantes


def encontrar_portadores_rs334(variantes, nombres_muestras, panel):
    """
    Busca portadores de la mutacion rs334 (Anemia Falciforme).
    
    En el VCF (cadena +, GRCh37):
    - rs334 esta en posicion 5,248,232
    - ref = T (normal en cadena +)
    - alt = A (mutacion SCA en cadena +)
    - En cadena codificante (minus): esto es A>T, osea GAG>GTG (E7V)
    
    Genotipos:
    - 0|0 = Normal (TT)
    - 0|1 o 1|0 = Portador heterocigoto (TA) = Rasgo falciforme
    - 1|1 = Homocigoto (AA) = Anemia Falciforme
    
    Returns:
        list de dicts con info de cada portador
    """
    print(f"\n  Buscando portadores de rs334...")

    # Encontrar la variante rs334
    variante_rs334 = None
    for v in variantes:
        if v["es_rs334"]:
            variante_rs334 = v
            break

    if variante_rs334 is None:
        print("  [!] rs334 NO encontrado en la region. Verificar coordenadas.")
        return []

    print(f"  rs334 encontrado: pos={variante_rs334['posicion_grch37']}, "
          f"ref={variante_rs334['ref']}, alt={variante_rs334['alt']}")

    portadores = []
    conteo_genotipos = {"0|0": 0, "0|1": 0, "1|0": 0, "1|1": 0, "otro": 0}

    for i, genotipo in enumerate(variante_rs334["genotipos"]):
        gt = genotipo.split(':')[0]  # Solo el campo GT (puede haber mas campos)

        if gt in conteo_genotipos:
            conteo_genotipos[gt] += 1
        else:
            conteo_genotipos["otro"] += 1

        # Es portador si tiene al menos un alelo alternativo
        if '1' in gt:
            muestra_id = nombres_muestras[i]
            info_pop = panel.get(muestra_id, {})
            pop = info_pop.get("pop", "?")
            sexo = info_pop.get("sexo", "?")

            # Determinar cigosidad
            if gt in ("1|1", "1/1"):
                cigosidad = "homocigoto"
                tipo = "ENFERMO (HbSS)"
            else:
                cigosidad = "heterocigoto"
                tipo = "PORTADOR (HbAS)"

            portadores.append({
                "muestra_id": muestra_id,
                "indice": i,
                "genotipo_rs334": gt,
                "cigosidad": cigosidad,
                "tipo": tipo,
                "poblacion": pop,
                "poblacion_info": POBLACIONES.get(pop, {"nombre": pop, "region": "?", "etnia": "?"}),
                "sexo": sexo,
            })

    # Imprimir estadisticas
    total = sum(conteo_genotipos.values())
    print(f"\n  === ESTADISTICAS rs334 EN 2,504 PERSONAS ===")
    print(f"  Normal  (0|0): {conteo_genotipos['0|0']:>5} ({conteo_genotipos['0|0']/total*100:.1f}%)")
    het = conteo_genotipos['0|1'] + conteo_genotipos['1|0']
    print(f"  Portador(het): {het:>5} ({het/total*100:.1f}%)")
    print(f"  Enfermo (1|1): {conteo_genotipos['1|1']:>5} ({conteo_genotipos['1|1']/total*100:.1f}%)")
    
    freq_alelo = (het + 2 * conteo_genotipos['1|1']) / (2 * total)
    print(f"  Frecuencia alelo SCA: {freq_alelo:.4f} ({freq_alelo*100:.2f}%)")
    print(f"  Total portadores encontrados: {len(portadores)}")

    # Desglose por poblacion
    print(f"\n  === PORTADORES POR POBLACION ===")
    por_poblacion = {}
    for p in portadores:
        pop = p["poblacion"]
        if pop not in por_poblacion:
            por_poblacion[pop] = {"het": 0, "hom": 0, "nombre": p["poblacion_info"]["nombre"]}
        if p["cigosidad"] == "heterocigoto":
            por_poblacion[pop]["het"] += 1
        else:
            por_poblacion[pop]["hom"] += 1

    for pop in sorted(por_poblacion, key=lambda x: por_poblacion[x]["het"] + por_poblacion[x]["hom"], reverse=True):
        info = por_poblacion[pop]
        total_pop = info["het"] + info["hom"]
        print(f"  {pop} ({info['nombre']}): "
              f"{total_pop} portadores ({info['het']} het, {info['hom']} hom)")

    return portadores


def extraer_variantes_muestra(variantes, indice_muestra, muestra_id):
    """
    Extrae todas las variantes NO-referencia de una muestra especifica
    en la region HBB.
    
    Para cada variante en la region, revisa si esta muestra tiene un
    genotipo no-referencia (es decir, si tiene alguna variante ahi).
    
    Estas variantes son las que usaremos para personalizar los off-targets.
    
    Args:
        variantes: todas las variantes de la region HBB
        indice_muestra: indice de la muestra en el array de genotipos
        muestra_id: ID de la muestra (para el reporte)
        
    Returns:
        list de dicts con variantes de esta muestra
    """
    variantes_muestra = []

    for v in variantes:
        genotipo = v["genotipos"][indice_muestra].split(':')[0]

        # Si tiene algun alelo alternativo
        if '1' in genotipo:
            # Determinar cigosidad de esta variante especifica
            if genotipo in ("1|1", "1/1"):
                cig = "homocigoto"
            else:
                cig = "heterocigoto"

            variantes_muestra.append({
                "cromosoma": f"chr{v['cromosoma']}",
                "posicion_grch37": v["posicion_grch37"],
                "posicion": v["posicion_grch38"],  # Usamos GRCh38 para Exonik
                "ref": v["ref"],
                "alt": v["alt"],
                "rs_id": v["id"],
                "cigosidad": cig,
                "genotipo": genotipo,
                "es_rs334": v["es_rs334"],
            })

    return variantes_muestra


def analizar_variantes_para_offtarget(variantes_muestra):
    """
    Analiza las variantes de una muestra para determinar su potencial
    efecto en off-targets de CRISPR.
    
    Logica simplificada para el prototipo:
    - Si una variante crea o destruye un dinucleotido GG (parte del PAM NGG)
      cerca del gen HBB, podria afectar sitios off-target
    - Si una variante esta en una region codificante de otro gen de globina,
      es relevante para la seguridad.
    """
    # Regiones de interes para off-targets (GRCh38)
    from config import OFF_TARGETS_DB

    efectos = []
    for var in variantes_muestra:
        if var["es_rs334"]:
            continue  # rs334 es la mutacion causal, no un off-target

        pos = var["posicion"]  # GRCh38
        ref = var["ref"]
        alt = var["alt"]
        efecto = "neutral"
        nota = f"Variante {var['rs_id']} en pos {pos}"

        # Verificar si crea/destruye dinucleotido GG (parte del PAM)
        if len(ref) == 1 and len(alt) == 1:  # Solo SNVs
            # Si cambia G por otra cosa o viceversa, podria afectar un PAM
            if ref == 'G' and alt != 'G':
                efecto = "destruye_pam_potencial"
                nota = f"SNP {ref}>{alt} podria destruir un PAM (NGG) cercano"
            elif ref != 'G' and alt == 'G':
                efecto = "crea_pam_potencial"
                nota = f"SNP {ref}>{alt} podria crear un PAM (NGG) nuevo"

        var["efecto_off_target"] = efecto
        var["nota_off_target"] = nota
        efectos.append(var)

    return efectos


def generar_perfil_exonik(portador, variantes_muestra, indice_paciente):
    """
    Genera un archivo JSON de paciente compatible con el Modulo 01 de Exonik.
    
    Toma los datos REALES de 1000 Genomes y los formatea en la estructura
    que Exonik espera, con la misma estructura que paciente_001.json.
    """
    info_pop = portador["poblacion_info"]
    
    # Separar variante rs334 del resto
    variante_sca = None
    variantes_genomicas = []
    pam_destruidos = []
    pam_creados = []
    
    for v in variantes_muestra:
        if v["es_rs334"]:
            variante_sca = v
        else:
            variantes_genomicas.append({
                "cromosoma": v["cromosoma"],
                "posicion": v["posicion"],
                "ref": v["ref"],
                "alt": v["alt"],
                "cigosidad": v["cigosidad"],
                "gen": "HBB_region",
                "tipo": "SNV" if len(v["ref"]) == 1 and len(v["alt"]) == 1 else "INDEL",
                "rs_id": v["rs_id"],
                "efecto_off_target": v.get("efecto_off_target", "neutral"),
                "nota": v.get("nota_off_target", f"Variante real de 1000 Genomes ({portador['muestra_id']})"),
            })
            
            if v.get("efecto_off_target") == "destruye_pam_potencial":
                pam_destruidos.append(v["rs_id"])
            elif v.get("efecto_off_target") == "crea_pam_potencial":
                pam_creados.append(v["rs_id"])

    # Construir perfil
    perfil = {
        "id": f"EXO-REAL-{indice_paciente:03d}",
        "fuente": "1000 Genomes Project Phase 3",
        "muestra_original": portador["muestra_id"],
        "info_clinica": {
            "edad": "N/A (datos poblacionales)",
            "sexo": "M" if portador["sexo"] == "male" else "F",
            "etnia": info_pop.get("etnia", "Desconocida"),
            "region": info_pop.get("region", "Desconocida"),
            "poblacion_1000g": portador["poblacion"],
            "poblacion_nombre": info_pop.get("nombre", portador["poblacion"]),
            "diagnostico": "Anemia Falciforme (HbSS)" if portador["cigosidad"] == "homocigoto"
                          else "Portador rasgo falciforme (HbAS)",
            "hemoglobina_g_dl": "N/A",
            "hbf_porcentaje": "N/A",
            "crisis_vasooclusivas_anual": "N/A",
            "notas": (
                f"Datos genomicos reales del Proyecto 1000 Genomes. "
                f"Muestra: {portador['muestra_id']}. "
                f"Poblacion: {info_pop.get('nombre', portador['poblacion'])}. "
                f"Genotipo rs334: {portador['genotipo_rs334']}."
            ),
        },
        "variantes_hbb": [
            {
                "posicion_cds": 20,
                "ref": "A",
                "alt": "T",
                "rs_id": "rs334",
                "cigosidad": portador["cigosidad"],
                "alelo1": "T",
                "alelo2": "T" if portador["cigosidad"] == "homocigoto" else "A",
                "efecto": "E7V (Glu>Val)",
                "patogenicidad": "patogenica",
                "clasificacion_clinvar": "Patogenica",
                "genotipo_vcf": portador["genotipo_rs334"],
                "nota": f"Mutacion SCA confirmada en datos reales de {portador['muestra_id']}",
            }
        ],
        "variantes_genomicas": variantes_genomicas,
        "resumen_perfil_off_target": {
            "pam_destruidos_potenciales": pam_destruidos,
            "pam_creados_potenciales": pam_creados,
            "total_variantes_region_hbb": len(variantes_muestra),
            "total_variantes_no_sca": len(variantes_genomicas),
            "perfil_seguridad": "DATOS_REALES - Requiere analisis BLAST para evaluacion completa",
        },
    }

    return perfil


# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================

def main():
    print("\n" + "=" * 74)
    print("  EXONIK - FASE 1: OBTENCION DE GENOMAS REALES")
    print("  Fuente: Proyecto 1000 Genomes (2,504 personas, 26 poblaciones)")
    print("=" * 74)

    # Crear directorios
    os.makedirs(DIR_DESCARGAS, exist_ok=True)
    os.makedirs(DIR_PACIENTES_REALES, exist_ok=True)

    # =========================================================================
    # PASO 1: Descargar panel de muestras
    # =========================================================================
    print(f"\n  [PASO 1/5] Descargando panel de muestras...")
    ruta_panel = os.path.join(DIR_DESCARGAS, "panel_muestras.txt")
    if not descargar_con_progreso(PANEL_URL, ruta_panel, "Panel de muestras"):
        print("  [ERROR] No se pudo descargar el panel. Abortando.")
        sys.exit(1)

    panel = cargar_panel_poblaciones(ruta_panel)
    print(f"  Muestras en panel: {len(panel)}")

    # =========================================================================
    # PASO 2: Descargar VCF del cromosoma 11
    # =========================================================================
    print(f"\n  [PASO 2/5] Descargando VCF del cromosoma 11...")
    print(f"  NOTA: Este archivo pesa ~290MB. La descarga puede tomar varios minutos.")
    ruta_vcf = os.path.join(DIR_DESCARGAS, "chr11_1000genomes.vcf.gz")

    if not descargar_con_progreso(VCF_URL, ruta_vcf, "VCF cromosoma 11"):
        print("  Intentando servidor alternativo (NCBI)...")
        if not descargar_con_progreso(VCF_URL_ALT, ruta_vcf, "VCF cromosoma 11 (NCBI)"):
            print("  [ERROR] No se pudo descargar el VCF. Abortando.")
            sys.exit(1)

    # =========================================================================
    # PASO 3: Parsear VCF y extraer region HBB
    # =========================================================================
    print(f"\n  [PASO 3/5] Parseando VCF - extrayendo region HBB...")
    nombres_muestras, variantes = parsear_vcf_region_hbb(ruta_vcf)

    if not variantes:
        print("  [ERROR] No se encontraron variantes en la region HBB. Abortando.")
        sys.exit(1)

    # Mostrar variantes encontradas
    print(f"\n  === VARIANTES EN REGION HBB ===")
    print(f"  {'ID':<15} {'POS(GRCh37)':<15} {'POS(GRCh38)':<15} {'REF':<5} {'ALT':<5} {'rs334?'}")
    print(f"  {'-'*70}")
    for v in variantes[:20]:  # Mostrar las primeras 20
        marca = " <<<" if v["es_rs334"] else ""
        print(f"  {v['id']:<15} {v['posicion_grch37']:<15} {v['posicion_grch38']:<15} "
              f"{v['ref']:<5} {v['alt']:<5}{marca}")
    if len(variantes) > 20:
        print(f"  ... y {len(variantes) - 20} variantes mas")

    # =========================================================================
    # PASO 4: Encontrar portadores de rs334
    # =========================================================================
    print(f"\n  [PASO 4/5] Buscando portadores reales de rs334...")
    portadores = encontrar_portadores_rs334(variantes, nombres_muestras, panel)

    if not portadores:
        print("  [!] No se encontraron portadores de rs334.")
        sys.exit(1)

    # =========================================================================
    # PASO 5: Generar perfiles de pacientes reales
    # =========================================================================
    print(f"\n  [PASO 5/5] Generando perfiles de pacientes reales...")

    # Seleccionar una muestra representativa de portadores:
    # - Hasta 3 homocigotos (si existen)
    # - Hasta 5 heterocigotos de diferentes poblaciones
    homocigotos = [p for p in portadores if p["cigosidad"] == "homocigoto"]
    heterocigotos = [p for p in portadores if p["cigosidad"] == "heterocigoto"]

    # Seleccionar heterocigotos de poblaciones diversas
    pob_vistas = set()
    het_diversos = []
    for p in heterocigotos:
        if p["poblacion"] not in pob_vistas:
            het_diversos.append(p)
            pob_vistas.add(p["poblacion"])
        if len(het_diversos) >= 5:
            break

    seleccionados = homocigotos[:3] + het_diversos
    
    print(f"  Portadores seleccionados: {len(seleccionados)}")
    print(f"    Homocigotos: {min(len(homocigotos), 3)}")
    print(f"    Heterocigotos (diversas poblaciones): {len(het_diversos)}")

    perfiles_generados = []
    for i, portador in enumerate(seleccionados, 1):
        # Extraer todas las variantes de esta muestra
        vars_muestra = extraer_variantes_muestra(
            variantes, portador["indice"], portador["muestra_id"]
        )
        
        # Analizar efectos en off-targets
        vars_analizadas = analizar_variantes_para_offtarget(vars_muestra)
        
        # Generar perfil Exonik
        perfil = generar_perfil_exonik(portador, vars_muestra, i)
        
        # Guardar archivo JSON
        nombre_archivo = f"real_{portador['muestra_id']}_{portador['poblacion']}.json"
        ruta_archivo = os.path.join(DIR_PACIENTES_REALES, nombre_archivo)
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(perfil, f, indent=4, ensure_ascii=False)
        
        perfiles_generados.append({
            "archivo": nombre_archivo,
            "muestra": portador["muestra_id"],
            "poblacion": portador["poblacion"],
            "cigosidad": portador["cigosidad"],
            "variantes_totales": len(vars_muestra),
            "variantes_no_sca": len(vars_muestra) - 1,
        })
        
        print(f"    [{i}] {portador['muestra_id']} ({portador['poblacion']}) - "
              f"{portador['tipo']} - {len(vars_muestra)} variantes en region HBB "
              f"-> {nombre_archivo}")

    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print(f"\n{'=' * 74}")
    print(f"  FASE 1 COMPLETADA - RESUMEN")
    print(f"{'=' * 74}")
    print(f"  Fuente de datos:         1000 Genomes Project Phase 3")
    print(f"  Total muestras:          {len(nombres_muestras)}")
    print(f"  Variantes en region HBB: {len(variantes)}")
    print(f"  Portadores rs334:        {len(portadores)}")
    hom_count = len([p for p in portadores if p['cigosidad'] == 'homocigoto'])
    het_count = len([p for p in portadores if p['cigosidad'] == 'heterocigoto'])
    print(f"    Homocigotos (HbSS):    {hom_count}")
    print(f"    Heterocigotos (HbAS):  {het_count}")
    print(f"  Perfiles generados:      {len(perfiles_generados)}")
    print(f"  Guardados en:            {DIR_PACIENTES_REALES}")
    print(f"\n  Archivos generados:")
    for p in perfiles_generados:
        print(f"    - {p['archivo']} ({p['variantes_totales']} variantes)")
    
    print(f"\n  SIGUIENTE PASO:")
    print(f"  Estos perfiles pueden alimentarse al Modulo 01 de Exonik")
    print(f"  para obtener diagnosticos basados en datos REALES.")
    print(f"  Luego, en la Fase 2, usaremos BLAST+ para buscar off-targets")
    print(f"  reales en el genoma humano completo.")
    print(f"{'=' * 74}\n")

    return perfiles_generados


if __name__ == "__main__":
    main()

