# Analisador da linguagem assembly hipotetica (le o .asm e monta a lista de instrucoes + dados)
#
# .code
# [rotulo:] MNEMONICO [operando]   # comentario
# .endcode
# .data
# nome valor
# .enddata

MNEMONICOS_ARITMETICOS = ["ADD", "SUB", "MULT", "DIV"]
MNEMONICOS_DE_DESVIO = ["BRANY", "BRPOS", "BRZERO", "BRNEG"]
MNEMONICOS_VALIDOS = MNEMONICOS_ARITMETICOS + MNEMONICOS_DE_DESVIO + ["LOAD", "STORE", "SYSCALL"]


class ErroDeMontagem(Exception):
    pass


class Instrucao:
    def __init__(self, mnemonico, operando=None):
        self.mnemonico = mnemonico
        self.operando = operando
        self.indice_alvo = None  # preenchido depois para BRANY/BRPOS/BRZERO/BRNEG

    def eh_imediato(self):
        return isinstance(self.operando, str) and self.operando.startswith("#")


def _eh_imediato_valido(token):
    # imediato e algo como '#5' ou '#-3': '#' seguido de numero
    if not token.startswith("#"):
        return False
    numero = token[1:].lstrip("-")
    return numero.isdigit()


def _remover_comentario(tokens):
    # um '#' que nao e um imediato valido marca o inicio do comentario
    tokens_uteis = []
    for token in tokens:
        if token.startswith("#") and not _eh_imediato_valido(token):
            break
        tokens_uteis.append(token)
    return tokens_uteis


def _processar_linha_de_codigo(tokens, lineno, instrucoes, rotulos):
    if tokens[0].endswith(":"):
        rotulos[tokens[0][:-1]] = len(instrucoes)
        tokens = tokens[1:]
        if not tokens:
            return

    mnemonico = tokens[0].upper()
    if mnemonico not in MNEMONICOS_VALIDOS:
        raise ErroDeMontagem(f"linha {lineno}: mnemonico desconhecido '{mnemonico}'")

    operando = tokens[1] if len(tokens) > 1 else None
    instrucoes.append(Instrucao(mnemonico, operando))


def _processar_linha_de_dados(tokens, lineno, dados):
    if len(tokens) < 2:
        raise ErroDeMontagem(f"linha {lineno}: declaracao de dado invalida")
    nome, valor = tokens[0], tokens[1]
    dados[nome] = int(valor)


def _resolver_rotulos(instrucoes, rotulos):
    for idx, instrucao in enumerate(instrucoes):
        if instrucao.mnemonico in MNEMONICOS_DE_DESVIO:
            if instrucao.operando not in rotulos:
                raise ErroDeMontagem(f"instrucao {idx}: rotulo '{instrucao.operando}' nao definido")
            instrucao.indice_alvo = rotulos[instrucao.operando]
        elif instrucao.mnemonico == "SYSCALL":
            if instrucao.operando not in ("0", "1", "2"):
                raise ErroDeMontagem(f"instrucao {idx}: SYSCALL invalido '{instrucao.operando}'")


def analisar_programa(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()

    secao_atual = None
    instrucoes = []
    rotulos = {}
    dados = {}

    for lineno, linha in enumerate(linhas, start=1):
        tokens = _remover_comentario(linha.split())
        if not tokens:
            continue

        if tokens[0] == ".code":
            secao_atual = "code"
        elif tokens[0] == ".endcode":
            secao_atual = None
        elif tokens[0] == ".data":
            secao_atual = "data"
        elif tokens[0] == ".enddata":
            secao_atual = None
        elif secao_atual == "code":
            _processar_linha_de_codigo(tokens, lineno, instrucoes, rotulos)
        elif secao_atual == "data":
            _processar_linha_de_dados(tokens, lineno, dados)

    _resolver_rotulos(instrucoes, rotulos)
    return instrucoes, dados
