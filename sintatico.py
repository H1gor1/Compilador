
from lexico import TOKEN, Lexico
from semantico import Semantico

class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.nomeAlvo = 'alvo.out'
        self.semantico = Semantico(self.nomeAlvo)

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        self.prog()
        print('Traduzido com sucesso.')


    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            print(f'Erro na linha {linha}, coluna {coluna}:')
            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'Era esperado {msgTokenAtual} mas veio {msg}')
            raise Exception

    def consomeOpRel(self, *tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if token in tokenAtual:
            op = self.tokenLido[0]
            self.tokenLido = self.lexico.getToken()
            return op
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            print(f'Erro na linha {linha}, coluna {coluna}:')
            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'Era esperado {msgTokenAtual} mas veio {msg}')
            raise Exception

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof :
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

#-------- segue a gramatica -----------------------------------------
    def prog(self):
        # <prog> -> <funcao> <RestoFuncoes>
        self.semantico.gera(0, '# Código gerado pelo compilador\n')
        self.semantico.gera(0, 'class Programa:\n')
        self.semantico.gera(1, 'def __init__(self):\n')
        self.semantico.gera(2, 'pass\n\n')
        self.funcao(1)
        self.restoFuncoes(1)

        self.semantico.gera(0, '\nif __name__ == "__main__":\n')
        self.semantico.gera(1, 'programa = Programa()\n')
        self.semantico.gera(1, 'programa.main()\n')

    def funcao(self, indent_level):
        self.consome(TOKEN.FUNCTION)
        salvaIdent = self.tokenLido
        self.consome(TOKEN.ident)
        self.consome(TOKEN.abrePar)
        argumentos = self.params()
        self.consome(TOKEN.fechaPar)
        resultado = self.tipoResultado()
        tipos = argumentos + [resultado]
        self.semantico.declara(salvaIdent, (TOKEN.FUNCTION, tipos))

        nome_funcao = salvaIdent[1]
        if argumentos != []:
            parametros = ', '.join([arg[0][1] for arg in argumentos])
            self.semantico.gera(indent_level, f'\ndef {nome_funcao}(self, {parametros}):\n') 
        else:
            self.semantico.gera(indent_level, f'\ndef {nome_funcao}(self):\n') 
        
        self.semantico.iniciaFuncao(resultado)

        for p in argumentos:
            (tt, (tipo, info)) = p
            self.semantico.declara(tt, (tipo, info))

        self.corpo(indent_level +1)
        self.semantico.terminaFuncao()

    def restoFuncoes(self, indent_level):
        #<RestoFuncoes> -> <funcao> <RestoFuncoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao(indent_level)
            self.restoFuncoes(indent_level)

    def params(self):
        #<params> -> <tipo> ident <restoParams> | LAMBDA
        if self.tokenLido[0] in [TOKEN.TSTRING, TOKEN.TFLOAT, TOKEN.TINT]:
            tipo = self.tipo()
            salvaIdent = self.tokenLido
            self.consome(TOKEN.ident)
            tipoParam = (salvaIdent, tipo)
            resto = self.restoParams()
            tiposArgs = [tipoParam] + resto
            return tiposArgs
        else:
            return []

    def restoParams(self):
        # <restoParams> -> LAMBDA | , <tipo> ident <restoParams>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipo = self.tipo()
            salvaIdent = self.tokenLido
            self.consome(TOKEN.ident)
            tipoParam = (salvaIdent, tipo)
            resto = self.restoParams()
            tiposArgs = [tipoParam] + resto
            return tiposArgs
        else:
            return []

    def tipoResultado(self):
        # <tipoResultado> -> LAMBDA | -> <tipo>
        if self.tokenLido[0] == TOKEN.returnCharacter:
            self.consome(TOKEN.returnCharacter)
            tipo = self.tipo()
        else:
            tipo = None
        return tipo

    def tipo(self):
        # <tipo> -> string <opcLista> | int <opcLista> | float <opcLista> 
        if self.tokenLido[0] == TOKEN.TSTRING:
            self.consome(TOKEN.TSTRING)
            is_lista = self.opcLista()
            return (TOKEN.TSTRING, is_lista)
        elif self.tokenLido[0] == TOKEN.TINT:
            self.consome(TOKEN.TINT)
            is_lista = self.opcLista()
            return (TOKEN.TINT, is_lista)
        elif self.tokenLido[0] == TOKEN.TFLOAT:
            self.consome(TOKEN.TFLOAT)
            is_lista = self.opcLista()
            return (TOKEN.TFLOAT, is_lista)
        elif self.tokenLido[0] == TOKEN.TBOOLEAN:
            self.consome(TOKEN.TBOOLEAN)
            is_lista = self.opcLista()
            return (TOKEN.TBOOLEAN, is_lista)
        else:
            # Erro: tipo não esperado
            linha, coluna = self.tokenLido[2], self.tokenLido[3]
            raise Exception(f"Erro na linha {linha}, coluna {coluna}: tipo esperado mas não encontrado.")

    def opcLista(self):
        # <opcLista> -> [ list ] | LAMBDA
        if self.tokenLido[0] != TOKEN.BEGIN and self.tokenLido[0] != TOKEN.ident:
            self.consome(TOKEN.abreCol)
            self.consome(TOKEN.LIST)
            self.consome(TOKEN.fechaCol)
            return True
        return False

    def corpo(self, indent_level):
        # <corpo> -> begin <declaracoes> <calculo> end
        self.consome(TOKEN.BEGIN)
        self.declaracoes(indent_level)
        self.calculo(indent_level)
        self.consome(TOKEN.END)

    def declaracoes(self, indent_level):
        # <declaracoes> -> <declara> <declaracoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.TSTRING or self.tokenLido[0] == TOKEN.TINT or self.tokenLido[0] == TOKEN.TFLOAT or self.tokenLido[0] == TOKEN.TBOOLEAN:
            self.declara(indent_level)
            self.declaracoes(indent_level)

    def declara(self, indent_level):
        # <declara> -> <tipo> <idents> ;
        tipo = self.tipo()
        idents = self.idents()
        self.consome(TOKEN.ptoVirg)

        for ident in idents:
            self.semantico.declara(ident, tipo)

            nome_variavel = ident[1]
            if tipo[0] == TOKEN.TINT:
                self.semantico.gera(indent_level, f'{nome_variavel} = 0  # Declarado como inteiro \n')
            elif tipo[0] == TOKEN.TFLOAT:
                self.semantico.gera(indent_level, f'{nome_variavel} = 0.0  # Declarado como float \n')
            elif tipo[0] == TOKEN.TSTRING:
                self.semantico.gera(indent_level, f'{nome_variavel} = ""  # Declarado como string \n')
            elif tipo[0] == TOKEN.TBOOLEAN:
                self.semantico.gera(indent_level, f'{nome_variavel} = False  # Declarado como booleano \n')
            elif tipo[1]:
                self.semantico.gera(indent_level, f'{nome_variavel} = []  # Declarado como lista\n')

    def idents(self):
        # <idents> -> ident <restoIdents> 
        idents = [self.tokenLido]
        self.consome(TOKEN.ident)
        idents += self.restoIdents()
        return idents

    def restoIdents(self):
        # <restoIdents> -> , ident <restoIdents> | LAMBDA
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            idents = [self.tokenLido]
            self.consome(TOKEN.ident)
            return idents+self.restoIdents()
        return []

    def calculo(self, indent_level):
        # <calculo> -> LAMBDA | <com> <calculo>
        while self.tokenLido[0] != TOKEN.fechaChave and self.tokenLido[0] != TOKEN.END:
            self.com(indent_level)

    def com(self, indent_level):
        # <com> -> <atrib> | <if> | <leitura> | <escrita> | <bloco> | <for> | <while> | <retorna>
        if self.tokenLido[0] == TOKEN.ident:
            salvaIdent = self.tokenLido
            result = self.semantico.consulta(salvaIdent)
            if result is None:
                msg = f'Variavel {self.tokenLido[1]} nao declarada'
                self.semantico.erroSemantico(salvaIdent, "Identificador não declarado.")
            else:
                (tipo, info) = result
                if (tipo == TOKEN.FUNCTION):
                    self.call()
                    self.consome(TOKEN.ptoVirg)
                else:
                    self.atrib(indent_level)
        elif self.tokenLido[0] == TOKEN.IF:
            self.se(indent_level)
        elif self.tokenLido[0] == TOKEN.READ:
            self.leitura(indent_level)
        elif self.tokenLido[0] == TOKEN.WRITE:
            self.impressao(indent_level)
        elif self.tokenLido[0] == TOKEN.abreChave:
            self.bloco(indent_level)
        elif self.tokenLido[0] == TOKEN.FOR:
            self.repeticao(indent_level)
        elif self.tokenLido[0] == TOKEN.WHILE:
            self.condicional(indent_level)
        elif self.tokenLido[0] == TOKEN.RET:
            self.retorna(indent_level)

    def retorna(self, indent_level):
        lexema = self.tokenLido  # Salva o token do comando return
        self.consome(TOKEN.RET)

        e1 = None  # Inicialização da variável e1 para evitar UnboundLocalError

        while self.tokenLido[0] != TOKEN.ptoVirg:
            if self.tokenLido[0] == TOKEN.abreCol:
                self.consome(TOKEN.abreCol)
                e1 = self.expOpc()

                if e1:
                    e1 = [(e1[0][0], True), e1[1]]
                    retornoFunction = self.semantico.returnoFuncaoAtual
                    if e1[0] != retornoFunction:
                        self.semantico.erroSemantico(
                            lexema, "Expression doesn't match with the function return type."
                        )
                self.consome(TOKEN.fechaCol)

            else:
                e1 = self.expOpc()
                if e1:
                    retornoFunction = self.semantico.returnoFuncaoAtual
                    if e1[0] != retornoFunction:
                        self.semantico.erroSemantico(
                            lexema, "Expression doesn't match with the function return type."
                        )

        if e1:
            self.semantico.gera(indent_level, f'return {e1[1]}\n')
        else:
            self.semantico.gera(indent_level, 'return\n')
        self.consome(TOKEN.ptoVirg)

    def expOpc(self):
        # <expOpc> -> LAMBDA | <exp>
        if self.tokenLido[0] != TOKEN.ptoVirg:
            return self.exp()

    def condicional(self, indent_level):
        # <while> -> while ( <exp> ) <com>
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.abrePar)
        e1 = self.exp()

        if e1[0] != (TOKEN.TBOOLEAN, False):
            self.semantico.erroSemantico(self.tokenLido, "A expressão deve ser um boolean")
        self.consome(TOKEN.fechaPar)

        # Gera o código para o while
        self.semantico.gera(2, f'while {e1[1]}:\n')

        self.com(indent_level + 1)

    def repeticao(self, indent_level):
        # <for> -> for ident in <range> do <com>
        self.consome(TOKEN.FOR)
        salvaIdent = self.tokenLido
        self.consome(TOKEN.ident)
        res = self.semantico.consulta(salvaIdent)
        if res is None:
            self.semantico.declara(salvaIdent, (TOKEN.TINT, False))
        self.consome(TOKEN.IN)
        range_info = self.range()
        self.consome(TOKEN.DO)

        nome_var = salvaIdent[1]
        self.semantico.gera(indent_level, f'for {nome_var} in {range_info[1]}:\n')
        self.com(indent_level + 1)

    def range(self):
        if self.tokenLido[0] == TOKEN.RANGE:
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.abrePar)
            start = self.exp()[1]
            self.consome(TOKEN.virg)
            end = self.exp()[1]
            step_code = ""
            if self.tokenLido[0] == TOKEN.virg:
                self.consome(TOKEN.virg)
                step = self.exp()[1]
                step_code = f", {step}"
            self.consome(TOKEN.fechaPar)
            return [None, f"range({start}, {end}{step_code})"]
        else:
            return self.lista()

    def opcRange(self):
        # <opcRange> -> , <exp> | LAMBDA
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            return self.exp()

    def lista(self):
        # <lista> -> ident <opcIndice> | [ <elemLista> ]
        if self.tokenLido[0] == TOKEN.ident:
            e1 = self.tokenLido
            self.consome(TOKEN.ident)
            return self.opcIndice(token=e1)
        else:
            self.consome(TOKEN.abreCol)
            res = self.elemLista()
            self.consome(TOKEN.fechaCol)
            if res:
                resNovo = [(res[0][0], True), res[1]]
                return resNovo
            return res

    def opcIndice(self, token):
        e1 = token
        result = self.semantico.consulta(e1)
        if self.tokenLido[0] == TOKEN.abreCol:
            self.consome(TOKEN.abreCol)  # Consome o colchete aberto
            e2 = self.exp()  # Processa o índice/expressão

            if self.tokenLido[0] == TOKEN.doisPts:  # Tratamento para slices (dois pontos)
                self.consome(TOKEN.doisPts)
                e3 = self.exp()  # Segundo índice do slice (opcional)

                # Garantia de índices inteiros
                if e2[0] == (TOKEN.TINT, False) and e3[0] == (TOKEN.TINT, False):
                    result = [(TOKEN.TINT, True), f"{e1[1]}[{e2[1]}:{e3[1]}]"]
                else:
                    self.semantico.erroSemantico(e1, "Índices devem ser inteiros.")
            else:
                # Acessando um único índice
                if e2[0] == (TOKEN.TINT, False):
                    if result and result[1]:  # Atualiza tipo de listas
                        result = [(result[0], False), f"{e1[1]}[{e2[1]}]"]
                else:
                    self.semantico.erroSemantico(e2, "O índice deve ser um número inteiro.")

            self.consome(TOKEN.fechaCol)  # Consome o colchete fechado
            return result  # Retorna com o formato correto

        # Retorno padrão se não há colchetes
        if result:
            return [result, e1[1]]
        else:
            self.semantico.erroSemantico(e1, "Variável não declarada ou inválida.")

    def elemLista(self):
        # <elemLista> -> LAMBDA | <elem> <restoElemLista>
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.floatVal, TOKEN.strVal, TOKEN.ident]:
            # Processa o primeiro elemento
            elem = self.exp()
            # Processa o restante da lista
            resto = self.restoElemLista()
            return elem + resto
        else:
            return []

    def restoElemLista(self):
        # <restoElemLista> -> LAMBDA | , <elem> <restoElemLista>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            # Processa o próximo elemento
            elem = self.elem()
            # Processa o restante da lista
            resto = self.restoElemLista()
            return elem + resto
        else:
            return []

    def elem(self):
        # <elem> -> intVal | floatVal | strVal | ident 
        if self.tokenLido[0] == TOKEN.intVal:
            valor = self.tokenLido[1]
            self.consome(TOKEN.intVal)
            return [(TOKEN.TINT, False), valor]
        elif self.tokenLido[0] == TOKEN.floatVal:
            valor = self.tokenLido[1]
            self.consome(TOKEN.floatVal)
            return [(TOKEN.TFLOAT, False), valor]
        elif self.tokenLido[0] == TOKEN.strVal:
            valor = self.tokenLido[1]
            self.consome(TOKEN.strVal)
            return [(TOKEN.TSTRING, False), valor]
        elif self.tokenLido[0] == TOKEN.ident:
            salvaIdent = self.tokenLido
            self.consome(TOKEN.ident)
            result = self.semantico.consulta(salvaIdent)
            if result is not None:
                return [result, salvaIdent[1]]
            else:
                self.semantico.erroSemantico(salvaIdent, "Identificador não declarado.")

    def atrib(self, indent_level):
        # <atrib> -> ident <opcIndice> = <exp> ;
        if self.tokenLido[0] == TOKEN.ident:
            salvaIdent = self.tokenLido
            self.consome(TOKEN.ident)

            is_lista = self.opcIndice(salvaIdent)

            self.consome(TOKEN.atrib)
            tipo_expressao = self.exp()
            
            nome_variavel = salvaIdent[1]
            
            if tipo_expressao == []:
                if is_lista[1]:
                    self.semantico.gera(indent_level, f'{is_lista[1]} = []\n')
                else:
                    self.semantico.gera(indent_level, f'{nome_variavel} = []\n')
            else:
                if is_lista[1]:
                    self.semantico.gera(indent_level, f'{is_lista[1]} = {tipo_expressao[1]}\n')
                else:
                    self.semantico.gera(indent_level, f'{nome_variavel} = {tipo_expressao[1]}\n')

            self.consome(TOKEN.ptoVirg)



    def se(self, indent_level):
        # <if> -> if ( <exp> ) then <com> <else_opc>
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        e1 = self.exp()
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.THEN)

        # Gera o código para o if
        self.semantico.gera(indent_level, f'if {e1[1]}:\n')
        self.com(indent_level +1)
        self.elseopc(indent_level)

    def elseopc(self, indent_level):
        # <else_opc> -> LAMBDA | else <com> 
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.semantico.gera(indent_level, f"else: \n")
            self.com(indent_level + 1)
        else:
            pass

    def leitura(self, indent_level):
        # <leitura> -> read ( <exp> , ident ) ;
        self.consome(TOKEN.READ)
        self.consome(TOKEN.abrePar)
        tipo_exp = self.exp()  # Aceita uma expressão
        if tipo_exp[0] != (TOKEN.TSTRING, False):
            self.semantico.erroSemantico(self.tokenLido, "O prompt deve ser uma string.")
        self.consome(TOKEN.virg)
        salva_ident = self.tokenLido
        self.consome(TOKEN.ident)
        # Verifica se a variável existe
        if self.semantico.consulta(salva_ident) is None:
            self.semantico.erroSemantico(salva_ident, "Variável não declarada.")


        # Gera o código para a leitura
        nome_variavel = salva_ident[1]
        self.semantico.gera(indent_level, f'{nome_variavel} = input()\n')

        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)

    def impressao(self, indent_level):
        self.consome(TOKEN.WRITE)
        self.consome(TOKEN.abrePar)
        codigos = self.listaOut()
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)

        args = ', '.join(codigos) if codigos else ''
        self.semantico.gera(indent_level, f'print({args})\n')


    def listaOut(self):
        primeiro = self.out() or ""  # Garante string vazia se None
        restante = self.restoListaOut()
        return [primeiro] + restante

    def restoListaOut(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            proximo = self.out() or ""  # Garante string vazia
            outros = self.restoListaOut()
            return [proximo] + outros
        else:
            return []

    def out(self):
        resultado_exp = self.exp()  # Obtém (tipo, código)
        return resultado_exp[1] if resultado_exp else ""

    def bloco(self, indent_level):
        # <bloco> -> { <calculo> }
        self.consome(TOKEN.abreChave)
        self.calculo(indent_level)
        self.consome(TOKEN.fechaChave)

    def exp(self):
        # <exp> -> <disj>
        return self.disj()

    def disj(self):
        # <disj> -> <conj> <restoDisj>
        e1 = self.conj()
        return self.restoDisj(e1)

    def restoDisj(self, e1):
        # <restoDisj> -> LAMBDA | || <conj> <restoDisj>
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            e2 = self.conj()
            res = self.semantico.verificaOperacao(e1, TOKEN.OR, e2)  # Operação lógica OR
            return self.restoDisj([res, f"{e1[1]} or {e2[1]}"])
        else:
            return e1

    def conj(self):
        # <conj> -> <nao> <restoConj>
        e1 = self.nao()
        return self.restoConj(e1)

    def restoConj(self, e1):
        # <restoConj> -> LAMBDA | && <rel> <restoConj>
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            e2 = self.rel()
            res = self.semantico.verificaOperacao(e1, TOKEN.AND, e2)  # Operação lógica AND
            return self.restoConj([res, f"{e1[1]} and {e2[1]}"])
        else:
            return e1

    def nao(self):
        # <nao> -> not <nao> | <rel>
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            e1 = self.nao()
            return self.semantico.verificaOperacao(e1, TOKEN.NOT)
        else:
            return self.rel()

    def rel(self):
        # <rel> -> <soma> <restoRel>
        e1 = self.soma()
        return self.restoRel(e1)

    def restoRel(self, e1):
        op_map = {
            TOKEN.igual: "==",
            TOKEN.diferente: "!=",
            TOKEN.menorIgual: "<=",
            TOKEN.menor: "<",
            TOKEN.maior: ">",
            TOKEN.maiorIgual: ">="
        }

        if self.tokenLido[0] in op_map:
            op_token = self.tokenLido[0]
            op_str = op_map[op_token]
            self.consome(op_token)
            e2 = self.soma()
            res = self.semantico.verificaOperacao(e1, op_token, e2)
            return [res, f"{e1[1]} {op_str} {e2[1]}"]
        else:
            return e1

    def soma(self):
        # <soma> -> <mult> <restoSoma>
        e1 = self.mult()
        return self.restoSoma(e1)

    def restoSoma(self, e1):
        # <restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            e2 = self.mult()
            res = self.semantico.verificaOperacao(e1, TOKEN.mais, e2)  # Soma
            return self.restoSoma([res, f"{e1[1]} + {e2[1]}"])
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            e2 = self.mult()
            res = self.semantico.verificaOperacao(e1, TOKEN.menos, e2)  # Subtração
            return self.restoSoma([res, f"{e1[1]} - {e2[1]}"])
        else:
            return e1

    def mult(self):
        # <mult> -> <uno> <restoMult>
        e1 = self.uno()
        return self.restoMult(e1)

    def restoMult(self, e1):
        # <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> <restoMult>
        if self.tokenLido[0] == TOKEN.divide:
            self.consome(TOKEN.divide)
            e2 = self.uno()
            res = self.semantico.verificaOperacao(e1, TOKEN.divide, e2)
            return self.restoMult([res, f"{e1[1]} / {e2[1]}"])  # Propaga o novo tipo sem valor
        elif self.tokenLido[0] == TOKEN.multiplica:
            self.consome(TOKEN.multiplica)
            e2 = self.uno()
            res = self.semantico.verificaOperacao(e1, TOKEN.multiplica, e2)
            return self.restoMult([res, f"{e1[1]} * {e2[1]}"])
        elif self.tokenLido[0] == TOKEN.mod:
            self.consome(TOKEN.mod)
            e2 = self.uno()
            res = self.semantico.verificaOperacao(e1, TOKEN.mod, e2)
            return self.restoMult([res, f"{e1[1]} % {e2[1]}"])
        else:
            return e1  # Retorna e1 diretamente se não há mais operações

    def uno(self):
        # <uno> -> + <uno> | - <uno> | <folha>
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            e1 = self.uno()
            return [self.semantico.verificaOperacao(e1, TOKEN.mais), f"+{e1[1]}"]  # Ajusta para o formato [tipo, valor]
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            e1 = self.uno()
            return [self.semantico.verificaOperacao(e1, TOKEN.menos), f"-{e1[1]}"]  # Ajusta para o formato [tipo, valor]
        else:
            return self.folha()

    def folha(self):
        if self.tokenLido[0] == TOKEN.intVal:
            valor = self.tokenLido[1]
            self.consome(TOKEN.intVal)
            return [(TOKEN.TINT, False), valor]
        elif self.tokenLido[0] == TOKEN.floatVal:
            valor = self.tokenLido[1]
            self.consome(TOKEN.floatVal)
            return [(TOKEN.TFLOAT, False), valor]
        elif self.tokenLido[0] == TOKEN.strVal:
            valor = self.tokenLido[1]
            self.consome(TOKEN.strVal)
            return [(TOKEN.TSTRING, False), valor]
        elif self.tokenLido[0] == TOKEN.ident:
            salvaIdent = self.tokenLido
            result = self.semantico.consulta(salvaIdent)
            if result is None:
                msg = f'Variável {self.tokenLido[1]} não declarada.'
                self.semantico.erroSemantico(salvaIdent, msg)
            else:
                (tipo, info) = result
                if tipo == TOKEN.FUNCTION:
                    res = self.call()  # Função retorna algo
                    return res
                else:
                    res = self.lista()  # Tratar como lista
                    return res  # Garantido ter o formato correto
        elif self.tokenLido[0] == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            res = self.exp()
            self.consome(TOKEN.fechaPar)
            return res  # Já retorna no formato correto
        elif self.tokenLido[0] == TOKEN.abreCol:
            res = self.lista()
            return res
        elif self.tokenLido[0] == TOKEN.FALSE:
            self.consome(TOKEN.FALSE)
            return [(TOKEN.TBOOLEAN, False), False]
        elif self.tokenLido[0] == TOKEN.TRUE:
            self.consome(TOKEN.TRUE)
            return [(TOKEN.TBOOLEAN, False), True]

    def call(self):
        salvaIdent = self.tokenLido
        self.consome(TOKEN.ident)
        result = self.semantico.consulta(salvaIdent)
        self.consome(TOKEN.abrePar)
        params = self.listaOutsOpc()
        self.consome(TOKEN.fechaPar)
        
        # Corrigindo a geração do nome da função e parâmetros
        nome_funcao = salvaIdent[1]  # Pega apenas o lexema do identificador
        args = ', '.join(params) if params else ''
        code = f"{nome_funcao}({args})"

        if nome_funcao == "len":
            code = f"len({args})"
        
        return [result[1][-1], code] if result else [None, code]

    def listaOutsOpc(self):
        # <lista_outs_opc> -> <lista_outs> | LAMBDA
        if self.tokenLido[0] != TOKEN.fechaPar:
            params = self.listaOut()
            return params
        else:
            return []
    
        
if __name__ == '__main__':
    print("Para testar, chame o Tradutor")