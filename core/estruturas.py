"""Módulo de estruturas de dados fundamentais do Kernel Guardian.

Todas as estruturas foram implementadas 100% manualmente em Python puro,
sem dependência de bibliotecas prontas de estruturas de dados, visando
clareza didática e rigor acadêmico.
"""


STATUS_VALIDOS = ("LIVRE", "SISTEMA", "MALWARE")


class No:
    """Representa um bloco individual de memória RAM na lista encadeada.

    Atributos:
        endereco_hex (str): Endereço hexadecimal inicial do bloco (ex: '0x00A0').
        tamanho_mb (int): Tamanho ocupado pelo bloco em megabytes.
        status (str): Estado do bloco ('LIVRE', 'SISTEMA' ou 'MALWARE').
        assinatura (str): Identificador ou assinatura do processo/ameaça no bloco.
        proximo (No | None): Ponteiro para o próximo bloco adjacente na memória.
    """

    def __init__(
        self,
        endereco_hex: str,
        tamanho_mb: int,
        status: str = "LIVRE",
        assinatura: str = "",
        proximo=None,
    ):
        """Inicializa um nó de bloco de memória validando seu status."""
        if status not in STATUS_VALIDOS:
            raise ValueError(
                f"Status inválido '{status}'. Valores permitidos: {STATUS_VALIDOS}."
            )
        self.endereco_hex = endereco_hex
        self.tamanho_mb = tamanho_mb
        self.status = status
        self.assinatura = assinatura
        self.proximo = proximo

    def __repr__(self) -> str:
        """Retorna uma representação legível do bloco de memória."""
        return (
            f"No(endereco_hex='{self.endereco_hex}', "
            f"tamanho_mb={self.tamanho_mb}, "
            f"status='{self.status}', "
            f"assinatura='{self.assinatura}')"
        )


class ListaEncadeada:
    """Lista simplesmente encadeada que modela o mapa de blocos da memória RAM."""

    def __init__(self):
        """Inicializa a lista encadeada vazia com ponteiro cabeça nulo."""
        self.cabeca = None

    @property
    def inicio(self):
        """Alias conveniente para o nó inicial (cabeça) da lista."""
        return self.cabeca

    def esta_vazia(self) -> bool:
        """Verifica se não há nenhum bloco alocado na lista."""
        return self.cabeca is None

    def inserir(
        self,
        endereco_hex,
        tamanho_mb: int = None,
        status: str = "LIVRE",
        assinatura: str = "",
    ) -> No:
        """Insere um novo bloco no final da lista encadeada.

        Aceita tanto uma instância já criada de `No` quanto os parâmetros
        individuais para construir o nó internamente.
        """
        if isinstance(endereco_hex, No):
            novo_no = endereco_hex
            novo_no.proximo = None
        else:
            if tamanho_mb is None:
                raise ValueError(
                    "O parâmetro 'tamanho_mb' é obrigatório ao criar um novo nó."
                )
            novo_no = No(endereco_hex, tamanho_mb, status, assinatura)

        if self.cabeca is None:
            self.cabeca = novo_no
            return novo_no

        # Percorre manualmente pelos ponteiros .proximo até encontrar o último nó
        atual = self.cabeca
        while atual.proximo is not None:
            atual = atual.proximo

        atual.proximo = novo_no
        return novo_no

    def remover_por_endereco(self, endereco_hex: str):
        """Remove o bloco correspondente ao endereço hexadecimal informado.

        Religa os ponteiros manualmente para preservar a continuidade da lista.
        Retorna o nó removido ou None caso o endereço não seja encontrado.
        """
        atual = self.cabeca
        anterior = None

        while atual is not None:
            if atual.endereco_hex == endereco_hex:
                if anterior is None:
                    # Remoção na cabeça: avança o início da lista
                    self.cabeca = atual.proximo
                else:
                    # Remoção no meio ou fim: o nó anterior aponta para o próximo
                    anterior.proximo = atual.proximo

                atual.proximo = None
                return atual

            anterior = atual
            atual = atual.proximo

        return None

    def remover(self, endereco_hex: str):
        """Alias para `remover_por_endereco`."""
        return self.remover_por_endereco(endereco_hex)

    def coalescencia(self) -> int:
        """Funde blocos 'LIVRE' adjacentes em um único bloco contíguo.

        Percorre os nós sequencialmente e, sempre que dois blocos consecutivos
        estiverem com status 'LIVRE', soma seus tamanhos no primeiro bloco e
        religa seu ponteiro `.proximo` para pular o segundo bloco.

        Retorna a quantidade de fusões realizadas.
        """
        fusoes = 0
        atual = self.cabeca

        while atual is not None and atual.proximo is not None:
            proximo_no = atual.proximo
            if atual.status == "LIVRE" and proximo_no.status == "LIVRE":
                atual.tamanho_mb += proximo_no.tamanho_mb
                if not atual.assinatura:
                    atual.assinatura = ""

                # Religa o ponteiro pulando o bloco fundido e desconecta a referência antiga
                atual.proximo = proximo_no.proximo
                proximo_no.proximo = None
                fusoes += 1
                # Não avança `atual` para que 3 ou mais blocos livres seguidos sejam fundidos
            else:
                atual = atual.proximo

        return fusoes

    def coalescer(self) -> int:
        """Alias para `coalescencia`."""
        return self.coalescencia()

    def tamanho(self) -> int:
        """Conta manualmente a quantidade de nós presentes na lista."""
        contador = 0
        atual = self.cabeca
        while atual is not None:
            contador += 1
            atual = atual.proximo
        return contador

    def para_lista(self) -> list:
        """Converte a lista encadeada em uma lista Python percorrendo os ponteiros."""
        resultado = []
        atual = self.cabeca
        while atual is not None:
            resultado.append(atual)
            atual = atual.proximo
        return resultado

    def __iter__(self):
        """Permite iterar manualmente sobre os nós via `.proximo`."""
        atual = self.cabeca
        while atual is not None:
            yield atual
            atual = atual.proximo


class Pilha:
    """Pilha (LIFO) estática que simula a Call Stack com capacidade fixa de 8 itens."""

    CAPACIDADE_MAXIMA = 8

    def __init__(self, capacidade_maxima: int = CAPACIDADE_MAXIMA):
        """Inicializa o vetor interno de tamanho fixo e o ponteiro do topo."""
        if capacidade_maxima <= 0:
            raise ValueError("A capacidade máxima da pilha deve ser positiva.")
        self._capacidade = capacidade_maxima
        self._itens = [None] * capacidade_maxima
        self._topo = -1

    def esta_cheia(self) -> bool:
        """Retorna True se a pilha atingiu sua capacidade máxima."""
        return (self._topo + 1) >= self._capacidade

    def esta_vazia(self) -> bool:
        """Retorna True se não houver nenhum elemento empilhado."""
        return self._topo == -1

    def tamanho(self) -> int:
        """Retorna a quantidade atual de elementos na pilha."""
        return self._topo + 1

    def push(self, item) -> bool:
        """Empilha um elemento no topo se houver espaço disponível.

        Retorna True em caso de sucesso ou False se ocorrer Stack Overflow (pilha cheia).
        """
        if self.esta_cheia():
            return False

        self._topo += 1
        self._itens[self._topo] = item
        return True

    def pop(self):
        """Remove e retorna o elemento do topo da pilha, ou None se estiver vazia."""
        if self.esta_vazia():
            return None

        item = self._itens[self._topo]
        self._itens[self._topo] = None
        self._topo -= 1
        return item

    def peek(self):
        """Consulta o elemento no topo da pilha sem removê-lo."""
        if self.esta_vazia():
            return None
        return self._itens[self._topo]

    def para_lista(self) -> list:
        """Retorna uma cópia dos itens empilhados da base até o topo."""
        resultado = []
        for i in range(self._topo + 1):
            resultado.append(self._itens[i])
        return resultado


class _NoFila:
    """Nó interno auxiliar utilizado para encadear elementos na Fila FIFO."""

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class Fila:
    """Fila (FIFO) implementada manualmente com ponteiros de frente e trás.

    Modela o escalonador de processos do sistema operacional, garantindo
    operações de enfileiramento e desenfileiramento em tempo O(1).
    """

    def __init__(self):
        """Inicializa uma fila vazia."""
        self._frente = None
        self._tras = None
        self._tamanho = 0

    def esta_vazia(self) -> bool:
        """Retorna True se a fila não possuir elementos."""
        return self._tamanho == 0

    def tamanho(self) -> int:
        """Retorna o número de elementos atualmente na fila."""
        return self._tamanho

    def enqueue(self, item) -> None:
        """Insere um novo processo no final da fila."""
        novo_no = _NoFila(item)
        if self.esta_vazia():
            self._frente = novo_no
            self._tras = novo_no
        else:
            self._tras.proximo = novo_no
            self._tras = novo_no
        self._tamanho += 1

    def dequeue(self):
        """Remove e retorna o processo da frente da fila, ou None se vazia."""
        if self.esta_vazia():
            return None

        no_removido = self._frente
        self._frente = no_removido.proximo
        if self._frente is None:
            self._tras = None

        no_removido.proximo = None
        self._tamanho -= 1
        return no_removido.dado

    def frente(self):
        """Retorna o processo no início da fila sem removê-lo."""
        if self.esta_vazia():
            return None
        return self._frente.dado

    def para_lista(self) -> list:
        """Retorna uma lista com os elementos da fila na ordem FIFO."""
        resultado = []
        atual = self._frente
        while atual is not None:
            resultado.append(atual.dado)
            atual = atual.proximo
        return resultado
