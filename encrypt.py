# Importação das bibliotecas necessárias para criptografia, manipulação de dados e variáveis de ambiente
from Crypto.Cipher import AES  # Para criptografia AES (Advanced Encryption Standard)
from Crypto.Util.Padding import pad, unpad  # Para adicionar ou remover padding da mensagem
from binascii import hexlify, unhexlify  # Para converter bytes em hexadecimal e vice-versa
from Crypto.Protocol.KDF import PBKDF2  # Para derivar uma chave a partir de uma senha (PBKDF2)
import os  # Para acessar funções de sistema, como geração de salt aleatório
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env

# Carrega as variáveis de ambiente do arquivo '.env'
load_dotenv()

def derive_key(password, salt):
    """
    Deriva uma chave criptográfica a partir de uma senha e um salt usando o PBKDF2.

    O PBKDF2 (Password-Based Key Derivation Function 2) aplica várias iterações de uma função de hash
    à senha e ao salt para gerar uma chave de comprimento fixo. Isso aumenta a resistência a ataques de força bruta.

    Parâmetros:
    - password: A senha fornecida pelo usuário (como string).
    - salt: O salt (sequência aleatória) utilizado para aumentar a segurança do processo de derivação.

    Retorna:
    - Uma chave derivada de 16 bytes (128 bits) que será usada na criptografia e descriptografia.
    """
    # Utiliza PBKDF2 para gerar a chave de 16 bytes a partir da senha e salt fornecidos
    return PBKDF2(password, salt, dkLen=16)

def encrypt_message(message, password):
    """
    Criptografa uma mensagem usando o AES (Advanced Encryption Standard) em modo CBC (Cipher Block Chaining).

    O processo de criptografia é feito da seguinte forma:
    1. Geração de um salt aleatório de 16 bytes.
    2. Derivação da chave criptográfica a partir da senha e do salt.
    3. Criptografia da mensagem utilizando AES no modo CBC, com padding para garantir que a mensagem tenha um comprimento múltiplo de 16 bytes.

    Parâmetros:
    - message: A mensagem a ser criptografada (como string).
    - password: A senha usada para gerar a chave de criptografia.

    Retorna:
    - iv: O vetor de inicialização (IV) usado no AES (gerado aleatoriamente).
    - ciphertext: A mensagem criptografada.
    - salt: O salt aleatório gerado e utilizado para derivar a chave.
    """
    # Gera um salt aleatório de 16 bytes
    salt = os.urandom(16)
    
    # Deriva a chave a partir da senha e do salt gerado
    key = derive_key(password, salt)
    
    # Cria o objeto de cifragem AES com a chave derivada e o modo CBC
    cipher = AES.new(key, AES.MODE_CBC)
    
    # Adiciona padding à mensagem para garantir que seu tamanho seja múltiplo de 16 bytes
    padded_message = pad(message.encode('utf-8'), 16)
    
    # Criptografa a mensagem
    ciphertext = cipher.encrypt(padded_message)
    
    # Retorna o vetor de inicialização (iv), o texto cifrado e o salt utilizado
    return cipher.iv, ciphertext, salt

def decrypt_message(ciphertext, password, iv, salt):
    """
    Descriptografa uma mensagem criptografada usando o AES em modo CBC.

    O processo de descriptografia é feito da seguinte forma:
    1. Deriva a chave a partir da senha e do salt fornecidos.
    2. Utiliza o AES no modo CBC com o IV original para descriptografar a mensagem.
    3. Remove o padding da mensagem descriptografada.

    Parâmetros:
    - ciphertext: A mensagem criptografada.
    - password: A senha usada para derivar a chave de criptografia.
    - iv: O vetor de inicialização (IV) utilizado no AES.
    - salt: O salt utilizado para derivar a chave.

    Retorna:
    - A mensagem original, agora descriptografada (como string).
    """
    # Deriva a chave novamente usando o salt fornecido
    key = derive_key(password, salt)
    
    # Cria o objeto de cifragem AES com a chave derivada e o modo CBC
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Descriptografa a mensagem cifrada
    decrypted_padded_message = cipher.decrypt(ciphertext)
    
    # Remove o padding da mensagem descriptografada e a retorna como uma string
    return unpad(decrypted_padded_message, 16).decode('utf-8')

# Bloco principal, não executa código diretamente quando o arquivo for importado como módulo
if __name__ == "__main__":
    pass  # Nenhum código executável é necessário diretamente aqui
