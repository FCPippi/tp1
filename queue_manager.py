"""Estruturas das filas 0 e 1 do MLFQ."""

from collections import deque


class QueueManager:
    def __init__(self):
        self.fila0 = deque()
        self.grupos_fila1 = {}

    def adicionar_fila0(self, processo):
        processo.fila = 0
        self.fila0.append(processo)

    def adicionar_fila1(self, processo, frente=False):
        processo.fila = 1
        grupo = self.grupos_fila1.setdefault(processo.prioridade, deque())
        if frente:
            grupo.appendleft(processo)
        else:
            grupo.append(processo)

    def retirar_fila0(self):
        return self.fila0.popleft() if self.fila0 else None

    def retirar_fila1(self):
        for prioridade in sorted(self.grupos_fila1, reverse=True):
            if self.grupos_fila1[prioridade]:
                processo = self.grupos_fila1[prioridade].popleft()
                return processo
        return None

    def fila1_vazia(self):
        return not any(self.grupos_fila1.values())

    def conteudo_fila1(self):
        return [processo.nome for prioridade in sorted(self.grupos_fila1, reverse=True)
                for processo in self.grupos_fila1[prioridade]]

    def remover(self, processo):
        try:
            self.fila0.remove(processo)
        except ValueError:
            for grupo in self.grupos_fila1.values():
                try:
                    grupo.remove(processo)
                    return
                except ValueError:
                    continue

    def vazia(self):
        return not self.fila0 and self.fila1_vazia()