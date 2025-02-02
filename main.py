#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import Lexico
from sintatico import Sintatico

class Tradutor:

    def __init__(self, nomeArq):
        self.nomeArq = nomeArq

    def inicializa(self):
        self.arq = open(self.nomeArq, "r")
        self.lexico = Lexico(self.arq)
        self.sintatico = Sintatico(self.lexico)

    def traduz(self):
        self.sintatico.traduz()

    def finaliza(self):
        self.arq.close()

# inicia a traducao
if __name__ == '__main__':
    # for i in range(10):
    #     x = Tradutor(f"tests/program_test{i}.txt")
    #     x.inicializa()
    #     x.traduz()
    #     #x.sintatico.testaLexico()
    #     x.finaliza()
    
    x = Tradutor("./bolha.txt")
    x.inicializa()
    x.traduz()
    #x.sintatico.testaLexico()
    x.finaliza()

