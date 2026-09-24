"""Calculo das metricas da simulacao."""


def metricas_processo(processo):
    termino = processo.tempo_termino
    turnaround = None if termino is None else termino - processo.chegada
    espera = None if turnaround is None else turnaround - processo.cpu_consumida - processo.tempo_bloqueado
    return {
        "pid": processo.pid,
        "nome": processo.nome,
        "chegada": processo.chegada,
        "termino": termino,
        "turnaround": turnaround,
        "cpu": processo.cpu_consumida,
        "bloqueio": processo.tempo_bloqueado,
        "espera": espera,
    }


def metricas_gerais(processos):
    dados = [metricas_processo(processo) for processo in processos]
    concluidos = [item for item in dados if item["termino"] is not None]
    quantidade = len(concluidos)
    return {
        "processos": dados,
        "media_espera": sum(item["espera"] for item in concluidos) / quantidade if quantidade else 0,
        "media_turnaround": sum(item["turnaround"] for item in concluidos) / quantidade if quantidade else 0,
    }