#---------------------------------------------------
# Tradutor para a linguagem B-A-BA
#
# versao final (jan-2025)
#---------------------------------------------------
from lexico import Lexico
from sintatico import Sintatico
import glob

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
    for file_path in glob.glob("tests/*.txt"):
        x = Tradutor(file_path)
        x.inicializa()
        x.traduz()
        # x.sintatico.testaLexico()
        x.finaliza()
    
    # x = Tradutor("./tests/find_sublist_with_sum.txt")
    # x.inicializa()
    # x.traduz()
    # #x.sintatico.testaLexico()
    # x.finaliza()

