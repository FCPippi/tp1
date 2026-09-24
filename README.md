# Simulador MLFQ

Projeto acadêmico em Python que simula a execução de processos Assembly em um escalonador **Multilevel Feedback Queue**.

## Arquitetura

- `assembler.py`: lê `.asm`, valida as seções, resolve rótulos e produz instruções e memória inicial.
- `process.py`: representa o PCB, registradores, estado, prioridade, tempos e fila do processo.
- `cpu.py`: executa uma instrução por vez. Cada chamada equivale a uma UT.
- `queue_manager.py`: mantém a Fila 0 (FIFO) e a Fila 1 agrupada por prioridade.
- `scheduler.py`: aplica chegada, admissão, preempção, quanta, bloqueios e retorno de I/O.
- `metrics.py`: calcula turnaround, espera, CPU e bloqueio.
- `gantt.py`: formata o histórico da CPU.
- `main.py`: interface de execução e demonstração.
- `tests/`: testes automatizados do parser e da simulação.

O processo é um PCB orientado a objetos. As filas usam `deque`; os grupos da Fila 1 usam um dicionário de prioridade para manter ordenação por prioridade e FIFO dentro do empate. O histórico guarda, a cada UT, CPU, estados, filas e bloqueados.

## Regras implementadas

- Fila 0: Round Robin, quantum 2.
- Fila 1: Round Robin com prioridade estática, quantum 4.
- Novo processo e processo que retorna de I/O entram na Fila 0.
- Processo da Fila 1 é preemptado imediatamente quando existe processo na Fila 0.
- `SYSCALL 1` e `SYSCALL 2` bloqueiam por 3 UTs.
- `SYSCALL 1` imprime imediatamente no formato `[P1] Impressao (SYSCALL 1): valor`.
- `SYSCALL 2` solicita um inteiro pelo teclado quando executado.
- `SYSCALL 0` finaliza o processo.
- Nomes de dados e rótulos são tratados sem distinção entre maiúsculas e minúsculas.
- `STORE` aceita somente nomes de dados, nunca valores imediatos como `#7`.
- Erros de execução finalizam apenas o processo afetado e são registrados no log.
- O limite padrão é de 10000 UTs e pode ser alterado com `--max-uts`.
- Troca de contexto não consome UT.
- Turnaround = término - chegada.
- Espera = turnaround - CPU consumida - tempo bloqueado.

## Execução

No PowerShell, a partir desta pasta:

```powershell
python main.py
```

Isso executa automaticamente `programs/teste1.asm` e `programs/teste2.asm`, imprime o estado a cada UT, o Gantt e as métricas.

Para executar um arquivo isolado:

```powershell
python main.py --programa programs/teste1.asm
```

Para usar cadastro em JSON:

```json
[
  {"nome": "P1", "arrivalTime": 0, "prioridade": 3, "arquivo": "programs/teste1.asm"}
]
```

Salve o conteúdo, por exemplo, em `processos.json` e execute:

```powershell
python main.py --config processos.json
```

Para evitar que um programa com laço infinito prolongue a apresentação:

```powershell
python main.py --max-uts 500
```

## Validação

```powershell
python test_analisador.py
python -m py_compile analisador.py assembler.py process.py cpu.py queue_manager.py metrics.py scheduler.py gantt.py main.py
```

Se `pytest` estiver instalado:

```powershell
python -m pytest -q
```

## Demonstração

1. Apresente a estrutura modular e o formato das seções `.code` e `.data`.
2. Execute `python main.py`.
3. Mostre uma chegada na Fila 0, a promoção para a Fila 1 após o quantum e a preempção causada por uma nova chegada.
4. Destaque os logs de `SYSCALL 1` e `SYSCALL 0`.
5. Demonstre um programa com `SYSCALL 2` e informe um valor no teclado.
6. Explique o Gantt e confira as métricas individuais e médias.
7. Mostre os testes, a validação de `STORE #7` e o limite de UTs.

## Melhorias futuras

- Interface gráfica ou visualização animada do Gantt.
- Política configurável de entrada do `SYSCALL 2`.
- Exportação das métricas para CSV.
- Mais diretivas Assembly e testes de propriedades do escalonador.
- Persistência de cenários e comparação entre políticas de escalonamento.
