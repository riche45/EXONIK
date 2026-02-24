#!/usr/bin/env python3
"""
==============================================================================
  EXONIK - FASE 5: REPORTE CLINICO INTEGRADO + DASHBOARD INTERACTIVO
==============================================================================

  Que hace este script?
  -----------------------
  Toma TODOS los resultados de las Fases 1-4 y genera:

  1. **Dashboard HTML interactivo** (abre en cualquier navegador):
     - Comparacion de guias CRISPR por seguridad
     - Off-targets por cromosoma (mapa genomico)
     - Comparacion entre pacientes (personalizacion)
     - Metricas del ARNm terapeutico
     - Estructura secundaria del ARNm

  2. **Reporte clinico por paciente** (HTML profesional):
     - Diagnostico y datos del paciente
     - Guia CRISPR recomendada + perfil de seguridad
     - ARNm terapeutico disenado
     - Puntuaciones globales

  3. **Tabla resumen exportable** (TSV):
     - Una fila por paciente con todas las metricas clave

  Archivos de salida:
  -------------------
  - reporte_integrado/dashboard_exonik.html
  - reporte_integrado/reporte_clinico_{muestra}.html (x5 pacientes)
  - reporte_integrado/resumen_ejecutivo.html
  - reporte_integrado/secuencias_laboratorio.txt
"""

import json
import os
import glob
import sys
from datetime import datetime

# =============================================================================
# CONFIGURACION
# =============================================================================

DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_PACIENTES = os.path.join(DIR_BASE, "datos_pacientes_reales")
DIR_BLAST = os.path.join(DIR_BASE, "resultados_blast")
DIR_PERSONAL = os.path.join(DIR_BASE, "resultados_personalizados")
DIR_MRNA = os.path.join(DIR_BASE, "resultados_mrna")
DIR_GUIAS = os.path.join(DIR_BASE, "guias_fasta")
DIR_SALIDA = os.path.join(DIR_BASE, "reporte_integrado")

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Colores Exonik
COL_PRIMARY = "#1a73e8"
COL_SUCCESS = "#34a853"
COL_WARNING = "#fbbc04"
COL_DANGER = "#ea4335"
COL_INFO = "#4285f4"
COL_DARK = "#202124"
COL_LIGHT = "#f8f9fa"
COL_BG = "#ffffff"

# =============================================================================
# CARGA DE DATOS
# =============================================================================

def cargar_datos():
    """Carga todos los resultados de Fases 1-4."""
    datos = {}

    # --- Fase 1: Pacientes reales ---
    print("\n  [1/4] Cargando pacientes reales...")
    datos["pacientes"] = {}
    for f in sorted(glob.glob(os.path.join(DIR_PACIENTES, "real_*.json"))):
        with open(f, "r", encoding="utf-8") as fh:
            pac = json.load(fh)
            muestra = pac["muestra_original"]
            datos["pacientes"][muestra] = pac
    print(f"        {len(datos['pacientes'])} pacientes cargados")

    # --- Fase 2: Off-targets BLAST ---
    print("  [2/4] Cargando off-targets BLAST...")
    archivos_blast = sorted(glob.glob(os.path.join(DIR_BLAST, "offtargets_reales_*.json")))
    if archivos_blast:
        with open(archivos_blast[-1], "r", encoding="utf-8") as fh:
            datos["blast"] = json.load(fh)
        print(f"        {datos['blast']['guias_analizadas']} guias analizadas")
    else:
        print("        [!] No se encontraron resultados BLAST")
        datos["blast"] = {}

    # --- Fase 3: Personalizacion ---
    print("  [3/4] Cargando personalizacion...")
    archivos_pers = sorted(glob.glob(os.path.join(DIR_PERSONAL, "personalizacion_completa_*.json")))
    if archivos_pers:
        with open(archivos_pers[-1], "r", encoding="utf-8") as fh:
            datos["personalizacion"] = json.load(fh)
        print(f"        {datos['personalizacion']['total_pacientes']} pacientes personalizados")
    else:
        print("        [!] No se encontraron resultados de personalizacion")
        datos["personalizacion"] = {}

    # --- Fase 4: ARNm ---
    print("  [4/4] Cargando validacion ARNm...")
    archivos_mrna = sorted(glob.glob(os.path.join(DIR_MRNA, "mrna_validacion_*.json")))
    if archivos_mrna:
        with open(archivos_mrna[-1], "r", encoding="utf-8") as fh:
            datos["mrna"] = json.load(fh)
        print(f"        Score global ARNm: {datos['mrna']['score_global']}/100")
    else:
        print("        [!] No se encontraron resultados de ARNm")
        datos["mrna"] = {}

    # --- Metadatos de guias ---
    meta_path = os.path.join(DIR_GUIAS, "guias_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as fh:
            datos["guias_meta"] = json.load(fh)
    else:
        datos["guias_meta"] = []

    return datos


# =============================================================================
# UTILIDADES HTML
# =============================================================================

CSS_GLOBAL = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #f0f2f5;
    color: #202124;
    line-height: 1.6;
  }

  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }

  .header {
    background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
    color: white;
    padding: 40px 30px;
    border-radius: 16px;
    margin-bottom: 30px;
    box-shadow: 0 4px 20px rgba(26,115,232,0.3);
  }

  .header h1 {
    font-size: 2em;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .header .subtitle {
    font-size: 1.1em;
    opacity: 0.9;
    font-weight: 300;
  }

  .card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    border: 1px solid #e8eaed;
  }

  .card h2 {
    font-size: 1.3em;
    font-weight: 600;
    color: #1a73e8;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e8eaed;
  }

  .card h3 {
    font-size: 1.05em;
    font-weight: 600;
    color: #5f6368;
    margin: 12px 0 8px 0;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin: 16px 0;
  }

  .metric-box {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    border: 1px solid #e8eaed;
  }

  .metric-box .value {
    font-size: 2em;
    font-weight: 700;
    line-height: 1.2;
  }

  .metric-box .label {
    font-size: 0.85em;
    color: #5f6368;
    margin-top: 4px;
  }

  .score-excellent { color: #34a853; }
  .score-good { color: #1a73e8; }
  .score-medium { color: #fbbc04; }
  .score-bad { color: #ea4335; }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 0.9em;
  }

  table th {
    background: #1a73e8;
    color: white;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
  }

  table td {
    padding: 8px 12px;
    border-bottom: 1px solid #e8eaed;
  }

  table tr:nth-child(even) { background: #f8f9fa; }
  table tr:hover { background: #e8f0fe; }

  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
  }

  .badge-high { background: #fce8e6; color: #c5221f; }
  .badge-medium { background: #fef7e0; color: #e37400; }
  .badge-low { background: #e6f4ea; color: #137333; }
  .badge-safe { background: #e8f0fe; color: #1967d2; }
  .badge-info { background: #e8eaed; color: #5f6368; }

  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .seq-box {
    font-family: 'Courier New', monospace;
    background: #263238;
    color: #80cbc4;
    padding: 16px;
    border-radius: 8px;
    font-size: 0.85em;
    overflow-x: auto;
    word-break: break-all;
    line-height: 1.8;
  }

  .footer {
    text-align: center;
    padding: 20px;
    color: #9aa0a6;
    font-size: 0.85em;
  }

  .nav-links {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin: 16px 0;
  }

  .nav-links a {
    display: inline-block;
    padding: 8px 16px;
    background: #e8f0fe;
    color: #1967d2;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.9em;
    transition: background 0.2s;
  }

  .nav-links a:hover { background: #d2e3fc; }

  .progress-bar {
    height: 8px;
    background: #e8eaed;
    border-radius: 4px;
    overflow: hidden;
    margin: 4px 0;
  }

  .progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
  }

  @media (max-width: 768px) {
    .two-col { grid-template-columns: 1fr; }
    .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  }

  .disclaimer {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 16px;
    margin-top: 20px;
    font-size: 0.85em;
    color: #856404;
  }
</style>
"""


def score_class(score):
    """Retorna la clase CSS segun el score."""
    if score >= 90: return "score-excellent"
    if score >= 75: return "score-good"
    if score >= 50: return "score-medium"
    return "score-bad"


def score_color(score):
    """Retorna color hex segun el score."""
    if score >= 90: return COL_SUCCESS
    if score >= 75: return COL_INFO
    if score >= 50: return COL_WARNING
    return COL_DANGER


def badge_riesgo(nivel):
    """Retorna badge HTML segun nivel de riesgo."""
    nivel = nivel.upper()
    if nivel == "ALTO": return '<span class="badge badge-high">ALTO</span>'
    if nivel == "MEDIO": return '<span class="badge badge-medium">MEDIO</span>'
    if nivel == "BAJO": return '<span class="badge badge-low">BAJO</span>'
    return f'<span class="badge badge-info">{nivel}</span>'


def progress_bar_html(value, max_val=100, color=None):
    """Genera HTML para barra de progreso."""
    pct = min(100, max(0, (value / max_val) * 100))
    if color is None:
        color = score_color(value)
    return f'''<div class="progress-bar">
        <div class="progress-fill" style="width:{pct:.0f}%;background:{color}"></div>
    </div>'''


def wrap_html(title, body_html, nav_html="", include_plotly=False):
    """Envuelve contenido en un documento HTML completo."""
    plotly_script = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>' if include_plotly else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Exonik</title>
    {plotly_script}
    {CSS_GLOBAL}
</head>
<body>
<div class="container">
{nav_html}
{body_html}
<div class="footer">
    Exonik v0.1.0 - Plataforma de Diseno de Terapia Genica Personalizada<br>
    Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}<br>
    <strong>SOLO PARA INVESTIGACION - NO PARA USO CLINICO</strong>
</div>
</div>
</body>
</html>"""


# =============================================================================
# GENERACION DE GRAFICOS CON PLOTLY
# =============================================================================

def generar_graficos(datos):
    """Genera los graficos interactivos con plotly y retorna HTML embebido."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    graficos = {}
    blast = datos.get("blast", {})
    personal = datos.get("personalizacion", {})
    mrna = datos.get("mrna", {})

    # =========================================================================
    # GRAFICO 1: Seguridad de guias CRISPR (barras)
    # =========================================================================
    resultados = blast.get("resultados", {})
    guias_ids = []
    scores_ref = []
    n_ot = []
    estrategias = []
    colores_bar = []

    # Ordenar: HBB primero, luego BCL
    orden = sorted(resultados.keys(), key=lambda x: (0 if x.startswith("HBB") else 1, x))
    for gid in orden:
        g = resultados[gid]
        guias_ids.append(gid)
        sc = g["resumen_seguridad"]["score_seguridad"]
        scores_ref.append(sc)
        n_ot.append(g["resumen_seguridad"]["total_off_targets"])
        estrategias.append(g.get("estrategia", ""))
        colores_bar.append(COL_SUCCESS if sc >= 95 else COL_WARNING if sc >= 80 else COL_DANGER)

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=guias_ids, y=scores_ref,
        marker_color=colores_bar,
        text=[f"{s}/100" for s in scores_ref],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Score: %{y}/100<br>Off-targets: %{customdata}<extra></extra>",
        customdata=n_ot
    ))
    fig1.update_layout(
        title=dict(text="Seguridad de Guias CRISPR (Genoma de Referencia)", font=dict(size=16)),
        yaxis=dict(title="Score de Seguridad", range=[0, 110]),
        xaxis=dict(title="Guia CRISPR"),
        template="plotly_white",
        height=400,
        margin=dict(t=60, b=40),
    )
    graficos["guias_seguridad"] = fig1.to_html(full_html=False, include_plotlyjs=False)

    # =========================================================================
    # GRAFICO 2: Off-targets por cromosoma (scatter)
    # =========================================================================
    ot_chr = {}
    for gid, g in resultados.items():
        for ot in g.get("off_targets", []):
            cr = ot.get("cromosoma", "?")
            # Extraer nombre de cromosoma limpio
            if "NC_000011" in cr: cr_name = "chr11"
            elif "NC_000002" in cr: cr_name = "chr2"
            elif "NC_000014" in cr: cr_name = "chr14"
            elif "NT_187601" in cr: cr_name = "chrUn"
            else: cr_name = cr[:10]
            if cr_name not in ot_chr:
                ot_chr[cr_name] = []
            ot_chr[cr_name].append({
                "guia": gid,
                "pos": ot["posicion_start"],
                "mm": ot["mismatches"],
                "riesgo": ot["riesgo_nivel"],
                "pam": ot.get("pam_secuencia", "?")
            })

    fig2 = go.Figure()
    chr_colors = {"chr2": "#4285f4", "chr11": "#ea4335", "chr14": "#fbbc04", "chrUn": "#9aa0a6"}
    for cr_name, ots in sorted(ot_chr.items()):
        fig2.add_trace(go.Scatter(
            x=[o["pos"] for o in ots],
            y=[o["mm"] for o in ots],
            mode="markers",
            marker=dict(size=14, color=chr_colors.get(cr_name, "#5f6368"), line=dict(width=1, color="white")),
            name=cr_name,
            text=[f"{o['guia']} | {o['riesgo']} | PAM:{o['pam']}" for o in ots],
            hovertemplate="<b>%{text}</b><br>Pos: %{x:,.0f}<br>Mismatches: %{y}<extra>%{fullData.name}</extra>"
        ))
    fig2.update_layout(
        title=dict(text="Mapa de Off-targets por Cromosoma", font=dict(size=16)),
        xaxis=dict(title="Posicion Genomica"),
        yaxis=dict(title="Mismatches", dtick=1, range=[-0.5, 4.5]),
        template="plotly_white",
        height=400,
        margin=dict(t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    graficos["ot_cromosoma"] = fig2.to_html(full_html=False, include_plotlyjs=False)

    # =========================================================================
    # GRAFICO 3: Comparacion entre pacientes (heatmap de scores)
    # =========================================================================
    perfiles = personal.get("perfiles", {})
    if perfiles:
        pac_ids = sorted(perfiles.keys())
        guias_all = []
        # Recopilar todas las guias
        for pid in pac_ids:
            for gid in perfiles[pid].get("guias", {}):
                if gid not in guias_all:
                    guias_all.append(gid)
        guias_all.sort(key=lambda x: (0 if x.startswith("HBB") else 1, x))

        # Construir matriz de scores personalizados
        z_data = []
        hover_data = []
        for pid in pac_ids:
            row = []
            h_row = []
            pob = perfiles[pid].get("poblacion", "?")
            for gid in guias_all:
                ginfo = perfiles[pid].get("guias", {}).get(gid, {})
                res = ginfo.get("resumen", {})
                sc = res.get("score_personalizado", res.get("score_referencia", 100))
                row.append(sc)
                n_elim = res.get("eliminados", 0)
                n_agr = res.get("mas_peligrosos", 0)
                h_row.append(f"{pid} ({pob})<br>{gid}: {sc}/100<br>Elim:{n_elim} Agrav:{n_agr}")
            z_data.append(row)
            hover_data.append(h_row)

        fig3 = go.Figure(go.Heatmap(
            z=z_data,
            x=guias_all,
            y=[f"{p} ({perfiles[p].get('poblacion','?')[:6]})" for p in pac_ids],
            colorscale=[[0, COL_DANGER], [0.5, COL_WARNING], [0.8, COL_INFO], [1, COL_SUCCESS]],
            zmin=0, zmax=100,
            text=[[f"{v}" for v in row] for row in z_data],
            texttemplate="%{text}",
            textfont=dict(size=11, color="white"),
            hovertext=hover_data,
            hovertemplate="%{hovertext}<extra></extra>",
            colorbar=dict(title="Score"),
        ))
        fig3.update_layout(
            title=dict(text="Score de Seguridad Personalizado: Paciente x Guia", font=dict(size=16)),
            xaxis=dict(title="Guia CRISPR"),
            yaxis=dict(title="Paciente"),
            template="plotly_white",
            height=350,
            margin=dict(t=60, b=40, l=160),
        )
        graficos["heatmap_pacientes"] = fig3.to_html(full_html=False, include_plotlyjs=False)
    else:
        graficos["heatmap_pacientes"] = "<p>Sin datos de personalizacion</p>"

    # =========================================================================
    # GRAFICO 4: Metricas del ARNm (radar)
    # =========================================================================
    if mrna:
        categorias = ["CAI", "GC Balance", "AUG Accesible", "No Inmunogenico", "Estabilidad", "Sin Motivos"]
        opt = mrna.get("optimizacion", {})
        mejor = opt.get("mejor_estrategia", "")
        metricas_est = opt.get("estrategias", {}).get(mejor, {}).get("metricas", {})

        cai = metricas_est.get("cai", 0) * 100
        gc = metricas_est.get("gc_content", 50)
        # Normalizar GC: 55% optimo, penalizar lejos de 55
        gc_score = max(0, 100 - abs(gc - 55) * 4)
        aug_score = mrna.get("accesibilidad_aug", {}).get("score_accesibilidad", 0)
        inmuno_score = mrna.get("inmunogenicidad", {}).get("score", 0)
        estab_score = mrna.get("estabilidad", {}).get("score_estabilidad", 0)
        motivos = metricas_est.get("total_motivos_problematicos", 0)
        motivos_score = 100 if motivos == 0 else max(0, 100 - motivos * 25)

        valores = [cai, gc_score, aug_score, inmuno_score, estab_score, motivos_score]

        fig4 = go.Figure()
        fig4.add_trace(go.Scatterpolar(
            r=valores + [valores[0]],
            theta=categorias + [categorias[0]],
            fill="toself",
            fillcolor="rgba(26,115,232,0.15)",
            line=dict(color=COL_PRIMARY, width=2),
            marker=dict(size=8, color=COL_PRIMARY),
            hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>"
        ))
        fig4.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], ticksuffix=""),
            ),
            title=dict(text=f"Perfil del ARNm Terapeutico (Estrategia: {mejor})", font=dict(size=16)),
            template="plotly_white",
            height=420,
            margin=dict(t=80, b=40),
            showlegend=False,
        )
        graficos["radar_mrna"] = fig4.to_html(full_html=False, include_plotlyjs=False)
    else:
        graficos["radar_mrna"] = "<p>Sin datos de ARNm</p>"

    # =========================================================================
    # GRAFICO 5: GC content por ventana del CDS (linea)
    # =========================================================================
    if mrna:
        mejor_est = mrna.get("optimizacion", {}).get("mejor_estrategia", "")
        gc_ventanas = mrna.get("optimizacion", {}).get("estrategias", {}).get(mejor_est, {}).get("metricas", {}).get("gc_ventanas", [])
        if gc_ventanas:
            x_pos = list(range(1, len(gc_ventanas) + 1))
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=x_pos, y=gc_ventanas,
                mode="lines+markers",
                line=dict(color=COL_PRIMARY, width=2),
                marker=dict(size=5),
                name="GC% por ventana",
                hovertemplate="Ventana %{x}: %{y:.1f}%<extra></extra>"
            ))
            # Rango optimo
            fig5.add_hrect(y0=45, y1=65, fillcolor=COL_SUCCESS, opacity=0.1,
                           annotation_text="Rango optimo (45-65%)", annotation_position="top left")
            fig5.update_layout(
                title=dict(text="GC Content por Ventana del CDS Optimizado", font=dict(size=16)),
                xaxis=dict(title="Ventana (30nt cada una)"),
                yaxis=dict(title="GC %", range=[20, 90]),
                template="plotly_white",
                height=350,
                margin=dict(t=60, b=40),
            )
            graficos["gc_ventanas"] = fig5.to_html(full_html=False, include_plotlyjs=False)
        else:
            graficos["gc_ventanas"] = ""
    else:
        graficos["gc_ventanas"] = ""

    # =========================================================================
    # GRAFICO 6: Comparacion de estrategias de optimizacion (barras agrupadas)
    # =========================================================================
    if mrna:
        estrategias = mrna.get("optimizacion", {}).get("estrategias", {})
        if estrategias:
            nombres = list(estrategias.keys())
            cais = [estrategias[n]["metricas"]["cai"] for n in nombres]
            gcs = [estrategias[n]["metricas"]["gc_content"] for n in nombres]
            scores_comp = [estrategias[n]["score_compuesto"] for n in nombres]
            motivos_t = [estrategias[n]["metricas"]["total_motivos_problematicos"] for n in nombres]

            fig6 = make_subplots(rows=1, cols=3,
                                 subplot_titles=["CAI (Codon Adaptation)", "GC Content (%)", "Score Compuesto"])
            fig6.add_trace(go.Bar(x=nombres, y=cais, marker_color=[COL_PRIMARY]*3,
                                  text=[f"{v:.2f}" for v in cais], textposition="outside"), row=1, col=1)
            fig6.add_trace(go.Bar(x=nombres, y=gcs,
                                  marker_color=[COL_DANGER if g > 65 else COL_SUCCESS if g >= 45 else COL_WARNING for g in gcs],
                                  text=[f"{v:.1f}%" for v in gcs], textposition="outside"), row=1, col=2)
            fig6.add_trace(go.Bar(x=nombres, y=scores_comp,
                                  marker_color=[score_color(s) for s in scores_comp],
                                  text=[f"{v:.1f}" for v in scores_comp], textposition="outside"), row=1, col=3)
            fig6.update_layout(
                title=dict(text="Comparacion de Estrategias de Optimizacion de Codones", font=dict(size=16)),
                template="plotly_white",
                height=380,
                showlegend=False,
                margin=dict(t=80, b=40),
            )
            fig6.update_yaxes(range=[0, 1.15], row=1, col=1)
            fig6.update_yaxes(range=[0, 80], row=1, col=2)
            fig6.update_yaxes(range=[0, 110], row=1, col=3)
            graficos["estrategias_comp"] = fig6.to_html(full_html=False, include_plotlyjs=False)
        else:
            graficos["estrategias_comp"] = ""
    else:
        graficos["estrategias_comp"] = ""

    return graficos


# =============================================================================
# DASHBOARD PRINCIPAL
# =============================================================================

def generar_dashboard(datos, graficos):
    """Genera el dashboard HTML principal."""
    blast = datos.get("blast", {})
    personal = datos.get("personalizacion", {})
    mrna_data = datos.get("mrna", {})
    pacientes = datos.get("pacientes", {})

    # --- Metricas resumen ---
    n_pacientes = len(pacientes)
    n_guias = blast.get("guias_analizadas", 0)
    total_ot_ref = sum(
        r["resumen_seguridad"]["total_off_targets"]
        for r in blast.get("resultados", {}).values()
    )
    mrna_score = mrna_data.get("score_global", 0)

    # Mejor guia
    mejor_guia = ""
    mejor_score = 0
    for gid, g in blast.get("resultados", {}).items():
        sc = g["resumen_seguridad"]["score_seguridad"]
        if sc > mejor_score or (sc == mejor_score and gid.startswith("HBB")):
            mejor_score = sc
            mejor_guia = gid

    # Guias con score 100
    guias_100 = [gid for gid, g in blast.get("resultados", {}).items()
                 if g["resumen_seguridad"]["score_seguridad"] == 100]

    nav = '''<div class="nav-links">
        <a href="#resumen">Resumen</a>
        <a href="#crispr">CRISPR</a>
        <a href="#offtargets">Off-targets</a>
        <a href="#personalizacion">Personalizacion</a>
        <a href="#mrna">ARNm</a>
        <a href="#pacientes">Pacientes</a>
    </div>'''

    # --- Seccion 1: Header ---
    body = f'''
    <div class="header">
        <h1>EXONIK Dashboard</h1>
        <div class="subtitle">Plataforma de Diseno de Terapia Genica Personalizada para Anemia Falciforme</div>
        <div class="subtitle" style="margin-top:8px;opacity:0.7">
            Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Genoma: GRCh38.p14 | BLAST+ v2.17.0
        </div>
    </div>

    {nav}

    <!-- RESUMEN EJECUTIVO -->
    <div class="card" id="resumen">
        <h2>Resumen Ejecutivo</h2>
        <div class="metrics-grid">
            <div class="metric-box">
                <div class="value" style="color:{COL_PRIMARY}">{n_pacientes}</div>
                <div class="label">Pacientes Reales</div>
            </div>
            <div class="metric-box">
                <div class="value" style="color:{COL_PRIMARY}">{n_guias}</div>
                <div class="label">Guias CRISPR</div>
            </div>
            <div class="metric-box">
                <div class="value" style="color:{COL_WARNING}">{total_ot_ref}</div>
                <div class="label">Off-targets Totales</div>
            </div>
            <div class="metric-box">
                <div class="value" style="color:{COL_SUCCESS}">{len(guias_100)}</div>
                <div class="label">Guias con Score 100</div>
            </div>
            <div class="metric-box">
                <div class="value {score_class(mrna_score)}">{mrna_score}/100</div>
                <div class="label">Score ARNm Global</div>
            </div>
            <div class="metric-box">
                <div class="value" style="color:{COL_SUCCESS}">{mejor_guia}</div>
                <div class="label">Mejor Guia HBB</div>
            </div>
        </div>
    </div>
    '''

    # --- Seccion 2: CRISPR ---
    body += f'''
    <div class="card" id="crispr">
        <h2>Analisis de Guias CRISPR</h2>
        <p style="color:#5f6368;margin-bottom:12px">
            12 guias disenadas: 6 para correccion directa del gen HBB y 6 para disrupcion del enhancer BCL11A.
            Cada guia fue analizada contra el genoma humano completo ({blast.get("genoma_referencia","GRCh38")}).
        </p>
        {graficos.get("guias_seguridad", "")}
        <table>
            <tr>
                <th>Guia</th><th>Secuencia (5'&rarr;3')</th><th>PAM</th>
                <th>Estrategia</th><th>Hits BLAST</th><th>Off-targets</th><th>Score</th>
            </tr>'''

    for gid in sorted(blast.get("resultados", {}).keys(), key=lambda x: (0 if x.startswith("HBB") else 1, x)):
        g = blast["resultados"][gid]
        sc = g["resumen_seguridad"]["score_seguridad"]
        n = g["resumen_seguridad"]["total_off_targets"]
        est = g.get("estrategia", "").replace("_", " ").title()
        body += f'''
            <tr>
                <td><strong>{gid}</strong></td>
                <td class="seq-box" style="padding:4px 8px;font-size:0.8em;background:#f8f9fa;color:#202124">{g["secuencia"]}</td>
                <td>{g["pam"]}</td>
                <td>{est}</td>
                <td>{g["total_hits_blast"]:,}</td>
                <td>{n} {badge_riesgo("BAJO" if n == 0 else "MEDIO")}</td>
                <td><strong class="{score_class(sc)}">{sc}/100</strong></td>
            </tr>'''
    body += '</table></div>'

    # --- Seccion 3: Off-targets ---
    body += f'''
    <div class="card" id="offtargets">
        <h2>Mapa de Off-targets Genomicos</h2>
        <p style="color:#5f6368;margin-bottom:12px">
            Cada punto representa un sitio donde CRISPR-Cas9 podria cortar fuera del objetivo.
            La posicion X muestra la ubicacion en el cromosoma, Y los mismatches (0 = match perfecto = mas peligroso).
        </p>
        {graficos.get("ot_cromosoma", "")}
    </div>
    '''

    # --- Seccion 4: Personalizacion ---
    body += f'''
    <div class="card" id="personalizacion">
        <h2>Personalizacion por Paciente</h2>
        <p style="color:#5f6368;margin-bottom:12px">
            Cruce de 12 off-targets de referencia con las variantes geneticas reales de cada paciente
            (datos de 1000 Genomes Project). Cromosomas personalizados: chr2, chr11, chr14.
        </p>
        {graficos.get("heatmap_pacientes", "")}

        <h3>Hallazgo clave: Linkage Disequilibrium en chr11</h3>
        <p style="color:#5f6368;font-size:0.9em;">
            Los 5 pacientes comparten un SNP en <strong>chr11:5,227,013</strong> (A&rarr;G, homocigoto).
            Esta variante esta en <em>linkage disequilibrium</em> con rs334 (la mutacion SCA, solo 11 bp de distancia).
            Esto <strong>agrava</strong> el off-target de la guia HBB-g21 (reduce mismatches de 1 a 0),
            haciendo que HBB-g66 y HBB-g68 sean las opciones mas seguras.
        </p>
    </div>
    '''

    # --- Seccion 5: ARNm ---
    mrna_seq = mrna_data.get("mrna", {}).get("secuencia_completa", "")
    mrna_len = mrna_data.get("mrna", {}).get("longitud", 0)
    mrna_gc = mrna_data.get("mrna", {}).get("gc_content", 0)
    aug_score = mrna_data.get("accesibilidad_aug", {}).get("score_accesibilidad", 0)
    inmuno_score = mrna_data.get("inmunogenicidad", {}).get("score", 0)
    estab_score = mrna_data.get("estabilidad", {}).get("score_estabilidad", 0)
    vida_media = mrna_data.get("estabilidad", {}).get("vida_media_estimada", "?")
    cap = mrna_data.get("mrna", {}).get("cap", "?")
    mod = mrna_data.get("mrna", {}).get("modificacion", "?")

    body += f'''
    <div class="card" id="mrna">
        <h2>ARNm Terapeutico - Hemoglobina Beta Normal</h2>
        <div class="metrics-grid">
            <div class="metric-box">
                <div class="value {score_class(mrna_score)}">{mrna_score}/100</div>
                <div class="label">Score Global</div>
                {progress_bar_html(mrna_score)}
            </div>
            <div class="metric-box">
                <div class="value {score_class(aug_score)}">{aug_score}/100</div>
                <div class="label">AUG Accesible</div>
                {progress_bar_html(aug_score)}
            </div>
            <div class="metric-box">
                <div class="value {score_class(inmuno_score)}">{inmuno_score}/100</div>
                <div class="label">Inmunogenicidad</div>
                {progress_bar_html(inmuno_score)}
            </div>
            <div class="metric-box">
                <div class="value {score_class(estab_score)}">{estab_score}%</div>
                <div class="label">Estabilidad</div>
                {progress_bar_html(estab_score)}
            </div>
        </div>

        <div class="two-col">
            <div>
                <h3>Propiedades del ARNm</h3>
                <table>
                    <tr><td>Longitud total</td><td><strong>{mrna_len} nt</strong></td></tr>
                    <tr><td>CDS (codificante)</td><td>444 nt (148 codones)</td></tr>
                    <tr><td>GC content</td><td>{mrna_gc:.1f}%</td></tr>
                    <tr><td>Cap 5'</td><td>{cap}</td></tr>
                    <tr><td>Modificacion</td><td>{mod}</td></tr>
                    <tr><td>Vida media estimada</td><td>{vida_media}</td></tr>
                    <tr><td>Uridinas (m1Psi)</td><td>{mrna_data.get("mrna",{}).get("n_uridinas",0)}</td></tr>
                </table>
            </div>
            <div>
                {graficos.get("radar_mrna", "")}
            </div>
        </div>

        {graficos.get("estrategias_comp", "")}
        {graficos.get("gc_ventanas", "")}

        <h3>Secuencia del ARNm Terapeutico (595 nt)</h3>
        <div class="seq-box">{_colorear_mrna(mrna_seq)}</div>
    </div>
    '''

    # --- Seccion 6: Tabla de pacientes ---
    body += '''
    <div class="card" id="pacientes">
        <h2>Pacientes Reales Analizados</h2>
        <p style="color:#5f6368;margin-bottom:12px">
            5 portadores reales de la mutacion rs334 del Proyecto 1000 Genomes, seleccionados
            de poblaciones diversas con alta prevalencia de Anemia Falciforme.
        </p>
        <table>
            <tr>
                <th>Muestra</th><th>ID Exonik</th><th>Poblacion</th>
                <th>Diagnostico</th><th>Mejor Guia</th><th>Score</th><th>Reporte</th>
            </tr>'''

    perfiles = personal.get("perfiles", {})
    for muestra, pac in sorted(pacientes.items()):
        info = pac.get("info_clinica", {})
        pob = info.get("poblacion_nombre", "?")
        diag = info.get("diagnostico", "?")
        eid = pac.get("id", "?")

        # Encontrar mejor guia HBB para este paciente
        mejor_g = "N/A"
        mejor_s = 0
        if muestra in perfiles:
            for gid, ginfo in perfiles[muestra].get("guias", {}).items():
                if not gid.startswith("HBB"):
                    continue
                sc = ginfo.get("resumen", {}).get("score_personalizado", 0)
                if sc > mejor_s:
                    mejor_s = sc
                    mejor_g = gid

        body += f'''
            <tr>
                <td><strong>{muestra}</strong></td>
                <td>{eid}</td>
                <td>{pob}</td>
                <td>{diag}</td>
                <td>{mejor_g}</td>
                <td><strong class="{score_class(mejor_s)}">{mejor_s}/100</strong></td>
                <td><a href="reporte_clinico_{muestra}.html" style="color:{COL_PRIMARY}">Ver reporte</a></td>
            </tr>'''

    body += '''</table>
        <div class="nav-links" style="margin-top:16px">'''
    for muestra in sorted(pacientes.keys()):
        body += f'<a href="reporte_clinico_{muestra}.html">Reporte {muestra}</a>'
    body += '</div></div>'

    # --- Disclaimer ---
    body += '''
    <div class="disclaimer">
        <strong>AVISO IMPORTANTE:</strong> Este es un prototipo computacional con fines exclusivamente
        educativos y de investigacion. NO constituye consejo medico ni ha sido validado clinicamente.
        Los resultados requieren verificacion experimental in vitro/in vivo antes de cualquier
        aplicacion terapeutica. Exonik v0.1.0 - Solo para investigacion (Research Use Only).
    </div>
    '''

    return wrap_html("Dashboard Exonik", body, nav, include_plotly=True)


def _colorear_mrna(seq):
    """Colorea la secuencia del ARNm por regiones."""
    if not seq:
        return ""
    # Estructura: [5'UTR 10] [CDS 444] [3'UTR 21] [PolyA 120]
    utr5 = seq[:10]
    cds = seq[10:454]
    utr3 = seq[454:475]
    polya = seq[475:]

    return (
        f'<span style="color:#ff9800" title="5\'UTR Kozak (10nt)">{utr5}</span>'
        f'<span style="color:#4caf50" title="CDS optimizado (444nt)">{cds}</span>'
        f'<span style="color:#2196f3" title="3\'UTR (21nt)">{utr3}</span>'
        f'<span style="color:#9e9e9e" title="Poly-A (120nt)">{polya}</span>'
    )


# =============================================================================
# REPORTES CLINICOS POR PACIENTE
# =============================================================================

def generar_reporte_clinico(muestra, datos):
    """Genera un reporte clinico HTML individual para un paciente."""
    pac = datos["pacientes"].get(muestra, {})
    personal = datos.get("personalizacion", {})
    perfiles = personal.get("perfiles", {})
    perfil = perfiles.get(muestra, {})
    mrna_data = datos.get("mrna", {})
    blast = datos.get("blast", {})

    info = pac.get("info_clinica", {})
    pob = info.get("poblacion_nombre", "?")
    pob_code = info.get("poblacion_1000g", "?")
    diag = info.get("diagnostico", "?")
    sexo = info.get("sexo", "?")
    eid = pac.get("id", "?")
    genotipo = ""
    for v in pac.get("variantes_hbb", []):
        if v.get("rs_id") == "rs334":
            genotipo = v.get("genotipo_vcf", "?")

    nav = '<div class="nav-links"><a href="dashboard_exonik.html">&larr; Volver al Dashboard</a></div>'

    body = f'''
    <div class="header">
        <h1>Reporte Clinico - {muestra}</h1>
        <div class="subtitle">{pob} | {diag} | {eid}</div>
    </div>

    <div class="card">
        <h2>Informacion del Paciente</h2>
        <div class="two-col">
            <div>
                <table>
                    <tr><td>Muestra</td><td><strong>{muestra}</strong></td></tr>
                    <tr><td>ID Exonik</td><td>{eid}</td></tr>
                    <tr><td>Sexo</td><td>{sexo}</td></tr>
                    <tr><td>Poblacion</td><td>{pob} ({pob_code})</td></tr>
                    <tr><td>Diagnostico</td><td>{diag}</td></tr>
                    <tr><td>Genotipo rs334</td><td><strong>{genotipo}</strong></td></tr>
                    <tr><td>Fuente</td><td>1000 Genomes Project Phase 3</td></tr>
                </table>
            </div>
            <div>
                <h3>Variantes en Region HBB</h3>
                <table>
                    <tr><th>Posicion</th><th>Ref</th><th>Alt</th><th>Cigosidad</th></tr>'''

    for v in pac.get("variantes_genomicas", [])[:8]:
        body += f'''
                    <tr>
                        <td>{v.get("posicion", "?"):,}</td>
                        <td>{v.get("ref", "?")}</td>
                        <td>{v.get("alt", "?")}</td>
                        <td>{v.get("cigosidad", "?")}</td>
                    </tr>'''
    n_vars = len(pac.get("variantes_genomicas", []))
    if n_vars > 8:
        body += f'<tr><td colspan="4" style="color:#9aa0a6">... y {n_vars - 8} variantes mas</td></tr>'
    body += '</table></div></div></div>'

    # --- Perfil CRISPR personalizado ---
    body += '''
    <div class="card">
        <h2>Perfil CRISPR Personalizado</h2>
        <p style="color:#5f6368;margin-bottom:12px">
            Analisis de off-targets cruzado con las variantes geneticas reales del paciente.
        </p>
        <table>
            <tr>
                <th>Guia</th><th>Estrategia</th><th>Off-targets</th>
                <th>Score Ref.</th><th>Score Personal.</th><th>Efecto</th>
            </tr>'''

    mejor_guia_hbb = ""
    mejor_score_hbb = 0
    mejor_guia_bcl = ""
    mejor_score_bcl = 0

    guias_orden = sorted(perfil.get("guias", {}).keys(), key=lambda x: (0 if x.startswith("HBB") else 1, x))
    for gid in guias_orden:
        ginfo = perfil["guias"][gid]
        res = ginfo.get("resumen", {})
        sc_ref = res.get("score_referencia", 100)
        sc_per = res.get("score_personalizado", 100)
        n_ot = res.get("total_off_targets", 0)
        n_elim = res.get("eliminados", 0)
        n_agr = res.get("mas_peligrosos", 0)
        est_name = ginfo.get("estrategia", "").replace("_", " ").title()

        efecto_parts = []
        if n_elim > 0: efecto_parts.append(f'<span class="badge badge-low">{n_elim} eliminados</span>')
        if n_agr > 0: efecto_parts.append(f'<span class="badge badge-high">{n_agr} agravados</span>')
        if n_ot == 0: efecto_parts.append('<span class="badge badge-safe">Limpia</span>')
        elif not efecto_parts: efecto_parts.append(f'<span class="badge badge-info">{n_ot} sin cambio</span>')

        body += f'''
            <tr>
                <td><strong>{gid}</strong></td>
                <td>{est_name}</td>
                <td>{n_ot}</td>
                <td class="{score_class(sc_ref)}">{sc_ref}/100</td>
                <td><strong class="{score_class(sc_per)}">{sc_per}/100</strong></td>
                <td>{" ".join(efecto_parts)}</td>
            </tr>'''

        # Rastrear mejor guia
        if gid.startswith("HBB") and sc_per > mejor_score_hbb:
            mejor_score_hbb = sc_per
            mejor_guia_hbb = gid
        elif gid.startswith("BCL") and sc_per > mejor_score_bcl:
            mejor_score_bcl = sc_per
            mejor_guia_bcl = gid

    body += '</table></div>'

    # --- Recomendacion terapeutica ---
    mrna_score = mrna_data.get("score_global", 0)
    body += f'''
    <div class="card" style="border-left: 4px solid {COL_SUCCESS}">
        <h2>Recomendacion Terapeutica para {muestra}</h2>
        <div class="two-col">
            <div>
                <h3>Terapia CRISPR</h3>
                <table>
                    <tr><td>Guia HBB recomendada</td><td><strong style="font-size:1.2em">{mejor_guia_hbb}</strong></td></tr>
                    <tr><td>Score personalizado</td><td><strong class="{score_class(mejor_score_hbb)}" style="font-size:1.2em">{mejor_score_hbb}/100</strong></td></tr>
                    <tr><td>Guia BCL11A recomendada</td><td><strong>{mejor_guia_bcl}</strong></td></tr>
                    <tr><td>Score BCL11A</td><td><strong class="{score_class(mejor_score_bcl)}">{mejor_score_bcl}/100</strong></td></tr>
                    <tr><td>Nucleasa</td><td>SpCas9 (NGG)</td></tr>
                </table>
            </div>
            <div>
                <h3>Terapia ARNm Complementaria</h3>
                <table>
                    <tr><td>Score ARNm</td><td><strong class="{score_class(mrna_score)}" style="font-size:1.2em">{mrna_score}/100</strong></td></tr>
                    <tr><td>Proteina</td><td>HBB normal (147 aa)</td></tr>
                    <tr><td>Longitud ARNm</td><td>{mrna_data.get("mrna",{}).get("longitud",0)} nt</td></tr>
                    <tr><td>Modificacion</td><td>m1Psi (N1-metilpseudouridina)</td></tr>
                    <tr><td>Vehiculo</td><td>LNP + anti-CD71</td></tr>
                </table>
            </div>
        </div>

        <h3 style="margin-top:20px">Estrategia Combinada</h3>
        <div style="background:#e6f4ea;padding:16px;border-radius:8px;margin-top:8px">
            <strong>1. CRISPR ({mejor_guia_hbb}):</strong> Corregir la mutacion SCA (c.20A>T) directamente en celulas madre
            hematopoyeticas. Score de seguridad personalizado: <strong>{mejor_score_hbb}/100</strong>.<br><br>
            <strong>2. ARNm HBB:</strong> Mientras las celulas editadas se expanden, administrar ARNm encapsulado
            en LNP dirigido a precursores eritroides para produccion transitoria de hemoglobina normal.
            Score: <strong>{mrna_score}/100</strong>.<br><br>
            <strong>3. BCL11A ({mejor_guia_bcl}):</strong> Opcion alternativa/complementaria: disrumpir el enhancer
            de BCL11A para reactivar hemoglobina fetal (HbF), similar a Casgevy.
        </div>
    </div>
    '''

    # --- Disclaimer ---
    body += '''
    <div class="disclaimer">
        <strong>AVISO:</strong> Este reporte es generado computacionalmente con fines educativos y de investigacion.
        No constituye diagnostico ni recomendacion medica. Requiere validacion experimental y aprobacion regulatoria
        antes de cualquier aplicacion clinica. Exonik v0.1.0 (Research Use Only).
    </div>
    '''

    return wrap_html(f"Reporte {muestra}", body, nav)


# =============================================================================
# RESUMEN EJECUTIVO
# =============================================================================

def generar_resumen_ejecutivo(datos):
    """Genera una pagina de resumen ejecutivo."""
    blast = datos.get("blast", {})
    personal = datos.get("personalizacion", {})
    mrna_data = datos.get("mrna", {})
    pacientes = datos.get("pacientes", {})
    perfiles = personal.get("perfiles", {})

    nav = '<div class="nav-links"><a href="dashboard_exonik.html">&larr; Dashboard</a></div>'

    body = f'''
    <div class="header" style="background:linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1a73e8 100%)">
        <h1>Exonik - Resumen Ejecutivo</h1>
        <div class="subtitle">Terapia Genica Personalizada para Anemia Falciforme</div>
    </div>

    <div class="card">
        <h2>Vision General del Proyecto</h2>
        <p>Exonik es una plataforma computacional que disena terapia genica <strong>personalizada</strong>
        para enfermedades monogenicas, comenzando con Anemia Falciforme (SCA). A diferencia de los
        tratamientos actuales que usan un enfoque de "talla unica", Exonik analiza el genoma real
        de cada paciente para identificar la guia CRISPR mas segura <em>para esa persona especifica</em>.</p>
    </div>

    <div class="card">
        <h2>Pipeline Completado</h2>
        <table>
            <tr><th>Fase</th><th>Descripcion</th><th>Resultado Clave</th><th>Estado</th></tr>
            <tr>
                <td><strong>Fase 1</strong></td>
                <td>Datos genomicos reales (1000 Genomes)</td>
                <td>{len(pacientes)} pacientes de 5 poblaciones diversas</td>
                <td><span class="badge badge-low">Completada</span></td>
            </tr>
            <tr>
                <td><strong>Fase 2</strong></td>
                <td>Off-targets con BLAST+ vs genoma completo</td>
                <td>12 guias analizadas, {sum(r["resumen_seguridad"]["total_off_targets"] for r in blast.get("resultados",{}).values())} off-targets encontrados</td>
                <td><span class="badge badge-low">Completada</span></td>
            </tr>
            <tr>
                <td><strong>Fase 3</strong></td>
                <td>Personalizacion con variantes reales</td>
                <td>12/12 off-targets personalizados en 3 cromosomas</td>
                <td><span class="badge badge-low">Completada</span></td>
            </tr>
            <tr>
                <td><strong>Fase 4</strong></td>
                <td>ARNm terapeutico con validacion</td>
                <td>Score global: {mrna_data.get("score_global",0)}/100</td>
                <td><span class="badge badge-low">Completada</span></td>
            </tr>
            <tr>
                <td><strong>Fase 5</strong></td>
                <td>Dashboard + reportes clinicos</td>
                <td>Este documento</td>
                <td><span class="badge badge-low">Completada</span></td>
            </tr>
        </table>
    </div>

    <div class="card">
        <h2>Resultados por Paciente</h2>
        <table>
            <tr>
                <th>Paciente</th><th>Poblacion</th>
                <th>Mejor Guia HBB</th><th>Score</th>
                <th>Mejor Guia BCL</th><th>Score</th>
                <th>ARNm</th>
            </tr>'''

    for muestra in sorted(pacientes.keys()):
        pac = pacientes[muestra]
        pob = pac.get("info_clinica", {}).get("poblacion_nombre", "?")
        perfil = perfiles.get(muestra, {})

        mejor_hbb, sc_hbb = "N/A", 0
        mejor_bcl, sc_bcl = "N/A", 0
        for gid, ginfo in perfil.get("guias", {}).items():
            sc = ginfo.get("resumen", {}).get("score_personalizado", 0)
            if gid.startswith("HBB") and sc > sc_hbb:
                sc_hbb = sc
                mejor_hbb = gid
            elif gid.startswith("BCL") and sc > sc_bcl:
                sc_bcl = sc
                mejor_bcl = gid

        body += f'''
            <tr>
                <td><strong><a href="reporte_clinico_{muestra}.html" style="color:{COL_PRIMARY}">{muestra}</a></strong></td>
                <td>{pob}</td>
                <td>{mejor_hbb}</td>
                <td><strong class="{score_class(sc_hbb)}">{sc_hbb}</strong></td>
                <td>{mejor_bcl}</td>
                <td><strong class="{score_class(sc_bcl)}">{sc_bcl}</strong></td>
                <td><strong class="{score_class(mrna_data.get('score_global',0))}">{mrna_data.get("score_global",0)}</strong></td>
            </tr>'''

    body += '''</table>
    </div>

    <div class="card">
        <h2>Diferenciador Clave: Personalizacion</h2>
        <div class="two-col">
            <div>
                <h3>Lo que existe hoy</h3>
                <ul style="padding-left:20px;color:#5f6368">
                    <li>CRISPRscan, Benchling: disenan guias con genoma de REFERENCIA</li>
                    <li>Cas-OFFinder: busca off-targets sin personalizar</li>
                    <li>Casgevy (Vertex): UNA guia para TODOS los pacientes</li>
                </ul>
            </div>
            <div>
                <h3>Lo que hace Exonik</h3>
                <ul style="padding-left:20px;color:#202124">
                    <li><strong>Toma variantes REALES</strong> del paciente</li>
                    <li><strong>Cruza</strong> off-targets con SNPs individuales</li>
                    <li><strong>Recomienda</strong> la guia mas segura para ESE paciente</li>
                    <li><strong>Diseña</strong> ARNm complementario optimizado</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="disclaimer">
        <strong>AVISO:</strong> Prototipo computacional con fines educativos y de investigacion.
        No constituye consejo medico. Requiere validacion experimental. Exonik v0.1.0 (Research Use Only).
    </div>
    '''

    return wrap_html("Resumen Ejecutivo - Exonik", body, nav)


# =============================================================================
# SECUENCIAS PARA LABORATORIO
# =============================================================================

def generar_secuencias_lab(datos):
    """Genera archivo de texto con secuencias listas para sintesis."""
    blast = datos.get("blast", {})
    mrna_data = datos.get("mrna", {})

    lines = []
    lines.append("=" * 70)
    lines.append("  EXONIK - SECUENCIAS PARA LABORATORIO")
    lines.append("  Formato listo para sintesis / orden")
    lines.append("=" * 70)
    lines.append(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"  SOLO PARA INVESTIGACION (Research Use Only)")
    lines.append("=" * 70)

    # --- Guias CRISPR ---
    lines.append("\n\n" + "=" * 70)
    lines.append("  SECCION 1: GUIAS CRISPR (formato sgRNA)")
    lines.append("=" * 70)

    for gid in sorted(blast.get("resultados", {}).keys(), key=lambda x: (0 if x.startswith("HBB") else 1, x)):
        g = blast["resultados"][gid]
        seq = g["secuencia"]
        pam = g["pam"]
        est = g.get("estrategia", "")
        sc = g["resumen_seguridad"]["score_seguridad"]
        lines.append(f"\n  > {gid} | PAM: {pam} | {est} | Score: {sc}/100")
        # ADN
        lines.append(f"  DNA (para sintesis): 5'-{seq}-3'")
        # ARN guia
        rna_seq = seq.replace("T", "U")
        lines.append(f"  RNA (sgRNA):         5'-{rna_seq}-3'")

    # --- ARNm terapeutico ---
    lines.append("\n\n" + "=" * 70)
    lines.append("  SECCION 2: ARNm TERAPEUTICO (HBB normal)")
    lines.append("=" * 70)

    mrna_seq = mrna_data.get("mrna", {}).get("secuencia_completa", "")
    if mrna_seq:
        lines.append(f"\n  Longitud: {len(mrna_seq)} nt")
        lines.append(f"  Cap: {mrna_data.get('mrna',{}).get('cap','?')}")
        lines.append(f"  Modificacion: {mrna_data.get('mrna',{}).get('modificacion','?')}")
        lines.append(f"  Score global: {mrna_data.get('score_global',0)}/100\n")

        # CDS solo
        cds = mrna_data.get("optimizacion", {}).get("estrategias", {}).get(
            mrna_data.get("optimizacion", {}).get("mejor_estrategia", ""), {}
        ).get("cds", "")
        if cds:
            lines.append(f"  CDS optimizado (444 nt, para clonacion):")
            # Formato FASTA-like
            for i in range(0, len(cds), 60):
                lines.append(f"  {cds[i:i+60]}")

        lines.append(f"\n  ARNm completo (595 nt, para sintesis IVT):")
        for i in range(0, len(mrna_seq), 60):
            lines.append(f"  {mrna_seq[i:i+60]}")

    # --- Guias recomendadas por paciente ---
    lines.append("\n\n" + "=" * 70)
    lines.append("  SECCION 3: RECOMENDACIONES POR PACIENTE")
    lines.append("=" * 70)

    personal = datos.get("personalizacion", {})
    perfiles = personal.get("perfiles", {})
    pacientes = datos.get("pacientes", {})

    for muestra in sorted(pacientes.keys()):
        pac = pacientes[muestra]
        pob = pac.get("info_clinica", {}).get("poblacion_nombre", "?")
        perfil = perfiles.get(muestra, {})

        mejor_hbb, sc_hbb = "N/A", 0
        for gid, ginfo in perfil.get("guias", {}).items():
            if gid.startswith("HBB"):
                sc = ginfo.get("resumen", {}).get("score_personalizado", 0)
                if sc > sc_hbb:
                    sc_hbb = sc
                    mejor_hbb = gid

        lines.append(f"\n  {muestra} ({pob})")
        lines.append(f"    Guia HBB: {mejor_hbb} (Score: {sc_hbb}/100)")
        if mejor_hbb != "N/A" and mejor_hbb in blast.get("resultados", {}):
            seq = blast["resultados"][mejor_hbb]["secuencia"]
            lines.append(f"    sgRNA:    5'-{seq.replace('T','U')}-3'")

    lines.append("\n\n" + "=" * 70)
    lines.append("  FIN DEL DOCUMENTO")
    lines.append("  SOLO PARA INVESTIGACION - NO PARA USO CLINICO")
    lines.append("=" * 70)

    return "\n".join(lines)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("  EXONIK - FASE 5: REPORTE INTEGRADO + DASHBOARD")
    print("=" * 60)

    # Crear directorio de salida
    os.makedirs(DIR_SALIDA, exist_ok=True)

    # --- 1. Cargar datos ---
    print("\n  Cargando datos de Fases 1-4...")
    datos = cargar_datos()

    # Verificar que tenemos datos
    if not datos["pacientes"]:
        print("\n  [ERROR] No se encontraron pacientes. Ejecuta Fase 1 primero.")
        sys.exit(1)

    # --- 2. Generar graficos ---
    print("\n  Generando graficos interactivos...")
    try:
        graficos = generar_graficos(datos)
        print(f"        {len(graficos)} graficos generados")
    except ImportError:
        print("  [!] plotly no instalado. Instalalo con: pip install plotly")
        print("      Generando reportes sin graficos...")
        graficos = {}

    # --- 3. Generar dashboard ---
    print("\n  Generando dashboard principal...")
    dashboard_html = generar_dashboard(datos, graficos)
    dashboard_path = os.path.join(DIR_SALIDA, "dashboard_exonik.html")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    print(f"        -> {dashboard_path}")

    # --- 4. Generar reportes clinicos ---
    print("\n  Generando reportes clinicos por paciente...")
    for muestra in sorted(datos["pacientes"].keys()):
        reporte_html = generar_reporte_clinico(muestra, datos)
        reporte_path = os.path.join(DIR_SALIDA, f"reporte_clinico_{muestra}.html")
        with open(reporte_path, "w", encoding="utf-8") as f:
            f.write(reporte_html)
        print(f"        -> reporte_clinico_{muestra}.html")

    # --- 5. Generar resumen ejecutivo ---
    print("\n  Generando resumen ejecutivo...")
    resumen_html = generar_resumen_ejecutivo(datos)
    resumen_path = os.path.join(DIR_SALIDA, "resumen_ejecutivo.html")
    with open(resumen_path, "w", encoding="utf-8") as f:
        f.write(resumen_html)
    print(f"        -> {resumen_path}")

    # --- 6. Generar secuencias para laboratorio ---
    print("\n  Exportando secuencias para laboratorio...")
    lab_text = generar_secuencias_lab(datos)
    lab_path = os.path.join(DIR_SALIDA, "secuencias_laboratorio.txt")
    with open(lab_path, "w", encoding="utf-8") as f:
        f.write(lab_text)
    print(f"        -> {lab_path}")

    # --- Resumen final ---
    n_archivos = 2 + len(datos["pacientes"]) + 2  # dashboard + resumen + reportes + lab
    print("\n" + "=" * 60)
    print(f"  FASE 5 COMPLETADA")
    print(f"  {n_archivos} archivos generados en: reporte_integrado/")
    print("=" * 60)
    print(f"\n  Para ver el dashboard, abre en tu navegador:")
    print(f"  {dashboard_path}")
    print()


if __name__ == "__main__":
    main()

