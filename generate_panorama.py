import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import re
import html
import unicodedata
from pathlib import Path
from collections import Counter, defaultdict

# Load catalog data
local_json = Path(__file__).parent / "catalog_defesas.json"
brain_json = Path(r"C:\Users\Casa\.gemini\antigravity\brain\6738a72b-0664-43b4-b7b5-77b8a9c32ac0\scratch\catalog_defesas.json")

if local_json.exists():
    json_path = local_json
elif brain_json.exists():
    json_path = brain_json
else:
    raise FileNotFoundError("catalog_defesas.json not found in repository or brain cache.")

catalog = json.load(open(json_path, encoding="utf-8"))

def norm(s):
    if not s:
        return ""
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def clean_and_capitalize_abstract(res):
    if not res:
        return ""
    res = res.strip()
    
    # Strip leading metadata if present
    m = re.search(r'\b(20[12]\d)\s+(?:disserta[çc][ãa]o|tese)\s+(.*)', res, flags=re.IGNORECASE | re.DOTALL)
    if m:
        rem = m.group(2).strip()
    else:
        m2 = re.search(r'\b\d{2}/\d{2}/(20[12]\d)\s+(.*)', res, flags=re.IGNORECASE | re.DOTALL)
        if m2:
            rem = m2.group(2).strip()
            rem = re.sub(r'^(?:20[12]\d\s+)?(?:disserta[çc][ãa]o|tese)\s+', '', rem, flags=re.IGNORECASE).strip()
        else:
            rem = res

    if not rem:
        return ""

    # Capitalize first character
    rem = rem[0].upper() + rem[1:]

    # Capitalize after periods, exclamation marks, question marks
    def cap_after_punct(match):
        punct = match.group(1)
        space = match.group(2)
        char = match.group(3)
        return f"{punct}{space}{char.upper()}"
        
    rem = re.sub(r'([.!?])(\s+)([a-záàâãéèêíïóôõúüç])', cap_after_punct, rem)

    # Standard academic and institutional acronyms
    acronyms = [
        r'\bppges\b', r'\bufsb\b', r'\bcnj\b', r'\btjba\b', r'\bsuas\b', r'\bcras\b',
        r'\bcreas\b', r'\bsus\b', r'\badi\b', r'\bcejusc\b', r'\bcejuscs\b',
        r'\bcapes\b', r'\bcnpq\b', r'\bcfchs\b', r'\bproppg\b', r'\boab\b',
        r'\brasp\b', r'\bclt\b', r'\bstf\b', r'\bstj\b', r'\bufba\b', r'\bunesp\b',
        r'\busp\b', r'\bufmg\b', r'\bufrj\b', r'\bunb\b', r'\bmec\b', r'\bpnaes\b',
        r'\bpnae\b', r'\bifba\b', r'\blgbt\b', r'\blgbtqia\+?\b', r'\bcpi\b'
    ]
    for acr in acronyms:
        rem = re.sub(acr, lambda m: m.group(0).upper(), rem, flags=re.IGNORECASE)

    # Regional place names and proper nouns
    proper_nouns = [
        (r'\bporto seguro\b', 'Porto Seguro'),
        (r'\beun[aá]polis\b', 'Eunápolis'),
        (r'\bteixeira de freitas\b', 'Teixeira de Freitas'),
        (r'\bitamaraju\b', 'Itamaraju'),
        (r'\bilh[eé]us\b', 'Ilhéus'),
        (r'\bsanta cruz cabr[aá]lia\b', 'Santa Cruz Cabrália'),
        (r'\bcoroa vermelha\b', 'Coroa Vermelha'),
        (r'\bmonte pascoal\b', 'Monte Pascoal'),
        (r'\bvale verde\b', 'Vale Verde'),
        (r'\bextremo sul baiano\b', 'Extremo Sul Baiano'),
        (r'\bextremo sul\b', 'Extremo Sul'),
        (r'\bsul da bahia\b', 'Sul da Bahia'),
        (r'\bbahia\b', 'Bahia'),
        (r'\bbrasil\b', 'Brasil'),
        (r'\bpatax[oó]\b', 'Pataxó'),
        (r'\btupinamb[aá]\b', 'Tupinambá'),
    ]
    for pat, rep in proper_nouns:
        rem = re.sub(pat, rep, rem, flags=re.IGNORECASE)

    return rem

for d in catalog:
    d['orientador_clean'] = d.get('orientador', '').replace("Texto Integral", "").strip()
    d['clean_resumo'] = clean_and_capitalize_abstract(d.get('resumo', ''))

by_year = defaultdict(list)
for d in catalog:
    by_year[d['ano']].append(d)

advisor_counts = Counter(d['orientador_clean'] for d in catalog)

# Verify statistics
stats_by_year = {}
for y in sorted(by_year.keys(), reverse=True):
    items = by_year[y]
    m_count = sum(1 for it in items if 'mestrado' in it['nivel'].lower())
    t_count = sum(1 for it in items if 'doutorado' in it['nivel'].lower())
    pdf_count = sum(1 for it in items if bool(it.get('link_pdf') and it['link_pdf'].strip()))
    stats_by_year[y] = {
        'mestrado': m_count,
        'doutorado': t_count,
        'total': len(items),
        'pdf': pdf_count
    }

# Build HTML
out = []

out.append("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panorama de Dissertações e Teses: PPGES (UFSB) | 2019-2026</title>
    <meta name="description" content="Panorama interativo das 151 dissertações e teses defendidas no Programa de Pós-Graduação em Estado e Sociedade (PPGES/UFSB), com análise de aderência jurídica, currículos Lattes dos docentes e diretrizes para anteprojeto.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-page: #FBF9F5;
            --bg-card: #FFFFFF;
            --bg-card-subtle: #F6F3EC;
            --bg-highlight: #F0ECE1;
            
            --text-main: #23262B;
            --text-secondary: #585E6A;
            --text-muted: #7A808C;
            
            --accent-navy: #1B365D;
            --accent-navy-light: #2C5282;
            --accent-wine: #782635;
            --accent-wine-light: #9B3245;
            --accent-gold: #966E36;
            --accent-green: #295743;
            --accent-green-light: #3D7A5E;
            
            --border-light: #E7E2D8;
            --border-medium: #D5CEBF;
            --border-dark: #A39B8B;
            
            --font-serif-title: 'Lora', 'Georgia', serif;
            --font-serif-body: 'Source Serif 4', 'Charter', 'Georgia', serif;
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            
            --measure: 890px;
        }

        html {
            scroll-behavior: smooth;
        }

        @media (prefers-reduced-motion: reduce) {
            html {
                scroll-behavior: auto;
            }
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-page);
            color: var(--text-main);
            font-family: var(--font-serif-body);
            font-size: 16.5px;
            line-height: 1.72;
            padding: 30px 16px 60px 16px;
            -webkit-font-smoothing: antialiased;
        }

        .skip-link {
            position: absolute;
            top: -50px;
            left: 20px;
            background: var(--accent-navy);
            color: #FFFFFF;
            padding: 8px 16px;
            font-family: var(--font-sans);
            font-size: 14px;
            font-weight: 600;
            z-index: 9999;
            border-radius: 0 0 4px 4px;
            transition: top 0.2s ease;
            text-decoration: none;
        }

        .skip-link:focus {
            top: 0;
            outline: 3px solid var(--accent-wine);
        }

        .page-container {
            max-width: var(--measure);
            margin: 0 auto;
            background: var(--bg-card);
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            padding: 48px 56px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        }

        @media (max-width: 768px) {
            body { padding: 12px 6px 40px 6px; }
            .page-container { padding: 28px 18px; }
        }

        .institutional-header {
            border-bottom: 2px solid var(--border-medium);
            padding-bottom: 24px;
            margin-bottom: 34px;
            text-align: center;
        }

        .inst-sub {
            font-family: var(--font-sans);
            font-size: 12px;
            letter-spacing: 1.6px;
            text-transform: uppercase;
            color: var(--accent-wine);
            font-weight: 700;
            margin-bottom: 4px;
        }

        .inst-name {
            font-family: var(--font-sans);
            font-size: 14px;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 12px;
        }

        .main-title {
            font-family: var(--font-serif-title);
            font-size: 30px;
            font-weight: 700;
            color: var(--accent-navy);
            line-height: 1.25;
            margin-bottom: 8px;
        }

        @media (max-width: 600px) {
            .main-title { font-size: 24px; }
        }

        .main-subtitle {
            font-family: var(--font-sans);
            font-size: 17px;
            color: var(--text-secondary);
            font-weight: 500;
            margin-bottom: 16px;
        }

        .doc-meta-row {
            display: flex;
            justify-content: center;
            gap: 16px;
            font-family: var(--font-sans);
            font-size: 12.5px;
            color: var(--text-muted);
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .doc-meta-badge {
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-light);
            padding: 4px 10px;
            border-radius: 4px;
        }

        .intro-box {
            background: var(--bg-card-subtle);
            border-left: 4px solid var(--accent-navy);
            padding: 22px 26px;
            margin-bottom: 38px;
            border-radius: 0 4px 4px 0;
        }

        .intro-box h3 {
            font-family: var(--font-sans);
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--accent-navy);
            margin-bottom: 8px;
            font-weight: 700;
        }

        .intro-box p {
            margin-bottom: 10px;
            font-size: 16px;
            line-height: 1.65;
            color: var(--text-main);
        }

        .intro-box p:last-child {
            margin-bottom: 0;
        }

        /* Quick Actions Bar */
        .quick-actions-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 34px;
            padding: 16px;
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-medium);
            border-radius: 4px;
        }

        @media (max-width: 820px) {
            .quick-actions-bar {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 480px) {
            .quick-actions-bar {
                grid-template-columns: 1fr;
            }
        }

        .quick-action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 12px 14px;
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            color: var(--accent-navy);
            text-decoration: none;
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: 700;
            text-align: center;
            line-height: 1.35;
            transition: all 0.15s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }

        .quick-action-btn:hover {
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(0,0,0,0.08);
            text-decoration: none;
        }

        .quick-action-btn:focus,
        .quick-action-btn:focus-visible {
            outline: 2px solid var(--accent-wine);
            outline-offset: 2px;
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
            text-decoration: none;
        }

        .quick-action-btn .btn-subtitle {
            display: block;
            font-size: 11px;
            font-weight: 500;
            color: var(--text-muted);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .quick-action-btn:hover .btn-subtitle,
        .quick-action-btn:focus .btn-subtitle,
        .quick-action-btn:focus-visible .btn-subtitle {
            color: #E2E8F0;
        }

        /* Cronograma e Prazos do Edital */
        .cronograma-alert {
            background: #FDF7F8;
            border: 1px solid #E8C1C6;
            border-left: 4px solid var(--accent-wine);
            border-radius: 0 4px 4px 0;
            padding: 18px 22px;
            margin-bottom: 24px;
        }

        .cronograma-alert-title {
            font-family: var(--font-sans);
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--accent-wine);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .cronograma-alert-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-top: 12px;
        }

        @media (max-width: 720px) {
            .cronograma-alert-grid {
                grid-template-columns: 1fr;
            }
        }

        .cronograma-alert-item {
            background: #FFFFFF;
            border: 1px solid #E8D3D6;
            border-radius: 4px;
            padding: 12px 14px;
        }

        .cronograma-alert-label {
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--accent-wine);
            margin-bottom: 4px;
            display: block;
        }

        .cronograma-alert-val {
            font-family: var(--font-sans);
            font-size: 14px;
            font-weight: 700;
            color: var(--text-main);
            display: block;
            line-height: 1.35;
        }

        .cronograma-alert-detail {
            font-family: var(--font-sans);
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 4px;
            line-height: 1.4;
            display: block;
        }

        /* Timeline Flow */
        .timeline-steps {
            display: flex;
            flex-direction: column;
            gap: 14px;
            margin: 24px 0;
        }

        .timeline-step-card {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            padding: 16px 20px;
            display: grid;
            grid-template-columns: 130px 1fr auto;
            gap: 16px;
            align-items: center;
            transition: border-color 0.15s ease;
        }

        .timeline-step-card:hover {
            border-color: var(--accent-navy);
        }

        @media (max-width: 680px) {
            .timeline-step-card {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            .step-badge-col {
                text-align: left;
            }
            .step-meta-col {
                text-align: left;
            }
        }

        .step-badge-col {
            text-align: center;
        }

        .step-number {
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--accent-wine);
            display: block;
        }

        .step-date-badge {
            font-family: var(--font-sans);
            font-size: 13.5px;
            font-weight: 700;
            color: var(--accent-navy);
            display: block;
            margin-top: 2px;
            line-height: 1.25;
        }

        .step-info-col h4 {
            font-family: var(--font-serif-title);
            font-size: 16px;
            font-weight: 700;
            color: var(--accent-navy);
            margin-bottom: 4px;
        }

        .step-info-col p {
            font-family: var(--font-sans);
            font-size: 13px;
            color: var(--text-secondary);
            margin: 0;
            line-height: 1.5;
        }

        .step-meta-col {
            text-align: right;
            min-width: 140px;
        }

        @media (max-width: 680px) {
            .step-meta-col {
                text-align: left;
            }
        }

        .step-weight-badge {
            display: inline-block;
            font-family: var(--font-sans);
            font-size: 12px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 3px;
            background: #EBF1F8;
            color: var(--accent-navy);
            border: 1px solid #CDDCED;
        }

        .step-nature-text {
            display: block;
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .formula-card {
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-medium);
            border-left: 4px solid var(--accent-navy);
            padding: 16px 20px;
            border-radius: 0 4px 4px 0;
            margin-top: 20px;
            font-family: var(--font-sans);
            font-size: 13.5px;
        }

        .formula-card strong {
            color: var(--accent-navy);
        }

        .formula-code {
            display: block;
            background: #FFFFFF;
            border: 1px solid var(--border-light);
            border-radius: 3px;
            padding: 8px 12px;
            font-family: monospace;
            font-size: 13px;
            color: var(--accent-navy);
            margin: 8px 0;
            font-weight: 600;
        }

        /* Compliance Checklist */
        .compliance-checklist-card {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            padding: 24px;
            margin: 28px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }

        @media (max-width: 600px) {
            .compliance-checklist-card {
                padding: 16px 14px;
            }
        }

        .compliance-checklist-header {
            border-bottom: 2px solid var(--accent-wine);
            padding-bottom: 10px;
            margin-bottom: 18px;
        }

        .compliance-checklist-header h3 {
            font-family: var(--font-serif-title);
            font-size: 18px;
            font-weight: 700;
            color: var(--accent-wine);
            margin-bottom: 4px;
        }

        .compliance-checklist-header p {
            font-family: var(--font-sans);
            font-size: 13.5px;
            color: var(--text-secondary);
            margin: 0;
        }

        .checklist-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }

        .checklist-item {
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-light);
            border-radius: 4px;
            padding: 12px 16px;
            display: flex;
            align-items: flex-start;
            gap: 14px;
            cursor: pointer;
            user-select: none;
            transition: all 0.15s ease;
        }

        .checklist-item:hover {
            border-color: var(--accent-navy);
            background: #FFFFFF;
        }

        .checklist-item:focus,
        .checklist-item:focus-visible {
            outline: 2px solid var(--accent-wine);
            outline-offset: 2px;
        }

        .checklist-item.checked {
            background: #F4FBF6;
            border-color: #A3D9B5;
        }

        .checklist-item.checked .checklist-indicator {
            background: #1E6B39;
            border-color: #1E6B39;
            color: #FFFFFF;
        }

        .checklist-indicator {
            flex-shrink: 0;
            width: 22px;
            height: 22px;
            border-radius: 3px;
            background: #FFFFFF;
            border: 2px solid var(--accent-navy);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 2px;
            color: var(--accent-navy);
        }

        .checklist-body {
            flex-grow: 1;
        }

        .checklist-item-title {
            font-family: var(--font-sans);
            font-size: 14px;
            font-weight: 700;
            color: var(--accent-navy);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 4px;
        }

        .checklist-tag {
            font-family: var(--font-sans);
            font-size: 10.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            padding: 2px 6px;
            border-radius: 3px;
            background: #FDF3E7;
            color: #92540D;
            border: 1px solid #F5D3A6;
        }

        .checklist-tag.danger {
            background: #FDF4F5;
            color: var(--accent-wine);
            border-color: #E8C1C6;
        }

        .checklist-tag.success {
            background: #EEF8F1;
            color: #1E6B39;
            border-color: #C4E6CD;
        }

        .checklist-desc {
            font-family: var(--font-sans);
            font-size: 13px;
            color: var(--text-main);
            line-height: 1.5;
            margin: 0;
        }

        .toc-box {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            padding: 22px 26px;
            margin-bottom: 44px;
        }

        .toc-title {
            font-family: var(--font-sans);
            font-size: 13.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-wine);
            margin-bottom: 14px;
            border-bottom: 1px solid var(--border-light);
            padding-bottom: 8px;
        }

        .toc-list {
            list-style: none;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px 24px;
        }

        @media (max-width: 650px) {
            .toc-list { grid-template-columns: 1fr; }
        }

        .toc-list li a {
            font-family: var(--font-sans);
            font-size: 14px;
            color: var(--accent-navy);
            text-decoration: none;
            font-weight: 600;
            transition: color 0.15s ease;
            display: inline-block;
        }

        .toc-list li a:hover {
            color: var(--accent-wine);
            text-decoration: underline;
        }

        /* Section layout */
        .section-block {
            margin-bottom: 48px;
            scroll-margin-top: 24px;
        }

        .section-header {
            border-bottom: 2px solid var(--accent-navy);
            padding-bottom: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
        }

        .section-tag {
            font-family: var(--font-sans);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--accent-wine);
            font-weight: 700;
        }

        .section-title {
            font-family: var(--font-serif-title);
            font-size: 23px;
            color: var(--accent-navy);
            font-weight: 700;
            flex-grow: 1;
            margin-left: 12px;
        }

        @media (max-width: 600px) {
            .section-title {
                margin-left: 0;
                font-size: 20px;
                width: 100%;
            }
        }

        p {
            margin-bottom: 16px;
        }

        /* Tables */
        .table-responsive {
            overflow-x: auto;
            margin: 24px 0;
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            -webkit-overflow-scrolling: touch;
        }

        .academic-table {
            width: 100%;
            border-collapse: collapse;
            font-family: var(--font-sans);
            font-size: 13.5px;
            background: #FFFFFF;
        }

        .academic-table th {
            background-color: var(--bg-card-subtle);
            color: var(--accent-navy);
            font-weight: 700;
            text-align: left;
            padding: 12px 14px;
            border-bottom: 2px solid var(--border-medium);
            font-size: 13px;
        }

        .academic-table th.center, .academic-table td.center {
            text-align: center;
        }

        .academic-table td {
            padding: 11px 14px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-main);
            vertical-align: top;
        }

        .academic-table tbody tr:hover {
            background-color: var(--bg-page);
        }

        .academic-table tfoot td {
            background-color: var(--bg-card-subtle);
            font-weight: 700;
            border-top: 2px solid var(--border-medium);
            border-bottom: none;
        }

        /* Policy Cards */
        .policy-card {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-left: 4px solid var(--accent-navy);
            border-radius: 0 4px 4px 0;
            padding: 18px 22px;
            margin-bottom: 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }

        .policy-card.wine-accent { border-left-color: var(--accent-wine); }
        .policy-card.gold-accent { border-left-color: var(--accent-gold); }
        .policy-card.green-accent { border-left-color: var(--accent-green); }

        .policy-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 6px;
            flex-wrap: wrap;
            gap: 8px;
        }

        .policy-name {
            font-family: var(--font-sans);
            font-size: 16px;
            font-weight: 700;
            color: var(--accent-navy);
        }

        .policy-card.wine-accent .policy-name { color: var(--accent-wine); }
        .policy-card.gold-accent .policy-name { color: var(--accent-gold); }
        .policy-card.green-accent .policy-name { color: var(--accent-green); }

        .policy-count-tag {
            font-family: var(--font-sans);
            font-size: 11.5px;
            color: var(--text-muted);
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-light);
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: 600;
        }

        .policy-body {
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 12px;
            line-height: 1.6;
        }

        .policy-examples {
            font-family: var(--font-sans);
            font-size: 13px;
            background: var(--bg-card-subtle);
            padding: 12px 14px;
            border-radius: 3px;
            border: 1px solid var(--border-light);
        }

        .policy-examples strong {
            display: block;
            margin-bottom: 6px;
            color: var(--text-main);
            font-size: 12.5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .policy-examples ul {
            list-style: none;
            padding-left: 0;
        }

        .policy-examples li {
            margin-bottom: 6px;
            padding-left: 14px;
            position: relative;
            line-height: 1.55;
        }

        .policy-examples li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: var(--accent-wine);
            font-weight: bold;
        }

        .policy-examples a {
            color: var(--accent-navy);
            text-decoration: underline;
            font-weight: 600;
            margin-left: 4px;
        }

        /* Faculty Cards */
        .faculty-subheading {
            font-family: var(--font-sans);
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--accent-wine);
            font-weight: 700;
            margin: 26px 0 14px 0;
            border-bottom: 1px solid var(--border-light);
            padding-bottom: 6px;
        }

        .faculty-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
            margin-bottom: 24px;
        }

        @media (max-width: 820px) {
            .faculty-grid { grid-template-columns: 1fr; }
        }

        .faculty-card {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .faculty-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        .faculty-card.law-focus {
            border-top: 4px solid var(--accent-navy);
        }

        .faculty-header-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 6px;
        }

        .faculty-name {
            font-family: var(--font-sans);
            font-size: 16px;
            font-weight: 700;
            color: var(--accent-navy);
            line-height: 1.35;
        }

        .faculty-badge {
            display: inline-block;
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            padding: 3px 8px;
            border-radius: 3px;
            background: #EBF1F8;
            color: var(--accent-navy);
            margin-bottom: 8px;
        }

        .faculty-vagas-badge {
            display: inline-block;
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 3px;
            background: #FDF3E7;
            color: #92540D;
            border: 1px solid #F5D3A6;
            margin-bottom: 10px;
        }

        .faculty-cohort-badge {
            display: inline-block;
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 3px;
            background: #EEF8F1;
            color: #1E6B39;
            border: 1px solid #C4E6CD;
            margin-bottom: 10px;
        }

        .faculty-training {
            font-family: var(--font-sans);
            font-size: 12.5px;
            color: var(--text-secondary);
            margin-bottom: 8px;
            line-height: 1.45;
        }

        .faculty-desc {
            font-size: 14px;
            color: var(--text-main);
            margin-bottom: 12px;
            line-height: 1.6;
        }

        .faculty-tip-box {
            background: #FAF7F0;
            border-left: 3px solid var(--accent-gold);
            padding: 8px 12px;
            margin-bottom: 14px;
            font-size: 13px;
            font-family: var(--font-sans);
            color: #4A3E2C;
            line-height: 1.5;
        }

        .faculty-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border-light);
        }

        .faculty-lattes-btn {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-medium);
            padding: 5px 10px;
            font-family: var(--font-sans);
            font-size: 12px;
            font-weight: 600;
            color: var(--accent-navy);
            text-decoration: none;
            border-radius: 3px;
            transition: all 0.15s ease;
        }

        .faculty-lattes-btn:hover {
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
        }

        .faculty-filter-btn {
            background: transparent;
            border: 1px solid var(--border-medium);
            padding: 5px 10px;
            font-family: var(--font-sans);
            font-size: 12px;
            font-weight: 600;
            color: var(--accent-wine);
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .faculty-filter-btn:hover {
            background: var(--accent-wine);
            color: #FFFFFF;
            border-color: var(--accent-wine);
        }

        .faculty-meta {
            font-family: var(--font-sans);
            font-size: 11.5px;
            color: var(--text-muted);
            margin-top: 6px;
        }

        /* Housing Proposal Buttons in Faculty Card */
        .faculty-housing-proposals-box {
            background: #F8F5EE;
            border: 1px solid var(--border-medium);
            border-left: 3px solid var(--accent-wine);
            border-radius: 4px;
            padding: 8px 10px;
            margin-top: 10px;
        }

        .faculty-housing-label {
            display: block;
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--accent-wine);
            margin-bottom: 6px;
        }

        .faculty-housing-btns {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .faculty-prop-btn {
            display: inline-flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 3px;
            padding: 6px 10px;
            font-family: var(--font-sans);
            font-size: 11.5px;
            font-weight: 600;
            color: var(--accent-navy);
            cursor: pointer;
            text-align: left;
            transition: all 0.15s ease;
            text-decoration: none;
        }

        .faculty-prop-btn:hover {
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
        }

        /* Housing Proposals Section */
        .housing-proposals-container {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 6px;
            padding: 24px;
            margin: 28px 0;
            box-shadow: 0 3px 12px rgba(0,0,0,0.03);
        }

        .housing-header {
            margin-bottom: 18px;
            border-bottom: 1px solid var(--border-light);
            padding-bottom: 14px;
        }

        .housing-tag {
            display: inline-block;
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            padding: 3px 8px;
            border-radius: 3px;
            background: #FDF3E7;
            color: #92540D;
            border: 1px solid #F5D3A6;
            margin-bottom: 8px;
        }

        .housing-title {
            font-family: var(--font-serif);
            font-size: 20px;
            color: var(--accent-navy);
            margin: 4px 0 8px 0;
            line-height: 1.35;
        }

        .housing-subtitle {
            font-size: 13.5px;
            color: var(--text-secondary);
            line-height: 1.55;
            margin: 0;
        }

        .housing-tabs-bar {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }

        @media (max-width: 820px) {
            .housing-tabs-bar {
                grid-template-columns: 1fr;
            }
        }

        .housing-tab-btn {
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            padding: 12px 14px;
            text-align: left;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .housing-tab-btn:hover {
            border-color: var(--accent-navy);
            background: #F0EDE4;
        }

        .housing-tab-btn.active {
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
            box-shadow: 0 2px 6px rgba(27, 54, 93, 0.25);
        }

        .housing-tab-btn .tab-num {
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--accent-wine);
        }

        .housing-tab-btn.active .tab-num {
            color: var(--accent-gold);
        }

        .housing-tab-btn .tab-label {
            font-family: var(--font-serif);
            font-size: 13.5px;
            font-weight: 600;
            line-height: 1.3;
            color: var(--accent-navy);
        }

        .housing-tab-btn.active .tab-label {
            color: #FFFFFF;
        }

        .housing-option-panel {
            background: #FAFAF7;
            border: 1px solid var(--border-light);
            border-left: 4px solid var(--accent-wine);
            border-radius: 4px;
            padding: 22px;
        }

        .option-badge-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }

        .option-meta-badge {
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 3px;
            background: #EBF1F8;
            color: var(--accent-navy);
        }

        .option-meta-badge.gold {
            background: #FDF3E7;
            color: #92540D;
        }

        .option-meta-badge.wine {
            background: #F9EBF5;
            color: var(--accent-wine);
        }

        .option-title-text {
            font-family: var(--font-serif);
            font-size: 18px;
            font-weight: 700;
            color: var(--accent-navy);
            margin: 0 0 16px 0;
            line-height: 1.4;
        }

        .option-grid-fields {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }

        @media (max-width: 820px) {
            .option-grid-fields {
                grid-template-columns: 1fr;
            }
        }

        .option-field {
            background: #FFFFFF;
            border: 1px solid var(--border-light);
            border-radius: 4px;
            padding: 12px 14px;
        }

        .option-field.full-width {
            grid-column: 1 / -1;
        }

        .option-field-label {
            display: block;
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--accent-wine);
            margin-bottom: 6px;
        }

        .option-field-content {
            font-size: 13.5px;
            line-height: 1.6;
            color: var(--text-main);
            margin: 0;
        }

        .option-copy-btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--accent-navy);
            color: #FFFFFF;
            border: 1px solid var(--accent-navy);
            border-radius: 4px;
            padding: 9px 16px;
            font-family: var(--font-sans);
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 10px;
        }

        .option-copy-btn:hover {
            background: #12243F;
            border-color: #12243F;
        }

        /* Catalog Search and Filter Controls */
        .catalog-controls {
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-medium);
            border-radius: 5px;
            padding: 22px 24px;
            margin: 28px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }

        .search-row {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            position: relative;
        }

        .search-input {
            flex-grow: 1;
            padding: 10px 14px;
            font-family: var(--font-sans);
            font-size: 15px;
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            background: #FFFFFF;
            color: var(--text-main);
            outline: none;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }

        .search-input:focus {
            border-color: var(--accent-navy);
            box-shadow: 0 0 0 3px rgba(27, 54, 93, 0.12);
        }

        .search-clear-btn {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            font-size: 16px;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px 8px;
            display: none;
        }

        .search-clear-btn:hover {
            color: var(--accent-wine);
        }

        .filter-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
            margin-bottom: 12px;
        }

        .filter-group-label {
            font-family: var(--font-sans);
            font-size: 12.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-secondary);
            min-width: 80px;
        }

        .filter-buttons {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .filter-btn {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            padding: 6px 12px;
            font-family: var(--font-sans);
            font-size: 12.5px;
            font-weight: 600;
            color: var(--text-secondary);
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .filter-btn:hover {
            border-color: var(--accent-navy);
            color: var(--accent-navy);
        }

        .filter-btn.active {
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
        }

        .filter-select {
            padding: 6px 10px;
            font-family: var(--font-sans);
            font-size: 13px;
            border: 1px solid var(--border-medium);
            border-radius: 3px;
            background: #FFFFFF;
            color: var(--text-main);
            outline: none;
            min-width: 220px;
            max-width: 100%;
        }

        @media (max-width: 600px) {
            .filter-select {
                width: 100%;
                min-width: unset;
            }
            .filter-group-label {
                width: 100%;
                margin-bottom: 2px;
            }
        }

        .filter-select:focus {
            border-color: var(--accent-navy);
            box-shadow: 0 0 0 2px rgba(27, 54, 93, 0.12);
        }

        .catalog-action-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            padding-top: 12px;
            border-top: 1px solid var(--border-light);
            margin-top: 12px;
        }

        .catalog-counter {
            font-family: var(--font-sans);
            font-size: 13.5px;
            font-weight: 600;
            color: var(--accent-navy);
        }

        .batch-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .small-action-btn {
            background: transparent;
            border: 1px solid var(--border-medium);
            font-family: var(--font-sans);
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .small-action-btn:hover {
            background: #FFFFFF;
            color: var(--text-main);
            border-color: var(--text-muted);
        }

        /* Thesis entries */
        .catalog-year-header {
            font-family: var(--font-serif-title);
            font-size: 21px;
            font-weight: 700;
            color: var(--accent-wine);
            border-bottom: 2px solid var(--border-light);
            padding-bottom: 6px;
            margin: 40px 0 16px 0;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }

        .catalog-year-header .year-count {
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: normal;
            color: var(--text-muted);
        }

        .thesis-entry {
            padding: 18px 0;
            border-bottom: 1px dotted var(--border-light);
            transition: background-color 0.15s ease;
        }

        .thesis-entry:hover {
            background-color: rgba(0,0,0,0.005);
        }

        .thesis-entry:last-child {
            border-bottom: none;
        }

        .thesis-top-meta {
            font-family: var(--font-sans);
            font-size: 11.5px;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .type-badge {
            padding: 2px 7px;
            border-radius: 3px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .type-badge.dissertacao {
            background: #E8EEF5;
            color: var(--accent-navy);
        }

        .type-badge.tese {
            background: #F7EAEB;
            color: var(--accent-wine);
        }

        .thesis-date {
            color: var(--text-muted);
        }

        .thesis-author {
            font-family: var(--font-sans);
            font-weight: 700;
            color: var(--text-main);
            font-size: 15px;
            letter-spacing: 0.2px;
        }

        .thesis-title {
            font-family: var(--font-serif-title);
            font-size: 17px;
            color: var(--text-main);
            line-height: 1.42;
            margin: 6px 0 10px 0;
            font-weight: 600;
        }

        .thesis-bottom-meta {
            font-family: var(--font-sans);
            font-size: 13px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }

        .advisor-btn-link {
            background: none;
            border: none;
            color: var(--accent-navy);
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            padding: 0;
            text-decoration: underline;
            text-decoration-style: dotted;
        }

        .advisor-btn-link:hover {
            color: var(--accent-wine);
        }

        .pdf-link {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: var(--accent-green);
            text-decoration: none;
            font-weight: 600;
            font-size: 12.5px;
            padding: 4px 9px;
            border-radius: 3px;
            background: #EDF5F0;
            border: 1px solid #D5E8DC;
            transition: all 0.15s ease;
        }

        .pdf-link:hover {
            background: var(--accent-green);
            color: #FFFFFF;
            text-decoration: none;
        }

        .pdf-missing {
            font-family: var(--font-sans);
            font-size: 12px;
            color: var(--text-muted);
            font-style: italic;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        /* Abstract Details / Accordion */
        .thesis-abstract-details {
            margin-top: 8px;
            border-top: 1px dashed #EDE8DF;
            padding-top: 6px;
        }

        .thesis-abstract-details summary {
            font-family: var(--font-sans);
            font-size: 12.5px;
            font-weight: 600;
            color: var(--accent-navy);
            cursor: pointer;
            user-select: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 6px;
            border-radius: 3px;
            transition: background-color 0.15s ease, color 0.15s ease;
        }

        .thesis-abstract-details summary:hover {
            color: var(--accent-wine);
            background: #F4EFEA;
        }

        .thesis-abstract-details summary:focus-visible {
            outline: 2px solid var(--accent-navy);
            background: #F4EFEA;
        }

        .thesis-abstract-details[open] summary {
            margin-bottom: 8px;
            color: var(--accent-wine);
        }

        .thesis-abstract-content {
            background: #FAF8F4;
            border-left: 3px solid var(--border-medium);
            padding: 14px 18px;
            border-radius: 0 4px 4px 0;
            font-size: 14.5px;
            line-height: 1.68;
            color: #383D45;
            text-align: justify;
        }

        /* Guidelines */
        .guideline-card {
            background: #FAF7F0;
            border-left: 4px solid var(--accent-wine);
            padding: 18px 22px;
            margin-bottom: 18px;
            border-radius: 0 3px 3px 0;
        }

        .guideline-card.navy { border-left-color: var(--accent-navy); }
        .guideline-card.gold { border-left-color: var(--accent-gold); }
        .guideline-card.green { border-left-color: var(--accent-green); }

        .guideline-title {
            font-family: var(--font-serif-title);
            font-size: 17px;
            font-weight: 700;
            display: block;
            margin-bottom: 6px;
        }

        .guideline-card .guideline-title { color: var(--accent-wine); }
        .guideline-card.navy .guideline-title { color: var(--accent-navy); }
        .guideline-card.gold .guideline-title { color: var(--accent-gold); }
        .guideline-card.green .guideline-title { color: var(--accent-green); }

        .guideline-card p {
            margin: 0;
            font-size: 15px;
            color: var(--text-main);
        }

        .guardrail-alert {
            background: #FDF4F5;
            border: 1px solid #E8C1C6;
            border-left: 4px solid var(--accent-wine);
            padding: 16px 20px;
            margin: 22px 0;
            border-radius: 4px;
        }

        .guardrail-alert h4 {
            font-family: var(--font-sans);
            font-size: 13.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--accent-wine);
            margin-bottom: 8px;
        }

        .guardrail-alert ul {
            font-size: 14.5px;
            line-height: 1.6;
            padding-left: 20px;
            color: var(--text-main);
        }

        .guardrail-alert li {
            margin-bottom: 6px;
        }

        /* Floating Back to Top Button */
        #backToTopBtn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 99;
            background: var(--accent-navy);
            color: #FFFFFF;
            border: none;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.18);
            display: none;
            align-items: center;
            justify-content: center;
            transition: opacity 0.2s ease, transform 0.2s ease;
        }

        #backToTopBtn:hover {
            background: var(--accent-wine);
            transform: translateY(-2px);
        }

        /* Sticky Main Tabs Navigation Bar */
        .main-tabs-sticky-bar {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(255, 255, 255, 0.97);
            border: 1px solid var(--border-medium);
            border-top: 3px solid var(--accent-navy);
            border-radius: 6px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            padding: 10px 14px;
            margin: 20px 0 28px 0;
            backdrop-filter: blur(8px);
        }

        @media (max-width: 860px) {
            .main-tabs-sticky-bar {
                grid-template-columns: 1fr 1fr;
                gap: 6px;
                padding: 8px;
            }
        }

        .main-tab-nav-btn {
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-medium);
            border-radius: 4px;
            padding: 10px 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.18s ease;
            text-align: left;
            font-family: var(--font-sans);
        }

        .main-tab-nav-btn:hover {
            border-color: var(--accent-navy);
            background: #EDE8DE;
        }

        .main-tab-nav-btn.active {
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
            box-shadow: 0 2px 8px rgba(27, 54, 93, 0.25);
        }

        .main-tab-nav-btn .tab-pill-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #EBF1F8;
            color: var(--accent-navy);
            font-weight: 700;
            font-size: 11px;
            flex-shrink: 0;
        }

        .main-tab-nav-btn.active .tab-pill-badge {
            background: var(--accent-gold);
            color: #1A1A1A;
        }

        .main-tab-nav-btn .tab-text-wrap {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .main-tab-nav-btn .tab-main-title {
            font-size: 13.5px;
            font-weight: 700;
            color: var(--accent-navy);
            line-height: 1.25;
        }

        .main-tab-nav-btn.active .tab-main-title {
            color: #FFFFFF;
        }

        .main-tab-nav-btn .tab-sub-title {
            font-size: 11px;
            color: var(--text-muted);
            line-height: 1.2;
        }

        .main-tab-nav-btn.active .tab-sub-title {
            color: #DFE8F4;
        }

        /* Tab Panes */
        .main-tab-pane {
            animation: fadeInTab 0.2s ease-in-out;
        }

        @keyframes fadeInTab {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Catalog Pagination Controls */
        .catalog-pagination-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            margin: 18px 0;
            padding: 12px 16px;
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-medium);
            border-radius: 4px;
        }

        .pagination-buttons {
            display: flex;
            align-items: center;
            gap: 5px;
            flex-wrap: wrap;
        }

        .pg-btn {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            border-radius: 3px;
            padding: 6px 11px;
            font-family: var(--font-sans);
            font-size: 12.5px;
            font-weight: 600;
            color: var(--accent-navy);
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .pg-btn:hover:not(:disabled) {
            background: var(--accent-navy);
            color: #FFFFFF;
            border-color: var(--accent-navy);
        }

        .pg-btn.active {
            background: var(--accent-wine);
            color: #FFFFFF;
            border-color: var(--accent-wine);
        }

        .pg-btn:disabled {
            opacity: 0.45;
            cursor: not-allowed;
        }

        .pagination-meta {
            font-family: var(--font-sans);
            font-size: 12.5px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .pagination-select {
            padding: 4px 8px;
            font-family: var(--font-sans);
            font-size: 12px;
            border: 1px solid var(--border-medium);
            border-radius: 3px;
            background: #FFFFFF;
            color: var(--text-main);
            cursor: pointer;
        }

        .print-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 10px;
        }

        .print-btn {
            background: #FFFFFF;
            border: 1px solid var(--border-medium);
            padding: 8px 16px;
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: 600;
            color: var(--accent-navy);
            border-radius: 3px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }

        .print-btn:hover {
            background: #F4EFEA;
            border-color: var(--accent-navy);
        }

        .editorial-footer {
            border-top: 2px solid var(--border-medium);
            padding-top: 32px;
            margin-top: 60px;
            text-align: center;
            font-family: var(--font-sans);
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.65;
        }

        .editorial-footer strong {
            color: var(--text-main);
        }

        @media print {
            body {
                background: #FFFFFF !important;
                padding: 0 !important;
                color: #000000 !important;
                font-size: 11pt !important;
            }
            .page-container {
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                max-width: 100% !important;
            }
            .print-bar, .catalog-controls, .toc-box, #backToTopBtn, .skip-link, .faculty-actions, .quick-actions-bar {
                display: none !important;
            }
            .policy-card, .faculty-card, .thesis-entry, .guideline-card {
                page-break-inside: avoid;
            }
            a {
                color: #000000 !important;
                text-decoration: underline !important;
            }
            .pdf-link {
                background: none !important;
                padding: 0 !important;
                border: none !important;
            }
        }
    </style>
</head>
<body>

<a href="#sec-catalogo" class="skip-link">Pular direto para o catálogo de defesas</a>

<button id="backToTopBtn" onclick="window.scrollTo({top: 0, behavior: 'smooth'})" title="Voltar ao topo" aria-label="Voltar ao topo">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"></polyline></svg>
</button>

<div class="page-container">

    <div class="print-bar">
        <span style="font-family: var(--font-sans); font-size: 12.5px; color: var(--text-muted);">Caderno Técnico de Análise Empírica e Planejamento Acadêmico</span>
        <button class="print-btn" onclick="window.print()">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
            Imprimir ou Salvar em PDF
        </button>
    </div>

    <header class="institutional-header">
        <div class="inst-sub">Universidade Federal do Sul da Bahia</div>
        <div class="inst-name">Centro de Formação em Ciências Humanas e Sociais (CFCHS)</div>
        <h1 class="main-title">Programa de Pós-Graduação em Estado e Sociedade</h1>
        <p class="main-subtitle">Panorama das 151 Dissertações e Teses Defendidas (2019–2026)</p>
        <div class="doc-meta-row">
            <span class="doc-meta-badge"><strong>Campus:</strong> Sosígenes Costa (Porto Seguro, BA)</span>
            <span class="doc-meta-badge"><strong>Fonte:</strong> Acervo do SIGAA / UFSB</span>
            <span class="doc-meta-badge"><strong>Total:</strong> 151 defesas (86 mestrados / 65 doutorados)</span>
            <span class="doc-meta-badge"><strong>Acervo Aberto:</strong> 129 textos integrais (85,4%)</span>
        </div>
    </header>

    <nav class="quick-actions-bar" aria-label="Ações Rápidas">
        <a href="#sec-cronograma" class="quick-action-btn" onclick="navegarAbaPrincipal('cronograma', 'sec-cronograma'); return false;">
            <span>Cronograma e Prazos do Edital</span>
            <span class="btn-subtitle">Inscrições e 5 Etapas</span>
        </a>
        <a href="#sec-dicas" class="quick-action-btn" onclick="navegarAbaPrincipal('dicas', 'sec-dicas'); return false;">
            <span>Regras Formais do Anteprojeto</span>
            <span class="btn-subtitle">Checklist e Vedações</span>
        </a>
        <a href="#sec-professores" class="quick-action-btn" onclick="navegarAbaPrincipal('professores', 'sec-professores'); return false;">
            <span>Docentes e Vagas da Linha 1</span>
            <span class="btn-subtitle">Perfis e Orientações</span>
        </a>
        <a href="#sec-catalogo" class="quick-action-btn" onclick="navegarAbaPrincipal('catalogo', 'sec-catalogo'); return false;">
            <span>Catálogo de Defesas com Busca</span>
            <span class="btn-subtitle">151 Trabalhos e PDFs</span>
        </a>
    </nav>

    <div class="intro-box">
        <h3>Apresentação e Escopo do Documento</h3>
        <p>
            Este caderno documenta e examina sistematicamente o histórico de defesas do PPGES da UFSB entre 2019 e 2026. A finalidade do mapeamento é identificar os temas admitidos pelo corpo docente, os perfis metodológicos recorrentes e as condições de enquadramento de pesquisas da área jurídica nas linhas do programa, com foco especial no <strong>Edital PROPPG nº 30/2026</strong>.
        </p>
        <p>
            A graduação em Direito possui aderência prioritária à <strong>Linha 1 (Estado, Instituições e Governança)</strong>. O programa privilegia o exame empírico das normas constitucionais, da atuação dos órgãos de justiça e segurança pública, e dos conflitos distributivos na região Sul e Extremo Sul da Bahia, rejeitando abordagens puramente dogmáticas ou exegéticas desprovidas de ancoragem sociopolítica e territorial.
        </p>
    </div>

    <!-- Barra Fixa de Abas Principais (Sticky Navigation Bar) -->
    <nav id="mainTabsNav" class="main-tabs-sticky-bar" role="tablist" aria-label="Navegação em Abas do Portal">
        <button type="button" id="tabBtn-cronograma" class="main-tab-nav-btn active" role="tab" aria-selected="true" aria-controls="pane-cronograma" onclick="navegarAbaPrincipal('cronograma')">
            <span class="tab-pill-badge">1</span>
            <span class="tab-text-wrap">
                <span class="tab-main-title">Edital &amp; Cronograma</span>
                <span class="tab-sub-title">Etapas, prazos e dados</span>
            </span>
        </button>
        <button type="button" id="tabBtn-professores" class="main-tab-nav-btn" role="tab" aria-selected="false" aria-controls="pane-professores" onclick="navegarAbaPrincipal('professores')">
            <span class="tab-pill-badge">2</span>
            <span class="tab-text-wrap">
                <span class="tab-main-title">Docentes &amp; Vagas</span>
                <span class="tab-sub-title">Linha 1, Lattes e perfis</span>
            </span>
        </button>
        <button type="button" id="tabBtn-catalogo" class="main-tab-nav-btn" role="tab" aria-selected="false" aria-controls="pane-catalogo" onclick="navegarAbaPrincipal('catalogo')">
            <span class="tab-pill-badge">3</span>
            <span class="tab-text-wrap">
                <span class="tab-main-title">Catálogo de Defesas</span>
                <span class="tab-sub-title">151 pesquisas com páginas</span>
            </span>
        </button>
        <button type="button" id="tabBtn-dicas" class="main-tab-nav-btn" role="tab" aria-selected="false" aria-controls="pane-dicas" onclick="navegarAbaPrincipal('dicas')">
            <span class="tab-pill-badge">4</span>
            <span class="tab-text-wrap">
                <span class="tab-main-title">Oficina de Anteprojeto</span>
                <span class="tab-sub-title">Checklist 7 laudas e propostas</span>
            </span>
        </button>
    </nav>

    <!-- Aba 1: Edital, Cronograma, Enquadramento e Políticas -->
    <div id="pane-cronograma" class="main-tab-pane active" role="tabpanel" aria-labelledby="tabBtn-cronograma">

    <section class="section-block" id="sec-cronograma">
        <div class="section-header">
            <span class="section-tag">Edital PROPPG nº 30/2026</span>
            <h2 class="section-title">Cronograma Oficial, Prazos e Etapas da Seleção (Ingresso 2027.1)</h2>
        </div>
        <p>
            O processo seletivo do Programa de Pós-Graduação em Estado e Sociedade da UFSB para ingresso no primeiro semestre letivo de 2027 (Turma 2027.1) é regido pelo <strong>Edital PROPPG nº 30/2026</strong>. O certame distribui-se em 5 etapas sucessivas, com nota de corte mínima de <strong>7,0 (sete)</strong> em cada etapa de caráter eliminatório.
        </p>

        <div class="cronograma-alert" role="alert">
            <div class="cronograma-alert-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                Alerta de Urgência: Prazos Críticos de Inscrição e Pagamento
            </div>
            <p style="font-family: var(--font-sans); font-size: 13.5px; color: var(--text-main); margin-bottom: 8px;">
                A submissão do anteprojeto e a inscrição são exclusivamente eletrônicas pelo portal público de processos seletivos do SIGAA UFSB. Fique atenta aos horários bancários e prazos improrrogáveis:
            </p>
            <div class="cronograma-alert-grid">
                <div class="cronograma-alert-item">
                    <span class="cronograma-alert-label">Inscrições no SIGAA</span>
                    <span class="cronograma-alert-val">08/10 a 20/10/2026</span>
                    <span class="cronograma-alert-detail">Encerramento improrrogável às 23h59 pelo sistema SIGAA.</span>
                </div>
                <div class="cronograma-alert-item">
                    <span class="cronograma-alert-label">Taxa (R$ 150,00) via PagTesouro</span>
                    <span class="cronograma-alert-val">Até 20/10 às 20h00</span>
                    <span class="cronograma-alert-detail">Pagamento exclusivamente via PagTesouro (Boleto/Pix) até as 20h00.</span>
                </div>
                <div class="cronograma-alert-item">
                    <span class="cronograma-alert-label">Pedido de Isenção da Taxa</span>
                    <span class="cronograma-alert-val">08/10 a 12/10/2026</span>
                    <span class="cronograma-alert-detail">Para inscritos no CadÚnico ou hipossuficientes conforme edital.</span>
                </div>
            </div>
            <div style="margin-top: 12px; font-family: var(--font-sans); font-size: 13px;">
                <strong>Acesso Direto:</strong> <a href="https://sig.ufsb.edu.br/sigaa/public/processo_seletivo/lista.jsf?nivel=S&amp;aba=p-stricto" target="_blank" rel="noopener noreferrer" style="color: var(--accent-wine); font-weight: 700; text-decoration: underline;">Portal de Inscrições do SIGAA / UFSB (Stricto Sensu)</a>
            </div>
        </div>

        <h3 style="font-family: var(--font-serif-title); font-size: 18px; color: var(--accent-navy); margin: 26px 0 12px 0;">Linha do Tempo Visual das 5 Etapas do Certame</h3>
        
        <div class="timeline-steps">
            <div class="timeline-step-card">
                <div class="step-badge-col">
                    <span class="step-number">Etapa 1</span>
                    <span class="step-date-badge">08/10 a 20/10/2026</span>
                </div>
                <div class="step-info-col">
                    <h4>Avaliação do Anteprojeto de Pesquisa (AA)</h4>
                    <p>Submissão eletrônica do arquivo em PDF no ato da inscrição no SIGAA. Avaliação anônima pela comissão examinadora da Linha 1 (máximo rígido de 7 laudas úteis). Resultado da homologação em novembro.</p>
                </div>
                <div class="step-meta-col">
                    <span class="step-weight-badge">Peso 3 (0,3)</span>
                    <span class="step-nature-text">Eliminatória e Classificatória</span>
                </div>
            </div>

            <div class="timeline-step-card">
                <div class="step-badge-col">
                    <span class="step-number">Etapa 2</span>
                    <span class="step-date-badge">23/11/2026</span>
                </div>
                <div class="step-info-col">
                    <h4>Prova Escrita de Conhecimentos (PE)</h4>
                    <p>Presencial no Campus Sosígenes Costa (Porto Seguro/BA), das 09h às 13h (4 horas). Até 3 questões dissertativas sobre a bibliografia da Linha 1. Consulta liberada exclusivamente a textos impressos na 1ª hora (09h às 10h).</p>
                </div>
                <div class="step-meta-col">
                    <span class="step-weight-badge">Peso 2 (0,2)</span>
                    <span class="step-nature-text">Eliminatória e Classificatória</span>
                </div>
            </div>

            <div class="timeline-step-card">
                <div class="step-badge-col">
                    <span class="step-number">Etapa 3</span>
                    <span class="step-date-badge">08/12 a 10/12/2026</span>
                </div>
                <div class="step-info-col">
                    <h4>Arguição Oral do Anteprojeto (AAP)</h4>
                    <p>Sessão individual remota por videoconferência (Google Meet) de 30 minutos: 10 min de exposição oral pela candidata, 10 min de arguição pela banca examinadora e 10 min de respostas. Foco na maturidade metodológica e territorial.</p>
                </div>
                <div class="step-meta-col">
                    <span class="step-weight-badge">Peso 3 (0,3)</span>
                    <span class="step-nature-text">Eliminatória e Classificatória</span>
                </div>
            </div>

            <div class="timeline-step-card">
                <div class="step-badge-col">
                    <span class="step-number">Etapa 4</span>
                    <span class="step-date-badge">Janeiro/2027</span>
                </div>
                <div class="step-info-col">
                    <h4>Análise do Currículo Lattes (ACL)</h4>
                    <p>Avaliação exclusivamente documental baseada no barema do Anexo IX do edital: Formação Acadêmica (peso 3), Atuação Profissional e Docente (peso 3) e Produção Científica/Técnica (peso 4). Documentos comprobatórios em PDF único.</p>
                </div>
                <div class="step-meta-col">
                    <span class="step-weight-badge">Peso 2 (0,2)</span>
                    <span class="step-nature-text">Apenas Classificatória</span>
                </div>
            </div>

            <div class="timeline-step-card">
                <div class="step-badge-col">
                    <span class="step-number">Etapa 5</span>
                    <span class="step-date-badge">11/02/2027</span>
                </div>
                <div class="step-info-col">
                    <h4>Heteroidentificação Étnico-Racial</h4>
                    <p>Procedimento presencial no Campus Sosígenes Costa perante a Comissão de Heteroidentificação da UFSB. Aplicável exclusivamente aos candidatos inscritos nas vagas reservadas para pessoas negras (pretas e pardas).</p>
                </div>
                <div class="step-meta-col">
                    <span class="step-weight-badge" style="background: #FDF4F5; color: var(--accent-wine); border-color: #E8C1C6;">Apto / Não Apto</span>
                    <span class="step-nature-text">Eliminatória</span>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="academic-table" aria-label="Quadro sinóptico do cronograma oficial e pesos das etapas">
                <thead>
                    <tr>
                        <th>Etapa da Seleção</th>
                        <th>Modalidade / Local</th>
                        <th>Período ou Data</th>
                        <th>Caráter</th>
                        <th class="center">Peso na MF</th>
                        <th class="center">Nota Mínima</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Inscrições e Envio do Anteprojeto</strong></td>
                        <td>Digital (SIGAA UFSB)</td>
                        <td>08/10 a 20/10/2026 (às 23h59)</td>
                        <td>Obrigatória</td>
                        <td class="center">—</td>
                        <td class="center">—</td>
                    </tr>
                    <tr>
                        <td><strong>Pagamento da Taxa de Inscrição</strong></td>
                        <td>PagTesouro (Boleto / Pix)</td>
                        <td>Até 20/10/2026 (às 20h00)</td>
                        <td>Obrigatória (R$ 150)</td>
                        <td class="center">—</td>
                        <td class="center">—</td>
                    </tr>
                    <tr>
                        <td><strong>1. Avaliação do Anteprojeto (AA)</strong></td>
                        <td>Documental / Anônima</td>
                        <td>Outubro a Novembro/2026</td>
                        <td>Eliminatória e Classificatória</td>
                        <td class="center"><strong>3 (0,3)</strong></td>
                        <td class="center">7,0</td>
                    </tr>
                    <tr>
                        <td><strong>2. Prova Escrita Presencial (PE)</strong></td>
                        <td>Presencial (CSC - Porto Seguro)</td>
                        <td>23/11/2026 (09h às 13h)</td>
                        <td>Eliminatória e Classificatória</td>
                        <td class="center"><strong>2 (0,2)</strong></td>
                        <td class="center">7,0</td>
                    </tr>
                    <tr>
                        <td><strong>3. Arguição Oral do Anteprojeto (AAP)</strong></td>
                        <td>Remota (Google Meet)</td>
                        <td>08/12 a 10/12/2026</td>
                        <td>Eliminatória e Classificatória</td>
                        <td class="center"><strong>3 (0,3)</strong></td>
                        <td class="center">7,0</td>
                    </tr>
                    <tr>
                        <td><strong>4. Análise do Currículo Lattes (ACL)</strong></td>
                        <td>Documental (Anexo IX)</td>
                        <td>Janeiro/2027</td>
                        <td>Apenas Classificatória</td>
                        <td class="center"><strong>2 (0,2)</strong></td>
                        <td class="center">—</td>
                    </tr>
                    <tr>
                        <td><strong>5. Heteroidentificação Étnico-Racial</strong></td>
                        <td>Presencial (CSC - Porto Seguro)</td>
                        <td>11/02/2027</td>
                        <td>Eliminatória (Cotas)</td>
                        <td class="center">—</td>
                        <td class="center">Apto</td>
                    </tr>
                    <tr>
                        <td><strong>Homologação do Resultado Final</strong></td>
                        <td>Publicação Oficial UFSB</td>
                        <td><strong>26/02/2027</strong></td>
                        <td>Classificatória Final</td>
                        <td class="center"><strong>10 (1,0)</strong></td>
                        <td class="center">7,0</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="formula-card">
            <strong>Fórmula Oficial de Cálculo da Média Final (MF):</strong>
            <span class="formula-code">MF = (AA × 0,3) + (PE × 0,2) + (AAP × 0,3) + (ACL × 0,2)</span>
            <span style="color: var(--text-secondary); font-size: 13px; display: block;">
                São sumariamente eliminados os candidatos que obtiverem nota inferior a 7,0 (sete) na Avaliação do Anteprojeto, na Prova Escrita ou na Arguição Oral, ou parecer "Não Apto" na Heteroidentificação.
            </span>
        </div>
    </section>

    <nav class="toc-box" aria-label="Sumário">
        <div class="toc-title">Sumário do Caderno</div>
        <ul class="toc-list">
            <li><a href="#sec-cronograma">§ 0. Cronograma e Prazos do Edital PROPPG nº 30/2026</a></li>
            <li><a href="#sec-encontro">§ 1. O Direito no PPGES: Aderência e Eixos</a></li>
            <li><a href="#sec-estatisticas">§ 2. Evolução Histórica das 151 Defesas (2019–2026)</a></li>
            <li><a href="#sec-politicas">§ 3. Pesquisas em Políticas Públicas e Justiça</a></li>
            <li><a href="#sec-professores">§ 4. Corpo Docente, Lattes e Orientações</a></li>
            <li><a href="#sec-catalogo">§ 5. Acervo Completo das 151 Defesas (com busca)</a></li>
            <li><a href="#sec-dicas">§ 6. Diretrizes Técnicas e Checklist do Anteprojeto</a></li>
        </ul>
    </nav>
""")

# Section 1
out.append("""
    <section class="section-block" id="sec-encontro">
        <div class="section-header">
            <span class="section-tag">Capítulo 1</span>
            <h2 class="section-title">O Enquadramento da Pesquisa Jurídica no PPGES</h2>
        </div>
        <p>
            O Programa de Pós-Graduação em Estado e Sociedade da UFSB adota regime marcadamente interdisciplinar, constituindo espaço de convergência entre o Direito, a Sociologia Política, a Antropologia e a Ciência Política. O programa forma pesquisadores voltados ao exame do papel do Estado, da eficácia social das normas e dos conflitos materiais por direitos.
        </p>
        <p>
            A <strong>Linha 1 (Estado, Instituições e Governança)</strong> concentra as propostas com fundamentação jurídica. O histórico de defesas do programa indica quatro eixos de convergência essenciais:
        </p>
        <ul style="padding-left: 28px; margin-bottom: 20px; line-height: 1.8;">
            <li><strong>Direito Constitucional e Políticas Públicas:</strong> Condições materiais de implementação de direitos fundamentais à saúde, educação, previdência e assistência social no nível local.</li>
            <li><strong>Instituições do Sistema de Justiça:</strong> Atuação do Poder Judiciário, Ministério Público, Defensoria Pública, audiências de custódia, centros judiciários de solução consensual de conflitos (CEJUSCs) e sistema prisional.</li>
            <li><strong>Direitos Humanos e Antidiscriminatórios:</strong> Acesso à justiça para mulheres, população negra, povos indígenas (Pataxó e Tupinambá) e comunidades remanescentes de quilombos.</li>
            <li><strong>Função Socioambiental e Regulação Territorial:</strong> Conflitos possessórios, regularização fundiária, tributação ambiental (IPTU/ICMS ecológico) e governança das águas no Sul da Bahia.</li>
        </ul>
        <p>
            A análise do acervo revela que <strong>110 das 151 defesas (72,8%)</strong> enfrentam diretamente institutos jurídicos, atos normativos ou a operação institucional de políticas públicas, o que consolida o PPGES como ambiente de excelência para graduadas e graduados em Direito que desenvolvem pesquisa empírica.
        </p>
    </section>
""")

# Section 2
out.append("""
    <section class="section-block" id="sec-estatisticas">
        <div class="section-header">
            <span class="section-tag">Capítulo 2</span>
            <h2 class="section-title">Evolução Histórica das Defesas (2019 a 2026)</h2>
        </div>
        <p>
            O programa registrou 151 defesas desde a conclusão da primeira turma de mestrado em 2019. A formação iniciou com turmas de mestrado acadêmico (2019–2020) e expandiu para o doutorado a partir de 2021, apresentando ritmo contínuo e consolidação na pós-graduação brasileira.
        </p>
        <div class="table-responsive">
            <table class="academic-table" aria-label="Estatísticas históricas das defesas do PPGES por ano">
                <thead>
                    <tr>
                        <th>Ano Letivo</th>
                        <th class="center">Dissertações (Mestrado)</th>
                        <th class="center">Teses (Doutorado)</th>
                        <th class="center">Total de Defesas</th>
                        <th class="center">Participação (%)</th>
                        <th class="center">Disponibilidade de Texto Integral</th>
                    </tr>
                </thead>
                <tbody>
""")

years_sorted = sorted(stats_by_year.keys(), reverse=True)
tot_m = sum(stats_by_year[y]['mestrado'] for y in years_sorted)
tot_t = sum(stats_by_year[y]['doutorado'] for y in years_sorted)
tot_all = sum(stats_by_year[y]['total'] for y in years_sorted)
tot_pdf = sum(stats_by_year[y]['pdf'] for y in years_sorted)

for y in years_sorted:
    st = stats_by_year[y]
    pct = (st['total'] / tot_all) * 100
    pdf_text = f"{st['pdf']} de {st['total']} disponíveis"
    out.append(f"""                    <tr>
                        <td><strong>{y}</strong></td>
                        <td class="center">{st['mestrado']}</td>
                        <td class="center">{st['doutorado']}</td>
                        <td class="center"><strong>{st['total']}</strong></td>
                        <td class="center">{pct:.1f}%</td>
                        <td class="center">{pdf_text}</td>
                    </tr>""")

out.append(f"""                </tbody>
                <tfoot>
                    <tr>
                        <td><strong>TOTAL GERAL</strong></td>
                        <td class="center"><strong>{tot_m}</strong></td>
                        <td class="center"><strong>{tot_t}</strong></td>
                        <td class="center"><strong>{tot_all}</strong></td>
                        <td class="center"><strong>100,0%</strong></td>
                        <td class="center"><strong>{tot_pdf} trabalhos em PDF ({tot_pdf/tot_all*100:.1f}%)</strong></td>
                    </tr>
                </tfoot>
            </table>
        </div>

        <p style="font-size: 15px; color: var(--text-secondary); font-style: italic;">
            * Nota institucional: Das 18 defesas realizadas no ciclo de 2026, 13 cumprem o prazo regulamentar para entrega da versão final com ficha catalográfica e homologação das atas no SIGAA, após o que os arquivos são liberados para acesso público irrestrito.
        </p>
    </section>
""")

# Section 3
out.append("""
    <section class="section-block" id="sec-politicas">
        <div class="section-header">
            <span class="section-tag">Capítulo 3</span>
            <h2 class="section-title">Áreas de Investigação em Políticas Públicas e Sistema de Justiça</h2>
        </div>
        <p>
            As pesquisas do PPGES analisam a formulação, implementação e controle social das políticas públicas na escala regional e municipal. A produção empírica organiza-se em sete setores fundamentais:
        </p>

        <div class="policy-card">
            <div class="policy-header">
                <div class="policy-name">1. Assistência Social, SUAS e Trabalho Social</div>
                <span class="policy-count-tag">Proteção Social</span>
            </div>
            <div class="policy-body">
                Avaliação dos serviços prestados nos Centros de Referência de Assistência Social (CRAS e CREAS), assédio moral e condições laborais das equipes multiprofissionais, e garantia de direitos para a população em situação de rua.
            </div>
            <div class="policy-examples">
                <strong>Trabalhos Defendidos de Referência:</strong>
                <ul>
                    <li><em>Assédio moral na assistência social: um estudo com trabalhadoras e trabalhadores do SUAS em Eunápolis, BA</em> (Dissertação, 2024). Autora: Rozana Maria da Fonseca. Orientadora: Profa. Dra. Sandra Adriana Neves Nunes. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=1059655&key=437aa837fb6586b904dec50162b7d2ca" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Democratização do acesso a direitos e luta por visibilidade: uma análise sobre o Movimento Nacional de População em Situação de Rua</em> (Dissertação, 2019). Autora: Kelly Cristina Santos Morais. Orientador: Prof. Dr. Gustavo Bruno Bicalho Gonçalves. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=357542&key=7385ab5153240e06b360ca2e1f305b53" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Violência relacionada ao trabalho e os fatores de risco psicossociais: o contexto do SUAS</em> (Dissertação, 2026). Autora: Gabrielli Sobral Dias. Orientadora: Profa. Dra. Sandra Adriana Neves Nunes. [Em homologação]</li>
                </ul>
            </div>
        </div>

        <div class="policy-card wine-accent">
            <div class="policy-header">
                <div class="policy-name">2. Sistema de Justiça, Segurança Pública e Execução Penal</div>
                <span class="policy-count-tag">Poder Judiciário</span>
            </div>
            <div class="policy-body">
                Pesquisas sobre o impacto de resoluções do Conselho Nacional de Justiça, eficácia de centros judiciários de conciliação e mediação, rotinas de audiências de custódia e dinâmicas prisionais na Bahia.
            </div>
            <div class="policy-examples">
                <strong>Trabalhos Defendidos de Referência:</strong>
                <ul>
                    <li><em>O ingresso de pessoas negras no Tribunal de Justiça do Estado da Bahia a partir da Resolução nº 203/2015 do CNJ: comarcas do Extremo Sul</em> (Dissertação, 2026). Autora: Heleonora Ferreira da Silva. Orientadora: Profa. Dra. Carolina Bessa Ferreira de Oliveira. [Em homologação]</li>
                    <li><em>Política pública de mediação e acesso efetivo à Justiça: um estudo comparativo entre Centros Judiciários de Teixeira de Freitas, BA</em> (Tese, 2023). Autor: Tiago Pereira Aguiar Susmickat. Orientador: Prof. Dr. Herbert Toledo Martins. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=914769&key=2541206888ad56c45caa227d0157e713" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>“Doutor, eu vou ficar preso?”: Análise da audiência de custódia na comarca de Porto Seguro, Bahia</em> (Dissertação, 2024). Autor: Emerson da Silva Mendes. Orientador: Prof. Dr. Herbert Toledo Martins. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=1086739&key=2faa605a64536dc7ba5e8825fe8493ab" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Políticas de segurança pública em Porto Seguro, BA: um estudo interdisciplinar sobre a Base Comunitária de Segurança do Baianão</em> (Dissertação, 2020). Autor: Silvoney Silva Pena. Orientador: Prof. Dr. Roberto Muhajir Rahnemay Rabbani. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=699154&key=0a92be5579ce233395a7275604088470" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                </ul>
            </div>
        </div>

        <div class="policy-card gold-accent">
            <div class="policy-header">
                <div class="policy-name">3. Políticas Educacionais e Ações Afirmativas</div>
                <span class="policy-count-tag">Educação Pública</span>
            </div>
            <div class="policy-body">
                Análise da efetivação de diretrizes curriculares, implementação de cotas étnico-raciais em concursos e vestibulares, educação escolar quilombola e inclusão educacional de pessoas com deficiência.
            </div>
            <div class="policy-examples">
                <strong>Trabalhos Defendidos de Referência:</strong>
                <ul>
                    <li><em>A política de educação infantil e os espaços físicos para crianças de zero a seis anos: análise a partir da abordagem do ciclo de políticas públicas</em> (Tese, 2022). Autora: Márcia Lacerda Santos Santana. Orientadora: Profa. Dra. Sandra Adriana Neves Nunes. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=856270&key=dd87ca7f9c053a2392770f58a745044e" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>O Programa Nacional de Alimentação Escolar e a Agricultura Familiar sob a ótica do desenvolvimento como liberdade</em> (Tese, 2022). Autora: Nara Eloy Machado Maturino. Orientador: Prof. Dr. Álamo Pimentel Gonçalves da Silva. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=843732&key=9f0008e5535710def4727bfb27a5b65b" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>18 Anos da Lei de Libras: avanços ou retrocessos nas políticas públicas de inclusão dos surdos?</em> (Dissertação, 2021). Autora: Angela Lemos de Oliveira. Orientadora: Profa. Dra. Christianne Benatti Rochebois. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=768181&key=2c17d1f47cd48a7799e68086254873ca" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                </ul>
            </div>
        </div>

        <div class="policy-card green-accent">
            <div class="policy-header">
                <div class="policy-name">4. Saúde Coletiva, Controle Social e Direitos Reprodutivos</div>
                <span class="policy-count-tag">Sistema Único de Saúde</span>
            </div>
            <div class="policy-body">
                Funcionamento de conselhos municipais de saúde, direitos sexuais e reprodutivos, itinerários de acesso à esterilização cirúrgica no SUS e saúde de populações tradicionais e ciganas.
            </div>
            <div class="policy-examples">
                <strong>Trabalhos Defendidos de Referência:</strong>
                <ul>
                    <li><em>Participação, sociedade civil e a capacidade de influenciar políticas sociais: o caso do Conselho Municipal de Saúde de Teixeira de Freitas</em> (Dissertação, 2020). Autora: Betânia do Amaral e Souza. Orientadora: Profa. Dra. Sandra Adriana Neves Nunes. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=473294&key=4b06541b1c8b63a7e21c6d876f120275" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Itinerários reprodutivos e a busca pela laqueadura tubária no SUS</em> (Dissertação, 2024). Autora: Paola Damascena Possari. Orientadora: Profa. Dra. Ana Carneiro Cerqueira. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=1221944&key=a1a865eabfb4fa08cefd800ee62439bf" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Filhos do Vento: adaptação e validação do PCATool Brasil versão povos ciganos adultos para a atenção primária</em> (Tese, 2023). Autora: Dayse Batista Santos. Orientadora: Profa. Dra. Sandra Adriana Neves Nunes. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=1001767&key=82f334ec10fefdfdc33f8dd1fec39a75" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                </ul>
            </div>
        </div>

        <div class="policy-card">
            <div class="policy-header">
                <div class="policy-name">5. Governança Federativa e Consórcios Públicos</div>
                <span class="policy-count-tag">Administração Pública</span>
            </div>
            <div class="policy-body">
                Arranjos federativos intermunicipais, consórcios públicos para saneamento e desenvolvimento, cooperação intergovernamental e capacidades estatais no Litoral Sul da Bahia.
            </div>
            <div class="policy-examples">
                <strong>Trabalhos Defendidos de Referência:</strong>
                <ul>
                    <li><em>A relação da multiplicidade de competências administrativas em Coroa Vermelha (BA) com as omissões do Estado: o consórcio público como instrumento jurídico de diálogo e ação</em> (Dissertação, 2022). Autor: Emmanuel Mendes Ferraz Soares. Orientador: Prof. Dr. Roberto Muhajir Rahnemay Rabbani. <span class="pdf-missing" title="Catalogado no acervo institucional">[Acervo UFSB]</span></li>
                    <li><em>Instituições e desenvolvimento territorial no Litoral Sul da Bahia: capacidades institucionais</em> (Tese, 2021). Autor: Carlos Henrique Leite Borges. Orientadora: Profa. Dra. Maria José Teixeira Carneiro. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=621668&key=362965f40fbd3400ae991e20be07393e" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Política pública de assistência técnica e inclusão socioprodutiva: Rede Mata Atlântica no Baixo Sul da Bahia</em> (Dissertação, 2019). Autora: Adriana Vilas-Bôas Borges. Orientadora: Profa. Dra. Sandra Adriana Neves Nunes. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=354767&key=e7c7d2babc29f577ca4a353719d81b67" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                </ul>
            </div>
        </div>

        <div class="policy-card wine-accent">
            <div class="policy-header">
                <div class="policy-name">6. Conflitos Fundiários e Gestão Territorial</div>
                <span class="policy-count-tag">Direito Socioambiental</span>
            </div>
            <div class="policy-body">
                Demarcação de terras tradicionalmente ocupadas, sobreposição com unidades de conservação, disputas hídricas, e atuação do Poder Judiciário em ações possessórias e constitucionais.
            </div>
            <div class="policy-examples">
                <strong>Trabalhos Defendidos de Referência:</strong>
                <ul>
                    <li><em>Terras Indígenas e Unidades de Conservação da Natureza: sobreposição de territórios, políticas públicas federais e direitos humanos no Extremo Sul da Bahia</em> (Tese, 2021). Autor: Ciro de Lopes e Barbuda. Orientadora: Profa. Dra. May Waddington Telles Ribeiro. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=718960&key=f55983bf2ba11113891b8ce5d95976c7" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Protagonismo indígena e governança da água em Porto Seguro</em> (Tese, 2025). Autor: Ricardo Almeida Cunha. Orientador: Prof. Dr. Roberto Muhajir Rahnemay Rabbani. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=1261967&key=418ba4ea05359a160810f264d745b000" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>A luta pela ressignificação dos quilombos: dos primórdios da resistência quilombola ao julgamento da ADI nº 3.239</em> (Tese, 2025). Autor: Jeferson Fernando Celos. Orientador: Prof. Dr. Roberto Muhajir Rahnemay Rabbani. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=1325680&key=1c44fb8cfba3d98b13b430dce454e717" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                </ul>
            </div>
        </div>

        <div class="policy-card gold-accent">
            <div class="policy-header">
                <div class="policy-name">7. Enfrentamento da Violência Doméstica e Igualdade Racial</div>
                <span class="policy-count-tag">Direito Antidiscriminatório</span>
            </div>
            <div class="policy-body">
                Rotas críticas de atendimento na rede de acolhimento a mulheres vítimas de violência doméstica, assistência policial e judiciária a mulheres negras, e discriminação no acesso à seguridade social.
            </div>
            <div class="policy-examples">
                <strong>Trabalhos Defendidos de Referência:</strong>
                <ul>
                    <li><em>Rotas críticas e a rede de atenção a mulheres em situação de violência doméstica e familiar em Porto Seguro, BA</em> (Dissertação, 2024). Autora: Luciane Minetto da Costa. Orientador: Prof. Dr. Rafael Andres Patino Orozco. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=1111069&key=06ed2e5d2edab93cc6eff93ac09fe25f" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>Intersecções entre a violência doméstica contra a mulher negra e as configurações afetivas no Sul da Bahia</em> (Dissertação, 2019). Autora: Eva Dayane Almeida de Goes. Orientadora: Profa. Dra. Maria Aparecida de Oliveira Lopes. <a href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=380926&key=07ef146a3aaf84d488ef01c7913bf108" target="_blank" rel="noopener noreferrer">[Texto Integral]</a></li>
                    <li><em>A discriminação racial da mulher negra no sistema previdenciário: análise crítica e o acesso à justiça</em> (Dissertação, 2024). Autora: Marta de Melo Lisboa. Orientadora: Profa. Dra. Maria Aparecida de Oliveira Lopes. [Em homologação]</li>
                </ul>
            </div>
        </div>
    </section>
    </div> <!-- /pane-cronograma -->

    <!-- Aba 2: Docentes e Vagas da Linha 1 -->
    <div id="pane-professores" class="main-tab-pane" style="display: none;" role="tabpanel" aria-labelledby="tabBtn-professores">

    <section class="section-block" id="sec-professores">
        <div class="section-header">
            <span class="section-tag">Capítulo 4</span>
            <h2 class="section-title">Corpo Docente, Currículos Lattes e Áreas de Orientação</h2>
        </div>
        <p>
            O quadro abaixo cataloga os docentes permanentes e colaboradores do PPGES com aderência a temas jurídicos, institucionais e de governança pública. Estão destacados os links oficiais para a <strong>Plataforma Lattes do CNPq</strong>, as vagas disponíveis no <strong>Edital PROPPG nº 30/2026</strong>, a formação acadêmica e as diretrizes estratégicas para o anteprojeto de mestrado.
        </p>

        <div class="faculty-subheading">4.1. Docentes da Linha 1 (Estado, Instituições e Governança) — Núcleo Jurídico Principal</div>

        <div class="faculty-grid">

            <!-- Roberto Rabbani -->
            <div class="faculty-card law-focus">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Prof. Dr. Roberto Muhajir Rahnemay Rabbani</h3>
                    </div>
                    <span class="faculty-badge">Docente Permanente (Linha 1)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 1 vaga Mestrado | 1 vaga Doutorado</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutor e Mestre em Direito (UFBA). Docente permanente da UFSB com atuação nos programas de pós-graduação da UFS e UFBA.
                    </div>
                    <p class="faculty-desc">
                        Pesquisa Teoria do Estado, Justiça Constitucional, Tributação Ambiental, Função Socioambiental da Propriedade e Pluralismo Jurídico. Orientou pesquisas sobre consórcios públicos em Coroa Vermelha, a ADI 3.239 (ressignificação dos quilombos), tributação ambiental e IPTU verde, governança indígena da água, subordinação jurídica no Uber e pluralismo jurídico camponês em Vale Verde.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Orientador prioritário para projetos que articulem direito tributário-ambiental, função social da posse/propriedade rural e conflitos territoriais com metodologia empírica no Sul da Bahia.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/8576195795981994" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Lattes Principal
                        </a>
                        <a href="http://lattes.cnpq.br/2287351005376845" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            Lattes Auxiliar
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('ROBERTO MUHAJIR RAHNEMAY RABBANI')">
                            Ver 10 defesas orientadas ↓
                        </button>
                    </div>
                    <div class="faculty-meta">10 defesas concluídas no PPGES | 24 participações em bancas examinadoras</div>
                </div>
            </div>

            <!-- Maria do Carmo Rebouças -->
            <div class="faculty-card law-focus">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Profa. Dra. Maria do Carmo Rebouças</h3>
                    </div>
                    <span class="faculty-badge">Docente Permanente (Linha 1)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 2 vagas Mestrado | 2 vagas Doutorado</span></div>
                    <div><span class="faculty-cohort-badge">Orientações ativas em andamento no PPGES</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutora em Desenvolvimento, Sociedade e Cooperação Internacional (UnB); Graduada em Direito. Ex-Pró-Reitora de Pesquisa e Pós-Graduação (PROPPG/UFSB).
                    </div>
                    <p class="faculty-desc">
                        Atua em Direito Constitucional, Direitos Humanos Internacionais, Direito Antidiscriminatório, Pluralismo Jurídico e Relações Étnico-Raciais. Desenvolve pesquisas de ponta sobre igualdade substantiva, descolonização do saber jurídico e proteção a grupos historicamente vulnerabilizados.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Principal recomendação para projetos sobre acesso à justiça, antidiscriminação de raça e gênero, tratados internacionais de direitos humanos e crítica emancipatória ao positivismo jurídico estrito.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/3610248932250458" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('MARIA DO CARMO REBOUCAS')">
                            Consultar turmas no acervo ↓
                        </button>
                    </div>
                    <div class="faculty-housing-proposals-box">
                        <span class="faculty-housing-label">Propostas de Políticas Habitacionais (Linha 1):</span>
                        <div class="faculty-housing-btns">
                            <button type="button" class="faculty-prop-btn" onclick="selecionarOpcaoHabitacional(1)">
                                <span>Opção 1: REURB-S Baianão (DPE/BA)</span>
                                <span>↓</span>
                            </button>
                            <button type="button" class="faculty-prop-btn" onclick="selecionarOpcaoHabitacional(2)">
                                <span>Opção 2: Mediação TJBA &amp; CIDH (Trancoso)</span>
                                <span>↓</span>
                            </button>
                            <button type="button" class="faculty-prop-btn" onclick="selecionarOpcaoHabitacional(3)">
                                <span>Opção 3: REURB-E vs. REURB-S na Orla</span>
                                <span>↓</span>
                            </button>
                        </div>
                    </div>
                    <div class="faculty-meta">Maior oferta de vagas na Linha 1 no Edital 2026/2027 | Atuação destacada na governança universitária</div>
                </div>
            </div>

            <!-- Carolina Bessa -->
            <div class="faculty-card law-focus">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Profa. Dra. Carolina Bessa F. de Oliveira</h3>
                    </div>
                    <span class="faculty-badge">Docente Permanente (Linha 1)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 1 vaga Mestrado | 1 vaga Doutorado</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutora em Educação (USP); Mestre (UFU); Graduada em Direito e em Pedagogia; Especialista em Direitos Humanos.
                    </div>
                    <p class="faculty-desc">
                        Investiga as relações estruturais entre Direitos Humanos, direitos sociais e desigualdades no sistema de justiça. Orientou a pesquisa sobre cotas raciais para ingresso na magistratura no Tribunal de Justiça da Bahia (Resolução CNJ nº 203/2015).
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Excelente interlocução para projetos que investiguem a dinâmica interna do Poder Judiciário, carreiras jurídicas, políticas afirmativas nas instituições de justiça e educação em prisões.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/4621783626179392" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('CAROLINA BESSA FERREIRA DE OLIVEIRA')">
                            Ver defesa orientada (2026) ↓
                        </button>
                    </div>
                    <div class="faculty-meta">Orientação pioneira sobre cotas no Judiciário baiano | Pesquisa sobre desigualdades institucionais</div>
                </div>
            </div>

            <!-- Herbert Toledo Martins -->
            <div class="faculty-card law-focus">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Prof. Dr. Herbert Toledo Martins</h3>
                    </div>
                    <span class="faculty-badge">Docente Colaborador (Linha 1)</span>
                    <div><span class="faculty-vagas-badge">Líder do Grupo de Pesquisa GPECS / CNPq</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutor em Sociologia (UFRJ); Mestre e Graduado em Ciências Sociais (UFMG).
                    </div>
                    <p class="faculty-desc">
                        Especialista em Sociologia Política e Sociologia do Direito, meios consensuais de resolução de conflitos (CEJUSCs), audiências de custódia, dinâmicas prisionais e administração de conflitos ambientais.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Referência para pesquisas empíricas sobre o funcionamento cotidiano de fóruns, audiências de custódia, centros de conciliação/mediação e práticas policiais no Extremo Sul baiano.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/7404757966009813" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('HERBERT TOLEDO MARTINS')">
                            Ver 11 defesas orientadas ↓
                        </button>
                    </div>
                    <div class="faculty-meta">11 defesas concluídas no PPGES | 22 participações em bancas examinadoras</div>
                </div>
            </div>

            <!-- Spensy Pimentel -->
            <div class="faculty-card law-focus">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Prof. Dr. Spensy Kmitta Pimentel</h3>
                    </div>
                    <span class="faculty-badge">Docente Permanente (Linha 1)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 1 vaga Mestrado</span></div>
                    <div><span class="faculty-cohort-badge">Orientações ativas em andamento no PPGES</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutor em Antropologia Social (USP); Graduado em Jornalismo.
                    </div>
                    <p class="faculty-desc">
                        Atua em Antropologia do Direito, Conflitos Fundiários e Demarcação de Terras Indígenas, Ecologia Política, Autonomias Comunitárias e Retomadas Territoriais. Analisa a interação entre laudos antropológicos, decisões judiciais e direitos territoriais originários.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Orientação recomendada para propostas que abordem direitos indígenas (Art. 231 da CF/88), teses do marco temporal, pluralismo jurídico tradicional e judicialização de conflitos possessórios.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/0323206925873394" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('SPENSY')">
                            Consultar turmas no acervo ↓
                        </button>
                    </div>
                    <div class="faculty-meta">Referência nacional em antropologia jurídica e direitos dos povos originários</div>
                </div>
            </div>

            <!-- José André Ribeiro -->
            <div class="faculty-card law-focus">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Prof. Dr. José André Ribeiro</h3>
                    </div>
                    <span class="faculty-badge">Docente Permanente (Linha 1)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 1 vaga Mestrado</span></div>
                    <div><span class="faculty-cohort-badge">Orientações ativas em andamento no PPGES</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutor em Filosofia (UFC); Docente do IFBA Porto Seguro e permanente no PPGES.
                    </div>
                    <p class="faculty-desc">
                        Pesquisa Ética, Teoria Democrática, Filosofia Política e as relações entre Estado, Tecnologia, Algoritmos e Novas Dinâmicas do Poder. Examina a governança digital e seus reflexos na esfera pública contemporânea.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Perfil indicado para anteprojetos que debatam governança digital, regulação de inteligência artificial pelo Estado, proteção de dados e transformações tecnológicas nas instituições públicas.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/2909888019684406" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('JOSE ANDRE RIBEIRO')">
                            Consultar turmas no acervo ↓
                        </button>
                    </div>
                    <div class="faculty-meta">Pesquisa em teoria democrática, ética e tecnologia na Linha 1</div>
                </div>
            </div>

        </div>

        <div class="faculty-subheading">4.2. Docentes das Linhas 2, 3 e 4 com Interface em Políticas Públicas, Memória e Direitos</div>

        <div class="faculty-grid">

            <!-- Sandra Adriana -->
            <div class="faculty-card">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Profa. Dra. Sandra Adriana Neves Nunes</h3>
                    </div>
                    <span class="faculty-badge">Políticas Sociais e Saúde (Linha 2)</span>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutora em Saúde Pública (ISC/UFBA); Mestre em Saúde Coletiva; Graduada em Serviço Social.
                    </div>
                    <p class="faculty-desc">
                        Coordena investigações sobre a rede do SUAS (CRAS e CREAS), controle social nos conselhos municipais, saúde de populações vulneráveis, assédio laboral e direitos sexuais/reprodutivos no SUS.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Interlocução estratégica para investigações sobre a eficácia de direitos sociais na ponta (SUAS, CREAS e CRAS), violência e assédio no trabalho de assistência social, direitos sexuais/reprodutivos e saúde coletiva no SUS regional.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/1233148620777469" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('SANDRA ADRIANA NEVES NUNES')">
                            Ver 11 defesas orientadas ↓
                        </button>
                    </div>
                    <div class="faculty-meta">11 defesas concluídas no PPGES | 17 participações em bancas examinadoras</div>
                </div>
            </div>

            <!-- Valéria Giannella -->
            <div class="faculty-card">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Profa. Dra. Valéria Giannella</h3>
                    </div>
                    <span class="faculty-badge">Governança dos Comuns (Linha 2)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 1 vaga Mestrado | 2 vagas Doutorado</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutora em Políticas Públicas do Território (IUAV de Veneza/Itália); Pós-Doutora pela UFBA.
                    </div>
                    <p class="faculty-desc">
                        Trabalha com a abordagem sociocêntrica na análise de políticas públicas, governança de bens comuns hídricos, direitos das juventudes indígenas e redes de proteção a crianças e adolescentes.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Referência para pesquisas sobre a governança de bens comuns, gestão e conflitos em torno das águas no Sul da Bahia, participação comunitária e conselhos de direitos de crianças e adolescentes.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/2523004549190093" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('VALERIA GIANNELLA')">
                            Ver 8 defesas orientadas ↓
                        </button>
                    </div>
                    <div class="faculty-meta">8 defesas concluídas no PPGES | 15 participações em bancas examinadoras</div>
                </div>
            </div>

            <!-- Álamo Pimentel -->
            <div class="faculty-card">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Prof. Dr. Álamo Pimentel G. da Silva</h3>
                    </div>
                    <span class="faculty-badge">Educação e Sociedade (Linha 2)</span>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutor em Educação (UFRGS); Pós-Doutor em Sociologia do Conhecimento (Universidade de Coimbra - CES).
                    </div>
                    <p class="faculty-desc">
                        Desenvolve pesquisas sobre políticas educacionais, ações afirmativas, titulação de territórios quilombolas, educação popular e efetividade de direitos fundamentais para comunidades tradicionais.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Recomendado para propostas que articulem ações afirmativas, igualdade racial e étnica, direitos quilombolas e a efetivação de políticas educacionais no território baiano.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/5299277618123064" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('ALAMO PIMENTEL GONCALVES DA SILVA')">
                            Ver 11 defesas orientadas ↓
                        </button>
                    </div>
                    <div class="faculty-meta">11 defesas concluídas no PPGES | 38 participações em bancas examinadoras</div>
                </div>
            </div>

            <!-- Francisco Cancela -->
            <div class="faculty-card">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Prof. Dr. Francisco Eduardo Torres Cancela</h3>
                    </div>
                    <span class="faculty-badge">Memória e Direitos Originários (Linha 4)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 2 vagas Mestrado | 2 vagas Doutorado</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutor em História Social do Brasil (UFBA); Professor Titular da UNEB e permanente no PPGES/UFSB.
                    </div>
                    <p class="faculty-desc">
                        Especialista em História Indígena, Direitos Originários, Retomadas Territoriais e Decolonialidade. Orientou a pesquisa sobre a retomada Pataxó Aragwaksã no território do Monte Pascoal.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Docente de referência na Linha 4 para projetos em história indígena, direitos territoriais originários, demarcações de terras e confrontos jurídicos-históricos (como a retomada Pataxó Aragwaksã).
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/8498239058487526" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('FRANCISCO EDUARDO TORRES CANCELA')">
                            Ver 4 defesas orientadas ↓
                        </button>
                    </div>
                    <div class="faculty-meta">4 defesas concluídas no PPGES | Pesquisador das resistências indígenas no Sul da Bahia</div>
                </div>
            </div>

            <!-- Fernanda Lunkes -->
            <div class="faculty-card">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Profa. Dra. Fernanda Luzia Lunkes</h3>
                    </div>
                    <span class="faculty-badge">Discurso Jurídico e Trabalho (Linha 3)</span>
                    <div><span class="faculty-vagas-badge">Edital 2026: 1 vaga Mestrado | 1 vaga Doutorado</span></div>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutora em Estudos de Linguagem (UFF); Mestre em Letras (UEM).
                    </div>
                    <p class="faculty-desc">
                        Aplica a Análise do Discurso Materialista a textos jurídicos e jornalísticos, com foco em trabalho análogo à escravidão, violência institucional e silenciamentos nos discursos de Estado.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Recomendada na Linha 3 para projetos de interface entre Direito e Linguagem que apliquem a análise do discurso a processos judiciais, sentenças, termos de ajustamento de conduta (TAC) e discursos estatais sobre trabalho análogo à escravidão.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/4507366472893400" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('FERNANDA LUZIA LUNKES')">
                            Ver defesa orientada (2026) ↓
                        </button>
                    </div>
                    <div class="faculty-meta">Orientação de 2026 sobre trabalho análogo à escravidão e memória institucional</div>
                </div>
            </div>

            <!-- Lilian Reichert Coelho -->
            <div class="faculty-card">
                <div>
                    <div class="faculty-header-top">
                        <h3 class="faculty-name">Profa. Dra. Lilian Reichert Coelho</h3>
                    </div>
                    <span class="faculty-badge">Cultura, Sociedade e Território (Linha 4)</span>
                    <div class="faculty-training">
                        <strong>Formação:</strong> Doutora em Letras (UFBA); Mestre (UNESP); Graduada em Jornalismo (UEL).
                    </div>
                    <p class="faculty-desc">
                        Concentra o maior volume de orientações concluídas no PPGES (13 defesas). Analisa dinâmicas territoriais, conselhos municipais, narrativas contra-hegemônicas e redes produtivas comunitárias.
                    </p>
                    <div class="faculty-tip-box">
                        <strong>Diretriz para Anteprojeto:</strong>
                        Maior orientadora histórica do programa (13 defesas), com forte aderência a projetos sobre conselhos municipais, redes de economia solidária, trajetórias contra-hegemônicas e políticas públicas no Baixo Sul da Bahia.
                    </div>
                </div>
                <div>
                    <div class="faculty-actions">
                        <a href="http://lattes.cnpq.br/9631991512840338" target="_blank" rel="noopener noreferrer" class="faculty-lattes-btn">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Currículo Lattes
                        </a>
                        <button type="button" class="faculty-filter-btn" onclick="filtrarPorDocente('LILIAN REICHERT COELHO')">
                            Ver 13 defesas orientadas ↓
                        </button>
                    </div>
                    <div class="faculty-meta">Maior número de orientações defendidas na história do PPGES (13 defesas)</div>
                </div>
            </div>

        </div>

        <div class="faculty-subheading">4.3. Quadro Geral dos 21 Orientadores e Histórico de Defesas (2019–2026)</div>
        <p style="font-size: 14.5px; color: var(--text-secondary); margin-bottom: 12px;">
            A tabela reúne a integralidade dos 21 professores que orientaram trabalhos concluídos no PPGES, categorizados pelo volume de dissertações e teses defendidas, com links de filtragem direta no acervo:
        </p>

        <div class="table-responsive">
            <table class="academic-table" aria-label="Quadro geral dos 21 orientadores com histórico de defesas">
                <thead>
                    <tr>
                        <th>Orientador(a)</th>
                        <th class="center">Dissertações</th>
                        <th class="center">Teses</th>
                        <th class="center">Total</th>
                        <th class="center">Ação Rápida</th>
                    </tr>
                </thead>
                <tbody>
""")

# Compile 21 advisors data
advisor_table_data = []
for ori_name in sorted(advisor_counts.keys()):
    ori_items = [d for d in catalog if d['orientador_clean'] == ori_name]
    m_cnt = sum(1 for d in ori_items if 'mestrado' in d['nivel'].lower())
    t_cnt = sum(1 for d in ori_items if 'doutorado' in d['nivel'].lower())
    advisor_table_data.append((ori_name, m_cnt, t_cnt, len(ori_items)))

# Sort by total descending, then name
advisor_table_data.sort(key=lambda x: (-x[3], x[0]))

for ori_name, m_cnt, t_cnt, tot_cnt in advisor_table_data:
    out.append(f"""                    <tr>
                        <td><strong>{html.escape(ori_name.title())}</strong></td>
                        <td class="center">{m_cnt}</td>
                        <td class="center">{t_cnt}</td>
                        <td class="center"><strong>{tot_cnt}</strong></td>
                        <td class="center">
                            <button type="button" class="advisor-btn-link" onclick="filtrarPorDocente('{html.escape(ori_name)}')" title="Filtrar todas as {tot_cnt} defesas no acervo">
                                Filtrar defesas ({tot_cnt})
                            </button>
                        </td>
                    </tr>""")

out.append(f"""                </tbody>
                <tfoot>
                    <tr>
                        <td><strong>TOTAL (21 Orientadores)</strong></td>
                        <td class="center"><strong>{tot_m}</strong></td>
                        <td class="center"><strong>{tot_t}</strong></td>
                        <td class="center"><strong>{tot_all}</strong></td>
                        <td class="center"><strong>151 defesas mapeadas</strong></td>
                    </tr>
                </tfoot>
            </table>
        </div>

    </section>
    </div> <!-- /pane-professores -->

    <!-- Aba 3: Catálogo de Defesas -->
    <div id="pane-catalogo" class="main-tab-pane" style="display: none;" role="tabpanel" aria-labelledby="tabBtn-catalogo">

    <section class="section-block" id="sec-catalogo">
        <div class="section-header">
            <span class="section-tag">Capítulo 5</span>
            <h2 class="section-title">Acervo Completo das 151 Dissertações e Teses (2019 a 2026)</h2>
        </div>
        <p>
            O catálogo abaixo reúne todas as 151 pesquisas defendidas no PPGES da UFSB em ordem cronológica decrescente. Utilize o campo de busca com normalização fonética/ortográfica ou os filtros interativos para pesquisar por tema jurídico, conceito-chave, autor, orientador ou ano:
        </p>

        <!-- Controls Block -->
        <div class="catalog-controls" role="search" aria-label="Controles de busca e filtro de defesas">
            <div class="search-row">
                <input type="text" id="searchInput" class="search-input" placeholder="Digite uma palavra-chave, conceito jurídico, autor ou orientador..." oninput="filtrarAcervo()" aria-label="Pesquisar defesas por palavra-chave ou nome">
                <button type="button" id="searchClearBtn" class="search-clear-btn" onclick="limparBusca()" aria-label="Limpar termo de busca">✕</button>
            </div>
            
            <div class="filter-row">
                <span class="filter-group-label">Nível:</span>
                <div class="filter-buttons" role="group" aria-label="Filtro por nível acadêmico">
                    <button type="button" class="filter-btn active" data-tipo="todos" onclick="setFiltroTipo('todos', this)" aria-pressed="true">Todos (151)</button>
                    <button type="button" class="filter-btn" data-tipo="dissertacao" onclick="setFiltroTipo('dissertacao', this)" aria-pressed="false">Dissertações (86)</button>
                    <button type="button" class="filter-btn" data-tipo="tese" onclick="setFiltroTipo('tese', this)" aria-pressed="false">Teses (65)</button>
                </div>
            </div>

            <div class="filter-row">
                <span class="filter-group-label">Arquivo:</span>
                <div class="filter-buttons" role="group" aria-label="Filtro por disponibilidade de arquivo">
                    <button type="button" class="filter-btn active" data-pdf="todos" onclick="setFiltroPdf('todos', this)" aria-pressed="true">Todos (151)</button>
                    <button type="button" class="filter-btn" data-pdf="com-pdf" onclick="setFiltroPdf('com-pdf', this)" aria-pressed="false">Com PDF (129)</button>
                    <button type="button" class="filter-btn" data-pdf="homologacao" onclick="setFiltroPdf('homologacao', this)" aria-pressed="false">Em Homologação (22)</button>
                </div>
            </div>

            <div class="filter-row" style="margin-bottom: 6px;">
                <span class="filter-group-label">Seletores:</span>
                <select id="yearSelect" class="filter-select" onchange="filtrarAcervo()" aria-label="Filtrar por ano de defesa">
                    <option value="todos">Todos os Anos (2019–2026)</option>
                    <option value="2026">Ano 2026 (18 defesas)</option>
                    <option value="2025">Ano 2025 (18 defesas)</option>
                    <option value="2024">Ano 2024 (17 defesas)</option>
                    <option value="2023">Ano 2023 (26 defesas)</option>
                    <option value="2022">Ano 2022 (24 defesas)</option>
                    <option value="2021">Ano 2021 (22 defesas)</option>
                    <option value="2020">Ano 2020 (13 defesas)</option>
                    <option value="2019">Ano 2019 (13 defesas)</option>
                </select>

                <select id="advisorSelect" class="filter-select" onchange="filtrarAcervo()" aria-label="Filtrar por orientador(a)">
                    <option value="todos">Todos os 21 Orientadores</option>
""")

for adv, cnt in sorted(advisor_counts.items(), key=lambda x: norm(x[0])):
    out.append(f"""                    <option value="{html.escape(adv)}">{html.escape(adv.title())} ({cnt})</option>""")

out.append("""                </select>
            </div>

            <div class="catalog-action-row">
                <div class="catalog-counter" id="catalogCounter" aria-live="polite">
                    Exibindo todas as 151 defesas cadastradas.
                </div>
                <div class="batch-actions">
                    <button type="button" class="small-action-btn" onclick="toggleTodosResumos(true)">Expandir Resumos</button>
                    <button type="button" class="small-action-btn" onclick="toggleTodosResumos(false)">Recolher Resumos</button>
                    <button type="button" class="small-action-btn" onclick="resetarFiltros()">Limpar Filtros</button>
                </div>
            </div>
        </div>

        <!-- Barra de Paginação Superior -->
        <div class="catalog-pagination-bar" id="paginationBarTop"></div>

        <div id="catalogListContainer">
""")

# Build Entries grouped by year
for y in sorted(by_year.keys(), reverse=True):
    items = by_year[y]
    out.append(f"""            <div class="year-group" data-year="{y}">
                <div class="catalog-year-header">
                    <span>Ano Letivo {y}</span>
                    <span class="year-count">{len(items)} defesas</span>
                </div>
""")
    for item in items:
        entry_id = item['id']
        nivel = item['nivel']
        tipo_code = "dissertacao" if "mestrado" in nivel.lower() else "tese"
        nivel_label = f"Mestrado #{entry_id}" if tipo_code == "dissertacao" else f"Doutorado #{entry_id}"
        badge_cls = "dissertacao" if tipo_code == "dissertacao" else "tese"
        
        has_pdf = bool(item.get('link_pdf') and item['link_pdf'].strip())
        pdf_attr = "com-pdf" if has_pdf else "homologacao"
        
        data_text = item.get('data', f'Ano {y}')
        autor = item.get('autor', '').strip()
        titulo = item.get('titulo', '').strip()
        orientador = item['orientador_clean']
        clean_res = item['clean_resumo']
        
        # Build search attribute: normalized text containing all metadata tokens
        search_blob = norm(f"{entry_id} {autor} {titulo} {orientador} {data_text} {y} {nivel} {clean_res}")
        
        # PDF link or status
        if has_pdf:
            pdf_html = f"""<a href="{html.escape(item['link_pdf'])}" target="_blank" rel="noopener noreferrer" class="pdf-link" title="Baixar texto integral em PDF no SIGAA">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                            Texto Integral (SIGAA)
                        </a>"""
        else:
            pdf_html = """<span class="pdf-missing" title="Trabalho concluído cumprindo prazo regulamentar de entrega e homologação institucional">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                            Em homologação no SIGAA
                        </span>"""
        
        # Summary details
        resumo_html = ""
        if clean_res:
            resumo_html = f"""                    <details class="thesis-abstract-details">
                        <summary>
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                            Ver resumo da pesquisa
                        </summary>
                        <div class="thesis-abstract-content">
                            {html.escape(clean_res)}
                        </div>
                    </details>"""
        
        out.append(f"""                <div class="thesis-entry" data-tipo="{tipo_code}" data-pdf="{pdf_attr}" data-ano="{y}" data-orientador="{html.escape(orientador)}" data-search="{html.escape(search_blob)}">
                    <div class="thesis-top-meta">
                        <span class="type-badge {badge_cls}">{nivel_label}</span>
                        <span class="thesis-date">{html.escape(data_text)}</span>
                    </div>
                    <div class="thesis-author">{html.escape(autor)}</div>
                    <div class="thesis-title">{html.escape(titulo)}</div>
                    <div class="thesis-bottom-meta">
                        <div class="advisor-name">
                            Orientador(a): <button type="button" class="advisor-btn-link" onclick="filtrarPorDocente('{html.escape(orientador)}')" title="Filtrar todas as defesas orientadas por {html.escape(orientador)}">{html.escape(orientador)}</button>
                        </div>
                        <div>{pdf_html}</div>
                    </div>
{resumo_html}
                </div>""")
        
    out.append("""            </div>
""")

out.append("""        </div>

        <!-- Barra de Paginação Inferior -->
        <div class="catalog-pagination-bar" id="paginationBarBottom"></div>

        <div id="noResultsMsg" style="display: none; padding: 40px 20px; text-align: center; background: #FAF7F0; border-radius: 4px; margin-top: 20px; border: 1px solid var(--border-medium);">
            <p id="noResultsTitle" style="font-family: var(--font-serif-title); font-size: 19px; color: var(--accent-wine); margin-bottom: 8px;">Nenhum trabalho localizado com os critérios informados.</p>
            <p id="noResultsDesc" style="font-family: var(--font-sans); font-size: 14px; color: var(--text-secondary); margin-bottom: 16px;">Tente utilizar termos mais genéricos ou clique no botão abaixo para redefinir os filtros.</p>
            <button type="button" class="small-action-btn" onclick="resetarFiltros()" style="padding: 8px 16px; font-size: 13px; color: var(--accent-navy); border-color: var(--accent-navy);">Limpar Todos os Filtros</button>
        </div>

    </section>
    </div> <!-- /pane-catalogo -->

    <!-- Aba 4: Regras Formais e Oficina de Anteprojeto -->
    <div id="pane-dicas" class="main-tab-pane" style="display: none;" role="tabpanel" aria-labelledby="tabBtn-dicas">

    <section class="section-block" id="sec-dicas">
        <div class="section-header">
            <span class="section-tag">Capítulo 6</span>
            <h2 class="section-title">Diretrizes Técnicas e Checklist do Anteprojeto de Pesquisa</h2>
        </div>
        <p>
            O exame exaustivo das 151 defesas e as disposições do <strong>Edital PROPPG nº 30/2026</strong> permitem consolidar diretrizes estratégicas e metodológicas indispensáveis para a candidatura de graduadas e graduados em Direito:
        </p>
        
        <div class="guideline-card">
            <strong class="guideline-title">1. Delimitação sociopolítica do problema (O Direito em Ação)</strong>
            <p>
                A proposta deve investigar os efeitos práticos do ordenamento jurídico nas relações sociais, na eficácia das políticas públicas e na garantia de direitos fundamentais. Anteprojetos dedicados exclusivamente à dogmática civil/constitucional abstrata ou à catalogação descontextualizada de jurisprudência colidem frontalmente com a proposta interdisciplinar do PPGES e são sistematicamente desaconselhados pela banca examinadora.
            </p>
        </div>

        <div class="guideline-card navy">
            <strong class="guideline-title">2. Articulação com a bibliografia obrigatória da Linha 1</strong>
            <p>
                O referencial teórico deve dialogar com as categorias dos autores recomendados no processo seletivo: governança democrática e arranjos jurídicos de políticas públicas (Brunet & Bucci), pluralismo jurídico e direitos socioambientais (Roberto Rabbani), e perspectivas decoloniais e contra-hegemônicas sobre a terra e o bem viver (Ailton Krenak).
            </p>
        </div>

        <div class="guideline-card gold">
            <strong class="guideline-title">3. Recorte territorial e empírico no Sul da Bahia</strong>
            <p>
                Mais de 80% dos trabalhos defendidos no programa elegem territórios do Sul e Extremo Sul baiano como campo empírico (Porto Seguro, Eunápolis, Teixeira de Freitas, Itamaraju, Ilhéus, Santa Cruz Cabrália, Coroa Vermelha ou Monte Pascoal). O projeto ganha robustez ao delimitar comarcas, varas judiciais, CEJUSCs, delegacias, conselhos tutelares ou comunidades tradicionais específicas.
            </p>
        </div>

        <div class="guideline-card green">
            <strong class="guideline-title">4. Alinhamento temático e estratégico às vagas dos orientadores</strong>
            <p>
                A candidata deve demonstrar convergência direta com a produção científica recente e as vagas do orientador pretendido na Linha 1. Se o foco for desigualdades no Judiciário e sistema de justiça, priorizar a Profa. Dra. Carolina Bessa ou a Profa. Dra. Maria do Carmo Rebouças; se o foco for propriedade rural, tributação e meio ambiente, convergir com o Prof. Dr. Roberto Rabbani; se envolver mediação e custódia, dialogar com o Prof. Dr. Herbert Toledo Martins; se versar sobre direitos originários e territorialidade indígena, articular com o Prof. Dr. Spensy Pimentel ou Prof. Dr. Francisco Cancela.
            </p>
        </div>

        <div class="guardrail-alert" role="alert">
            <h4>Limites Formais Rígidos e Vedações do Edital (PROPPG nº 30/2026)</h4>
            <ul>
                <li><strong>Extensão Máxima Rígida:</strong> O anteprojeto de mestrado é restrito a <strong>no máximo 7 laudas úteis</strong> de texto corrido (excluindo capa e referências bibliográficas). Extrapolar o limite de páginas gera perda imediata de pontos ou desclassificação formal.</li>
                <li><strong>Vedação Absoluta à Quebra de Anonimato:</strong> O arquivo do anteprojeto <strong>NUNCA deve conter o nome da candidata</strong>, número de inscrição na OAB, menção a escritórios, cargos profissionais ou elementos biográficos que permitam identificar a autoria perante a comissão examinadora. A quebra de sigilo acarreta eliminação sumária do certame.</li>
                <li><strong>Declaração de Integridade sobre Inteligência Artificial:</strong> O anteprojeto deve conter, em sua folha final, a declaração explícita de uso/não uso de ferramentas de inteligência artificial generativa, sob as penas de desclassificação, em cumprimento à Portaria CNPq nº 2.664/2026.</li>
                <li><strong>Composição da Nota Final:</strong> O anteprojeto possui <strong>peso 0,3</strong> na média ponderada final: <code>MF = (Anteprojeto × 0,3) + (Prova Escrita × 0,2) + (Arguição Oral × 0,3) + (Currículo Lattes × 0,2)</code>. A nota mínima eliminatória é 7,0 por etapa.</li>
            </ul>
        </div>

        <div class="compliance-checklist-card" id="sec-checklist">
            <div class="compliance-checklist-header">
                <h3>Checklist de Conformidade Pré-Submissão do Anteprojeto</h3>
                <p>Verificação item a item antes do upload definitivo no SIGAA / UFSB (Edital PROPPG nº 30/2026):</p>
            </div>
            <div class="checklist-grid">
                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="1. Limite Máximo Rígido de Extensão: até 7 laudas úteis">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>1. Limite Máximo Rígido de Extensão</span>
                            <span class="checklist-tag danger">Eliminatório: Máx. 7 Laudas</span>
                        </div>
                        <p class="checklist-desc">
                            O corpo textual do anteprojeto (Introdução, Problema, Hipótese, Justificativa, Objetivos, Referencial Teórico, Metodologia e Cronograma) possui limite rígido de <strong>até 7 laudas úteis</strong> de texto corrido. A capa/folha de rosto e as referências bibliográficas não contam nesse cômputo. Extrapolações geram perda drástica de pontos ou eliminação sumária.
                        </p>
                    </div>
                </div>

                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="2. Anonimato Absoluto no Corpo do Texto">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>2. Anonimato Absoluto no Corpo do Texto</span>
                            <span class="checklist-tag danger">Eliminatório: Sigilo Total</span>
                        </div>
                        <p class="checklist-desc">
                            O documento <strong>NUNCA deve conter nome civil da candidata, número de inscrição na OAB, e-mail pessoal</strong>, cargos ocupados, escritórios de advocacia, menção a processos em que atuou ou quaisquer elementos autobiográficos. A quebra de anonimato acarreta desclassificação imediata.
                        </p>
                    </div>
                </div>

                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="3. Higienização de Metadados do Arquivo PDF">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>3. Higienização de Metadados do Arquivo PDF</span>
                            <span class="checklist-tag danger">Sigilo Digital</span>
                        </div>
                        <p class="checklist-desc">
                            Antes de exportar o arquivo em PDF, confira as propriedades do documento (no Word: Arquivo &gt; Informações &gt; Propriedades; no LibreOffice: Arquivo &gt; Propriedades) e <strong>remova o nome do autor, da empresa e do usuário do computador</strong>, assegurando que o leitor de PDF da banca examinadora não identifique a autoria.
                        </p>
                    </div>
                </div>

                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="4. Declaração de Integridade sobre Inteligência Artificial: Portaria CNPq nº 2.664/2026">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>4. Declaração de Integridade sobre Inteligência Artificial</span>
                            <span class="checklist-tag danger">Portaria CNPq nº 2.664/2026</span>
                        </div>
                        <p class="checklist-desc">
                            Inserção obrigatória, na folha final após as referências bibliográficas, de cláusula explícita informando a utilização ou não de ferramentas de inteligência artificial generativa (e suas finalidades, como revisão textual ou formatação), sob pena de desclassificação formal.
                        </p>
                    </div>
                </div>

                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="5. Indicação de 2 Opções de Orientadores da Linha 1">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>5. Indicação de 2 Opções de Orientadores da Linha 1</span>
                            <span class="checklist-tag success">Alinhamento Estratégico</span>
                        </div>
                        <p class="checklist-desc">
                            Constar na folha de rosto anônima a indicação expressa da <strong>1ª e 2ª opção de orientador(a)</strong> dentre os docentes com vagas abertas na Linha 1 (Estado, Instituições e Governança), compatibilizando o tema do projeto com as linhas de pesquisa declaradas pelos professores.
                        </p>
                    </div>
                </div>

                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="6. Formatação Gráfica e Padrões Técnicos ABNT NBR 6023 em PDF">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>6. Formatação Gráfica e Padrões Técnicos ABNT</span>
                            <span class="checklist-tag">Normas ABNT em PDF</span>
                        </div>
                        <p class="checklist-desc">
                            Arquivo exportado obrigatoriamente em formato PDF (.pdf). Formatação: folha A4, fonte Times New Roman 12 ou Arial 12, espaçamento entrelinhas 1,5, margens superior e esquerda de 3,0 cm, inferior e direita de 2,0 cm, recuo de primeira linha de parágrafo regular (1,25 cm), e referências bibliográficas alinhadas à esquerda e formatadas segundo a <strong>ABNT NBR 6023</strong>.
                        </p>
                    </div>
                </div>

                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="7. Ancoragem Territorial e Epistemológica no Sul da Bahia">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>7. Ancoragem Territorial e Epistemológica no Sul da Bahia</span>
                            <span class="checklist-tag success">O Direito em Ação</span>
                        </div>
                        <p class="checklist-desc">
                            Problema de pesquisa explicitamente situado no contexto empírico e sociopolítico do Sul e Extremo Sul da Bahia (Porto Seguro, Eunápolis, Teixeira de Freitas, Itamaraju, Ilhéus, etc.), investigando a eficácia concreta das instituições e direitos, superando o dogmatismo exegético abstrato.
                        </p>
                    </div>
                </div>

                <div class="checklist-item" tabindex="0" role="checkbox" aria-checked="false" aria-label="8. Diálogo com a Bibliografia Obrigatória da Linha 1">
                    <div class="checklist-indicator">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="checklist-body">
                        <div class="checklist-item-title">
                            <span>8. Diálogo com a Bibliografia Obrigatória da Linha 1</span>
                            <span class="checklist-tag">Referencial Teórico</span>
                        </div>
                        <p class="checklist-desc">
                            Articulação teórica com ao menos uma das obras obrigatórias da Linha 1 do Edital 2026/2027: Brunet &amp; Bucci (governança pública e arranjos institucionais), Ailton Krenak (pensamento socioambiental e decolonial) e Roberto Rabbani (função socioambiental e tributação).
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Painel Interativo de Propostas de Políticas Habitacionais - Profa. Dra. Maria do Carmo Rebouças -->
        <div id="sec-propostas-habitacao" class="housing-proposals-container" style="scroll-margin-top: 28px;">
            <div class="housing-header">
                <span class="housing-tag">Linha 1 — Estado, Instituições e Governança | Profa. Dra. Maria do Carmo Rebouças</span>
                <h3 class="housing-title">Dossiê de Propostas de Anteprojeto: Políticas Habitacionais e Direito à Cidade</h3>
                <p class="housing-subtitle">
                    Estruturação metodológica e empírica fundamentada nas dinâmicas territoriais do Extremo Sul da Bahia, nos relatórios da Comissão Regional de Soluções Fundiárias do TJBA (Decreto Judiciário nº 367/2024), na atuação da Defensoria Pública da Bahia (Projeto Solo Cidadão) e na execução municipal da REURB (Lei nº 13.465/2017). Selecione uma das 3 opções abaixo:
                </p>
            </div>

            <!-- Botões das 3 Opções -->
            <div class="housing-tabs-bar" role="tablist" aria-label="Seletor de Propostas Habitacionais">
                <button type="button" id="tab-opcao-1" class="housing-tab-btn active" role="tab" aria-selected="true" aria-controls="painel-opcao-1" onclick="selecionarOpcaoHabitacional(1)">
                    <span class="tab-num">Opção 1</span>
                    <span class="tab-label">REURB-S no Baianão (DPE/BA)</span>
                </button>
                <button type="button" id="tab-opcao-2" class="housing-tab-btn" role="tab" aria-selected="false" aria-controls="painel-opcao-2" onclick="selecionarOpcaoHabitacional(2)">
                    <span class="tab-num">Opção 2</span>
                    <span class="tab-label">Mediação TJBA &amp; CIDH (Trancoso)</span>
                </button>
                <button type="button" id="tab-opcao-3" class="housing-tab-btn" role="tab" aria-selected="false" aria-controls="painel-opcao-3" onclick="selecionarOpcaoHabitacional(3)">
                    <span class="tab-num">Opção 3</span>
                    <span class="tab-label">REURB-E vs. REURB-S na Orla</span>
                </button>
            </div>

            <!-- Painel Opção 1 -->
            <div id="painel-opcao-1" class="housing-option-panel" role="tabpanel" aria-labelledby="tab-opcao-1">
                <div class="option-badge-row">
                    <span class="option-meta-badge">Linha 1: Estado, Instituições e Governança</span>
                    <span class="option-meta-badge gold">Orientadora: Profa. Dra. Maria do Carmo Rebouças (2 vagas)</span>
                    <span class="option-meta-badge wine">Foco: REURB-S e Direito à Cidade</span>
                </div>
                <h4 class="option-title-text">
                    Entre o Título Registral e a Integração Urbana: Arranjos Institucionais da REURB-S no Complexo Baianão e a Garantia do Direito à Cidade em Porto Seguro
                </h4>
                <div class="option-grid-fields">
                    <div class="option-field">
                        <span class="option-field-label">Problema de Pesquisa</span>
                        <p class="option-field-content">
                            Em que medida os arranjos institucionais do programa municipal "Esta Casa é Minha" (Lei nº 13.465/2017) nos oito subnúcleos do Complexo Frei Calixto (Baianão) asseguram a integração urbanística e ambiental plena recomendada pelo projeto "Solo Cidadão" da DPE/BA, superando a mera regularização cartorária e mitigando o racismo ambiental?
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Hipótese de Trabalho</span>
                        <p class="option-field-content">
                            A política municipal de regularização confere segurança jurídica registral individual (titulação formal), mas apresenta gargalos de coordenação intergovernamental na entrega de saneamento, contenção de encostas e equipamentos sociais, perpetuando a vulnerabilidade socioambiental e a segregação racial da maior periferia da Costa do Descobrimento.
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Objeto Empírico &amp; Campo</span>
                        <p class="option-field-content">
                            Processos de REURB-S na Secretaria Municipal de Habitação e Regularização Fundiária (SEHAB) de Porto Seguro nos subnúcleos do Baianão (Mercado do Povo, Areial, Casas Novas, etc.); atuação da Defensoria Pública da Bahia (DPE/BA) pelo projeto "Solo Cidadão"; e Inquéritos Civis da Promotoria de Habitação e Urbanismo do MPBA.
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Marco Teórico &amp; Edital</span>
                        <p class="option-field-content">
                            <strong>Maria Paula Dallari Bucci:</strong> Arranjos institucionais e capacidades estatais em políticas públicas territoriais.<br>
                            <strong>Maria do Carmo Rebouças:</strong> Teoria crítica dos direitos humanos, direito antidiscriminatório e Observatório ODS 18.<br>
                            <strong>Ailton Krenak:</strong> Crítica ontológica à mercantilização do solo e aos modos de habitar.
                        </p>
                    </div>
                    <div class="option-field full-width">
                        <span class="option-field-label">Metodologia e Procedimentos (24 meses)</span>
                        <p class="option-field-content">
                            Abordagem qualitativa com pesquisa documental em decretos, certidões de regularização fundiária (CRFs) e relatórios socioeconômicos da SEHAB; análise de dados cartorários de títulos emitidos; análise de conteúdo dos TACs do MPBA; e entrevistas semiestruturadas com gestores da SEHAB, defensores públicos da comarca e lideranças comunitárias dos bairros Areial e Mercado do Povo.
                        </p>
                    </div>
                </div>
                <button type="button" id="btn-copiar-1" class="option-copy-btn" onclick="copiarDossie(1)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    Copiar Dossiê Completo da Opção 1
                </button>
            </div>

            <!-- Painel Opção 2 -->
            <div id="painel-opcao-2" class="housing-option-panel" style="display:none;" role="tabpanel" aria-labelledby="tab-opcao-2">
                <div class="option-badge-row">
                    <span class="option-meta-badge">Linha 1: Estado, Instituições e Governança</span>
                    <span class="option-meta-badge gold">Orientadora: Profa. Dra. Maria do Carmo Rebouças (2 vagas)</span>
                    <span class="option-meta-badge wine">Foco: Sistema de Justiça e Parâmetros Interamericanos</span>
                </div>
                <h4 class="option-title-text">
                    Mediação Judicial de Conflitos Fundiários Urbanos e Controle de Convencionalidade: A Atuação da Comissão Regional de Soluções Fundiárias do TJBA no Extremo Sul da Bahia
                </h4>
                <div class="option-grid-fields">
                    <div class="option-field">
                        <span class="option-field-label">Problema de Pesquisa</span>
                        <p class="option-field-content">
                            Como a Comissão Regional de Soluções Fundiárias do TJBA (Resolução CNJ nº 510/2023 e Decreto Judiciário nº 367/2024) tem articulado os parâmetros internacionais de direitos humanos sobre a proibição de despejos forçados arbitrários nas visitas técnicas e processos de mediação de ocupações coletivas urbanas nas comarcas de Porto Seguro e Eunápolis?
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Hipótese de Trabalho</span>
                        <p class="option-field-content">
                            Embora as "Caravanas Regionais" do TJBA promovam mediação qualificada que evita reintegrações violentas imediatas, o sistema de justiça local enfrenta barreiras para efetivar soluções habitacionais perenes, decorrentes da carência de áreas públicas reservadas para habitação de interesse social nos municípios da região.
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Objeto Empírico &amp; Campo</span>
                        <p class="option-field-content">
                            Relatórios técnicos e atas de mediação da Comissão Regional de Soluções Fundiárias (CRSF/TJBA) nas comarcas polo, com ênfase nas visitas à área central de Trancoso (agosto/2026) e ao assentamento Baixa Verde em Eunápolis; atuação conjunta com a DPE/BA, CEAMA/MPBA e comissões do CNJ.
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Marco Teórico &amp; Edital</span>
                        <p class="option-field-content">
                            <strong>Maria do Carmo Rebouças:</strong> Controle de convencionalidade, Sistema Interamericano de Direitos Humanos (SIDH/OEA) e grupo de pesquisa "Usos Emancipatórios do Direito".<br>
                            <strong>Maria Paula Dallari Bucci:</strong> O Judiciário como ator de arranjos institucionais multinível.<br>
                            <strong>Roberto Rabbani:</strong> A primazia da posse coletiva para moradia frente ao direito formal de propriedade.
                        </p>
                    </div>
                    <div class="option-field full-width">
                        <span class="option-field-label">Metodologia e Procedimentos (24 meses)</span>
                        <p class="option-field-content">
                            Estudo de casos múltiplos comparativos (ocupação central de Trancoso vs. ocupação Baixa Verde/Eunápolis). Análise documental dos autos no PJe do TJBA e das atas da CRSF; levantamento de decisões à luz dos precedentes da Corte IDH e do Comitê DESC; entrevistas com magistrados da comissão fundiária e defensores públicos estaduais.
                        </p>
                    </div>
                </div>
                <button type="button" id="btn-copiar-2" class="option-copy-btn" onclick="copiarDossie(2)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h6"></path></svg>
                    Copiar Dossiê Completo da Opção 2
                </button>
            </div>

            <!-- Painel Opção 3 -->
            <div id="painel-opcao-3" class="housing-option-panel" style="display:none;" role="tabpanel" aria-labelledby="tab-opcao-3">
                <div class="option-badge-row">
                    <span class="option-meta-badge">Linha 1: Estado, Instituições e Governança</span>
                    <span class="option-meta-badge gold">Orientadora: Profa. Dra. Maria do Carmo Rebouças (2 vagas)</span>
                    <span class="option-meta-badge wine">Foco: Gentrificação, REURB-E vs. REURB-S</span>
                </div>
                <h4 class="option-title-text">
                    A Dupla Face da Regularização Fundiária na Costa do Descobrimento: Assimetrias Institucionais entre a REURB-Específica e a REURB-Social sob a Perspectiva do Direito Antidiscriminatório
                </h4>
                <div class="option-grid-fields">
                    <div class="option-field">
                        <span class="option-field-label">Problema de Pesquisa</span>
                        <p class="option-field-content">
                            De que forma a aplicação concomitante da REURB-E (voltada a ocupações de média e alta renda e empreendimentos turísticos) e da REURB-S (voltada a populações vulneráveis) pela gestão municipal de Porto Seguro expressa uma distribuição assimétrica de recursos institucionais, favorecendo a gentrificação dos distritos costeiros de Trancoso e Arraial d'Ajuda?
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Hipótese de Trabalho</span>
                        <p class="option-field-content">
                            A celeridade dos procedimentos de REURB-E — impulsionada pelo mercado imobiliário turístico — contrasta com a morosidade e precariedade técnica da REURB-S nas áreas periféricas e nas comunidades tradicionais costeiras, consolidando um padrão de "justiça urbanística de duas velocidades" incompatível com o direito antidiscriminatório e com a função social da posse.
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Objeto Empírico &amp; Campo</span>
                        <p class="option-field-content">
                            Decretos de instauração e certidões de REURB publicados no Diário Oficial de Porto Seguro (2020–2026), confrontando a tramitação em Trancoso (Pindorama, Xandó, centro) e Arraial d'Ajuda com o Complexo Baianão; autos de Ações Civis Públicas e representações do MPBA e DPE/BA sobre empresas privadas de regularização.
                        </p>
                    </div>
                    <div class="option-field">
                        <span class="option-field-label">Marco Teórico &amp; Edital</span>
                        <p class="option-field-content">
                            <strong>Maria do Carmo Rebouças:</strong> Projeto de pesquisa "Estudos Críticos do Constitucionalismo e do Desenvolvimento", racismo institucional e pluralismo contra-hegemônico.<br>
                            <strong>Maria Paula Dallari Bucci:</strong> Arranjos regulatórios urbanos e risco de captura corporativa das agências estatais.<br>
                            <strong>Ailton Krenak:</strong> A expropriação predatória de territórios comunitários pela economia de consumo turístico.
                        </p>
                    </div>
                    <div class="option-field full-width">
                        <span class="option-field-label">Metodologia e Procedimentos (24 meses)</span>
                        <p class="option-field-content">
                            Mapeamento quanti-qualitativo de prazos de tramitação via Diário Oficial de Porto Seguro; análise da matriz contratual de empresas privadas credenciadas; exame de inquéritos civis do MPBA; e entrevistas com membros do CONCIDADE e moradores tradicionais de Trancoso.
                        </p>
                    </div>
                </div>
                <button type="button" id="btn-copiar-3" class="option-copy-btn" onclick="copiarDossie(3)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h6"></path></svg>
                    Copiar Dossiê Completo da Opção 3
                </button>
            </div>
        </div>

        <div class="table-responsive">
            <table class="academic-table" aria-label="Matriz de alinhamento estratégico entre tema e orientador">
                <thead>
                    <tr>
                        <th>Eixo Temático do Anteprojeto</th>
                        <th>Orientador(a) Recomendado(a)</th>
                        <th>Linha de Pesquisa</th>
                        <th>Conceitos-Chave e Obras de Conexão</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Acesso à Justiça, Discriminação e Judiciário</strong></td>
                        <td>Profa. Dra. Carolina Bessa / Profa. Dra. Maria do Carmo Rebouças</td>
                        <td>Linha 1</td>
                        <td>Res. 203/CNJ, igualdade substantiva, descolonização do direito, ações afirmativas na magistratura.</td>
                    </tr>
                    <tr>
                        <td><strong>Tributação Ambiental, Propriedade e Função Social</strong></td>
                        <td>Prof. Dr. Roberto Muhajir Rahnemay Rabbani</td>
                        <td>Linha 1</td>
                        <td>Função socioambiental da propriedade rural, tributação ecológica, pluralismo jurídico, camponeses de Vale Verde.</td>
                    </tr>
                    <tr>
                        <td><strong>Audiências de Custódia e Meios Consensuais (CEJUSCs)</strong></td>
                        <td>Prof. Dr. Herbert Toledo Martins</td>
                        <td>Colaborador / Linha 1</td>
                        <td>Sociologia do direito, rotinas decisórias em flagrante, eficácia qualitativa da mediação em Teixeira de Freitas.</td>
                    </tr>
                    <tr>
                        <td><strong>Conflitos Fundiários e Direitos Originários Indígenas</strong></td>
                        <td>Prof. Dr. Spensy Pimentel / Prof. Dr. Francisco Cancela</td>
                        <td>Linha 1 / Linha 4</td>
                        <td>Art. 231 CF/88, retomadas territoriais Pataxó/Tupinambá, laudos antropológicos, decolonialidade.</td>
                    </tr>
                    <tr>
                        <td><strong>Trabalho Escravo Contemporâneo e Discurso de Estado</strong></td>
                        <td>Profa. Dra. Fernanda Luzia Lunkes</td>
                        <td>Linha 3</td>
                        <td>Análise do discurso materialista, produção da norma trabalhista, violações estruturais de direitos fundamentais.</td>
                    </tr>
                </tbody>
            </table>
        </div>

    </section>
    </div> <!-- /pane-dicas -->
""")

# Footer
out.append("""
    <footer class="editorial-footer">
        <p>
            <strong>Universidade Federal do Sul da Bahia (UFSB)</strong> — Programa de Pós-Graduação em Estado e Sociedade (PPGES)<br>
            Campus Sosígenes Costa — Rodovia Porto Seguro-Eunápolis, BR-367, Km 10, Porto Seguro/BA.<br>
            Base documental: 151 defesas homologadas (2019–2026) | Dados consolidados para o Edital PROPPG nº 30/2026.
        </p>
    </footer>

</div>

<script>
    // State
    let filtroTipoAtual = 'todos';
    let filtroPdfAtual = 'todos';
    let paginaAtual = 1;
    let itensPorPagina = 12;
    let resultadosFiltrados = [];

    // Mapeamento semântico de âncoras para abas
    const MAPA_ANCHORS_TAB = {
        'sec-cronograma': 'cronograma',
        'sec-encontro': 'cronograma',
        'sec-estatisticas': 'cronograma',
        'sec-politicas': 'cronograma',
        'sec-professores': 'professores',
        'sec-catalogo': 'catalogo',
        'sec-dicas': 'dicas',
        'sec-checklist': 'dicas',
        'sec-propostas-habitacao': 'dicas',
        'sec-propostas': 'dicas'
    };

    function normalizarTexto(str) {
        if (!str) return '';
        return str
            .normalize('NFD')
            .replace(/[\\u0300-\\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function navegarAbaPrincipal(tabName, subTargetId, atualizarHash = true) {
        const tabsValidas = ['cronograma', 'professores', 'catalogo', 'dicas'];
        if (!tabsValidas.includes(tabName)) {
            tabName = 'cronograma';
        }

        // Alternar visibilidade dos painéis de conteúdo
        tabsValidas.forEach(t => {
            const pane = document.getElementById('pane-' + t);
            const btn = document.getElementById('tabBtn-' + t);
            const ativo = (t === tabName);
            if (pane) {
                pane.style.display = ativo ? 'block' : 'none';
                pane.classList.toggle('active', ativo);
            }
            if (btn) {
                btn.classList.toggle('active', ativo);
                btn.setAttribute('aria-selected', ativo ? 'true' : 'false');
            }
        });

        // Rolagem e Hash
        if (subTargetId) {
            const el = document.getElementById(subTargetId);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            if (atualizarHash && history.replaceState) {
                history.replaceState(null, '', '#' + subTargetId);
            }
        } else {
            const navBar = document.getElementById('mainTabsNav');
            if (navBar && window.scrollY > navBar.offsetTop) {
                navBar.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            if (atualizarHash && history.replaceState) {
                history.replaceState(null, '', '#pane-' + tabName);
            }
        }
    }

    function setFiltroTipo(tipo, btn) {
        filtroTipoAtual = tipo;
        document.querySelectorAll('.filter-btn[data-tipo]').forEach(b => {
            const isActive = b.getAttribute('data-tipo') === tipo;
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
        filtrarAcervo(true);
    }

    function setFiltroPdf(pdfStatus, btn) {
        filtroPdfAtual = pdfStatus;
        document.querySelectorAll('.filter-btn[data-pdf]').forEach(b => {
            const isActive = b.getAttribute('data-pdf') === pdfStatus;
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
        filtrarAcervo(true);
    }

    function limparBusca() {
        const input = document.getElementById('searchInput');
        input.value = '';
        document.getElementById('searchClearBtn').style.display = 'none';
        input.focus();
        filtrarAcervo(true);
    }

    function resetarFiltros() {
        filtroTipoAtual = 'todos';
        filtroPdfAtual = 'todos';
        document.getElementById('searchInput').value = '';
        document.getElementById('searchClearBtn').style.display = 'none';
        document.getElementById('yearSelect').value = 'todos';
        document.getElementById('advisorSelect').value = 'todos';
        
        document.querySelectorAll('.filter-btn[data-tipo]').forEach(b => {
            const isActive = b.getAttribute('data-tipo') === 'todos';
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
        document.querySelectorAll('.filter-btn[data-pdf]').forEach(b => {
            const isActive = b.getAttribute('data-pdf') === 'todos';
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        filtrarAcervo(true);
    }

    function filtrarPorDocente(nomeDocente) {
        // Redireciona para a Aba 3 (Catálogo)
        navegarAbaPrincipal('catalogo', 'sec-catalogo', false);

        const advisorSelect = document.getElementById('advisorSelect');
        const normTarget = normalizarTexto(nomeDocente);
        
        let foundVal = null;
        for (let opt of advisorSelect.options) {
            if (opt.value === 'todos') continue;
            const normOpt = normalizarTexto(opt.value);
            if (normOpt === normTarget || normOpt.includes(normTarget) || normTarget.includes(normOpt)) {
                foundVal = opt.value;
                break;
            }
        }
        
        // Reset type, pdf, year and search input
        filtroTipoAtual = 'todos';
        filtroPdfAtual = 'todos';
        document.querySelectorAll('.filter-btn[data-tipo]').forEach(b => {
            const isActive = b.getAttribute('data-tipo') === 'todos';
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
        document.querySelectorAll('.filter-btn[data-pdf]').forEach(b => {
            const isActive = b.getAttribute('data-pdf') === 'todos';
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
        document.getElementById('yearSelect').value = 'todos';
        document.getElementById('searchInput').value = '';
        document.getElementById('searchClearBtn').style.display = 'none';

        const counter = document.getElementById('catalogCounter');
        const noResults = document.getElementById('noResultsMsg');
        const noResultsTitle = document.getElementById('noResultsTitle');
        const noResultsDesc = document.getElementById('noResultsDesc');

        if (foundVal) {
            advisorSelect.value = foundVal;
            filtrarAcervo(true);
        } else {
            // Professor without completed defenses in 2019-2026 catalog
            advisorSelect.value = 'todos';
            resultadosFiltrados = [];
            document.querySelectorAll('.thesis-entry').forEach(e => e.style.display = 'none');
            document.querySelectorAll('.year-group').forEach(g => g.style.display = 'none');
            renderizarControlesPaginacao(0);
            
            noResults.style.display = 'block';
            noResultsTitle.innerText = 'Orientações Ativas em Andamento no PPGES';
            noResultsDesc.innerHTML = 'O(A) docente <strong>' + nomeDocente + '</strong> atua na Linha 1 com vagas abertas no Edital PROPPG nº 30/2026. Suas primeiras turmas estão em andamento e suas pesquisas ainda não possuem defesas concluídas registradas no acervo histórico 2019–2026.';
            counter.innerText = 'Docente com turmas em andamento no Edital 2026 (sem defesas históricas concluídas no acervo 2019–2026).';
        }
        
        const secCatalogo = document.getElementById('sec-catalogo');
        if (secCatalogo) {
            secCatalogo.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function toggleTodosResumos(abrir) {
        document.querySelectorAll('.thesis-entry').forEach(entry => {
            if (entry.style.display !== 'none') {
                const details = entry.querySelector('.thesis-abstract-details');
                if (details) {
                    details.open = abrir;
                }
            }
        });
    }

    function filtrarAcervo(resetarPagina = true) {
        if (resetarPagina) {
            paginaAtual = 1;
        }

        const rawQuery = document.getElementById('searchInput').value;
        const normQuery = normalizarTexto(rawQuery);
        const clearBtn = document.getElementById('searchClearBtn');
        if (clearBtn) clearBtn.style.display = rawQuery.length > 0 ? 'block' : 'none';

        // Tokenize query into separate words for flexible multi-word matching
        const queryTokens = normQuery.split(/\\s+/).filter(Boolean);

        const anoFiltro = document.getElementById('yearSelect').value;
        const orientadorFiltro = document.getElementById('advisorSelect').value;
        const normOrientadorFiltro = normalizarTexto(orientadorFiltro);

        const entries = document.querySelectorAll('.thesis-entry');
        resultadosFiltrados = [];
        let dissertacoesVisiveis = 0;
        let tesesVisiveis = 0;

        entries.forEach(entry => {
            const entryTipo = entry.getAttribute('data-tipo');
            const entryPdf = entry.getAttribute('data-pdf');
            const entryAno = entry.getAttribute('data-ano');
            const entryOrientador = entry.getAttribute('data-orientador') || '';
            const normEntryOrientador = normalizarTexto(entryOrientador);
            const searchData = entry.getAttribute('data-search') || '';

            // Match conditions
            const matchTipo = (filtroTipoAtual === 'todos') || (entryTipo === filtroTipoAtual);
            const matchPdf = (filtroPdfAtual === 'todos') || (entryPdf === filtroPdfAtual);
            const matchAno = (anoFiltro === 'todos') || (entryAno === anoFiltro);
            const matchOrientador = (orientadorFiltro === 'todos') || (normEntryOrientador === normOrientadorFiltro);
            
            // All tokens must be present in searchData
            const matchQuery = (queryTokens.length === 0) || queryTokens.every(token => searchData.includes(token));

            if (matchTipo && matchPdf && matchAno && matchOrientador && matchQuery) {
                resultadosFiltrados.push(entry);
                if (entryTipo === 'dissertacao') dissertacoesVisiveis++;
                if (entryTipo === 'tese') tesesVisiveis++;
            } else {
                entry.style.display = 'none';
            }
        });

        const total = resultadosFiltrados.length;
        const counter = document.getElementById('catalogCounter');
        const noResults = document.getElementById('noResultsMsg');
        const noResultsTitle = document.getElementById('noResultsTitle');
        const noResultsDesc = document.getElementById('noResultsDesc');

        if (total === 0) {
            if (noResults) {
                noResults.style.display = 'block';
                noResultsTitle.innerText = 'Nenhum trabalho localizado com os critérios informados.';
                noResultsDesc.innerText = 'Tente utilizar termos mais genéricos ou clique no botão abaixo para redefinir os filtros.';
            }
            if (counter) counter.innerText = 'Nenhum trabalho localizado com os critérios informados.';
        } else {
            if (noResults) noResults.style.display = 'none';
            if (counter) {
                if (rawQuery === '' && filtroTipoAtual === 'todos' && filtroPdfAtual === 'todos' && anoFiltro === 'todos' && orientadorFiltro === 'todos') {
                    counter.innerText = 'Exibindo todas as 151 defesas cadastradas (' + dissertacoesVisiveis + ' dissertações e ' + tesesVisiveis + ' teses).';
                } else {
                    let partes = [];
                    if (filtroTipoAtual !== 'todos') partes.push(filtroTipoAtual === 'dissertacao' ? 'Dissertações' : 'Teses');
                    if (filtroPdfAtual !== 'todos') partes.push(filtroPdfAtual === 'com-pdf' ? 'Com PDF' : 'Em homologação');
                    if (anoFiltro !== 'todos') partes.push('Ano ' + anoFiltro);
                    if (orientadorFiltro !== 'todos') partes.push('Orientador(a): ' + orientadorFiltro);
                    if (rawQuery.trim() !== '') partes.push('Termo: "' + rawQuery.trim() + '"');

                    const pluralTrabalho = total === 1 ? 'trabalho encontrado' : 'trabalhos encontrados';
                    counter.innerText = 'Exibindo ' + total + ' ' + pluralTrabalho + ' (' + dissertacoesVisiveis + ' dissertações e ' + tesesVisiveis + ' teses) [' + partes.join(', ') + '].';
                }
            }
        }

        aplicarPaginacaoVisivel();
    }

    function aplicarPaginacaoVisivel() {
        const total = resultadosFiltrados.length;

        if (total === 0) {
            document.querySelectorAll('.year-group').forEach(g => g.style.display = 'none');
            renderizarControlesPaginacao(0);
            return;
        }

        let inicioIdx = 0;
        let fimIdx = total;

        if (itensPorPagina !== 'todas') {
            const limite = parseInt(itensPorPagina, 10);
            const totalPaginas = Math.ceil(total / limite);
            if (paginaAtual > totalPaginas) {
                paginaAtual = totalPaginas;
            }
            if (paginaAtual < 1) {
                paginaAtual = 1;
            }
            inicioIdx = (paginaAtual - 1) * limite;
            fimIdx = Math.min(inicioIdx + limite, total);
        }

        resultadosFiltrados.forEach((entry, idx) => {
            if (idx >= inicioIdx && idx < fimIdx) {
                entry.style.display = 'block';
            } else {
                entry.style.display = 'none';
            }
        });

        // Alterna cabeçalhos de ano de acordo com a visibilidade dos cards filhos na página ativa
        document.querySelectorAll('.year-group').forEach(group => {
            const hasVisible = Array.from(group.querySelectorAll('.thesis-entry')).some(e => e.style.display !== 'none');
            group.style.display = hasVisible ? 'block' : 'none';
        });

        renderizarControlesPaginacao(total);
    }

    function renderizarControlesPaginacao(total) {
        const topBar = document.getElementById('paginationBarTop');
        const bottomBar = document.getElementById('paginationBarBottom');
        if (!topBar && !bottomBar) return;

        if (total === 0) {
            if (topBar) { topBar.innerHTML = ''; topBar.style.display = 'none'; }
            if (bottomBar) { bottomBar.innerHTML = ''; bottomBar.style.display = 'none'; }
            return;
        }

        let totalPaginas = 1;
        let inicioNum = 1;
        let fimNum = total;

        if (itensPorPagina !== 'todas') {
            const limite = parseInt(itensPorPagina, 10);
            totalPaginas = Math.ceil(total / limite);
            inicioNum = (paginaAtual - 1) * limite + 1;
            fimNum = Math.min(paginaAtual * limite, total);
        }

        let paginasHtml = '';
        if (totalPaginas > 1) {
            const desabAnt = paginaAtual === 1 ? ' disabled' : '';
            paginasHtml += '<button type="button" class="pg-btn prev-btn"' + desabAnt + ' onclick="mudarPagina(' + (paginaAtual - 1) + ')" aria-label="Página anterior">« Anterior</button>';

            let paginasParaMostrar = [];
            if (totalPaginas <= 7) {
                for (let p = 1; p <= totalPaginas; p++) paginasParaMostrar.push(p);
            } else {
                paginasParaMostrar.push(1);
                if (paginaAtual > 3) paginasParaMostrar.push('...');
                const inicioMeio = Math.max(2, paginaAtual - 1);
                const fimMeio = Math.min(totalPaginas - 1, paginaAtual + 1);
                for (let p = inicioMeio; p <= fimMeio; p++) {
                    if (!paginasParaMostrar.includes(p)) paginasParaMostrar.push(p);
                }
                if (paginaAtual < totalPaginas - 2) paginasParaMostrar.push('...');
                if (!paginasParaMostrar.includes(totalPaginas)) paginasParaMostrar.push(totalPaginas);
            }

            paginasParaMostrar.forEach(p => {
                if (p === '...') {
                    paginasHtml += '<span style="padding: 4px 6px; color: var(--text-secondary); font-size: 13px;">…</span>';
                } else {
                    const ativo = (p === paginaAtual) ? ' active' : '';
                    paginasHtml += '<button type="button" class="pg-btn' + ativo + '" onclick="mudarPagina(' + p + ')" aria-label="Ir para página ' + p + '">' + p + '</button>';
                }
            });

            const desabProx = paginaAtual === totalPaginas ? ' disabled' : '';
            paginasHtml += '<button type="button" class="pg-btn next-btn"' + desabProx + ' onclick="mudarPagina(' + (paginaAtual + 1) + ')" aria-label="Próxima página">Próxima »</button>';
        }

        const opcoesItens = [12, 24, 48, 'todas'];
        let seletorItensHtml = '<span style="font-size: 12.5px; color: var(--text-secondary); font-weight: 600;">Por página:</span> ';
        opcoesItens.forEach(opt => {
            const isCurrent = (opt === itensPorPagina || (opt === 'todas' && itensPorPagina === 'todas') || (opt.toString() === itensPorPagina.toString()));
            const btnClass = isCurrent ? 'pg-btn active' : 'pg-btn';
            const label = (opt === 'todas') ? 'Todas' : opt;
            seletorItensHtml += '<button type="button" class="' + btnClass + '" style="min-width: 32px; padding: 4px 8px; font-size: 12px;" onclick="alterarItensPorPagina(\\'' + opt + '\\')">' + label + '</button> ';
        });

        const metaHtml = 'Mostrando <strong>' + inicioNum + '–' + fimNum + '</strong> de <strong>' + total + '</strong> defesas';

        const htmlCompleto = '' +
            '<div class="pagination-meta">' + metaHtml + '</div>' +
            '<div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap;">' + seletorItensHtml + '</div>' +
            '<div class="pagination-buttons" role="navigation" aria-label="Paginação do catálogo">' + paginasHtml + '</div>';

        if (topBar) {
            topBar.innerHTML = htmlCompleto;
            topBar.style.display = 'flex';
        }
        if (bottomBar) {
            bottomBar.innerHTML = htmlCompleto;
            bottomBar.style.display = 'flex';
        }
    }

    function mudarPagina(novaPagina) {
        paginaAtual = novaPagina;
        aplicarPaginacaoVisivel();
        const secCatalogo = document.getElementById('sec-catalogo');
        if (secCatalogo) {
            secCatalogo.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function alterarItensPorPagina(qtd) {
        itensPorPagina = (qtd === 'todas') ? 'todas' : parseInt(qtd, 10);
        paginaAtual = 1;
        aplicarPaginacaoVisivel();
    }
    // Alternar e exibir proposta habitacional selecionada
    function selecionarOpcaoHabitacional(num) {
        navegarAbaPrincipal('dicas', 'sec-propostas-habitacao', false);
        for (let i = 1; i <= 3; i++) {
            const tab = document.getElementById('tab-opcao-' + i);
            const panel = document.getElementById('painel-opcao-' + i);
            if (tab && panel) {
                if (i === num) {
                    tab.classList.add('active');
                    tab.setAttribute('aria-selected', 'true');
                    panel.style.display = 'block';
                    panel.classList.add('active');
                } else {
                    tab.classList.remove('active');
                    tab.setAttribute('aria-selected', 'false');
                    panel.style.display = 'none';
                    panel.classList.remove('active');
                }
            }
        }
        const target = document.getElementById('sec-propostas-habitacao');
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // Copiar dossie completo da proposta para a area de transferencia
    function copiarDossie(opcaoNum) {
        let texto = "";
        if (opcaoNum === 1) {
            texto = "ANTEPROJETO DE PESQUISA (PPGES/UFSB - EDITAL PROPPG Nº 30/2026)\n" +
                    "Linha 1: Estado, Instituições e Governança\n" +
                    "Orientadora Pretendida: Profa. Dra. Maria do Carmo Rebouças da Cruz Ferreira dos Santos\n\n" +
                    "TÍTULO PRELIMINAR:\n" +
                    "Entre o Título Registral e a Integração Urbana: Arranjos Institucionais da REURB-S no Complexo Baianão e a Garantia do Direito à Cidade em Porto Seguro\n\n" +
                    "PROBLEMA DE PESQUISA:\n" +
                    "Em que medida os arranjos institucionais do programa municipal 'Esta Casa é Minha' (Lei nº 13.465/2017) nos oito subnúcleos do Complexo Frei Calixto (Baianão) asseguram a integração urbanística e ambiental plena recomendada pelo projeto 'Solo Cidadão' da DPE/BA, superando a mera regularização cartorária e mitigando o racismo ambiental?\n\n" +
                    "HIPÓTESE DE TRABALHO:\n" +
                    "A política municipal de regularização confere segurança jurídica registral individual (titulação formal), mas apresenta gargalos de coordenação intergovernamental na entrega de saneamento, contenção de encostas e equipamentos sociais, perpetuando a vulnerabilidade socioambiental e a segregação racial da maior periferia da Costa do Descobrimento.\n\n" +
                    "OBJETO EMPÍRICO E RECORTE:\n" +
                    "Processos administrativos de REURB-S na SEHAB de Porto Seguro no Complexo Baianão (Mercado do Povo, Areial, Casas Novas, etc.); atuação da DPE/BA pelo projeto 'Solo Cidadão'; e Inquéritos Civis da Promotoria de Habitação e Urbanismo do MPBA.\n\n" +
                    "MARCO TEÓRICO:\n" +
                    "- Maria Paula Dallari Bucci (Direito e Políticas Públicas; arranjos institucionais e capacidades estatais).\n" +
                    "- Maria do Carmo Rebouças (Teoria crítica dos direitos humanos, direito antidiscriminatório e Observatório ODS 18).\n" +
                    "- Ailton Krenak (Crítica ontológica à mercantilização do solo).\n\n" +
                    "METODOLOGIA:\n" +
                    "Pesquisa empírico-qualitativa documental (SEHAB, Cartório de Registro de Imóveis, MPBA) e entrevistas semiestruturadas com gestores municipais, defensores públicos e lideranças comunitárias locais.\n\n" +
                    "DECLARAÇÃO DE INTEGRIDADE SOBRE IA:\n" +
                    "Em conformidade com a Portaria CNPq nº 2.664/2026, declara-se que as ferramentas de inteligência artificial foram empregadas estritamente como suporte técnico-revisório, preservando-se a autoria intelectual originária da pesquisa.";
        } else if (opcaoNum === 2) {
            texto = "ANTEPROJETO DE PESQUISA (PPGES/UFSB - EDITAL PROPPG Nº 30/2026)\n" +
                    "Linha 1: Estado, Instituições e Governança\n" +
                    "Orientadora Pretendida: Profa. Dra. Maria do Carmo Rebouças da Cruz Ferreira dos Santos\n\n" +
                    "TÍTULO PRELIMINAR:\n" +
                    "Mediação Judicial de Conflitos Fundiários Urbanos e Controle de Convencionalidade: A Atuação da Comissão Regional de Soluções Fundiárias do TJBA no Extremo Sul da Bahia\n\n" +
                    "PROBLEMA DE PESQUISA:\n" +
                    "Como a Comissão Regional de Soluções Fundiárias do TJBA (Resolução CNJ nº 510/2023 e Decreto Judiciário nº 367/2024) tem articulado os parâmetros internacionais de direitos humanos sobre a proibição de despejos forçados arbitrários nas visitas técnicas e processos de mediação de ocupações coletivas urbanas nas comarcas de Porto Seguro e Eunápolis?\n\n" +
                    "HIPÓTESE DE TRABALHO:\n" +
                    "Embora as 'Caravanas Regionais' do TJBA promovam mediação qualificada que evita reintegrações violentas imediatas, o sistema de justiça local enfrenta barreiras para efetivar soluções habitacionais perenes, decorrentes da carência de áreas públicas reservadas para habitação de interesse social nos municípios da região.\n\n" +
                    "OBJETO EMPÍRICO E RECORTE:\n" +
                    "Relatórios técnicos e atas de mediação da Comissão Regional de Soluções Fundiárias (CRSF/TJBA) nas comarcas polo, com ênfase nas visitas à área central de Trancoso (agosto/2026) e ao assentamento Baixa Verde em Eunápolis; atuação da DPE/BA e CEAMA/MPBA.\n\n" +
                    "MARCO TEÓRICO:\n" +
                    "- Maria do Carmo Rebouças (Controle de convencionalidade, SIDH/OEA e Usos Emancipatórios do Direito).\n" +
                    "- Maria Paula Dallari Bucci (O Judiciário como ator de arranjos institucionais).\n" +
                    "- Roberto Rabbani (Posse coletiva para moradia frente ao direito formal de propriedade).\n\n" +
                    "METODOLOGIA:\n" +
                    "Estudo de caso múltiplo comparativo (Trancoso vs. Baixa Verde/Eunápolis). Análise documental no PJe do TJBA e relatórios da CRSF; confronto com precedentes da Corte IDH e Comitê DESC; entrevistas com magistrados e defensores públicos.\n\n" +
                    "DECLARAÇÃO DE INTEGRIDADE SOBRE IA:\n" +
                    "Em conformidade com a Portaria CNPq nº 2.664/2026, declara-se que as ferramentas de inteligência artificial foram empregadas estritamente como suporte técnico-revisório, preservando-se a autoria intelectual originária da pesquisa.";
        } else if (opcaoNum === 3) {
            texto = "ANTEPROJETO DE PESQUISA (PPGES/UFSB - EDITAL PROPPG Nº 30/2026)\n" +
                    "Linha 1: Estado, Instituições e Governança\n" +
                    "Orientadora Pretendida: Profa. Dra. Maria do Carmo Rebouças da Cruz Ferreira dos Santos\n\n" +
                    "TÍTULO PRELIMINAR:\n" +
                    "A Dupla Face da Regularização Fundiária na Costa do Descobrimento: Assimetrias Institucionais entre a REURB-Específica e a REURB-Social sob a Perspectiva do Direito Antidiscriminatório\n\n" +
                    "PROBLEMA DE PESQUISA:\n" +
                    "De que forma a aplicação concomitante da REURB-E (voltada a ocupações de média e alta renda e empreendimentos turísticos) e da REURB-S (voltada a populações vulneráveis) pela gestão municipal de Porto Seguro expressa uma distribuição assimétrica de recursos institucionais, favorecendo a gentrificação dos distritos costeiros de Trancoso e Arraial d'Ajuda?\n\n" +
                    "HIPÓTESE DE TRABALHO:\n" +
                    "A celeridade dos procedimentos de REURB-E — impulsionada pelo mercado imobiliário turístico — contrasta com a morosidade e precariedade técnica da REURB-S nas áreas periféricas e nas comunidades tradicionais costeiras, consolidando um padrão de 'justiça urbanística de duas velocidades' incompatível com o direito antidiscriminatório e com a função social da posse.\n\n" +
                    "OBJETO EMPÍRICO E RECORTE:\n" +
                    "Decretos de instauração e certidões de REURB no Diário Oficial de Porto Seguro (2020–2026), confrontando a tramitação em Trancoso/Arraial d'Ajuda com o Complexo Baianão; ACPs e representações do MPBA e DPE/BA sobre empresas privadas de regularização.\n\n" +
                    "MARCO TEÓRICO:\n" +
                    "- Maria do Carmo Rebouças (Estudos Críticos do Constitucionalismo e do Desenvolvimento; racismo institucional).\n" +
                    "- Maria Paula Dallari Bucci (Arranjos regulatórios urbanos e risco de captura corporativa).\n" +
                    "- Ailton Krenak (Expropriação predatória pela economia turística).\n\n" +
                    "METODOLOGIA:\n" +
                    "Mapeamento quanti-qualitativo de prazos de tramitação via Diário Oficial de Porto Seguro; análise da matriz contratual de empresas privadas credenciadas; exame de inquéritos civis do MPBA; e entrevistas com membros do CONCIDADE e moradores tradicionais.\n\n" +
                    "DECLARAÇÃO DE INTEGRIDADE SOBRE IA:\n" +
                    "Em conformidade com a Portaria CNPq nº 2.664/2026, declara-se que as ferramentas de inteligência artificial foram empregadas estritamente como suporte técnico-revisório, preservando-se a autoria intelectual originária da pesquisa.";
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(texto).then(function() {
                const btn = document.getElementById('btn-copiar-' + opcaoNum);
                if (btn) {
                    const originalHtml = btn.innerHTML;
                    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Dossiê copiado com sucesso!';
                    btn.style.background = '#2D5A43';
                    btn.style.borderColor = '#2D5A43';
                    setTimeout(function() {
                        btn.innerHTML = originalHtml;
                        btn.style.background = '';
                        btn.style.borderColor = '';
                    }, 3000);
                }
            });
        }
    }

    // Scroll back to top behavior
    window.addEventListener('scroll', function() {
        const btn = document.getElementById('backToTopBtn');
        if (btn) {
            if (window.scrollY > 400) {
                btn.style.display = 'flex';
            } else {
                btn.style.display = 'none';
            }
        }
    });

    // Sincronização por Hash da URL
    function sincronizarAbaPorHash() {
        const rawHash = window.location.hash ? window.location.hash.substring(1) : '';
        if (!rawHash) {
            navegarAbaPrincipal('cronograma', null, false);
            return;
        }

        if (rawHash.startsWith('pane-')) {
            const tabName = rawHash.replace('pane-', '');
            navegarAbaPrincipal(tabName, null, false);
            return;
        }

        const tabMapeada = MAPA_ANCHORS_TAB[rawHash];
        if (tabMapeada) {
            navegarAbaPrincipal(tabMapeada, rawHash, false);
        } else {
            const targetEl = document.getElementById(rawHash);
            if (targetEl) {
                const panePai = targetEl.closest('.main-tab-pane');
                if (panePai && panePai.id.startsWith('pane-')) {
                    const tabNome = panePai.id.replace('pane-', '');
                    navegarAbaPrincipal(tabNome, rawHash, false);
                    return;
                }
            }
            navegarAbaPrincipal('cronograma', null, false);
        }
    }

    window.addEventListener('hashchange', sincronizarAbaPorHash);

    // Run initial setup and checklist interactions
    document.addEventListener('DOMContentLoaded', function() {
        sincronizarAbaPorHash();
        filtrarAcervo(true);
        
        document.querySelectorAll('.checklist-item').forEach(function(item) {
            function toggleItem() {
                const isChecked = item.classList.toggle('checked');
                item.setAttribute('aria-checked', isChecked ? 'true' : 'false');
            }
            item.addEventListener('click', toggleItem);
            item.addEventListener('keydown', function(e) {
                if (e.key === ' ' || e.key === 'Enter') {
                    e.preventDefault();
                    toggleItem();
                }
            });
        });

        // Intercepta cliques nos links do Sumário (TOC) para alternar abas dinamicamente
        document.querySelectorAll('.toc-list a').forEach(function(link) {
            link.addEventListener('click', function(e) {
                const targetHref = link.getAttribute('href');
                if (targetHref && targetHref.startsWith('#')) {
                    const targetId = targetHref.substring(1);
                    const tab = MAPA_ANCHORS_TAB[targetId];
                    if (tab) {
                        e.preventDefault();
                        navegarAbaPrincipal(tab, targetId, true);
                    }
                }
            });
        });
    });
</script>

</body>
</html>
""")

full_html = "".join(out)
target_path = Path("panorama_defesas_ppges_ufsb.html")
target_path.write_text(full_html, encoding="utf-8")
print(f"Generated {target_path} successfully ({len(full_html)} chars, {len(full_html.encode('utf-8'))} bytes).")

index_path = Path("index.html")
index_path.write_text(full_html, encoding="utf-8")
print(f"Mirrored to {index_path} successfully.")
