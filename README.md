# 🏀 NBA Medical Intelligence System

Plataforma inteligente para monitoramento, análise e predição de lesões na NBA utilizando **Machine Learning**, **Case-Based Reasoning (CBR)** e análise médica aplicada.

Este projeto foi desenvolvido como um **projeto acadêmico** com foco em inteligência artificial aplicada à saúde esportiva, analytics médicos e sistemas inteligentes de suporte à decisão.

---

## 📌 Objetivo do Projeto

O objetivo do sistema é centralizar informações sobre lesões de jogadores da NBA e fornecer recursos de:

- Monitoramento de lesões
- Histórico médico esportivo
- Predição de tempo de recuperação
- Classificação de gravidade
- Inteligência baseada em casos (CBR)
- Visualização analítica de dados médicos

O sistema busca explorar como técnicas de **IA aplicada** podem auxiliar no entendimento de padrões de lesões esportivas.

---

## 🚀 Funcionalidades

### 📊 Dashboard Inteligente
- KPIs médicos
- Estatísticas de lesões
- Jogadores mais lesionados
- Times mais afetados
- Insights automáticos

### 🏀 Gestão de Jogadores
- Cadastro de jogadores
- Informações físicas
- Histórico esportivo
- Busca e filtros

### 🏥 Gestão de Lesões
- Cadastro de lesões
- Histórico detalhado
- Status médicos
- Dias afastado
- CID médico
- Cirurgia realizada
- Observações clínicas

### 🧠 Inteligência Artificial
#### Machine Learning
- Predição de tempo de recuperação
- Classificação de gravidade
- Engenharia de features médicas

#### Case-Based Reasoning (CBR)
- Busca de casos médicos similares
- Comparação entre históricos
- Apoio à decisão médica

### 📂 Upload de Dados
- Importação CSV
- Atualização de base médica
- Integração de datasets

---

## 🛠️ Tecnologias Utilizadas

### Backend
- Python
- Flask
- SQLite

### Data Science & IA
- Pandas
- NumPy
- Scikit-Learn
- Machine Learning
- Case-Based Reasoning (CBR)

### Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript
- Chart.js

---

## 📁 Estrutura do Projeto

```plaintext
nba-medical-intelligence-system/
│
├── app.py
├── config.py
│
├── templates/
├── static/
│
├── data/
│   ├── historico_lesoes_gold.csv
│   ├── jogadores_corrigido.csv
│   └── cbr_nba_cases_real.csv
│
├── modelos/
│
├── train_recovery_model.py
├── train_severity_models.py
└── cbr_nba_engine.py
```

## ⚙️ Como Executar

### 1. Clonar o projeto

```bash
git clone https://github.com/VictorAbrum/nba-injury-system.git
```

### 2. Entrar na pasta

```bash
cd nba-injury-system
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar o sistema

```bash
python app.py
```

---

## 📈 Machine Learning

O sistema utiliza modelos de Machine Learning para:

- Predição do tempo de recuperação
- Classificação de gravidade da lesão
- Análise de risco médico

Features utilizadas incluem:

- Histórico de lesões
- Dias totais lesionado
- Tipo de lesão
- Grupo corporal
- Recorrência
- Gravidade
- Informações físicas do atleta

---

## 🔬 Status do Projeto

🚧 Em desenvolvimento contínuo

Melhorias futuras:

- Melhorias no dataset médico
- Mais modelos preditivos
- Explicabilidade do ML
- API médica
- Novos dashboards
- Deploy online

---

## 👨‍💻 Autor

**Victor Abrum**  
Estudante de Sistemas de Informação

Projeto acadêmico focado em **IA aplicada à saúde esportiva**.