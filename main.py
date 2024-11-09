import threading
import publisher
import consumer
import time

def send_message_thread(password):    
    while True:
        message = input("")
        if message == "sair":
            print("Saindo do envio de mensagens...")
            break
        
        if len(message) > 128:
            print("Erro: A mensagem não pode exceder 128 caracteres. Tente novamente.")
            break
        
        # Agora vamos passar a mensagem para a função de envio.
        publisher.main(password, message)  # Passando senha e mensagem para o publisher

def consume_messages_thread(password):
    # Inicia o consumidor para ouvir as mensagens
    consumer.main(password)  # Passando a senha para o consumidor

def main():
    passEncrypt = input("Digite sua senha: ")  # Entrada de senha pelo usuário
    name = input("Digite seu nome: ")
    
    publisher.main(passEncrypt, "Contectado...") # Notifica entrada...
    
    # Criação das threads para enviar e consumir mensagens
    send_thread = threading.Thread(target=send_message_thread, args=(passEncrypt,))
    consume_thread = threading.Thread(target=consume_messages_thread, args=(passEncrypt,))

    # Inicia as threads
    send_thread.start()
    consume_thread.start()

    # Espera as threads terminarem (se necessário)
    send_thread.join()
    consume_thread.join()

if __name__ == "__main__":
    main()
