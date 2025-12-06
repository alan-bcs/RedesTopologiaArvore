import networkx as nx
import random
import time

class NetworkSimulator:
    def __init__(self):
        # grafo não direcionado para representar a topologia física
        self.topo = nx.Graph()
        # dicionário para mapear IP -> nome do dispositivo
        self.ip_table = {}

    def add_device(self, name, ip, device_type):
        self.topo.add_node(name, ip=ip, type=device_type)
        self.ip_table[ip] = name

    def add_link(self, node1, node2, latency_ms):
        self.topo.add_edge(node1, node2, weight=latency_ms)

    def get_device_by_ip(self, ip):
        return self.ip_table.get(ip)

    def display_routing_tables(self):
        print("\nTABELAS DE ROTEAMENTO (Simulação Estática)")
        
        # tabela do core (C1)
        print("\n[Roteador Core - C1]")
        print(f"{'Destino':<18} | {'Máscara':<20} | {'Próximo Salto'}")
        print("-" * 60)

        # agrega e1 e e2 (172.16.0.0 e .32) numa rota /26 via A1
        print(f"{'172.16.0.0':<18} | {'/26 (Agreg. e1+e2)':<20} | {'172.16.2.2 (Via A1)'}")
        print(f"{'172.16.1.0':<18} | {'/26 (Agreg. e3+e4)':<20} | {'172.16.2.6 (Via A2)'}")

        # tabela do agreador 1 (A1)
        print("\n[Roteador Agregador - A1]")
        print(f"{'Destino':<18} | {'Máscara':<20} | {'Próximo Salto'}")
        print("-" * 60)
        print(f"{'0.0.0.0':<18} | {'/0  (Rota Default)':<20} | {'172.16.2.1 (Via C1)'}")
        print(f"{'172.16.0.0':<18} | {'/27 (Local e1)':<20} | {'Conectado (Fa0/0)'}")
        print(f"{'172.16.0.32':<18} | {'/27 (Local e2)':<20} | {'Conectado (Fa0/1)'}")

        # tabela do agregador 2 (A2)
        print("\n[Roteador Agregador - A2]")
        print(f"{'Destino':<18} | {'Máscara':<20} | {'Próximo Salto'}")
        print("-" * 60)

        print(f"{'0.0.0.0':<18} | {'/0  (Rota Default)':<20} | {'172.16.2.5 (Via C1)'}")
        print(f"{'172.16.1.0':<18} | {'/27 (Local e3)':<20} | {'Conectado (Fa0/0)'}")
        print(f"{'172.16.1.32':<18} | {'/27 (Local e4)':<20} | {'Conectado (Fa0/1)'}")
        print("\n")

    def xprobe(self, src_ip, dst_ip):
        # verifica rota e latência (RTT).
        print(f"\nIniciando XProbe: {src_ip} -> {dst_ip}")
        
        src_node = self.get_device_by_ip(src_ip)
        dst_node = self.get_device_by_ip(dst_ip)

        if not src_node:
            print(f"Erro: IP de origem {src_ip} não encontrado na topologia.")
            return
        if not dst_node:
            print(f"Erro: IP de destino {dst_ip} inalcançável (Host Down ou Inexistente).")
            return

        try:
            # busca o caminho mais curto considerando a latência usando Dijkstra
            path = nx.shortest_path(self.topo, source=src_node, target=dst_node, weight='weight')
            
            # reconstrói a string do caminho e calcula latência base
            base_latency = 0
            path_str = ""
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = self.topo.get_edge_data(u, v)
                base_latency += edge_data['weight']
                path_str += f"{u} -> "
            path_str += f"{dst_node}"

            print(f"Rota Identificada: {path_str}")
            print(f"Saltos (Hops): {len(path) - 1}")

            # simula envio de 3 pacotes (probes)
            rtt_samples = []
            print("Enviando probes ICMP simulados...")
            for seq in range(1, 4):
                # adiciona variação aleatória (jitter)
                jitter = random.uniform(0.90, 1.10)
                # RTT = Ida + Volta (latência * 2) * jitter
                rtt = (base_latency * 2) * jitter
                rtt_samples.append(rtt)
                print(f"  Seq={seq} | RTT={rtt:.2f} ms")
                time.sleep(0.3)

            avg_rtt = sum(rtt_samples) / len(rtt_samples)
            print(f"[SUCESSO] Destino alcançável. RTT Médio: {avg_rtt:.2f} ms")

        except nx.NetworkXNoPath:
            print(f"[FALHA] Rede inalcançável. Não há rota física entre os dispositivos.")

    def build_scenario(self):
        # monta a topologia (Nós e Arestas) com base no diagrama
        print("Carregando topologia da rede (Fase 1)...")
        
        # NÍVEL 1 e 2: ROTEADORES
        self.add_device("C1", "172.16.2.1", "Router Core") 
        self.add_device("A1", "172.16.2.2", "Router Agg") 
        self.add_device("A2", "172.16.2.6", "Router Agg") 

        # Links de Fibra (Alta velocidade -> Latência 2ms)
        self.add_link("C1", "A1", 2)
        self.add_link("C1", "A2", 2)

        # NÍVEL 3 e 4: SUB-REDES ESQUERDA (A1)

        # e1
        self.add_device("Sw_e1", "172.16.0.100", "Switch")
        self.add_device("h1", "172.16.0.2", "Host")
        self.add_link("A1", "Sw_e1", 5)   # Link Agg->Edge (5ms)
        self.add_link("Sw_e1", "h1", 1)   # Link Edge->Host (1ms)

        # e2
        self.add_device("Sw_e2", "172.16.0.133", "Switch")
        self.add_device("h2", "172.16.0.34", "Host")
        self.add_link("A1", "Sw_e2", 5)
        self.add_link("Sw_e2", "h2", 1)

        # NÍVEL 3 e 4: SUB-REDES DIREITA (A2)
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
    
    # mostra as tabelas
    sim.display_routing_tables()

    # executa os testes (parte prática)
    print("\nEXECUÇÃO DOS TESTES DE CONECTIVIDADE")
    
    # host pingando seu gateway/core (subida)
    sim.xprobe("172.16.0.2", "172.16.2.1") 
    
    # host pingando vizinho no mesmo agregador (local)
    sim.xprobe("172.16.0.2", "172.16.0.34")
    
    # host pingando host do outro lado da árvore (full path)
    sim.xprobe("172.16.0.2", "172.16.1.2") 
    
    # erro proposital (botar IP inexistente)
    sim.xprobe("172.16.0.2", "192.168.99.99")
