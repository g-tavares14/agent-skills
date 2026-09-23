# Spec: codex-package

## Objective

Distribuir este pacote como plugin nativo do Codex CLI e do Codex no app ChatGPT. Remover as superfícies de distribuição próprias do Grok. O pacote contém skills e, opcionalmente, um hook local que o usuário pode revisar e confiar.

### Acceptance criteria

- Um manifesto portátil na raiz identifica `agent-skills`, sua versão, licença, repositório e apresentação no Codex.
- O manifesto aponta para o hook Codex quando habilitado; o diretório raiz `skills/` é descoberto como conteúdo do plugin.
- O marketplace do repositório aponta para o plugin e corresponde ao nome/versão declarados.
- Instruções cobrem instalação no CLI e descoberta pelo marketplace local do app, sem passos Grok.
- A instalação CLI via sparse checkout inclui o catálogo e os arquivos referenciados pelo plugin localizado na raiz.
- Arquivos Grok e o overlay Codex duplicado deixam de ser fontes de configuração.

## Tech Stack

Markdown, JSON, Python 3 standard library para validação local. Plugin portable Agent Plugins com extensão OpenAI para interface e hook do Codex.

## Commands

```bash
python3 -m json.tool plugin.json
python3 -m json.tool .agents/plugins/marketplace.json
codex plugin --help
```

## Project Structure

```text
plugin.json                    → manifesto portátil do plugin
.agents/plugins/marketplace.json → catálogo local para o app
skills/                        → skills empacotadas
hooks/hooks.json               → hook opcional do Codex
README.md                      → instalação e uso
```

## Code Style

JSON válido, indentado com dois espaços e sem chaves de produto Grok. A interface deve nomear as cinco etapas com os mesmos termos do README: spec, plan, build, verify e review.

## Testing Strategy

Validar JSON com `python3 -m json.tool`; revisar correspondência entre manifest e marketplace; validar instalação/documentação contra a documentação oficial de plugins e marketplace do Codex. A instalação real no app requer ação do usuário na interface e confiança explícita do hook.

## Boundaries

- **Always:** Manter `name` e `version` coerentes entre manifest e marketplace; manter paths relativos à raiz do plugin.
- **Ask first:** Renomear o repositório remoto ou publicar o pacote no diretório público.
- **Never:** Depender de manifest, comando, evento ou variável exclusiva de Grok.

## Success Criteria

- O manifest raiz usa o esquema portátil e declara as capacidades OpenAI/Codex em `extensions.com.openai`.
- O marketplace local aponta para o manifest raiz.
- README e instruções de instalação explicam Codex CLI e app.
- Nenhuma referência operacional a instalação do Grok permanece.

## Open Questions

- Nenhuma para a implementação autorizada. A publicação pública permanece fora do escopo.
