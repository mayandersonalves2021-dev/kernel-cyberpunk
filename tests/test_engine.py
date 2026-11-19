"""Script de testes automatizados para o motor de regras (engine/jogo.py).

Simula uma partida completa de 10 rodadas até a vitória (validando todos os
atos, os 2 eventos surpresa e as 4 ações defensivas) e também os 3 cenários
de derrota (Superaquecimento, Stack Overflow e Colapso de Memória).
"""

import os
import sys

RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from engine.jogo import MotorJogo


def testar_estado_inicial():
    """Valida todas as condições iniciais definidas para o MotorJogo."""
    motor = MotorJogo(seed=42)

    assert motor.rodada_atual == 1
    assert motor.total_rodadas == 10
    assert motor.acoes_restantes == 2
    assert motor.temperatura_cpu == 25
    assert motor.ram_total_mb == 1024
    assert len(motor.setores_disco) == 200
    assert len(motor.blacklist_ips) == 10000
    assert motor.call_stack.esta_vazia() is True
    assert motor.fila_processos.esta_vazia() is True
    assert motor.fim_de_jogo is False

    # Garante manualmente que a blacklist de 10.000 IPs está estritamente ordenada
    for i in range(len(motor.blacklist_ips) - 1):
        assert motor.blacklist_ips[i] < motor.blacklist_ips[i + 1]

    # Garante soma dos blocos iniciais de RAM = 1024 MB
    soma_ram = 0
    for bloco in motor.ram:
        soma_ram += bloco.tamanho_mb
    assert soma_ram == 1024

    print("[OK] Estado inicial do MotorJogo validado")


def testar_partida_completa_vitoria():
    """Simula uma partida completa de 10 rodadas com um bot estratégico até a Vitória."""
    motor = MotorJogo(seed=42)
    evento_1_visto = False
    evento_2_visto = False

    while not motor.fim_de_jogo:
        inicio = motor.iniciar_rodada()
        assert inicio["sucesso"] is True
        rodada = inicio["rodada"]

        # Valida curva de dificuldade e eventos surpresa
        if rodada <= 3:
            assert inicio["ato"] == 1
            assert len(motor.setores_disco) == 200
        elif rodada <= 7:
            assert inicio["ato"] == 2
            assert len(motor.setores_disco) == 1500
            if rodada == 4:
                evento = inicio["evento_surpresa"]
                assert evento is not None and evento["id"] == 1
                assert evento["titulo"] == "Injeção de Pacotes Fantasmas"
                assert motor.fila_processos.tamanho() >= 4
                evento_1_visto = True
        else:
            assert inicio["ato"] == 3
            assert len(motor.setores_disco) == 5000
            if rodada == 8:
                evento = inicio["evento_surpresa"]
                assert evento is not None and evento["id"] == 2
                assert evento["titulo"] == "Sobrecarga Térmica + Embaralhamento Total"
                assert motor.temperatura_cpu >= 65
                evento_2_visto = True

        # Executa as 2 ações disponíveis na rodada usando heurística defensiva
        while motor.acoes_restantes > 0 and not motor.fim_de_jogo:
            estado = motor.obter_estado()

            if rodada == 8 and not motor.disco_ordenado:
                res = motor.acao_desfragmentar_disco("merge_sort")
                assert res["sucesso"] is True
                assert res["impacto_termico"] == 6
            elif rodada == 2 and not motor.disco_ordenado:
                res = motor.acao_desfragmentar_disco("quick_sort")
                assert res["sucesso"] is True
                assert res["impacto_termico"] == 8
            elif estado["call_stack_tamanho"] >= 5:
                res = motor.acao_desempilhar_stack()
                assert res["sucesso"] is True
            elif estado["ram_malware_mb"] > 0:
                res = motor.acao_limpar_ram()
                assert res["sucesso"] is True
                assert res["limpo"] is True
            elif not motor.fila_processos.esta_vazia():
                res = motor.acao_escanear_fila()
                assert res["sucesso"] is True
                assert res["passos"] >= 1
            elif estado["call_stack_tamanho"] > 0:
                res = motor.acao_desempilhar_stack()
                assert res["sucesso"] is True
            else:
                res = motor.acao_desfragmentar_disco("merge_sort")
                assert res["sucesso"] is True

        resumo_fim = motor.finalizar_rodada()
        assert resumo_fim["sucesso"] is True

    assert evento_1_visto is True, "Evento Surpresa 1 não foi disparado na rodada 4."
    assert evento_2_visto is True, "Evento Surpresa 2 não foi disparado na rodada 8."
    assert motor.fim_de_jogo is True
    assert motor.vitoria is True
    assert motor.motivo_fim == "Vitória"
    assert motor.rodada_atual == 10

    # Valida que o histórico de benchmark acumulou métricas reais
    assert motor.historico_benchmark["merge_sort"]["execucoes"] >= 1
    assert motor.historico_benchmark["quick_sort"]["execucoes"] >= 1
    assert motor.historico_benchmark["busca_binaria"]["execucoes"] >= 1
    assert motor.historico_benchmark["busca_sequencial"]["execucoes"] >= 1
    assert motor.historico_benchmark["merge_sort"]["comparacoes"] > 0

    print("[OK] Simulação de 10 rodadas até a Vitória e eventos surpresa validados")


def testar_derrota_superaquecimento():
    """Valida a armadilha térmica na Rodada 8 ao usar algoritmos O(n²)."""
    for algoritmo_pesado in ("selection_sort", "insertion_sort"):
        motor = MotorJogo(seed=7)
        motor.rodada_atual = 8
        motor.iniciar_rodada()
        assert motor.temperatura_cpu == 65
        assert len(motor.setores_disco) == 5000

        res = motor.acao_desfragmentar_disco(algoritmo_pesado)
        assert res["sucesso"] is True
        assert motor.temperatura_cpu >= 100
        assert motor.fim_de_jogo is True
        assert motor.vitoria is False
        assert motor.motivo_fim == "Superaquecimento"

    print("[OK] Derrota por Superaquecimento (O(n²) na Rodada 8) validada")


def testar_derrota_stack_overflow():
    """Valida Game Over por Stack Overflow ao ignorar a Call Stack até exceder 8 itens."""
    motor = MotorJogo(seed=99)

    while not motor.fim_de_jogo and motor.rodada_atual <= 10:
        motor.iniciar_rodada()
        if motor.fim_de_jogo:
            break
        # Não desempilha a stack; apenas avança as rodadas
        motor.finalizar_rodada()

    assert motor.fim_de_jogo is True
    assert motor.vitoria is False
    assert motor.motivo_fim == "Stack Overflow"

    print("[OK] Derrota por Stack Overflow validada")


def testar_derrota_colapso_memoria():
    """Valida Game Over por Colapso de Memória quando não há blocos LIVRE suficientes."""
    motor = MotorJogo(seed=123)

    # Ocupa os 512 MB livres iniciais em blocos de 128 MB (4 alocações)
    for _ in range(4):
        assert motor._injetar_malware_ram(tamanho_mb=128, assinatura="0xDEAD") is True

    # A 5ª alocação deve falhar por falta de bloco LIVRE e encerrar o jogo
    assert motor._injetar_malware_ram(tamanho_mb=128, assinatura="0xDEAD") is False
    assert motor.fim_de_jogo is True
    assert motor.vitoria is False
    assert motor.motivo_fim == "Colapso de Memória"

    print("[OK] Derrota por Colapso de Memória validada")


def executar_todos_os_testes():
    """Executa toda a suíte de validação do motor de regras."""
    print("=== INICIANDO TESTES DO MOTOR (ENGINE) - KERNEL GUARDIAN ===")
    testar_estado_inicial()
    testar_partida_completa_vitoria()
    testar_derrota_superaquecimento()
    testar_derrota_stack_overflow()
    testar_derrota_colapso_memoria()
    print("============================================================")
    print("Todos os testes do motor passaram com sucesso!")


if __name__ == "__main__":
    executar_todos_os_testes()
