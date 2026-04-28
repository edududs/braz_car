# BrazCar 🚗

> **Centralize suas caronas, conecte sua comunidade**

Plataforma web para centralizar e organizar caronas compartilhadas entre moradores de cidades rurais do DF e o centro de Brasília, eliminando a necessidade de múltiplos grupos de WhatsApp desorganizados.

[![Django Version](https://img.shields.io/badge/Django-6.0%20alpha-green.svg)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)](https://github.com)

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [O Problema](#-o-problema)
- [A Solução](#-a-solução)
- [Tecnologias](#️-tecnologias)
- [Arquitetura](#-arquitetura)
- [Funcionalidades](#-funcionalidades)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#️-estrutura-do-projeto)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

O **BrazCar** nasceu da necessidade real de moradores de cidades rurais do Distrito Federal que dependem de caronas compartilhadas para se locomover até o centro de Brasília. Atualmente, essas caronas são anunciadas em dezenas de grupos de WhatsApp, causando desorganização, redundância e perda de oportunidades.

### Contexto

Nas cidades rurais do DF:
- O transporte público é **precário** e com horários limitados
- O centro (Brasília) fica **longe** (30-50km em média)
- Moradores criaram **grupos de WhatsApp** para compartilhar caronas
- Com o tempo, surgiram **dezenas de grupos diferentes**
- Mesmas caronas são anunciadas **repetidamente** em vários grupos
- Informações se **perdem** em meio a conversas

---

## 📍 O Problema

### Anúncios Típicos em Grupos de WhatsApp

```
[07/10 15:39] +55 61 9142-9684:
03 VAGAS
Saindo às 19:30 ⏰

🚘 Esplanada
🚘 Eixo Monumental
🚘 Estrutural
🚘 Brazlândia

Chamar PV 📱
7,00 Dinheiro ou PIX
```

### Problemas Identificados

❌ **Redundância** - Mesmas caronas anunciadas em 5-10 grupos diferentes  
❌ **Desorganização** - Informações espalhadas, difíceis de encontrar  
❌ **Perda de Tempo** - Horas procurando caronas em grupos cheios de spam  
❌ **Falta de Filtros** - Não dá para buscar por rota ou horário específico  
❌ **Sem Histórico** - Mensagens antigas desaparecem  
❌ **Sem Avaliações** - Não há sistema de reputação de motoristas  

---

## 🎯 A Solução

O **BrazCar** é uma plataforma centralizada que:

### Benefícios para Passageiros
✅ **Busca Centralizada** - Todas as caronas em um só lugar  
✅ **Filtros Inteligentes** - Busca por origem, destino, horário, preço  
✅ **Candidatura Simplificada** - Um clique para solicitar vaga  
✅ **Avaliações** - Sistema de reputação de motoristas  
✅ **Notificações** - Alertas de novas caronas na sua rota  

### Benefícios para Motoristas
✅ **Anúncio Organizado** - Formulário padronizado para caronas  
✅ **Gerenciamento** - Controle de vagas e candidatos  
✅ **Visibilidade** - Alcance todos os interessados de uma vez  
✅ **Reputação** - Construa histórico positivo de viagens  
✅ **Sem Repetição** - Anuncie uma vez, alcance todos  

---

## 🛠️ Tecnologias

### Backend
- **Django 6.0 alpha** - Framework web Python robusto e escalável
- **Python 3.13** - Linguagem moderna com recursos avançados
- **PostgreSQL** - Banco de dados alvo para ambientes configurados via `DATABASE_URL`
- **SQLite** - Fallback local apenas para bootstrap com `DEBUG=true`
- **Pillow** - Processamento de imagens (fotos de perfil)

### Frontend
- **React 19** - SPA responsável pelo dashboard e pela página pública de detalhes
- **TypeScript 5.9** - Tipagem do frontend e testes do cliente
- **Tailwind CSS 4.1** - Framework CSS utilitário moderno
- **Vite 7.1** - Build tool ultra-rápido com HMR
- **React Router 7** - Roteamento do dashboard e dos detalhes de carona

### Integrações
- **Django Vite** - Integração perfeita entre Django e Vite
- **django-vite 3.1+** - Hot Module Replacement em desenvolvimento

### Desenvolvimento
- **uv** - Gerenciador de pacotes Python e ambientes virtuais
- **Yarn 1 (via Corepack)** - Gerenciador de pacotes JavaScript padronizado no repositório
- **Git** - Controle de versão

---

## 🏗 Arquitetura

### Fluxo atual da aplicação

O BrazCar agora serve um app shell Django mínimo em `/` e `/rides/<id>/`, enquanto a experiência principal roda em uma SPA React carregada via Vite.

```text
Request HTTP
  -> Django URLConf (core/urls.py)
  -> app shell / auth redirect / API Ninja
  -> template templates/app_shell.html
  -> frontend/src/main.tsx
  -> React Router (dashboard e detalhe da carona)
  -> chamadas para /api/ride-listings, /api/me e /events/ride-listings/
```

### Estrutura relevante do repositório

```text
BrazCar/
├── core/                             # Configurações Django e URLConf raiz
├── users/                            # Login, logout, registro e redirects seguros para o app shell
├── src/brazcar/adapters/inbound/http/
│   ├── api_views.py                  # Endpoints HTTP/Ninja consumidos pelo frontend
│   ├── page_views.py                 # Renderização do app shell
│   ├── sse_views.py                  # SSE das listagens de carona
│   └── urls.py                       # /, /rides/<id>/, /api e /events
├── templates/
│   └── app_shell.html                # HTML mínimo com data-* runtime config para a SPA
├── frontend/
│   └── src/
│       ├── main.tsx                  # Entrada React/Vite
│       ├── app/router.tsx            # Rotas do dashboard e detalhe
│       └── features/rides/           # Dashboard, detalhe e testes do fluxo público
├── static/
│   └── css/main.css                  # Estilos Tailwind importados pelo entrypoint React
└── tests/                            # Testes backend/integração da camada HTTP
```

### Fluxo de autenticação e detalhe público

- `GET /users/login/` e `GET /users/register/` não renderizam mais páginas legadas; ambos redirecionam de volta para o app shell.
- O parâmetro `next` é validado no backend antes de qualquer redirect para preservar o fluxo público do detalhe sem abrir redirecionamento inseguro.
- A tela `frontend/src/features/rides/pages/RideDetailPage.tsx` carrega a carona publicamente e usa `/api/me` apenas para decidir se o bloco "Ações futuras" deve aparecer.
- Se a consulta de autenticação falhar, a página de detalhe continua pública e funcional.

### Fluxo de dados

```mermaid
graph LR
    A[Usuário] -->|Abre / ou /rides/7| B[App shell Django]
    B --> C[SPA React]
    C -->|GET| D[/api/ride-listings]
    C -->|GET| E[/api/me]
    C -->|SSE| F[/events/ride-listings/]
    E -->|is_authenticated| G{Mostrar ações futuras?}
    G -->|Sim| H[Bloco autenticado no detalhe]
    G -->|Não| I[Detalhe permanece público]
```

### Modelos de Dados

#### User (users.User)
```python
- username, email, password      # Autenticação
- cpf (unique)                   # Identificação única
- phone                          # Contato
- birth_date                     # Idade
- profile_picture                # Avatar
- is_verified                    # Verificação
- address → Location.Address     # Endereço
```

#### Ride (rides.Ride)
```python
- driver → User                  # Motorista
- vehicle → Vehicle              # Veículo usado
- location_start → Location      # Origem
- location_end → Location        # Destino
- created_at, updated_at         # Timestamps
```

#### RideRequest (rides.RideRequest)
```python
- ride → Ride                    # Carona solicitada
- user → User                    # Passageiro
- created_at, updated_at         # Timestamps
```

---

## ✨ Funcionalidades

### ✅ Implementadas

#### Sistema de Autenticação
- [x] **Login Multi-Campo**: Aceita username, email, CPF ou telefone
- [x] **Backend Customizado**: `MultiFieldBackend` para flexibilidade
- [x] **Proteção CSRF**: Segurança contra ataques
- [x] **Mensagens de Feedback**: Sucesso/erro para o usuário
- [x] **Logout Seguro**: Desconexão com redirecionamento
- [x] **Validação CPF**: Normalização e verificação de CPF

#### Interface do Usuário
- [x] **Dashboard React**: Shell renderizado pelo Django com hidratação via Vite
- [x] **Página pública de detalhe**: `/rides/<id>/` acessível sem login
- [x] **Ações futuras condicionais**: bloco autenticado exibido apenas quando `/api/me` retorna usuário autenticado
- [x] **Ride Cards**: Cards de carona completos e informativos
- [x] **Hot Reload**: Desenvolvimento ágil com Vite HMR
- [x] **Runtime config no shell**: endpoints expostos via `data-*` em `#app-shell`

#### Arquitetura
- [x] **Apps Especializados**: 5 apps Django bem definidos
- [x] **Models Estruturadas**: Relacionamentos claros
- [x] **URLs Namespaced**: Organização clara de rotas
- [x] **Context Processors**: Dados mockados para desenvolvimento
- [x] **Settings Configurados**: Ambiente otimizado

### 🚧 Em Desenvolvimento

- [ ] **Cadastro de Usuários**: Formulário completo com validação
- [ ] **CRUD de Caronas**: Criar, editar, excluir anúncios
- [ ] **Sistema de Busca**: Filtros por origem, destino, horário
- [ ] **Candidaturas**: Solicitação e gerenciamento de vagas
- [ ] **Avaliações**: Sistema de rating entre usuários

### 🔮 Planejadas

- [ ] **Chat Integrado**: Mensagens entre motorista e passageiro
- [ ] **Notificações Push**: Alertas de novas caronas
- [ ] **Pagamentos**: Integração com PIX
- [ ] **App Mobile**: React Native para iOS/Android
- [ ] **Analytics**: Dashboard para motoristas
- [ ] **Rotas Fixas**: Caronas recorrentes

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.13** instalado
- **uv** instalado para gerenciar ambiente virtual e dependências Python
- **Node.js 18+** com **Corepack** habilitado
- **Git** para clonar o repositório

### Passo a Passo

#### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/BrazCar.git
cd BrazCar
```

#### 2. Configure o Ambiente Python
```bash
# Criar e ativar o ambiente virtual com uv
uv venv --python 3.13
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências do projeto e ferramentas de desenvolvimento
uv sync --all-groups
```

#### 3. Configure o Ambiente local
```bash
cp .env.example .env
```

O projeto usa um package de settings:
- `core.settings.dev` para desenvolvimento local
- `core.settings.testing` para pytest
- `core.settings.production` para runtime/container
- `core.settings` aponta para `dev` por padrão para compatibilidade local

Com o `.env.example` padrão, o bootstrap local usa:
- `DJANGO_SETTINGS_MODULE=core.settings.dev`
- `DEBUG=true`
- `DATABASE_URL=sqlite:///db.sqlite3`
- `ALLOWED_HOSTS=localhost,127.0.0.1,[::1]`

Em ambientes não locais, defina explicitamente:
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

Nos testes, o repositório já injeta defaults seguros via `conftest.py`, então `uv run pytest` não depende de export manual de env vars.

Se quiser usar Postgres localmente, edite o `.env`:
```bash
export DJANGO_SETTINGS_MODULE=core.settings.dev
export DEBUG=true
export DATABASE_URL='postgresql://user:pass@localhost:5432/brazcar'
export ALLOWED_HOSTS='localhost,127.0.0.1,[::1]'
```

Depois carregue o arquivo no shell da sua preferência.

A variável `SECRET_KEY` pode ficar ausente no fluxo local com `DEBUG=true`, mas deve existir em qualquer ambiente compartilhado ou de produção.

#### 4. Configure o Banco de Dados
```bash
# Aplicar migrações
uv run python manage.py migrate

# Criar superusuário para acessar o admin
uv run python manage.py createsuperuser
# Siga as instruções e forneça:
# - Username
# - Email
# - CPF (11 dígitos)
# - Phone
# - Birth date
# - Password
```

#### 5. Configure o Frontend
```bash
# Habilitar o Yarn padronizado pelo repositório
corepack enable

# Instalar dependências do Node
corepack yarn install

# Verificar se o Yarn e o Vite estão disponíveis
corepack yarn --version
corepack yarn vite --version
```

#### 6. Inicie os Servidores

**Terminal 1: Django**
```bash
uv run python manage.py runserver
```

**Terminal 2: Vite**
```bash
corepack yarn dev
```

Se quiser forçar outro package de settings localmente:
```bash
DJANGO_SETTINGS_MODULE=core.settings.dev uv run python manage.py runserver
```

#### 7. Execute os testes

**Backend**
```bash
uv run pytest
```

**Frontend**
```bash
corepack yarn test
```

**Checks adicionais**
```bash
uv run pyright
uv run ruff check .
corepack yarn lint
corepack yarn build
```

#### 8. Acesse a Aplicação
- **Frontend**: <http://localhost:8000>
- **Admin Django**: <http://localhost:8000/admin>
- **Vite Dev Server**: <http://localhost:5173>

---

## 💡 Como Usar

### Testando o fluxo público e autenticado

1. **Abra o app shell**
   - Acesse <http://localhost:8000>
   - O Django entrega `templates/app_shell.html` e o React assume a navegação

2. **Explore uma carona pública**
   - Abra uma rota de detalhe, por exemplo: <http://localhost:8000/rides/7/>
   - A página busca a carona em `/api/ride-listings` e continua pública mesmo sem sessão

3. **Verifique o comportamento sensível à autenticação**
   - Sem login, o detalhe não mostra o bloco "Ações futuras"
   - Com `/api/me` autenticado, o detalhe exibe o placeholder de ações futuras
   - Se o lookup de autenticação falhar, o detalhe continua público

4. **Teste login e retorno seguro para o detalhe**
   - Acesse <http://localhost:8000/users/login/?next=/rides/7/>
   - O backend valida `next` e redireciona para o app shell em vez de renderizar templates legados
   - O mesmo comportamento vale para `GET /users/register/`

### Explorando a aplicação

- **Dashboard**: use a home para filtrar e navegar entre caronas
- **Detalhe**: veja informações completas da rota, motorista, veículo e restrições
- **Admin**: gerencie dados via Django Admin
- **Config local**: mantenha `DEBUG=true` no shell local enquanto usar os defaults de bootstrap

---

## 🗂️ Estrutura do Projeto

### Superfícies principais

| Superfície | Descrição |
|-----------|-----------|
| `core/settings/base.py` | Configuração compartilhada entre dev/testing/production |
| `core/settings/dev.py` | Configuração local de desenvolvimento |
| `core/settings/testing.py` | Configuração usada pelo pytest |
| `core/settings/production.py` | Configuração esperada pelo runtime/container |
| `conftest.py` | Bootstrap de env vars para testes Django/pytest |
| `.env.example` | Exemplo mínimo de variáveis para desenvolvimento e produção |
| `templates/app_shell.html` | HTML mínimo servido pelo Django com os `data-*` usados pela SPA |
| `frontend/src/app/router.tsx` | Rotas React para dashboard e detalhe da carona |
| `frontend/src/features/rides/pages/RideDetailPage.tsx` | Detalhe público com lookup opcional de autenticação |
| `frontend/src/features/rides/components/RideDetail.tsx` | Apresentação dos dados da carona e bloco autenticado |
| `tests/adapters/inbound/test_api_views.py` | Regressões do shell, endpoints e redirects do backend |
| `frontend/src/features/rides/__tests__/RideDetailPage.test.tsx` | Regressões do fluxo público/autenticado no detalhe |

### Sistema de Design

**Cores Principais**
- **Primary**: Azul (#3b82f6)
- **Secondary**: Teal (#0d9488)
- **Success**: Verde (#10b981)
- **Error**: Vermelho (#ef4444)
- **Gray Scale**: De gray-50 a gray-900

**Tipografia**
- **Fonte**: Inter (sans-serif)
- **Tamanhos**: Sistema modular do Tailwind

**Componentes Estilizados**
- Botões: `.btn-primary`, `.btn-secondary`
- Inputs: `.form-input`, `.form-label`
- Cards: `.card`, `.card-hover`
- Links: `.nav-link`, `.nav-link.active`

---

## 📊 Roadmap

### v0.2.0 - Alpha (Atual) ✅
- [x] Sistema de autenticação multi-campo
- [x] Interface responsiva e componentes
- [x] Estrutura de banco de dados
- [x] Ambiente de desenvolvimento

### v0.3.0 - Cadastro (Próximo)
- [ ] Formulário de cadastro de usuários
- [ ] Upload de foto de perfil
- [ ] Validação de CPF em tempo real
- [ ] Confirmação de email/telefone

### v0.4.0 - Caronas
- [ ] CRUD completo de caronas
- [ ] Sistema de pontos de parada
- [ ] Validação de horários e datas
- [ ] Formulário intuitivo

### v0.5.0 - Busca e Filtros
- [ ] Sistema de busca avançada
- [ ] Filtros por rota, horário, preço
- [ ] Ordenação de resultados
- [ ] Paginação

### v0.6.0 - Candidaturas
- [ ] Sistema de solicitação de vagas
- [ ] Gerenciamento de candidatos
- [ ] Status de candidatura
- [ ] Notificações básicas

### v0.7.0 - Avaliações
- [ ] Sistema de rating (1-5 estrelas)
- [ ] Comentários sobre viagens
- [ ] Perfil público com histórico
- [ ] Badges de conquistas

### v1.0.0 - MVP
- [ ] Chat integrado
- [ ] Notificações push
- [ ] Testes automatizados
- [ ] Deploy em produção
- [ ] Documentação completa

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Este é um projeto open-source com impacto social real.

### Como Contribuir

1. **Fork** o projeto
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/BrazCar.git`
3. **Crie uma branch**: `git checkout -b feature/nova-funcionalidade`
4. **Commit** suas mudanças: `git commit -m 'Add: nova funcionalidade'`
5. **Push** para a branch: `git push origin feature/nova-funcionalidade`
6. **Abra um Pull Request**

### Diretrizes

- Siga o padrão de código existente
- Escreva testes para novas funcionalidades
- Atualize a documentação quando necessário
- Mensagens de commit claras e descritivas
- Um commit por funcionalidade/correção

### Áreas que Precisam de Ajuda

- Design/UX: Melhorias na interface
- Backend: Novas funcionalidades
- Testes: Cobertura de testes
- Mobile: App React Native
- Documentação: Tutoriais e guias

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Contato e Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/BrazCar/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/BrazCar/discussions)
- **Email**: contato@brazcar.com.br

---

## 🙏 Agradecimentos

Agradecimentos especiais aos moradores das cidades rurais do DF que compartilharam suas experiências e necessidades, tornando este projeto possível.

---

<div align="center">

**BrazCar** - Conectando comunidades através da economia colaborativa 🚗💚

Feito com ❤️ para quem precisa se locomover com dignidade e segurança

[⬆ Voltar ao topo](#brazcar-)

</div>
