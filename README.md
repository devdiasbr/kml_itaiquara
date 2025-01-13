# KML Itaiquara

Gerador de arquivos KML para visualização de distribuidores e municípios no Google Earth.

## 📋 Descrição

Este projeto é um sistema automatizado para geração de arquivos KML (Keyhole Markup Language) que permite visualizar a distribuição geográfica de distribuidores e municípios no Google Earth. O sistema processa dados de diferentes fontes, unifica as informações e gera arquivos KML organizados por tipo de unidade e estrutura hierárquica.

## 🚀 Funcionalidades

- Processamento de múltiplas bases de dados
- Geração de KMLs separados por tipo de unidade
- Geração de KML unificado com toda a estrutura
- Visualização de polígonos dos municípios
- Informações detalhadas de cada distribuidor
- Cores únicas para identificação visual
- Estrutura hierárquica organizada (Tipo Unidade > Unidade > Razão Social > Municípios)

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Bibliotecas principais:
  - `simplekml`: Geração de arquivos KML
  - `pandas`: Processamento de dados
  - `os`: Manipulação de arquivos e diretórios

## 📁 Estrutura do Projeto

```
KML Itaiquara/
├── data/               # Diretório com os dados de entrada
├── dist/              # Diretório com os arquivos processados
│   └── data/          # Cópia dos arquivos processados
├── src/               # Código fonte
│   ├── config.py      # Configurações do projeto
│   ├── data_processor.py # Processamento dos dados
│   ├── kml_generator.py  # Geração dos arquivos KML
│   └── utils.py       # Funções utilitárias
└── main.py            # Script principal
```

## 🔧 Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install simplekml pandas
```

## 💻 Como Usar

1. Coloque os arquivos de dados na pasta `data/`
2. Execute o script principal:
```bash
python main.py
```

O script irá:
1. Processar os dados das diferentes bases
2. Gerar os arquivos KML organizados por tipo de unidade
3. Gerar um arquivo KML unificado
4. Copiar todos os arquivos processados para a pasta `dist/data/`

## 📊 Estrutura dos KMLs Gerados

Os arquivos KML são organizados em uma estrutura hierárquica:

- Tipo de Unidade
  - Unidade
    - Razão Social
      - Municípios (com informações detalhadas)

Cada município contém:
- Nome e UF
- População
- Informações do distribuidor
- Contatos
- Endereço da sede

## 🎨 Visualização

- Cada razão social possui uma cor única para fácil identificação
- Municípios sem coordenadas são representados por pontos
- Municípios com coordenadas são representados por polígonos
- Estilo normal e highlight para melhor interatividade

## 📝 Notas

- Os arquivos são gerados tanto na pasta `data/` quanto em `dist/data/`
- Municípios sem coordenadas são centralizados em Brasília
- As cores são geradas automaticamente para cada razão social
- O sistema suporta diferentes tipos de unidades e estruturas organizacionais

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das suas alterações
4. Faça push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença [Adicionar tipo de licença].
