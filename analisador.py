"""Compatibilidade com a API original do trabalho."""

from assembler import Assembler, ErroDeMontagem, Instrucao


def analisar_programa(caminho):
    programa = Assembler().assemble(caminho)
    return programa.instrucoes, programa.dados


__all__ = ["analisar_programa", "ErroDeMontagem", "Instrucao"]
