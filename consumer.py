import pika
import json
import encrypt
import os
from dotenv import load_dotenv
from functools import partial  # Importação para usar o `partial`

load_dotenv()

class RabbitMQConsumer:
    
    def __init__(self, callback, passEncrypt) -> None:
        self.__host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.__port = os.getenv('RABBITMQ_PORT', 5672)
        self.__username = os.getenv('RABBITMQ_USER', 'guest')
        self.__password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.__vhost = os.getenv('RABBITMQ_VHOST', 'gbakvcim')
        self.__exchange = "fanout_exchange"  # Exchange de tipo 'fanout'
        self.__queue = ""  # Consumidores não precisam de fila fixa em fanout
        self.__callback = callback
        
        # Atribuindo a senha corretamente para o objeto
        self._passEncrypt = passEncrypt  # A senha agora é atribuída corretamente
    
        self.__channel = self.__create_channel()  # Criando o canal para consumir
    
    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            virtual_host=self.__vhost,
            credentials=pika.PlainCredentials(
                username=self.__username,
                password=self.__password
            )
        )
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()

        # Declare a exchange do tipo 'fanout'
        channel.exchange_declare(
            exchange=self.__exchange,  # Nome da exchange
            exchange_type='fanout',  # Tipo da exchange
            durable=True  # Durável
        )

        # Declare uma fila anônima (para cada consumidor)
        result = channel.queue_declare(queue='', exclusive=True)  # Fila exclusiva
        self.__queue = result.method.queue

        # Vincula a fila à exchange do tipo 'fanout'
        channel.queue_bind(exchange=self.__exchange, queue=self.__queue)

        # Usando `partial` para garantir que passEncrypt seja passado corretamente
        callback_with_pass = partial(self.__callback, passEncrypt=self._passEncrypt)

        # Configura o callback do consumidor
        channel.basic_consume(
            queue=self.__queue,
            auto_ack=True,
            on_message_callback=callback_with_pass  # Passando o callback modificado
        )
        
        return channel
    
    def start(self):
        # Inicia o consumidor
        self.__channel.start_consuming()

def queue_callback(ch, method, properties, body, passEncrypt):
    message = json.loads(body.decode())
    
    # Extraindo os dados da mensagem
    iv = bytes.fromhex(message['iv'])
    salt = bytes.fromhex(message['salt'])
    encrypted_message = bytes.fromhex(message['encrypted_message'])
    name = message['name']  # Obtendo o nome da mensagem
    cor = message['cor']  # Obtendo a cor da mensagem

    # A senha está sendo passada corretamente para a função de descriptografar
    password = passEncrypt

    # Descriptografando a mensagem
    try:
        decrypted_message = encrypt.decrypt_message(encrypted_message, password, iv, salt)
        print(cor + f"{name}: {decrypted_message}")
    except ValueError:
        print("Não foi possível abrir essa mensagem. A senha pode estar incorreta ou a mensagem está corrompida.")

def main(passEncrypt, exibir_mensagem_com_cor, cor):
    rabbitMq_consumer = RabbitMQConsumer(queue_callback, passEncrypt)
    rabbitMq_consumer.start()

if __name__ == "__main__":
    pass  # Não há necessidade de código executável aqui diretamente.
