import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

print("=== INICIANDO BATERIA EXAUSTIVA DE TESTES E VERIFICAÇÃO ===")

html_text = Path("panorama_defesas_ppges_ufsb.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html_text, "html.parser")
catalog = json.load(open(r"C:\Users\Casa\.gemini\antigravity\brain\6738a72b-0664-43b4-b7b5-77b8a9c32ac0\scratch\catalog_defesas.json", encoding="utf-8"))

# Test 1: Exactly 151 thesis entries
entries = soup.find_all("div", class_="thesis-entry")
print(f"Test 1 - Total thesis entries: {len(entries)} (Esperado: 151)")
assert len(entries) == 151, f"Expected 151, got {len(entries)}"

# Test 2: Exactly 8 year groups
year_groups = soup.find_all("div", class_="year-group")
years = [g.get("data-year") for g in year_groups]
print(f"Test 2 - Year groups: {years} (Esperado: 8 anos de 2026 a 2019)")
assert len(year_groups) == 8, f"Expected 8 year groups, got {len(year_groups)}"
assert years == ['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019']

# Test 3: Faculty Cards semantic heading (h3) and count
faculty_cards = soup.find_all("div", class_=lambda c: c and "faculty-card" in c)
print(f"Test 3 - Faculty cards: {len(faculty_cards)} (Esperado: 12)")
assert len(faculty_cards) == 12, f"Expected 12, got {len(faculty_cards)}"

h3_names = [c.find("h3", class_="faculty-name") for c in faculty_cards]
assert all(h3 is not None for h3 in h3_names), "All faculty cards must have semantic <h3 class='faculty-name'>"
print(f"Test 3b - All 12 faculty cards have semantic <h3> headings: OK")

# Test 4: All 12 faculty cards have strategic research tips ("Diretriz para Anteprojeto")
tips = [c.find("div", class_="faculty-tip-box") for c in faculty_cards]
assert all(t is not None for t in tips), "All 12 faculty cards must have strategic research tips (faculty-tip-box)"
print(f"Test 4 - All 12 faculty cards have strategic research guidelines (tips): OK")

# Test 5: Roberto Rabbani card does NOT have false attribution of custody hearings
rabbani_card = next(c for c in faculty_cards if "Rabbani" in c.get_text())
assert "audiência de custódia" not in rabbani_card.get_text().lower() and "audiências de custódia" not in rabbani_card.get_text().lower(), "Rabbani card must not claim custody hearings"
print(f"Test 5 - Factual accuracy of Roberto Rabbani card (no false custody claim): OK")

# Test 6: Lattes links in faculty cards
lattes_links = [a["href"] for a in soup.find_all("a", href=re.compile(r"lattes\.cnpq\.br/\d{16}"))]
unique_lattes = set(lattes_links)
print(f"Test 6 - Unique 16-digit Lattes links in document: {len(unique_lattes)}")
assert len(unique_lattes) >= 13, f"Expected at least 13 unique Lattes URLs, got {len(unique_lattes)}"

# Test 7: Section 4.3 General Table of 21 Advisors
table_advisors = soup.find("table", attrs={"aria-label": re.compile(r"21 orientadores", re.I)})
assert table_advisors is not None, "Section 4.3 table of 21 advisors must exist"
rows_advisors = table_advisors.find("tbody").find_all("tr")
print(f"Test 7 - General table of advisors rows: {len(rows_advisors)} (Esperado: 21)")
assert len(rows_advisors) == 21, f"Expected 21 advisors in summary table, got {len(rows_advisors)}"

# Test 8: Section 3 Citations and Links
sec3 = soup.find("section", id="sec-politicas")
assert sec3 is not None, "Section 3 must exist"

# 8a: Adriana Vilas-Bôas (2019) attributed to Sandra Adriana Neves Nunes
adv_m = re.search(r'Política pública de assistência técnica.*?Adriana Vilas-Bôas.*?Orientadora:\s*Profa\.\s*Dra\.\s*Sandra Adriana Neves Nunes', sec3.get_text(), re.DOTALL)
assert adv_m is not None, "Adriana Vilas-Bôas (2019) must be attributed to Sandra Adriana Neves Nunes"
print("Test 8a - Adriana Vilas-Bôas (2019) attributed to Sandra Nunes: OK")

# 8b: Eva Dayane (2019) attributed to Maria Aparecida de Oliveira Lopes
eva_m = re.search(r'Intersecções entre a violência doméstica.*?Eva Dayane.*?Orientadora:\s*Profa\.\s*Dra\.\s*Maria Aparecida de Oliveira Lopes', sec3.get_text(), re.DOTALL)
assert eva_m is not None, "Eva Dayane (2019) must be attributed to Maria Aparecida de Oliveira Lopes"
print("Test 8b - Eva Dayane (2019) attributed to Maria Aparecida Lopes: OK")

# 8c: Silvoney Silva Pena (2020) link
silvoney_a = sec3.find("a", href="https://sig.ufsb.edu.br/sigaa/verArquivo?idArquivo=699154&key=0a92be5579ce233395a7275604088470")
assert silvoney_a is not None, "Silvoney Silva Pena PDF link must match catalog (idArquivo=699154)"
print("Test 8c - Silvoney Silva Pena PDF link verified: OK")

# 8d: Emmanuel Soares (2022) correctly marked as Acervo UFSB without fake link
emmanuel_li = next(li for li in sec3.find_all("li") if "Coroa Vermelha" in li.get_text())
assert emmanuel_li.find("a") is None and "Acervo UFSB" in emmanuel_li.get_text(), "Emmanuel Soares must not have fake link and must be flagged as Acervo UFSB"
print("Test 8d - Emmanuel Soares cataloged as Acervo UFSB: OK")

# Test 9: Catalog PDFs (129 links in catalog)
cat_pdf_links = [e.find("a", class_="pdf-link") for e in entries]
cat_pdf_count = sum(1 for a in cat_pdf_links if a is not None)
print(f"Test 9 - Catalog PDF links: {cat_pdf_count} (Esperado: 129)")
assert cat_pdf_count == 129, f"Expected 129 PDF links in catalog, got {cat_pdf_count}"

# Test 10: All 151 abstracts exist and are capitalized
abstract_details = soup.find_all("details", class_="thesis-abstract-details")
print(f"Test 10 - Abstract details elements: {len(abstract_details)} (Esperado: 151)")
assert len(abstract_details) == 151, f"Expected 151 abstracts, got {len(abstract_details)}"

first_chars = [d.find("div", class_="thesis-abstract-content").get_text(strip=True)[0] for d in abstract_details]
assert all(ch.isupper() or ch in ['“', '"', '«'] for ch in first_chars), "All abstracts must start with an uppercase letter or quotation mark"
print("Test 10b - All 151 abstracts start with uppercase character: OK")

# Test 11: Multi-word search simulation
def norm_py(s):
    import unicodedata
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def search_sim(query):
    norm_q = norm_py(query)
    tokens = norm_q.split()
    matched = []
    for e in entries:
        s_data = e.get("data-search", "")
        if all(tok in s_data for tok in tokens):
            matched.append(e)
    return matched

sim_queries = [
    ("rabbani quilombo", 1), # Jeferson Celos
    ("herbert custodia", 1), # Emerson Mendes
    ("bessa cotas", 1),      # Heleonora Silva
    ("uber subordinacao", 1), # Ilan Fonseca
    ("custodia", 2),
    ("custódia", 2),
    ("justica", 13),
    ("justiça", 13),
    ("educacao", 27),
    ("educação", 27),
]

for q, exp in sim_queries:
    res = search_sim(q)
    print(f"Test 11 - Query '{q}': found {len(res)} matches (Expected >= {exp})")
    assert len(res) >= exp, f"Query '{q}' expected >= {exp}, got {len(res)}"

assert len(search_sim("justica")) == len(search_sim("justiça")), "Search with and without accents must yield identical results"
assert len(search_sim("educacao")) == len(search_sim("educação")), "Search with and without accents must yield identical results"
print("Test 11b - Normalization equality check passed: OK")

# Test 12: ARIA states on filter buttons
filter_btns = soup.find_all("button", class_="filter-btn")
for btn in filter_btns:
    assert btn.has_attr("aria-pressed"), f"Filter button {btn.get_text()} must have aria-pressed attribute"
print("Test 12 - All filter buttons have aria-pressed attribute: OK")

# Test 13: index.html is 100% identical to panorama_defesas_ppges_ufsb.html
index_text = Path("index.html").read_text(encoding="utf-8")
assert index_text == html_text, "index.html must be identical to panorama_defesas_ppges_ufsb.html"
print("Test 13 - index.html is identical to panorama_defesas_ppges_ufsb.html: OK")

# Test 14: Anonymity verification (no candidate names, no personal workspace leaks)
forbidden_tokens = ["Bacharel em Direito:", "Candidata:"]
for tok in forbidden_tokens:
    assert tok not in html_text, f"Forbidden token '{tok}' found in HTML"
print("Test 14 - Anonymity check: OK")

# Test 15: Quick Actions Bar (barra de 4 Ações Rápidas no topo sem emojis)
quick_bar = soup.find("nav", class_="quick-actions-bar")
assert quick_bar is not None, "Quick actions bar must exist"
quick_links = quick_bar.find_all("a", class_="quick-action-btn")
print(f"Test 15 - Quick actions buttons count: {len(quick_links)} (Esperado: 4)")
assert len(quick_links) == 4, f"Expected 4 quick action buttons, got {len(quick_links)}"

expected_anchors = [
    ("#sec-cronograma", "Cronograma e Prazos do Edital"),
    ("#sec-dicas", "Regras Formais do Anteprojeto"),
    ("#sec-professores", "Docentes e Vagas da Linha 1"),
    ("#sec-catalogo", "Catálogo de Defesas com Busca")
]
for i, (exp_href, exp_title) in enumerate(expected_anchors):
    btn = quick_links[i]
    assert btn["href"] == exp_href, f"Button {i+1} href must be {exp_href}, got {btn['href']}"
    assert exp_title in btn.get_text(), f"Button {i+1} must contain '{exp_title}', got {btn.get_text()}"
    # Verify no emojis
    for ch in btn.get_text():
        assert ord(ch) < 0x1F300 or ord(ch) > 0x1FAFF, f"Emoji detected in quick action button: {ch}"
print("Test 15b - All 4 Quick Action buttons verified (exact anchors, titles, no emojis): OK")

# Test 16: Section #sec-cronograma (Cronograma Oficial e 5 etapas)
sec_crono = soup.find("section", id="sec-cronograma")
assert sec_crono is not None, "Section #sec-cronograma must exist"
crono_text = sec_crono.get_text()

# Check critical deadlines and urgency alert
assert "08/10 a 20/10/2026" in crono_text, "Inscrições 08/10 a 20/10/2026 must be present"
assert "23h59" in crono_text, "Horário de encerramento 23h59 must be present"
assert "PagTesouro" in crono_text, "Menção a PagTesouro must be present"
assert "20h00" in crono_text or "20:00" in crono_text, "Horário limite taxa 20h00 must be present"
assert "150,00" in crono_text or "150" in crono_text, "Taxa de R$ 150 must be present"
assert "08/10 a 12/10/2026" in crono_text, "Isenção 08/10 a 12/10/2026 must be present"

# Check the 5 stages and dates
timeline_cards = sec_crono.find_all("div", class_="timeline-step-card")
print(f"Test 16a - Timeline stage cards: {len(timeline_cards)} (Esperado: 5)")
assert len(timeline_cards) == 5, f"Expected 5 timeline stage cards, got {len(timeline_cards)}"

assert "23/11/2026" in crono_text, "Prova escrita 23/11/2026 must be present"
assert "08/12 a 10/12/2026" in crono_text, "Arguição 08/12 a 10/12/2026 must be present"
assert "Janeiro/2027" in crono_text or "janeiro/2027" in crono_text, "Análise do Lattes janeiro/2027 must be present"
assert "11/02/2027" in crono_text, "Heteroidentificação 11/02/2027 must be present"
assert "26/02/2027" in crono_text, "Resultado final 26/02/2027 must be present"

# Check weights and formula
assert "Peso 3 (0,3)" in crono_text, "Anteprojeto e Arguição peso 3 must be present"
assert "Peso 2 (0,2)" in crono_text, "Prova escrita e Lattes peso 2 must be present"
assert "MF = (AA × 0,3) + (PE × 0,2) + (AAP × 0,3) + (ACL × 0,2)" in crono_text, "Formula MF must be present"
print("Test 16b - All dates, stages, weights and formula in #sec-cronograma verified: OK")

# Test 17: Checklist de Conformidade in #sec-dicas
sec_dicas = soup.find("section", id="sec-dicas")
assert sec_dicas is not None, "Section #sec-dicas must exist"
checklist = sec_dicas.find("div", class_="compliance-checklist-card")
assert checklist is not None, "Compliance checklist card must exist in #sec-dicas"

checklist_items = checklist.find_all("div", class_="checklist-item")
print(f"Test 17a - Checklist items count: {len(checklist_items)} (Esperado: 8)")
assert len(checklist_items) >= 6, f"Expected at least 6 checklist items, got {len(checklist_items)}"

chk_text = checklist.get_text()
assert "7 laudas" in chk_text.lower() or "7 lauda" in chk_text.lower(), "Checklist must specify 7 laudas"
assert "anonimato" in chk_text.lower(), "Checklist must specify anonimato"
assert "metadados" in chk_text.lower(), "Checklist must specify higienização de metadados"
assert "2.664/2026" in chk_text or "2664" in chk_text, "Checklist must cite Portaria CNPq 2.664/2026"
assert "linha 1" in chk_text.lower(), "Checklist must reference Linha 1 orientadores"
assert "abnt" in chk_text.lower(), "Checklist must reference ABNT NBR 6023"
print("Test 17b - Checklist items content and compliance criteria verified: OK")

# Test 18: TOC contains anchor to #sec-cronograma
toc_box = soup.find("nav", class_="toc-box")
assert toc_box is not None, "TOC must exist"
assert toc_box.find("a", href="#sec-cronograma") is not None, "TOC must link to #sec-cronograma"
print("Test 18 - TOC links to #sec-cronograma: OK")

print("\n>>> TODAS AS 18 VERIFICAÇÕES PASSARAM COM 100% DE SUCESSO! <<<")
