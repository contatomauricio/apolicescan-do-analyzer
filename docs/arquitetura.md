# Arquitetura da solução

## Visão geral

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
| (ingest)      |   | (LLM+schema)| | (tools no DB)  |  | Relatório       |
+-------+-------+   +------+------+ +--------+-------+  +--------+--------+
        |                  |                 |                   |
        +------------------+--------+--------+-------------------+
                                    |
                            +-------v-------+
                            | SQLite (DB)   |
                            | + arquivos    |
                            +---------------+
```

## Componentes (`app/`)

- `ingest/`: recepção (validação e persistência de arquivos), extração de texto nativo
  (PyMuPDF) e OCR de fallback (Tesseract).
- `schemas/`: modelos Pydantic — `ApoliceDO`, `Diferenca`, `ResultadoComparacao` — com
  `valor`, `pagina`, `trecho_origem` e `confianca` em cada campo extraído.
- `agents/`: agentes `pydantic-ai` configurados com o provedor **Groq**:
  - `extraction_agent`: transforma texto em `ApoliceDO` validada, com retry automático em
    caso de saída fora do esquema e processamento em blocos de páginas para documentos longos.
  - `qa_agent`: responde perguntas usando tools de leitura no banco (`app/tools/db_tools.py`),
    nunca inventando conteúdo fora dos dados retornados.
  - `comparison_agent`: combina diff determinístico (código, `services/comparator.py`) com
    comparação semântica de cláusulas textuais via LLM.
  - `report_agent`: redige o resumo executivo a partir das diferenças já classificadas.
  - `orchestrator`: coordena o fluxo ponta a ponta.
- `db/`: modelos SQLAlchemy e repositório de acesso ao SQLite.
- `services/normalizers.py`: normalização de moeda, data e percentual feita em código
  (nunca pelo LLM), conforme seção 5.2 da spec.
- `ui/`: três páginas Streamlit (Upload, Consulta, Comparação).

## Fluxo completo

1. Upload de uma ou mais apólices.
2. Recepção valida tipo/tamanho e salva o arquivo.
3. Extração de texto por página (nativo + fallback OCR).
4. Agente de Extração produz `ApoliceDO` com citações de página e trecho.
5. Persistência grava apólice, coberturas, franquias e exclusões no SQLite.
6. Usuário compara duas apólices ou pergunta em linguagem natural.
7. Comparação gera `Diferenca[]`; Relatório escreve o resumo em texto.
8. UI mostra tabela lado a lado com destaque por status e o resumo executivo.

## Por que Groq

A spec original recomendava Claude/Gemini pela leitura nativa de PDF/imagem; este projeto
usa **Groq** (LLMs open-weight servidos com baixa latência) como provedor principal via
`pydantic-ai`. Como os modelos hospedados na Groq são texto-apenas, a extração depende do
texto já obtido por `PyMuPDF`/`Tesseract` em vez de envio multimodal do PDF — por isso o
pipeline de OCR descrito na seção 5.2 é obrigatório, não apenas um plano B.
