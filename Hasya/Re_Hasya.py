"""
Variables:
['CONST', NOMBRE, 'VAR']

Constantes:
['CONST', VALOR, TIPO DE DATO]

Símbolos y por menores:
[VALOR EN tok, VALOR ESCRITO, 'TOK']

Funciones con return:
[VALOR EN funcReturn, VALOR ESCRITO, 'FUNCRETURN']

Funciones sin return:
[VALOR EN func, VALOR ESCRITO, 'FUNC']

Métodos:
[VALOR ESCRITO, VALOR EN METODOS, 'METD']

"""

import sys
import subprocess
import json

import ast
import re
from Re_Reservadas import *

d = combinar(combinar(tok, metodos), combinar(func, funcReturn))
KeysVars = [i for i in d if re.match(r"[a-zA-Z]", i)]

VARIABLES = { # NOMBRE: (VALOR, TIPO DE DATO)

}


FUNCIONES = { # NOMBRE: (ARGUMENTOS, LINEA_DONDE_INICIA, LINEA_DONDE_TERMINA)

}

IMPORTADOS = []

nLinea = 0

ERRORES_ = [] # Lista de tuplas ('HYS', nLinea)


estructuras_primarias = { # Estructuras irreducibles

    (): 'LINEA_VACIA',
    ('CONST',): 'CONSTANTE',

    ('print', '(', 'CONST', ')',): 'MOSTRAR',
    ('CONST', '=', 'CONST',): 'ASIGNAR',

    ('CONST', '+=', 'CONST',): 'SUMARLE',
    ('CONST', '-=', 'CONST',): 'RESTARLE',
    ('CONST', '*=', 'CONST',): 'MULTIPLICARLE',
    ('CONST', '/=', 'CONST',): 'DIVIDIRLE',
    ('CONST', '**=', 'CONST',): 'ELEVARLE',

    ('if', 'CONST', ':',): 'if',
    ('elif', 'CONST', ':',): 'elif',
    ('else', ':',): 'else',

    ('while', 'CONST', ':',): 'while',

    ('for', 'CONST', 'in', 'CONST', ':',): 'for',
    ('foreach', 'CONST', 'in', 'CONST', ':',): 'foreach',

    ('goto', 'CONST',): 'goto',

    ('return', 'CONST',): 'return',

    ('match', 'CONST', ':',): 'match',
    ('case', 'CONST', ':',): 'case',


}

estructuras_secundarias = { # Estructuras reduccibles a otras

    ('CONST', '.', 'METD',): 'METODO',

    ('CONST', 'for', 'CONST', 'in', 'CONST', ): 'forComp',
}

estructuras_notacion = { # Estructuras que puede usar el usuario para aclarar ciertas situaciones, pero que serán eliminadas de clasificado ya que no aportan nada

    (':', 'tipo',): 'CONSTANTE_ACLARADA',
    ('-', '>', 'tipo',): 'FUNCION_ACLARADA',

}

tipos_de_variables = ( # Tipos de variables en general

    'str', 
    'list',
    'int', 
    'float',
    'complex', 

    'tipo'
    'sintipo'

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
    '**='

)

iterables = ( # Tipos de dato sobre los cuales se puede iterar

    'list',
    'str'

)

aIdentar = ( # Palabras clave que lleven si o si a bloques identados (descontando la compresión)

    'for',
    'while',
    'each',

    'if',
    'elif',
    'else',

    'match',
    'case',

    'def',

)

keys_de_tok = '|'.join(re.escape(i) for i in tok.keys())

def hayLista(texto: str, ini: str = '[', fini: str = ']') -> bool:
    nivel = 0
    inicio = None
    for char in texto:
        if char == ini:
            nivel += 1
            inicio = True
        elif char == fini:
            nivel -= 1
            if nivel == 0 and inicio is not None:
                return True
    return False

def capturarLista(texto: str, ini: str = '[', fini: str = ']') -> list:
    indices = []
    nivel = 0
    inicio = None

    for i, char in enumerate(texto):
        if char == ini:
            if nivel == 0:
                inicio = i
            nivel += 1
        elif char == fini:
            nivel -= 1
            if nivel == 0 and inicio is not None:
                indices.append((inicio, i + 1))
                inicio = None

    return indices

def procesarLista(texto: str, ini: str = '[', fini: str = ']') -> list:
    """
    Procesa una lista dada en formato de cadena, eliminando espacios innecesarios y tokenizando los elementos internos.
    """
    #print(f'procesarLista: {texto = }')

    elementos = []
    nivel = 0
    elemento_actual = ''

    for char in texto:
        if char == ini:
            if nivel > 0:
                elemento_actual += char
            nivel += 1
        elif char == fini:
            nivel -= 1
            if nivel > 0:
                elemento_actual += char
            elif nivel == 0 and elemento_actual:
                elementos.append(elemento_actual.strip())
                elemento_actual = ''
        elif char == ',' and nivel == 1:
            if elemento_actual:
                elementos.append(elemento_actual.strip())
                elemento_actual = ''
        elif nivel > 0:
            elemento_actual += char

    if elemento_actual:  # Para manejar el caso donde no hay comas al final de la lista
        elementos.append(elemento_actual.strip())

    #print(elementos, '<- elementos procesados')
    tokens = []
    for elemento in elementos:
        clasi = clasificar(elemento)
        if len(clasi) >= 2:
            for c in clasi:
                tokens.append(c)
        else:
            tokens.append(clasi[0])
    #tokens = [clasificar(elemento) for elemento in elementos]
    #print(tokens, '<- tokens generados')

    return tokens

def procesarDict(texto: str, ini: str = '{', fini: str = '}') -> list:
    diccionario = []
    item = []
    lista = texto.split(',')

    lista[0] = lista[0][1:]
    lista[-1] = lista[-1][:-1]

    i = 0
    while i < len(lista):
        temp = clasificar(lista[i])

        item.append(temp[0])
        item.append(temp[-1])

        diccionario += [item]
        item = []
        i += 1

    return diccionario

def condiClasificar(coincidencia: str, identificadas: list) -> list:

    if re.match(r"'([^']*)'", coincidencia):  
        identificadas.append(['CONST', coincidencia[1:-1], 'str'])

    elif re.match(r'\d*\.?\d+j$', coincidencia):  # Números complejos
        identificadas.append(['CONST', complex(coincidencia), 'complex'])

    elif re.match(r'-*\d+\.?\d*$', coincidencia):  # Números
        if '.' in coincidencia:
            identificadas.append(['CONST', float(coincidencia), 'float'])
        else:
            identificadas.append(['CONST', int(coincidencia), 'int'])

    elif coincidencia in ('Verdadero', 'Falso'):  # Booleanos
        identificadas.append(['CONST', 1 if coincidencia == 'Verdadero' else 0, 'int'])

    elif coincidencia == 'Nada':  # None
        identificadas.append(['CONST', 'Nada', 'sintipo'])

    elif coincidencia in ('int', 'float', 'complex', 'str', 'list', 'tuple', 'dict', 'set', 'bool'):
        identificadas.append(['tipo', coincidencia, 'tipo'])

    elif re.match(r'{(.:.)+(,.:.)*}', coincidencia):
        items_dict = procesarDict(coincidencia)
        identificadas.append(['CONST', items_dict, 'dict'])

    elif re.match(r'{.*\}', coincidencia):
        elementos_conj = procesarLista(coincidencia[0:-1])
        identificadas.append(['CONST', elementos_conj, 'set'])

    elif coincidencia in tok:  # Aca entra casi todo
        identificadas.append([tok[coincidencia], coincidencia, 'TOK'])

    elif coincidencia in func: # Funciones
        identificadas.append([func[coincidencia], coincidencia, 'FUNC'])

    elif coincidencia in funcReturn: # Funciones con return
        identificadas.append([funcReturn[coincidencia], coincidencia, 'FUNCRETURN'])

    elif coincidencia in metodos:  # Métodos
        identificadas.append([coincidencia, metodos[coincidencia], 'METD'])

    elif coincidencia in FUNCIONES:
        identificadas.append([coincidencia, coincidencia, 'FUNCRETURN'])

    elif re.match(r'[\.A-Za-z_]\w*', coincidencia):
        if coincidencia == '_':
            identificadas.append(['CONST', coincidencia, 'CUALQR'])
        else:
            identificadas.append(['CONST', coincidencia, 'VAR'])

    else:
        hayL = hayLista(coincidencia)
        if hayL:
            #print('coincidencia:', coincidencia, sep='\n')

            indices = capturarLista(coincidencia)

            for i, j in indices:
                #print(i, j)
                elementos_lista = procesarLista(coincidencia[i:j])
                #print(elementos_lista, '<- elementos_lista')
                identificadas.append(['CONST', elementos_lista, 'list'])
                #print(coincidencias, coincidencia, (iteracion), '<- cci')

        else:
            print(f"{coincidencia = } <- COINCIDENCIA NO CLASIFICADA")
            print(identificadas)
            sys.exit()

    return identificadas

def clasificar(texto: str) -> list:
    """
    clasificar toma como entrada un texto la/s linea/s en cuestión y 
    la/s convierte en una serie de tokens para ser procesados posteriormente.
    En esencia, clasificar es un Lexer.
    """
    identificadas = [] # identificadas = clasificado, pero no lo cambiemos porque me gusta como queda
    patron = rf'(\[.*\]|["\'].*?["\']|\(.*?,\)|\{{.*?\}}|:{keys_de_tok}|[A-Za-z0-9_][A-Za-z_]*[\.A-Za-z_0-9]*|\d*\.?\d+j|-?\d+\.?\d*|Verdadero|Falso|Nada)'

    coincidencias = re.findall(patron, texto)
    #print(f'{texto = }')
    #print('coincidencias: ', coincidencias)
    for iteracion, coincidencia in enumerate(coincidencias):
        #print(coincidencia, '<- coincidencia')
        try: 
            identificadas = condiClasificar(coincidencia, identificadas)
        except TypeError:
            coincidencia = coincidencia[0]
            identificadas = condiClasificar(coincidencia, identificadas)

        
        #print(identificadas[-1], '<-- COINCIDENCIA DETECTADA')

    #print(identificadas, '<- clasificar return')
    return identificadas

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
        if clasificado[i][2] in tipos_de_variables or clasificado[i][2] == 'VAR':
            resumido += 'C'

        elif clasificado[i][2] == 'TOK':
                resumido += clasificado[i][1]

        elif clasificado[i][2] == 'tipo':
            resumido += 'T'

        elif clasificado[i][2] == 'sintipo':
            resumido += 'S'

        elif clasificado[i][2] == 'FUNC':
            resumido += 'Fn'

        elif clasificado[i][2] == 'FUNCRETURN':
            resumido += 'Fr'

        elif clasificado[i][0] == 'METD':
            resumido += 'M'

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

def reemVariables(clasificado: list, LINEAS: list, nLinea: int, VARIABLES: dict = VARIABLES) -> list:
    #print('VARIABLES:', VARIABLES, sep='\n')
    #print(clasificado, '<- clasificado reemVariables')
    i = 0
    while i < len(clasificado):
        Rp = False
        
        if clasificado[i][2] == 'VAR':
            Rp = True
            if i+1 < len(clasificado):
                if clasificado[i+1][1] in asignadores:
                    Rp = False

            if clasificado[0][0] == 'for':
                if clasificado[i-1][0] != 'in':
                    Rp = False

            if clasificado[0][0] == 'foreach':
                if clasificado[i-1][0] != 'in':
                    Rp = False

            if clasificado[0][0] == 'import':
                Rp = False
            if clasificado[0][0] == 'from':
                Rp = False
            if clasificado[0][0] == 'match':
                Rp = False
            if clasificado[0][0] == 'def':
                Rp = False

        elif clasificado[i][2] == 'list':
            clasificado[i] = ['CONST', reemVariables(clasificado[i][1], LINEAS, nLinea), 'list']

        #print(i, '<- i', Rp)

        if Rp:
            #print(VARIABLES)
            #print(clasificado, i)
            if clasificado[i][1] not in VARIABLES:
                #print(LINEAS, nLinea, 'AAA')
                if clasificado[i][1] in KeysVars:
                    pass
                else:
                    ServirErrores(2, LINEAS, nLinea, i)
                    sys.exit()
            else:
                clasificado[i] = ['CONST', VARIABLES[clasificado[i][1]][0], VARIABLES[clasificado[i][1]][1]]
            #print(clasificado, i)
        i += 1
    #print(clasificado, '<- reemVariables return')
    return clasificado

def enFuncion(LINEAS: list, nLinea: int) -> bool:
    #print('FUNCIONES:', FUNCIONES)
    nivel = 0
    for _, i, j in FUNCIONES.values():
        print(i, j)
        if nLinea in range(i, j):
            nivel += 1

    return nivel, nLinea+1

def idenConjunto(clasificado: str) -> list:
    i = 0
    while i < len(clasificado):
        ...

def evalFuncionesR(clasificado: list, LINEAS: list) -> list:
    #print(clasificado, '<- clasificado evalFuncionesR')

    i = 0
    parejas = asignarP(clasificado)
    copiaclasificado = clasificado.copy()
    #print(copiaclasificado)
    eliminar = []
    while i < len(copiaclasificado):
        #print(i, '<- i') 
        if copiaclasificado[i][2] == 'FUNCRETURN':
            #print('data:')
            j = parejas[i+1]
            #print(copiaclasificado, i, j, sep='\n')
            seudoclasificado = copiaclasificado[i+2:j]
            #print(seudoclasificado, '<- seudoclasificado')
            copiaclasificado[i+2:j] = evalExpresiones(seudoclasificado, LINEAS)
            #print(copiaclasificado, '<- copiaclasificado')
            parejas = asignarP(copiaclasificado)
            j = parejas[i+1] # j = indice donde se encuentra el ) de la función
            #print(copiaclasificado, i, '<- copiaclasificado, i')
            if copiaclasificado[i][1] in FUNCIONES: # FUNCIONES contiene exclusivamente las funciones que haya definido el usuario
                #print(copiaclasificado, i, '<- FUNCIONES')

                ArgumentosCall = []
                for k in copiaclasificado[i+2:j:2]:
                    ArgumentosCall += [k]
                #print(ArgumentosCall, '<- ArgumentosCall')
                ArgumentosFunc = FUNCIONES[copiaclasificado[i][1]][0][0]
                #print(ArgumentosFunc, '<- ArgumentosFunc')
                for k in range(len(ArgumentosFunc)):
                    VARIABLES[ArgumentosFunc[k][1]] = (ArgumentosCall[k][1], ArgumentosCall[k][2])
                #print(VARIABLES)

                inicio = FUNCIONES[copiaclasificado[i][1]][1]
                fin = FUNCIONES[copiaclasificado[i][1]][2]
                #print(LINEAS, inicio, fin)
                #print(LINEAS[inicio:fin+2], '<- ejecuta')
                retorno = ejecutarCodigo(LINEAS[inicio:fin+2])
                #print(retorno, '<- retorno')
                if retorno == 0:
                    copiaclasificado[i] = ['CONST', 'Nada', 'sintipo']
                else:
                    copiaclasificado[i] = retorno[0]
                    
                #print(copiaclasificado, i, '<- copiaclasificado, i')

            else:
                match copiaclasificado[i][0]:
                    case 'input':
                        if j - i == 2:
                            copiaclasificado[i] = ['CONST', f'{input()}', 'str']

                        elif j - i == 3:
                            copiaclasificado[i] = ['CONST', f'{input(copiaclasificado[i+2][1])}', 'str']

                    case 'len':
                        copiaclasificado[i] = ['CONST', len(copiaclasificado[i+2][1]), 'int']

                    case 'reversed':
                        copiaclasificado[i] = ['CONST', list(reversed(copiaclasificado[i+2][1])), copiaclasificado[i+2][2]]

                    case 'range':
                        #print(copiaclasificado, j, i, '<- copiaclasificado, j, i')
                        if j - i == 3:
                            copiaclasificado[i] = clasificar(str(list(range(int(copiaclasificado[i+2][1])))))[0]
                        elif j - i == 5:
                            copiaclasificado[i] = clasificar(str(list(range(int(copiaclasificado[i+2][1]), int(copiaclasificado[i+4][1])))))[0]

                        elif j - i == 7:
                            copiaclasificado[i] = clasificar(str(list(range(int(copiaclasificado[i+2][1]), int(copiaclasificado[i+4][1]), int(copiaclasificado[i+6][1])))))[0]
                    case 'list':
                        copiaclasificado[i] = clasificar(str(list(copiaclasificado[i+2][1])))[0]

                    case 'matrix':
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

                    case 'enumerate':
                        ...
                    case 'all':
                        ...
                
            eliminar.append((i+1, j+1)) # Se agregan los índices desde el ( hasta el ) para después eliminarlos
            i = j + 1# i Se actualiza para valer el indice donde esta el ) de la función que se evaluo

        elif copiaclasificado[i][2] == 'METD':
            ...
        i += 1 # Y se le agrega 1

    for i, j in reversed(eliminar): # Se elimina del final al principio para "borrar la basura"
        #print(i, j)
        del copiaclasificado[i:j]

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

            """ elif clasificado[i][2] in ('FUNC', 'METD', 'FUNCRETURN'):
            #print('func, metd, o funcretrun', i)
            if inicio is False:
                inicio = i
                fin = False"""

        elif clasificado[i][0] in comparadores:
            #print('comparadores', i)
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

    # Funciones con return
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
            elif clasificado[j][2] == 'list':
                subexpresion += str(procesarListaAnidada(clasificado[j][1]))
            elif clasificado[j][0] in comparadores:
                hayComp = True
                subexpresion += str(clasificado[j][0])
            else:
                subexpresion += str(clasificado[j][1])
            j += 1
        #print(clasificado, i, '<- clasificado, i ***')
        #print(f'{subexpresion = }')
        """
        Aca debería ir nuestra propia función para evaluar propiamente las expresiones
        """
        res = eval(subexpresion)
        #print(res, '<- res')
        
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
            clasificado[expresiones[i][0]] = tuple(('CONST', resultados[i][0], 'str'))
        elif resultados[i][2]: # Si hay comparadores
            clasificado[expresiones[i][0]] = tuple(('CONST', int(resultados[i][0]), 'int'))
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
    if isinstance(lista, list):
        return '[' + ','.join(procesarListaAnidada(elem[1]) for elem in lista) + ']'
    else:
        return repr(lista)

def imprimir_lista(lista):
    if isinstance(lista, list):
        return '[' + ', '.join(imprimir_lista(item[1]) for item in lista) + ']'
    else:
        return str(lista)

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
    for e in EN:
        n = len(e)
        i = 0
        while i < len(clasificado):
            seudoclasificado = tuple([j[0] for j in clasificado[i:i+n]])
            if seudoclasificado == e:
                del clasificado[i:i+n]
                i -= 1
            i += 1
    return clasificado

def ejecutarGeneral(clasificado: list, LINEAS: list, nLinea, ES: dict = estructuras_secundarias, EP: dict = estructuras_primarias):
    """"
        Toma como entrada una linea clasificada y evalúa las estructuras que tenga dentro a excepción de las que lleven a
        bloques identados y cuestiones que necesiten un enfoque aparte y mas robusto (ubicado en ejecutarCodigo)
    """
    global VARIABLES, KeysVars
    #print(clasificado, '<- clasificado ejecutarGeneral')

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
                        clasificado[i] = ['CONST', resultado, 'list']
                    case 'METODO':

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
                            case 'list':
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

    #print(clasificado, '<- clasificado')
    directiva = [] # directiva es el primer elemento de cada elemento en clasificado
    #print(clasificado)
    expresion = ''

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
        print(clasificado, '<- clasificado de sintaxis')
        print(directiva)
        sys.exit()
    #print(ejecutar, '<- ejecutar')

    match ejecutar:
        case 'LINEA_VACIA':
            pass

        case 'MOSTRAR':
            #print('MOSTRAR:')
            #print(clasificado)
            if len(clasificado) == 3:
                    print() 
            else:
                for j in range(2, len(clasificado)):
                    #print(clasificado, j, '<- clasificado, j')
                    match clasificado[j][2]:
                        case 'str':
                            print(clasificado[j][1], end=' ')
                        case 'int':
                            print(clasificado[j][1], end=' ')
                        case 'float':
                            print(clasificado[j][1], end=' ')
                        case 'complex':
                            print(clasificado[j][1], end=' ')
                        case 'list':
                            print(imprimir_lista(clasificado[j][1]), end=' ')
                        case 'bool':
                            print(clasificado[j][1], end=' ')
                        case 'sintipo':
                            print(clasificado[j][1], end=' ')
                        case 'TOK':
                            if clasificado[j][1] not in ('(', ',', ')'):
                                print(clasificado[j][1], end=' ')
                        case _:
                            #print(clasificado, j, '<- clasificado, j MOSTRAR')
                            ...

            print()

        case 'ASIGNAR':
            #print(clasificado, '<- clasificado ASIGNAR')

            if len(clasificado) > 3:
                expresion = ''
                for i in range(2, len(clasificado)):
                    if clasificado[i][2] == 'str':
                        expresion += f"'{clasificado[i][1]}'"

                    elif clasificado[i][2] == 'int':
                        expresion += str(clasificado[i][1])

                    elif clasificado[i][2] == 'float':
                        expresion += str(clasificado[i][1])

                    elif clasificado[i][2] == 'complex':
                        expresion += str(clasificado[i][1])

                    elif clasificado[i][2] == 'list':
                        expresion += str(clasificado[i][1])

                    else:
                        expresion += clasificado[i][1]

            obj2 = clasificado[-1][1]
            tipo = clasificado[-1][2]           
            """try:
                if negativo: obj2 = - obj2
            except UnboundLocalError:
                pass"""


            VARIABLES[clasificado[0][1]] = (obj2, tipo)

            KeysVars += [clasificado[0][1]]

            #print(clasificado, '<- clasificado ejecutarGeneral')
            #print('VARIABLES:', VARIABLES, sep='\n')

        case 'SUMARLE':
            VARIABLES.update({clasificado[0][1]: (VARIABLES[clasificado[0][1]][0] + clasificado[2][1], VARIABLES[clasificado[0][1]][1])})

        case 'RESTARLE':
            VARIABLES.update({clasificado[0][1]: (VARIABLES[clasificado[0][1]][0] - clasificado[2][1], VARIABLES[clasificado[0][1]][1])})

        case 'MULTIPLICARLE':
            VARIABLES.update({clasificado[0][1]: (VARIABLES[clasificado[0][1]][0] * clasificado[2][1], VARIABLES[clasificado[0][1]][1])})


        case 'DIVIDIRLE':
            VARIABLES.update({clasificado[0][1]: (VARIABLES[clasificado[0][1]][0] / clasificado[2][1], VARIABLES[clasificado[0][1]][1])})


        case 'ELEVARLE':
            VARIABLES.update({clasificado[0][1]: (VARIABLES[clasificado[0][1]][0] ** clasificado[2][1], VARIABLES[clasificado[0][1]][1])})


        case 'while' | 'if' | 'elif' | 'else' | 'for' | 'foreach' | 'CONSTANTE' | 'goto':
            pass

        case _:
            print('ejecutarGeneral >> case _:')
            print(clasificado)
            resumido = resumir(clasificado)
            if re.match(r"C(,C)*=C(,C)*", resumido):
                print('Múltiple asignación')

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
    #print(fragmentoCodigo)
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
    condicion = ejecutarGeneral(clasificar(fragmentoCodigo[0]), LINEAS, nLinea)
    while condicion[1][1]:
        if ejecutarCodigo(fragmentoCodigo[1:]):
            break
        condicion = ejecutarGeneral(clasificar(fragmentoCodigo[0]), LINEAS, nLinea)
    #print(condicion, '<- condicion')
    return condicion[1][1]

def ejecutarCodigo(LINEAS: list, nLinea: int = 0):
    global IMPORTADOS, KeysVars
    ultimaCondicion = None

    #print(LINEAS, '<- LINEAS')
    while nLinea < len(LINEAS):
        #print(nLinea, '<- nLinea')

        clasificado = clasificar(LINEAS[nLinea])
        #print('En función: ', enFuncion(LINEAS, nLinea))

        #print('** CLASIFICADO **')
        #print(clasificado)
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

                #print(clasificado, '<- clasificado pre match ***')
                if clasificado == []:
                    pass
                else:
                    match clasificado[0][0]:
                        case 'def':
                            clasificado[1][2] = 'FUNCRETURN'
                            ArgumentosDef = [clasificado[3:-2:2]]
                            #print(clasificado)
                            #print(ArgumentosDef)
                            #print(nLinea)
                            fragmentoCodigo, AuxnLinea = seleccionarFragmento(LINEAS, nLinea)
                            #print(fragmentoCodigo)
                            FUNCIONES[clasificado[1][1]] = (ArgumentosDef, nLinea, len(fragmentoCodigo)-2 + nLinea)
                            nLinea = AuxnLinea
                            #print(clasificado, nLinea)
                            #print(FUNCIONES)
                            
                        case 'return':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            #print(clasificado, '<- clasificado return')
                            return clasificado[1:]    
                            #print(fragmentoCodigo, nLinea)

                        case 'goto':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            #clasificado = ejecutarGeneral(clasificado)
                            nLinea = clasificado[1][1] - 2 # -1 por el quilombo con los índices y -1 (otra vez) xq al final del while se suma 1 a nLinea

                        case 'for':
                            fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                            #print('FOR:')
                            #print(clasificado)
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
                                if iterable[2] == 'list':
                                    for i, variable in enumerate(iterable[1]): # variable = (('CONST', bla bla, 'iterable'), ('CONST', bla bla, 'iterable'))
                                        #print(VARIABLES)
                                        #print(variable, '<- variable')
                                        #print(i, '<- i')
                                        for j in range(len(variablesFor)): 
                                            #print(variable[1], '<- variable[1]')
                                            #print(j, '<- j')

                                            VARIABLES[variablesFor[j]] = (variable[1][j][1], variable[1][j][2])
                                            #print('VAR->', VARIABLES[variablesFor[j]])

                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break

                                else:
                                    for variable in iterable[1]:
                                        #print(VARIABLES)
                                        #print(variable, '<- variable')
                                        for i in range(len(variablesFor)):
                                            #print(i)
                                            VARIABLES[variablesFor[i]] = (variable[i][1], variable[i][2])
                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break

                            else:
                                if iterable[2] == 'list':
                                    for variable in iterable[1]:
                                        #print(VARIABLES)
                                        #print(variable, '<- variable')
                                        VARIABLES[variablesFor[0]] = (variable[1], variable[2])

                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break
                                elif iterable[2] == 'str':
                                    for variable in iterable:
                                        VARIABLES[variablesFor[0]] = (variable, 'str')
                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break
                                else:
                                    for variable in iterable[1]:
                                        #print(VARIABLES)
                                        #print(variable, '<- variable')
                                        VARIABLES[variablesFor[0]] = (variable[1], variable[2])
                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break

                        case 'foreach':
                            #print('pre eval FOREACH:')
                            #print(clasificado)

                            fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                            variablesForeach = [i[1] for i in clasificado[1:-3:2] if i[2] == 'VAR']

                            #print(variablesForeach, '<- variablesForeach')


                            nombreIterable = clasificado[-2][1]

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
                                if iterable[2] == 'list':

                                    for i, variable in enumerate(iterable[1]): 
                                        #print(variable, '<- variable')

                                        #print(i, '<- i')
                                        for j in range(len(variablesForeach)): 

                                            #print(j, '<- j')

                                            VARIABLES[variablesForeach[j]] = (variable[1][j][1], variable[1][j][2])
                                            #print('VAR ->', f'{variablesForeach[j]} : {VARIABLES[variablesForeach[j]]}')

                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break
                                        #print('VI:', VARIABLES[nombreIterable][0])
                                        #print(i, '<- i')

                                        reemplazar = []
                                        for j in range(len(variablesForeach)):
                                            reemplazar.append(('CONST', VARIABLES[variablesForeach[j]][0], VARIABLES[variablesForeach[j]][1]))

                                        VARIABLES[nombreIterable][0][i][1] = reemplazar.copy()


                                else:
                                    for i, variable in enumerate(iterable[1]): 
                                        #print(variable, '<- variable')

                                        #print(i, '<- i')
                                        for j in range(len(variablesForeach)): 

                                            #print(j, '<- j')

                                            VARIABLES[variablesForeach[j]] = (variable[1][j][1], variable[1][j][2])
                                            #print('VAR ->', f'{variablesForeach[j]} : {VARIABLES[variablesForeach[j]]}')

                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break
                                        #print('VI:', VARIABLES[nombreIterable][0])
                                        #print(i, '<- i')

                                        reemplazar = []
                                        for j in range(len(variablesForeach)):
                                            reemplazar.append(('CONST', VARIABLES[variablesForeach[j]][0], VARIABLES[variablesForeach[j]][1]))

                                        VARIABLES[nombreIterable][0][i][1] = reemplazar.copy()

                            else:
                                if iterable[2] == 'list':
                                    for i, variable in enumerate(iterable[1]):
                                        VARIABLES[variablesForeach[0]] = (variable[1], variable[2])

                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break
                                        iterable[1][i] = ('CONST', VARIABLES[variablesForeach[0]][0],VARIABLES[variablesForeach[0]][1])
                                    #print(iterable)
                                    VARIABLES[nombreIterable] = (iterable[1], iterable[2])

                                elif iterable[2] == 'str':
                                    #print(iterable)
                                    #print(iterable[1])
                                    for i, variable in enumerate(list(iterable[1])):
                                        VARIABLES[variablesForeach[0]] = (variable, 'str')
                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break
                                        #print(iterable[1])
                                        listaProvisoria = list(iterable[1])
                                        #print(listaProvisoria)
                                        listaProvisoria[i] = VARIABLES[variablesForeach[0]][0]
                                        iterable = ('CONST', listaProvisoria, 'str')

                                    cadena = ''
                                    for i in iterable[1]:
                                        cadena+=i
                                    iterable = ('CONST', cadena, 'str')
                                    VARIABLES[nombreIterable] = (str(iterable[1]), 'str')

                                else:
                                    for i, variable in enumerate(iterable[1]):
                                        #print(VARIABLES)
                                        #print(variable, '<- variable')
                                        VARIABLES[variablesForeach[0]] = (variable[1], variable[2])

                                        if ultimaCondicion := ejecutarCodigo(fragmentoCodigo[1:]):
                                            break
                                        iterable[1][i] = ('CONST', VARIABLES[variablesForeach[0]][0],VARIABLES[variablesForeach[0]][1])
                                    #print(iterable)

                        case 'while':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                            #print(clasificado)
                            ultimaCondicion = ejecutarMientras(fragmentoCodigo, LINEAS, nLinea)
                            #print(ultimaCondicion, '<- ultimaCondicion')

                        case 'break':
                            ultimaCondicion = False
                            #print('BREAK')
                            #print(clasificado, '<- clasificado')
                            return True # not ultimaCondicion

                        case 'if':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            #print(clasificado, '<- clasificado')
                            if clasificado[1][1]:
                                pass # Se seguirá ejecutando con normalidad

                            else: # La condición es falsa, el número de linea (nLinea) es igual al final del bloque indentado
                                fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                                #print(nLinea)
                            ultimaCondicion = clasificado[1][1]
                            #print(clasificado, '<- ultimaCondicion')

                        case 'elif':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            if ultimaCondicion:
                                #print(clasificado)
                                clasificado = ejecutarGeneral(clasificado, LINEAS, nLinea) # Se encarga de evaluar la condición hasta hacerla un 'Verdadero' o 'Falso'

                                if clasificado[1][1]:
                                    pass # Se seguirá ejecutando con normalidad

                                else: # La condición es falsa, el número de linea (nLinea) es igual al final del bloque indentado
                                    fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)
                                    #print(nLinea)
                                ultimaCondicion = clasificado[1][1]

                            else: # La anterior condición era verdadera, con lo cual este bloque no se ejecuta
                                fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)

                        case 'else':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            if ultimaCondicion:
                                fragmentoCodigo, nLinea = seleccionarFragmento(LINEAS, nLinea)

                            else: # La anterior condición era verdadera, con lo cual este bloque no se ejecuta
                                ultimaCondicion = None


                        case 'match':
                            clasificado = reemVariables(clasificado, LINEAS, nLinea)
                            clasificado = evalExpresiones(clasificado, LINEAS)

                            ejecutaCase = False
                            #print(clasificado)
                            variablesMatch = [i[1] for i in clasificado[1:-1:2] if i[2] == 'VAR']
                            #print(variablesMatch)
                            i = 0
                            while i < len(variablesMatch):
                                variablesMatch[i] = VARIABLES[variablesMatch[i]][0]
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
                            #print(modulos)
                            for i in modulos:    
                                comando = f"python {sys.argv[0]} segundo {i}.hsy"
                                IMPORTADOS += [i]
                                KeysVars += [i]
                                SALIDA = ejecutar_comando_terminal(comando)


                                #print(repr(SALIDA), '<- repr(SALIDA)')
                                AUX_VARIABLES = ast.literal_eval(SALIDA)[0]
                                for j in AUX_VARIABLES:
                                    VARIABLES[f"{i}.{j}"] = AUX_VARIABLES[j]
                                    KeysVars += [f"{i}.{j}"]
                            #print(KeysVars, '<- KeysVars')
                            #print(VARIABLES, '<- VARIABLES')
                            #print(IMPORTADOS, '<- IMPORTADOS')

                        case 'from':
                            ...
                        case 'HALT':
                            sys.exit()

                        case _: # No se encontraron estructuras que lleven a bloques identados
                            #print(clasificado, '<- clasificado ejecutarCodigo | ejcutarGeneral')
                            ejecutarGeneral(clasificado, LINEAS, nLinea)

        nLinea += 1
    return 0

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

def SugerenciasWF(palabra, diccionario, corte=10):
    sugerencias = []

    for palabra_correcta in diccionario:
        distancia = Wagner_Fischer(palabra, palabra_correcta)
        sugerencias.append((palabra_correcta, distancia))
    sugerencias.sort(key=lambda x: x[1])
    i = 0
    while i < len(sugerencias):
        sugerencias[i] = list(sugerencias[i])
        if sugerencias[i][1] > corte:
            sugerencias = sugerencias[0:i]
            break

        sugerencias[i][1] = corte - sugerencias[i][1] + 1
        i += 1
    #print(sugerencias)
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
    
def ComprobarComentarios(clasificado: list) -> bool:
    ...
    """ if bien: return 0
        else: return 6
    """

def ComprobarSintaxis(clasificado: list) -> str | bool:
    resumido = resumir(clasificado)
    if re.match(r"defC\(C?(,C)*\):", resumido): # def
        return False
    elif re.match(r"gotoC", resumido): # goto
        return False
    elif re.match(r"(for|foreach)C(,C)*inC:", resumido): # for, foreach
        return False
    elif re.match(r"(while|(el)?if)C:", resumido): # while elif if
        return False
    elif re.match(r"(match|case)C(,C)*:", resumido): # match case
        return False
    elif re.match(r"(break|pass|HALT|else:)", resumido): # break, pass, HALT, else
        return False

    return 1

def ServirErrores(ERROR: int, LINEAS: list, nLinea: int, i: int) -> bool:
    clasificado = clasificar(LINEAS[nLinea])
    if ERROR != 0:
        print('\nERROR')
        print('*'*73, '', sep='\n')
        print(f"Tipo de error: {ERROR} | Linea: {nLinea + 1}")
        match ERROR:
            case 1:
                print(f"Error de sintaxis.")
            case 2:
                print(f"\"{clasificado[i][1]}\" No se encuentra definido.")
                Mug = SugerenciasWF(clasificado[i][1], KeysVars)
                Sug = Mug[0]
                TipoSug = (clasificar(Sug))[0][2]
                CertezaSug = Mug[1]
                match TipoSug:
                    case 'VAR':
                        TipoSug = 'variable'
                    case 'TOK':
                        TipoSug = 'palabra peservada'
                    case 'FUNC' | 'FUNCRETURN':
                        TipoSug = 'función'
                    
                print(f"¿Querrá escribir \"{Sug}\" ( {TipoSug} )? Certeza: [{CertezaSug*'*'}]")

            case 3:
                print(f"Se esperaba un bloque identado despues de la estructura \"{clasificado[0][1]}\".")

            case 4:
                ...
            case 5:
                ...
            case 6:
                ...
        print(f'{nLinea + 1} |{LINEAS[nLinea]}')
        return True
    return False

def ComprobarErrores(LINEAS: list, nLinea: int = 0) -> bool:
    """
    Primero comprueba los diferentes tipos de errores a ver si existe alguno
    Al primero que vea, lo ejecuta y se cierra la función
    """
    #print('Comprobando...')

    while nLinea < len(LINEAS):
        clasificado = clasificar(LINEAS[nLinea])
        ERROR = ComprobarComentarios(clasificado)
        if ERROR:
            return ERROR
        clasificado = depurarComentarios(clasificado)
        ERROR = 0
        if ExisteProximaLinea(LINEAS, nLinea):
            #print(nLinea, LINEAS[nLinea])
            ERROR  = comprobarIdentacion(LINEAS, nLinea)
            #print(ERROR, '<- comprobar Idetancion')

        #ERROR = ComprobarSintaxis(clasificado)
        if ERROR:
            ERROR = ServirErrores(ERROR, LINEAS, nLinea, 0)
            return ERROR
        nLinea += 1
    return False


### EJECUCIÓN ###
def EJECUTAR(archivo):
    with open(rf"G:\JUEGOS\py\Py_y_html\Re_Hasya\{archivo}", "r", encoding="utf-8") as CODIGO:
        #print('casi pre main')
        LINEAS = CODIGO.read()
        CODIGO_PROCESADO = procesarCodigo(LINEAS)
        
        #print(CODIGO_PROCESADO)
        ERROR = False
        ERROR = ComprobarErrores(CODIGO_PROCESADO)
        #print(ERROR, '<- ERROR')

        if not ERROR:
            ejecutarCodigo(CODIGO_PROCESADO)

        #Errores(ERRORES, CODIGO_PROCESADO)

        #for i in CODIGO_PROCESADO:
         #   if i != '': print('>>>', i)
        #print('VARIABLES:')
        #print(VARIABLES)

def main(archivo: __file__):
    try:
        EJECUTAR(archivo)

    except FileNotFoundError:
        print(f"El archivo {archivo} no se encuentra.")

def ejecutar_comando_terminal(comando: str):
    proceso = subprocess.run(comando, shell=True, check=True, text=True, stdout=subprocess.PIPE)
    # Filtrar la salida para capturar solo el diccionario de VARIABLES
    #print(proceso.stdout.split('\n'))
    salida = proceso.stdout.split('\n')[-2]
    return salida

def DATOS_DOCUMENTO_2():

    # Crear un diccionario con las variables
    datos = [

        VARIABLES

    ]
    return datos

if __name__ == "__main__":
    if len(sys.argv) == 2:
        archivo1 = sys.argv[1]
        contenido1 = main(archivo1)

    elif len(sys.argv) == 3 and sys.argv[1] == "segundo":
        archivo2 = sys.argv[2]
        contenido2 = main(archivo2)
        
        # Generar datos basados en documento2.txt
        datos = DATOS_DOCUMENTO_2()

        # Imprimir los datos en formato JSON
        print(json.dumps(datos))

#print(VARIABLES)