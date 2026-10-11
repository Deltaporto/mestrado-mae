import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from pathlib import Path
from bs4 import BeautifulSoup

print("=== INICIANDO VERIFICAÇÃO ESPECÍFICA DE ABAS E PAGINAÇÃO ===")

html_text = Path("panorama_defesas_ppges_ufsb.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html_text, "html.parser")

# 1. Verificar barra de navegação de abas fixas
main_tabs_nav = soup.find("nav", id="mainTabsNav")
assert main_tabs_nav is not None, "Elemento #mainTabsNav deve existir"
assert "main-tabs-sticky-bar" in main_tabs_nav.get("class", []), "Deve ter classe main-tabs-sticky-bar"

tab_btns = main_tabs_nav.find_all("button", class_="main-tab-nav-btn")
print(f"Check 1 - Total de botões de abas no topo: {len(tab_btns)} (Esperado: 4)")
assert len(tab_btns) == 4, f"Esperado 4 botões de abas, obtido {len(tab_btns)}"

expected_tabs = [
    ("tabBtn-cronograma", "pane-cronograma", "Edital & Cronograma"),
    ("tabBtn-professores", "pane-professores", "Docentes & Vagas"),
    ("tabBtn-catalogo", "pane-catalogo", "Catálogo de Defesas"),
    ("tabBtn-dicas", "pane-dicas", "Oficina de Anteprojeto"),
]

for btn_id, pane_id, title in expected_tabs:
    btn = main_tabs_nav.find("button", id=btn_id)
    assert btn is not None, f"Botão {btn_id} deve existir"
    assert btn.get("role") == "tab", f"Botão {btn_id} deve ter role='tab'"
    assert btn.get("aria-controls") == pane_id, f"Botão {btn_id} deve controlar {pane_id}"
    assert title in btn.get_text(), f"Botão {btn_id} deve conter texto '{title}'"
print("Check 1b - Todos os 4 botões de abas possuem IDs, ARIA e títulos corretos: OK")

# 2. Verificar os 4 painéis de abas
for btn_id, pane_id, _ in expected_tabs:
    pane = soup.find("div", id=pane_id)
    assert pane is not None, f"Painel #{pane_id} deve existir"
    assert "main-tab-pane" in pane.get("class", []), f"Painel #{pane_id} deve ter classe main-tab-pane"
    assert pane.get("role") == "tabpanel", f"Painel #{pane_id} deve ter role='tabpanel'"
    assert pane.get("aria-labelledby") == btn_id, f"Painel #{pane_id} deve ser referenciado por {btn_id}"
print("Check 2 - Todos os 4 painéis de abas (panes) existem com role='tabpanel': OK")

# 3. Verificar painel ativo por padrão (Aba 1: cronograma)
pane_crono = soup.find("div", id="pane-cronograma")
assert "active" in pane_crono.get("class", []), "Painel cronograma deve ser o ativo padrão"

# 4. Barras de paginação no catálogo
top_pg = soup.find("div", id="paginationBarTop")
bottom_pg = soup.find("div", id="paginationBarBottom")
assert top_pg is not None, "Barra #paginationBarTop deve existir no DOM"
assert bottom_pg is not None, "Barra #paginationBarBottom deve existir no DOM"
assert "catalog-pagination-bar" in top_pg.get("class", []), "#paginationBarTop deve ter classe catalog-pagination-bar"
assert "catalog-pagination-bar" in bottom_pg.get("class", []), "#paginationBarBottom deve ter classe catalog-pagination-bar"
print("Check 4 - Barras superior e inferior de paginação presentes: OK")

# 5. Funções JavaScript obrigatórias
funcoes_js_requeridas = [
    "navegarAbaPrincipal",
    "aplicarPaginacaoVisivel",
    "renderizarControlesPaginacao",
    "mudarPagina",
    "alterarItensPorPagina",
    "sincronizarAbaPorHash",
    "selecionarOpcaoHabitacional"
]
for fn in funcoes_js_requeridas:
    assert f"function {fn}" in html_text or f"{fn}(" in html_text, f"Função JS '{fn}' deve estar definida no script"
print("Check 5 - Todas as funções de controle de abas, paginação e roteamento presentes no JS: OK")

# 6. Sincronia index.html e panorama
index_text = Path("index.html").read_text(encoding="utf-8")
assert index_text == html_text, "index.html deve ser 100% idêntico a panorama_defesas_ppges_ufsb.html"
print("Check 6 - index.html idêntico a panorama_defesas_ppges_ufsb.html: OK")

print("\n>>> SUCESSO: TODAS AS VERIFICAÇÕES DE ABAS E PAGINAÇÃO PASSARAM COM 100%! <<<")
