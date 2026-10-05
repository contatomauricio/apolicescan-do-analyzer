# Decisões arquiteturais (ADRs curtos)

## ADR-01: Provedor de LLM — Groq em vez de Claude/Gemini

**Contexto:** a spec recomendava Claude ou Gemini pela leitura nativa de PDF/imagem.
**Decisão:** usar Groq (modelos Llama servidos com baixa latência) via `pydantic-ai`.
**Consequência:** como a Groq não lê PDF/imagem diretamente, o texto precisa ser extraído
antes (PyMuPDF + Tesseract), reforçando o pipeline de OCR como parte central do fluxo, não
apenas fallback. Em compensação, ganhamos respostas rápidas e baratas, adequadas ao MVP.

## ADR-02: Framework de agentes — Pydantic AI

**Contexto:** era necessário um framework de agentes com saída estruturada tipada.
**Decisão:** Pydantic AI, por integrar validação Pydantic nativamente ao ciclo de
extração/comparação e por oferecer tools tipadas para o agente de consulta.
**Consequência:** saída sempre validada contra o esquema (`ApoliceDO`, `Diferenca`), com
retry automático em caso de falha de validação (RNF-02/RNF-05).

## ADR-03: Banco de dados — SQLite via SQLAlchemy

**Decisão:** SQLite, por não exigir infraestrutura adicional e ser fácil de distribuir com
o repositório/ZIP de entrega.
**Consequência:** suficiente para o volume de um MVP (dezenas de apólices); não serve para
concorrência alta, o que é aceitável dado o objetivo de aprendizado, não produto comercial.

## ADR-04: Comparação em duas camadas (determinística + semântica)

**Decisão:** campos numéricos e datas são comparados em código puro; apenas cláusulas
textuais (exclusões, coberturas) passam por um agente LLM de classificação.
**Consequência:** reduz custo e risco de alucinação em comparações que o código resolve com
exatidão, e concentra o uso de IA generativa onde ela agrega valor real — critério que pesa
30% da nota (uso correto de IA).

## ADR-05: Interface — Streamlit

**Decisão:** Streamlit para upload, tabelas e abas, por entrega rápida e reuso de padrões já
praticados no Desafio 4.
**Consequência:** interface simples (não objetivo do projeto é produto comercial), mas
suficiente para demonstrar upload → extração → consulta → comparação.
