"""Ponto de entrada principal do jogo KERNEL CYBERPUNK: Contrabando de Memória."""

import os
import sys

# Garante que a raiz do projeto esteja no sys.path em qualquer forma de execução
RAIZ_PROJETO = os.path.dirname(os.path.abspath(__file__))
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from engine.jogo import MotorJogo
from ui.interface import InterfaceCyberpunk


def _configurar_utf8() -> None:
    """Garante codificação UTF-8 no console quando suportada pelo ambiente."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except OSError:
                pass


def executar_partida(ui: InterfaceCyberpunk, pular_abertura: bool = False) -> bool:
    """Executa uma partida completa de até 10 rodadas.

    Retorna True quando a partida chega ao fim normal (vitória ou derrota) e
    False quando o jogador escolhe abortar a sessão pelo menu.
    """
    motor = MotorJogo()

    if not pular_abertura:
        ui.exibir_abertura()
        ui.pausar("Pressione ENTER para assumir o terminal do Kernel...")

    while not motor.fim_de_jogo:
        inicio = motor.iniciar_rodada()

        if inicio.get("evento_surpresa"):
            ui.exibir_alerta_evento(inicio["evento_surpresa"])

        while motor.acoes_restantes > 0 and not motor.fim_de_jogo:
            estado = motor.obter_estado()
            ui.exibir_dashboard(estado)
            opcao = ui.ler_opcao("Escolha sua ação [0-5]")

            if opcao == "1":
                if not motor.fila_processos.esta_vazia():
                    ui.efeito_matrix("BUSCA BINÁRIA NA BLACKLIST")
                resultado = motor.acao_escanear_fila()
                ui.exibir_resultado_fila(resultado)

            elif opcao == "2":
                ui.efeito_matrix("BUSCA SEQUENCIAL NA RAM")
                resultado = motor.acao_limpar_ram()
                ui.exibir_resultado_ram(resultado)

            elif opcao == "3":
                resultado = motor.acao_desempilhar_stack()
                ui.exibir_resultado_stack(resultado)

            elif opcao == "4":
                algoritmo = ui.escolher_algoritmo_ordenacao()
                if algoritmo is not None:
                    ui.animar_ordenacao(algoritmo)
                    resultado = motor.acao_desfragmentar_disco(algoritmo)
                    ui.exibir_resultado_disco(resultado)

            elif opcao == "5":
                ui.exibir_mapa_ram(estado)

            elif opcao == "0":
                ui.exibir_aviso("Sessão encerrada pelo operador. Saindo do Kernel...")
                return False

            else:
                ui.exibir_aviso(
                    f"Comando '{opcao}' inválido! Selecione uma opção entre 0 e 5."
                )

        if not motor.fim_de_jogo:
            resumo = motor.finalizar_rodada()
            ui.exibir_resumo_rodada(resumo)

    estado_final = motor.obter_estado()
    if motor.vitoria:
        ui.exibir_tela_vitoria(estado_final, motor.historico_benchmark)
    else:
        ui.exibir_tela_derrota(estado_final, motor.historico_benchmark)

    return True


def main() -> None:
    """Inicializa a interface e gerencia o ciclo de partidas."""
    _configurar_utf8()
    ui = InterfaceCyberpunk()
    pular_abertura = "--sem-abertura" in sys.argv

    try:
        while True:
            finalizou_normalmente = executar_partida(
                ui, pular_abertura=pular_abertura
            )
            if not finalizou_normalmente:
                break

            resposta = ui.ler_opcao("Deseja jogar novamente? [S/N]").lower()
            if resposta not in ("s", "sim"):
                ui.exibir_aviso("Desconectando do Kernel Cyberpunk. Até a próxima!")
                break
    except KeyboardInterrupt:
        ui.exibir_aviso("Interrupção recebida. Encerrando sessão com segurança.")


if __name__ == "__main__":
    main()
