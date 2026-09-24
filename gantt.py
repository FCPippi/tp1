"""Formatacao do historico temporal da CPU."""


def formatar_gantt(historico):
    if not historico:
        return "(sem execucao)"
    return " ".join(f"{item['tempo']}:{item['processo']}" for item in historico)


def tabela_gantt(historico):
    return [(item["tempo"], item["processo"]) for item in historico]