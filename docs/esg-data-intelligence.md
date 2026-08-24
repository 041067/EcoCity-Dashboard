# ESG Data Intelligence — Sprint 8

Sprint 8 cria uma camada de evidências externas entre os provedores públicos e o Materiality Engine. A materialidade continua sendo calculada exclusivamente pelas avaliações de impacto, finanças e stakeholders da Sprint 7; evidências externas não alteram scores automaticamente.

```text
Provider → Raw payload → NormalizationService → ESGIndicator / IndicatorValue
                                                   ↓
                                            EvidenceService → Material topic
```

## Modelo e proveniência

`ESGIndicator` é o catálogo universal: código, nome, pilar, categoria, unidade, descrição e tipo de fonte. `IndicatorValue` é uma observação imutável e também o cache no banco. Ele guarda unidade, fonte, referência, latitude/longitude, horário observado, horário de coleta, metadados e os scores explícitos de qualidade, relevância, confiança e atualização.

O vínculo `MaterialityEvidence` registra quais observações externas sustentam uma avaliação material. Assim, uma evidência sempre pode ser rastreada até seu indicador, site, provider e horário.

## Providers e frequência

| Provider | Categorias | Frequência | Fallback |
|---|---|---:|---|
| Open-Meteo | clima, ar, energia, água | 15 min | último valor no banco |
| OpenAQ | ar | 1 h | último valor no banco |
| NASA POWER | clima histórico, energia | diária | último valor no banco |
| INPE | território | diária | último valor no banco |
| ANEEL | energia | diária | último valor no banco |

OpenAQ precisa de `OPENAQ_API_KEY`. INPE e ANEEL usam endpoints configuráveis por `INPE_API_URL` e `ANEEL_API_URL`, porque seus datasets e contratos de acesso variam. A ausência dessas configurações marca somente a fonte como indisponível; nunca derruba a aplicação.

Todos os clientes usam HTTPS, timeout, uma repetição limitada para falhas transitórias, cache por provider/site e circuit breaker após falhas consecutivas. Logs de sincronização registram provider, status, categoria, duração e mensagem sem incluir credenciais.

## Riscos climáticos

`ClimateRiskService` deriva risco de calor, seca, inundação, vento e estresse hídrico por regras de limiar versionadas. Os níveis são `low`, `moderate`, `high` e `critical`; não há geração de risco por IA.

## APIs

| Método | Rota | Uso |
|---|---|---|
| GET | `/api/v1/esg/indicators` | catálogo de indicadores |
| GET | `/api/v1/esg/providers` | status e último sync dos providers |
| GET | `/api/v1/esg/organizations/{id}/indicators` | observações da organização |
| GET | `/api/v1/esg/sites/{id}/indicators` | observações do site |
| GET | `/api/v1/esg/sites/{id}/climate-risk` | riscos determinísticos |
| GET | `/api/v1/esg/sites/{id}/air-quality` | qualidade do ar |
| GET | `/api/v1/esg/sites/{id}/energy` | contexto energético/solar |
| POST | `/api/v1/esg/sites/{id}/sync` | sincronização administrativa resiliente |
| GET | `/api/v1/esg/materiality/{id}/evidence` | evidências externas da matriz |

O frontend oferece a tela `/esg/intelligence` para escolher uma unidade, sincronizar dados e consultar suas evidências. A matriz de materialidade exibe as evidências vinculadas ao tema selecionado.
