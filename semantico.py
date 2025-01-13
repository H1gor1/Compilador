from ttoken import TOKEN

class SemanticoErro(Exception):
    pass

class Semantico:

    def __init__(self, nomeAlvo):
        self.tabelaSimbolos = [dict()]

        self.returnoFuncaoAtual = None

        # Tabela de operações usando apenas tokens para o operador
        self.tabelaOperacoes = {
            frozenset({(TOKEN.TINT, False), TOKEN.mais, (TOKEN.TINT, False)}): (TOKEN.TINT, False),
            frozenset({(TOKEN.TFLOAT, False), TOKEN.mais, (TOKEN.TFLOAT, False)}): (TOKEN.TFLOAT, False),
            frozenset({(TOKEN.TINT, False), TOKEN.multiplica, (TOKEN.TINT, False)}): (TOKEN.TINT, False),
            frozenset({(TOKEN.TFLOAT, False), TOKEN.multiplica, (TOKEN.TFLOAT, False)}): (TOKEN.TFLOAT, False),

            # Operações unárias
            frozenset({TOKEN.menos, (TOKEN.TINT, False)}): (TOKEN.TINT, False),
            frozenset({TOKEN.NOT, (TOKEN.TBOOLEAN, False)}): (TOKEN.TBOOLEAN, False),
        }
        self.alvo = open(nomeAlvo, "wt")
        self.declara((TOKEN.ident, 'len', 0, 0),
                     (TOKEN.FUNCTION, [(None, True), (TOKEN.TINT, False)]))
        self.declara((TOKEN.ident, 'num2str', 0, 0),
                     (TOKEN.FUNCTION, [(TOKEN.TFLOAT, False), (TOKEN.TSTRING, False)]))
        self.declara((TOKEN.ident, 'str2num', 0, 0),
                     (TOKEN.FUNCTION, [(TOKEN.TSTRING, False), (TOKEN.TFLOAT, False)]))
        self.declara((TOKEN.ident, 'trunc', 0, 0),
                     (TOKEN.FUNCTION, [(TOKEN.TFLOAT, False), (TOKEN.TINT, False)]))

    def finaliza(self):
        self.alvo.close()

    def erroSemantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}: {msg}')
        raise SemanticoErro(msg)

    def gera(self, nivel, codigo):
        identacao = ' ' * 3 * nivel
        linha = identacao + codigo + '\n'
        self.alvo.write(linha)

    def declara(self, tokenAtual, tipo):
        """ nome = lexema do ident
            tipo = (base, lista)
            base = int | float | strig | function | None # listas genericas
            Se base in [int,float,string]
                lista = boolean # True se o tipo for lista
            else
                Lista = lista com os tipos dos argumentos, mais tipo do retorno
        """
        (token, nome, linha, coluna) = tokenAtual
        if not self.consulta(tokenAtual) is None:
            msg = f'Variavel {nome} redeclarada'
            self.erroSemantico(tokenAtual, msg)
        else:
            escopo = self.tabelaSimbolos[0]
            escopo[nome] = tipo

    def consulta(self, tokenAtual):
        (token, nome, linha, coluna) = tokenAtual
        for escopo in self.tabelaSimbolos:
            if nome in escopo:
                return escopo[nome]
        return None

    def iniciaFuncao(self, tipo):
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos
        self.returnoFuncaoAtual = tipo

    def terminaFuncao(self):
        self.tabelaSimbolos = self.tabelaSimbolos[1:]
        self.returnoFuncaoAtual = None

    def verificaOperacao(self, e1, op, e2=None):
        if e2 is None:
            # Operação unária
            entrada = frozenset({op, e1})
        else:
            # Operação binária
            entrada = frozenset({e1, op, e2})
        
        if entrada in self.tabelaOperacoes:
            return self.tabelaOperacoes[entrada]
        else:
            msg = f"Operação inválida: {e1} {op} {e2}" if e2 else f"Operação inválida: {op} {e1}"
            raise SemanticoErro(msg)
    

