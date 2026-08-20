# 🏙️ Urbix: Plataforma Híbrida de Ranqueamento de Cidades Inteligentes

**Urbix** é uma plataforma analítica desenvolvida como projeto de Iniciação Científica (CNPq) no curso de Engenharia de Computação da Universidade Tecnológica Federal do Paraná (UTFPR). 

O sistema foi desenhado para consolidar dados governamentais dispersos em um *Data Lake* unificado e aplicar o método multicritério **TOPSIS** (*Technique for Order of Preference by Similarity to Ideal Solution*) para avaliar e ranquear o nível de maturidade de municípios brasileiros. A matriz de avaliação é estritamente fundamentada nas normas internacionais **ISO 37120**, **ISO 37122** e **ISO 37123 (Marco de Sendai)**.

---

## 🎯 Propósito e Justificativa

Atualmente, gestores públicos e pesquisadores enfrentam grande dificuldade para comparar a eficiência das cidades devido à fragmentação de dados em diferentes esferas governamentais (IBGE, DataSUS, SICONFI, INEP). 

O Urbix resolve esse problema atuando em duas frentes:
1. **Engenharia de Dados (ETL):** Extrai, limpa e padroniza dados brutos de mais de 100 planilhas e arquivos locais governamentais, construindo denominadores padronizados (ex: per capita, por 100 mil habitantes, porcentagem).
2. **Motor Matemático (TOPSIS):** Transforma esses dados brutos em uma Matriz de Decisão normalizada, considerando pesos e direções de impacto (benefícios vs. custos), gerando um "Índice Smart" de 0 a 1 que permite a comparação justa entre cidades de portes diferentes.

---

## 🏗️ Estrutura do Projeto (Monorepo)

O projeto adota uma arquitetura de Monorepo, separando a extração de dados da visualização:

### ⚙️ Backend (Python / FastAPI)
O motor de dados e cálculos.
* **`app/etl_config.py`**: O dicionário de dados central. Mapeia como o sistema deve ler planilhas `.csv`, `.xls` e `.ods`, cruzando "numeradores" (ex: número de homicídios) com "denominadores base" (ex: população total).
* **`app/services/topsis_core.py`**: A implementação matemática do algoritmo TOPSIS.
* **`app/routers/`**: APIs RESTful que servem os cálculos matemáticos sob demanda.
* **Data Lake (SQLite/Pandas):** Processamento em lotes (batch) para armazenamento estático do histórico das cidades.

### 💻 Frontend (React / Vite)
A interface de *Data Visualization*.
* **Dashboard Híbrido:** Permite ao usuário cruzar dados reais do banco com simulações de cenários hipotéticos inseridos na interface, sem corromper o banco de dados oficial.
* **Radar Charts (`react-chartjs-2`):** Visualização de desempenho relativo das cidades separadas por eixos temáticos (escala de 0 a 100), facilitando a identificação visual de pontos fortes e fracos da gestão municipal.

---

## 📊 Matriz de Indicadores Oficiais

A arquitetura do Urbix mapeia **47 indicadores** estruturados em **6 Eixos Temáticos**. 

### 1. Economia & Governança 💰
* Taxa de desemprego (CAGED)
* Taxa de endividamento (SICONFI)
* Despesas de capital (SICONFI)
* Receita própria (SICONFI)
* Orçamento per capita (IBGE/PIB)
* Mulheres eleitas (TSE)
* Condenações por corrupção (CNJ)
* Participação eleitoral (TSE)

### 2. Urbanismo & Segurança 🏘️
* Moradias inadequadas (MUNIC)
* População sem-teto (CadÚnico)
* Efetivo de bombeiros (MUNIC)
* Mortes por incêndio (DataSUS SIM)
* Agentes de polícia (MUNIC)
* Taxa de homicídios (FBSP)
* Acidentes industriais (Min. do Trabalho)

### 3. Educação & Inovação 📚
* Relação estudante/professor (ATU)
* IDEB Anos Iniciais (INEP)
* Sobrevivência de novos negócios (CAGED)
* Empregos em TIC (CAGED)
* Graduados em áreas STEM (INEP Superior)

### 4. Sustentabilidade & Smart City (ISO 37122) 🌳
* Energia gerada por resíduos (SINISA)
* Iluminação com telegestão (MUNIC)
* Medidores inteligentes de energia (ANEEL)
* Edifícios verdes certificados (GBC Brasil)
* Monitoramento de ar em tempo real (MMA)
* Serviços urbanos online (MUNIC)
* Prontuário eletrônico (CNES)
* Consultas remotas (CNES)
* Medidores inteligentes de água (SNIS)
* Áreas cobertas por câmeras (MUNIC)
* Lixeiras com sensores (SINISA)
* Semáforos inteligentes (Denatran)
* Frota de ônibus zero emissão (Senatran)
* Escolas conectadas (MUNIC)
* População com seguro contra ameaças (SUSEP)
* Empregos informais (CAGED)

### 5. Resiliência a Desastres (ISO 37123 / Sendai) 🚨
* Escolas com plano de emergência (INEP)
* População treinada para emergência
* Hospitais com gerador backup (CNES)
* População com seguro saúde básico (ANS)
* Taxa de imunização (DataSUS PNI)
* Abrigos de emergência (MUNIC)
* Edifícios vulneráveis a desastres
* Rotas de evacuação identificadas
* Reservas de alimentos para 72h (Defesa Civil)
* Mapas de ameaças públicos
* Mortalidade por desastres (S2ID)
* Pessoas afetadas por desastres (S2ID)
* Perdas econômicas por desastres (S2ID)
* Danos à infraestrutura básica

### 6. Conectividade 📶
* Densidade de banda larga fixa (Anatel)

---

## 🚧 Status Atual e Trabalhos Futuros

Para manter o rigor metodológico da pesquisa, foi aplicado um **congelamento de escopo (*Code Freeze*)**. 

* **Status Atual:** A infraestrutura matemática (Motor TOPSIS), o painel de visualização (Radar Charts) e o pipeline de banco de dados (SQLite) estão 100% operacionais. Atualmente, **11 indicadores foram extraídos, limpos e validados com sucesso**, servindo como base irrefutável de testes para comprovar a eficácia da arquitetura do ranqueamento.
* **O que falta (Trabalhos Futuros):** A matriz listada acima contém indicadores cujas fontes brutas (*Data Lake*) possuem formatações de planilhas governamentais altamente complexas (ex: abas aninhadas, falha em chaves primárias do IBGE, células mescladas). O desenvolvimento de *scripts* individuais de tratamento de dados (*Data Wrangling*) para os 36 indicadores restantes é a próxima etapa natural do projeto para obter uma cobertura de 100% da norma ISO.

---
*Desenvolvido por Murilo Fontana Muniz — Iniciação Científica, Universidade Tecnológica Federal do Paraná (UTFPR).*