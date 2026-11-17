import shutil
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
import gspread

load_dotenv()
client = genai.Client(http_options={"timeout": 20000})


class AnaliseCorrida(BaseModel):
    eh_corrida: bool = Field(description="True se o print for um treino de corrida/esteira, False caso contrário.")
    data: str = Field(description="Data do treino no formato DD/MM/AAAA.")
    modalidade: str = Field(description="Corrida de Rua ou Esteira.")
    treino_identificado: str = Field(description="Ex: Semana 1 - Segunda (ou 'Treino Livre' se não corresponder à tabela).")
    treino_prescrito: str = Field(description="Treino prescrito na tabela para aquele dia.")
    distancia_km: float = Field(description="Distância percorrida em km.")
    duracao: str = Field(description="Tempo total do treino no formato HH:MM:SS ou MM:SS.")
    pace_medio: str = Field(description="Ritmo médio no formato MM:SS.")
    fc_media: int = Field(description="Frequência cardíaca média em bpm (0 se ausente).")
    cadencia: int = Field(description="Cadência média em spm (0 se ausente).")
    calorias: int = Field(description="Calorias gastas em kcal.")
    feedback_ia: str = Field(description="Análise curta comparando pace e FC executados com as zonas-alvo Z1-Z4 prescritas.")


def conectar_planilha():
    gc = gspread.service_account(filename="credentials.json")
    planilha = gc.open("Controle de Corridas")
    return planilha.worksheet("Corridas")


def analisar_print(caminho_print: Path, imagem_plano: Image.Image) -> AnaliseCorrida:
    imagem_treino = Image.open(caminho_print)

    prompt = """
    Você é um treinador de corrida analisando a evolução de um atleta rumo aos 5 km sub-30min.
    Você recebeu DUAS imagens:
    1) A primeira imagem é a tabela do plano de treinos (Semanas 1 a 4, com zonas Z1 a Z4).
    2) A segunda imagem é o print do resumo do treino no app Samsung Health.

    Tarefas:
    - Verifique se o print é realmente uma corrida (rua ou esteira). Se não for, marque eh_corrida como False.
    - Extraia as métricas exatas do print do Samsung Health.
    - Cruze a data/dia da semana, a duração total e a estrutura do treino do print com a primeira imagem para identificar qual treino prescrito foi executado.
    - Escreva um feedback técnico objetivo comparando o realizado com o prescrito.
    """

    modelos = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-4-hydrogen"]
    ultimo_erro = None

    for modelo in modelos:
        try:
            resposta = client.models.generate_content(
                model=modelo,
                contents=[imagem_plano, imagem_treino, prompt],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AnaliseCorrida,
                    "temperature": 0.2,
                },
            )
            return AnaliseCorrida.model_validate_json(resposta.text)
        except Exception as erro:
            ultimo_erro = erro
            print(f" -> Modelo {modelo} indisponível no momento, tentando alternativa...")

    raise ultimo_erro


def main():
    pasta_novos = Path("prints_novos")
    pasta_processados = Path("prints_processados")
    caminho_plano = Path("plano_treinos.png")

    if not caminho_plano.exists():
        print("Erro: Arquivo 'plano_treinos.png' não encontrado na pasta raiz.")
        return

    extensoes_validas = {".jpg", ".jpeg", ".png"}
    prints = [f for f in pasta_novos.iterdir() if f.suffix.lower() in extensoes_validas]

    if not prints:
        print("Nenhum print novo encontrado na pasta 'prints_novos'.")
        return

    print(f"Encontrados {len(prints)} print(s). Conectando ao Google Sheets...")
    aba_corridas = conectar_planilha()
    imagem_plano = Image.open(caminho_plano)

    for arquivo in prints:
        print(f"\nAnalisando '{arquivo.name}'...")
        try:
            resultado = analisar_print(arquivo, imagem_plano)

            if not resultado.eh_corrida:
                print(f" -> Ignorado: '{arquivo.name}' não é um treino de corrida.")
            else:
                nova_linha = [
                    resultado.data,
                    resultado.modalidade,
                    resultado.treino_identificado,
                    resultado.treino_prescrito,
                    resultado.distancia_km,
                    resultado.duracao,
                    resultado.pace_medio,
                    resultado.fc_media,
                    resultado.cadencia,
                    resultado.calorias,
                    resultado.feedback_ia,
                ]
                aba_corridas.append_row(nova_linha, value_input_option="USER_ENTERED")
                print(f" -> Sucesso: '{resultado.treino_identificado}' salvo na planilha.")
                print(f" -> Feedback: {resultado.feedback_ia}")

            shutil.move(str(arquivo), str(pasta_processados / arquivo.name))

        except Exception as erro:
            print(f" -> Erro ao processar '{arquivo.name}': {erro}")


if __name__ == "__main__":
    main()