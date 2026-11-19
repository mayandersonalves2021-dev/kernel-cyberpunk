"""Script de testes unitários manuais para o núcleo (core) do Kernel Guardian.

Valida as estruturas de dados (`No`, `ListaEncadeada`, `Pilha`, `Fila`) e
os algoritmos manuais de ordenação e busca em Python puro.
"""

import os
import sys

# Garante que a raiz do projeto esteja no sys.path ao executar diretamente
RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from core.estruturas import No, ListaEncadeada, Pilha, Fila
from core.algoritmos import (
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    busca_sequencial,
    busca_binaria,
)


def testar_lista_encadeada():
    """Testa inserção, remoção por endereço, validação de status e coalescência."""
    memoria = ListaEncadeada()
    assert memoria.esta_vazia() is True
    assert memoria.tamanho() == 0

    # Valida exceção para status inválido
    erro_status = False
    try:
        No("0xFFFF", 16, "DESCONHECIDO", "INVALIDO")
    except ValueError:
        erro_status = True
    assert erro_status is True, "Deveria lançar ValueError para status inválido."

    # Inserção por parâmetros e por instância de No
    memoria.inserir("0x0000", 64, "SISTEMA", "KERNEL_BASE")
    memoria.inserir("0x0040", 32, "LIVRE", "")
    memoria.inserir(No("0x0060", 16, "LIVRE", ""))
    memoria.inserir("0x0070", 48, "MALWARE", "TROJAN_X")
    memoria.inserir("0x00A0", 32, "LIVRE", "")
    memoria.inserir("0x00C0", 64, "LIVRE", "")
    memoria.inserir("0x0100", 32, "LIVRE", "")

    assert memoria.esta_vazia() is False
    assert memoria.tamanho() == 7
    assert memoria.inicio is memoria.cabeca
    assert memoria.cabeca.endereco_hex == "0x0000"

    # Coalescência de blocos LIVRE adjacentes (2 seguidos e 3 seguidos)
    fusoes = memoria.coalescencia()
    assert fusoes == 3, f"Esperava 3 fusões, obteve {fusoes}."
    assert memoria.tamanho() == 4

    blocos = memoria.para_lista()
    assert blocos[0].endereco_hex == "0x0000" and blocos[0].tamanho_mb == 64
    assert blocos[1].endereco_hex == "0x0040" and blocos[1].tamanho_mb == 48
    assert blocos[2].endereco_hex == "0x0070" and blocos[2].status == "MALWARE"
    assert blocos[3].endereco_hex == "0x00A0" and blocos[3].tamanho_mb == 128

    # Remoção por endereço (meio, cabeça, fim e inexistente)
    removido_malware = memoria.remover_por_endereco("0x0070")
    assert removido_malware is not None and removido_malware.assinatura == "TROJAN_X"
    assert memoria.tamanho() == 3

    # Após remover o malware entre 0x0040 (LIVRE) e 0x00A0 (LIVRE), nova coalescência deve fundi-los
    fusoes_pos_remocao = memoria.coalescencia()
    assert fusoes_pos_remocao == 1
    assert memoria.tamanho() == 2
    assert memoria.cabeca.proximo.tamanho_mb == 176

    removido_cabeca = memoria.remover_por_endereco("0x0000")
    assert removido_cabeca is not None and removido_cabeca.endereco_hex == "0x0000"
    assert memoria.tamanho() == 1

    removido_inexistente = memoria.remover_por_endereco("0x9999")
    assert removido_inexistente is None

    removido_ultimo = memoria.remover_por_endereco("0x0040")
    assert removido_ultimo is not None
    assert memoria.esta_vazia() is True

    print("[OK] No e ListaEncadeada (inserção, remoção por endereço e coalescência)")


def testar_pilha():
    """Testa a Call Stack com capacidade fixa de 8 itens e comportamento LIFO."""
    pilha = Pilha()
    assert pilha.esta_vazia() is True
    assert pilha.esta_cheia() is False
    assert pilha.tamanho() == 0
    assert pilha.peek() is None
    assert pilha.pop() is None

    # Preenche até o limite de 8 itens
    for i in range(1, 9):
        sucesso = pilha.push(f"FRAME_{i}")
        assert sucesso is True
        assert pilha.tamanho() == i
        assert pilha.peek() == f"FRAME_{i}"

    assert pilha.esta_cheia() is True
    assert pilha.esta_vazia() is False

    # Tentativa de 9º item deve falhar sem sobrescrever o topo
    overflow = pilha.push("FRAME_9")
    assert overflow is False
    assert pilha.tamanho() == 8
    assert pilha.peek() == "FRAME_8"

    # Remoção na ordem LIFO
    for i in range(8, 0, -1):
        item = pilha.pop()
        assert item == f"FRAME_{i}"

    assert pilha.esta_vazia() is True
    assert pilha.tamanho() == 0
    assert pilha.pop() is None

    print("[OK] Pilha (Call Stack com capacidade máxima fixa de 8 itens)")


def testar_fila():
    """Testa o escalonador FIFO e todas as operações da Fila."""
    fila = Fila()
    assert fila.esta_vazia() is True
    assert fila.tamanho() == 0
    assert fila.frente() is None
    assert fila.dequeue() is None

    processos = ["PID_101", "PID_102", "PID_103", "PID_104"]
    for proc in processos:
        fila.enqueue(proc)

    assert fila.esta_vazia() is False
    assert fila.tamanho() == 4
    assert fila.frente() == "PID_101"
    assert fila.para_lista() == processos

    for esperado in processos:
        removido = fila.dequeue()
        assert removido == esperado

    assert fila.esta_vazia() is True
    assert fila.tamanho() == 0
    assert fila.frente() is None
    assert fila.dequeue() is None

    print("[OK] Fila (Escalonador FIFO)")


def testar_algoritmos_ordenacao():
    """Testa selection_sort, insertion_sort, merge_sort e quick_sort."""
    entrada = [42, 5, 12, 1, 9, 5, 2]
    copia_controle = [42, 5, 12, 1, 9, 5, 2]
    esperado = [1, 2, 5, 5, 9, 12, 42]

    algoritmos = [
        ("selection_sort", selection_sort),
        ("insertion_sort", insertion_sort),
        ("merge_sort", merge_sort),
        ("quick_sort", quick_sort),
    ]

    for nome, funcao in algoritmos:
        resultado = funcao(entrada)

        # Garante que a lista de entrada não foi alterada
        assert entrada == copia_controle, f"{nome} modificou a lista original."

        # Valida chaves e tipos do dicionário retornado
        assert set(resultado.keys()) == {
            "ordenado",
            "comparacoes",
            "trocas",
            "tempo_ms",
        }
        assert resultado["ordenado"] == esperado, (
            f"{nome} retornou {resultado['ordenado']} em vez de {esperado}"
        )
        assert isinstance(resultado["comparacoes"], int) and resultado["comparacoes"] > 0
        assert isinstance(resultado["trocas"], int) and resultado["trocas"] >= 0
        assert isinstance(resultado["tempo_ms"], float) and resultado["tempo_ms"] >= 0.0

        # Casos de borda: lista vazia e unitária
        assert funcao([])["ordenado"] == []
        assert funcao([99])["ordenado"] == [99]

    print("[OK] Algoritmos de ordenação (selection, insertion, merge e quick sort)")


def testar_algoritmos_busca():
    """Testa busca_sequencial em ListaEncadeada e busca_binaria em lista ordenada."""
    memoria = ListaEncadeada()
    memoria.inserir("0x0010", 32, "SISTEMA", "SYS_BOOT")
    memoria.inserir("0x0030", 16, "LIVRE", "")
    memoria.inserir("0x0040", 64, "MALWARE", "WORM_V2")
    memoria.inserir("0x0080", 32, "SISTEMA", "SYS_NET")

    # Busca sequencial: caso encontrado
    no_encontrado, nos_percorridos = busca_sequencial(memoria, "WORM_V2")
    assert no_encontrado is not None
    assert no_encontrado.endereco_hex == "0x0040"
    assert no_encontrado.status == "MALWARE"
    assert nos_percorridos == 3

    # Busca sequencial: caso não encontrado
    no_ausente, percorridos_ausente = busca_sequencial(memoria, "ROOTKIT_Z")
    assert no_ausente is None
    assert percorridos_ausente == 4

    # Busca binária: caso encontrado
    assinaturas_ordenadas = [10, 20, 30, 40, 50, 60, 70, 80]
    encontrado, indice, passos = busca_binaria(assinaturas_ordenadas, 60)
    assert encontrado is True
    assert indice == 5
    assert assinaturas_ordenadas[indice] == 60
    assert passos >= 1

    # Busca binária: caso não encontrado
    encontrado_ausente, indice_ausente, passos_ausente = busca_binaria(
        assinaturas_ordenadas, 45
    )
    assert encontrado_ausente is False
    assert indice_ausente == -1
    assert passos_ausente >= 1

    # Busca binária em lista vazia
    assert busca_binaria([], 10) == (False, -1, 0)

    print("[OK] Algoritmos de busca (busca_sequencial e busca_binaria)")


def executar_todos_os_testes():
    """Executa toda a suíte de testes do núcleo."""
    print("=== INICIANDO TESTES DO NÚCLEO (CORE) - KERNEL GUARDIAN ===")
    testar_lista_encadeada()
    testar_pilha()
    testar_fila()
    testar_algoritmos_ordenacao()
    testar_algoritmos_busca()
    print("===========================================================")
    print("Todos os testes do núcleo passaram com sucesso!")


if __name__ == "__main__":
    executar_todos_os_testes()
