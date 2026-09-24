import os

import pytest

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


def test_nomes_de_dados_sao_case_insensitive(tmp_path):
    arquivo = tmp_path / "capitalizacao.asm"
    arquivo.write_text(
        ".code\nLOAD variable\nADD #2\nSTORE VARIABLE\nSYSCALL 1\nSYSCALL 0\n"
        ".endcode\n.data\nVariable 5\n.enddata\n",
        encoding="utf-8",
    )
    processos = carregar_processos([{
        "nome": "P1", "arrivalTime": 0, "prioridade": 3, "arquivo": str(arquivo)
    }])
    Scheduler(processos, mostrar=False).executar()
    assert processos[0].saidas == [7]
    assert processos[0].memoria["variable"] == 7


def test_store_imediato_e_rejeitado(tmp_path):
    arquivo = tmp_path / "store_imediato.asm"
    arquivo.write_text(".code\nSTORE #7\n.endcode\n.data\n.enddata\n", encoding="utf-8")
    with pytest.raises(ErroDeMontagem):
        Assembler().assemble(arquivo)


def test_syscall_2_recebe_entrada(tmp_path):
    arquivo = tmp_path / "entrada.asm"
    arquivo.write_text(
        ".code\nSYSCALL 2\nSYSCALL 1\nSYSCALL 0\n.endcode\n.data\n.enddata\n",
        encoding="utf-8",
    )
    processos = carregar_processos([{
        "nome": "P1", "arrivalTime": 0, "prioridade": 3, "arquivo": str(arquivo)
    }])
    resultado = Scheduler(processos, entrada=lambda _: 42, mostrar=False).executar()
    assert processos[0].entradas == [42]
    assert processos[0].saidas == [42]
    assert resultado["tempo_final"] > 0


def test_limite_interrompe_loop_infinito(tmp_path):
    arquivo = tmp_path / "loop.asm"
    arquivo.write_text(".code\nL: BRANY L\n.endcode\n.data\n.enddata\n", encoding="utf-8")
    processos = carregar_processos([{
        "nome": "LOOP", "arrivalTime": 0, "prioridade": 1, "arquivo": str(arquivo)
    }])
    Scheduler(processos, mostrar=False, max_uts=5).executar()
    assert processos[0].finalizado
    assert "limite" in processos[0].erro