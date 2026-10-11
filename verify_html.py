import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from pathlib import Path

html_text = Path("panorama_defesas_ppges_ufsb.html").read_text(encoding="utf-8")
print(f"Total length: {len(html_text)} chars")

# Check 1: 151 entries
entries = re.findall(r'<div class="thesis-entry"', html_text)
print(f"Check 1 - Total thesis-entry divs: {len(entries)} (Expected: 151)")
assert len(entries) == 151, f"Expected 151, got {len(entries)}"

# Check 2: All 8 year groups
year_groups = re.findall(r'<div class="year-group" data-year="(\d{4})">', html_text)
print(f"Check 2 - Year groups: {year_groups} (Expected 8 years: 2026 to 2019)")
assert len(year_groups) == 8, f"Expected 8 year groups, got {len(year_groups)}"

# Check 3: Faculty cards
faculty_cards = re.findall(r'<div class="faculty-card[^"]*">', html_text)
print(f"Check 3 - Faculty cards: {len(faculty_cards)} (Expected: 12)")
assert len(faculty_cards) == 12, f"Expected 12 faculty cards, got {len(faculty_cards)}"

# Check 4: Lattes links
lattes_links = re.findall(r'href="(http://lattes\.cnpq\.br/\d{16})"', html_text)
print(f"Check 4 - Unique Lattes links in faculty cards: {len(set(lattes_links))}")
for l in sorted(set(lattes_links)):
    print(f"   Lattes: {l}")
assert len(set(lattes_links)) >= 12, f"Expected at least 12 Lattes links, got {len(set(lattes_links))}"

# Check 5: PDF links in catalog and Section 3
all_ver_arquivo = re.findall(r'https://sig\.ufsb\.edu\.br/sigaa/verArquivo[^"]*', html_text)
print(f"Check 5 - Total SIGAA verArquivo URLs: {len(all_ver_arquivo)} (Expected: 147 - 129 no catalogo e 18 em politicas publicas)")
assert len(all_ver_arquivo) == 147, f"Expected 147 verArquivo URLs, got {len(all_ver_arquivo)}"

catalog_pdf_links = re.findall(r'<a\s+[^>]*class="pdf-link"[^>]*>', html_text)
print(f"Check 5b - Catalog specific PDF links: {len(catalog_pdf_links)} (Expected: 129)")
assert len(catalog_pdf_links) == 129, f"Expected 129 catalog PDF links, got {len(catalog_pdf_links)}"

# Check 6: Abstracts (<details class="thesis-abstract-details">)
abstract_details = re.findall(r'<details class="thesis-abstract-details">', html_text)
print(f"Check 6 - Abstract details elements: {len(abstract_details)} (Expected: 151)")
assert len(abstract_details) == 151, f"Expected 151 abstract details, got {len(abstract_details)}"

# Check 7: Chapter 3 corrections
emerson_m = re.search(r'Análise da audiência de custódia na comarca de Porto Seguro.*?Orientador:\s*Prof\.\s*Dr\.\s*Herbert Toledo Martins', html_text, re.DOTALL)
print(f"Check 7a - Emerson da Silva Mendes orientador Herbert Toledo Martins: {bool(emerson_m)}")
assert bool(emerson_m), "Emerson da Silva Mendes must have Herbert Toledo Martins as orientador"

celos_m = re.search(r'A luta pela ressignificação dos quilombos.*?Orientador:\s*Prof\.\s*Dr\.\s*Roberto Muhajir Rahnemay Rabbani', html_text, re.DOTALL)
print(f"Check 7b - Jeferson Celos orientador Roberto Rabbani: {bool(celos_m)}")
assert bool(celos_m), "Jeferson Celos must have Roberto Rabbani as orientador"

cunha_m = re.search(r'Protagonismo indígena e governança da água.*?Orientador:\s*Prof\.\s*Dr\.\s*Roberto Muhajir Rahnemay Rabbani', html_text, re.DOTALL)
print(f"Check 7c - Ricardo Cunha orientador Roberto Rabbani: {bool(cunha_m)}")
assert bool(cunha_m), "Ricardo Cunha must have Roberto Rabbani as orientador"

adriana_m = re.search(r'Política pública de assistência técnica.*?Adriana Vilas-Bôas.*?Orientadora:\s*Profa\.\s*Dra\.\s*Sandra Adriana Neves Nunes', html_text, re.DOTALL)
print(f"Check 7d - Adriana Vilas-Bôas orientadora Sandra Adriana Neves Nunes: {bool(adriana_m)}")
assert bool(adriana_m), "Adriana Vilas-Bôas (2019) must have Sandra Adriana Neves Nunes as orientador"

eva_m = re.search(r'Intersecções entre a violência doméstica.*?Eva Dayane.*?Orientadora:\s*Profa\.\s*Dra\.\s*Maria Aparecida de Oliveira Lopes', html_text, re.DOTALL)
print(f"Check 7e - Eva Dayane orientadora Maria Aparecida Lopes: {bool(eva_m)}")
assert bool(eva_m), "Eva Dayane (2019) must have Maria Aparecida de Oliveira Lopes as orientador"

# Check 8: Check Anonymity (ensure no sensitive names or OAB numbers)
for forbidden in ["OAB", "Advogad", "Bacharel"]:
    matches = re.findall(rf'\b{forbidden}\b', html_text, re.IGNORECASE)
    print(f"Check 8 - Pattern '{forbidden}' occurrences: {len(matches)}")

# Check 9: Equality of index.html and panorama_defesas_ppges_ufsb.html
index_text = Path("index.html").read_text(encoding="utf-8")
print(f"Check 9 - index.html identical to panorama_defesas_ppges_ufsb.html: {index_text == html_text}")
assert index_text == html_text, "index.html must be identical to panorama_defesas_ppges_ufsb.html"

print("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
