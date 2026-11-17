# 🏃‍♂️ AI Running Performance Tracker

Automação em Python que utiliza **Visão Computacional Multimodal (Google Gemini API)** para cruzar screenshots de treinos do **Samsung Health** com uma planilha visual de periodização de corrida, extraindo métricas estruturadas e registrando avaliações técnicas de performance diretamente no **Google Sheets**.

## 🚀 Arquitetura e Funcionalidades

- **Análise Multimodal Cruzada:** Envia simultaneamente a imagem da tabela de treinos prescritos (semanas e zonas de frequência cardíaca Z1–Z4) e o print do smartwatch para identificar qual treino foi executado e avaliar o cumprimento das metas.
- **Structured Outputs (Saída Estruturada):** Utiliza **Pydantic** para garantir que o LLM retorne um JSON estritamente tipado, filtrando automaticamente atividades que não sejam corrida.
- **Resiliência e Fallback:** Implementa timeout de rede e rotação automática entre modelos (`gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-4-hydrogen`) para contornar picos de indisponibilidade (HTTP 503).
- **Integração com Google Sheets:** Autenticação via Service Account (`gspread`) para persistência automática dos dados e movimentação dos arquivos já processados.

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3
- **IA / LLM:** Google GenAI SDK (Gemini Multimodal)
- **Validação de Dados:** Pydantic
- **Processamento de Imagem:** Pillow (PIL)
- **Integração:** Google Sheets API (`gspread`)

## 📁 Estrutura do Projeto

```text
corrida-ai-tracker/
├── main.py                 # Script principal de análise e integração
├── plano_treinos.png       # Imagem da tabela de periodização (Semanas 1 a 4)
├── requirements.txt        # Dependências do projeto
├── .gitignore              # Arquivos ignorados pelo Git (.env, credentials.json, prints)
├── prints_novos/           # Diretório de entrada para novos screenshots
└── prints_processados/     # Diretório para onde os prints são movidos após registro
```

## ⚙️ Como Executar Localmente

1. **Clone o repositório e instale as dependências:**
   ```bash
   git clone https://github.com/gustavoocdp/corrida-ai-tracker.git
   cd corrida-ai-tracker
   pip install -r requirements.txt
   ```

2. **Configure a chave da API do Gemini:**
   Crie um arquivo `.env` na raiz do projeto e adicione sua chave do Google AI Studio:
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   ```

3. **Configure o acesso ao Google Sheets:**
   - Crie uma Service Account no Google Cloud Console com acesso às APIs **Google Sheets** e **Google Drive**.
   - Baixe a chave JSON, renomeie para `credentials.json` e coloque na raiz do projeto.
   - Crie uma planilha chamada **Controle de Corridas** com uma aba chamada **Corridas** e compartilhe-a como *Editor* com o e-mail da Service Account.

4. **Execute a automação:**
   Adicione a imagem do seu plano como `plano_treinos.png`, insira os screenshots do Samsung Health na pasta `prints_novos/` e rode:
   ```bash
   python main.py
   ```