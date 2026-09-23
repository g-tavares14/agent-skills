# Spec: codex-specialists

## Objective

Preservar as perspectivas úteis dos quatro arquivos de persona (revisão, segurança, testes e desempenho) por meios que funcionem quando o pacote é instalado como plugin Codex. O fluxo `$review` é a entrada única de revisão; pode usar subagents disponíveis ou executar as perspectivas sequencialmente no contexto principal.

### Acceptance criteria

- `$review` funciona sem custom agent TOML instalado separadamente.
- `$review` executa revisão de qualidade e inclui uma passagem de segurança quando a superfície alterada justificar; confere cobertura/testes e desempenho web quando aplicável.
- Se subagents não estiverem disponíveis, o fluxo conclui as mesmas verificações no contexto principal.
- Instruções não mandam persona iniciar outra persona; a coordenação fica na skill `review`.
- Arquivos e docs não prometem autodiscovery de `agents/*.md` pelo plugin Codex.

## Tech Stack

Skills Agent Skills, referências Markdown e subagents do Codex quando suportados pela sessão. Os papéis são prompts/instruções de workflow, não uma configuração de agentes separada necessária à instalação.

## Commands

```text
$review
$security-and-hardening
$test-driven-development
$performance-optimization
```

## Project Structure

```text
skills/review/                         → wrapper e coordenação da revisão
skills/code-review-and-quality/        → workflow canônico de revisão
skills/security-and-hardening/         → perspectiva de segurança
skills/test-driven-development/        → perspectiva de testes
skills/performance-optimization/       → perspectiva de desempenho
references/                            → checklists reutilizáveis
docs/agents.md                          → explicação dos papéis no Codex
```

## Code Style

Reusar os checklists existentes, limitar delegação a investigações independentes e sintetizar achados com arquivo/linha, gravidade e evidência. Cada passagem especializada deve ter objetivo e saída definidos.

## Testing Strategy

Verificar links internos para skills/checklists, testar revisão com e sem delegação como cenários descritos, e assegurar que a skill de review tem fallback sequencial e não exige nenhum nome de agente customizado.

## Boundaries

- **Always:** Tornar explícito quando uma perspectiva não se aplica e não fabricar resultados de subagents.
- **Ask first:** Adicionar serviços remotos/MCP ou exigir configuração global do usuário.
- **Never:** Depender de mecanismo de persona Grok ou chamar uma habilidade disponível como se fosse um agente Codex instalado.

## Success Criteria

- `$review` funciona a partir de uma instalação limpa do plugin.
- As perspectivas existentes continuam representadas pelas skills/checklists Codex.
- `docs/agents.md` e `references/orchestration-patterns.md` documentam apenas práticas compatíveis com Codex.

## Open Questions

- Nenhuma para a implementação autorizada.
