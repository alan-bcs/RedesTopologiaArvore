import networkx as nx
import random
import time

class NetworkSimulator:
    def __init__(self):
        self.topo = nx.Graph()
        self.ip_table = {}

    def add_device(self, name, ip, device_type):
        self.topo.add_node(name, ip=ip, type=device_type)
        self.ip_table[ip] = name

    def add_link(self, node1, node2, latency_ms):
        self.topo.add_edge(node1, node2, weight=latency_ms)

    def get_device_by_ip(self, ip):
        return self.ip_table.get(ip)

    def display_routing_tables(self):
        """
        Exibe as tabelas de roteamento estáticas conforme definido na Fase 1.
        Isso ajuda a validar visualmente a lógica durante a demonstração em vídeo.
        """
        print("\n=== TABELAS DE ROTEAMENTO (Simulação Estática) ===")
        
        # Tabela do Core (C1)
        print("\n[Roteador Core - C1]")
        print(f"{'Destino':<18} | {'Máscara':<15} | {'Gateway/Interface'}")
        print("-" * 55)
        print(f"{'172.16.0.0':<18} | {'/26 (Agreg. e1,e2)':<15} | {'172.16.2.2 (Via A1)'}")
        print(f"{'172.16.1.0':<18} | {'/26 (Agreg. e3,e4)':<15} | {'172.16.2.6 (Via A2)'}")

        # Tabela do Agregador 1 (A1)
        print("\n[Roteador Agregador - A1]")
        print(f"{'Destino':<18} | {'Máscara':<15} | {'Gateway/Interface'}")
        print("-" * 55)
        print(f"{'0.0.0.0':<18} | {'/0  (Default)':<15} | {'172.16.2.1 (Via C1)'}")
        print(f"{'172.16.0.0':<18} | {'/27 (Local e1)':<15} | {'Conectado (Fa0/0)'}")
        print(f"{'172.16.0.32':<18} | {'/27 (Local e2)':<15} | {'Conectado (Fa0/1)'}")

        # Tabela do Agregador 2 (A2)
        print("\n[Roteador Agregador - A2]")
        print(f"{'Destino':<18} | {'Máscara':<15} | {'Gateway/Interface'}")
        print("-" * 55)
        print(f"{'0.0.0.0':<18} | {'/0  (Default)':<15} | {'172.16.2.5 (Via C1)'}")
        print(f"{'172.16.1.0':<18} | {'/27 (Local e3)':<15} | {'Conectado (Fa0/0)'}")
        print(f"{'172.16.1.32':<18} | {'/27 (Local e4)':<15} | {'Conectado (Fa0/1)'}")
        print("==================================================\n")

    def xprobe(self, src_ip, dst_ip):
        # ... (Mantém a mesma lógica do xprobe anterior) ...
        print(f"\n--- Iniciando XProbe: {src_ip} -> {dst_ip} ---")
        
        src_node = self.get_device_by_ip(src_ip)
        dst_node = self.get_device_by_ip(dst_ip)

        if not src_node:
            print(f"Erro: IP de origem {src_ip} não encontrado.")
            return
        if not dst_node:
            print(f"Erro: IP de destino {dst_ip} inalcançável (Host Down/Inexistente).")
            return

        try:
            path = nx.shortest_path(self.topo, source=src_node, target=dst_node, weight='weight')
            
            # Cálculo de latência base
            base_latency = 0
            path_str = ""
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = self.topo.get_edge_data(u, v)
                base_latency += edge_data['weight']
                path_str += f"{u} -> "
            path_str += f"{dst_node}"

            print(f"Rota Identificada: {path_str}")
            print(f"Saltos: {len(path) - 1}")

            # Simulação de Pings
            rtt_samples = []
            print("Executando probes...")
            for seq in range(1, 4):
                jitter = random.uniform(0.95, 1.15) # Jitter
                rtt = (base_latency * 2) * jitter
                rtt_samples.append(rtt)
                print(f"  Seq={seq} | RTT={rtt:.2f} ms")
                time.sleep(0.3)

            avg_rtt = sum(rtt_samples) / len(rtt_samples)
            print(f"[SUCESSO] RTT Médio: {avg_rtt:.2f} ms")

        except nx.NetworkXNoPath:
            print(f"[FALHA] Rede inalcançável.")

    def build_scenario(self):
        # ... (Mantém a mesma topologia anterior) ...
        # (C1, A1, A2, Switches e Hosts conforme definimos)
        print("Construindo Topologia em Grafo...")
        # Adicione aqui o conteúdo do método build_scenario que fiz antes
        # Roteadores
        self.add_device("C1", "172.16.2.1", "Router Core") 
        self.add_device("A1", "172.16.2.2", "Router Agg") 
        self.add_device("A2", "172.16.2.6", "Router Agg") 
        self.add_link("C1", "A1", 2)
        self.add_link("C1", "A2", 2)
        # e1
        self.add_device("Sw_e1", "172.16.0.100", "Switch")
        self.add_device("h1", "172.16.0.2", "Host")
        self.add_link("A1", "Sw_e1", 5)
        self.add_link("Sw_e1", "h1", 1)
        # e2
        self.add_device("Sw_e2", "172.16.0.133", "Switch")
        self.add_device("h2", "172.16.0.34", "Host")
        self.add_link("A1", "Sw_e2", 5)
        self.add_link("Sw_e2", "h2", 1)
        # e3
        self.add_device("Sw_e3", "172.16.1.100", "Switch")
        self.add_device("h3", "172.16.1.2", "Host")
        self.add_link("A2", "Sw_e3", 5)
        self.add_link("Sw_e3", "h3", 1)
        # e4
        self.add_device("Sw_e4", "172.16.1.133", "Switch")
        self.add_device("h4", "172.16.1.34", "Host")
        self.add_link("A2", "Sw_e4", 5)
        self.add_link("Sw_e4", "h4", 1)

if __name__ == "__main__":
    sim = NetworkSimulator()
    sim.build_scenario()
    
    sim.display_routing_tables()

    # Executa os testes
    sim.xprobe("172.16.0.2", "172.16.2.1")    # Host -> Core
    sim.xprobe("172.16.0.2", "172.16.0.34")   # Host -> Host (Mesmo Agregador)
    sim.xprobe("172.16.0.2", "172.16.1.2")    # Host -> Host (Outro Agregador)
    sim.xprobe("172.16.0.2", "192.168.99.99") # Falha
