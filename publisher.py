import pika
import json
import encrypt
import os
from dotenv import load_dotenv

load_dotenv()

class RabbitMQPublisher:
    
    def __init__(self) -> None:
        self.__host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.__port = os.getenv('RABBITMQ_PORT', 5672)
        self.__username = os.getenv('RABBITMQ_USER', 'guest')
        self.__password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.__vhost = os.getenv('RABBITMQ_VHOST', 'gbakvcim')
        self.__exchange = "fanout_exchange"
        self.__channel = self.__create_channel()
    
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

        # Declarando a exchange do tipo 'fanout' e durável
        channel.exchange_declare(
            exchange=self.__exchange,  # Nome da exchange
            exchange_type='fanout', # Tipo da exchange
            durable=True # Durável
        )
        return channel
    
    def send_message(self, body: dict):
        self.__channel.basic_publish(
            exchange=self.__exchange,  # Usando a exchange 'fanout_exchange'
            routing_key='',  # Não usamos routing_key em fanout
            body=json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=2  # Tornando a mensagem persistente
            )
        )

def main(password, name, message, cor):
    rabbitMq_publisher = RabbitMQPublisher()
    
    # Criptografar a mensagem
    iv, encrypted_message, salt = encrypt.encrypt_message(message, password)
    
    # Preparar a mensagem a ser enviada, incluindo o nome
    message_to_send = {
        'name': name,  # Inclui o nome
        'iv': iv.hex(),  # Convertendo para hexadecimal
        'salt': salt.hex(),
        'encrypted_message': encrypted_message.hex(),
        'cor': cor  # Passando a cor para a mensagem
    }
    
    # Enviar a mensagem criptografada
    rabbitMq_publisher.send_message(message_to_send)


if __name__ == "__main__":
    pass  # Não há necessidade de código executável aqui diretamente.
