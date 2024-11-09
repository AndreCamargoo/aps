from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from binascii import hexlify, unhexlify
from Crypto.Protocol.KDF import PBKDF2
import os

from dotenv import load_dotenv
load_dotenv()  # Carrega as variáveis do arquivo .env

def derive_key(password, salt):
    # Deriva uma chave de 32 bytes (256 bits) usando PBKDF2
    '''
        O PBKDF2 aceita senhas de qualquer comprimento. Portanto, se você fornecer uma senha menor que 16 bytes, 
        ela será processada e transformada em uma chave de 32 bytes (ou o comprimento que você especificar em dkLen).
        
        O PBKDF2 aplica uma função de hash repetidamente (um número configurável de iterações) à senha e a um salt, 
        tornando mais difícil para um atacante usar ataques de força bruta, mesmo que a senha seja fraca.
        
        Se você usar uma senha como "minha senha", que tem apenas 12 bytes, a função PBKDF2 ainda a transformará em uma chave de 32 bytes. 
        Isso é feito com um processo de hash que "expande" a senha.
        
        O que é um salt
        
        Salt é uma sequência aleatória de bytes que é adicionada a uma senha antes de ser processada por uma função de hash. 
        O objetivo principal do salt é aumentar a segurança das senhas armazenadas e protegê-las contra ataques
    '''
    return PBKDF2(password, salt, dkLen=16)

def encrypt_message(message, password):
    # Gera um salt aleatório
    salt = os.urandom(16)    
    key = derive_key(password, salt)    
    cipher = AES.new(key, AES.MODE_CBC)
    
    padded_message = pad(message.encode('utf-8'), 16)
    ciphertext = cipher.encrypt(padded_message)
    
    return cipher.iv, ciphertext, salt

def decrypt_message(ciphertext, password, iv, salt):
    key = derive_key(password, salt)  # Deriva a chave novamente
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded_message = cipher.decrypt(ciphertext)
    return unpad(decrypted_padded_message, 16).decode('utf-8')

if __name__ == "__main__":
    pass # Não há necessidade de código executável aqui diretamente.
