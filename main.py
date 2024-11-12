# Importação das bibliotecas necessárias
import threading  # Para gerenciar threads e execução paralela
import publisher  # Módulo customizado para enviar mensagens 
import consumer   # Módulo customizado para consumir mensagens 
import random     # Para gerar números aleatórios
from colorama import init, Fore  # Biblioteca para colorir o texto no terminal

# Inicializa o Colorama para manipulação das cores no terminal
init(autoreset=True)

# Lista de cores que serão usadas para colorir as mensagens
cores = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.CYAN,
    Fore.MAGENTA,
    Fore.BLUE, 
    Fore.WHITE
]

# Função para escolher uma cor aleatória da lista
def escolher_cor_aleatoria():
    return random.choice(cores)  # Retorna uma cor aleatória da lista 'cores'

# Função para exibir a mensagem com a cor escolhida
def exibir_mensagem_com_cor(nome_usuario, mensagem, cor):
    print(cor + f"{nome_usuario}: {mensagem}")  # Exibe a mensagem colorida com o nome do usuário

# Função que será executada pela thread de envio de mensagens
def send_message_thread(password, name, cor):    
    while True:
        message = input("")  # Solicita que o usuário digite uma mensagem
        if message == "sair":  # Condição de saída
            print("Saindo do envio de mensagens...")  # Mensagem indicando que o envio foi encerrado
            break  # Sai do loop se o usuário digitar "sair"
        
        if len(message) > 128:  # Verifica se a mensagem ultrapassa o limite de 128 caracteres
            print("Erro: A mensagem não pode exceder 128 caracteres. Tente novamente.")  # Exibe erro
            continue  # Volta ao início do loop e solicita nova mensagem
        
        # Passa a senha, nome, mensagem e cor para o módulo publisher para enviar a mensagem
        publisher.main(password, name, message, cor)

# Função que será executada pela thread de consumo de mensagens
def consume_messages_thread(password, cor):
    # Inicia o consumidor que irá ouvir e exibir as mensagens recebidas
    consumer.main(password, exibir_mensagem_com_cor, cor)

# Função principal que gerencia o fluxo do programa
def main():
    passEncrypt = input("Digite sua senha: ")  # Solicita ao usuário a senha
    name = input("Digite seu nome: ")  # Solicita ao usuário o nome

    # Escolhe uma cor aleatória para o usuário
    cor = escolher_cor_aleatoria()  
    print(cor + f"Conectado como {name}...")  # Exibe uma mensagem indicando a conexão do usuário com a cor escolhida

    welcome_message = f"Conectado..."  # Mensagem de boas-vindas
    # Publica a mensagem de boas-vindas com a senha, nome e cor
    publisher.main(passEncrypt, name, welcome_message, cor)

    # Criação da thread para envio de mensagens
    send_thread = threading.Thread(target=send_message_thread, args=(passEncrypt, name, cor))
    # Criação da thread para consumo de mensagens
    consume_thread = threading.Thread(target=consume_messages_thread, args=(passEncrypt, cor))

    # Inicia as threads
    send_thread.start()  
    consume_thread.start()

    # Espera as threads terminarem antes de encerrar o programa
    send_thread.join()
    consume_thread.join()

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    main()  # Chama a função principal para iniciar a execução do programa
