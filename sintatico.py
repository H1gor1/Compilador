
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

        self.funcao()
        self.restoFuncoes()
    
    def funcao(self):
        # <funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
        self.consome(TOKEN.FUNCTION)
        salvaIdent = self.tokenLido
        self.consome(TOKEN.ident)
        self.consome(TOKEN.abrePar)
        argumentos = self.params()
        self.consome(TOKEN.fechaPar)
        resultado = self.tipoResultado()
        tipos = argumentos + [resultado]
        self.semantico.declara(salvaIdent, (TOKEN.FUNCTION, tipos))
        self.semantico.iniciaFuncao(resultado)
        for p in argumentos:
            (tt, (tipo,info)) = p
            self.semantico.declara(tt, (tipo,info))
        self.corpo()
        self.semantico.terminaFuncao()

    def restoFuncoes(self):
        #<RestoFuncoes> -> <funcao> <RestoFuncoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao()
            self.restoFuncoes()
    
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

    def corpo(self):
        # <corpo> -> begin <declaracoes> <calculo> end
        self.consome(TOKEN.BEGIN)
        self.declaracoes()
        self.calculo()
        self.consome(TOKEN.END)

    def declaracoes(self):
        # <declaracoes> -> <declara> <declaracoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.TSTRING or self.tokenLido[0] == TOKEN.TINT or self.tokenLido[0] == TOKEN.TFLOAT:
            self.declara()
            self.declaracoes()
    
    def declara(self):
        # <declara> -> <tipo> <idents> ;
        tipo = self.tipo()
        idents = self.idents()
        self.consome(TOKEN.ptoVirg)
        
        for ident in idents:
            self.semantico.declara(ident, tipo)
    
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
        
    def calculo(self):
        # <calculo> -> LAMBDA | <com> <calculo>
        while self.tokenLido[0] != TOKEN.fechaChave and self.tokenLido[0] != TOKEN.END:
            self.com()
    
    def com(self):
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
                    self.atrib()
        elif self.tokenLido[0] == TOKEN.IF:
            self.se()
        elif self.tokenLido[0] == TOKEN.READ:
            self.leitura()
        elif self.tokenLido[0] == TOKEN.WRITE:
            self.impressao()
        elif self.tokenLido[0] == TOKEN.abreChave:
            self.bloco()
        elif self.tokenLido[0] == TOKEN.FOR:
            self.repeticao()
        elif self.tokenLido[0] == TOKEN.WHILE:
            self.condicional()
        elif self.tokenLido[0] == TOKEN.RET:
            self.retorna()
    
    def retorna(self):
        # <retorna> -> return <expOpc> ;
        lexema = self.tokenLido
        self.consome(TOKEN.RET)
        e1 = self.expOpc()
        if e1:
            retornoFunction = self.semantico.returnoFuncaoAtual
            if e1 != retornoFunction:
                self.semantico.erroSemantico(lexema, "Expression dont match with the function return")
        self.consome(TOKEN.ptoVirg)
    
    def expOpc(self):
        # <expOpc> -> LAMBDA | <exp>
        if self.tokenLido[0] != TOKEN.ptoVirg:
            return self.exp()
    
    def condicional(self):
        # <while> -> while ( <exp> ) <com>
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.abrePar)
        e1 = self.exp()

        if e1 != (TOKEN.TBOOLEAN, False):
            self.semantico.erroSemantico(self.tokenLido, "A expressão deve ser um boolean")
        self.consome(TOKEN.fechaPar)
        self.com()
    
    def repeticao(self):
        # <for> -> for ident in <range> do <com>
        self.consome(TOKEN.FOR)
        self.consome(TOKEN.ident)
        self.consome(TOKEN.IN)
        self.range()
        self.consome(TOKEN.DO)
        self.com()

    def range(self):
        # <range> -> <lista> | range ( <exp> , <exp> <opcRange> )
        if self.tokenLido[0] == TOKEN.ident:
            self.lista()
        elif self.tokenLido[0] == TOKEN.RANGE:
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.abrePar)
            e1 = self.exp()

            if e1 != (TOKEN.TINT, False):
                self.semantico.erroSemantico(self.tokenLido, "A expressão deve ser um inteiro")
            self.consome(TOKEN.virg)
            e2 = self.exp()

            if e2 != (TOKEN.TINT, False):
                self.semantico.erroSemantico(self.tokenLido, "A expressão deve ser um inteiro")
            self.opcRange()
            self.consome(TOKEN.fechaPar)
    
    def opcRange(self):
        # <opcRange> -> , <exp> | LAMBDA
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.exp()
    
    def lista(self):
        # <lista> -> ident <opcIndice> | [ <elemLista> ]
        if self.tokenLido[0] == TOKEN.ident:
            e1 = self.tokenLido
            self.consome(TOKEN.ident)
            return self.opcIndice(token=e1)
        else:
            self.consome(TOKEN.abreCol)
            self.elemLista()
            self.consome(TOKEN.fechaCol)
    
    def opcIndice(self, token):
        e1 = token
        result = self.semantico.consulta(e1)
        # <opcIndice> -> LAMBDA | [ <exp> <restoElem> ]
        if self.tokenLido[0] == TOKEN.abreCol:
            self.consome(TOKEN.abreCol)
            e2 = self.exp()

            if self.tokenLido[0] == TOKEN.doisPts:
                self.consome(TOKEN.doisPts)
                e3 = self.exp()
                if e2 == (TOKEN.TINT, False) and e3 == (TOKEN.TINT, False):
                    result = (TOKEN.TINT, True)
                else:
                    self.semantico.erroSemantico(e1, "Indices devem ser inteiros.")
            else:
                if e2 == (TOKEN.TINT, False):
                    result = (TOKEN.TINT, False)
                else:
                    self.semantico.erroSemantico(e1, "Indice deve ser inteiro.")

            self.consome(TOKEN.fechaCol)
            return result
        else:
            return result
    
    def elemLista(self):
        # <elemLista> -> LAMBDA | <elem> <restoElemLista>
        if self.tokenLido[0] == TOKEN.intVal or self.tokenLido[0] == TOKEN.floatVal or self.tokenLido[0] == TOKEN.strVal or self.tokenLido[0] == TOKEN.ident:
            self.elem()
            self.restoElemLista()
        pass

    def restoElemLista(self):
        # <restoElemLista> -> LAMBDA | , <elem> <restoElemLista>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.elem()
            self.restoElemLista()
    
    def elem(self):
        # <elem> -> intVal | floatVal | strVal | ident 
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
            return (TOKEN.TFLOAT, False)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
        elif self.tokenLido[0] == TOKEN.ident:
            self.consome(TOKEN.ident)
    
    def atrib(self):
        # <atrib> -> ident <opcIndice> = <exp> ;
        if self.tokenLido[0] == TOKEN.ident:
            salvaIdent = self.tokenLido
            self.consome(TOKEN.ident)
            
            is_lista = self.opcIndice(salvaIdent)

            self.consome(TOKEN.atrib)
            tipo_expressao = self.exp()

            self.consome(TOKEN.ptoVirg)
    


    def se(self):
        # <if> -> if ( <exp> ) then <com> <else_opc>
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        self.exp()
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.THEN)
        self.com()
        self.elseopc()
    
    def elseopc(self):
        # <else_opc> -> LAMBDA | else <com> 
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.com()
        else:
            pass
    
    def leitura(self):
        # <leitura> -> read ( strVal , ident ) ;
        self.consome(TOKEN.READ)
        self.consome(TOKEN.abrePar)
        self.consome(TOKEN.strVal)
        self.consome(TOKEN.virg)
        self.consome(TOKEN.ident)
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)
    
    def impressao(self):
        # <escrita> -> write ( <lista_out> ) ;
        self.consome(TOKEN.WRITE)
        self.consome(TOKEN.abrePar)
        self.listaOut()
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)
    
    def listaOut(self):
        # <lista_outs> -> <out> <restoLista_outs>
        self.out()
        self.restoListaOut()

    def restoListaOut(self):
        # <restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.out()
            self.restoListaOut()
        else:
            pass
    
    def out(self):
        # <out> -> <folha>
        self.folha()
    
    def bloco(self):
        # <bloco> -> { <calculo> }
        self.consome(TOKEN.abreChave)
        self.calculo()
        self.consome(TOKEN.fechaChave)

    def exp(self):
        # <exp> -> <disj>
        return self.disj()
    
    def disj(self):
        # <disj> -> <conj> <restoDisj>
        e1 = self.conj()
        return self.restoDisj(e1)

    def restoDisj(self, e1):
        # <restoDisj> -> LAMBDA | or <conj> <restoDisj>
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            e2 = self.conj()
            res = self.semantico.verificaOperacao(e1, TOKEN.OR, e2)
            return self.restoDisj(res)
        else:
            return e1
    
    def conj(self):
        # <conj> -> <nao> <restoConj>
        e1 = self.nao()
        return self.restoConj(e1)
    
    def restoConj(self, e1):
        # <restoConj> -> LAMBDA | and <nao> <restoConj>
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            e2 = self.nao()
            res = self.semantico.verificaOperacao(e1, TOKEN.AND, e2)
            return self.restoConj(res)
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
        # <restoRel> -> LAMBDA | oprel <soma>
        if self.tokenLido[0] in {TOKEN.igual, TOKEN.diferente, TOKEN.menor, TOKEN.menorIgual, TOKEN.maior, TOKEN.maiorIgual}:
            op = self.consomeOpRel(TOKEN.igual, TOKEN.diferente, TOKEN.menor, TOKEN.menorIgual, TOKEN.maior, TOKEN.maiorIgual)
            e2 = self.soma()
            return self.semantico.verificaOperacao(e1, op, e2)
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
            res = self.semantico.verificaOperacao(e1, TOKEN.mais, e2)
            return self.restoSoma(res)
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            e2 = self.mult()
            res = self.semantico.verificaOperacao(e1, TOKEN.menos, e2)
            return self.restoSoma(res)
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
            return self.restoMult(res)
        elif self.tokenLido[0] == TOKEN.multiplica:
            self.consome(TOKEN.multiplica)
            e2 = self.uno()
            res = self.semantico.verificaOperacao(e1, TOKEN.multiplica, e2)
            return self.restoMult(res)
        elif self.tokenLido[0] == TOKEN.mod:
            self.consome(TOKEN.mod)
            e2 = self.uno()
            res = self.semantico.verificaOperacao(e1, TOKEN.mod, e2)
            return self.restoMult(res)
        else:
            return e1
    
    def uno(self):
        # <uno> -> + <uno> | - <uno> | <folha>
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            e1 = self.uno()
            return(self.semantico.verificaOperacao(e1, TOKEN.mais))
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            e1 = self.uno()
            return(self.semantico.verificaOperacao(e1, TOKEN.menos))
        else:
            return self.folha()
        
    def folha(self):
        # <folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> ) 
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
            return (TOKEN.TINT, False)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
            return (TOKEN.TFLOAT, False)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
            return (TOKEN.TSTRING, False)
        elif self.tokenLido[0] == TOKEN.ident:
            if self.tokenLido[0] == TOKEN.ident:
                salvaIdent = self.tokenLido
                result = self.semantico.consulta(salvaIdent)
                if result is None:
                    msg = f'Variavel {self.tokenLido[1]} nao declarada'
                    self.semantico.erroSemantico(salvaIdent, "Identificador não declarado.")
                else:
                    (tipo, info) = result
                    if (tipo == TOKEN.FUNCTION):
                        return self.call()
                    else:
                        res = self.lista()
                        return res
                    
        elif self.tokenLido[0] == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.fechaPar)
        elif self.tokenLido[0] == TOKEN.abreCol:
            self.lista()

    def call(self):
        # <call> -> ident ( <lista_outs> )
        # if self.tokenLido[1] == 'lista':
        #     self.consome(TOKEN.ident)
        #     return

        salvaIdent = self.tokenLido
        self.consome(TOKEN.ident)
        result = self.semantico.consulta(salvaIdent)
        self.consome(TOKEN.abrePar)
        self.listaOutsOpc()
        self.consome(TOKEN.fechaPar)
        return result[1][-1]

    def listaOutsOpc(self):
        # <lista_outs_opc> -> <lista_outs> | LAMBDA
        if self.tokenLido[0] != TOKEN.fechaPar:
            self.listaOut()
        else:
            pass
    
        
if __name__ == '__main__':
    print("Para testar, chame o Tradutor")