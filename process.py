"""PCB e estados de um processo da simulacao."""

from dataclasses import dataclass, field
from enum import Enum


class Estado(str, Enum):
    NOVO = "Novo"
    PRONTO = "Pronto"
    EXECUTANDO = "Executando"
    BLOQUEADO = "Bloqueado"
    FINALIZADO = "Finalizado"


@dataclass
class Processo:
    pid: int
    nome: str
    chegada: int
    prioridade: int
    instrucoes: list
    memoria: dict
    estado: Estado = Estado.NOVO
    pc: int = 0
    acc: int = 0
    fila: int = 0
    quantum_usado: int = 0
    tempo_termino: int | None = None
    cpu_consumida: int = 0
    tempo_bloqueado: int = 0
    bloqueado_ate: int | None = None
    saidas: list = field(default_factory=list)
    entradas: list = field(default_factory=list)

    @property
    def finalizado(self):
        return self.estado == Estado.FINALIZADO