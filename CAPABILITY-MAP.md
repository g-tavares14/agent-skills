# Mapa de capacidades: migração exclusiva para Codex

## Objetivo e premissas

O pacote terá como destinos o Codex CLI e o Codex no app ChatGPT, autenticados pela conta ChatGPT. Conversas comuns do ChatGPT não são um destino desta migração. O ciclo principal terá exatamente cinco entradas: `$spec` → `$plan` → `$build` → `$verify` → `$review`. Skills especializadas podem continuar disponíveis fora desse ciclo. O suporte a Grok Build será encerrado.

## Módulos

| ID estável | Responsabilidade verificável | Depende de |
|---|---|---|
| `codex-package` | Definir o manifesto, o catálogo, a instalação e a validação do plugin para Codex CLI e app; retirar os artefatos de distribuição exclusivos do Grok. | — |
| `codex-workflows` | Adaptar as skills e os atalhos para o ciclo único spec → plan → build → verify → review; incorporar a verificação de testes em `verify`, retirar `ship` do ciclo e substituir referências operacionais a comandos e ferramentas de outros agentes. | `codex-package` |
| `codex-specialists` | Preservar revisão, segurança, testes e auditoria de desempenho com um mecanismo suportado pelo Codex; definir como `review` utiliza esses papéis e as verificações finais. | `codex-workflows` |
| `codex-guardrails` | Decidir e implementar o equivalente Codex do `simplify-ignore`, incluindo contrato de eventos, tratamento seguro dos arquivos e testes de recuperação; retirar a configuração de hook exclusiva do Grok. | `codex-package` |

**Ordem:** `codex-package` → `codex-workflows` → `codex-specialists`; `codex-guardrails` pode seguir após `codex-package` em paralelo aos fluxos.

Cada módulo terá sua própria especificação `SPEC-<ID>.md` após a aprovação deste mapa. O mapa será o índice das especificações; os limites entre módulos e os critérios de aceitação serão definidos nelas.

## Base observada antes da migração

- A distribuição Codex já usa `.codex-plugin/plugin.json` e `.agents/plugins/marketplace.json`; `plugin.json`, `.grok-plugin/`, `commands/` e `agents/*.md` ainda contêm contratos do Grok.
- Há 31 arquivos `SKILL.md`, incluindo seis atalhos explícitos para Codex. Os atalhos atuais usam `$plan-work`, `$test`, `$review-code` e `$ship`, que serão substituídos ou retirados do ciclo de cinco etapas. Parte dos fluxos canônicos ainda cita `/agent-skills:*` e ferramentas de outros ambientes.
- `hooks/hooks.json` e `hooks/simplify-ignore.sh` usam eventos e variáveis do Grok. O script substitui trechos no próprio arquivo durante a leitura e restaura depois, comportamento que precisa de requisito explícito de segurança e recuperação.

## Fontes oficiais para a próxima fase

- [Empacotamento de plugins](https://developers.openai.com/plugins/build/plugins)
- [Criação de skills](https://learn.chatgpt.com/docs/build-skills)
- [Hooks do Codex](https://learn.chatgpt.com/docs/hooks)
- [Subagents e agentes personalizados](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## Decisões confirmadas

- O mapa e a ordem foram aprovados pelo usuário.
- O ciclo tem cinco etapas: `$spec` → `$plan` → `$build` → `$verify` → `$review`.
- O contrato de `simplify-ignore` permanece; a implementação do Codex não pode reescrever o arquivo-fonte durante leitura.
