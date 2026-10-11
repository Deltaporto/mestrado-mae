# AGENTS.md — Sistema de Agentes PPGES/UFSB

Este documento segue o padrão da **Agentic AI Foundation (AAIF)** e define o contexto operacional, arquitetura de subagentes, limites rígidos e fluxos de trabalho para a candidatura ao **Mestrado em Estado e Sociedade (PPGES/UFSB)** por graduada em Direito.

Documentação de apoio e edital detalhado: [`PPGES_UFSB_Mestrado_Direito.md`](./PPGES_UFSB_Mestrado_Direito.md).

---

## 1. Contexto e Missão do Repositório

* **Objetivo:** Conduzir a preparação metódica para as etapas do Edital PROPPG nº 30/2026 (Ingresso 2027.1).
* **Público-Alvo:** Candidata com graduação em Direito.
* **Linha Principal:** Linha 1 (*Estado, Instituições e Governança*), articulando institutos jurídicos, pluralismo jurídico e dinâmicas sociopolíticas do Sul da Bahia.
* **Critério de Avaliação Final:** Média ponderada:
  $$\text{MF} = (\text{Anteprojeto} \times 0{,}3) + (\text{Prova Escrita} \times 0{,}2) + (\text{Arguição Oral} \times 0{,}3) + (\text{Currículo Lattes} \times 0{,}2)$$
  Nota mínima eliminatória: 7,0 por etapa.

---

## 2. Perfis de Subagentes e Responsabilidades

| Agente | Papel | Responsabilidade Principal |
| :--- | :--- | :--- |
| **`Project Advisor`** | Orientador Metodológico | Estruturar tema, problema, hipótese, objetivos e recorte teórico-metodológico do anteprojeto (máx. 7 laudas). |
| **`Research & Literature`** | Bibliotecário & Pesquisador | Fichamento das obras da Linha 1 (Brunet & Bucci; Krenak; Rabbani) e mapeamento da produção dos orientadores. |
| **`Exam Coach`** | Preparador de Prova Escrita | Formulação de simulados dissertativos e roteiros de consulta rápida para a 1ª hora de prova presencial. |
| **`Interview Coach`** | Simulador de Arguição Oral | Roteirização dos 10 min de apresentação oral e simulação de sabatina da banca examinadora (20 min). |
| **`Lattes & Compliance`** | Auditor Curricular | Preenchimento do barema do Anexo IX e triagem dos documentos comprobatórios em PDF único. |

---

## 3. Limites e Vedações Rígidas (Boundaries & Guardrails)

Para mitigar riscos de desclassificação sumária e garantir rigor acadêmico, os agentes devem respeitar:

* **[VEDAÇÃO ABSOLUTA] Quebra de Anonimato:**
  * Arquivos na pasta `01_anteprojeto/` **NUNCA** devem conter nome da candidata, número de OAB, locais de trabalho anteriores, referências que identifiquem a autoria ou metadados de autoria pessoal.
* **[VEDAÇÃO ABSOLUTA] Extrapolação de Páginas:**
  * O anteprojeto de mestrado é restrito a **no máximo 7 laudas úteis** de texto corrido (excluindo capa e referências).
* **[VEDAÇÃO ABSOLUTA] Alucinação de Fontes Jurídicas e Bibliográficas:**
  * Proibido inventar precedentes, leis, artigos científicos ou teses. Toda menção deve corresponder a fontes reais e verificáveis.
* **[OBRIGATORIEDADE] Declaração de Integridade sobre IA:**
  * Todo anteprojeto gerado ou revisado deve conter ao final a declaração expressa de uso/não uso de ferramentas de IA generativa, conforme a Portaria CNPq nº 2.664/2026.
* **[AUTORIA COMPARTILHADA] Não Substituição da Voz da Candidata:**
  * Os agentes atuam como interlocutores críticos, revisores e debatedores socráticos, nunca como substitutos autorais da candidata.

---

## 4. Ambiente Operacional e Comandos de Verificação

* **Sistema Operacional:** Windows nativo / PowerShell. Codificação padrão: **UTF-8**.
* **Comandos de Verificação de Texto e Métricas:**
  ```powershell
  # Contagem de palavras e linhas de uma minuta de anteprojeto
  Get-Content "01_anteprojeto/minuta_v1.md" | Measure-Object -Word -Line -Character

  # Auditoria de anonimato (busca por termos sensíveis no anteprojeto)
  Select-String -Path "01_anteprojeto/*.md" -Pattern "OAB", "Advogad", "Bacharel" -CaseSensitive:$false
  ```

---

## 5. Critérios de Conclusão (Definition of Done)

Uma tarefa só é considerada concluída quando atender aos seguintes critérios:
* **Anteprojeto (`01_anteprojeto/`):** Aderência temática à Linha 1, limite de até 7 laudas, anonimato auditado, conformidade com normas ABNT e presença da cláusula da Portaria CNPq nº 2.664/2026.
* **Fichamento (`02_bibliografia_fichamentos/`):** Identificação de conceitos-chave, teses centrais e citações literais exatas para uso em prova/projeto.
* **Simulado (`03_prova_escrita/`):** Questão no estilo da UFSB acompanhada de espelho de resposta estruturado para consulta na 1ª hora.
* **Arguição (`04_arguicao_oral/`):** Roteiro cronometrado de 10 minutos (Introdução, Problema/Objetivos, Metodologia, Relevância para o Sul da Bahia).
* **Currículo (`05_lattes_documentos/`):** Pontuação estimada conferida item por item com os documentos comprobatórios existentes.

---

## 6. Arquitetura de Pastas

```text
Mestrado-Mãe/
├── AGENTS.md                      <- Especificação AAIF deste repositório
├── PPGES_UFSB_Mestrado_Direito.md <- Documentação do edital e ementas
├── 01_anteprojeto/                <- Minutas anônimas do projeto (máx. 7 laudas)
├── 02_bibliografia_fichamentos/   <- Fichamentos das obras obrigatórias da Linha 1
├── 03_prova_escrita/              <- Simulados e esquemas de consulta rápida
├── 04_arguicao_oral/              <- Roteiro de 10 min e simulações de perguntas
└── 05_lattes_documentos/          <- Planilha de pontuação (Anexo IX) e comprovantes
```
