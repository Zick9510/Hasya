Nota a tener en cuenta:

    Para ejecutar un archivo de Hasya (.hsy) el archivo deberá estar en la misma carpeta que el archivo Re_Hasya.py, luego
    en la terminal tendran que escribir python Ruta\Re_Hasya.py Ruta\TuArchivo.hsy.

    <id>: Identificador
    <vd> o <valor>: Valor
    <e>: Expresión matemática (puede o no contener otras variables)
    
    <x>: Cualquiera de los anteriores

    <it>: Iterable

    Hasya esta fuertemente insipado en Python y ciertos toques de C.
    En Hasya los bloques identados funcionan igual que en Python y en general todo es bastante
    similar, como los comentarios simples, aunque los multilinea van #/ comentario /#



### DOCUMENTACIÓN


Variables:

    1. Para asignares un valor:
    <id> = <x>

    2. Se pueden operar las variables entre si y reasignar sus valores.

    3. Las listas van entre corchetes y sus elementos separados por ","
        A. Se pueden operar con los elementos de una lista de la siguiente forma:
            <it>[<x>] # Donde <it> es el nombre de tu lista, y <x> la posición/índice del elemento en cuestión
        
        B. Se pueden reasignar los elementos de una lista aplicando el concepto anterior, agregando un igual y luego el 
            nuevo valor
        
        C. Si, una lista puede contener listas y otros tipos de variables



    4. Las cadenas de texto o strings, van entre comillas simples "'" # Próximamente se podrán usar las comillas dobles '"'
        A. Al igual que las listas, se pueden obtener los caracteres de una cadena utilizando <it>[<x>]

        B. No se pueden reasignar los elementos de una cadena # Aunque es probable que se vea esta funcionalidad

Instrucciones:

    Una instrucción es una linea que le dicta a la computadora que hacer, por ejemplo:
    
    retorno <x>
    
    ir a <x>

    1. Retorno
        En funciones, una vez que alcanza la linea del retorno, se reemplaza el valor del retorno 
        en la llamada de la función

    2. Ir a
        Selecciona una linea  a la cual ir, y el número de linea se actualiza a esa, y seguirá ejecutando desde ahí
        Advertencia: Esta instrucción puede fácilmente llevar a bucles indeseados y actualmente Hasya no cuenta con 
        una parada automática

    3. Importar
        Se usa para importar 1 o más archivos .hsy, se traen únicamente sus variables:

        # Supongamos, tengo un archivo prueba.hsy donde x = 2

        importar prueba
        x = 1
        mostrar(x, prueba.x) # En la terminal veo 1 2

    3. Salir y Pasar
        Salir se utiliza para salir de un bloque identado de un ciclo. (salir)

        Pasar es una instrucción que literalmente no hace nada. (pasar)

    4. DETENER
        Literalmente detiene completamente la ejecución del programa

Estructuras:

    Una estructura es una instrucción que lleva a bloques identados

    En las estructuras que funcionen con condiciones, llamadas condicionales, se pueden utilizar los siguientes símbolos para 
    constituirlas:
    
        == # "Es igual"
        != # "Es diferente" 
        >  # "Es mayor"
        <  # "Es menor"
        >= # "Es mayor o igual"
        <= # "Es menor o igual"

        && / y # "Esto y esto" -> Requiere que ambas condiciones sean verdadera
        || / o # "Esto o esto" -> Con una condición verdadera basta
        ! / no # "La negación de lo que sigue" -> La condición inicial debe ser falsa para dar un verdadero (y viceversa)



    1. Si
        Toma una condición y evalua el bloque identado si es verdadera

        si CONDICION:
            lineas a ejecutar

    2. Sino si
        Si la condición del si es falsa, se evalua una nueva condición de manera similar, se pueden
        concatenar tantos sino si como se desee

        si CONDICION FALSA: # Esto no se ejecuta
            lineas a ejecutar
        sino si CONDICION:
            otras lineas a ejecutar

    3. Sino
        Si todas las condiciones anteriores del si, y el/los sino si (si es que existen) son falsas, se ejecutará 
        el proximo bloque identado

        si CONDICION FALSA: # Esto no se ejecuta
            lineas a ejecutar

        sino si CONDICION FALSA: # Esto tampoco
            otras lineas a ejecutar

        sino:
            otras otras lineas a ejecutar

    Las estructuras sino si y sino son opcionales

    4. Capta y caso
        Capta toma una o más variables como entrada y compara los casos, en el momento en que uno coincida, se ejecutara 
        ese bloque de ese caso y saldra del capta
        
        capta <id o ids>:
            caso <id o ids>:
                ...
            ... 
        
        Se puede agregar "_" en los casos para que esa variable en concreto no importe:

            a = 2
            b = 3
            capta a, b:
                caso 2, 2:
                    mostrar(2, 2)
                caso 1, 3:
                    mostrar(1, 3)
                caso 1, _:
                    mostrar(1, '_')
                caso _:
                    mostrar('_')

Ciclos:

    Un ciclo es una estructura que se ejecuta a si misma hasta determinada condición o cierto iterable

    1. Mientras
        mientras CONDICION:
            lineas a ejecutar

        Mientras CONDICION se verdadera, las lineas a ejecutar se van a ejecutar hasta que CONDICION sea falsa

    2. Para
        para <id o ids> en <it>:
            lineas a ejecutar
        
        El/Los id/ids tomarán los valores correspondientes en <it>, e iran ejecutando las lineas identadas
        hasta que ocupen el/los último/s valores de <it>

        lista1 = [1, 2, 3, 4]
        para i en lista1: # lista1 se puede reemplazar por [1, 2, 3, 4] y se obtendrá el mismo resultado
            mostrar(i)

    3. Cada
        Similar al ciclo para, solo que se reemplazará en <it> el valor de la/s variables <id/s>
        
        cada i en lista1:
            i = i + 2 # También válido i += 2
        # Ya no nos encontramos en el ciclo cada
        mostrar(lista1)

Funciones Incorporadas sin retorno:

    1. Mostrar
        Puede recibir múltiples argumentos y los imprimira en pantalla, cada argumento estará separado por un espacio y al final de la función se imprimira de manera
        automática una nueva linea ("\n"). Esto no se puede cambiar, aunque en próximas actualizaciones espero poder añadir la posiblidad de hacero

Funciones Incorporadas con retorno

    1. Ingresar
    Puede recibir un argumento y lo imprimira en pantalla, luego esperara a que el usuario ingrese un texto y
    presione enter para enviarlo

    2. Largo
        Su argumento es un <it> y devuelve su longitud

    3. Invertir
        Toma un <it> y lo revierte, dejando los últimos elementos como los primeros y viceversa

    4. Rango # No la película
        Puede tomar hasta 3 argumentos y funciona de la siguiente manera:
            Con 1 argumento devuelve una lista desde el 0 hasta ese <x>
            Con 2 la lista comienza en el primero y sigue hasta el segundo (sin incluir el segundo)
            Con 3 funciona similar al 2, pero el tercero indica cada cuantos elementos se saltea
        
    5. Matriz
        Toma un <it> como primer argumento y un <x> como segundo, el primero marca las dimensiones y el segundo es
        el elemento con el cual rellenar todas las casillas

Funciones del usuario:

    Las funciones son útiles cuando se quiere ejecutar determinada sección del código varias veces, a veces cambiando ciertos
    valores, un ejemplo sería:

    def f(x):
        retorno x**2 # Aca x, el argumento, se eleva al cuadrado y se retorna para reemplazarse en el lugar en el que se llamo la función

    Para definir una función, se utiliza la palabra clave def.
    Las funciones pueden o no recibir argumentos. # Son parámetros con los cuales opera la función
    Las funciones pueden retornar un valor. # Próximamente se va a poder retornar varios valores al mismo tiempo

    def suma(n1, n2):
        resultado = n1 + n2
        retorno resultado

    mostrar(suma(3, 4)) # En la terminal veríamos un 7

    Advertencia:
        Al llamar a una función, reescribira el valor de sus argumentos según los valore que le
        pasemos:
            h = 3

            def hola(h):
                mostrar(h)
                retorno h

            hola(2)

            # Para este punto del código, h vale 2, no 3

        Este es un error que no se exactamente como corregir, aunque espero que pronto se de la situación.
