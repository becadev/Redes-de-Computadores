import socket  # Cria a conexão
import time
import json
import ast  # Importando para segurança na avaliação de tupla
from Sistema import Sistema  # Certifique-se de que Sistema está implementado corretamente

class Cliente:
    def __init__(self) -> None:
        self.server_ip, self.server_port = self.descobrir_servidor()

    def descobrir_servidor(self) -> tuple:
        """Busca uma conexão com um servidor"""
        print("Esperando servidores...")
        HOST = ''              # Endereço IP do Servidor
        PORT = 5005            # Porta que o Servidor está
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        orig = (HOST, PORT)
        udp.bind(orig)

        while True:
            msg, cliente = udp.recvfrom(1024)
            tupla = ast.literal_eval(msg.decode("utf-8"))  # Usando ast.literal_eval

            return cliente[0], int(tupla[1])  # Retorna o ip e a porta como tupla (str, int)
          
    def enviar_info(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.server_ip, self.server_port))

            # Coletar informações do sistema
            dados = {
                "espaco_livre_hd": Sistema.espaco_livre_hd(),
                "qtd_processadores": Sistema.qtd_processadores(),
                "espaco_memoria": Sistema.espaco_memoria()
            }

            # Serializar o dicionário para JSON e depois para bytes
            dados_json = json.dumps(dados)  # Converte o dicionário para uma string JSON
            s.send(dados_json.encode("utf-8"))  # Converte a string JSON para bytes e envia ao servidor
            print("Informações enviadas ao servidor.")

            s.close()  # Fechar a conexão depois de enviar os dados
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")
            

def main():
    cliente = Cliente()
    while True:
        cliente.enviar_info()  # Enviar informações para o servidor
        time.sleep(10)  # Aguardar 10 segundos antes de enviar novamente


if __name__ == "__main__":
    main()
