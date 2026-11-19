"""Módulo de interface visual no terminal utilizando a biblioteca Rich.

Isola toda a apresentação gráfica, animações dinâmicas e interação visual
do jogo KERNEL CYBERPUNK, mantendo desacoplamento total da lógica de negócio
definida em `core/` e `engine/jogo.py`.
"""

import random
import time

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text


BANNER_KERNEL_CYBERPUNK = r"""
 _  __ _____ ____  _   _ _____ _     
| |/ /| ____|  _ \| \ | | ____| |    
| ' / |  _| | |_) |  \| |  _| | |    
| . \ | |___|  _ <| |\  | |___| |___ 
|_|\_\|_____|_| \_\_| \_|_____|_____|
  ____ __   __ ____  _____ ____  ____  _   _ _   _ _  __
 / ___|\ \ / /| __ )| ____|  _ \|  _ \| | | | \ | | |/ /
| |     \ V / |  _ \|  _| | |_) | |_) | | | |  \| | ' / 
| |___   | |  | |_) | |___|  _ <|  __/| |_| | |\  | . \ 
 \____|  |_|  |____/|_____|_| \_\_|    \___/|_| \_|_|\_\
"""

SUBTITULO_PROJETO = (
    "Contrabando de Memória — Protocolo de Defesa e Sobrevivência de Kernel v1.0"
)

CADEADO_FECHADO = r"""
          .--------.
        /   .----.   \
       |   |      |   |
       |   |      |   |
     __|   |______|   |__
   .'  |___|      |___|  '.
  |   .----------------.   |
  |  |                  |  |
  |  |     [ LOCK ]     |  |
  |  |                  |  |
   '. '----------------' .'
     '------------------'
"""

CADEADO_RACHANDO = r"""
          .--------.
        /   .----.   \    *
       |   |      |   | !
       |   |      |   |
     __|   |______|   |__  #
   .'  |___|  /   |___|  '.
  |   .------/ --------.   | *
  |  |      /           |  |
  |  |     [ CRK! ]     |  | !
  |  |                  |  |
   '. '----------------' .'
     '------------------'
"""

CADEADO_QUEBRADO = r"""
          .--------.
        /   .----.   \      *
       |   |      |   |   !
       |   |       '=='  #
     __|   |______________
   .'  |___|    / /       '.
  |   .--------/ /-------.  |  *
  |  |        / /         | |
  |  |       [ OPEN ]     | |  !
  |  |                    | |
   '. '------------------' .'
     '--------------------'
"""

CAVEIRA_HACKER = r'''
             .-------------.
           .'   _________   '.
          /   .'         '.   \
         |   |  |\       /|  |   |
         |   |  |##\   /##|  |   |
         |   |  '---' '---'  |   |
         |   |      /^\      |   |
         |   \     /___\     /   |
     __   \   '._ | | | | _.'   /   __
    /  \___\     |_|_|_|_|     /___/  \
    \__     '.    '-----'    .'     __/
       \______\    \   /    /______/
               \_____X_____/
       ________/   /   \   \________
      (___        /     \        ___)
           [ ROOTKIT :: 0xDEAD ]
'''

ESCUDO_CIBERNETICO = r'''
      .==============================.
    .'  .==========================.  '.
   /   /           |  |           \   \
  |   |            |  |            |   |
  |   |   KERNEL SHIELD :: ATIVO   |   |
  |   | ===========+  +=========== |   |
  |   | ===========+  +=========== |   |
  |   |            |  |            |   |
   \   \    [ INTEGRIDADE OK ]    /   /
    \   \          |  |          /   /
     \   '.        |  |        .'   /
      \    '.      |  |      .'    /
       '.    '.    |  |    .'    .'
         '.    '.  \  /  .'    .'
           '.    '. \/ .'    .'
             '.    '..'    .'
               '._      _.'
                  '.__.'
'''

BANNER_KERNEL_PANIC = r"""
 _  __ _____ ____  _   _ _____ _       ____   _    _   _ ___ ____ 
| |/ /| ____|  _ \| \ | | ____| |     |  _ \ / \  | \ | |_ _/ ___|
| ' / |  _| | |_) |  \| |  _| | |     | |_) / _ \ |  \| || | |    
| . \ | |___|  _ <| |\  | |___| |___  |  __/ ___ \| |\  || | |___ 
|_|\_\|_____|_| \_\_| \_|_____|_____| |_| /_/   \_\_| \_|___\____|
"""


class InterfaceCyberpunk:
    """Camada de visualização no terminal usando Rich para o Kernel Cyberpunk."""

    NOME_ATOS = {
        1: "ATO 1 — O Reconhecimento",
        2: "ATO 2 — A Escalada",
        3: "ATO 3 — O Ataque Final",
    }

    def __init__(self, console: Console = None):
        """Inicializa o console Rich e o gerador de quadros visuais."""
        self.console = console or Console(highlight=False)
        self._rng = random.Random()

    def limpar_tela(self) -> None:
        """Limpa o terminal antes de renderizar uma nova visão."""
        self.console.clear()

    def ler_opcao(self, prompt_texto: str = "Comando") -> str:
        """Lê entrada do usuário com prompt estilizado e tratamento seguro de EOF."""
        try:
            self.console.print(
                f"\n[bold bright_cyan]kernel@cyberpunk[/]:[bold bright_green]~[/]$ {prompt_texto}: ",
                end="",
            )
            return input().strip()
        except (EOFError, KeyboardInterrupt):
            return "0"

    def pausar(self, mensagem: str = "Pressione ENTER para continuar...") -> None:
        """Aguarda confirmação do jogador sem quebrar em fluxos não interativos."""
        try:
            self.console.print(f"\n[dim cyan]{mensagem}[/]", end="")
            input()
        except (EOFError, KeyboardInterrupt):
            pass

    def exibir_banner_principal(self) -> Panel:
        """Constrói o painel com a identidade visual obrigatória do projeto."""
        conteudo = Text()
        conteudo.append(BANNER_KERNEL_CYBERPUNK.strip("\n"), style="bold bright_green")
        conteudo.append("\n\n")
        conteudo.append(SUBTITULO_PROJETO, style="bold bright_cyan")
        return Panel(
            Align.center(conteudo),
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2),
        )

    def exibir_abertura(self) -> None:
        """Executa a abertura animada em 3 Atos: Cadeado, Caveira e Escudo."""
        self.limpar_tela()

        # Ato 1: Cadeado quebrando com faíscas
        quadros_cadeado = [
            (CADEADO_FECHADO, "bold cyan", "[ VERIFICANDO PORTA 0x80 :: SEGURO ]", "cyan"),
            (CADEADO_RACHANDO, "bold yellow", "[ ! ALERTA: TENTATIVA DE QUEBRA NA PORTA 0x80 ! ]", "yellow"),
            (CADEADO_QUEBRADO, "bold red", "[ INTRUSÃO DETECTADA NA PORTA 0x80 ]", "bright_red"),
        ]
        with Live(console=self.console, refresh_per_second=8, transient=True) as live:
            for arte, cor_arte, aviso, cor_borda in quadros_cadeado:
                bloco = Group(
                    Align.center(Text("ATO I :: QUEBRA DE PERÍMETRO", style="bold yellow")),
                    Align.center(Text(arte, style=cor_arte)),
                    Align.center(Text(aviso, style=f"bold {cor_borda}")),
                )
                live.update(
                    Panel(bloco, border_style=cor_borda, box=box.HEAVY, padding=(1, 2))
                )
                time.sleep(1.5)

        # Ato 2: Caveira Hacker piscando entre vermelho e verde neon (~1.8s)
        with Live(console=self.console, refresh_per_second=10, transient=True) as live:
            for ciclo in range(7):
                cor = "bold red" if ciclo % 2 == 0 else "bold bright_green"
                borda = "bright_red" if ciclo % 2 == 0 else "bright_green"
                bloco = Group(
                    Align.center(Text("ATO II :: SUBMUNDO DA RAM INVADIDO", style=cor)),
                    Align.center(Text(CAVEIRA_HACKER, style=cor)),
                    Align.center(
                        Text(
                            "PACOTES FANTASMAS DETECTADOS — CONTRABANDO DE MEMÓRIA EM CURSO",
                            style=cor,
                        )
                    ),
                )
                live.update(
                    Panel(bloco, border_style=borda, box=box.DOUBLE, padding=(1, 2))
                )
                time.sleep(0.25)

        # Ato 3: Escudo Cibernético assumindo o controle (1.5s) + Banner Principal
        with Live(console=self.console, refresh_per_second=6, transient=True) as live:
            bloco = Group(
                Align.center(Text("ATO III :: PROTOCOLO DE DEFESA INICIADO", style="bold bright_green")),
                Align.center(Text(ESCUDO_CIBERNETICO, style="bold bright_green")),
            )
            live.update(
                Panel(bloco, border_style="bright_green", box=box.DOUBLE, padding=(1, 2))
            )
            time.sleep(1.5)

        self.limpar_tela()
        self.console.print(self.exibir_banner_principal())
        self.console.print(
            Align.center(
                Text(
                    "Defenda o Kernel por 10 rodadas gerenciando RAM, Call Stack, Fila e Disco!",
                    style="italic green",
                )
            )
        )
        time.sleep(0.5)

    def efeito_matrix(self, operacao: str, duracao: float = 1.0) -> None:
        """Exibe fluxo animado em tela cheia com códigos hexadecimais e binários verdes."""
        hex_tokens = [
            "0x7FF4", "0xDEAD", "0x00A1", "0xC0DE", "0xBEEF",
            "0x00FF", "0x8086", "0xCAFE", "0x1337", "0xFA12",
        ]
        bin_tokens = ["010110", "110010", "101001", "001111", "111000", "011011"]

        largura_total = max(40, self.console.width)
        altura_painel = max(12, self.console.height - 2)
        altura_interna = max(8, altura_painel - 2)
        largura_interna = max(24, largura_total - 4)
        tokens_por_linha = max(3, (largura_interna + 2) // 8)

        def _gerar_linha() -> str:
            partes = []
            for _ in range(tokens_por_linha):
                if self._rng.random() < 0.6:
                    partes.append(self._rng.choice(hex_tokens))
                else:
                    partes.append(self._rng.choice(bin_tokens))
            return "  ".join(partes)

        linhas_tela = [_gerar_linha() for _ in range(altura_interna)]
        inicio = time.perf_counter()

        self.limpar_tela()
        with Live(
            console=self.console, refresh_per_second=14, screen=True, transient=True
        ) as live:
            while (time.perf_counter() - inicio) < duracao:
                linhas_tela.append(_gerar_linha())
                if len(linhas_tela) > altura_interna:
                    linhas_tela.pop(0)

                texto_matrix = Text()
                total_linhas = len(linhas_tela)
                for idx, linha in enumerate(linhas_tela):
                    estilo = "bold bright_green" if idx >= total_linhas - 2 else "green"
                    sufixo = "\n" if idx < total_linhas - 1 else ""
                    texto_matrix.append(linha + sufixo, style=estilo)

                painel = Panel(
                    Align.center(texto_matrix),
                    title=f"[bold bright_green]MATRIX SCAN :: {operacao}[/]",
                    border_style="bright_green",
                    box=box.SQUARE,
                    width=largura_total,
                    height=altura_painel,
                )
                live.update(painel)
                time.sleep(0.08)

        self.limpar_tela()

    def animar_ordenacao(self, nome_algoritmo: str, duracao: float = 2.5) -> None:
        """Exibe animação de 20 barras verticais se ordenando com barra de progresso."""
        simbolos = (" ", "▂", "▃", "▄", "▅", "▆", "▇", "█")
        barras = [18, 15, 19, 12, 20, 14, 16, 17, 10, 13, 8, 4, 9, 6, 2, 7, 11, 1, 3, 5]
        n = len(barras)

        progresso = Progress(
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=32, complete_style="bright_green", finished_style="green"),
            TextColumn("[bold bright_green]{task.percentage:>3.0f}%"),
        )
        tarefa = progresso.add_task(f"Desfragmentando ({nome_algoritmo})", total=100)

        # Pré-calcula os passos reais de ordenação via Selection Sort manual (23 quadros)
        passos_animacao = []
        copia = [v for v in barras]
        for i in range(n - 1):
            indice_menor = i
            for j in range(i + 1, n):
                if copia[j] < copia[indice_menor]:
                    indice_menor = j
            if indice_menor != i:
                passos_animacao.append(([v for v in copia], i, indice_menor, False))
                copia[i], copia[indice_menor] = copia[indice_menor], copia[i]
                passos_animacao.append(([v for v in copia], i, indice_menor, True))
        passos_animacao.append((copia, -1, -1, True))

        total_quadros = len(passos_animacao)
        atraso = max(0.10, min(0.12, duracao / max(total_quadros, 1)))

        def _renderizar_barras(estado_barras: list, idx_a: int, idx_b: int, trocou: bool) -> Text:
            linhas = Text()
            altura_max = 5
            for nivel in range(altura_max, 0, -1):
                limite_baixo = (nivel - 1) * 4
                for idx, valor in enumerate(estado_barras):
                    if valor >= nivel * 4:
                        char = "█"
                    elif valor > limite_baixo:
                        indice_simbolo = min(7, max(1, (valor - limite_baixo) * 2))
                        char = simbolos[indice_simbolo]
                    else:
                        char = " "

                    if idx_a == -1:
                        estilo = "bold bright_green"
                    elif idx == idx_a or idx == idx_b:
                        estilo = "bold bright_green" if trocou else "bold yellow"
                    else:
                        estilo = "cyan"
                    linhas.append(f" {char} ", style=estilo)
                linhas.append("\n")
            return linhas

        with Live(console=self.console, refresh_per_second=24, transient=True) as live:
            for indice_quadro, (estado_atual, a, b, trocou) in enumerate(passos_animacao):
                percentual = ((indice_quadro + 1) / total_quadros) * 100
                progresso.update(tarefa, completed=percentual)

                legenda = Text(
                    "Amarelo: Comparação  |  Verde: Troca / Ordenado",
                    style="dim white",
                )
                conteudo = Group(
                    Align.center(_renderizar_barras(estado_atual, a, b, trocou)),
                    Align.center(progresso),
                    Align.center(legenda),
                )
                live.update(
                    Panel(
                        conteudo,
                        title=f"[bold yellow]DESFRAGMENTAÇÃO DE DISCO :: {nome_algoritmo.upper()}[/]",
                        border_style="bright_cyan",
                        box=box.ROUNDED,
                    )
                )
                time.sleep(atraso)

    def exibir_alerta_evento(self, evento: dict) -> None:
        """Faz o alerta central piscar 3 vezes entre vermelho e amarelo intenso."""
        if not evento:
            return

        with Live(console=self.console, refresh_per_second=6, transient=False) as live:
            for ciclo in range(6):
                estilo = "bold bright_red" if ciclo % 2 == 0 else "bold bright_yellow"
                borda = "bright_red" if ciclo % 2 == 0 else "bright_yellow"
                corpo = Text()
                corpo.append(f"{evento['titulo'].upper()}\n\n", style=estilo)
                corpo.append(evento["descricao"], style="bold white")

                painel = Align.center(
                    Panel(
                        Align.center(corpo),
                        title=f"[{estilo}][ ⚠️ ALERTA CRÍTICO DE INTRUSÃO ⚠️ ][/]",
                        border_style=borda,
                        box=box.DOUBLE,
                        padding=(1, 4),
                    )
                )
                live.update(painel)
                time.sleep(0.35)
        self.pausar("Alerta crítico registrado. Pressione ENTER para assumir o terminal...")

    @staticmethod
    def _barra_ascii(valor: int, maximo: int, largura: int = 20) -> str:
        """Desenha barra de progresso ASCII proporcional sem depender de widgets externos."""
        if maximo <= 0:
            return "░" * largura
        proporcao = min(1.0, max(0.0, valor / maximo))
        preenchido = int(proporcao * largura)
        return ("█" * preenchido) + ("░" * (largura - preenchido))

    def exibir_dashboard(self, estado: dict) -> None:
        """Exibe o dashboard principal organizado com Layout, Panels e Tables."""
        self.limpar_tela()

        layout = Layout()
        layout.split_column(
            Layout(name="cabecalho", size=3),
            Layout(name="corpo", size=15),
            Layout(name="menu", size=6),
        )
        layout["corpo"].split_row(
            Layout(name="hardware", ratio=1),
            Layout(name="estruturas", ratio=1),
        )
        layout["estruturas"].split_column(
            Layout(name="pilha", size=10),
            Layout(name="fila", size=5),
        )

        # Cabeçalho
        nome_ato = self.NOME_ATOS.get(estado["ato_atual"], f"ATO {estado['ato_atual']}")
        info_cabecalho = Table.grid(expand=True)
        info_cabecalho.add_column(justify="left", ratio=2)
        info_cabecalho.add_column(justify="center", ratio=3)
        info_cabecalho.add_column(justify="right", ratio=1)
        info_cabecalho.add_row(
            Text("KERNEL CYBERPUNK", style="bold bright_green"),
            Text(
                f"RODADA {estado['rodada_atual']}/{estado['total_rodadas']} | {nome_ato}",
                style="bold bright_cyan",
            ),
            Text(
                f"AÇÕES: {estado['acoes_restantes']}/2",
                style="bold bright_yellow" if estado["acoes_restantes"] > 0 else "bold red",
            ),
        )
        layout["cabecalho"].update(
            Panel(info_cabecalho, border_style="bright_cyan", box=box.DOUBLE)
        )

        # Painel Esquerdo: Saúde do Hardware (RAM, CPU e Disco)
        temp = estado["temperatura_cpu"]
        cor_temp = "bright_green" if temp < 55 else ("yellow" if temp < 80 else "bold red")
        ram_livre = estado["ram_livre_mb"]
        ram_total = estado["ram_total_mb"]
        cor_ram = "bright_green" if ram_livre >= 256 else ("yellow" if ram_livre >= 128 else "bold red")

        tabela_hw = Table(box=box.SIMPLE, expand=True, show_header=False, padding=(0, 1))
        tabela_hw.add_column("Recurso", style="bold cyan", width=11, no_wrap=True)
        tabela_hw.add_column("Status")

        barra_ram = self._barra_ascii(ram_livre, ram_total, 10)
        tabela_hw.add_row(
            "RAM Livre",
            Text(f"[{barra_ram}] {ram_livre}/{ram_total}MB", style=cor_ram),
        )
        tabela_hw.add_row(
            "RAM Uso",
            Text(
                f"Sys: {estado['ram_sistema_mb']}MB | Mal: {estado['ram_malware_mb']}MB",
                style="bold red" if estado["ram_malware_mb"] > 0 else "dim white",
            ),
        )

        barra_cpu = self._barra_ascii(temp, 100, 10)
        tabela_hw.add_row(
            "Temp. CPU",
            Text(f"[{barra_cpu}] {temp}°C/100°C", style=cor_temp),
        )

        status_disco = (
            Text("DESFRAGMENTADO", style="bold bright_green")
            if estado["disco_ordenado"]
            else Text("FRAGMENTADO", style="bold yellow")
        )
        tabela_hw.add_row("Disco", Text(f"{estado['setores_disco_tamanho']} setores", style="white"))
        tabela_hw.add_row("Estado", status_disco)
        tabela_hw.add_row("Blacklist", Text(f"{estado['blacklist_tamanho']} IPs", style="dim cyan"))

        layout["hardware"].update(
            Panel(
                tabela_hw,
                title="[bold bright_cyan]MONITOR DE HARDWARE[/]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )

        # Painel Direito: Call Stack (Pilha 0/8) e Fila FIFO
        pilha_itens = estado["call_stack"]
        cap_pilha = estado["call_stack_capacidade"]
        tam_pilha = estado["call_stack_tamanho"]
        cor_pilha = "bright_green" if tam_pilha <= 4 else ("yellow" if tam_pilha <= 6 else "bold red")

        texto_pilha = Text()
        for slot in range(cap_pilha - 1, -1, -1):
            quebra = "\n" if slot > 0 else ""
            if slot < len(pilha_itens):
                texto_pilha.append(f" [{slot + 1}] {pilha_itens[slot]}{quebra}", style=cor_pilha)
            else:
                texto_pilha.append(f" [{slot + 1}] <vazio>{quebra}", style="dim white")

        fila_itens = estado["fila_processos"]
        texto_fila = Text()
        if fila_itens:
            frente = fila_itens[0]
            texto_fila.append(
                f"PRÓXIMO (FRENTE): PID {frente['pid']} | {frente['nome']} | IP {frente['ip']}\n",
                style="bold bright_yellow",
            )
            texto_fila.append(
                f"Total aguardando na Fila FIFO: {estado['fila_tamanho']} processo(s)",
                style="cyan",
            )
        else:
            texto_fila.append("Fila FIFO vazia — nenhum processo pendente.", style="green")

        layout["pilha"].update(
            Panel(
                texto_pilha,
                title=f"[{cor_pilha}]CALL STACK (PILHA {tam_pilha}/{cap_pilha})[/]",
                border_style=cor_pilha,
                box=box.SQUARE,
            )
        )
        layout["fila"].update(
            Panel(
                texto_fila,
                title=f"[bold cyan]ESCALONADOR FIFO ({estado['fila_tamanho']} na fila)[/]",
                border_style="cyan",
                box=box.SQUARE,
            )
        )

        # Menu de Ações
        menu_texto = Text()
        menu_texto.append("[1] ", style="bold bright_green")
        menu_texto.append("Escanear Fila (Busca Binária)    ", style="white")
        menu_texto.append("[2] ", style="bold bright_green")
        menu_texto.append("Limpar RAM (Busca Seq. + Coalescência)\n", style="white")
        menu_texto.append("[3] ", style="bold bright_green")
        menu_texto.append("Desempilhar Call Stack (Pop)     ", style="white")
        menu_texto.append("[4] ", style="bold bright_green")
        menu_texto.append("Desfragmentar Disco (Ordenação)\n", style="white")
        menu_texto.append("[5] ", style="bold bright_cyan")
        menu_texto.append("Mapa de Ponteiros da RAM (grátis) ", style="bright_cyan")
        menu_texto.append("[0] ", style="bold red")
        menu_texto.append("Abortar Sessão", style="dim red")

        layout["menu"].update(
            Panel(
                menu_texto,
                title="[bold bright_yellow]CONSOLA DE AÇÕES DEFENSIVAS[/]",
                border_style="bright_yellow",
                box=box.ROUNDED,
                padding=(0, 2),
            )
        )

        self.console.print(layout)

    def exibir_mapa_ram(self, estado: dict) -> None:
        """Desenha visualmente os nós da ListaEncadeada da RAM ligados por ponteiros."""
        blocos = estado["blocos_ram"]
        cadeia = Text()

        for idx, bloco in enumerate(blocos):
            status = bloco["status"]
            assinatura = f" ({bloco['assinatura']})" if bloco["assinatura"] else ""
            rotulo = f"[{bloco['endereco_hex']} | {bloco['tamanho_mb']}MB | {status}{assinatura}]"

            if status == "SISTEMA":
                estilo = "bold cyan"
            elif status == "MALWARE":
                estilo = "bold bright_red"
            else:
                estilo = "bold bright_green"

            cadeia.append(rotulo, style=estilo)
            if idx < len(blocos) - 1:
                cadeia.append(" ──► ", style="bold yellow")
            else:
                cadeia.append(" ──► NULL", style="dim white")

        legenda = Text("\n\n")
        legenda.append("■ SISTEMA ", style="bold cyan")
        legenda.append("■ MALWARE ", style="bold bright_red")
        legenda.append("■ LIVRE ", style="bold bright_green")
        legenda.append(
            "— Blocos LIVRE adjacentes são fundidos automaticamente por coalescência ao limpar a RAM.",
            style="dim white",
        )

        self.console.print(
            Panel(
                Group(cadeia, legenda),
                title="[bold bright_cyan]MAPA VISUAL DE PONTEIROS DA RAM (LISTA ENCADEADA)[/]",
                border_style="bright_cyan",
                box=box.DOUBLE,
                padding=(1, 2),
            )
        )
        self.pausar()

    def escolher_algoritmo_ordenacao(self) -> str | None:
        """Exibe menu para escolha do algoritmo de desfragmentação de disco."""
        tabela = Table(
            title="[bold bright_cyan]SELECIONE O ALGORITMO DE ORDENAÇÃO[/]",
            box=box.ROUNDED,
            border_style="cyan",
        )
        tabela.add_column("Opção", style="bold bright_yellow", justify="center")
        tabela.add_column("Algoritmo", style="bold white")
        tabela.add_column("Complexidade", style="cyan")
        tabela.add_column("Impacto Térmico", style="bold")

        tabela.add_row("[1]", "Selection Sort", "O(n²)", Text("+38°C (Risco Crítico!)", style="bold red"))
        tabela.add_row("[2]", "Insertion Sort", "O(n²)", Text("+32°C / +36°C (Risco Alto!)", style="bold red"))
        tabela.add_row("[3]", "Merge Sort", "O(n log n)", Text("+6°C (Eficiente)", style="bold bright_green"))
        tabela.add_row("[4]", "Quick Sort", "O(n log n)", Text("+8°C (Eficiente)", style="bold bright_green"))
        tabela.add_row("[0]", "Cancelar / Voltar", "-", Text("Não gasta ação", style="dim white"))

        self.console.print(tabela)

        mapa = {
            "1": "selection_sort",
            "2": "insertion_sort",
            "3": "merge_sort",
            "4": "quick_sort",
        }
        while True:
            escolha = self.ler_opcao("Algoritmo [0-4]")
            if escolha == "0":
                return None
            if escolha in mapa:
                return mapa[escolha]
            self.exibir_aviso("Opção inválida! Escolha entre 1, 2, 3, 4 ou 0 para voltar.")

    def exibir_resultado_fila(self, resultado: dict) -> None:
        """Exibe o relatório técnico da Busca Binária aplicada à fila FIFO."""
        if not resultado.get("sucesso"):
            self.exibir_aviso(resultado.get("erro", "Falha ao escanear fila."))
            return

        proc = resultado["processo"]
        status_texto = (
            Text("AMEAÇA BLOQUEADA E REMOVIDA DA FILA!", style="bold bright_red")
            if resultado["bloqueado"]
            else Text("PROCESSO LEGÍTIMO EXECUTADO COM SEGURANÇA.", style="bold bright_green")
        )
        corpo = Text()
        corpo.append(f"Processo: {proc['nome']} (PID {proc['pid']}) — IP {proc['ip']}\n", style="white")
        corpo.append("Resultado: ")
        corpo.append_text(status_texto)
        corpo.append(
            f"\nBusca Binária: encontrado={resultado['encontrado']} | índice={resultado['indice']} "
            f"| passos={resultado['passos']} | tempo={resultado['tempo_ms']} ms",
            style="cyan",
        )
        self.console.print(
            Panel(corpo, title="[bold cyan]RESULTADO :: BUSCA BINÁRIA NA BLACKLIST[/]", border_style="cyan")
        )
        self.pausar()

    def exibir_resultado_ram(self, resultado: dict) -> None:
        """Exibe o relatório da Busca Sequencial e coalescência na RAM."""
        if not resultado.get("sucesso"):
            self.exibir_aviso(resultado.get("erro", "Falha ao limpar RAM."))
            return

        corpo = Text()
        if resultado["limpo"]:
            no_info = resultado["no_limpo"]
            corpo.append(
                f"Malware removido em {no_info['endereco_hex']} "
                f"({no_info['tamanho_mb']} MB, assinatura {no_info['assinatura_anterior']})!\n",
                style="bold bright_green",
            )
            corpo.append(
                f"Coalescência executada: {resultado['fusoes']} fusão(ões) de blocos LIVRE adjacentes.\n",
                style="bold yellow",
            )
        else:
            corpo.append("Nenhum bloco MALWARE encontrado na RAM.\n", style="cyan")

        corpo.append(
            f"Busca Sequencial: nós percorridos={resultado['nos_percorridos']} | tempo={resultado['tempo_ms']} ms",
            style="cyan",
        )
        self.console.print(
            Panel(corpo, title="[bold bright_green]RESULTADO :: VARREDURA DE MEMÓRIA RAM[/]", border_style="bright_green")
        )
        self.pausar()

    def exibir_resultado_stack(self, resultado: dict) -> None:
        """Exibe o relatório da remoção do topo da Call Stack."""
        if not resultado.get("sucesso"):
            self.exibir_aviso(resultado.get("erro", "Call Stack já está vazia."))
            return

        corpo = Text(
            f"Frame removido do topo da Call Stack: {resultado['chamada_removida']}\n"
            f"Ocupação atual da Pilha: {resultado['tamanho_stack']} / 8",
            style="bold bright_green",
        )
        self.console.print(
            Panel(corpo, title="[bold cyan]RESULTADO :: DESEMPILHAMENTO DA CALL STACK[/]", border_style="cyan")
        )
        self.pausar()

    def exibir_resultado_disco(self, resultado: dict) -> None:
        """Exibe métricas de desempenho e impacto térmico após ordenação do disco."""
        if not resultado.get("sucesso"):
            self.exibir_aviso(resultado.get("erro", "Falha ao ordenar disco."))
            return

        tabela = Table(box=box.SIMPLE, show_header=False)
        tabela.add_column("Métrica", style="bold cyan")
        tabela.add_column("Valor", style="bold white")
        tabela.add_row("Algoritmo", resultado["algoritmo"].upper())
        tabela.add_row("Comparações", str(resultado["comparacoes"]))
        tabela.add_row("Trocas", str(resultado["trocas"]))
        tabela.add_row("Tempo (ms)", f"{resultado['tempo_ms']} ms")
        tabela.add_row(
            "Impacto Térmico",
            Text(
                f"+{resultado['impacto_termico']}°C (CPU atual: {resultado['temperatura_cpu']}°C)",
                style="bold red" if resultado["temperatura_cpu"] >= 80 else "bold yellow",
            ),
        )
        self.console.print(
            Panel(tabela, title="[bold bright_cyan]RELATÓRIO :: DESFRAGMENTAÇÃO DE DISCO[/]", border_style="bright_cyan")
        )
        self.pausar()

    def exibir_resumo_rodada(self, resumo: dict) -> None:
        """Exibe o que ocorreu no processamento do fim da rodada."""
        if not resumo.get("sucesso") or resumo.get("fim_de_jogo"):
            return

        corpo = Text()
        executados = resumo.get("processos_seguros_executados", [])
        corpo.append(f"Processos legítimos finalizados: {len(executados)}\n", style="green")

        invasao = resumo.get("invasao_ocorrida")
        if invasao:
            proc = invasao["processo"]
            corpo.append(
                f"INVASÃO! Processo malicioso restante {proc['nome']} (PID {proc['pid']}) "
                f"atingiu o alvo: {invasao['tipo']}!\n",
                style="bold red",
            )
        else:
            corpo.append("Nenhuma invasão na fila ao encerrar a rodada.\n", style="bright_green")

        self.console.print(
            Panel(
                corpo,
                title=f"[bold yellow]FIM DA RODADA {resumo['rodada_concluida']}[/]",
                border_style="yellow",
            )
        )
        time.sleep(0.6)

    def exibir_aviso(self, mensagem: str) -> None:
        """Exibe uma caixa de aviso estilizada sem interromper o programa."""
        self.console.print(
            Panel(Text(mensagem, style="bold yellow"), border_style="yellow", title="[ AVISO ]")
        )
        time.sleep(0.5)

    def _construir_tabela_benchmark(self, historico_benchmark: dict) -> Table:
        """Cria a Table estilizada do Boletim Final de Benchmark."""
        nomes_legiveis = [
            ("selection_sort", "Selection Sort", "O(n²)"),
            ("insertion_sort", "Insertion Sort", "O(n²)"),
            ("merge_sort", "MergeSort", "O(n log n)"),
            ("quick_sort", "QuickSort", "O(n log n)"),
            ("busca_sequencial", "Busca Sequencial", "O(n)"),
            ("busca_binaria", "Busca Binária", "O(log n)"),
        ]

        tabela = Table(
            title="[bold bright_cyan]BOLETIM FINAL DE BENCHMARK — MÉTRICAS REAIS DA PARTIDA[/]",
            box=box.DOUBLE_EDGE,
            border_style="bright_cyan",
        )
        tabela.add_column("Algoritmo", style="bold white")
        tabela.add_column("Complexidade", style="cyan", justify="center")
        tabela.add_column("Execuções", style="yellow", justify="right")
        tabela.add_column("Comparações", style="bright_green", justify="right")
        tabela.add_column("Trocas", style="magenta", justify="right")
        tabela.add_column("Tempo Total (ms)", style="bold bright_cyan", justify="right")

        for chave, rotulo, complexidade in nomes_legiveis:
            dados = historico_benchmark.get(chave, {})
            tabela.add_row(
                rotulo,
                complexidade,
                str(dados.get("execucoes", 0)),
                str(dados.get("comparacoes", 0)),
                str(dados.get("trocas", 0)),
                f"{dados.get('tempo_ms', 0.0):.4f}",
            )
        return tabela

    def exibir_tela_derrota(self, estado: dict, historico_benchmark: dict) -> None:
        """Exibe o banner dramático de Kernel Panic detalhando o motivo exato da derrota."""
        self.limpar_tela()
        motivo_bruto = estado.get("motivo_fim", "FALHA CRÍTICA")
        mapa_motivos = {
            "Stack Overflow": "STACK OVERFLOW",
            "Superaquecimento": "SUPERAQUECIMENTO DA CPU",
            "Colapso de Memória": "COLAPSO DE MEMÓRIA",
        }
        motivo_formatado = mapa_motivos.get(motivo_bruto, motivo_bruto.upper())

        conteudo = Group(
            Align.center(Text(BANNER_KERNEL_PANIC.strip("\n"), style="bold red")),
            Align.center(Text(CAVEIRA_HACKER, style="bold bright_red")),
            Align.center(
                Text(
                    f"CAUSA FATAL: {motivo_formatado} (Rodada {estado['rodada_atual']} / {estado['total_rodadas']})",
                    style="bold bright_yellow on red",
                )
            ),
        )
        self.console.print(
            Panel(
                conteudo,
                title="[bold red]SYSTEM HALTED :: KERNEL PANIC[/]",
                border_style="bright_red",
                box=box.DOUBLE,
                padding=(1, 2),
            )
        )
        self.console.print(self._construir_tabela_benchmark(historico_benchmark))

    def exibir_tela_vitoria(self, estado: dict, historico_benchmark: dict) -> None:
        """Exibe o escudo estabilizado e o Boletim Final de Benchmark."""
        self.limpar_tela()
        conteudo = Group(
            Align.center(Text(ESCUDO_CIBERNETICO, style="bold bright_green")),
            Align.center(
                Text(
                    "VITÓRIA! O KERNEL SOBREVIVEU ÀS 10 RODADAS DE CONTRABANDO DE MEMÓRIA!",
                    style="bold bright_cyan",
                )
            ),
            Align.center(
                Text(
                    f"Temperatura final da CPU: {estado['temperatura_cpu']}°C  |  "
                    f"RAM Livre: {estado['ram_livre_mb']} MB",
                    style="green",
                )
            ),
        )
        self.console.print(
            Panel(
                conteudo,
                title="[bold bright_green]MISSÃO CUMPRIDA :: KERNEL ESTABILIZADO[/]",
                border_style="bright_green",
                box=box.DOUBLE,
                padding=(1, 2),
            )
        )
        self.console.print(self._construir_tabela_benchmark(historico_benchmark))
