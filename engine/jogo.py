"""Módulo do motor de regras e gerenciamento de estado do Kernel Guardian.

Este módulo contém exclusivamente a lógica pura e orientada a dados do jogo,
sem qualquer dependência de bibliotecas de interface visual (como `rich`) ou
comandos de entrada/saída no terminal.
"""

import random
import time

from core.algoritmos import (
    busca_binaria,
    busca_sequencial,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)
from core.estruturas import Fila, ListaEncadeada, No, Pilha


class MotorJogo:
    """Controla o estado completo da partida, eventos, ações e regras de vitória/derrota."""

    TOTAL_RODADAS = 10
    ACOES_POR_RODADA = 2
    TEMP_INICIAL_CPU = 25
    TEMP_MAXIMA_CPU = 100
    RAM_TOTAL_MB = 1024
    TOTAL_BLACKLIST_IPS = 10000

    IMPACTOS_TERMICOS = {
        "selection_sort": 38,
        "insertion_sort": 32,
        "merge_sort": 6,
        "quick_sort": 8,
    }

    def __init__(self, seed: int = None):
        """Inicializa o estado padrão do sistema operacional sob ataque."""
        self._rng = random.Random(seed)
        self._proximo_pid = 1000
        self._contador_chamadas = 0
        self._contador_invasoes = 0

        self.total_rodadas = self.TOTAL_RODADAS
        self.rodada_atual = 1
        self.acoes_restantes = self.ACOES_POR_RODADA
        self.temperatura_cpu = self.TEMP_INICIAL_CPU
        self.ram_total_mb = self.RAM_TOTAL_MB

        # Inicializa mapa de memória RAM (total = 1024 MB)
        self.ram = ListaEncadeada()
        self.ram.inserir("0x0000", 256, "SISTEMA", "KERNEL_CORE")
        self.ram.inserir("0x0100", 256, "LIVRE", "")
        self.ram.inserir("0x0200", 256, "SISTEMA", "SYS_DRIVERS")
        self.ram.inserir("0x0300", 256, "LIVRE", "")

        self.call_stack = Pilha()
        self.fila_processos = Fila()

        # Gera 10.000 IPs ordenados em ordem crescente ("185.220.100.100" .. "185.220.199.199")
        self.blacklist_ips = [
            f"185.220.{octeto_3}.{octeto_4}"
            for octeto_3 in range(100, 200)
            for octeto_4 in range(100, 200)
        ]

        # Ato 1 inicia com 200 setores bagunçados no disco
        self.setores_disco = self._gerar_setores_embaralhados(200)
        self.disco_ordenado = False

        # Acumulador de métricas reais para o boletim final
        self.historico_benchmark = {
            "selection_sort": self._novo_registro_benchmark(),
            "insertion_sort": self._novo_registro_benchmark(),
            "merge_sort": self._novo_registro_benchmark(),
            "quick_sort": self._novo_registro_benchmark(),
            "busca_binaria": self._novo_registro_benchmark(),
            "busca_sequencial": self._novo_registro_benchmark(),
        }

        self.fim_de_jogo = False
        self.vitoria = False
        self.motivo_fim = ""
        self.ultimo_evento_surpresa = None
        self._rodada_iniciada = False

    @property
    def memoria_ram(self) -> ListaEncadeada:
        """Alias para acesso à lista encadeada da memória RAM."""
        return self.ram

    @staticmethod
    def _novo_registro_benchmark() -> dict:
        """Cria um registro vazio de métricas acumuladas por algoritmo."""
        return {
            "execucoes": 0,
            "comparacoes": 0,
            "trocas": 0,
            "tempo_ms": 0.0,
            "historico": [],
        }

    def _registrar_benchmark(
        self,
        algoritmo: str,
        comparacoes: int,
        trocas: int,
        tempo_ms: float,
        tamanho_entrada: int,
    ) -> None:
        """Registra uma execução no histórico de benchmark da partida."""
        registro = self.historico_benchmark[algoritmo]
        registro["execucoes"] += 1
        registro["comparacoes"] += comparacoes
        registro["trocas"] += trocas
        registro["tempo_ms"] = round(registro["tempo_ms"] + tempo_ms, 4)
        registro["historico"].append(
            {
                "rodada": self.rodada_atual,
                "tamanho_entrada": tamanho_entrada,
                "comparacoes": comparacoes,
                "trocas": trocas,
                "tempo_ms": tempo_ms,
            }
        )

    def _gerar_setores_embaralhados(self, quantidade: int) -> list:
        """Gera lista de setores [1..quantidade] embaralhada manualmente (Fisher-Yates)."""
        setores = list(range(1, quantidade + 1))
        for i in range(quantidade - 1, 0, -1):
            j = self._rng.randint(0, i)
            setores[i], setores[j] = setores[j], setores[i]

        # Garante que não permaneça trivialmente ordenada quando quantidade > 1
        if quantidade > 1 and setores[0] < setores[1]:
            setores[0], setores[1] = setores[1], setores[0]

        self.disco_ordenado = False
        return setores

    def _criar_processo(self, malicioso: bool, nome_customizado: str = None) -> dict:
        """Constrói um dicionário de processo para o escalonador FIFO."""
        self._proximo_pid += 1
        if malicioso:
            ip = self._rng.choice(self.blacklist_ips)
            nomes_maliciosos = [
                "ghost_packet.bin",
                "trojan_injector.elf",
                "rootkit_daemon",
                "worm_replicator",
                "backdoor_sshd",
            ]
            nome = nome_customizado or self._rng.choice(nomes_maliciosos)
        else:
            oct3 = self._rng.randint(1, 254)
            oct4 = self._rng.randint(1, 254)
            ip = f"10.0.{oct3}.{oct4}"
            nomes_seguros = [
                "systemd-journald",
                "net_health_check",
                "cron_backup",
                "auth_verifier",
                "kernel_watchdog",
            ]
            nome = nome_customizado or self._rng.choice(nomes_seguros)

        return {
            "pid": self._proximo_pid,
            "nome": nome,
            "ip": ip,
            "malicioso": malicioso,
        }

    def _encerrar_derrota(self, motivo: str) -> None:
        """Marca a partida como encerrada por derrota com o motivo especificado."""
        if not self.fim_de_jogo:
            self.fim_de_jogo = True
            self.vitoria = False
            self.motivo_fim = motivo

    def _injetar_malware_ram(
        self, tamanho_mb: int = 128, assinatura: str = "0xDEAD"
    ) -> bool:
        """Aloca um bloco 'MALWARE' em um espaço 'LIVRE' da lista encadeada da RAM.

        Se não houver nenhum bloco 'LIVRE' com capacidade suficiente, dispara
        Game Over por Colapso de Memória.
        """
        atual = self.ram.cabeca
        while atual is not None:
            if atual.status == "LIVRE" and atual.tamanho_mb >= tamanho_mb:
                sobra = atual.tamanho_mb - tamanho_mb
                atual.tamanho_mb = tamanho_mb
                atual.status = "MALWARE"
                atual.assinatura = assinatura

                if sobra > 0:
                    endereco_base = int(atual.endereco_hex, 16)
                    novo_endereco = f"0x{endereco_base + tamanho_mb:04X}"
                    bloco_restante = No(
                        novo_endereco, sobra, "LIVRE", "", proximo=atual.proximo
                    )
                    atual.proximo = bloco_restante
                return True

            atual = atual.proximo

        self._encerrar_derrota("Colapso de Memória")
        return False

    def _empilhar_chamada(self, nome_chamada: str) -> bool:
        """Empilha uma chamada na Call Stack ou dispara Stack Overflow se estiver cheia."""
        if self.call_stack.esta_cheia():
            self._encerrar_derrota("Stack Overflow")
            return False

        sucesso = self.call_stack.push(nome_chamada)
        if not sucesso:
            self._encerrar_derrota("Stack Overflow")
            return False
        return True

    def _proxima_chamada(self, prefixo: str) -> str:
        """Gera identificador único de frame para a Call Stack."""
        self._contador_chamadas += 1
        return f"{prefixo}_{self._contador_chamadas:02d}()"

    def _tem_malware_ram(self) -> bool:
        """Verifica manualmente via `.proximo` se há bloco 'MALWARE' na RAM."""
        atual = self.ram.cabeca
        while atual is not None:
            if atual.status == "MALWARE":
                return True
            atual = atual.proximo
        return False

    def _primeira_assinatura_malware(self) -> str:
        """Obtém a assinatura do primeiro bloco 'MALWARE' ou retorna '0xDEAD'."""
        atual = self.ram.cabeca
        while atual is not None:
            if atual.status == "MALWARE":
                return atual.assinatura
            atual = atual.proximo
        return "0xDEAD"

    def _obter_ato_atual(self) -> int:
        """Retorna o número do Ato (1, 2 ou 3) conforme a rodada atual."""
        if self.rodada_atual <= 3:
            return 1
        if self.rodada_atual <= 7:
            return 2
        return 3

    def iniciar_rodada(self) -> dict:
        """Aplica os eventos e a carga de ataque da rodada atual.

        Retorna um dicionário estruturado descrevendo o ato, eventual evento
        surpresa disparado e o estado atualizado do sistema.
        """
        if self.fim_de_jogo:
            return {
                "sucesso": False,
                "erro": "A partida já foi encerrada.",
                "estado": self.obter_estado(),
            }

        self.acoes_restantes = self.ACOES_POR_RODADA
        self.ultimo_evento_surpresa = None
        self._rodada_iniciada = True
        ato = self._obter_ato_atual()

        if ato == 1:
            # Ato 1 (Rodadas 1 a 3 — O Reconhecimento): ataques leves
            self.fila_processos.enqueue(self._criar_processo(malicioso=True))
            self.fila_processos.enqueue(self._criar_processo(malicioso=False))
            self.setores_disco = self._gerar_setores_embaralhados(200)
            self._empilhar_chamada(self._proxima_chamada("recon_hook"))

        elif ato == 2:
            if self.rodada_atual == 4:
                # Evento Surpresa 1: Injeção de Pacotes Fantasmas
                for idx in range(1, 5):
                    self.fila_processos.enqueue(
                        self._criar_processo(
                            malicioso=True,
                            nome_customizado=f"phantom_pkt_{idx}.bin",
                        )
                    )
                self._injetar_malware_ram(tamanho_mb=128, assinatura="0xDEAD")
                self.ultimo_evento_surpresa = {
                    "id": 1,
                    "titulo": "Injeção de Pacotes Fantasmas",
                    "descricao": (
                        "4 processos maliciosos foram injetados na fila e "
                        "um bloco MALWARE (0xDEAD) ocupou a RAM!"
                    ),
                }
            else:
                self.fila_processos.enqueue(self._criar_processo(malicioso=True))
                self.fila_processos.enqueue(self._criar_processo(malicioso=False))

            # Ato 2 (Rodadas 4 a 7 — A Escalada): 1.500 setores + pressão na Stack
            self.setores_disco = self._gerar_setores_embaralhados(1500)
            self._empilhar_chamada(self._proxima_chamada("escalada_trap"))

        else:
            if self.rodada_atual == 8:
                # Evento Surpresa 2: Sobrecarga Térmica + Embaralhamento Total
                self.temperatura_cpu = max(self.temperatura_cpu, 65)
                self.setores_disco = self._gerar_setores_embaralhados(5000)
                self.ultimo_evento_surpresa = {
                    "id": 2,
                    "titulo": "Sobrecarga Térmica + Embaralhamento Total",
                    "descricao": (
                        "A CPU atingiu 65°C e 5.000 setores do disco foram "
                        "embaralhados! Algoritmos O(n²) causarão superaquecimento."
                    ),
                }
                self._empilhar_chamada(self._proxima_chamada("overload_irq"))
                self._empilhar_chamada(self._proxima_chamada("kernel_panic"))
            elif self.rodada_atual == 9:
                self.setores_disco = self._gerar_setores_embaralhados(5000)
                self._injetar_malware_ram(tamanho_mb=128, assinatura="0xDEAD")
                self._empilhar_chamada(self._proxima_chamada("final_breach"))
            else:
                self.setores_disco = self._gerar_setores_embaralhados(5000)
                self._empilhar_chamada(self._proxima_chamada("zero_day_a"))
                self._empilhar_chamada(self._proxima_chamada("zero_day_b"))

            # Ato 3 (Rodadas 8 a 10 — O Ataque Final): alta pressão na fila
            self.fila_processos.enqueue(self._criar_processo(malicioso=True))
            self.fila_processos.enqueue(self._criar_processo(malicioso=True))

        return {
            "sucesso": True,
            "rodada": self.rodada_atual,
            "ato": ato,
            "evento_surpresa": self.ultimo_evento_surpresa,
            "estado": self.obter_estado(),
        }

    def _validar_acao_disponivel(self) -> dict | None:
        """Verifica se o jogo está ativo e se ainda há ações disponíveis na rodada."""
        if self.fim_de_jogo:
            return {
                "sucesso": False,
                "erro": f"Partida encerrada ({self.motivo_fim}).",
                "acoes_restantes": self.acoes_restantes,
            }
        if self.acoes_restantes <= 0:
            return {
                "sucesso": False,
                "erro": "Sem ações restantes nesta rodada. Finalize a rodada.",
                "acoes_restantes": self.acoes_restantes,
            }
        return None

    def acao_escanear_fila(self) -> dict:
        """Inspeciona a frente da fila usando busca binária na blacklist de IPs.

        Se o IP estiver na blacklist, bloqueia (remove) o processo como ameaça;
        caso contrário, executa o processo legítimo normalmente e o remove da fila.
        """
        erro = self._validar_acao_disponivel()
        if erro is not None:
            return erro

        if self.fila_processos.esta_vazia():
            return {
                "sucesso": False,
                "erro": "A fila de processos está vazia.",
                "processo": None,
                "bloqueado": False,
                "encontrado": False,
                "indice": -1,
                "passos": 0,
                "tempo_ms": 0.0,
                "acoes_restantes": self.acoes_restantes,
            }

        processo_frente = self.fila_processos.frente()
        inicio = time.perf_counter()
        encontrado, indice, passos = busca_binaria(
            self.blacklist_ips, processo_frente["ip"]
        )
        tempo_ms = round((time.perf_counter() - inicio) * 1000, 4)

        processo_removido = self.fila_processos.dequeue()
        bloqueado = encontrado or bool(processo_removido["malicioso"])

        self._registrar_benchmark(
            "busca_binaria",
            comparacoes=passos,
            trocas=0,
            tempo_ms=tempo_ms,
            tamanho_entrada=len(self.blacklist_ips),
        )

        self.acoes_restantes -= 1

        return {
            "sucesso": True,
            "processo": processo_removido,
            "bloqueado": bloqueado,
            "encontrado": encontrado,
            "indice": indice,
            "passos": passos,
            "tempo_ms": tempo_ms,
            "acoes_restantes": self.acoes_restantes,
        }

    def acao_limpar_ram(self) -> dict:
        """Localiza bloco 'MALWARE' via busca sequencial, libera-o e executa coalescência."""
        erro = self._validar_acao_disponivel()
        if erro is not None:
            return erro

        assinatura_alvo = self._primeira_assinatura_malware()
        inicio = time.perf_counter()
        no_encontrado, nos_percorridos = busca_sequencial(self.ram, assinatura_alvo)
        tempo_ms = round((time.perf_counter() - inicio) * 1000, 4)

        fusoes = 0
        limpo = False
        no_limpo_info = None

        if no_encontrado is not None and no_encontrado.status == "MALWARE":
            no_limpo_info = {
                "endereco_hex": no_encontrado.endereco_hex,
                "tamanho_mb": no_encontrado.tamanho_mb,
                "assinatura_anterior": no_encontrado.assinatura,
            }
            no_encontrado.status = "LIVRE"
            no_encontrado.assinatura = ""
            fusoes = self.ram.coalescencia()
            limpo = True

        self._registrar_benchmark(
            "busca_sequencial",
            comparacoes=nos_percorridos,
            trocas=1 if limpo else 0,
            tempo_ms=tempo_ms,
            tamanho_entrada=self.ram.tamanho(),
        )

        self.acoes_restantes -= 1

        return {
            "sucesso": True,
            "limpo": limpo,
            "no_limpo": no_limpo_info,
            "nos_percorridos": nos_percorridos,
            "fusoes": fusoes,
            "tempo_ms": tempo_ms,
            "acoes_restantes": self.acoes_restantes,
        }

    def acao_desempilhar_stack(self) -> dict:
        """Remove a chamada no topo da Call Stack para evitar Stack Overflow."""
        erro = self._validar_acao_disponivel()
        if erro is not None:
            return erro

        if self.call_stack.esta_vazia():
            return {
                "sucesso": False,
                "erro": "A Call Stack já está vazia.",
                "chamada_removida": None,
                "tamanho_stack": 0,
                "acoes_restantes": self.acoes_restantes,
            }

        chamada = self.call_stack.pop()
        self.acoes_restantes -= 1

        return {
            "sucesso": True,
            "chamada_removida": chamada,
            "tamanho_stack": self.call_stack.tamanho(),
            "acoes_restantes": self.acoes_restantes,
        }

    def acao_desfragmentar_disco(self, nome_algoritmo: str) -> dict:
        """Desfragmenta os setores do disco com o algoritmo escolhido e aplica impacto térmico."""
        erro = self._validar_acao_disponivel()
        if erro is not None:
            return erro

        algoritmos_disponiveis = {
            "selection_sort": selection_sort,
            "insertion_sort": insertion_sort,
            "merge_sort": merge_sort,
            "quick_sort": quick_sort,
        }

        chave = nome_algoritmo.strip().lower()
        if chave not in algoritmos_disponiveis:
            raise ValueError(
                f"Algoritmo desconhecido '{nome_algoritmo}'. "
                f"Opções válidas: {tuple(algoritmos_disponiveis.keys())}."
            )

        funcao_ordenacao = algoritmos_disponiveis[chave]
        tamanho_setores = len(self.setores_disco)
        resultado = funcao_ordenacao(self.setores_disco)

        self.setores_disco = resultado["ordenado"]
        self.disco_ordenado = True

        # Sob carga extrema (>= 5.000 setores), insertion_sort também supera 100°C a partir de 65°C
        if chave == "insertion_sort" and tamanho_setores >= 5000:
            impacto_termico = 36
        else:
            impacto_termico = self.IMPACTOS_TERMICOS[chave]

        self.temperatura_cpu += impacto_termico

        self._registrar_benchmark(
            chave,
            comparacoes=resultado["comparacoes"],
            trocas=resultado["trocas"],
            tempo_ms=resultado["tempo_ms"],
            tamanho_entrada=tamanho_setores,
        )

        self.acoes_restantes -= 1

        if self.temperatura_cpu >= self.TEMP_MAXIMA_CPU:
            self._encerrar_derrota("Superaquecimento")

        return {
            "sucesso": True,
            "algoritmo": chave,
            "ordenado": resultado["ordenado"],
            "comparacoes": resultado["comparacoes"],
            "trocas": resultado["trocas"],
            "tempo_ms": resultado["tempo_ms"],
            "impacto_termico": impacto_termico,
            "temperatura_cpu": self.temperatura_cpu,
            "fim_de_jogo": self.fim_de_jogo,
            "motivo_fim": self.motivo_fim,
            "acoes_restantes": self.acoes_restantes,
        }

    def finalizar_rodada(self) -> dict:
        """Processa processos restantes na fila, avança o turno e checa vitória ou derrota."""
        if self.fim_de_jogo:
            return {
                "sucesso": False,
                "erro": f"A partida já encerrou ({self.motivo_fim}).",
                "fim_de_jogo": self.fim_de_jogo,
                "vitoria": self.vitoria,
                "motivo_fim": self.motivo_fim,
            }

        processos_seguros_executados = []
        invasao_ocorrida = None

        # Executa processos seguros que estejam na frente da fila
        while (
            not self.fila_processos.esta_vazia()
            and not self.fila_processos.frente()["malicioso"]
        ):
            processos_seguros_executados.append(self.fila_processos.dequeue())

        # Se sobrou processo malicioso na cabeça da fila, ele invade o sistema
        if (
            not self.fila_processos.esta_vazia()
            and self.fila_processos.frente()["malicioso"]
        ):
            processo_invasor = self.fila_processos.dequeue()
            self._contador_invasoes += 1

            # Alterna entre infectar a RAM e empurrar chamada maliciosa na Call Stack
            if self._contador_invasoes % 2 == 1:
                sucesso_ram = self._injetar_malware_ram(
                    tamanho_mb=128, assinatura="0xDEAD"
                )
                invasao_ocorrida = {
                    "tipo": "RAM",
                    "processo": processo_invasor,
                    "sucesso_alocacao": sucesso_ram,
                }
            else:
                chamada_maliciosa = f"intrusion_pid_{processo_invasor['pid']}()"
                sucesso_stack = self._empilhar_chamada(chamada_maliciosa)
                invasao_ocorrida = {
                    "tipo": "CALL_STACK",
                    "processo": processo_invasor,
                    "chamada": chamada_maliciosa,
                    "sucesso_push": sucesso_stack,
                }

        # Verifica condição térmica antes de avançar
        if self.temperatura_cpu >= self.TEMP_MAXIMA_CPU:
            self._encerrar_derrota("Superaquecimento")

        rodada_concluida = self.rodada_atual
        self.acoes_restantes = self.ACOES_POR_RODADA
        self._rodada_iniciada = False

        if not self.fim_de_jogo:
            if self.rodada_atual >= self.total_rodadas:
                self.fim_de_jogo = True
                self.vitoria = True
                self.motivo_fim = "Vitória"
            else:
                self.rodada_atual += 1

        return {
            "sucesso": True,
            "rodada_concluida": rodada_concluida,
            "proxima_rodada": self.rodada_atual,
            "processos_seguros_executados": processos_seguros_executados,
            "invasao_ocorrida": invasao_ocorrida,
            "fim_de_jogo": self.fim_de_jogo,
            "vitoria": self.vitoria,
            "motivo_fim": self.motivo_fim,
            "estado": self.obter_estado(),
        }

    def obter_estado(self) -> dict:
        """Retorna um snapshot estruturado de todo o estado do sistema para a UI."""
        blocos_ram = []
        ram_livre_mb = 0
        ram_malware_mb = 0
        ram_sistema_mb = 0

        for bloco in self.ram:
            blocos_ram.append(
                {
                    "endereco_hex": bloco.endereco_hex,
                    "tamanho_mb": bloco.tamanho_mb,
                    "status": bloco.status,
                    "assinatura": bloco.assinatura,
                }
            )
            if bloco.status == "LIVRE":
                ram_livre_mb += bloco.tamanho_mb
            elif bloco.status == "MALWARE":
                ram_malware_mb += bloco.tamanho_mb
            else:
                ram_sistema_mb += bloco.tamanho_mb

        return {
            "rodada_atual": self.rodada_atual,
            "total_rodadas": self.total_rodadas,
            "ato_atual": self._obter_ato_atual(),
            "acoes_restantes": self.acoes_restantes,
            "temperatura_cpu": self.temperatura_cpu,
            "ram_total_mb": self.ram_total_mb,
            "ram_livre_mb": ram_livre_mb,
            "ram_malware_mb": ram_malware_mb,
            "ram_sistema_mb": ram_sistema_mb,
            "blocos_ram": blocos_ram,
            "call_stack": self.call_stack.para_lista(),
            "call_stack_tamanho": self.call_stack.tamanho(),
            "call_stack_capacidade": self.call_stack.CAPACIDADE_MAXIMA,
            "fila_processos": self.fila_processos.para_lista(),
            "fila_tamanho": self.fila_processos.tamanho(),
            "setores_disco_tamanho": len(self.setores_disco),
            "disco_ordenado": self.disco_ordenado,
            "blacklist_tamanho": len(self.blacklist_ips),
            "fim_de_jogo": self.fim_de_jogo,
            "vitoria": self.vitoria,
            "motivo_fim": self.motivo_fim,
            "ultimo_evento_surpresa": self.ultimo_evento_surpresa,
        }
