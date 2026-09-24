"""Interpretador/assembler da linguagem Assembly hipotetica."""

from dataclasses import dataclass


class ErroDeMontagem(Exception):
    """Erro de sintaxe ou semantica no programa Assembly."""


MNEMONICOS_VALIDOS = {
    "LOAD", "STORE", "ADD", "SUB", "MULT", "DIV",
    "BRANY", "BRPOS", "BRZERO", "BRNEG", "SYSCALL",
}
DESVIOS = {"BRANY", "BRPOS", "BRZERO", "BRNEG"}
OPERACOES_COM_DADO = {"LOAD", "STORE", "ADD", "SUB", "MULT", "DIV"}


@dataclass(frozen=True)
class Instrucao:
    mnemonico: str
    operando: str | None = None
    indice_alvo: int | None = None

    def eh_imediato(self):
        return isinstance(self.operando, str) and self.operando.startswith("#")


@dataclass(frozen=True)
class Programa:
    instrucoes: list
    dados: dict


def _imediato_valido(token):
    return token.startswith("#") and token[1:].lstrip("-").isdigit()


def _tokens_sem_comentario(linha):
    tokens = []
    for token in linha.split():
        if token.startswith("#") and not _imediato_valido(token):
            break
        tokens.append(token)
    return tokens


def _normalizar_nome(nome):
    return nome.lower()


class Assembler:
    def assemble(self, caminho):
        instrucoes, rotulos, dados = [], {}, {}
        secao = None
        with open(caminho, "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
        for lineno, linha in enumerate(linhas, 1):
            tokens = _tokens_sem_comentario(linha)
            if not tokens:
                continue
            diretiva = tokens[0].lower()
            if diretiva in (".code", ".data"):
                if secao is not None:
                    raise ErroDeMontagem(f"linha {lineno}: secao anterior nao encerrada")
                secao = diretiva[1:]
                continue
            if diretiva in (".endcode", ".enddata"):
                if secao != diretiva[4:]:
                    raise ErroDeMontagem(f"linha {lineno}: encerramento de secao invalido")
                secao = None
                continue
            if secao == "code":
                self._codigo(tokens, lineno, instrucoes, rotulos)
            elif secao == "data":
                self._dado(tokens, lineno, dados)
            else:
                raise ErroDeMontagem(f"linha {lineno}: comando fora de uma secao")
        if secao is not None:
            raise ErroDeMontagem("fim de arquivo dentro de uma secao")
        resolvidas = []
        for indice, instrucao in enumerate(instrucoes):
            if instrucao.mnemonico in DESVIOS:
                rotulo = _normalizar_nome(instrucao.operando)
                if rotulo not in rotulos:
                    raise ErroDeMontagem(f"instrucao {indice}: rotulo nao definido")
                resolvidas.append(Instrucao(instrucao.mnemonico, rotulo, rotulos[rotulo]))
            elif instrucao.mnemonico in OPERACOES_COM_DADO and not instrucao.eh_imediato():
                nome = _normalizar_nome(instrucao.operando)
                if instrucao.mnemonico == "STORE" and instrucao.eh_imediato():
                    raise ErroDeMontagem(f"instrucao {indice}: STORE exige nome de dado")
                if nome not in dados:
                    raise ErroDeMontagem(f"instrucao {indice}: dado nao declarado '{instrucao.operando}'")
                resolvidas.append(Instrucao(instrucao.mnemonico, nome))
            elif instrucao.mnemonico == "SYSCALL" and instrucao.operando not in ("0", "1", "2"):
                raise ErroDeMontagem(f"instrucao {indice}: SYSCALL invalido")
            else:
                resolvidas.append(instrucao)
        return Programa(resolvidas, dados)

    def _codigo(self, tokens, lineno, instrucoes, rotulos):
        if tokens[0].endswith(":"):
            rotulo = tokens.pop(0)[:-1]
            rotulo = _normalizar_nome(rotulo)
            if not rotulo or rotulo in rotulos:
                raise ErroDeMontagem(f"linha {lineno}: rotulo invalido ou duplicado")
            rotulos[rotulo] = len(instrucoes)
            if not tokens:
                return
        mnemonico = tokens[0].upper()
        if mnemonico not in MNEMONICOS_VALIDOS:
            raise ErroDeMontagem(f"linha {lineno}: mnemonico desconhecido '{mnemonico}'")
        if len(tokens) > 2:
            raise ErroDeMontagem(f"linha {lineno}: operandos extras")
        operando = tokens[1] if len(tokens) == 2 else None
        if operando is None:
            raise ErroDeMontagem(f"linha {lineno}: operando ausente")
        if mnemonico == "STORE" and operando.startswith("#"):
            raise ErroDeMontagem(f"linha {lineno}: STORE exige nome de dado")
        instrucoes.append(Instrucao(mnemonico, operando))

    def _dado(self, tokens, lineno, dados):
        if len(tokens) != 2:
            raise ErroDeMontagem(f"linha {lineno}: declaracao de dado invalida")
        nome, valor = tokens
        nome = _normalizar_nome(nome)
        if nome in dados:
            raise ErroDeMontagem(f"linha {lineno}: dado duplicado '{nome}'")
        try:
            dados[nome] = int(valor)
        except ValueError as exc:
            raise ErroDeMontagem(f"linha {lineno}: valor de dado invalido") from exc