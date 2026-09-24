import os

from assembler import Assembler, ErroDeMontagem
from main import carregar_processos
from scheduler import Scheduler


BASE = os.path.dirname(os.path.dirname(__file__))


def configuracao(nome, chegada, prioridade, arquivo):
    return {"nome": nome, "arrivalTime": chegada, "prioridade": prioridade,
            "arquivo": os.path.join(BASE, "programs", arquivo)}


def test_casos_do_enunciado_terminam():
    processos = carregar_processos([
        configuracao("P1", 0, 3, "teste1.asm"),
        configuracao("P2", 1, 5, "teste2.asm"),
    ])
    resultado = Scheduler(processos, entrada=lambda _: 7, mostrar=False).executar()
    assert all(processo.finalizado for processo in processos)
    assert processos[0].saidas == [15]
    assert resultado["tempo_final"] > 0
    assert resultado["metricas"]["media_turnaround"] > 0


def test_assembler_rejeita_instrucao_sem_operando(tmp_path):
    arquivo = tmp_path / "ruim.asm"
    arquivo.write_text(".code\nLOAD\n.endcode\n.data\n.enddata\n", encoding="utf-8")
    try:
        Assembler().assemble(arquivo)
    except ErroDeMontagem:
        pass
    else:
        raise AssertionError("programa invalido aceito")