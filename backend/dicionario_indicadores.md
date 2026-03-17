# Dicionário de Indicadores - Plataforma Urbix

Este documento detalha os 24 indicadores estratégicos monitorados pela plataforma Urbix, baseados nas normas internacionais **ISO 37120** (Qualidade de Vida), **ISO 37122** (Cidades Inteligentes) e **ISO 37123** (Cidades Resilientes). 

Os indicadores estão divididos em 8 grandes áreas temáticas. Para cada indicador, é apresentada a justificativa técnica e a metodologia matemática de cálculo.

---

## 1. Economia e Finanças

### ECO.1 - Taxa de desemprego da cidade
* **Norma:** ISO 37120
* **Descrição:** Mede a proporção da força de trabalho que se encontra sem emprego, impactando diretamente a vitalidade econômica e a vulnerabilidade social do município.
* **Fórmula:** `(Número de pessoas desempregadas / Força de trabalho total) * 100`
* **Unidade de Medida:** %

### ECO.2 - Despesas de capital como porcentagem das despesas totais
* **Norma:** ISO 37120
* **Descrição:** Indica o montante do orçamento público alocado para projetos de investimento (Capex), como construção de infraestruturas físicas, sociais e críticas.
* **Fórmula:** `(Total de despesas em ativos fixos / Total de despesas do município) * 100`
* **Unidade de Medida:** % ao ano

### ECO.3 - Taxa de sobrevivência de novos negócios
* **Norma:** ISO 37122
* **Descrição:** Avalia o ambiente de inovação, o suporte a startups e a resiliência econômica local perante oscilações de mercado.
* **Fórmula:** `(Total de novos negócios sobreviventes no período / População total da cidade) * 100.000`
* **Unidade de Medida:** empresas ativas / 100.000 habitantes

---

## 2. Governança e Participação

### GOV.1 - Participação dos eleitores nas últimas eleições
* **Norma:** ISO 37120
* **Descrição:** Termômetro do engajamento cívico formal da população e da confiança nas instituições democráticas locais.
* **Fórmula:** `(Número de pessoas que votaram / Número de eleitores registrados) * 100`
* **Unidade de Medida:** %

### GOV.2 - Serviços urbanos solicitados online
* **Norma:** ISO 37122
* **Descrição:** Mede o nível de maturidade digital da prefeitura e a facilidade de acesso do cidadão aos serviços públicos sem necessidade de deslocamento físico.
* **Fórmula:** `(Número de serviços acessíveis 100% online / Total de serviços urbanos oferecidos) * 100`
* **Unidade de Medida:** %

### GOV.3 - Visitas ao portal de dados abertos
* **Norma:** ISO 37122
* **Descrição:** Mensura o interesse público e a efetividade das políticas de transparência e de governo aberto do município.
* **Fórmula:** `(Número anual de visitas ao portal de dados / População total da cidade) * 100.000`
* **Unidade de Medida:** visitas / 100.000 habitantes ao ano

---

## 3. Educação e Tecnologia

### EDU.1 - Graduados em STEM
* **Norma:** ISO 37122
* **Descrição:** Capacidade da cidade de formar capital humano qualificado nas áreas de Ciência, Tecnologia, Engenharia e Matemática (STEM), essencial para uma "Smart City".
* **Fórmula:** `(Número de diplomados em áreas STEM / População total da cidade) * 100.000`
* **Unidade de Medida:** graduados / 100.000 habitantes ao ano

### EDU.2 - Dispositivos de aprendizagem digital por aluno
* **Norma:** ISO 37122
* **Descrição:** Avalia a infraestrutura tecnológica oferecida nas escolas públicas para promover a inclusão digital de crianças e adolescentes.
* **Fórmula:** `(Número de computadores e tablets nas escolas públicas / Total de alunos matriculados) * 1.000`
* **Unidade de Medida:** dispositivos / 1.000 alunos

### EDU.3 - Acesso à Banda Larga
* **Norma:** ISO 37122
* **Descrição:** Percentual da população com acesso à internet de alta velocidade, infraestrutura base para qualquer inovação tecnológica urbana.
* **Fórmula:** `(População com acesso a banda larga / População total da cidade) * 100`
* **Unidade de Medida:** %

---

## 4. Saúde e Bem-Estar

### SAU.1 - Consultas médicas remotas (Telemedicina)
* **Norma:** ISO 37122
* **Descrição:** Utilização de tecnologias de comunicação para a prestação de cuidados médicos à distância, desafogando o sistema presencial.
* **Fórmula:** `(Número anual de teleconsultas realizadas / População total da cidade) * 100.000`
* **Unidade de Medida:** consultas / 100.000 habitantes ao ano

### SAU.2 - População com seguro/plano de saúde
* **Norma:** ISO 37123
* **Descrição:** Mede a resiliência do sistema de saúde local, identificando a proporção de cidadãos que podem recorrer à rede privada, aliviando a rede pública (SUS).
* **Fórmula:** `(Número de pessoas com cobertura de plano de saúde / População total da cidade) * 100`
* **Unidade de Medida:** %

### SAU.3 - Hospitais com geradores de backup
* **Norma:** ISO 37123
* **Descrição:** Capacidade da infraestrutura crítica de saúde de continuar operando e salvando vidas perante apagões ou desastres climáticos.
* **Fórmula:** `(Hospitais com gerador de energia próprio / Total de hospitais da cidade) * 100`
* **Unidade de Medida:** %

---

## 5. Habitação e Planejamento Urbano

### HAB.1 - População vivendo em moradias inadequadas
* **Norma:** ISO 37120
* **Descrição:** Proporção da população em assentamentos precários (favelas), o que amplia a vulnerabilidade a doenças e desastres naturais.
* **Fórmula:** `(Pessoas em moradias inadequadas / População total da cidade) * 100`
* **Unidade de Medida:** %

### HAB.2 - Área mapeada em tempo real (SIG)
* **Norma:** ISO 37122
* **Descrição:** Cobertura de ferramentas de Sistema de Informação Geográfica (SIG) ativas para planejamento, zoneamento e gestão urbana baseada em dados.
* **Fórmula:** `(Área territorial mapeada no SIG em km² / Área total da cidade em km²) * 100`
* **Unidade de Medida:** %

### HAB.3 - Edifícios vulneráveis a desastres
* **Norma:** ISO 37123
* **Descrição:** Mapeamento de passivos de infraestrutura, indicando imóveis construídos em encostas, áreas de alagamento ou com falhas estruturais graves.
* **Fórmula:** `(Edifícios estruturalmente vulneráveis ou em risco / Total de edifícios na cidade) * 100`
* **Unidade de Medida:** %

---

## 6. Segurança e Proteção

### SEG.1 - Agentes de polícia por 100.000 habitantes
* **Norma:** ISO 37120
* **Descrição:** Medida do efetivo das forças de segurança em tempo integral disponível para o patrulhamento preventivo e ostensivo.
* **Fórmula:** `(Total de policiais e guardas em tempo integral / População total da cidade) * 100.000`
* **Unidade de Medida:** agentes / 100.000 habitantes

### SEG.2 - Número de homicídios
* **Norma:** ISO 37120
* **Descrição:** Taxa padronizada de letalidade violenta intencional, sendo o principal termômetro global de segurança pública.
* **Fórmula:** `(Homicídios registrados no ano / População total da cidade) * 100.000`
* **Unidade de Medida:** homicídios / 100.000 habitantes ao ano

### SEG.3 - Cobertura de câmeras de vigilância digital
* **Norma:** ISO 37122
* **Descrição:** Extensão do território urbano monitorado por sistemas de CFTV interligados à central de inteligência do município.
* **Fórmula:** `(Área coberta por câmeras em km² / Área urbana total da cidade em km²) * 100`
* **Unidade de Medida:** %

---

## 7. Meio Ambiente e Saneamento

### AMB.1 - Lixo plástico reciclado
* **Norma:** ISO 37122
* **Descrição:** Eficiência da gestão de resíduos sólidos e das políticas de economia circular voltadas aos polímeros plásticos.
* **Fórmula:** `(Total de plástico reciclado em toneladas / Total de plástico consumido ou gerado em toneladas) * 100`
* **Unidade de Medida:** %

### AMB.2 - Monitoramento de água em tempo real
* **Norma:** ISO 37122
* **Descrição:** Proporção da rede de distribuição hídrica equipada com sensores inteligentes de telemetria para detecção imediata de vazamentos e perdas.
* **Fórmula:** `(Volume de água monitorada remotamente / Volume total de água distribuída) * 100`
* **Unidade de Medida:** %

### AMB.3 - Cobertura de copas de árvores
* **Norma:** ISO 37123
* **Descrição:** Disponibilidade de infraestrutura verde para o conforto térmico, infiltração de água no solo e mitigação do efeito "ilha de calor".
* **Fórmula:** `(Área territorial coberta por árvores em km² / Área total da cidade em km²) * 100`
* **Unidade de Medida:** %

---

## 8. Resiliência e Desastres

### RES.1 - População afetada por desastres
* **Norma:** ISO 37123
* **Descrição:** Impacto humano direto e anual provocado por ameaças naturais (enchentes, deslizamentos, vendavais).
* **Fórmula:** `(Pessoas evacuadas, feridas ou desalojadas / População total da cidade) * 100`
* **Unidade de Medida:** % ao ano

### RES.2 - Equipes de emergência treinadas
* **Norma:** ISO 37123
* **Descrição:** Nível de preparação técnica dos órgãos de primeira resposta (Defesa Civil, Bombeiros) para atuar em cenários de catástrofe.
* **Fórmula:** `(Equipes de resgate com treinamento específico em desastres / Total de equipes de emergência) * 100`
* **Unidade de Medida:** %

### RES.3 - Perdas econômicas por desastres
* **Norma:** ISO 37123
* **Descrição:** Avaliação monetária dos danos causados à infraestrutura pública e privada, em alinhamento com as diretrizes do Marco de Sendai.
* **Fórmula:** `(Soma financeira das perdas em infraestrutura e serviços / PIB da cidade) * 100`
* **Unidade de Medida:** % do PIB ao ano