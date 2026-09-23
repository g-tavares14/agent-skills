# Spec: codex-guardrails

## Objective

Migrar `simplify-ignore` para um hook Codex que protege blocos marcados sem modificar o arquivo fonte ao lê-lo. A checagem deve negar chamadas `apply_patch` que alterem ou removam blocos reconhecidos; formatos ambíguos falham fechados com motivo legível.

### Acceptance criteria

- O hook usa o formato de evento `PreToolUse` do Codex, matcher `apply_patch` e `tool_input.command`.
- O hook nunca substitui conteúdo por placeholder nem grava cache/backups no workspace.
- Patches que preservam os blocos são permitidos; patches que mudam, removem, truncam ou tornam ambíguo um bloco são negados com instrução clara.
- Blocos fora da região marcada podem ser editados quando o patch puder ser analisado sem ambiguidade.
- A documentação descreve confiança do hook via Codex e a limitação de que comandos shell e editores externos não passam por este matcher.
- Testes Python cobrem patch válido, alteração protegida, edição externa ao bloco e entradas malformadas.

## Tech Stack

Python 3 standard library, hook `command` nativo e JSON de hooks do Codex. Nenhuma dependência runtime adicional.

## Commands

```bash
python3 -m unittest discover -s hooks -p 'test_*.py'
python3 -m py_compile hooks/simplify_ignore_guard.py
```

## Project Structure

```text
plugin.json                 → aponta para hooks/hooks.json
hooks/hooks.json            → matcher Codex PreToolUse
hooks/simplify_ignore_guard.py → valida o patch sem alterar fontes
hooks/test_simplify_ignore_guard.py → testes unitários
hooks/SIMPLIFY-IGNORE.md    → sintaxe, comportamento, confiança e limites
```

## Code Style

Python tipado quando isso melhora clareza; parser conservador, funções pequenas, erros em JSON conforme o contrato do evento, saída de diagnóstico em `stderr`. Sem dependências externas.

## Testing Strategy

Testes unitários devem provar que blocos protegidos permanecem idênticos após patches permitidos e que alterações/formatos não analisáveis são negados. Executar a suíte com `unittest`; compilar o módulo com `py_compile`.

## Boundaries

- **Always:** Manter o arquivo fonte como única fonte da verdade; negar em caso de dúvida; explicar o caminho de recuperação sem automaticamente reescrever o arquivo.
- **Ask first:** Mudar a sintaxe dos marcadores ou ampliar o hook para bloquear comandos shell gerais.
- **Never:** Escrever placeholders ou conteúdo original ao disco durante leitura; apagar/repor arquivos do usuário como mecanismo de recuperação.

## Success Criteria

- Nenhum evento ou variável Grok permanece no hook.
- Nenhum caminho de execução modifica o workspace durante leitura.
- Os testes demonstram proteção fail-closed para operações `apply_patch` que não podem ser analisadas com segurança.

## Open Questions

- A cobertura do hook é limitada às ferramentas Codex interceptadas; alterações via shell/editor externo devem continuar cobertas pelas instruções do workflow e revisão do diff.
