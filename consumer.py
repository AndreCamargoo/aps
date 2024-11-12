# Importação das bibliotecas necessárias
import pika  # Biblioteca para interação com RabbitMQ
import json  # Biblioteca para manipulação de dados em formato JSON
import encrypt  # Módulo customizado para descriptografar a mensagem
import os  # Biblioteca para acessar variáveis de ambiente do sistema operacional
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env
from functools import partial  # Função para criar funções parcialmente aplicadas (útil para passar parâmetros adicionais)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class RabbitMQConsumer:
    """
    Classe para gerenciar o consumo de mensagens do RabbitMQ.
    """

    def __init__(self, callback, passEncrypt) -> None:
        """
        Inicializa o consumidor configurando a conexão com o RabbitMQ e o callback a ser utilizado
        para processar as mensagens recebidas.
        """
        # Carrega as configurações de conexão a partir das variáveis de ambiente
        self.__host = os.getenv('RABBITMQ_HOST', 'localhost')  # Endereço do RabbitMQ
        self.__port = os.getenv('RABBITMQ_PORT', 5672)  # Porta do RabbitMQ
        self.__username = os.getenv('RABBITMQ_USER', 'guest')  # Nome de usuário
        self.__password = os.getenv('RABBITMQ_PASSWORD', 'guest')  # Senha de acesso
        self.__vhost = os.getenv('RABBITMQ_VHOST', 'gbakvcim')  # Virtual host do RabbitMQ
        self.__exchange = "fanout_exchange"  # Nome da exchange do tipo 'fanout' que será usada
        self.__queue = ""  # Inicializa a fila como vazia (a fila será criada dinamicamente)
        self.__callback = callback  # Função de callback que será chamada quando uma mensagem for recebida
        
        # A senha é atribuída corretamente ao objeto
        self._passEncrypt = passEncrypt  # A senha usada para descriptografar as mensagens
    
        # Cria o canal de comunicação com o RabbitMQ
        self.__channel = self.__create_channel()

    def __create_channel(self):
        """
        Cria e configura o canal de comunicação com o RabbitMQ para consumir mensagens.
        """
        # Configurações de conexão com o RabbitMQ, incluindo credenciais e parâmetros
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,  # Endereço do RabbitMQ
            port=self.__port,  # Porta de conexão
            virtual_host=self.__vhost,  # Virtual host
            credentials=pika.PlainCredentials(  # Credenciais de acesso (usuário e senha)
                username=self.__username,
                password=self.__password
            )
        )

        # Estabelece uma conexão e cria um canal
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()

        # Declara a exchange de tipo 'fanout', garantindo que ela seja durável
        channel.exchange_declare(
            exchange=self.__exchange,  # Nome da exchange
            exchange_type='fanout',  # Tipo 'fanout' (distribui mensagens para todos os consumidores)
            durable=True  # Durável, ou seja, a exchange sobrevive a reinicializações
        )

        # Declara uma fila anônima e exclusiva, que será destruída quando o consumidor parar
        result = channel.queue_declare(queue='', exclusive=True)
        self.__queue = result.method.queue  # Recupera o nome da fila criada dinamicamente

        # Vincula a fila à exchange para que ela receba as mensagens da exchange 'fanout'
        channel.queue_bind(exchange=self.__exchange, queue=self.__queue)

        # Usa o `partial` para criar uma função de callback com a senha (passEncrypt) corretamente passada
        callback_with_pass = partial(self.__callback, passEncrypt=self._passEncrypt)

        # Configura o callback para consumir as mensagens da fila
        channel.basic_consume(
            queue=self.__queue,  # A fila da qual o consumidor irá receber mensagens
            auto_ack=True,  # O RabbitMQ irá reconhecer automaticamente a mensagem após o recebimento
            on_message_callback=callback_with_pass  # Callback para processar a mensagem recebida
        )
        
        return channel  # Retorna o canal de comunicação configurado
    
    def start(self):
        """
        Inicia o processo de consumo de mensagens do RabbitMQ.
        """
        self.__channel.start_consuming()  # Inicia o loop de consumo de mensagens

def queue_callback(ch, method, properties, body, passEncrypt):
    """
    Função callback que é chamada sempre que uma nova mensagem é recebida do RabbitMQ.
    Descriptografa a mensagem e exibe o conteúdo no terminal.
    """
    # Converte o corpo da mensagem de volta de bytes para um formato JSON
    message = json.loads(body.decode())

    # Extrai os dados da mensagem (iv, salt, mensagem criptografada, nome e cor)
    iv = bytes.fromhex(message['iv'])  # O IV é convertido de hexadecimal para bytes
    salt = bytes.fromhex(message['salt'])  # O salt também é convertido
    encrypted_message = bytes.fromhex(message['encrypted_message'])  # A mensagem criptografada é convertida
    name = message['name']  # Nome do usuário que enviou a mensagem
    cor = message['cor']  # Cor associada à mensagem

    # A senha para descriptografar a mensagem é fornecida como parâmetro
    password = passEncrypt

    # Tenta descriptografar a mensagem usando os dados extraídos
    try:
        decrypted_message = encrypt.decrypt_message(encrypted_message, password, iv, salt)
        print(cor + f"{name}: {decrypted_message}")  # Exibe a mensagem descriptografada no terminal com a cor associada
    except ValueError:
        # Se houver um erro na descriptografia, exibe uma mensagem de erro
        print("Não foi possível abrir essa mensagem. A senha pode estar incorreta ou a mensagem está corrompida.")

def main(passEncrypt, exibir_mensagem_com_cor, cor):
    """
    Função principal para iniciar o consumidor e processar mensagens recebidas.
    """
    # Cria o consumidor e inicia o consumo das mensagens
    rabbitMq_consumer = RabbitMQConsumer(queue_callback, passEncrypt)
    rabbitMq_consumer.start()

# A seguir, o bloco abaixo garante que o código no arquivo 'consumer.py' não será executado automaticamente
# se o arquivo for importado como módulo em outro lugar, mas só será executado se chamado diretamente.
if __name__ == "__main__":
    pass  # Não há necessidade de executar nada diretamente quando o módulo é carregado
