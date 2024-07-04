"""
Variables:
['CONST', NOMBRE, 'VAR']

Constantes:
['CONST', VALOR, TIPO DE DATO]

Símbolos y pormenores:
[VALOR EN tok, VALOR ESCRITO, 'TOK']

Funciones con return: / O del usuario (Incluye las funciones que retornan Nada)
[VALOR EN funcReturn, VALOR ESCRITO, 'FUNCRETURN']

Funciones sin return:
[VALOR EN func, VALOR ESCRITO, 'FUNC']

Métodos:
[VALOR ESCRITO, VALOR EN METODOS, 'METD']

"""

import ply.lex as lex

import sys
import subprocess

import json

import ast
import re

from Re_Expresiones import evaluar_expresion
from Re_Reservadas import *

d = combinar(combinar(tok, metodos), combinar(func, funcReturn))

KeysVars = [i for i in d if re.match(r"[a-zA-Z]", i)]

VARIABLES = { # (NOMBRE, CONTEXTO_): (VALOR, TIPO DE DATO) # Contexto = None si es general, "nombre de" si no

}


FUNCIONES = { # NOMBRE: (ARGUMENTOS, fragmentoCodigo)

}


CLASES = {
    

}

""" Ejemplo de clases:

# La clase "Gato"

'Gato': {
        [ # Va a una lista de tuplas
            ( # Cada tupla contiene el nombre de la función y una tupla
                'Func1', ( # Las tuplas contienen:

                    ('x', 'y', 'z'), # Argumentos de la función
                    int, # Linea donde inicia
                )
                
            ),
            (
                Func2', (

                    ('x', 'y'),
                    int,
                )
            )
        ],
    }

"""

IMPORTADOS = []

nLinea = 0

ERRORES_ = [] # Lista de tuplas ('HYS', nLinea)

contexto_ = None

estructuras_primarias = { # Estructuras irreducibles

    (): 'LINEA_VACIA',
    ('CONST',): 'CONSTANTE',

    ('CONST', '=', 'CONST',): 'ASIGNAR',
    ('CONST', 'CONST', '=', 'CONST',): 'ASIGNAR_ELEM',

    ('CONST', '+=', 'CONST',): 'SUMARLE',
    ('CONST', 'CONST', '+=', 'CONST',): 'SUMARLE_ELEM',

    ('CONST', '-=', 'CONST',): 'RESTARLE',
    ('CONST', 'CONST', '-=', 'CONST',): 'RESTARLE_ELEM',

    ('CONST', '*=', 'CONST',): 'MULTIPLICARLE',
    ('CONST', 'CONST', '*=', 'CONST',): 'MULTIPLICARLE_ELEM',

    ('CONST', '/=', 'CONST',): 'DIVIDIRLE',
    ('CONST', 'CONST', '/=', 'CONST',): 'DIVIDIRLE_ELEM',

    ('CONST', '**=', 'CONST',): 'ELEVARLE',
    ('CONST', 'CONST', '**=', 'CONST',): 'ELEVARLE_ELEM',

    ('CONST', '*/=', 'CONST',): 'RADICARLE',
    ('CONST', 'CONST', '*/=', 'CONST',): 'RADICARLE_ELEM',

    ('CONST', '>>=', 'CONST',): 'BITS_DERECHA',
    ('CONST', 'CONST', '>>=', 'CONST',): 'BITS_DERECHA_ELEM',

    ('CONST', '<<=', 'CONST',): 'BITS_IZQUIERDA',
    ('CONST', 'CONST', '<<=', 'CONST',): 'BITS_IZQUIERDA_ELEM',

    ('CONST', '%=', 'CONST',): 'RESTO',
    ('CONST', 'CONST', '%=', 'CONST',): 'RESTO_ELEM',

    ('CONST', '//=', 'CONST',): 'COCIENTE',
    ('CONST', 'CONST', '//=', 'CONST',): 'COCIENTE_ELEM',

    ('if', 'CONST', ':',): 'if',
    ('elif', 'CONST', ':',): 'elif',
    ('else', ':',): 'else',

    ('while', 'CONST', ':',): 'while',
    ('do', 'while', 'CONST', ':',): 'do while',

    ('for', 'CONST', 'in', 'CONST', ':',): 'for',
    ('foreach', 'CONST', 'in', 'CONST', ':',): 'foreach',

    ('goto', 'CONST',): 'goto',

    ('return', 'CONST',): 'return',

    ('match', 'CONST', ':',): 'match',
    ('case', 'CONST', ':',): 'case',

    ('del', 'CONST', 'CONST',): 'del',


}

estructuras_secundarias = { # Estructuras reduccibles a otras

    ('CONST', '.', 'METD',): 'METODO',

    ('CONST', 'for', 'CONST', 'in', 'CONST', ): 'forComp',
}

estructuras_notacion = { # Estructuras que puede usar el usuario para aclarar ciertas situaciones, pero que serán eliminadas de clasificado ya que no aportan nada

    (':', 'CONST',): 'CONSTANTE_ACLARADA',
    ('-', '>', 'CONST',): 'FUNCION_ACLARADA',

}

tipos_de_variables = ( # Tipos de variables en general

    'str', 
    'lista',
    'V-lista',
    'int', 
    'float',
    'complex', 

    'tipo',
    'sintipo',

    'INTER',

)

oPosibles = ( # Operadores destinados a calcular con 2 entidades
    
    # Normales
    
    '+',
    '-',
    '*',
    '/',
    '**',
    '%',
    '//',

    # Bit a Bit

    '&',
    '|',

)

comparadores = ( # Objetos encargados de comparar 2 cantidades o variables

    '>',
    '<',
    '>=',
    '<=',
    '==',
    '!=',

    'and',
    'or',
    'not',

)

asignadores = ( # Elementos capaces de asignar valores a variables

    '=',
    '+=',
    '-=',
    '*=',
    '/=',
    '**=',
    '*/=',
    '>>=',
    '<<=',
    '%=',
    '//=',

)

iterables = ( # Tipos de dato sobre los cuales se puede iterar y no es str

    'lista',
    'V-lista'

)

aIdentar = ( # Palabras clave que lleven si o si a bloques identados (descontando la compresión)

    'for',
    'each',
    'while',
    'do',
    

    'if',
    'elif',
    'else',

    'match',
    'case',

    'class',
    'def',

)

### LEXER ###

import ply.lex as lex

# Definir las palabras reservadas y los tokens
tokens = [
    'ID',       # Identificadores
    'NUMBER',   # Números enteros, flotantes y complejos
    'STRING',   # Cadenas de caracteres
    
    'SUMARLE',
    'RESTARLE',
    'MULTIPLICARLE',
    'DIVIDIRLE',
    'ELEVARLE',
    'RADICARLE',
    'BITS_DER',
    'BITS_IZQ',
    'RESTO',
    'COCIENTE',

    'MODULO',

    'MAS',     # Operador suma
    'MENOS',    # Operador resta
    'POR',    # Operador multiplicación
    'DIVIDIR',   # Operador división
    'ELEVAR',
    'RADICAR',

    'LPAREN',   # Paréntesis izquierdo
    'RPAREN',   # Paréntesis derecho
    'LCORCH',   # Corchete izquierdo
    'RCORCH',   # Corchete derecho
    'LLLAVE',   # Llave izquierda
    'RLLAVE',   # Llave derecha

    'COMA',     # Coma
    'PCOMA',    # Punto y coma
    'PUNTO',    # Punto
    'DPUNTO',   # Dos puntos

    'MENORQ',   # Menor que
    'MAYORQ',   # Mayor que
    'MENORIG',  # Menor o igual
    'MAYORIG',  # Mayor o igual
    'IGUAL',    # Igual
    'IGUALCOMP',# Igual de comparación
    'DISTINTO', # Distinto

    'INTER', # Intervalos

    'COMENTARIO',

] + list(key.values())

# Definir expresiones regulares para tokens

t_SUMARLE = r'\+='
t_RESTARLE = r'-='
t_MULTIPLICARLE = r'\*='
t_DIVIDIRLE = r'/='
t_ELEVARLE = r'\*\*='
t_RADICARLE = r'\*/='

t_BITS_DER = r'>>='
t_BITS_IZQ = r'<<='
t_RESTO = r'%='
t_COCIENTE = r'//='

t_MAS = r'\+'
t_MENOS = r'-'
t_POR = r'\*'
t_DIVIDIR = r'/'
t_ELEVAR = r'\*\*'
t_RADICAR = r'\*/'

t_MODULO = r'%'

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCORCH = r'\['
t_RCORCH = r'\]'
t_LLLAVE = r'\{'
t_RLLAVE = r'\}'

t_COMA = r','
t_PCOMA = r';'
t_PUNTO = r'\.'
t_DPUNTO = r':'

t_MENORQ = r'<'
t_MAYORQ = r'>'
t_MAYORIG = r'>='
t_MENORIG = r'<='
t_IGUALCOMP = r'=='
t_IGUAL = r'='
t_DISTINTO = r'!='

t_COMENTARIO = r'\#'

def t_NUMBER(t):
    r'-*\d+(\.\d+)?j?'
    if 'j' in t.value:
        t.value = complex(t.value)
    elif '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_STRING(t):
    r'\'[^\']*\''
    t.value = t.value[1:-1]
    return t

def t_INTER(t):
    r'\[[^\[\]]*:[^\[\]]*(?::[^\[\]]*)?\]'
    t.value = t.value[1:-1]  # Quitar los corchetes exteriores
    parts = t.value.split(':')
    parts = [p.strip() if p.strip() else 'Nada' for p in parts]
    
    while len(parts) < 3:
        parts.append('Nada')
    
    t.value = parts
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*[\.a-zA-Z_0-9]*'
    t.type = key.get(t.value, 'ID')
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

def agruparTokens(tokens: list) -> list:
    """
    Función que agrupa los tokens en listas y sets anidados.
    """
    stack = []
    lista_actual = []
    resultado = []

    #print(tokens, '<- pre pop')

    for it, token in enumerate(tokens):
        vlista = False

        if token[1] == 'v':
            vlista = True

        elif token[0] == '[' or token[0] == '{':
            # Si encontramos un corchete o llave izquierdo, comenzamos una nueva lista o set
            if vlista and token[0] == '[':
                tokens.pop(it-1)
                nuevo_grupo = ['CONST', [], 'V-lista']
            elif token[0] == '[':
                nuevo_grupo = ['CONST', [], 'lista']
            elif token[0] == '{':
                nuevo_grupo = ['CONST', [], 'set']

            if stack:
                lista_actual.append(nuevo_grupo)
            else:
                resultado.append(nuevo_grupo)
            stack.append(lista_actual)
            lista_actual = nuevo_grupo[1]
        elif token[0] == ']' or token[0] == '}':
            # Si encontramos un corchete o llave derecho, terminamos la lista o set actual
            if stack:
                lista_actual = stack.pop()
        elif token[0] == ',':
            if not stack:
                resultado.append(token)
            else:
                # Si encontramos una coma, simplemente continuamos
                continue
        elif token[0] == 'COMENTARIO':
            break
        elif token[0] == 'INTER':
            # Si encontramos un intervalo, lo añadimos a la lista o set actual
            if stack:
                lista_actual.append(['CONST', token[1:], 'INTER'])
            else:
                resultado.append(['CONST', token[1:], 'INTER'])
        else:
            # Para cualquier otro token, lo añadimos a la lista o set actual
            if stack:
                lista_actual.append(token)
            else:
                resultado.append(token)


    # Añadir cualquier lista o set restante que no haya sido cerrado
    while stack:
        lista_actual = stack.pop()

    return resultado

def combinarTokens(tokens: list) -> list:
    i = 0
    while i < len(tokens) - 1:
        if tokens[i][0] == 'else' and tokens[i+1][0] == 'if':
            tokens[i] = ['elif', 'elif', 'TOK']
            del tokens[i+1:i+2]
        i += 1
    return tokens

def clasificar(texto: str):
    lexer.input(texto)
    tokens = []
    while True:
        token = lexer.token()
        if not token:
            break
        if token.type == 'NUMBER':
            if 'j' in str(token.value):
                token.value = complex(token.value)
                token.type = 'complex'
            elif '.' in str(token.value):
                token.value = float(token.value)
                token.type = 'float'
            else:
                token.value = int(token.value)
                token.type = 'int'
            tokens.append(['CONST', token.value, token.type])
        elif token.type == 'STRING':
            tokens.append(['CONST', token.value, 'str'])
        elif token.type == 'ID':
            if token.value in funcReturn or token.value in FUNCIONES:
                tokens.append(['CONST', token.value, 'FUNCRETURN'])
            elif token.value in metodos:
                tokens.append(['CONST', token.value, 'METD'])
            elif token.value == 'Verdadero':
                tokens.append(['CONST', 1, 'int'])
            elif token.value == 'Falso':
                tokens.append(['CONST', 0, 'int'])
            elif token.value == 'Nada':
                tokens.append(['CONST', 'Nada', 'sintipo'])
            else:
                if token.value == '_':
                    tokens.append(['CONST', '_', 'ANY'])
                else:
                    tokens.append(['CONST', token.value, 'VAR'])
        elif token.type == 'INTER':
            tokens.append(['CONST', [clasificar(token.value[0])[0], clasificar(token.value[1])[0], clasificar(token.value[2])[0]], 'INTER'])
        elif token.type == 'COMENTARIO':
            break
        elif token.value in tok:
            tokens.append([tok[token.value], token.value, 'TOK'])
        elif token.value in key:
            tokens.append([key[token.value], token.value, 'TOK'])
        else:
            print('TOKEN NO PROCESADO: ', token.value, token.type, (token))
            print(tokens)
            sys.exit()

    tokens = agruparTokens(tokens)
    tokens = combinarTokens(tokens)
    #print(tokens, '<- tokens')

    return tokens


def resumir(clasificado: list) -> str:
    """
    C = constante \n
    T = tipo de dato \n
    S = sin tipo \n
    F = función \n
    M = método \n
    simbolo = simbolo

    """
    resumido = ''

    i = 0
    while i < len(clasificado):
        if clasificado[i][0] == 'CONST':
            resumido += 'C'

        elif clasificado[i][2] == 'TOK':
                resumido += clasificado[i][1]

        elif clasificado[i][2] == 'tipo':
            resumido += 'T'

        elif clasificado[i][2] == 'sintipo':
            resumido += 'S'

        i += 1
    return resumido

def asignarP(clasificado: list, inicio: str = '(', fin: str = ')') -> dict:
    #print(clasificado, '<- clasificado')
    texto = ''
    for i in clasificado:
        if i[1] == inicio:
            texto += inicio
        elif i[1] == fin:
            texto += fin
        else:
            texto += ' '

    parejas = {}

    for i in range(len(texto)):
        if texto[i] == inicio:
            cuenta = 0
            for j in range(len(texto[i:])):
                if texto[i+j] == inicio: 
                    cuenta += 1
                elif texto[i+j] == fin:
                    cuenta -= 1

                if cuenta == 0:
                    parejas.setdefault(i, i+j)
                    break
    return parejas

def aplanar(clasificado: list) -> list:
    aplanado = []
    pila = [clasificado]
    
    while pila:
        actual = pila.pop()
        for i in actual[1]:
            if i[2] in iterables:
                pila.append(i)
            else:
                aplanado.append(i)
                
    return aplanado

def reemVariables(clasificado: list, LINEAS: list, nLinea: int, VARIABLES: dict = VARIABLES) -> list:
    #print('VARIABLES:', VARIABLES, sep='\n')
    #print(clasificado, '<- clasificado reemVariables')

    i = 0
    while i < len(clasificado):
        #print(i, '<- i reemVariables')
        Rp = False
        
        if clasificado[i][2] == 'VAR':
            Rp = True

            if i + 1 < len(clasificado):
                if clasificado[i+1][2] == 'set':
                    Rp = False
     
            for j in clasificado[i:]:
                if j[1] in asignadores:
                    Rp = False

            if clasificado[0][0] == 'for':
                if ['in', 'en', 'TOK'] not in clasificado[:i]:
                    Rp = False

            if clasificado[0][0] == 'foreach':
                if ['in', 'en', 'TOK'] not in clasificado[:i]:
                    Rp = False

            if clasificado[0][0] == 'import':
                Rp = False
            if clasificado[0][0] == 'from':
                Rp = False
            if clasificado[0][0] == 'match':
                Rp = False
            if clasificado[0][0] == 'def':
                Rp = False

            if clasificado[0][0] == 'del':
                if i == 1:
                    Rp = False
        
        elif clasificado[i][2] == 'lista':
            clasificado[i] = ['CONST', reemVariables(clasificado[i][1], LINEAS, nLinea), 'lista']
        
        elif clasificado[i][2] == 'V-lista':
            clasificado[i] = ['CONST', reemVariables(clasificado[i][1], LINEAS, nLinea), 'V-lista']

        elif clasificado[i][2] == 'INTER':
            clasificado[i] = ['CONST', reemVariables(clasificado[i][1], LINEAS, nLinea), 'INTER']

        elif clasificado[i][2] == 'set':
            clasificado[i] = ['CONST', reemVariables(clasificado[i][1], LINEAS, nLinea), 'set']

        #print(i, '<- i', Rp)

        if Rp:
            #print(VARIABLES, contexto_)
            #print(clasificado, i)
            if (clasificado[i][1], contexto_) not in VARIABLES:
                #print('AAA')
                if clasificado[i][1] in KeysVars:
                    pass
                else:
                    ServirErrores(2, LINEAS, nLinea, i)
                    sys.exit()
            else:
                clasificado[i] = ['CONST', VARIABLES[(clasificado[i][1], contexto_)][0], VARIABLES[(clasificado[i][1], contexto_)][1]]
            #print(clasificado, i)
        i += 1
    #print(clasificado, '<- reemVariables return')
    #print(VARIABLES)
    return clasificado

def evalFuncionesR(clasificado: list, LINEAS: list) -> list:
    global contexto_
    #print(clasificado, '<- clasificado evalFuncionesR')
    copiaclasificado = clasificado.copy()

    i = 0
    while i < len(copiaclasificado) - 1:
        if copiaclasificado[i][2] == 'FUNC' and copiaclasificado[i+1][1] == '(':
            copiaclasificado[i][2] = 'FUNCRETURN'

        if copiaclasificado[i][2] == 'FUNCRETURN' and copiaclasificado[i+1][1] != '(':
            copiaclasificado[i][2] = 'FUNC'

        i += 1

    if copiaclasificado:
        if copiaclasificado[-1][2] == 'FUNCRETURN':
            copiaclasificado[-1][2] = 'FUNC'

    i = len(copiaclasificado) - 1
    #print(copiaclasificado)

    while i >= 0:
        #print(copiaclasificado, i, '<- copiaclasificado, i')
        parejas = asignarP(copiaclasificado)
        if copiaclasificado[i][2] in ('FUNCRETURN', 'METD'):
            #print('data:')
            j = parejas[i+1]
            #print(parejas)
            #print(i, j, '<- i, j')
            seudoclasificado = copiaclasificado[i+2:j]
            #print(seudoclasificado, '<- seudoclasificado')
            copiaclasificado[i+2:j] = evalExpresiones(seudoclasificado, LINEAS)
            #print(copiaclasificado, '<- copiaclasificado')
            parejas = asignarP(copiaclasificado)
            j = parejas[i+1] # j = indice donde se encuentra el ) de la función
            #print(copiaclasificado, i, '<- copiaclasificado, i')
            #eliminar.append((i+1, j+1))

            if copiaclasificado[i][2] == 'FUNCRETURN':
                #print('FUNCIONES:', FUNCIONES)
                if copiaclasificado[i][1] in FUNCIONES:
                    pre_contexto_ = contexto_
                    contexto_ = copiaclasificado[i][1]

                    ArgumentosCall = []
                    ArgumentosClave = []
                    k = i + 2
                    while k < j:
                        if copiaclasificado[k+1][0] == '=':
                            ArgumentosClave.append((copiaclasificado[k], copiaclasificado[k + 2]))
                            k += 2
                        elif copiaclasificado[k][0] == ',':
                            pass
                        else:
                            ArgumentosCall.append(copiaclasificado[k])
                        k += 1

                    ArgumentosFunc = FUNCIONES[copiaclasificado[i][1]][0]

                    argumentos = [None] * len(ArgumentosFunc)
                    # Asignar argumentos posicionales
                    for indi, (arg, valor) in enumerate(zip(ArgumentosFunc, ArgumentosCall)):
                        argumentos[indi] = valor

                    # Asignar argumentos clave
                    for clave, valor in ArgumentosClave:
                        for indi, arg in enumerate(ArgumentosFunc):
                            if arg[0][1] == clave[1]:
                                argumentos[indi] = valor
                                break

                    # Asignar valores predeterminados a los argumentos que no fueron proporcionados
                    for indi, arg in enumerate(ArgumentosFunc):
                        if argumentos[indi] is None:
                            if len(arg) > 1:  # Verificar si el argumento tiene un valor predeterminado
                                argumentos[indi] = ['CONST', arg[1][1], arg[1][2]]
                            else:
                                raise TypeError(f"Argumento faltante: {arg[0][1]}")
                    #print(argumentos)
                    # Actualizar VARIABLES con los argumentos
                    for arg, valor in zip(ArgumentosFunc, argumentos):
                        VARIABLES[(arg[0][1], contexto_)] = (valor[1], valor[2])

                    retorno = ejecutarCodigo(FUNCIONES[copiaclasificado[i][1]][1][1:])
                    contexto_ = pre_contexto_
                    copiaclasificado[i] = retorno[-1][0]

                    #sys.exit()
                    #print(copiaclasificado, i)

                    #print(copiaclasificado, i, '<- copiaclasificado, i')

                else:
                    #print(copiaclasificado, i, 'pre match')
                    match copiaclasificado[i][1]:
                        case 'ingresar':
                            if j - i == 2:
                                copiaclasificado[i] = ['CONST', f'{input()}', 'str']

                            elif j - i == 3:
                                copiaclasificado[i] = ['CONST', f'{input(copiaclasificado[i+2][1])}', 'str']

                        case 'largo':
                            copiaclasificado[i] = ['CONST', len(copiaclasificado[i+2][1]), 'int']

                        case 'invertir':
                            copiaclasificado[i] = ['CONST', [k for k in copiaclasificado[i+2][1][::-1]], copiaclasificado[i+2][2]]

                        case 'rango':
                            #print(copiaclasificado, j, i, '<- copiaclasificado, j, i')
                            if j - i == 3:
                                copiaclasificado[i] = clasificar(str(list(range(int(copiaclasificado[i+2][1])))))[0]
                            elif j - i == 5:
                                copiaclasificado[i] = clasificar(str(list(range(int(copiaclasificado[i+2][1]), int(copiaclasificado[i+4][1])))))[0]

                            elif j - i == 7:
                                copiaclasificado[i] = clasificar(str(list(range(int(copiaclasificado[i+2][1]), int(copiaclasificado[i+4][1]), int(copiaclasificado[i+6][1])))))[0]
                        
                        case 'lista':
                            copiaclasificado[i] = clasificar(str(list(copiaclasificado[i+2][1])))[0]

                        case 'matriz':
                            # Argumentos:
                            # Lista con dimensiones, rellenar con
                            
                            dim = []
                            for k in reversed(copiaclasificado[i+2][1]):
                                dim.append(k[1])
                            #print(copiaclasificado, i)

                            relleno = copiaclasificado[i+4][1]

                            #print(relleno, dim, sep='\n')
                            matriz = relleno
                            for k in dim:
                                matriz = [matriz] * k

                            #print(clasificar(str(matriz)))

                            copiaclasificado[i] = clasificar(str(matriz))[0]
                            #print(clasificado, i)

                        case 'enumerar':
                            #print(copiaclasificado, i)
                            k = 0
                            temp = []

                            while k < len(copiaclasificado[i+2][1]):
                                temp += [['CONST', [['CONST', k, 'int'], copiaclasificado[i+2][1][k]], 'lista']]

                                k += 1
                            #print('temp:', temp)

                            copiaclasificado[i] = ['CONST', temp, 'lista']
                            #print(copiaclasificado, i)

                        case 'todos':
                            #print(copiaclasificado, i)
                            k = 0
                            copiaclasificado[i] = ['CONST', 1, 'int']
                            while k < len(copiaclasificado[i+2][1]):
                                if not copiaclasificado[i+2][1][k][1]:
                                    copiaclasificado[i] = ['CONST', 0, 'int']
                                    break
                                k += 1
                        
                        case 'alguno':
                            k = 0
                            copiaclasificado[i] = ['CONST', 0, 'int']
                            while k < len(copiaclasificado[i+2][1]):
                                if copiaclasificado[i+2][1][k][1]:
                                    copiaclasificado[i] = ['CONST', 1, 'int']
                                    break
                                k += 1
                        
                        case 'relu':
                            #print(copiaclasificado, i)
                            if copiaclasificado[i+2][1] > 0:
                                copiaclasificado[i] = copiaclasificado[i+2].copy()
                            else: 
                                copiaclasificado[i] = ['CONST', 0, 'int']
                            
                        case 'mapear':
                            #print(copiaclasificado, i)
                            
                            iterable = copiaclasificado[i+4]


                            funcion = copiaclasificado[i+2]
                            funcion[2] = 'FUNCRETURN'
                            #print(funcion, '<- funcion')
                            #print(iterable[1], '<- iterable[1]')
                            #print(FUNCIONES)

                            if funcion[1] in FUNCIONES:
                                fragmentoCodigo = FUNCIONES[copiaclasificado[i+2][1]][1]

                                l = 0
                                while l < len(iterable[1]):
                                    #print(iterable[1][l])

                                    pre_contexto_ = contexto_
                                    contexto_ = copiaclasificado[i+2][1]

                                    ArgumentosCall = [iterable[1][l]]
                                    

                                    ArgumentosFunc = FUNCIONES[copiaclasificado[i+2][1]][0][0]
                                    for k in range(len(ArgumentosFunc)):
                                        VARIABLES[(ArgumentosFunc[k][1], contexto_)] = (ArgumentosCall[k][1], ArgumentosCall[k][2])

                                    #print(VARIABLES)

                                    retorno = ejecutarCodigo(fragmentoCodigo[1:])
                                    #print(retorno)

                                    contexto_ = pre_contexto_

                                    iterable[1][l] = retorno[-1][0]
                                
                                    l += 1

                            else:
                                l = 0
                                funcion[2] = 'FUNCRETURN'

                                while l < len(iterable[1]):
                                    

                                    iterable[1][l] = evalFuncionesR([funcion, ['(', '(', 'TOK'], iterable[1][l], [')', ')', 'TOK']], LINEAS)[0]

                                    l += 1

                            copiaclasificado[i] = iterable

                        case 'filtrar':
                            #print(copiaclasificado, i)
                            iterable = copiaclasificado[i+4]
                            iterabletemp = ['CONST', [], 'lista']
                            funcion = copiaclasificado[i+2]
                            funcion[2] = 'FUNCRETURN'

                            if funcion[1] in FUNCIONES:
                                fragmentoCodigo = FUNCIONES[funcion[1]][1]

                                l = 0
                                while l < len(iterable[1]):
                                    #print(iterable[1][l])

                                    pre_contexto_ = contexto_
                                    contexto_ = copiaclasificado[i+2][1]

                                    ArgumentosCall = [iterable[1][l]]
                                    

                                    ArgumentosFunc = FUNCIONES[copiaclasificado[i+2][1]][0][0]
                                    for k in range(len(ArgumentosFunc)):
                                        VARIABLES[(ArgumentosFunc[k][1], contexto_)] = (ArgumentosCall[k][1], ArgumentosCall[k][2])

                                    #print(VARIABLES)

                                    retorno = ejecutarCodigo(fragmentoCodigo[1:])
                                    #print(retorno, '<- retorno')

                                    contexto_ = pre_contexto_
                                    #print(iterabletemp)
                                    if retorno[-1][0][1]:
                                        iterabletemp[1].append(iterable[1][l])
                                
                                    l += 1
                                copiaclasificado[i] = iterabletemp
                            else:
                                l = 0
                                funcion[2] = 'FUNCRETURN'
                                iterable = copiaclasificado[i+4]
                                iterabletemp = iterabletemp = ['CONST', [], 'lista']

                                while l < len(iterable[1]):
                                    iterabletemp[1].append(evalFuncionesR([funcion, ['(', '(', 'TOK'], iterable[1][l], [')', ')', 'TOK']], LINEAS)[0])

                                    l += 1
                            copiaclasificado[i] = iterabletemp

                        case 'aplanar':
                            #print(copiaclasificado, i)
                            copiaclasificado[i] = ['CONST', aplanar(copiaclasificado[i+2]), 'lista']
                        
                        case 'mostrar':
                            if j - i == 2: # No tiene argumentos
                                pass 
                            else:
                                for k in range(i+2, j):
                                    #print(copiaclasificado, k, '<- clasificado, k')
                                    match copiaclasificado[k][2]:
                                        case 'str':
                                            print(copiaclasificado[k][1], end=' ')
                                        case 'int':
                                            print(copiaclasificado[k][1], end=' ')
                                        case 'float':
                                            print(copiaclasificado[k][1], end=' ')
                                        case 'complex':
                                            print(copiaclasificado[k][1], end=' ')
                                        case 'lista':
                                            print(imprimir_lista(copiaclasificado[k][1], LINEAS), end=' ')
                                        case 'bool':
                                            print(copiaclasificado[k][1], end=' ')
                                        case 'sintipo':
                                            print(copiaclasificado[k][1], end=' ')
                                        case 'VAR':
                                            print(VARIABLES[(copiaclasificado[k][1], contexto_)][0], end=' ')
                                        case 'TOK':
                                            if copiaclasificado[k][1] not in ('(', ',', ')'):
                                                print(copiaclasificado[k][1], end=' ')
                                        case 'INTER':
                                            print(imprimir_inter(copiaclasificado[k][1]), end=' ')
                                        case _:
                                            print(clasificado, j, '<- clasificado, j MOSTRAR')
                                            ...

                            print()
                            copiaclasificado[i] = ['CONST', 'Nada', 'sintipo']

                        case 'ayuda':
                            if j - i == 2:
                                ...
                            elif j - i == 3:
                                ...
                            copiaclasificado[i] = ['CONST', 'Nada', 'sintipo']

                #print(copiaclasificado, i, j)
                del copiaclasificado[i+1:j+1]
                #print(copiaclasificado)
            elif copiaclasificado[i][2] == 'METD':
                ...
            #print(copiaclasificado, i, j, '<- data 2')
            #del copiaclasificado[i+1:j+1]    
            #print(copiaclasificado)
            #i = j + 1
                del copiaclasificado[i+1:j+1]
            #eliminar.append((i+1, j+1)) # Se agregan los índices desde el ( hasta el ) para después eliminarlos
        i -= 1 # Y se le resta 1

    """for i, j in reversed(eliminar): # Se elimina del final al principio para "borrar la basura"
        #print(i, j)
        del copiaclasificado[i:j]"""

    for i, j in enumerate(reversed(copiaclasificado)):
        if j == 'ELIMINAR':
            copiaclasificado.pop(i)
    clasificado = copiaclasificado.copy()

    #print(clasificado, '<- evalFuncionesR return')
    return clasificado

def idenExpresiones(clasificado: list) -> list:
    #print(clasificado, '<- clasificado idenExpresiones')
    parejas = asignarP(clasificado)
    parejas2 = {}
    for i in parejas.keys():
        if i >= 1:
            if clasificado[i-1][2] in ('FUNC', 'METD', 'FUNCRETURN'):
                parejas2.setdefault(i, parejas[i])

    #print('parejas2:', parejas2)
    pares = [i for i in parejas2]
    for i in parejas2:
        pares.append(parejas2[i])
    #print(pares)

    expresiones = [] # (inicio, fin)
    i = 0
    inicio = False
    fin = False
    #print(clasificado, '<- clasificado')
    while i < len(clasificado):
        #print('pre:', inicio, fin)
        if clasificado[i][2] in tipos_de_variables:
            #print('tipos_de_variables', i)
            if inicio is False:
                inicio = i
                fin = False

            """elif clasificado[i][2] == 'VAR':
            if inicio is False:
                inicio = i
                fin = False"""

        elif clasificado[i][1] in oPosibles:
            #print('oPosibles', i)
            if inicio is False:
                inicio = i
                fin = False

        elif clasificado[i][1] in ('(', ')'):
            #print('()', i)
            if i not in pares:
                if inicio is False:
                    inicio = i
                    fin = False
            else:
                if i + 1 == len(clasificado):
                    break
                    # Esta es la última iteración del bucle y el elemento actual es un '(' o un ')' (normalmente)          

        elif clasificado[i][0] in comparadores:
            #print('comparadores', i)
            if inicio is False:
                inicio = i
                fin = False
        
        elif clasificado[i][2] == 'INTER':
            if inicio is False:
                inicio = i
                fin = False
        
        else:
            #print('else', i, inicio, fin)
            if inicio is not False:
                #print(inicio, i)
                fin = i
                expresiones.append((inicio, fin))
                inicio = False
        #print('post:', inicio, fin)
        i += 1
    if inicio is not False and fin is False: # La linea empieza con una expresión y nunca se cierra
        fin = i
        expresiones.append((inicio, fin))

    #print(clasificado)
    #print(expresiones, '<- idenExpresiones return')
    for i in reversed(expresiones):
        if i[0] + 1 == i[1]:
            expresiones.remove((i[0], i[1]))
    return expresiones


def evalExpresiones(clasificado: list, LINEAS) -> list:
    #print(clasificado, ' <- clasificado evalExpresion 1')

    # Funciones con return (Nada incluido)
    clasificado = evalFuncionesR(clasificado, LINEAS)
    #print(clasificado, '<- evalFuncionesR')

    # Identifica expresiones
    expresiones = idenExpresiones(clasificado)
    #print(expresiones, '<- idenExpresiones')

    # Calcula resultados
    resultados = []
    i = 0
    while i < len(expresiones):
        subexpresion = ''
        hayString = False
        hayComp = False
        hayImag = False
        #print(expresiones, i, '<- expresiones, i')
        j = expresiones[i][0]
        while j < expresiones[i][1]:
            if clasificado[j][2] == 'str':
                subexpresion += repr(clasificado[j][1])
                hayString = True
            elif clasificado[j][2] == 'lista':
                subexpresion += str(procesarListaAnidada(clasificado[j][1]))
            elif clasificado[j][2] == 'V-lista':
                subexpresion += str(procesarListaAnidada(clasificado[j][1]))
            elif clasificado[j][0] in comparadores:
                hayComp = True
                subexpresion += str(clasificado[j][0])

            elif clasificado[j][2] == 'INTER':
                #print('Entra como inter')
                #print(clasificado, j)
                subexpresion += '['
                k = 0
                while k < 3:
                    if clasificado[j][1][k][1] == 'Nada':
                        subexpresion += 'None'
                    else:
                        subexpresion += str(clasificado[j][1][k][1])
                    if 0 <= k <= 1:
                        subexpresion += ':' 
                    k += 1
                subexpresion += ']'

            else:
                subexpresion += str(clasificado[j][1])
            j += 1

        #print(clasificado, i, '<- clasificado, i ***')

        #print(f'{subexpresion = }')

        try:
            res = evaluar_expresion(subexpresion)

        except:
            print(clasificado, i, '<- clasificado, i ***')
            print(f'{subexpresion = }')
            sys.exit()
        
        if isinstance(res, complex):
            #print("hayImag")
            hayImag = True
        resultados.append((res, hayString, hayComp, hayImag))
        i += 1

    # Reemplaza por los resultados y depura el resto del clasificado
    i = 0
    j = 0
    while i < len(resultados):
        #print(resultados, i, '<- resultados, i')
        #print(expresiones, i, '<- expresiones, i')
        if resultados[i][1]: # Si hay string
            clasificado[expresiones[i][0]] = ['CONST', resultados[i][0], 'str']
        elif resultados[i][2]: # Si hay comparadores
            clasificado[expresiones[i][0]] = ['CONST', int(resultados[i][0]), 'int']
        elif resultados[i][3]:
            #print('Data..', clasificado, expresiones, resultados, i, sep='\n')
            if not res.real:
                #print(expresiones, i ,'<- expresiones, i')
                clasificado[expresiones[i][0]] = clasificar(str(resultados[i][0]))[0]
                #print(clasificado, '<- clasificado')
            else:
                #print(expresiones, i ,'<- expresiones, i')
                #clasificado[expresiones[i][0]] = clasificar(str(resultados[i][0]))[0]
                semiclasificado = clasificar(str(resultados[i][0])[1:-1])
                for j in range(len(semiclasificado)):
                    #print(resultados, i, j)
                    clasificado[expresiones[i][0]+j] = semiclasificado[j]
                #print(clasificado, '<- clasificado')
        else:
            insertar = clasificar(str(resultados[i][0]))
            if insertar[0][0] == '-': # Es negativo
                #print('Data..')
                #print(insertar, clasificado, expresiones, resultados, i, sep='\n')
                insertar[1][1] *= -1 
                insertar[0] = insertar[1]

            #print('Data..', clasificado, expresiones, resultados, insertar, i, sep='\n')
            #print(clasificar(str(resultados[i][0])))
            #print(expresiones, i ,'<- expresiones, i')
            clasificado[expresiones[i][0]] = insertar[0]
            #print(clasificado, '<- clasificado')
        i += 1
    #print('Data 2..')
    #print(clasificado)
    #print(resultados, expresiones, sep='\n')
    i = len(resultados) - 1
    while i >= 0:
        #print(i, '<- i')
        del clasificado[expresiones[i][0]+1+j:expresiones[i][1]]
        i -= 1

    #print(clasificado, '<- evalExpresiones return')
    return clasificado

def procesarListaAnidada(lista):
    #print(lista, '<- lista')
    if isinstance(lista, list):
        if lista[0][2] == 'INTER':
            ret = ''
            for i, elem in enumerate(lista[0][1]):
                if elem[1] != 'Nada':
                    ret += f'{elem[1]}'
                else:
                    ret += 'None'
                if i + 1 < 3:
                    ret += ':'
            return '[' + ret + ']'
        
        else:
            ret = ''
            for it, elem in enumerate(lista):
                if elem[1] != 'Nada':
                    ret += f'{procesarListaAnidada(elem[1])}'
                else:
                    ret += 'None'
                if it + 1 < len(lista):
                    ret += ','
            return '[' + ret + ']'

            #return '[' + ','.join(procesarListaAnidada(elem[1]) for elem in lista if elem[1] != 'Nada' else: 'None') + ']'
        
    else:
        return repr(lista)
    
def imprimir_lista(lista, LINEAS):
    if isinstance(lista, list):
        return '[' + ', '.join(imprimir_lista(reemVariables([item], LINEAS, nLinea)[0][1], LINEAS) for item in lista) + ']'
    else:
        return str(lista)
    
def imprimir_inter(inter):
    exp = ''
    i = 0
    while i < 3:
        if inter[i][1] == 'Nada':
            pass
        else:
            exp += str(inter[i][1])
        if i + 1 < 3:
            exp += ':' 
        i += 1
    return exp

def depurarComentarios(clasificado: list) -> list:
    i = 0
    simple = []
    doble = []
    eliminar = []
    while i < len(clasificado):
        if clasificado[i] == ['#', '#', 'TOK']:
            if doble:
                doble += [i+1]
                eliminar.append(tuple(doble))
                doble = []

            elif simple: 
                simple += [i+1]
                if len(simple) == 2:

                    eliminar.append(tuple(simple))
                    simple = []
            else:
                simple = [i]

        elif clasificado[i] == ['/', '/', 'TOK'] and doble:
            simple = []
            if len(doble) == 2:
                eliminar.append(tuple(doble))
                doble = []

        i += 1

    if simple:
        eliminar.append((simple[0], -1))

    for i, j in reversed(eliminar):
        del clasificado[i:j]
    if simple:
        clasificado.pop()

    return clasificado

def depurarNotacion(clasificado: list, EN: dict = estructuras_notacion) -> list:
    #print(clasificado, '<- depurarNotacion arg')
    for e in EN:
        #print(e, '<- e')
        n = len(e)
        i = 0
        while i < len(clasificado):
            #print(i)
            seudoclasificado = tuple([j[0] for j in clasificado[i:i+n]])
            if seudoclasificado == e:
                del clasificado[i:i+n]
                i -= 1
            i += 1
    #print(clasificado, '<- depurarNotacion return')
    return clasificado

def semiIndices(clasificado: list, LINEAS: list, nLinea: int) -> list:
    i = 0
    while i < len(clasificado):
        if clasificado[i][2] == 'VAR':
            if i + 1 < len(clasificado):
                if clasificado[i+1][2] == 'set':
                    #print(clasificado, i, '<- clasificado, i')

                    temp = str(clasificado[i][1]) + '_' + str(reemVariables(clasificado[i+1][1], LINEAS, nLinea)[0][1])

                    clasificado[i][1] = temp

                    del clasificado[i+1:i+2]
                    i -= 1
    
        elif clasificado[i][2] == 'lista':
            clasificado[i] = ['CONST', semiIndices(clasificado[i][1], LINEAS, nLinea), 'lista']
        elif clasificado[i][2] == 'V-lista':
            clasificado[i] = ['CONST', semiIndices(clasificado[i][1], LINEAS, nLinea), 'V-lista']

        i += 1
    return clasificado

def ejecutarGeneral(clasificado: list, LINEAS: list, nLinea, EP: dict = estructuras_primarias, ES: dict = estructuras_secundarias):
    """"
        Toma como entrada una linea clasificada y evalúa las estructuras que tenga dentro a excepción de las que lleven a
        bloques identados y cuestiones que necesiten un enfoque aparte y mas robusto (ubicado en ejecutarCodigo)
    """
    global VARIABLES, KeysVars
    #print(clasificado, '<- clasificado ejecutarGeneral')

    clasificado = semiIndices(clasificado, LINEAS, nLinea)
    #print(clasificado,'<- semiIndices General')

    clasificado = reemVariables(clasificado, LINEAS, nLinea)
    #print(clasificado,'<- reemVariables General')

    clasificado = evalExpresiones(clasificado, LINEAS)
    #print(clasificado, '<- evalExpresiones General')


    for e in ES:
        n = len(e)
        i = 0
        while i < len(clasificado):
            seudoclasificado = tuple([j[0] for j in clasificado[i:i+n]])
            #print(seudoclasificado, 'seudo')
            #print(e, 'e')
            if seudoclasificado == e:
                estructuraF = ES[seudoclasificado]
                #print(seudoclasificado, estructuraF, sep='\n')
                match estructuraF:
                    case 'REEMPLAZAR':
                        ...
                    case 'forComp':
                        #print(clasificado, i)
                        iterable = clasificado[i+4]
                        variablesForC = [j[1] for j in clasificado[i+2:i+n-2] if j[2] == 'VAR']
                        #print(variablesForC)
                        resultado = []
                        #print(iterable)
                        if len(variablesForC) == 1:
                            j = 0
                            while j < len(iterable[1]):
                                VARIABLES[variablesForC[0]] = (iterable[1][j][1], iterable[1][j][2])
                                resultado.append(['CONST', iterable[1][j][1], iterable[1][j][2]])
                                j += 1
                        #print(resultado, '<- resultado')
                        clasificado[i] = ['CONST', resultado, 'lista']

                    case 'METODO': # Esto hay que borrarlo y pasarlo a evalFuncionesR
                        #print(clasificado, i)
                        #print(VARIABLES)

                        tipo = clasificado[i][2]

                        match tipo:
                            case 'str':
                                match clasificado[i+2][1]:
                                    case 'capitalize':
                                        ... 
                                    case 'casefold':
                                        ...
                                    case 'center':
                                        ...
                                    case 'encode':
                                        ...
                                    case 'endswith':
                                        ...
                                    case 'expandtabs':
                                        ...
                                    case 'find':
                                        ...
                                    case 'format':
                                        ...
                                    case 'format_map':
                                        ...
                                    case 'isalnum':
                                        ...
                                    case 'isalpha':
                                        ...
                                    case 'isascii':
                                        ...
                                    case 'isdecimal':
                                        ...
                                    case 'isdigit':
                                        ...
                                    case 'isidentifier':
                                        ...
                                    case 'isislower':
                                        ...
                                    case 'isnumeric':
                                        ...
                                    case 'isprintable':
                                        ...
                                    case 'isspace':
                                        ...
                                    case 'istitle':
                                        ...
                                    case 'isupper':
                                        ...
                                    case 'join':
                                        ...
                                    case 'ljust':
                                        ...
                                    case 'lower':
                                        ...
                                    case 'lstrip':
                                        ...
                                    case 'maketrans':
                                        ...
                                    case 'partition':
                                        ...
                                    case 'removeprefix':
                                        ...
                                    case 'removesufix':
                                        ...
                                    case 'replace':
                                        ...
                                    case 'rfind':
                                        ...
                                    case 'rindex':
                                        ...
                                    case 'rjust':
                                        ...
                                    case 'rpartition':
                                        ...
                                    case 'rsplit':
                                        ...
                                    case 'rstrip':
                                        ...
                                    case 'split':
                                        ...
                                    case 'splitlines':
                                        ...
                                    case 'startswith':
                                        ...
                                    case 'strip':
                                        ...
                                    case 'swapcase':
                                        ...
                                    case 'title':
                                        ...
                                    case 'translate':
                                        ...
                                    case 'upper':
                                        ...
                                    case 'zfill':
                                        ...         
                            case 'int' | 'float':
                                ...
                            case 'complex':
                                ...
                            case 'lista':
                                    match clasificado[i+2][1]:
                                        case 'append':
                                            ...
                                        case 'remove':
                                            ...
                                        case 'pop':
                                            ...
                                        case 'clear':
                                            ...
                                        case 'copy':
                                            ...
                                        case 'count':
                                            ...
                                        case 'extend':
                                            ...
                                        case 'index':
                                            ...
                                        case 'insert':
                                            ...
                                        case 'reverse':
                                            ...
                                        case 'sort':
                                            ...
                            case 'bool':
                                ...                      

                #print(clasificado, i + 1, i + n)
                del clasificado[i+1:i+n] # Elimina la estructura encontrada para reducir el clasificado hasta las estructuras primaras
                #print(clasificado)
                i -= 1 # Encuentra una estructura y retrocede, para después quedarse en el lugar que la encontró, por si en el clasificado reducido hay una en el mismo lugar
            i += 1

    #print(clasificado, '<- clasificado ejecutarGeneral')
    directiva = [] # directiva es el primer elemento de cada elemento en clasificado

    for i in clasificado:
        directiva.append(i[0])
    directiva = tuple(directiva)
    #print(directiva, '<- directiva')
    if len(clasificado) >= 1:
        if clasificado[0][0] == 'print':
            directiva = ('print', '(', 'CONST', ')',)

        elif clasificado[0][0] == 'if':
            directiva = ('if', 'CONST', ':',)

        elif clasificado[0][0] == 'elif':
            directiva = ('elif', 'CONST', ':',)

    try:
        ejecutar = EP[directiva]

    except KeyError:
        ejecutar = None
    #print(directiva, '<- directiva')
    #print(ejecutar, '<- ejecutar')

    match ejecutar:
        case 'LINEA_VACIA':
            pass

        case 'ASIGNAR':
            #print(clasificado, '<- clasificado ASIGNAR')       

            VARIABLES[(clasificado[0][1], contexto_)] = (clasificado[2][1], clasificado[2][2])

            KeysVars += [clasificado[0][1]]

            #print(clasificado, '<- clasificado ejecutarGeneral')
            #print('VARIABLES:', VARIABLES, sep='\n')

        case 'ASIGNAR_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = clasificado[3]

        case 'SUMARLE':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] + clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])

        case 'SUMARLE_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] + clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']

        case 'RESTARLE':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] - clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])

        case 'RESTARLE_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] - clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']
        
        case 'MULTIPLICARLE':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] * clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])

        case 'MULTIPLICARLE_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] * clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']
        
        case 'DIVIDIRLE':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] / clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])

        case 'DIVIDIRLE_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] / clasificado[3][1], 'float']
        
        case 'ELEVARLE':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] ** clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])
        
        case 'ELEVARLE_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] ** clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']
        
        case 'RADICARLE':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] ** (1 / clasificado[2][1]), VARIABLES[(clasificado[0][1], contexto_)][1])
        
        case 'RADICARLE_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] ** (1 / clasificado[3][1]), 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']

        case 'RESTO':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] % clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])
        
        case 'RESTO_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] % clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']

        case 'COCIENTE':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] // clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])
        
        case 'COCIENTE_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] // clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']
        
        case 'BITS_DERECHA':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] >> clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])
        
        case 'BITS_DERECHA_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] >> clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']
        
        case 'BITS_IZQUIERDA':
            VARIABLES[(clasificado[0][1], contexto_)] = (VARIABLES[(clasificado[0][1], contexto_)][0] << clasificado[2][1], VARIABLES[(clasificado[0][1], contexto_)][1])
        
        case 'BITS_IZQUIERDA_ELEM':
            VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]] = ['CONST', VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][1] << clasificado[3][1], 'int' if VARIABLES[(clasificado[0][1], contexto_)][0][clasificado[1][1][0][1]][2] == clasificado[3][2] == 'int' else 'float']

        
        
        case 'while' | 'do while' | 'if' | 'elif' | 'else' | 'for' | 'foreach' | 'CONSTANTE' | 'goto' | 'del':
            pass

        case _:
            #print('ejecutarGeneral >> case _:')
            #print(clasificado)
            resumido = resumir(clasificado)
            #print(resumido, '<- resumido')
            if re.fullmatch(r"C(,C)*(=C(,C)*)+", resumido):
                #print("Hace fullmatch")
                for j, k in enumerate(reversed(clasificado)): # Buscamos el índice del último asignador
                    if k[1] in asignadores:
                        break

                #print(j, '<- j') 
                #print(clasificado)

                #cantIg = (len(clasificado) + 1) / (j + 1) - 1

                j = len(clasificado)-j-1 # Como lo tenemos desde la derecha, lo pasamos desde la izquierda

                #print(j, '<- j')

                valores = [] # Lista de tuplas que contienen (VALOR, TIPO DE DATO)

                asignados = [] # Variables a las cuales se le van a asignar un valor
                temp = [] 
                for i in range(0, len(clasificado), 2):
                    if i < j:
                        if clasificado[i][2] == 'lista':
                            for _ in range(clasificado[i][1][0][1]):
                                temp.append('_')
                        else:
                            temp.append(clasificado[i][1]) 

                        if clasificado[i+1][1] in asignadores:
                            asignados += [temp]
                            temp = []
                    else:
                        valores.append([clasificado[i][1], clasificado[i][2]])

                #print(asignados, valores)

                #sys.exit()

                if len(asignados[0]) <= len(valores):
                    i = 0
                    while i < len(asignados):
                        k = 0
                        while k < len(asignados[0]):
                            VARIABLES[(asignados[i][k], contexto_)] = (valores[k][0], valores[k][1])
                            k += 1
                        i += 1

                else:
                    i = 0
                    valores2 = []
                    while i < len(valores):
                        if valores[i][1] in iterables:
                            for k in valores[i][0]:
                                valores2.append([k[1], k[2]])
                        else:
                            valores2.append(valores[i])
                        i += 1

                    #print(asignados)
                    #print(valores2)
                    #print(clasificado)

                    i = 0
                    while i < len(asignados):
                        k = 0
                        while k < len(asignados[0]):
                            VARIABLES[(asignados[i][k], contexto_)] = (valores2[k][0], valores2[k][1])
                            k += 1
                        i += 1
                #print(valores2)

                #print(VARIABLES)

            
            else:
                print(clasificado, '<- clasificado de sintaxis')
                sys.exit()


    return clasificado

def contarEspacios(texto: str) -> int:
    espacios = 0
    try:
        while texto[espacios] == ' ':
            espacios += 1
        return espacios
    except:
        if texto == ' '*len(texto): return len(texto)
        else: return 0

def seleccionarFragmento(LINEAS, nLinea):
    #print(LINEAS, nLinea)
    nivelIdentado = contarEspacios(LINEAS[nLinea])
    # Se define que el fragmento de código comenzará con la linea del condicional
    fragmentoCodigo = [LINEAS[nLinea]]
    # Mientras la siguiente línea tenga más espacios en blanco que el nivel "base" de identado (es decir, más espacios que la línea condicional), se añade dicha línea al fragmento, y se pasa a la siguiente línea
    try:
        while contarEspacios(LINEAS[nLinea+1]) > nivelIdentado or LINEAS[nLinea+1] == ' '*len(LINEAS[nLinea+1]):
            fragmentoCodigo.append(LINEAS[nLinea+1])
            nLinea += 1
    except:
        pass
    
    if fragmentoCodigo[-1] not in ('', ' '*len(fragmentoCodigo)):
        fragmentoCodigo.append('')
        #nLinea += 1
    #print(fragmentoCodigo, nLinea, '<- seleccionarFragmento return')
    return fragmentoCodigo, nLinea

def comprobarIdentacionAct(LINEAS, nLinea):
    identado = None
    n = 1
    while LINEAS[nLinea+n] == ' '*len(LINEAS[nLinea+n]):
        n += 1

    if contarEspacios(LINEAS[nLinea]) < contarEspacios(LINEAS[nLinea+n]):
        identado = 1 # Aumento

    elif contarEspacios(LINEAS[nLinea]) == contarEspacios(LINEAS[nLinea+n]):
        identado = 0 # Se mantuvo igual

    else:        
        identado = -1 # Bajo

    return identado

def ejecutarMientras(fragmentoCodigo, LINEAS, nLinea):
    #print(fragmentoCodigo)
    condicion = clasificar(fragmentoCodigo[0])

    condicion = reemVariables(condicion, LINEAS, nLinea)
    condicion = evalExpresiones(condicion, LINEAS)

    while condicion[1][1]:
        if ejecutarCodigo(fragmentoCodigo[1:], nLinea=0)[1]:
            break
        condicion = clasificar(fragmentoCodigo[0])

        condicion = reemVariables(condicion, LINEAS, nLinea)
        condicion = evalExpresiones(condicion, LINEAS)  
    #print(condicion, '<- condicion')
    return condicion[1][1]

def ejecutarHaceMientras(fragmentoCodigo, LINEAS, nLinea):
    ejecutarCodigo(fragmentoCodigo[1:], nLinea=0)
    #print(fragmentoCodigo[1:])
    condicion = clasificar(fragmentoCodigo[0])

    condicion = reemVariables(condicion, LINEAS, nLinea)
    condicion = evalExpresiones(condicion, LINEAS)
    #print(condicion)

    while condicion[2][1]:
        if ejecutarCodigo(fragmentoCodigo[1:], nLinea=0)[1]:
            break
        condicion = clasificar(fragmentoCodigo[0])

        condicion = reemVariables(condicion, LINEAS, nLinea)
        condicion = evalExpresiones(condicion, LINEAS)
    #print(condicion, '<- condicion')
    return condicion[2][1]

def ejecutarCodigo(LINEAS: list, fin = None, nLinea: int = 0):
    global IMPORTADOS, KeysVars
    #print('Ejecutando:')
    #print(LINEAS)
    enClase = False
    identadoClase = -1
    ultimasCondiciones = [None, None, None, None, None, [['CONST', 'Nada', 'sintipo']]]

    """
        ultimasCondiciones

            para | cada | mientras | hace mientras

            salir 

            continuar

            retorno

            si | sino si | sino

            clasificado (VALOR)
    """

    if fin == None:
        fin = len(LINEAS)
    #print(LINEAS, '<- LINEAS')
    while nLinea < len(LINEAS) and nLinea < fin:
        #print(nLinea, '<- nLinea')
        if contarEspacios(LINEAS[nLinea]) <= identadoClase:
            enClase = False
            identadoClase = -1
        #print(LINEAS, nLinea)
        clasificado = clasificar(LINEAS[nLinea])

        #print('** CLASIFICADO **')
        #print(clasificado, '**')
        #print('** CLASIFICADO **')

        if clasificado == []:
            pass

        else:

            #print(clasificado, '<-- clasificado')
            clasificado = depurarComentarios(clasificado)
            #print(clasificado, '<- depurarComentarios')
            if clasificado == []:
                pass
            
            else:
                clasificado = depurarNotacion(clasificado)
                #print(clasificado, '<- depurarNotacion')

                #print(clasificado, '<- clasificado pre match ****')
                if clasificado == []:
                    pass
                else:
                    match clasificado[0][0]:
                        case 'class':
                            enClase = True
                            identadoClase = contarEspacios(LINEAS[nLinea])
                            clase = clasificado[1][1]

                        case 'def':
                            clasificado[1][2] = 'FUNCRETURN'
                            KeysVars += [clasificado[1][1]]
                            ArgumentosDef = [] # clasificado[3:-2:2]
                            #print(clasificado, '<- clasificado case def')

                            i = 3
                            while i < len(clasificado) - 2:
                                if clasificado[i][0] == ',':
                                    pass
                                elif clasificado[i][0] == '=':
                                    pass
                                elif clasificado[i][2] == 'VAR' and clasificado[i+1][0] == '=':
                                    ArgumentosDef += [[clasificado[i], clasificado[i+2]]]
                                    i += 2
                                elif clasificado[i][2] == 'VAR':
                                    ArgumentosDef += [[clasificado[i], False]]
                                i += 1
                            #print(ArgumentosDef, '<- ArgumentosDef')

                            #print(clasificado)
                            #print(nLinea)
                            fragmentoCodigo, AuxnLinea = seleccionarFragmento(LINEAS, nLinea)
                            #print(fragmentoCodigo, AuxnLinea, '<- fragmentoCodigo, AuxnLinea')
                                           
                            #print(guardar, '<- guardar', clasificado[1][1])

                            if enClase:
                                try:
                                    CLASES[clase] += [(clasificado[1][1], (ArgumentosDef, nLinea))]
                                except KeyError:
                                    CLASES[clase] = [(clasificado[1][1], (ArgumentosDef, nLinea))]

                            else:
                                FUNCIONES[clasificado[1][1]] = (ArgumentosDef, fragmentoCodigo)
                            nLinea = AuxnLinea
                            #print(clasificado, nLinea)
                            #print(FUNCIONES, '<- FUNCIONES def')
                            
                        case 'return':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)
                            #print(clasificado)
                            ultimasCondiciones = [None, None, None, 1, None, clasificado[1:]]
                            #print(ultimasCondiciones, '<- ultimasCondiciones return')
                            return ultimasCondiciones
                            

                        case 'goto':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            #clasificado = ejecutarGeneral(clasificado)
                            nLinea = clasificado[1][1] - 2 # -1 por el quilombo con los índices y -1 (otra vez) xq al final del while se suma 1 a nLinea               

                        case 'for':
                            fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                            #print('FOR:')
                            #print(clasificado)
                            #print(fragmentoCodigo)
                            variablesFor = []
                            for i in clasificado:
                                if i[2] == 'VAR':
                                    variablesFor.append(i[1])
                                elif i[0] == 'in':
                                    break

                            #print(variablesFor, '<- variablesFor')

                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            iterable = clasificado[-2]

                            #print(clasificado)

                            #print(variablesFor)
                            
                            #print(iterable, '<- iterable')

                            #print(fragmentoCodigo)
                            if len(variablesFor) >= 2:
                                if iterable[2] in ('V-lista', 'lista'):
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        for j in range(len(variablesFor)):
                                            VARIABLES[(variablesFor[j], contexto_)] = (variable[1][j][1], variable[1][j][2])
                                        ultimasCondiciones[0] = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1

                                elif iterable[2] == 'str':
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        for j in range(len(variablesFor)):
                                            VARIABLES[(variablesFor[j], contexto_)] = (variable[1][j][1], 'str')
                                        ultimasCondiciones[0] = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1
                                else:
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        for j in range(len(variablesFor)):
                                            VARIABLES[(variablesFor[j], contexto_)] = (variable[1][j][1], variable[1][j][2])
                                        ultimasCondiciones[0] = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1

                            else:
                                if iterable[2] in ('V-lista', 'lista'):
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        VARIABLES[(variablesFor[0], contexto_)] = (variable[1], variable[2])
                                        #print(ultimasCondiciones, '<- ultimasCondiciones pre ejecutarCodigo')
                                        ultimasCondiciones = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)
                                        #print(ultimasCondiciones, '<- ultimasCondiciones l')
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1

                                elif iterable[2] == 'str':
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        VARIABLES[(variablesFor[0], contexto_)] = (variable[1], 'str')
                                        ultimasCondiciones = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1
                                        

                                else:
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        VARIABLES[(variablesFor[0], contexto_)] = (variable[1], variable[2])
                                        ultimasCondiciones = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1

                        case 'foreach':
                            #print(clasificado)

                            fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                            variablesForeach = [i[1] for i in clasificado[1:-3:2] if i[2] == 'VAR']

                            #print(variablesForeach, '<- variablesForeach')

                            for i in range(len(clasificado)-1, -1, -1):
                                if clasificado[i][2] == 'VAR':
                                    nombreIterable = clasificado[i][1]
                                    break

                            #print(clasificado)
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            iterable = clasificado[-2]
                            #print(nombreIterable)
                            #print(iterable, '<- iterable')
                            #print(VARIABLES)
                            #print(variable, '<- variable')
                            #print(variablesForeach)

                            

                            #print(fragmentoCodigo)
                            if len(variablesForeach) >= 2:
                                if iterable[2] in ('V-lista', 'lista'):
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        for j in range(len(variablesForeach)): 
                                            VARIABLES[(variablesForeach[j], contexto_)] = (variable[1][j][1], variable[1][j][2])
                                        ultimasCondiciones = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)

                                        iterable[1][i] = ('CONST', VARIABLES[(variablesForeach[0], contexto_)][0], VARIABLES[(variablesForeach[0], contexto_)][1])

                                        VARIABLES[(nombreIterable, contexto_)] = (iterable[1], 'lista')
                                        #print(ultimasCondiciones)

                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1

                                    #print(iterable)

                                else:
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        for j in range(len(variablesForeach)): 
                                            VARIABLES[(variablesForeach[j], contexto_)] = (variable[1][j][1], variable[1][j][2])
                                        ultimasCondiciones[0] = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)

                                        iterable[1][i] = ('CONST', VARIABLES[(variablesForeach[0], contexto_)][0], VARIABLES[(variablesForeach[0], contexto_)][1])

                                        VARIABLES[(nombreIterable, contexto_)] = (iterable[1], iterable[2])
                                        
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1

                            else:
                                if iterable[2] in ('V-lista', 'lista'):
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        #print(variable)
                                        VARIABLES[(variablesForeach[0], contexto_)] = (variable[1], variable[2])
                                        ultimasCondiciones = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)

                                        iterable[1][i] = ['CONST', VARIABLES[(variablesForeach[0], contexto_)][0], VARIABLES[(variablesForeach[0], contexto_)][1]]
                                        #print(ultimasCondiciones)
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1

                                    #print(iterable)
                                    VARIABLES[(nombreIterable, contexto_)] = (iterable[1], 'lista')

                                elif iterable[2] == 'str':
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        VARIABLES[(variablesForeach[0], contexto_)] = (variable[1], 'str')
                                        ultimasCondiciones = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)

                                        iterable[1][i] = ('CONST', VARIABLES[(variablesForeach[0], contexto_)][0], VARIABLES[(variablesForeach[0], contexto_)][1])
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1
                                    #print(iterable)
                                    #print(iterable[1])
                                        #print(iterable[1])

                                    cadena = ''
                                    for i in iterable[1]:
                                        cadena+=i
                                    iterable = ('CONST', cadena, 'str')
                                    VARIABLES[(nombreIterable, contexto_)] = (str(iterable[1]), 'str')

                                else:
                                    i = 0
                                    while i < len(iterable[1]):
                                        variable = iterable[1][i]
                                        VARIABLES[(variablesForeach[0], contexto_)] = (variable[1], variable[2])
                                        ultimasCondiciones = ejecutarCodigo(fragmentoCodigo[1:], nLinea = 0)

                                        iterable[1][i] = ('CONST', VARIABLES[(variablesForeach[0], contexto_)][0], VARIABLES[(variablesForeach[0], contexto_)][1])
                                        if ultimasCondiciones[2]:
                                            i += 1
                                            ultimasCondiciones[2] = False
                                        elif ultimasCondiciones[3]:
                                            return ultimasCondiciones
                                        elif ultimasCondiciones[0]:
                                            break
                                        else:
                                            i += 1
                                    
                                        #print(VARIABLES)
                                        #print(variable, '<- variable')

                                    VARIABLES[(nombreIterable, contexto_)] = (iterable[1], iterable[2])
                                        
                                    #print(iterable)

                        case 'while':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                            #print(clasificado)
                            ultimasCondiciones[0] = ejecutarMientras(fragmentoCodigo, LINEAS, nLinea)

                            #print(ultimaCondicion, '<- ultimaCondicion')
                        
                        case 'do':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                            #print(clasificado)
                            ultimasCondiciones[0] = ejecutarHaceMientras(fragmentoCodigo, LINEAS, nLinea)
                            #print(ultimaCondicion, '<- ultimaCondicion')s

                        case 'break':
                            ultimasCondiciones[1] = True
                            ultimasCondiciones[0] = False
                            #print(clasificado, '<- clasificado')
                            return ultimasCondiciones

                        case 'continue':
                            ultimasCondiciones[2] = True
                            return ultimasCondiciones

                        case 'if':
                            #print(clasificado, '<- clasificado if')
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            #print(clasificado, '<- clasificado if')
                            if clasificado[1][1]:
                                pass # Se seguirá ejecutando con normalidad

                            else: # La condición es falsa, el número de linea (nLinea) es igual al final del bloque indentado
                                fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                                #print(fragmentoCodigo)
                                #print(nLinea)
                            ultimasCondiciones[4] = clasificado[1][1]
                            #print(clasificado, '<- clasificado if')

                        case 'elif':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            if not ultimasCondiciones[4]:
                                #print(clasificado)
                                clasificado = ejecutarGeneral(clasificado, LINEAS, nLinea) # Se encarga de evaluar la condición hasta hacerla un 'Verdadero' o 'Falso'

                                if clasificado[1][1]:
                                    pass # Se seguirá ejecutando con normalidad

                                else: # La condición es falsa, el número de linea (nLinea) es igual al final del bloque indentado
                                    fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                                    #print(nLinea)
                                ultimasCondiciones[4] = clasificado[1][1]
                                #print(clasificado, '<- clasificado elif')

                            else: # La anterior condición era verdadera, con lo cual este bloque no se ejecuta
                                fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)

                        case 'else':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)
                            #print(clasificado)
                            #print(ultimasCondiciones, '<- ultimasCondicions else')

                            if not ultimasCondiciones[4]:
                                ultimasCondiciones[4] = None

                            else:
                                fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)


                        case 'match':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            ejecutaCase = False
                            #print(clasificado)
                            variablesMatch = [i[1] for i in clasificado[1:-1:2] if i[2] == 'VAR']
                            #print(variablesMatch)
                            i = 0
                            while i < len(variablesMatch):
                                variablesMatch[i] = VARIABLES[(variablesMatch[i], contexto_)][0]
                                i += 1

                        case 'case':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            if not ejecutaCase:
                                constantesCase = [i[1] for i in clasificado[1:-1:2]]
                                #print(variablesMatch, constantesCase)
                                ejecutaCase = True
                                if len(constantesCase) == 1:
                                        if constantesCase[0] == '_':
                                            pass
                                else:
                                    for i, j in enumerate(variablesMatch):

                                        if constantesCase[i] != '_' and constantesCase[i] != j:
                                            ejecutaCase = False
                                            break

                                    if not ejecutaCase:
                                        fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)

                            else:
                                fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)

                        case 'pass':
                            pass

                        case 'import':

                            modulos = [i[1] for i in clasificado[1::2]]
                            for i in modulos:
                                IMPORTADOS += [i]
                                KeysVars += [i]
                                comando = f"python Re_Hasya.py s {i}.hsy"
                                SALIDA = ejecutar_comando_terminal(comando)[-2:]
                                SALIDA[0] = ast.literal_eval(SALIDA[0])
                                #print(SALIDA[0])
                                AUX_VARIABLES = SALIDA[0][0]
                                #print(AUX_VARIABLES)
                                for j in AUX_VARIABLES:
                                    VARIABLES[(f'{i}.{j}', contexto_)] = AUX_VARIABLES[j]
                                    KeysVars += [(f'{i}.{j}', contexto_)]

                                AUX_FUNCIONES = SALIDA[0][1]
                                for j in AUX_FUNCIONES:
                                    FUNCIONES[f'{i}.{j}'] = AUX_FUNCIONES[j]
                                    KeysVars += [f'{i}.{j}']

                            #print(FUNCIONES, '<- FUNCIONES')
                            #print(KeysVars, '<- KeysVars')
                            #print(VARIABLES, '<- VARIABLES')
                            #print(IMPORTADOS, '<- IMPORTADOS')

                        case 'from':
                            #print(clasificado, '<- clasificado')
                            modulo = clasificado[1][1]

                            comando = f"python Re_Hasya.py s {modulo}.hsy"
                            SALIDA = ejecutar_comando_terminal(comando)[-2:]
                            SALIDA[0] = ast.literal_eval(SALIDA[0])

                            if clasificado[-1][1] == '*':
                                SALIDA = ejecutar_comando_terminal(comando)[-2:]
                                SALIDA[0] = ast.literal_eval(SALIDA[0])

                                for i in SALIDA[0][0]:
                                    VARIABLES[(str(i), contexto_)] = SALIDA[0][0][i]
                                    KeysVars += [(str(i), contexto_)]

                                for i in SALIDA[0][1]:
                                    FUNCIONES[str(i)] = SALIDA[0][1][i]
                                    KeysVars += [str(i)]
                            else:
                                contenido = [i[1] for i in clasificado[3::2]]
                                
                                IMPORTADOS += [modulo]
                                KeysVars += [modulo]

                                #print(SALIDA[0][0], '<- SALIDA[0][0]')

                                for i in contenido:
                                    if i in SALIDA[0][0]:
                                        VARIABLES[(str(i), contexto_)] = SALIDA[0][0][i]
                                        KeysVars += [(str(i), contexto_)]
                                    elif i in SALIDA[0][1]:
                                        FUNCIONES[str(i)] = SALIDA[0][1][i]
                                        KeysVars += [str(i)]


                        case 'del':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)
                            #print(clasificado, '<- clasificado del')
                            inter = []
                            for i in clasificado[2][1]:
                                if i[1] != 'Nada':
                                    inter += [i[1]]
                                else:
                                    inter += [None]
                            #print(inter)
                            del VARIABLES[(clasificado[1][1], contexto_)][0][inter[0]:inter[1]:inter[2]]

                        case 'HALT':
                            sys.exit()

                        case _: # No se encontraron estructuras que lleven a bloques identados
                            #print('clasificado ejecutarCodigo')
                            #print(clasificado)
                            ejecutarGeneral(clasificado, LINEAS, nLinea)

        nLinea += 1
    return ultimasCondiciones

def procesarCodigo(codigo):
    codigoProcesado = []
    linea_actual = ""
    parentesis = corchetes = llaves = comentarios = 0

    for linea in codigo.split('\n'):
        linea_actual += linea
        parentesis += linea.count('(') - linea.count(')')
        corchetes += linea.count('[') - linea.count(']')
        llaves += linea.count('{') - linea.count('}')
        comentarios += linea.count('#/') - linea.count('/#')

        if parentesis == corchetes == llaves == comentarios == 0:
            codigoProcesado.append(linea_actual)
            linea_actual = ""

    if linea_actual:  # Por si queda alguna línea sin procesar
        codigoProcesado.append(linea_actual)

    return codigoProcesado

### ERRORES ### (convención: True si cumple con lo esperado, False si hay un error)

def Wagner_Fischer(p1, p2):
    len_p1, len_p2 = len(p1), len(p2)
    
    if len_p1 > len_p2:
        p1, p2 = p2, p1
        len_p1, len_p2 = len_p2, len_p1

    fila_actual = range(len_p1 + 1)

    for i in range(1, len_p2 + 1):
        fila_anterior, fila_actual = fila_actual, [i] + [0] * len_p1

        for j in range(1, len_p1 + 1):
            insertar, borrar, cambiar = fila_anterior[j] + 1, fila_actual[j-1] + 1, fila_anterior[j-1]

            if p1[j-1] != p2[i-1]:
                cambiar += 1
            fila_actual[j] = min(insertar, borrar, cambiar)

    return fila_actual[len_p1]

def SugerenciasWF(palabra, diccionario, corte: int = 10):
    sugerencias = []

    for palabra_correcta in diccionario:
        distancia = Wagner_Fischer(palabra, palabra_correcta)
        sugerencias.append((palabra_correcta, distancia))

    sugerencias.sort(key=lambda x: x[1])
    i = 0
    pS = list(sugerencias[0])
    while i < len(sugerencias):
        sugerencias[i] = list(sugerencias[i])
        if sugerencias[i][1] > corte:
            sugerencias = sugerencias[0:i]
            break

        sugerencias[i][1] = corte - sugerencias[i][1] + 1
        i += 1
    #print(sugerencias)
    #print(pS)
    
    if not sugerencias:
        
        pS[1] = corte - pS[1] + 2
        return pS
    
    return sugerencias[0]

def comprobarIdentacion(LINEAS: list, nLinea: int) -> int:
    clasificado = clasificar(LINEAS[nLinea])
    #print(clasificado, '<- comprobarIdentacion')
    if len(clasificado):
        if clasificado[0][0] in aIdentar:
            #print(clasificado, aIdentar, clasificado[0][0] in aIdentar)
            if comprobarIdentacionAct(LINEAS, nLinea) == 1:
                return 0 # No hay error, puesto que el nivel de aumentado va a subir
            else:
                return 3 # Codigo de error
        else:
            return 0
    else: 
        return 0
    
def ExisteProximaLinea(LINEAS: list, nLinea: int) -> bool:
    if nLinea + 1 < len(LINEAS):
        #print('Existe prox')
        return True
    else:
        #print('No existe prox')
        return False
    
def ComprobarComentarios(clasificado: list) -> int | bool:
    ...
    """ 
    if bien: return 0
    else: return 6
    """
def ComprobarNotacion(clasificado: list) -> int | bool:
    ...
    """
    if bien: return 0
    else return 6 
    """
    
def ComprobarSintaxis(clasificado: list, Est: str | None = None) -> int | bool:
    if Est == None: # Se analiza la una linea cualquiera
        ...
    elif Est == 0: # Detectar automáticamente
        Est = clasificado[0][0]
    else: # Ya nos dan la estructura 
        pass

    if Est is None:
        ...
    else:
        match Est:
            case 'def':
                ...
            case 'return':
                ...
            case 'goto':
                ...
            case 'for':
                ...
            case 'foreach':
                ...
            case 'while':
                ...
            case 'do':
                ...
            case 'break':
                ...
            case 'if':
                ...
            case 'elif':
                ...
            case 'else':
                ...
            case 'match':
                ...
            case 'case':
                ...
            case 'pass':
                ...
            case 'import':
                ...
            case 'from':
                ...
            case 'HALT':
                ...
            case _:
                ...

    return 1

def ServirErrores(ERROR: int, LINEAS: list, nLinea: int, i: int) -> bool:
    clasificado = clasificar(LINEAS[nLinea])
    if ERROR != 0:
        print('\nERROR')
        print('*'*73, '', sep='\n')
        print(f"Tipo de error: {ERROR} | Linea: {nLinea + 1}")
        match ERROR:
            case 1:
                ... # Sintaxis
            case 2:
                print(clasificado, i)
                print(f"\"{clasificado[i][1]}\" No se encuentra definido.")
                Mug = SugerenciasWF(clasificado[i][1], KeysVars)
                #print(Mug)
                Sug = Mug[0]
                TipoSug = (clasificar(Sug))[0][2]
                CertezaSug = Mug[1]
                match TipoSug:
                    case 'VAR':
                        TipoSug = 'variable'

                    case 'TOK':
                        TipoSug = 'palabra reservada'

                    case 'FUNC' | 'FUNCRETURN':
                        TipoSug = 'función'
                    
                print(f"¿Querrá escribir \"{Sug}\" ( {TipoSug} ) ? Certeza: [{CertezaSug}/10]")

            case 3:
                if ERROR == 3:
                    print(f"Se esperaba un bloque identado despues de la estructura \"{clasificado[0][1]}\".")
            case 4:
                ...
            case 5:
                ...
            case 6:
                ...
        print(f'{nLinea + 1} | {LINEAS[nLinea]}')
        return True
    return False

def ComprobarErrores(LINEAS: list, nLinea: int = 0) -> bool:
    """
    Primero comprueba los diferentes tipos de errores a ver si existe alguno
    Al primero que vea, lo ejecuta y se cierra la función   
    """

    while nLinea < len(LINEAS):
        clasificado = clasificar(LINEAS[nLinea])
        ERROR = ComprobarComentarios(clasificado)
        ERROR = ComprobarNotacion(clasificado)
        if ERROR:
            return ERROR
        clasificado = depurarComentarios(clasificado)
        clasificado = depurarNotacion(clasificado)
        ERROR = 0
        if ExisteProximaLinea(LINEAS, nLinea):
            #print(nLinea, LINEAS[nLinea])
            ERROR  = comprobarIdentacion(LINEAS, nLinea)
            #print(ERROR, '<- comprobar Idetancion')

        if ERROR:
            ERROR = ServirErrores(ERROR, LINEAS, nLinea, 0)
            return ERROR
        nLinea += 1
    return False

### EJECUCIÓN ###

def EJECUTAR(archivo):
    with open(rf"{archivo}", "r", encoding="utf-8") as CODIGO:
        #print('casi pre main')
        LINEAS = CODIGO.read()
        CODIGO_PROCESADO = procesarCodigo(LINEAS)
        
        #print(CODIGO_PROCESADO)

        
        ERROR = False
        ERROR = ComprobarErrores(CODIGO_PROCESADO)
        #print(ERROR, '<- ERROR')

        if not ERROR:
            ejecutarCodigo(CODIGO_PROCESADO, nLinea=0)

        #Errores(ERRORES, CODIGO_PROCESADO)

        #for i in CODIGO_PROCESADO:
        #   if i != '': print('>>>', i)
        #print('VARIABLES:')
        #print(VARIABLES)

def main(archivo: __file__):
    #try:
        EJECUTAR(archivo)

    #except FileNotFoundError:
     #   print(f"El archivo {archivo} no se encuentra.")

def ejecutar_comando_terminal(comando: str):
    proceso = subprocess.run(comando, shell=True, check=False, text=True, stdout=subprocess.PIPE)
    #print(proceso.stdout.split('\n'))
    return proceso.stdout.split('\n')

if __name__ == "__main__":
    #print(sys.argv)

    if len(sys.argv) == 1:
        archivo1 = "Hasya.hsy"
        contenido1 = main(archivo1)

    elif len(sys.argv) == 2:
        archivo1 = sys.argv[1]
        contenido1 = main(archivo1)

    elif len(sys.argv) == 3 and sys.argv[1] == "s":
        archivo2 = sys.argv[2]
        contenido2 = main(archivo2)
        #print(VARIABLES)
        VARIABLES2 = {}
        for i in VARIABLES.keys():
            VARIABLES2.setdefault(i[0], VARIABLES[i])
        print(json.dumps([VARIABLES2, FUNCIONES]))

#print(KeysVars)
#print(CLASES)
#print(VARIABLES)
