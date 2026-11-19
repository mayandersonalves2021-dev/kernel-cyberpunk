# KERNEL CYBERPUNK: Contrabando de Memória

**Protocolo de Defesa e Sobrevivência de Kernel v1.0**

Projeto acadêmico de Estrutura de Dados desenvolvido em Python puro, com separação em camadas entre estruturas/algoritmos (`core/`), motor de regras (`engine/`), interface visual em terminal (`ui/`) e suítes de testes (`tests/`).

Todas as estruturas de dados e algoritmos de ordenação e busca foram implementados **100% manualmente**, sem uso de `list.sort()`, `sorted()`, `bisect` ou bibliotecas externas de estruturas de dados.

---

## Arquitetura do Projeto

```text
kernel_guardian/
├── core/
│   ├── __init__.py
│   ├── estruturas.py    # No, ListaEncadeada (com coalescencia), Pilha (8 slots) e Fila FIFO
│   └── algoritmos.py    # Selection, Insertion, Merge, Quick Sort + Buscas Sequencial e Binária
├── engine/
│   ├── __init__.py
│   └── jogo.py          # Classe MotorJogo: regras, rodadas, atos, eventos surpresa e benchmark
├── ui/
│   ├── __init__.py
│   └── interface.py     # Classe InterfaceCyberpunk usando Rich (painéis, animações e tabelas)
├── tests/
│   ├── test_core.py     # Testes unitários das estruturas e algoritmos do núcleo
│   └── test_engine.py   # Simulação automatizada de 10 rodadas e cenários de derrota
├── main.py              # Ponto de entrada interativo do jogo
├── requirements.txt     # Dependência de interface (rich)
├── .gitignore
└── README.md
```

---

## Estruturas de Dados e Complexidades Assintóticas

### Estruturas de Dados (`core/estruturas.py`)

| Estrutura | Classe | Modelagem no Jogo | Operações e Complexidade |
| :--- | :--- | :--- | :--- |
| Lista Simplesmente Encadeada | `No`, `ListaEncadeada` | Mapa de blocos da memória RAM (`1024 MB`, status `LIVRE`, `SISTEMA`, `MALWARE`) | Inserção no fim $O(n)$, remoção por endereço $O(n)$ e `coalescencia()` $O(n)$ (funde blocos `LIVRE` adjacentes religando ponteiros `.proximo`) |
| Pilha Estática (LIFO) | `Pilha` | Call Stack com capacidade fixa de `8` frames | `push`, `pop`, `peek`, `esta_cheia`, `esta_vazia`, `tamanho` em $O(1)$ |
| Fila Encadeada (FIFO) | `Fila` | Escalonador de processos de entrada | `enqueue`, `dequeue`, `frente`, `esta_vazia`, `tamanho` em $O(1)$ via ponteiros `_frente` e `_tras` |

### Algoritmos (`core/algoritmos.py`)

| Algoritmo | Tipo | Complexidade (Melhor / Médio / Pior) | Aplicação no Jogo |
| :--- | :--- | :--- | :--- |
| `selection_sort` | Ordenação | $O(n^2)$ / $O(n^2)$ / $O(n^2)$ | Desfragmentação de disco (+38°C na CPU) |
| `insertion_sort` | Ordenação | $O(n)$ / $O(n^2)$ / $O(n^2)$ | Desfragmentação de disco (+32°C / +36°C com $\ge 5.000$ setores) |
| `merge_sort` | Ordenação | $O(n \log n)$ / $O(n \log n)$ / $O(n \log n)$ | Desfragmentação de disco (+6°C na CPU) |
| `quick_sort` | Ordenação | $O(n \log n)$ / $O(n \log n)$ / $O(n^2)$ | Desfragmentação de disco (+8°C na CPU) |
| `busca_sequencial` | Busca | $O(1)$ / $O(n)$ / $O(n)$ | Varredura de blocos `MALWARE` na `ListaEncadeada` da RAM |
| `busca_binaria` | Busca | $O(1)$ / $O(\log n)$ / $O(\log n)$ | Consulta iterativa na blacklist ordenada de `10.000` IPs |

---

## Mecânica da Partida

- **Objetivo**: Sobreviver a **10 rodadas** (2 ações defensivas por rodada) distribuídas em **3 Atos** e **2 Eventos Surpresa**:
  - **Ato 1 (Rodadas 1–3 — O Reconhecimento)**: Ataques leves e `200` setores fragmentados.
  - **Evento Surpresa 1 (Rodada 4 — *Injeção de Pacotes Fantasmas*)**: Injeta 4 processos maliciosos na fila e planta um bloco `MALWARE` (`0xDEAD`) na RAM.
  - **Ato 2 (Rodadas 4–7 — A Escalada)**: Pressão simultânea na fila e Call Stack com `1.500` setores no disco.
  - **Evento Surpresa 2 (Rodada 8 — *Sobrecarga Térmica + Embaralhamento Total*)**: Eleva a CPU para `65°C` e embaralha `5.000` setores (armadilha térmica onde algoritmos $O(n^2)$ ultrapassam `100°C`).
  - **Ato 3 (Rodadas 8–10 — O Ataque Final)**: Pressão máxima na Call Stack, na RAM e no disco até o encerramento da 10ª rodada.
- **Ações no Terminal**:
  - `[1]` Escanear próximo processo da Fila (`busca_binaria` na blacklist)
  - `[2]` Varrer e limpar `MALWARE` na RAM (`busca_sequencial` + `coalescencia()`)
  - `[3]` Desempilhar Call Stack (`pop()`)
  - `[4]` Desfragmentar setores do disco (comparativo térmico e métricas reais)
  - `[5]` Inspecionar Mapa de Ponteiros da RAM (gratuito — não consome ação)
- **Condições de Derrota (*Kernel Panic*)**: **Stack Overflow** (Call Stack > 8), **Superaquecimento da CPU** ($\ge 100^\circ\text{C}$) ou **Colapso de Memória** (sem bloco `LIVRE` suficiente na RAM).

---

## Instalação e Execução

1. Instale a dependência visual (`rich`):
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o jogo:
   ```bash
   python main.py
   ```
   *(Opcional: utilize `python main.py --sem-abertura` para iniciar direto na Rodada 1.)*

3. Execute os testes unitários e de integração:
   ```bash
   python tests/test_core.py
   python tests/test_engine.py
   ```
