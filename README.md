# ApoliceScan — Plataforma de Análise e Comparação de Apólices D&O

MVP desenvolvido para o Projeto Final do curso InsurMinds (I2A2). Recebe apólices D&O em PDF
ou imagem, extrai informações automaticamente com OCR + LLM (Groq), estrutura os dados em
banco, permite consultá-los em linguagem natural e compara apólices lado a lado.

Especificação completa em [spec.md](spec.md).

## Tecnologias

- Python 3.11+
- [Pydantic AI](https://ai.pydantic.dev/) com provedor **Groq** (LLM)
- PyMuPDF (texto nativo de PDF) + Tesseract OCR (fallback para páginas escaneadas)
- SQLAlchemy + SQLite (persistência)
- Streamlit (interface web)
- Pydantic (validação de esquema / saída estruturada)
- pytest (testes)

## Instalação

Pré-requisitos: Python 3.11+, Tesseract OCR instalado no sistema (para o fallback de OCR),
e uma chave de API da [Groq](https://console.groq.com/).

```bash
# instalar o Tesseract (Ubuntu/WSL)
sudo apt-get install -y tesseract-ocr tesseract-ocr-por

# criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# instalar dependências
pip install -r requirements.txt

# configurar variáveis de ambiente
cp .env.example .env
# edite .env e preencha GROQ_API_KEY
```

## Execução

```bash
streamlit run app/main.py
```

Acesse `http://localhost:8501`, vá até a aba **Upload e processamento**, envie 2 ou mais
apólices D&O de exemplo (ver `data/samples/`) e use as abas **Consulta** e **Comparação**.

## Testes

```bash
pytest
```

## Estrutura do repositório

```
app/
├── main.py            # entrypoint Streamlit
├── ui/                 # páginas: upload, consulta, comparação
├── agents/             # orquestrador e agentes (extração, Q&A, comparação, relatório)
├── tools/              # tools expostas ao agente de consulta
├── ingest/              # recepção, extração de texto, OCR
├── schemas/             # modelos Pydantic
├── db/                  # modelos SQLAlchemy e repositório
├── services/            # normalizadores e comparador determinístico
└── prompts/              # prompts versionados (.md)
data/samples/            # apólices de exemplo (adicionar antes da demo)
tests/                    # testes unitários e gabarito "golden"
docs/                     # arquitetura e decisões (ADRs)
```

Veja [docs/arquitetura.md](docs/arquitetura.md) para o detalhamento dos agentes e do fluxo,
e [docs/decisoes.md](docs/decisoes.md) para as justificativas técnicas (ADRs).

## Integrantes

- (preencher com os nomes do grupo)

## Licença

Distribuído sob a licença MIT — veja [LICENSE](LICENSE).
