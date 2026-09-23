# Spec: codex-workflows

## Objective

Padronizar o ciclo de engenharia do pacote como cinco skills explícitas para Codex: `$spec` → `$plan` → `$build` → `$verify` → `$review`. Skills de especialidade continuam disponíveis fora do ciclo. Atalhos antigos que duplicam etapas ou dependem de slash commands do Grok são removidos.

### Acceptance criteria

- Existem exatamente cinco atalhos de ciclo com nomes `spec`, `plan`, `build`, `verify` e `review`.
- `verify` aponta para o fluxo de testes/TDD; `review` aponta para revisão final e inclui critérios relevantes de segurança, qualidade e testes.
- Não existem atalhos de ciclo `$test`, `$plan-work`, `$review-code` ou `$ship`.
- As skills canônicas explicam invocação e comportamento no Codex; referências a `/agent-skills:*` e ferramentas Grok são removidas ou substituídas por capacidades equivalentes.
- Exemplos de código continuam em TypeScript/Python, conforme `AGENTS.md`.

## Tech Stack

Agent Skills padrão: diretório por skill com `SKILL.md` contendo `name` e `description`; `agents/openai.yaml` para apresentação e política de invocação explícita quando necessário.

## Commands

```text
$spec
$plan
$build
$verify
$review
```

## Project Structure

```text
skills/spec/       → atalho para spec-driven-development
skills/plan/       → atalho para planning-and-task-breakdown
skills/build/      → implementação incremental + TDD
skills/verify/     → verificação e fluxo orientado por testes
skills/review/     → revisão final multi-eixo
skills/*/SKILL.md  → workflows especializados/canônicos
AGENTS.md          → orientação específica do Codex
```

## Code Style

Usar frontmatter YAML com identificador minúsculo estável; descrições concisas e específicas sobre gatilhos; wrappers devem delegar à skill canônica sem duplicar suas instruções. Escrever instruções em frases diretas e usar comandos Codex válidos.

## Testing Strategy

Verificar que há exatamente um atalho para cada etapa, que wrappers apontam para skills existentes e que descrições não instruem uso de slash commands Grok. Testar manualmente a descoberta dos cinco nomes pelo seletor de skills após instalação.

## Boundaries

- **Always:** Preservar a ordem do ciclo e os checkpoints de aprovação existentes nas workflows canônicas.
- **Ask first:** Alterar o conteúdo substantivo dos workflows especializados ou a política de checkpoints.
- **Never:** Reintroduzir uma sexta etapa principal ou fingir que aliases são slash commands do Codex.

## Success Criteria

- Os cinco aliases são consistentes no README, manifests, AGENTS e skills.
- `verify` cobre a validação técnica; `review` produz achados e decisão final de prontidão.
- Skills fora do ciclo continuam acessíveis pelo nome canônico.

## Open Questions

- Nenhuma para a implementação autorizada.
