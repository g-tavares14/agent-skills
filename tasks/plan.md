# Implementation Plan: migração exclusiva para Codex

## Overview

Reempacotar Agent Skills como plugin Codex portátil, simplificar o ciclo principal para cinco skills, migrar as perspectivas de review para fluxos suportados e substituir o hook que reescreve arquivos por uma guarda Codex segura.

## Architecture Decisions

- Usar `plugin.json` portátil na raiz e `extensions.com.openai` para interface e hooks; remover o overlay `.codex-plugin` duplicado.
- Manter `skills/` na raiz, que é o diretório do conteúdo do plugin; manter os cinco atalhos como skills explícitas.
- Representar personas pela composição de skills e checklists com fallback inline, sem requerer agentes customizados globais para instalação.
- Implementar `simplify-ignore` em `PreToolUse` para `apply_patch`; não alterar o arquivo durante leitura.
- Atualizar documentação antes de remover artefatos Grok para manter cada incremento compreensível.

## Task List

### Phase 1: Plugin e fluxo principal
- [x] Task 1: Criar o manifesto portable e atualizar o catálogo local.
- [x] Task 2: Renomear e ajustar os aliases para spec, plan, build, verify e review.
- [x] Task 3: Atualizar documentação de uso e instruções do repositório para Codex.

### Checkpoint: Package e workflow
- [x] Manifestos JSON válidos e consistentes.
- [x] Exatamente cinco aliases do ciclo descritos e sem referências operacionais de outras plataformas.

### Phase 2: Especialistas e compatibilidade
- [x] Task 4: Integrar as perspectivas especializadas ao fluxo review e às docs.
- [x] Task 5: Remover comandos, manifests e referências exclusivas do Grok.

### Checkpoint: Fluxos
- [x] Skills e links internos resolvem.
- [x] Review tem fallback sem custom agents ou subagents.

### Phase 3: Hook seguro
- [x] Task 6: Escrever testes do parser e do bloqueio de patches protegidos.
- [x] Task 7: Implementar hook PreToolUse fail-closed sem mutação de arquivos.
- [x] Task 8: Atualizar a documentação do `simplify-ignore` e retirar testes/script legados.

### Checkpoint: Completo
- [x] JSON e referências validados.
- [x] Suíte unitária do hook passa.
- [x] Busca final não encontra instruções operacionais exclusivas de outras plataformas.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Plugin portátil e hook precisam ser confiados pelo usuário | Hook pode não executar até revisão no Codex | Documentar revisão de hook e manter skill textual como fallback |
| Parser de patch pode receber formato não suportado | Modificação protegida escaparia ou edição legítima seria bloqueada | Negar chamadas ambíguas e testar formatos válidos; limitar cobertura ao `apply_patch` |
| Subagents variam por sessão/superfície | Review poderia depender de configuração ausente | Instruir fallback sequencial inline |

## Open Questions

- Nenhuma para o escopo autorizado.
