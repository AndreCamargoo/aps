import threading
import publisher
import consumer
import time
import random
from colorama import init, Fore

# Inicializa o Colorama
init(autoreset=True)

# Lista de cores disponíveis
cores = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.CYAN,
    Fore.MAGENTA,
    Fore.BLUE,
    Fore.WHITE
]

# Função para escolher uma cor aleatória
def escolher_cor_aleatoria():
    return random.choice(cores)

# Função para exibir a mensagem com a cor escolhida
def exibir_mensagem_com_cor(nome_usuario, mensagem, cor):
    print(cor + f"{nome_usuario}: {mensagem}")

def send_message_thread(password, name, cor):    
    while True:
        message = input("")
        if message == "sair":
            print("Saindo do envio de mensagens...")
            break
        
        if len(message) > 128:
            print("Erro: A mensagem não pode exceder 128 caracteres. Tente novamente.")
            continue
        
        # Passando a senha, nome e a cor junto com a mensagem para o publisher
        publisher.main(password, name, message, cor)

def consume_messages_thread(password, cor):
    # Inicia o consumidor para ouvir as mensagens
    consumer.main(password, exibir_mensagem_com_cor, cor)

def main():
    passEncrypt = input("Digite sua senha: ")  # Entrada de senha pelo usuário
    name = input("Digite seu nome: ")
    
    # Escolhendo uma cor para o usuário
    cor = escolher_cor_aleatoria()
    print(cor + f"Conectado como {name}...")

    welcome_message = f"Conectado..."
    publisher.main(passEncrypt, name, welcome_message, cor)  # Notifica entrada
    
    # Criação das threads para enviar e consumir mensagens
    send_thread = threading.Thread(target=send_message_thread, args=(passEncrypt, name, cor))
    consume_thread = threading.Thread(target=consume_messages_thread, args=(passEncrypt, cor))

    # Inicia as threads
    send_thread.start()
    consume_thread.start()

    # Espera as threads terminarem
    send_thread.join()
    consume_thread.join()

if __name__ == "__main__":
    main()
