"""Módulo de algoritmos manuais de ordenação e busca do Kernel Guardian.

Todos os algoritmos foram implementados 100% manualmente em Python puro,
sem uso de `list.sort()`, `sorted()`, `bisect` ou bibliotecas externas
de ordenação/busca. O módulo `time` é utilizado exclusivamente para medir
o tempo de execução em milissegundos.
"""

import time


def _copiar_lista(lista: list) -> list:
    """Cria manualmente uma cópia rasa da lista de entrada sem alterá-la."""
    return [item for item in lista]


def _montar_resultado(
    ordenado: list, comparacoes: int, trocas: int, inicio_tempo: float
) -> dict:
    """Padroniza o dicionário de retorno com métricas dos algoritmos de ordenação."""
    fim_tempo = time.perf_counter()
    tempo_ms = round((fim_tempo - inicio_tempo) * 1000, 4)
    return {
        "ordenado": ordenado,
        "comparacoes": comparacoes,
        "trocas": trocas,
        "tempo_ms": tempo_ms,
    }


def selection_sort(lista: list) -> dict:
    """Ordena uma cópia da lista utilizando Selection Sort manual.

    Complexidade de tempo: O(n²) em todos os casos.
    Retorna dicionário com a lista ordenada e métricas de desempenho.
    """
    inicio_tempo = time.perf_counter()
    dados = _copiar_lista(lista)
    n = len(dados)
    comparacoes = 0
    trocas = 0

    for i in range(n - 1):
        indice_menor = i
        for j in range(i + 1, n):
            comparacoes += 1
            if dados[j] < dados[indice_menor]:
                indice_menor = j

        if indice_menor != i:
            dados[i], dados[indice_menor] = dados[indice_menor], dados[i]
            trocas += 1

    return _montar_resultado(dados, comparacoes, trocas, inicio_tempo)


def insertion_sort(lista: list) -> dict:
    """Ordena uma cópia da lista utilizando Insertion Sort manual.

    Complexidade de tempo: O(n) no melhor caso e O(n²) no pior caso.
    Retorna dicionário com a lista ordenada e métricas de desempenho.
    """
    inicio_tempo = time.perf_counter()
    dados = _copiar_lista(lista)
    n = len(dados)
    comparacoes = 0
    trocas = 0

    for i in range(1, n):
        chave = dados[i]
        j = i - 1

        while j >= 0:
            comparacoes += 1
            if dados[j] > chave:
                dados[j + 1] = dados[j]
                trocas += 1
                j -= 1
            else:
                break

        if j + 1 != i:
            dados[j + 1] = chave

    return _montar_resultado(dados, comparacoes, trocas, inicio_tempo)


def _merge(esquerda: list, direita: list, metricas: dict) -> list:
    """Intercala duas sublistas já ordenadas em uma única lista ordenada."""
    resultado = []
    i = 0
    j = 0
    tam_esq = len(esquerda)
    tam_dir = len(direita)

    while i < tam_esq and j < tam_dir:
        metricas["comparacoes"] += 1
        if esquerda[i] <= direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
        metricas["trocas"] += 1

    # Copia os elementos restantes da sublista esquerda, se houver
    while i < tam_esq:
        resultado.append(esquerda[i])
        i += 1
        metricas["trocas"] += 1

    # Copia os elementos restantes da sublista direita, se houver
    while j < tam_dir:
        resultado.append(direita[j])
        j += 1
        metricas["trocas"] += 1

    return resultado


def _merge_sort_recursivo(sublista: list, metricas: dict) -> list:
    """Divide recursivamente a lista ao meio e realiza a intercalação ordenada."""
    if len(sublista) <= 1:
        return sublista

    meio = len(sublista) // 2
    esquerda = _merge_sort_recursivo(sublista[:meio], metricas)
    direita = _merge_sort_recursivo(sublista[meio:], metricas)
    return _merge(esquerda, direita, metricas)


def merge_sort(lista: list) -> dict:
    """Ordena uma cópia da lista utilizando Merge Sort recursivo manual.

    Complexidade de tempo: O(n log n) em todos os casos.
    Retorna dicionário com a lista ordenada e métricas de desempenho.
    """
    inicio_tempo = time.perf_counter()
    dados = _copiar_lista(lista)
    metricas = {"comparacoes": 0, "trocas": 0}

    ordenado = _merge_sort_recursivo(dados, metricas)
    return _montar_resultado(
        ordenado, metricas["comparacoes"], metricas["trocas"], inicio_tempo
    )


def _particionar(dados: list, inicio: int, fim: int, metricas: dict) -> int:
    """Particiona a sublista em torno de um pivô (esquema de Lomuto).

    Utiliza o elemento central como pivô, movendo-o para o final antes da
    varredura para mitigar o pior caso em entradas já ordenadas.
    """
    meio = (inicio + fim) // 2
    if meio != fim:
        dados[meio], dados[fim] = dados[fim], dados[meio]
        metricas["trocas"] += 1

    pivo = dados[fim]
    indice_menor = inicio - 1

    for j in range(inicio, fim):
        metricas["comparacoes"] += 1
        if dados[j] <= pivo:
            indice_menor += 1
            if indice_menor != j:
                dados[indice_menor], dados[j] = dados[j], dados[indice_menor]
                metricas["trocas"] += 1

    posicao_pivo = indice_menor + 1
    if posicao_pivo != fim:
        dados[posicao_pivo], dados[fim] = dados[fim], dados[posicao_pivo]
        metricas["trocas"] += 1

    return posicao_pivo


def _quick_sort_recursivo(
    dados: list, inicio: int, fim: int, metricas: dict
) -> None:
    """Executa o particionamento recursivo do Quick Sort sobre a lista."""
    if inicio < fim:
        posicao_pivo = _particionar(dados, inicio, fim, metricas)
        _quick_sort_recursivo(dados, inicio, posicao_pivo - 1, metricas)
        _quick_sort_recursivo(dados, posicao_pivo + 1, fim, metricas)


def quick_sort(lista: list) -> dict:
    """Ordena uma cópia da lista utilizando Quick Sort manual.

    Complexidade de tempo: O(n log n) no caso médio e O(n²) no pior caso.
    Retorna dicionário com a lista ordenada e métricas de desempenho.
    """
    inicio_tempo = time.perf_counter()
    dados = _copiar_lista(lista)
    metricas = {"comparacoes": 0, "trocas": 0}

    if len(dados) > 1:
        _quick_sort_recursivo(dados, 0, len(dados) - 1, metricas)

    return _montar_resultado(
        dados, metricas["comparacoes"], metricas["trocas"], inicio_tempo
    )


def busca_sequencial(lista_encadeada, assinatura_alvo: str) -> tuple:
    """Percorre os nós manualmente via `.proximo` procurando a assinatura alvo.

    Aceita tanto uma instância de `ListaEncadeada` quanto um nó inicial `No`.
    Retorna uma tupla `(no_encontrado, nos_percorridos)`.
    """
    if lista_encadeada is None:
        return (None, 0)

    atual = (
        lista_encadeada.cabeca
        if hasattr(lista_encadeada, "cabeca")
        else lista_encadeada
    )
    nos_percorridos = 0

    while atual is not None:
        nos_percorridos += 1
        if atual.assinatura == assinatura_alvo:
            return (atual, nos_percorridos)
        atual = atual.proximo

    return (None, nos_percorridos)


def busca_binaria(lista_ordenada: list, alvo) -> tuple:
    """Realiza busca binária iterativa manual em uma lista previamente ordenada.

    Complexidade de tempo: O(log n).
    Retorna uma tupla `(encontrado: bool, indice: int, passos: int)`.
    """
    esquerda = 0
    direita = len(lista_ordenada) - 1
    passos = 0

    while esquerda <= direita:
        passos += 1
        meio = (esquerda + direita) // 2
        valor_meio = lista_ordenada[meio]

        if valor_meio == alvo:
            return (True, meio, passos)
        elif valor_meio < alvo:
            esquerda = meio + 1
        else:
            direita = meio - 1

    return (False, -1, passos)
