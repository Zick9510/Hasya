toke = {

    '#': '#',

    # OPERACIONES 

    '+': '+',
    '-': '-',
    '*': '*',
    '/': '/',
    '**': '**',
    '%': '%',
    '//': '//',

    '&': '&',
    '|': '|',
    
    # LÓGICOS

    ' y ': ' and ',
    ' o ': ' or ',
    ' no ': ' not ',
    
    '&&': ' and ',
    '||': ' or ',
    '!': ' not ',

    # CONDICIONES

    'en': 'in',
    '==': '==',
    '!=': '!=',
    '>': '>',
    '<': '<',
    '>=': '>=',
    '<=': '<=',

    # SEPARADORES Y OTROS ELEMENTOS

    ':': ':',
    '.': '.',
    ',': ',',

    '(': '(',
    ')': ')',

    '{': '{',
    '}': '}',

    '[': '[',
    ']': ']',

    # ASIGNADORES

    '=': '=',
    '+=': '+=',
    '-=': '-=',
    '*=': '*=',
    '/=': '/=',
    '**=': '**=',

    # ESTRUCTURAS

    'para': 'for',
    'cada': 'foreach',

    'mientras': 'while',

    'si': 'if',
    'sino si': 'elif',
    'sino': 'else',

    'def':'def',

    'capta':'match',
    'caso':'case',

    # INSTRUCCIONES

    'importar': 'import',
    'desde': 'from',

    'salir': 'break',
    'pasar': 'pass',
    'continuar': 'continue',

    'ir a': 'goto',

    'retorno': 'return',

    'DETENER': 'HALT',
    
    # OTRAS PALABRAS CLAVE
    
}
to = sorted(toke, key=len, reverse=True)
tok = {}
for i in to:
    tok.setdefault(i, toke[i])

funciones = {
    'mostrar': 'print',
    
}
fu = sorted(funciones, key=len, reverse=True)
func = {}
for i in fu:
    func.setdefault(i, funciones[i])

funcionesReturn = {
    
    'ingresar': 'input',
    'largo': 'len',
    'invertir': 'reversed',
    'rango': 'range',
    'enumerar': 'enumerate',
    'matriz': 'matrix',
    'lista': 'list',
    'todos': 'all',

}
funcRet = sorted(funcionesReturn, key=len, reverse=True)
funcReturn = {}
for i in funcRet:
    funcReturn.setdefault(i, funcionesReturn[i])

funcReturnU = {}
funcU = {}

meto = {
    
    # STRINGS:

    'capitalizar': 'capitalize',
    'casefold': 'casefold',
    'centrar': 'center',
    'contar': 'count',
    '': 'encode',
    'terminacon': 'endswith',
    '': 'expandtabs',
    'encontrar': 'find',
    'formato': 'format',
    '': 'format_map',
    '': 'isalnum',
    '': 'isalpha',
    '': 'isascii',
    'esdecimal': 'isdecimal',
    'esdigito': 'isdigit',
    '': 'isidentifier',
    'esminuscula': 'islower',
    'esnumerico': 'isnumeric',
    'esmostrable': 'isprintable',
    'esespacio': 'isspace',
    'estitulo': 'istitle',
    'esmayuscula': 'isupper',
    'juntar': 'join',
    '': 'ljust',
    'minuscula': 'lower',
    '': 'lstrip',
    '': 'maketrans',
    '': 'partition',
    '': 'removeprefix',
    '': 'removesufix',
    'reemplazar': 'replace',
    '': 'rfind',
    '': 'rindex',
    '': 'rjust',
    '': 'rpartition',
    '': 'rsplit',
    '': 'rstrip',
    'separar': 'split',
    '': 'splitlines',
    '': 'startswith',
    '': 'strip',
    '': 'swapcase',
    'titular': 'title',
    'intercambiar': 'translate',
    'mayuscula': 'upper',
    '': 'zfill',
    
    # LISTAS
    
    'agregar': 'append', # Agrega X a LIS
    'eliminar': 'remove', # Quita X de LIS
    'quitar': 'pop',  # Quita Indice de LIS
    'limpiar': 'clear', # Borra toda LIS
    'copiar': 'copy', # Crea una copia de LIS
    'contar': 'count', # Cuenta la cantidad de X en LIS
    'extender': 'extend', # Extiende LIS con X
    'indice': 'index', # Devuelve el indice de X
    'indices': 'indexs', # Devuelve todos los indices donde este X
    'insetar': 'insert', # Inserta en el índice n X
    'insertarlista':'insertlist', # Inserta en el índice n la lista LIS
    'revertir': 'reverse', # Revierte la lista (si X esta en [n] X pasa a estar en [-n-1])
    'ordenar': 'sort', # Hacer el coso para que esto pueda funcionar
    
}
met = sorted(meto, key=len, reverse=True)
metodos = {}
for i in met:
    metodos.setdefault(i, meto[i])
    
simb = {
    '->': 'si', # Si A es verdadero, entonces B tmb
    '<->': 'si solo si', # Lo mismo que el anterior pero y viceversa
    '^': 'y', # Y
    'v': 'o', # O
    '¬': 'negado', # Negación
    'A': 'for each', # Para cada
    'E': 'existe', # Existe
    'E*': 'no existe', # No existe
    'E!': 'existe único', # Existe un único
    ':': 'tal que', # Tal que
    '|': 'tal que', # Tal que
    '{': '{', # xd
    '}': '}', # xd**2
    'O*': 'C_VACIO', # Conjunto vacío = {}
    'e': 'pertenece', # Pertenece
    'e*': 'no pertenece', # No pertenece
    'c=*': 'incluye y !=', # Se incluye y no es igual
    'c=': 'incluye o ==', # Se incluye o es igual
    'c': 'inluye', # Se incluye

    'U': 'U', # Unión
    'U*': 'U*', # Conjunción
    '\\': '\\', # wtf?

    '-->': '-->',
    '->>': '->>',
    '+->': '+->',
    '|_': '|_',
    '_|': '_|',
    '|_*': '|_*',
    '_|*': '_|*',

    '==': '==',
    '!=': '!=',
    '>': '>',
    '<': '<',
    '>=': '>=',
    '<=': '<=',

}
sim = sorted(simb, key=len, reverse=True)
simbolos = {}
for i in sim:
    simbolos.setdefault(i, simb[i])

def combinar(d1, d2):
    d3 = {}
    for i in d1:
        d3.setdefault(i, d1[i])
    for i in d2:
        d3.setdefault(i, d2[i])
    return d3