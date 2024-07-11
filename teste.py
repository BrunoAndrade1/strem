import os
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Verificar se a chave da API está carregada corretamente
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada. Verifique o arquivo .env.")

# Inicialização do cliente OpenAI
client = OpenAI(api_key=api_key)

# Função para gerar respostas do modelo
def get_response(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# Inicializar o histórico de mensagens
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# Loop para interação contínua
while True:
    user_input = input("Você: ")
    if user_input.lower() in ['sair', 'exit', 'quit']:
        print("Encerrando a conversa.")
        break

    # Adicionar a mensagem do usuário ao histórico
    messages.append({"role": "user", "content": user_input})
    
    # Obter resposta do modelo
    assistant_response = get_response(messages)
    
    # Adicionar a resposta do assistente ao histórico
    messages.append({"role": "assistant", "content": assistant_response})
    
    # Imprimir a resposta do assistente
    print("Assistente:", assistant_response)
