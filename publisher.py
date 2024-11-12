# Importação das bibliotecas necessárias
import pika  # Biblioteca para trabalhar com RabbitMQ
import json  # Biblioteca para manipulação de JSON
import encrypt  # Módulo customizado para criptografar a mensagem
import os  # Biblioteca para interação com o sistema operacional, como variáveis de ambiente
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class RabbitMQPublisher:
    """
    Classe para gerenciar a publicação de mensagens no RabbitMQ.
    """

    def __init__(self) -> None:
        # Carrega as configurações de conexão do RabbitMQ a partir das variáveis de ambiente ou usa valores padrão
        self.__host = os.getenv('RABBITMQ_HOST', 'localhost')  # Endereço do servidor RabbitMQ
        self.__port = os.getenv('RABBITMQ_PORT', 5672)  # Porta do RabbitMQ
        self.__username = os.getenv('RABBITMQ_USER', 'guest')  # Usuário para autenticação no RabbitMQ
        self.__password = os.getenv('RABBITMQ_PASSWORD', 'guest')  # Senha para autenticação
        self.__vhost = os.getenv('RABBITMQ_VHOST', 'gbakvcim')  # Virtual host do RabbitMQ
        self.__exchange = "fanout_exchange"  # Nome da exchange do RabbitMQ (fanout)
        self.__channel = self.__create_channel()  # Cria o canal de comunicação com o RabbitMQ

    def __create_channel(self):
        """
        Cria e retorna um canal de comunicação com o RabbitMQ.
        """
        # Parâmetros de conexão com o RabbitMQ
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,  # Endereço do RabbitMQ
            port=self.__port,  # Porta do RabbitMQ
            virtual_host=self.__vhost,  # Virtual host
            credentials=pika.PlainCredentials(  # Credenciais para autenticação
                username=self.__username,  # Nome de usuário
                password=self.__password  # Senha
            )
        )

        # Estabelece uma conexão e cria um canal de comunicação
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()

        # Declara a exchange de tipo 'fanout', o que significa que ela irá distribuir mensagens para todos os consumidores
        channel.exchange_declare(
            exchange=self.__exchange,  # Nome da exchange
            exchange_type='fanout',  # Tipo 'fanout' significa que todas as mensagens são enviadas para todos os consumidores
            durable=True  # Garantia de que a exchange será durável
        )
        return channel  # Retorna o canal criado

    def send_message(self, body: dict):
        """
        Envia uma mensagem para a fila do RabbitMQ.
        """
        self.__channel.basic_publish(
            exchange=self.__exchange,  # Define a exchange como 'fanout_exchange'
            routing_key='',  # Em uma exchange 'fanout' não há necessidade de um routing key
            body=json.dumps(body),  # Converte o corpo da mensagem para formato JSON
            properties=pika.BasicProperties(
                delivery_mode=2  # Define a mensagem como persistente, ou seja, ela será salva no disco do RabbitMQ
            )
        )

# Função principal que será chamada quando o publisher for usado
def main(password, name, message, cor):
    """
    Função principal para criptografar a mensagem e publicá-la no RabbitMQ.
    """
    rabbitMq_publisher = RabbitMQPublisher()  # Instancia o publisher do RabbitMQ
    
    # Criptografa a mensagem usando a função do módulo 'encrypt'
    iv, encrypted_message, salt = encrypt.encrypt_message(message, password)

    # Prepara a mensagem a ser enviada, incluindo o nome, IV, salt e a mensagem criptografada
    message_to_send = {
        'name': name,  # Nome do usuário que está enviando a mensagem
        'iv': iv.hex(),  # IV (Initial Vector) em formato hexadecimal
        'salt': salt.hex(),  # Salt (valor aleatório usado na criptografia) em formato hexadecimal
        'encrypted_message': encrypted_message.hex(),  # A mensagem criptografada em formato hexadecimal
        'cor': cor  # A cor que será associada à mensagem
    }

    # Envia a mensagem criptografada para o RabbitMQ
    rabbitMq_publisher.send_message(message_to_send)

# A seguir, o bloco abaixo garante que o código no arquivo 'publisher.py' não será executado automaticamente
# se o arquivo for importado como módulo em outro lugar, mas só será executado se chamado diretamente.
if __name__ == "__main__":
    pass  # Não há necessidade de executar nada diretamente quando o módulo é carregado
