# Sistema Inteligente de Separacao Logistica (FastAPI)

Base inicial de API para um projeto academico de automacao logistica com leitura e separacao de itens por QR Code em esteira (prototipo com Lego).

## O que esta implementado

- Geracao de QR Code com dados do item logistico.
- Leitura e decodificacao de QR Code via imagem usando OpenCV (`cv2`).
- Validacao de payload/estrutura com Pydantic.
- Simulacao da decisao de separacao por regiao do Brasil.
- Estrutura em camadas pronta para evolucao (servicos, schemas, core, api).
- Tratamento global de excecoes com resposta padronizada.
- Endpoints de apoio: status, healthcheck, configuracoes e regioes validas.

## Estrutura do projeto

```text
.
|-- app
|   |-- api
|   |   |-- deps.py
|   |   `-- v1
|   |       |-- api.py
|   |       `-- endpoints
|   |           |-- health.py
|   |           |-- qrcode.py
|   |           |-- sort.py
|   |           `-- system.py
|   |-- core
|   |   |-- config.py
|   |   |-- exceptions.py
|   |   `-- handlers.py
|   |-- models
|   |-- schemas
|   |   |-- common.py
|   |   |-- item.py
|   |   |-- qrcode.py
|   |   |-- sort.py
|   |   `-- system.py
|   |-- services
|   |   |-- qrcode_service.py
|   |   `-- sorter_service.py
|   |-- utils
|   |   `-- response.py
|   `-- main.py
|-- docs
|   `-- api.md
|-- .env.example
|-- README.md
`-- requirements.txt
```

## Requisitos

- Python 3.11+
- pip

## Como executar localmente

1. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. (Opcional) Copie o arquivo de ambiente:

```bash
copy .env.example .env
```

No Linux/macOS:

```bash
cp .env.example .env
```

4. Suba a API:

```bash
uvicorn app.main:app --reload
```

5. Acesse:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Root: `http://127.0.0.1:8000/`

## Endpoints principais

- `POST /api/v1/qrcode/generate`
- `POST /api/v1/qrcode/generate/download`
- `POST /api/v1/qrcode/read`
- `POST /api/v1/sort/preview`
- `GET /api/v1/health`
- `GET /api/v1/regions`
- `GET /api/v1/config`
- `GET /api/v1`

## Exemplo: gerar QR Code

### Request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/qrcode/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "id_item": "ITEM-0001",
    "descricao": "Caixa de sensores",
    "regiao_destino": "NORTE",
    "uf_destino": "AM",
    "cidade_destino": "Manaus",
    "timestamp_criacao": "2026-03-13T10:00:00Z",
    "nome_arquivo": "item-0001.png"
  }'
```

### Response (resumida)

```json
{
  "success": true,
  "message": "QR Code gerado com sucesso.",
  "data": {
    "item": {
      "id_item": "ITEM-0001",
      "descricao": "Caixa de sensores",
      "regiao_destino": "NORTE",
      "uf_destino": "AM",
      "cidade_destino": "Manaus",
      "timestamp_criacao": "2026-03-13T10:00:00Z"
    },
    "filename": "item-0001.png",
    "mime_type": "image/png",
    "payload_json": "{\"id_item\":\"ITEM-0001\", ... }",
    "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "sort_preview": {
      "item_id": "ITEM-0001",
      "region": "NORTE",
      "gate": "GATE_NORTE",
      "actuator_command": "DIVERT_LEFT_01",
      "message": "Direcionar item para canal de expedicao da regiao Norte."
    }
  }
}
```

## Exemplo: ler QR Code

### Request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/qrcode/read" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./exemplos/item-0001.png"
```

### Response (resumida)

```json
{
  "success": true,
  "message": "QR Code lido com sucesso.",
  "data": {
    "item": {
      "id_item": "ITEM-0001",
      "descricao": "Caixa de sensores",
      "regiao_destino": "NORTE",
      "uf_destino": "AM",
      "cidade_destino": "Manaus",
      "timestamp_criacao": "2026-03-13T10:00:00Z"
    },
    "raw_payload": "{\"id_item\":\"ITEM-0001\", ... }",
    "sort_preview": {
      "item_id": "ITEM-0001",
      "region": "NORTE",
      "gate": "GATE_NORTE",
      "actuator_command": "DIVERT_LEFT_01",
      "message": "Direcionar item para canal de expedicao da regiao Norte."
    }
  }
}
```

## Exemplo: gerar QR Code com download direto (PNG)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/qrcode/generate/download" \
  -H "Content-Type: application/json" \
  -d '{
    "id_item": "ITEM-1001",
    "descricao": "Modulo de camera",
    "regiao_destino": "SUDESTE",
    "uf_destino": "SP",
    "cidade_destino": "Sao Paulo"
  }' \
  --output item-1001.png
```

## Exemplo: preview de separacao

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/sort/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "id_item": "ITEM-0099",
    "descricao": "Pacote de teste",
    "regiao_destino": "SUL",
    "uf_destino": "RS",
    "cidade_destino": "Porto Alegre"
  }'
```

## Proximos passos sugeridos

- Integrar captura de camera em tempo real.
- Persistir eventos de leitura/separacao em banco de dados.
- Adicionar autenticacao e autorizacao para operacao em ambiente real.
- Implementar camada de comando para atuadores fisicos (serial/MQTT/PLC).
- Criar testes unitarios e de integracao automatizados.
