# SPEC: Projeto Final InsurMinds
## Plataforma Inteligente para Análise e Comparação de Apólices D&O

> Spec de desenvolvimento do Projeto Final do curso InsurMinds (I2A2), derivada do documento "Desafios 3, 4, 5 e Projeto Final" (Celso Azevedo, 15/07/2026).
> **Prazo de entrega: 06/10/2026 às 23h59.** Esta entrega é a avaliação final e condição para aprovação e certificado do módulo avançado.

---

## 1. Resumo executivo

Construir um MVP funcional que recebe apólices D&O (Directors and Officers) em PDF ou imagem, extrai automaticamente as informações relevantes com OCR e LLM, estrutura os dados em banco, permite consultá-los em linguagem natural e compara pelo menos duas apólices, apresentando as diferenças em uma interface web.

O foco da avaliação é **aprendizado e arquitetura consistente**, não produto comercial. Um MVP simples, bem documentado e demonstrável vale mais do que uma solução complexa que o grupo não consiga explicar.

---

## 2. A trajetória dos desafios (de onde viemos)

O Projeto Final integra tudo o que foi praticado nos desafios anteriores. Cada desafio entrega uma competência que reaparece na solução final.

| Etapa | Tema | Competência central | Data |
|---|---|---|---|
| Desafio 3 | Machine Learning clássico (Titanic, Kaggle) | Ciclo completo de dados: EDA, limpeza, transformação, modelo, avaliação, reprodutibilidade (`random_state`), submissão | 26/07/2026 |
| Desafio 4 | Agente de consulta a CSV em linguagem natural | Agente com LLM + tools, framework de agentes, upload ZIP (CSV + dicionário de dados), respostas em texto, tabela e gráfico | 16/08/2026 |
| Desafio 5 | Comunicação proativa com o segurado (clima) | Agentes especializados em pipeline, consumo de API externa, regras de negócio, mensagens geradas por LLM, simulação de envio, README com MIT | 13/09/2026 |
| **Projeto Final** | **Comparação de apólices D&O** | **Integração de OCR + LLMs + agentes + banco de dados + interface + documentação + pitch + vídeo** | **06/10/2026** |

### 2.1 O que cada desafio contribui para o Projeto Final

| Herança | Origem | Como reaparece no Projeto Final |
|---|---|---|
| Rigor de pipeline de dados (limpar, tratar nulos, validar) | D3 | Pós-processamento da extração: normalização de valores monetários, datas, percentuais; tratamento de campos ausentes |
| Reprodutibilidade e avaliação do modelo | D3 | Conjunto de teste "ouro" com 2 apólices anotadas à mão para medir acurácia da extração; temperatura baixa e prompts versionados |
| Justificar decisões técnicas | D3 | Seção de decisões arquiteturais no relatório (ADRs curtos) |
| Upload de arquivos + processamento automático | D4 | Tela de upload de apólices que dispara o pipeline automaticamente |
| Agente interpreta pergunta e usa tools sobre dados | D4 | Agente de consulta que responde perguntas sobre as apólices consultando o banco estruturado |
| Respostas em texto, tabela e gráfico | D4 | Resultado da comparação em tabela lado a lado e destaque visual das diferenças |
| Framework de agentes obrigatório | D4 | Uso de um framework da lista (ver decisão em 5.1) |
| Separar interface, agentes, ferramentas e processamento | D4 | Estrutura modular do repositório (seção 7) |
| Pipeline coleta, análise, regras, geração, envio | D5 | Pipeline de ingestão, extração, estruturação, comparação, relatório |
| Agentes especializados por responsabilidade | D5 | Orquestrador e agentes da seção 6 |
| Mensagens/relatórios gerados por LLM | D5 | Relatório comparativo em linguagem natural gerado pelo agente de relatório |
| Chaves de API ocultas, `.env` | D4/D5 | `.env` + `.env.example`, `.gitignore` |
| Repositório público, README completo, licença MIT | D5 | Obrigatório também no final, com mais itens |
| Não responder manualmente com ChatGPT/Claude/Gemini | D4 | Toda resposta deve ser produzida pela aplicação do grupo |

---

## 3. Objetivos e não objetivos

### 3.1 Objetivos
- Ler apólices D&O em PDF (texto nativo e escaneado) e imagem.
- Extrair automaticamente campos e cláusulas relevantes.
- Armazenar de forma estruturada e consultável.
- Responder perguntas em linguagem natural sobre uma ou mais apólices, citando a fonte (página e trecho).
- Comparar no mínimo 2 apólices e apresentar as principais diferenças.
- Usar pelo menos um modelo de IA Generativa no processamento.
- Disponibilizar interface web que permita demonstrar tudo isso.

### 3.2 Não objetivos (explicitamente fora de escopo, conforme o documento)
- Produto comercial completo.
- Alta disponibilidade, autenticação robusta, mecanismos avançados de segurança.
- Integração com sistemas reais de seguradoras.
- Cobertura de todos os tipos de apólice (foco apenas em D&O).
- Interface sofisticada.

---

## 4. Requisitos

### 4.1 Funcionais (mínimos obrigatórios do documento)

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | Permitir upload de documentos em PDF ou imagem (PNG/JPG) | Must |
| RF-02 | Extrair texto automaticamente (texto nativo com fallback para OCR) | Must |
| RF-03 | Extrair informações relevantes das apólices usando LLM | Must |
| RF-04 | Estruturar os dados extraídos em esquema organizado (JSON validado + tabelas) | Must |
| RF-05 | Persistir em banco de dados | Must |
| RF-06 | Comparar pelo menos duas apólices | Must |
| RF-07 | Apresentar as principais diferenças identificadas ao usuário | Must |
| RF-08 | Interface web que permita demonstrar o funcionamento | Must |
| RF-09 | Consulta em linguagem natural sobre as apólices (agente com tools) | Should |
| RF-10 | Citar página e trecho de origem de cada campo extraído | Should |
| RF-11 | Exportar o relatório comparativo (Markdown ou PDF) | Could |
| RF-12 | Comparar mais de 2 apólices | Could |

### 4.2 Não funcionais

| ID | Requisito |
|---|---|
| RNF-01 | Código modular, com responsabilidades separadas (ingestão, OCR, extração, banco, agentes, UI) |
| RNF-02 | Tratamento de erros: arquivo inválido, PDF ilegível, falha de API, resposta do LLM fora do esquema (retry com validação) |
| RNF-03 | Credenciais fora do repositório (`.env`, `.env.example`, `.gitignore`) |
| RNF-04 | Instalação e execução em poucos comandos, documentadas no README |
| RNF-05 | Respostas do LLM com temperatura baixa e saída validada por Pydantic para reduzir alucinação |
| RNF-06 | Campo não encontrado deve ser retornado como `null` com indicação "não localizado", nunca inventado |
| RNF-07 | Demonstração reproduzível a partir de documentos de exemplo versionados no repositório |

---

## 5. Decisões técnicas propostas

Estas são recomendações; o grupo pode trocar qualquer item desde que justifique no relatório (critério explícito de avaliação).

### 5.1 Stack

| Camada | Escolha recomendada | Alternativas | Justificativa |
|---|---|---|---|
| Linguagem | Python 3.11+ | n/a | Padrão do curso e ecossistema de IA |
| Framework de agentes | **Pydantic AI** | LangChain, CrewAI, AutoGen, LlamaIndex | Saída estruturada tipada casa com a extração de cláusulas; agentes e tools simples; já aceito no D4 |
| LLM | Claude (Anthropic) ou Gemini | OpenAI, modelo local | Janela de contexto longa e boa leitura de PDF; Gemini/Claude aceitam PDF e imagem direto |
| Extração de texto | PyMuPDF (texto nativo) com fallback Tesseract OCR | Azure Document Intelligence, Google Vision, AWS Textract, LLM multimodal | Gratuito e local; LLM multimodal como plano B para escaneados difíceis |
| Banco de dados | SQLite via SQLAlchemy | PostgreSQL, MongoDB | Zero infraestrutura para o MVP; fácil de distribuir no ZIP |
| Interface | Streamlit | Gradio, FastAPI + HTML | Entrega rápida, upload e tabelas nativos |
| Gráficos/tabelas | pandas + Streamlit (st.dataframe) | Plotly | Reuso do D4 |
| Testes | pytest | n/a | Testes do esquema, normalizadores e comparador |

### 5.2 Estratégia de extração (ponto mais importante)

1. Tentar texto nativo do PDF por página. Se a página tiver pouco texto, aplicar OCR.
2. Guardar o texto por página (`pagina`, `texto`) para permitir citação de origem.
3. Para apólices longas, dividir em blocos (por seção ou por janelas de páginas) e extrair por bloco, depois consolidar. Se o modelo escolhido tiver contexto suficiente, enviar o documento inteiro.
4. Saída do LLM obrigatoriamente no esquema Pydantic da seção 8, com campos `valor`, `pagina`, `trecho_origem` e `confianca`.
5. Normalizar valores (moeda, datas, percentuais) em código Python, não no LLM.
6. Validar; se falhar, retry com mensagem de erro de validação (limite de 2 tentativas).

### 5.3 Estratégia de comparação

Comparação em duas camadas:

- **Determinística (código):** compara campos numéricos e datas diretamente (limite, retenção, vigência, prêmio) e calcula a diferença absoluta e percentual.
- **Semântica (LLM):** para cláusulas textuais (exclusões, condições, extensões), o agente compara os trechos e classifica cada item como `igual`, `diferente`, `somente_em_A`, `somente_em_B`, com explicação curta e citação.

Isso evita pedir ao LLM aquilo que o código faz com exatidão e mostra "uso correto de IA", que pesa 30% da nota.

---

## 6. Arquitetura

### 6.1 Visão geral

```
                       +--------------------+
   Usuário --------->  |  UI Streamlit      |
                       | (Upload | Consulta | Comparação)
                       +---------+----------+
                                 |
                       +---------v----------+
                       |   Orquestrador     |
                       +--+----+----+----+--+
                          |    |    |    |
        +-----------------+    |    |    +------------------+
        |                      |    |                       |
+-------v-------+   +----------v--+ +v---------------+  +----v------------+
| Agente de     |   | Agente de   | | Agente de      |  | Agente de       |
| Recepção/OCR  |   | Extração    | | Consulta (Q&A) |  | Comparação e    |
| (ingest)      |   | (LLM + schema)| | (tools no DB) |  | Relatório       |
+-------+-------+   +------+------+ +--------+-------+  +--------+--------+
        |                  |                 |                   |
        +------------------+--------+--------+-------------------+
                                    |
                            +-------v-------+
                            | SQLite (DB)   |
                            | + arquivos    |
                            +---------------+
```

### 6.2 Agentes e responsabilidades

Seguindo a dica do documento, de forma enxuta (6 papéis, mas só 3 a 4 agentes com LLM de fato):

| Agente / Componente | Usa LLM? | Responsabilidade | Entrada | Saída |
|---|---|---|---|---|
| Recepção | Não | Validar tipo e tamanho, salvar arquivo, registrar documento no banco | Arquivo | `documento_id` |
| OCR / Texto | Não (ou LLM multimodal como fallback) | Extrair texto por página | Arquivo | Lista de páginas com texto |
| Extração e Estruturação | **Sim** | Identificar campos e cláusulas relevantes e devolver no esquema Pydantic | Texto por página | `ApoliceD&O` validada |
| Persistência | Não | Gravar apólice e itens no SQLite | Objeto validado | Registros no DB |
| Consulta (Q&A) | **Sim** | Responder perguntas usando tools de leitura no banco (nunca inventar) | Pergunta | Resposta com citações |
| Comparação | Híbrido | Diff determinístico + análise semântica de cláusulas | 2+ apólices | Lista de diferenças classificadas |
| Relatório | **Sim** | Escrever o resumo comparativo para um corretor/gestor de risco | Diferenças | Texto + tabela |

### 6.3 Tools do agente de consulta

- `listar_apolices()`
- `obter_apolice(id)`
- `buscar_clausula(id, termo)` (busca no texto extraído e nas cláusulas)
- `comparar_apolices(id_a, id_b)`
- `obter_trecho(id, pagina)`

### 6.4 Fluxo completo de processamento

1. Usuário faz upload de 1 ou mais apólices.
2. Recepção valida e salva.
3. OCR/Texto extrai texto por página.
4. Extração produz o objeto estruturado com citações.
5. Persistência grava no banco.
6. Usuário escolhe duas apólices e clica em comparar (ou pergunta em linguagem natural).
7. Comparação gera diferenças; Relatório escreve o resumo.
8. UI mostra tabela lado a lado, destaques e texto explicativo, com links para os trechos de origem.

---

## 7. Estrutura do repositório

```
insurminds-do-platform/
├── README.md                    # descrição, instalação, execução, tecnologias, integrantes, licença MIT
├── LICENSE                      # MIT
├── .env.example
├── .gitignore
├── pyproject.toml / requirements.txt
├── app/
│   ├── main.py                  # Streamlit (entrypoint)
│   ├── ui/                      # páginas: upload, consulta, comparação
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── extraction_agent.py
│   │   ├── qa_agent.py
│   │   ├── comparison_agent.py
│   │   └── report_agent.py
│   ├── tools/                   # tools expostas aos agentes
│   ├── ingest/                  # recepção, pdf_text.py, ocr.py
│   ├── schemas/                 # modelos Pydantic (apólice, cláusula, diferença)
│   ├── db/                      # models, repositório, migrations simples
│   ├── services/                # normalizadores (moeda, data, %), comparador determinístico
│   ├── prompts/                 # prompts versionados em arquivos .md
│   └── config.py
├── data/
│   └── samples/                 # apólices públicas de exemplo (com fonte citada)
├── tests/
│   ├── golden/                  # apólices anotadas à mão + JSON esperado
│   └── test_*.py
├── docs/
│   ├── arquitetura.md
│   └── decisoes.md              # ADRs curtos
└── Projeto_Final_Artefatos/     # NOME EXATO exigido
    ├── InsurMinds_Projeto_Final.pptx
    ├── InsurMinds_Projeto_Final.mp4
    ├── Relatorio_Tecnico.pdf
    └── (prints, diagramas, exemplos de saída)
```

---

## 8. Modelo de dados

### 8.1 Campos extraídos de uma apólice D&O

Cada campo guarda `valor`, `pagina`, `trecho_origem`, `confianca` (0 a 1). Se não achado: `valor = null`.

**Identificação**
- Seguradora, número da apólice, número do processo SUSEP (se houver), tomador/segurado, vigência (início e fim), data de emissão.

**Valores**
- Limite Máximo de Garantia (LMG) por apólice e por sinistro/agregado, prêmio total, franquia/retenção (por tipo), moeda.

**Coberturas**
- Estrutura Side A / Side B / Side C (quando aplicável), custos de defesa (dentro ou fora do limite), cobertura para administradores atuais e ex-administradores, cônjuges/herdeiros, subsidiárias, extensões (ex.: gastos com crise, multas e penalidades, ambiental, trabalhista, regulatória).

**Condições temporais**
- Retroatividade, prazo complementar/estendido de notificação, base da cobertura (claims made), prazo para aviso de sinistro.

**Exclusões**
- Lista de exclusões com texto resumido e citação (ex.: atos dolosos/fraude, vantagem pessoal indevida, poluição, litígios pré-existentes, sanções, etc.).

**Outros**
- Foro/jurisdição, territorialidade, cláusulas de cancelamento, rateio/priorização de pagamentos, sub-rogação, observações relevantes.

> Obs.: os nomes exatos variam entre seguradoras; o prompt de extração deve instruir o modelo a mapear sinônimos para o campo canônico e a registrar o nome original encontrado no texto.

### 8.2 Tabelas (SQLite)

```
documento(id, nome_arquivo, caminho, tipo, paginas, enviado_em, status)
pagina(id, documento_id, numero, texto, usou_ocr)
apolice(id, documento_id, seguradora, numero, segurado, vigencia_ini, vigencia_fim,
        lmg, premio, moeda, retroatividade, prazo_complementar, base_cobertura,
        jurisdicao, json_completo)
cobertura(id, apolice_id, nome, descricao, sublimite, pagina, trecho, confianca)
franquia(id, apolice_id, tipo, valor, descricao, pagina, trecho)
exclusao(id, apolice_id, titulo, descricao, pagina, trecho)
comparacao(id, apolice_a, apolice_b, criado_em, resultado_json, relatorio_texto)
```

### 8.3 Esquema de saída da comparação

```
Diferenca:
  categoria: str            # ex.: "Limites", "Exclusões", "Condições temporais"
  item: str                 # ex.: "Limite Máximo de Garantia"
  valor_a, valor_b: str|num
  status: igual | diferente | somente_em_A | somente_em_B
  impacto: alto | medio | baixo
  explicacao: str           # 1 a 2 frases
  citacao_a, citacao_b: {pagina, trecho}
```

---

## 9. Interface (mínima, mas demonstrável)

Três abas no Streamlit:

1. **Upload e processamento:** arrastar PDFs/imagens, barra de progresso por etapa (texto, extração, gravação), lista de apólices processadas com status.
2. **Consulta:** campo de pergunta em linguagem natural sobre uma apólice selecionada (ex.: "Qual é o limite máximo de garantia?", "Há cobertura para custos de defesa?", "Quais são as exclusões?"), com resposta e citação da página.
3. **Comparação:** seleção de duas apólices, tabela lado a lado com diferenças destacadas por cor, resumo executivo gerado, botão de exportar relatório.

Tratamento de erros visível ao usuário (mensagens claras, sem stack trace).

---

## 10. Dados de teste

- Reunir **pelo menos 2 apólices D&O públicas** (modelos de seguradoras, documentos SUSEP, condições gerais públicas). Citar as fontes no relatório (exigência do documento).
- Idealmente 3 a 4 documentos, sendo 1 escaneado ou de baixa qualidade para exercitar o OCR.
- Anotar à mão os campos principais de 2 apólices em `tests/golden/*.json` para medir a acurácia da extração (herança do rigor de avaliação do D3).
- Não usar documentos confidenciais ou com dados pessoais reais.

---

## 11. Qualidade e validação

| Verificação | Como |
|---|---|
| Extração | Comparar saída com o gabarito manual; reportar % de campos corretos no relatório |
| Normalizadores | Testes unitários (moeda "R$ 10.000.000,00", datas pt-BR, percentuais) |
| Comparador determinístico | Testes unitários com pares sintéticos |
| Alucinação | Teste: pergunta sobre cláusula inexistente deve retornar "não localizado" |
| Robustez | Arquivo corrompido, PDF vazio, formato inválido, falha da API (mock) |
| Ponta a ponta | Roteiro de demo executado do zero em ambiente limpo (clonar, instalar, rodar) |

---

## 12. Entregáveis (checklist oficial)

### 12.1 Relatório Técnico (PDF)
- [ ] Arquitetura da solução (diagrama + descrição)
- [ ] Tecnologias utilizadas
- [ ] Descrição dos agentes desenvolvidos
- [ ] Fluxo completo de processamento
- [ ] Justificativa das decisões arquiteturais
- [ ] Limitações conhecidas
- [ ] Possibilidades de evolução futura
- [ ] Fontes dos documentos utilizados (obrigatório se vierem de fontes externas)
- [ ] Resultados de teste (acurácia da extração, exemplos de comparação)

### 12.2 Código-fonte
- [ ] Link do repositório **público** no GitHub
- [ ] ZIP com todo o código-fonte e demais artefatos
- [ ] README.md com: descrição do projeto, instruções de instalação, instruções de execução, tecnologias utilizadas, identificação dos integrantes, licença MIT
- [ ] Arquivo LICENSE (MIT)
- [ ] Nenhuma chave de API commitada (conferir histórico do git)

### 12.3 Apresentação
- [ ] Arquivo com nome exato **`InsurMinds_Projeto_Final.pptx`** (Pitch Deck)

### 12.4 Vídeo
- [ ] Arquivo com nome exato **`InsurMinds_Projeto_Final.mp4`**, **máximo 5 minutos**, mostrando: o problema abordado, a arquitetura da solução, o funcionamento da aplicação, os principais resultados obtidos

### 12.5 Organização do repositório
- [ ] Pasta **`Projeto_Final_Artefatos`** contendo a apresentação, o vídeo e demais artefatos auxiliares

### 12.6 Envio
- [ ] E-mail para `challenges@i2a2.academy`, enviado pelo representante do grupo, com cópia para todos os integrantes
- [ ] Assunto exato: `InsurMinds – Projeto Final`
- [ ] Corpo: `Entrega do grupo: <Nome do grupo>`
- [ ] Anexar os arquivos exigidos (relatório PDF, ZIP, pptx, e link do GitHub; confirmar se o mp4 vai anexado ou por link caso exceda o limite de e-mail)

---

## 13. Mapa de avaliação (como a nota é composta)

| Critério geral | Peso | Onde se garante |
|---|---|---|
| Funcionamento | 20% | Demo ponta a ponta sem erro; roteiro testado do zero |
| Qualidade técnica | 15% | Esquema validado, citações, normalização, tratamento de erros |
| Organização do código | 15% | Estrutura da seção 7, módulos, tipagem, testes |
| Documentação | 10% | README completo, relatório, docs/decisoes.md |
| Criatividade | 10% | Diferencial (ex.: classificação de impacto, destaque visual, citação com trecho) |
| **Uso correto de IA** | **30%** | LLM onde agrega valor (extração e síntese), código onde precisa de exatidão; saída estruturada; sem alucinação; prompts claros |

Critérios específicos do Projeto Final: qualidade da arquitetura, correta utilização de IA Generativa, integração entre componentes, organização do código, clareza da documentação, facilidade de uso, capacidade de demonstrar o sistema, inovação e criatividade.

### Definição de "entrega completa"
- [ ] A solução executa corretamente
- [ ] O processamento dos documentos pode ser demonstrado
- [ ] A extração ocorre de forma automática
- [ ] É possível comparar pelo menos duas apólices
- [ ] O relatório descreve claramente a arquitetura
- [ ] O repositório GitHub está organizado e acessível
- [ ] O Pitch Deck foi entregue
- [ ] O vídeo demonstra claramente o funcionamento

---

## 14. Plano de execução (prazo curto)

Hoje é 04/10 e o prazo é 06/10 às 23h59. Plano em ordem de prioridade; o que estiver no fim pode ser cortado.

### Dia 1 (04/10): núcleo funcional
1. Criar repositório público, licença MIT, README inicial, `.env.example`, `.gitignore`.
2. Escolher e baixar 2 a 3 apólices D&O públicas.
3. Implementar ingestão: PDF para texto por página, fallback OCR.
4. Definir esquema Pydantic e prompt de extração; rodar nas 2 apólices e ajustar.
5. Persistir no SQLite.

### Dia 2 (05/10): comparação, interface e consulta
6. Comparador determinístico + semântico; saída `Diferenca`.
7. Agente de relatório e agente de consulta com tools.
8. UI Streamlit com 3 abas.
9. Testes mínimos, tratamento de erros, gabarito manual e medida de acurácia.
10. Congelar o código (feature freeze) à noite.

### Dia 3 (06/10): documentação e entrega
11. Relatório Técnico em PDF.
12. Pitch Deck `InsurMinds_Projeto_Final.pptx`.
13. Gravar vídeo de até 5 min a partir de um roteiro (ver 14.1).
14. Montar `Projeto_Final_Artefatos`, gerar ZIP, conferir README e ausência de chaves.
15. Teste final em ambiente limpo e envio do e-mail **antes das 23h59** (alvo: até 20h, para ter margem).

### 14.1 Roteiro do vídeo (5 min)
- 0:00 a 0:45: problema (apólices longas, comparação manual demorada)
- 0:45 a 1:45: arquitetura (diagrama e agentes)
- 1:45 a 4:00: demo ao vivo (upload, extração, consulta, comparação)
- 4:00 a 5:00: resultados (acurácia no gabarito, limitações, próximos passos)

### 14.2 Estrutura sugerida do Pitch Deck
1. Problema e contexto
2. Solução (visão em uma frase)
3. Como funciona (fluxo)
4. Arquitetura e agentes
5. Demonstração (prints)
6. Resultados e métricas
7. Limitações e evolução
8. Equipe e tecnologias

### 14.3 Regra de corte se faltar tempo
Manter sempre: upload, extração, armazenamento, comparação de 2 apólices, interface, relatório, pptx, vídeo, README, MIT. Cortar primeiro: exportação do relatório (RF-11), comparação de mais de 2 apólices (RF-12), gráficos extras, citação com trecho exato (manter só a página).

---

## 15. Riscos e mitigação

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Prazo apertado | Alta | Escopo mínimo da seção 14.3; congelar código no Dia 2 |
| OCR ruim em escaneados | Média | Preferir PDFs com texto nativo na demo; plano B com LLM multimodal |
| LLM inventa campos | Média | Esquema com `null`, citação obrigatória, temperatura baixa, teste de pergunta sem resposta |
| Custo/limite de API | Média | Cache das extrações no banco (não reprocessar a mesma apólice); usar modelo menor para tarefas simples |
| Vazamento de chave no git | Baixa/alto impacto | `.gitignore`, `.env.example`, revisar histórico antes de tornar público |
| Falha na demo ao vivo | Média | Vídeo pré-gravado com dados reais; documentos de exemplo versionados |
| Apólices muito longas excedem contexto | Média | Extração por blocos e consolidação |
| Violação da regra de "não responder manualmente com LLM" | Baixa | Toda saída apresentada vem da aplicação; guardar prints das execuções |

---

## 16. Pontos a confirmar com o grupo

1. Nome do grupo e quem é o representante (quem envia o e-mail de entrega).
2. Provedor de LLM e chave disponível (Claude, Gemini, OpenAI) e orçamento de uso.
3. Quais apólices D&O públicas serão usadas e de onde vêm (para citar no relatório).
4. O vídeo vai por anexo ou link no e-mail (conferir limite de tamanho).
5. Se o grupo quer apresentar no encontro de revisão (nos desafios anteriores era preciso manifestar interesse até a data limite; vale confirmar para o final).

---

## 17. Definition of Done

O projeto está pronto quando, partindo de um clone limpo do repositório público, qualquer pessoa consegue seguir o README, subir a aplicação, enviar duas apólices D&O, ver a extração estruturada, fazer perguntas em linguagem natural e obter a comparação com diferenças e citações; e quando todos os itens do checklist da seção 12 estão marcados e o e-mail foi enviado dentro do prazo.
