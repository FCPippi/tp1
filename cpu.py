"""CPU que executa exatamente uma instrucao por chamada."""

from dataclasses import dataclass

from process import Estado, Processo


@dataclass
class ResultadoExecucao:
    bloqueou: bool = False
    finalizou: bool = False
    syscall: int | None = None
    valor: int | None = None


class CPU:
    def __init__(self, entrada=None):
        self.entrada = entrada or (lambda processo: 0)

    @staticmethod
    def _valor(processo, operando):
        if operando.startswith("#"):
            return int(operando[1:])
        operando = operando.lower()
        if operando not in processo.memoria:
            raise RuntimeError(f"PID {processo.pid}: dado inexistente '{operando}'")
        return processo.memoria[operando]

    def executar_uma(self, processo, tempo):
        if processo.pc >= len(processo.instrucoes):
            processo.estado = Estado.FINALIZADO
            processo.tempo_termino = tempo
            return ResultadoExecucao(finalizou=True)

        instrucao = processo.instrucoes[processo.pc]
        processo.pc += 1
        processo.cpu_consumida += 1
        mnemonico, operando = instrucao.mnemonico, instrucao.operando
        if mnemonico == "LOAD":
            processo.acc = self._valor(processo, operando)
        elif mnemonico == "STORE":
            processo.memoria[operando.lower()] = processo.acc
        elif mnemonico == "ADD":
            processo.acc += self._valor(processo, operando)
        elif mnemonico == "SUB":
            processo.acc -= self._valor(processo, operando)
        elif mnemonico == "MULT":
            processo.acc *= self._valor(processo, operando)
        elif mnemonico == "DIV":
            divisor = self._valor(processo, operando)
            if divisor == 0:
                raise RuntimeError(f"PID {processo.pid}: divisao por zero")
            processo.acc //= divisor
        elif mnemonico == "BRANY":
            processo.pc = instrucao.indice_alvo
        elif mnemonico == "BRPOS" and processo.acc > 0:
            processo.pc = instrucao.indice_alvo
        elif mnemonico == "BRZERO" and processo.acc == 0:
            processo.pc = instrucao.indice_alvo
        elif mnemonico == "BRNEG" and processo.acc < 0:
            processo.pc = instrucao.indice_alvo
        elif mnemonico == "SYSCALL":
            codigo = int(operando)
            if codigo == 0:
                processo.estado = Estado.FINALIZADO
                processo.tempo_termino = tempo + 1
                return ResultadoExecucao(finalizou=True, syscall=codigo, valor=processo.acc)
            if codigo == 1:
                processo.saidas.append(processo.acc)
            elif codigo == 2:
                processo.acc = int(self.entrada(processo))
                processo.entradas.append(processo.acc)
            processo.estado = Estado.BLOQUEADO
            processo.bloqueado_ate = tempo + 4
            return ResultadoExecucao(bloqueou=True, syscall=codigo, valor=processo.acc)
        return ResultadoExecucao()