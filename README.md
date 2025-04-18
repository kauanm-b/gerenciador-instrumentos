# Sistema de Gerenciamento de Instrumentos

Sistema para gerenciamento e controle de instrumentos de medição, incluindo importação de dados do SharePoint, geração de relatórios e análise de dados.

## Funcionalidades

- Importação de dados de instrumentos do SharePoint
- Armazenamento em banco de dados SQLite
- Interface gráfica para visualização e gerenciamento
- Geração de relatórios em Excel
- Análise de dados e estatísticas

## Estrutura do Projeto

```
.
├── data/           # Dados da aplicação
├── logs/           # Logs do sistema
├── src/            # Código fonte
│   ├── core/       # Lógica principal
│   ├── database/   # Camada de banco de dados
│   ├── gui/        # Interface gráfica
│   ├── tools/      # Scripts e ferramentas
│   └── utils/      # Utilitários
└── tests/          # Testes automatizados
```

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Copie `.env.example` para `.env` e configure as variáveis de ambiente

## Uso

1. Execute a aplicação principal:
   ```bash
   python -m src.main
   ```

2. Para análise da base de dados:
   ```bash
   python -m src.tools.analisar_base
   ```

## Manutenção

- Os logs são armazenados em `logs/`
- Backups do banco de dados são gerados em `backups/`
- Arquivos temporários são salvos em `data/`

## Licença

Uso interno - Todos os direitos reservados 