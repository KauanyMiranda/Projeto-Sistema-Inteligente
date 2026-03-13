# Documentacao Tecnica da API

## 1. Visao geral do projeto

Este projeto implementa a base de uma API para automacao logistica academica, com foco em leitura de QR Code e decisao de separacao por regiao do Brasil em uma esteira simulada (prototipo Lego).

## 2. Objetivo da API

A API foi desenhada para:

- Gerar QR Codes contendo dados estruturados de itens.
- Ler/decodificar QR Codes a partir de imagens via OpenCV.
- Validar o conteudo decodificado com schemas Pydantic.
- Determinar a acao de separacao logistica com base na regiao de destino.
- Servir de base para futura integracao com camera em tempo real e controle de atuadores.

## 3. Arquitetura inicial

Arquitetura em camadas:

- `app/api`: camada HTTP (roteamento e contratos externos).
- `app/schemas`: contratos de entrada/saida e validacoes.
- `app/services`: regras de negocio (geracao/leitura de QR e logica de separacao).
- `app/core`: configuracoes globais e tratamento de excecoes.
- `app/utils`: utilitarios transversais.
- `app/models`: reservado para evolucao futura (ORM/entidades).

Decisoes principais:

- Respostas padronizadas com envelope (`success`, `message`, `data`).
- Erros padronizados (`success=false`, `error.code`, `error.details`).
- Regioes representadas por `Enum` para reduzir inconsistencias.

## 4. Fluxos principais

### Fluxo A: Geracao de QR Code

1. Cliente envia JSON do item para `POST /api/v1/qrcode/generate`.
2. API valida o payload com Pydantic.
3. Service serializa item em JSON e gera imagem QR (PNG) com `qrcode`.
4. API retorna:
   - item estruturado,
   - payload serializado,
   - QR em base64,
   - preview da decisao de separacao.

### Fluxo B: Leitura de QR Code

1. Cliente envia imagem via `multipart/form-data` para `POST /api/v1/qrcode/read`.
2. API valida tipo/tamanho do arquivo.
3. OpenCV decodifica a imagem e tenta extrair QR.
4. Conteudo extraido e validado contra schema esperado.
5. API retorna dados do item e sugestao de separacao.

### Fluxo C: Preview de separacao

1. Cliente envia dados do item para `POST /api/v1/sort/preview`.
2. API aplica regra por `regiao_destino`.
3. API retorna `gate` e `actuator_command` sugeridos.

## 5. Endpoints existentes

### Sistema

- `GET /` - status geral da aplicacao.
- `GET /api/v1` - status da versao da API.
- `GET /api/v1/health` - healthcheck.
- `GET /api/v1/config` - configuracoes basicas carregadas.
- `GET /api/v1/regions` - regioes validas suportadas.

### QR Code

- `POST /api/v1/qrcode/generate`
  - Entrada: dados do item.
  - Saida: item validado, payload JSON, QR base64 e preview de separacao.

- `POST /api/v1/qrcode/generate/download`
  - Entrada: dados do item.
  - Saida: arquivo PNG do QR Code com download direto (`Content-Disposition: attachment`).

- `POST /api/v1/qrcode/read`
  - Entrada: upload de imagem com QR.
  - Saida: payload bruto, dados validados e preview de separacao.

### Sorting

- `POST /api/v1/sort/preview`
  - Entrada: dados do item.
  - Saida: decisao de separacao por regiao.

## 6. Regras de negocio iniciais

Regioes aceitas:

- `NORTE`
- `NORDESTE`
- `CENTRO_OESTE`
- `SUDESTE`
- `SUL`

Campos esperados no QR:

- `id_item`
- `descricao`
- `regiao_destino`
- `uf_destino`
- `cidade_destino`
- `timestamp_criacao`

Regra atual de separacao:

- Mapeamento fixo de `regiao_destino` para `gate` e `actuator_command`.
- Servico de separacao foi abstraido para facilitar troca por implementacao real de hardware.

## 7. Tratamento de erros

Casos cobertos:

- payload invalido (`422 INVALID_REQUEST`);
- imagem invalida/corrompida (`400 INVALID_IMAGE`);
- QR ausente na imagem (`404 QRCODE_NOT_FOUND`);
- QR malformado/JSON invalido (`422 QRCODE_MALFORMED`);
- falhas internas (`500 INTERNAL_SERVER_ERROR`).

## 8. Proximos passos esperados

- Adicionar testes automatizados (unitarios e integracao).
- Integrar com captura de camera em stream.
- Persistir historico de leituras e decisoes.
- Criar fila/event bus para comandos de atuadores.
- Implementar camada de driver para hardware (serial, MQTT, PLC).
- Adicionar autenticacao, autorizacao e auditoria para uso real.
