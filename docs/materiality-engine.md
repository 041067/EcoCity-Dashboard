# Materiality Engine

O Materiality Engine da Sprint 7 avalia cada tema ESG de uma organização para um ano de reporte. Ele foi desenhado para ser determinístico, explicável e auditável: a API recebe apenas os critérios de entrada e calcula todos os scores no backend.

## Escalas e normalização

Cada critério usa a escala de 1 (muito baixo) a 5 (muito alto). A média dos critérios é normalizada para uma escala de 0 a 100:

`score normalizado = média dos critérios / 5 × 100`

Portanto, uma avaliação preenchida com a escala atual fica entre 20 e 100. O intervalo 0 a 100 permanece suportado pelo motor para composição e classificação, além de permitir metodologias futuras que tenham componentes nulos.

### Impacto

O eixo de impacto é a média normalizada de:

- Severidade
- Escopo
- Probabilidade
- Remediabilidade

### Financeiro

O eixo financeiro é a média normalizada de:

- Impacto em receita
- Impacto em custos
- Impacto em ativos
- Impacto em financiamento
- Impacto regulatório

### Stakeholders

Para cada stakeholder são registrados relevância, nível de preocupação e influência. O score consolidado é a média normalizada de todos esses valores. Pelo menos um stakeholder é necessário para concluir uma avaliação.

## Score e prioridade

O score é calculado exclusivamente no servidor:

`materialidade = impacto × peso_impacto + financeiro × peso_financeiro + stakeholders × peso_stakeholders`

Os pesos padrão são configuráveis por ambiente e precisam somar `1.0`:

```env
MATERIALITY_IMPACT_WEIGHT=0.40
MATERIALITY_FINANCIAL_WEIGHT=0.40
MATERIALITY_STAKEHOLDER_WEIGHT=0.20
```

| Score | Prioridade |
|---:|---|
| 0–39 | Baixa |
| 40–59 | Média |
| 60–79 | Alta |
| 80–100 | Crítica |

## Integridade e auditoria

- Um tema só pode ser avaliado se estiver ativo para a organização.
- Há uma única avaliação por organização, tema e ano de reporte.
- Avaliações concluídas são imutáveis; um novo ano cria um novo registro histórico.
- Evidências são adicionadas de forma cumulativa e nunca substituem o cálculo.
- O endpoint de explicação retorna os componentes, critérios brutos, avaliações de stakeholders, evidências e pesos aplicados.
- A API rejeita campos de score enviados pelo cliente e valida limites tanto na camada Pydantic quanto no banco de dados.

## Limitações da Sprint 7

Esta metodologia é um mecanismo inicial e configurável; ela não substitui avaliação especializada, due diligence ou requisitos legais. Não inclui IA, ingestão externa, inventário de emissões, cálculo de ROI ou recomendações automáticas.
