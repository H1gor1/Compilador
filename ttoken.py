from enum import IntEnum
class TOKEN(IntEnum):
    erro = 1
    eof = 2
    ident = 3
    num = 4
    string = 5
    IF = 6
    ELSE = 7
    WHILE = 8
    BEGIN = 9
    END = 10
    abrePar = 11
    fechaPar = 12
    virg = 13
    ptoVirg = 14
    igual = 15
    diferente = 16 
    menor = 17
    menorIgual = 18
    maior = 19
    maiorIgual = 20
    AND = 21
    OR = 22
    NOT = 23
    mais = 24
    menos = 25
    multiplica = 26 
    divide = 27
    READ = 28
    WRITE = 29
    abreChave = 30
    fechaChave = 31
    atrib = 32
    THEN = 33

    
    FUNCTION = 34
    TSTRING = 35
    TINT = 36
    TFLOAT = 37
    abreCol = 38
    fechaCol = 39
    LIST = 40
    FOR = 41
    IN = 42
    DO = 43
    RANGE = 44
    intVal = 45
    floatVal = 46
    strVal = 47
    LEN = 48
    doisPts = 49
    returnCharacter = 50
    RET = 51
    mod = 52
    TBOOLEAN = 53
    TRUE = 54
    FALSE = 55


    @classmethod
    def msg(cls, token):
        nomes = {
            1:'erro',
            2:'<eof>',
            3:'ident',
            4:'numero',
            5:'string',
            6:'if',
            7:'else',
            8:'while',
            9:'begin',
            10:'end',
            11:'(',
            12:')',
            13:',',
            14:';',
            15: '==',
            16: '!=',
            17: '<',
            18: '<=',
            19: '>',
            20: '>=',
            21: 'and',
            22: 'or',
            24: '+',
            25: '-',
            26: '*',
            27: '/',
            28: 'read',
            29: 'write',
            30: '{',
            31: '}',
            32: '=',
            33: 'then',
            34: 'function',
            35: 'string',
            36: 'int',
            37: 'float',
            38: '[',
            39: ']',
            40: 'list',
            41: 'for',
            42: 'in',
            43: 'do',
            44: 'range',
            45: 'integer value',
            46: 'float value',
            47: 'string value',
            48: 'lenght',
            49: ':',
            50: '->',
            51: 'return',
            52: '%',
            53: 'boolean',
            54: 'true',
            55: 'false'

        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'if': TOKEN.IF,
            'while': TOKEN.WHILE,
            'begin': TOKEN.BEGIN,
            'end': TOKEN.END,
            'else': TOKEN.ELSE,
            'read': TOKEN.READ,
            'write': TOKEN.WRITE,
            'and': TOKEN.AND,
            'or': TOKEN.OR,
            'not': TOKEN.NOT,
            'then': TOKEN.THEN,
            'function': TOKEN.FUNCTION,
            'list': TOKEN.LIST,
            'for': TOKEN.FOR,
            'in': TOKEN.IN,
            'do': TOKEN.DO,
            'range': TOKEN.RANGE,
            'int': TOKEN.TINT,
            'float': TOKEN.TFLOAT,
            'string': TOKEN.TSTRING,
            'length': TOKEN.LEN,
            '->': TOKEN.returnCharacter,
            'return': TOKEN.RET,
            'boolean': TOKEN.TBOOLEAN,
            'true': TOKEN.TRUE,
            'false': TOKEN.FALSE,
        }
        if lexema in reservadas:
            return reservadas[lexema]
        else:
            return TOKEN.ident
