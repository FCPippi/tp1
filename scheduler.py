"""Simulador do escalonamento MLFQ."""

from cpu import CPU
from gantt import formatar_gantt
from metrics import metricas_gerais
from process import Estado, Processo
from queue_manager import QueueManager


class Scheduler:
    QUANTA = {0: 2, 1: 4}

    def __init__(self, processos, entrada=None, mostrar=True):
        self.processos = sorted(processos, key=lambda processo: (processo.chegada, processo.pid))
        self.filas = QueueManager()
        self.cpu = CPU(entrada)
        self.mostrar = mostrar
        self.tempo = 0
        self.executando = None
        self.historico = []

    def _admitir(self):
        for processo in self.processos:
            if processo.estado == Estado.NOVO and processo.chegada <= self.tempo:
                processo.estado = Estado.PRONTO
                self.filas.adicionar_fila0(processo)

    def _acordar(self):
        for processo in self.processos:
            if processo.estado == Estado.BLOQUEADO:
                if processo.bloqueado_ate <= self.tempo:
                    processo.estado = Estado.PRONTO
                    processo.bloqueado_ate = None
                    processo.quantum_usado = 0
                    self.filas.adicionar_fila0(processo)
                else:
                    processo.tempo_bloqueado += 1

    def _escolher(self):
        if self.filas.fila0:
            return self.filas.retirar_fila0()
        return self.filas.retirar_fila1()

    def _registrar(self, processo):
        item = {
            "tempo": self.tempo,
            "processo": processo.nome if processo else "IDLE",
            "estados": {p.nome: p.estado.value for p in self.processos},
            "fila0": [p.nome for p in self.filas.fila0],
            "fila1": self.filas.conteudo_fila1(),
            "bloqueados": [p.nome for p in self.processos if p.estado == Estado.BLOQUEADO],
        }
        self.historico.append(item)
        if self.mostrar:
            print(f"UT {self.tempo}: CPU={item['processo']} | estados={item['estados']} | "
                  f"F0={item['fila0']} | F1={item['fila1']} | bloqueados={item['bloqueados']}")

    def executar(self):
        while not all(processo.finalizado for processo in self.processos):
            self._admitir()
            self._acordar()
            if self.executando is not None and self.executando.estado != Estado.EXECUTANDO:
                self.executando = None

            if self.executando is not None and self.executando.fila == 1 and self.filas.fila0:
                self.executando.estado = Estado.PRONTO
                self.filas.adicionar_fila1(self.executando, frente=True)
                self.executando = None
            if self.executando is None:
                self.executando = self._escolher()
                if self.executando:
                    self.executando.estado = Estado.EXECUTANDO

            processo = self.executando
            if processo is None:
                self._registrar(None)
                self.tempo += 1
                continue

            resultado = self.cpu.executar_uma(processo, self.tempo)
            processo.quantum_usado += 1
            if resultado.bloqueou or resultado.finalizou:
                self.executando = None
            elif processo.quantum_usado >= self.QUANTA[processo.fila]:
                processo.estado = Estado.PRONTO
                if processo.fila == 0:
                    processo.quantum_usado = 0
                    self.filas.adicionar_fila1(processo)
                else:
                    processo.quantum_usado = 0
                    self.filas.adicionar_fila1(processo)
                self.executando = None
            self._registrar(processo)
            self.tempo += 1
        return self.resultado()

    def resultado(self):
        return {
            "tempo_final": self.tempo,
            "gantt": formatar_gantt(self.historico),
            "historico": self.historico,
            "metricas": metricas_gerais(self.processos),
        }