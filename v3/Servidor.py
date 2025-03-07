import socket
import json
import threading
import time

class Servidor:
    def __init__(self) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket TCP
        self.s.bind(("0.0.0.0", 5551))  # O servidor aceita conexões em qualquer rede
        self.s.listen(5)  # Máximo de 5 conexões
        self.info = {}
        self.ipPorta = ("0.0.0.0", 5551)  # Define o IP e a porta para broadcast

    def ligar(self) -> None:
        print("Servidor escutando conexões...")

        # Inicia a thread para enviar broadcasts
        threading.Thread(target=self.broadcast_server_ip, daemon=True).start()

        # Inicia uma thread do menu em paralelo
        threading.Thread(target=self.menu, daemon=True).start()  

        while True:
            clientsocket, address = self.s.accept()  # Aguarda conexões
            print(f"Conexão estabelecida com {address}.")
            threading.Thread(target=self.receber_dados, args=(clientsocket, address)).start()

    def broadcast_server_ip(self):
        """Envia periodicamente o IP e a porta do servidor via broadcast UDP."""
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        allips = [ip[-1][0] for ip in interfaces]  # Obtém todos os IPs do servidor
        msg = str(self.ipPorta).encode("utf-8")

        while True:
            for ip in allips:
                try:
                    print(f'Publicando em {ip}')
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Cria socket UDP
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Habilita broadcast
                    sock.bind((ip, 0))  # Usa o IP da interface
                    sock.sendto(msg, ("255.255.255.255", 5005))  # Envia broadcast
                    sock.close()
                except Exception as e:
                    print(f"Erro ao enviar broadcast em {ip}: {e}")

            time.sleep(5)  # Espera 5 segundos antes de enviar novamente

    def receber_dados(self, clientsocket, address):
        try:
            msg = clientsocket.recv(1024).decode("utf-8")
            try:
                dados_recebidos = json.loads(msg)
                self.info[address[0]] = {
                    'espaco_livre_hd': dados_recebidos.get("espaco_livre_hd", "Desconhecido"),
                    'qtd_processadores': dados_recebidos.get("qtd_processadores", "Desconhecido"),
                    'espaco_memoria': dados_recebidos.get("espaco_memoria", "Desconhecido")
                }
                self.salvar_em_json()
                print(f"Dados do IP {address[0]} armazenados.")
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON de {address[0]}. Dados recebidos: {msg}")

            clientsocket.close()
        except Exception as e:
            print(f"Erro ao receber dados: {e}")

    def salvar_em_json(self):
        try:
            dados_salvos = {}
            try:
                with open("informacoes_sistema.json", "r") as file:
                    dados_salvos = json.load(file)
            except FileNotFoundError:
                pass

            dados_salvos.update(self.info)

            with open("informacoes_sistema.json", 'w') as file:
                json.dump(dados_salvos, file, indent=3)

        except Exception as e:
            print(f"Erro ao salvar arquivo JSON: {e}")

    def calcular_media(self):
        total_pc = len(self.info)
        if total_pc == 0:
            print("Nenhum dado disponível para calcular a média.")
            return
        total_hd = sum(float(pc["espaco_livre_hd"].split()[0]) for pc in self.info.values())
        total_cpu = sum(int(pc["qtd_processadores"]) for pc in self.info.values())
        total_mem = sum(float(pc["espaco_memoria"].split()[0]) for pc in self.info.values())

        print("\nMédia dos computadores conectados")
        print(f"Espaço livre médio no HD: {total_hd / total_pc:.2f} GB")
        print(f"Quantidade média de processadores: {total_cpu / total_pc:.2f}")
        print(f"Memória RAM livre média: {total_mem / total_pc:.2f} GB")    

    def menu(self):
        while True:
            print("\nO que deseja visualizar?")
            print("1. Lista de IPs conectados")
            print("2. Consultar as informações por IP")
            print("3. Calcular média dos dados")
            print("4. Fechar servidor")
            opcao = int(input("Opção: "))

            if opcao == 1:
                self.listar_ips()
            elif opcao == 2:
                ip = input("Digite o IP desejado: ")
                self.consultar_por_ip(ip)
            elif opcao == 3:
                self.calcular_media()
            elif opcao == 4:
                print("Servidor fechado...")
                exit()
            else:
                print("Opção inválida!\n") 

    def listar_ips(self):
        try:
            with open("informacoes_sistema.json", "r") as file:
                dados = json.load(file)
                print("\nIPs que realizaram conexão: ")
                for ip in dados.keys():
                    print(f"- {ip}")
        except FileNotFoundError:
            print("Nenhuma informação registrada ainda")

    def consultar_por_ip(self, ip):
        try:
            with open("informacoes_sistema.json", "r") as file:
                dados = json.load(file)
                info = dados.get(ip)
                if info:
                    print(f"\nInformações do IP {ip}: ")
                    print(f"Espaço livre HD: {info.get('espaco_livre_hd')}")
                    print(f"Quantidade de processadores: {info.get('qtd_processadores')}")
                    print(f"Espaço livre na memória RAM: {info.get('espaco_memoria')}")
                else:
                    print(f"O IP não foi encontrado\n")
        except FileNotFoundError:
            print("Não há informações salvas ainda\n")

def main():
    server = Servidor()
    server.ligar()

if __name__ == "__main__":
    main()
