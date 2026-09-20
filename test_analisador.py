import os

from analisador import analisar_programa, ErroDeMontagem

PASTA_PROGRAMAS = os.path.join(os.path.dirname(__file__), "programs")


def teste_teste1():
    instrucoes, dados = analisar_programa(os.path.join(PASTA_PROGRAMAS, "teste1.asm"))
    assert dados["valor"] == 10
    assert instrucoes[0].mnemonico == "LOAD"
    assert instrucoes[1].mnemonico == "ADD"
    assert instrucoes[1].operando == "#5"
    print("teste1.asm: OK")


def teste_teste2():
    instrucoes, dados = analisar_programa(os.path.join(PASTA_PROGRAMAS, "teste2.asm"))
    assert dados["limite"] == 3
    assert dados["temp"] == 0
    mnemonicos = [i.mnemonico for i in instrucoes]
    assert "BRPOS" in mnemonicos
    assert "SYSCALL" in mnemonicos
    print("teste2.asm: OK")


def teste_rotulo_que_nao_existe():
    caminho = os.path.join(os.path.dirname(__file__), "programa_ruim.asm")
    with open(caminho, "w") as f:
        f.write(".code\nBRANY fim\n.endcode\n.data\n.enddata\n")

    deu_erro = False
    try:
        analisar_programa(caminho)
    except ErroDeMontagem:
        deu_erro = True

    os.remove(caminho)
    assert deu_erro
    print("rotulo inexistente: OK")


if __name__ == "__main__":
    teste_teste1()
    teste_teste2()
    teste_rotulo_que_nao_existe()
    print("\ntodos os testes passaram")
