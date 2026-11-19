# KERNEL CYBERPUNK: Contrabando de Memória

Projeto acadêmico e prático de Estrutura de Dados desenvolvido 100% em Python puro.

O projeto simula aspectos de baixo nível de um sistema operacional (gerenciamento de memória RAM, escalonamento de processos e pilha de execução) e implementa estruturas e algoritmos fundamentais de ordenação e busca sem o uso de bibliotecas prontas.

## Estrutura do Núcleo (Core)

- **Blocos de Memória RAM**: `No` e `ListaEncadeada` com inserção, remoção por endereço e algoritmo de coalescência de blocos livres contíguos.
- **Call Stack**: `Pilha` com capacidade fixa de 8 itens.
- **Escalonador FIFO**: `Fila` de processos com operações em $O(1)$.
- **Algoritmos de Ordenação**: `selection_sort`, `insertion_sort`, `merge_sort` e `quick_sort` manuais com contagem de trocas, comparações e tempo de execução.
- **Algoritmos de Busca**: `busca_sequencial` em lista encadeada e `busca_binaria` iterativa.
