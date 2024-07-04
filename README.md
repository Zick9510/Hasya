Nota a tener en cuenta:

    Para ejecutar un archivo de Hasya (.hsy) el archivo deberá estar en la misma carpeta que el archivo Re_Hasya.py, luego
    en la terminal tendran que escribir python ruta\a\main\Re_Hasya.py ruta\a\tu\archivo.hsy. En caso de no especificar un
    archivo a ejecutar, se ejecutará el archivo Hasya.hsy que se encuentra en la carpeta de Re_Hasya.py.

    <id>: Identificador
    <vd> o <valor>: Valor
    <e>: Expresión matemática (puede o no contener otras variables)
    
    <x>: Cualquiera de los anteriores

    <it>: Iterable

    Hasya esta fuertemente insipado en Python y ciertos toques de C.

    En Hasya los bloques identados sirven para definir el inicio y el fin de las estructuras y bloques de código:
    No es lo mismo escribir

    x = 2
    si x == 2:
        mostrar("x = 2")
        mostrar("Fin sentencia 'si'")

    A escribir

    x = 2
    si x == 2:
        mostrar("x = 2")
    mostrar("Fin sentencia 'si'")

    # En este caso, el segundo mostrar se va a ejecutar siempre, mientras que en el primero solo se va a mostrar si x == 2


### DOCUMENTACIÓN


Variables:

    1. Para asignares un valor:
        A. <id> = <x>

        B. Es posible separar múltiples <id> entre = para asignarles a todos el mismo valor <x>
    
        C. Es posible separar múltiples <id> entre cada signo igual para asignar secuencias de valores: # Se separan con ","
            
            a, b, c = d, e, f = 1, 2, 3 

            # Es como si se asignasen "de a pares", el primero con el primero, y siguiendo
            # a = d = 1, b = e = 2 y c = f = 3
        
        D. Se considera que una variable es verdadera cuando:

            a. Si es un número no nulo (distinto de 0)

            b. Si es una lista contiene al menos un elemento

            c. Si es una cadena contiene al menos un caracter (cualquiera, incluido el espacio "' '")

    2. Se pueden operar las variables entre si y reasignar sus valores.

    3. Las listas van entre corchetes y sus elementos separados por ","
        A. Se pueden operar con los elementos de una lista de la siguiente forma:
            <it>[<x>] # Donde <it> es el nombre de tu lista, y <x> la posición/índice del elemento en cuestión
            y se comienza a contar desde el 0, y termina en n - 1, donde n es el largo del iterable
        
        B. Se pueden reasignar los elementos de una lista aplicando el concepto anterior, agregando un igual y luego el 
            nuevo valor
        
        C. Si, una lista puede contener listas y otros tipos de variables

    4. V - listas:
        Las V - listas son listas que contienen variables, y al cambiar esas variables cambia el valor de las listas
        Se declaran poniendo una v antes del primer corchete:
            i = 3

            lis = v[1, 2, i, 4]

            x = lis[2]

            mostrar(x) # Acá veriamos un 3 como salida

        Pero en este caso:

            i = 3

            lis = v[1, 2, i, 4]

            i = 10

            x = lis[2]

            mostrar(x) # Veríamos un 10
        
        Ahora bien, a la hora de operar con listas es posible "enganchar" una variable a otra, haciendo que si cambia el valor de
        la primera, cambie el valor de la segunda:
            i = 3

            lis = v[1, 2, i, 4]

            x = lis[2] # En este momento, "x" queda enganchada a la variable "i"

            i = 2 # Por lo tanto, "x" ahora no vale 3, sino 2

            mostrar(x) # Entonces acá se vería un 2 en la terminal

        Otro ejemplo con V - listas:
            i = 3
            vlis = v[1, 2, i] # No es necesario poner una "v" al principio de la variable, pero si a la lista

            i = 2

            lis = [vlis, [4, 5, 6]]

            x = lis[0][2]

            i = 10

            mostrar(lis, x) # La salida es "[[1, 2, 10], [4, 5, 6]] 10"

        Además, se pueden enganchar múltiples variables a una sola:

            i = 3
            lis = v[1, 2, i]

            x1 = lis[2]

            y1 = x1

            i = 1

            z1 = y1

            mostrar(z1) # Vemos un 1

    5. Las cadenas de texto o strings, van entre comillas simples "'" # Próximamente se podrán usar las comillas dobles '"'
        A. Al igual que las listas, se pueden obtener los caracteres de una cadena utilizando <it>[<x>]

        B. No se pueden reasignar los elementos de una cadena # Aunque es probable que se vea esta funcionalidad

Operaciones:

    Para operar con una variable es posible usar cualquiera de estos operadores:

        1. Suma (+)
        2. Resta (-)
        3. Multiplicación (*)
        4. División (/)
        5. Potenciación (**)
        6. Radicación (*/)
        7. Resto (%)
        8. Cociente (//)
        9. Mover bits derecha (>>)
        10. Mover bits izquierda (<<)

        Si, hacen exactamente lo que estás pensando que hacen

    Adicionalmente, estos operadores se pueden anteponer al signo igual para que el resultado se almacene
    en la variable inicial:

        1. Incrementar (+=)
        2. Decrementar (-=)
        3. Multiplicar (*=)
        4. Dividir (/=)
        5. Potenciar (**=)
        6. Radicar (*/=)
        7. Resto (%=)
        8. Cociente (//=)
        9. Mover bits derecha (>>=)
        10. Mover bits izquierda (<<=)

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

    3. Salir
        Salir se utiliza para salir de bloques identados como funciones, ciclos, condicionales, etc.

    4. Pasar
        Pasar es una instrucción que literalmente no hace nada.

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
        Si la condición del "si" es falsa, se evalua una nueva condición de manera similar, se pueden
        concatenar tantos sino si como se desee

        si CONDICION FALSA: # Esto no se ejecuta
            lineas a ejecutar
        sino si CONDICION:
            otras lineas a ejecutar

    3. Sino
        Si todas las condiciones anteriores del "si", y el/los "sino si" (si es que existen) son falsas, se ejecutará 
        el proximo bloque identado

        si CONDICION FALSA: # Esto no se ejecuta
            lineas a ejecutar

        sino si OTRA CONDICION FALSA: # Esto tampoco
            otras lineas a ejecutar

        sino: # No lleva condición
            otras otras lineas a ejecutar

        Este mismo pensamiento se puede aplicar a los ciclos, pero utilizando la instrucción "salir",
        es decir, si se utiliza la instrucción "salir", el bloque "sino" no se va a ejecutar
        # Se puede pensar el bloque "sino" después de un ciclo como:
        "Si no usasate salir, hace esto: "

    Las estructuras "sino si" y "sino" son opcionales

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
                    mostrar(1, 3) # Si a vale 1 este bloque se ejecutaría

                caso 1, _: # Si esto en su lugar fuese "caso 2, _:" sería el que se ejecuta
                    mostrar(1, '_') 

                caso _:
                    mostrar('_')

Ciclos:

    Un ciclo es una estructura que se ejecuta a si misma hasta determinada condición o cierto iterable

    1. Mientras
        mientras CONDICION:
            lineas a ejecutar

        Mientras CONDICION se verdadera, las lineas a ejecutar se van a ejecutar hasta que CONDICION sea falsa

    2. Hace Mientras

        hace mientras CONDICION:
            lineas a ejecutar
        
        Similar al ciclo mientras, pero primero ejecutará sus lineas sin evaluar la condición, luego se comporta como un
        ciclo mientras común y corriente

        Ejemplo:
        
        i = 0
        hace mientras i == 1:
            mostrar('i vale:', i)
            i += 1 # i = i + 1

        # Eso es reemplazable por 

        i = 0
        mostrar('i vale:', i)
        i += 1
        mientras i == 1:
            mostrar('i vale:', i)
            i += 1

        # Nótese las similitudes

    3. Para
        para <id o ids> en <it>:
            lineas a ejecutar
        
        El/Los id/ids tomarán los valores correspondientes en <it>, e iran ejecutando las lineas identadas
        hasta que ocupen el/los último/s valores de <it>

        lista1 = [1, 2, 3, 4]
        para i en lista1: # lista1 se puede reemplazar por [1, 2, 3, 4] y se obtendrá el mismo resultado
            mostrar(i)

    4. Cada
        Similar al ciclo para, solo que se reemplazará en <it> el valor de la/s variables <id/s>
        
        cada i en lista1:
            i = i + 2 # También válido i += 2
        # Ya no nos encontramos en el ciclo cada
        mostrar(lista1)

        Nota:
            Este ciclo esta pensado para iterarse sobre un <it> y modificar sus valores, con lo cual no es correcto
            usar funciones que modifiquen el iterable o creen uno nuevo, como "enumerar" o "rango" y/o similares.
            Tampoco esta permitido pasar como <it> un argumento diferente de una variable, por la misma razón.

Funciones no anónimas:

    Una función no anónima es una sección del código al que se puede "llamar" utilizando su nombre, estas
    funciones pueden contener argumentos, sin valores con los cuales trabaja la función y pueden ser 
    diferentes en cada una de sus llamadas, permitiendo una alta verstílidad y volviendo el código más limpio
    al reutilizar partes del mismo. Estos argumentos pueden ser de 2 tipos:

        Posisicionales o no predefinidos:

            Cuando se llama una función se tiene que especificar su valor, ya sea por medio de "nombre_Argumento = Valor"
            o escribiendo directamente el valor en el lugar al cual se le corresponde la llamada. Ejemplo:

                def suma(n1 , n2: int, n3 = 3, n4: int = 4) -> int: # En este ejemplo, n1 y n2 son argumentos posicionales
                    retorno n1 + n2 + n3 + n4

                suma(1, 2) # Se le asigna el valor 1 a n1 y 2 a n2, si se queire especificar cual es el valor 
                           # para n1 y cual para n2 se debe hacer de la siguiente manera.

                suma(n1=1, n2=2) # De esta forma, se puede prescindir del orden de los argumentos en la llamada (suma(n2=2, n1=1) es quivalente)
            
        Clave o predefinidos:

            Siguiendo el ejemplo anterior, n3 y n4 serían argumentos clave, ya que no es necesario especificar su valor a la
            hora de llamar la función, y al no hacerlo, éstos tomaran el valor preestablecido, en este caso, n3 y n4 valdrán
            3 y 4 respectivamente. Una vez más, se puede modificar sus valores al usar "n3=10" o siguiendo el orden de 
            la llamada:
            
            suma(1, 2, 10) # Al no establecer el valor de n4, éste valdra 4, mientras que el resto valdrá 1, 2 y 10 respectivamente
            suma(1, 2, n3=10) # Ambas provocan el mismo resultado, 17

            Es posible modificar el valor de n4 dejando el de n3 como su valor preestablecido, nuevamente usando "n4=20"
                

    Funciones Incorporadas con retorno distinto de Nada

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
        
        6. Enumerar
            Su argumento es un <it> y devuelve una lista de listas (o parejas) tales que el primer elemento de la pareja
            indica el índice del segundo elemento de la pareja, la lista general está ordenada según los indices de menor a mayor
        
        7. Todos
            Ingresa un <it> como argumento y devuelve 1 si todos sus elementos son verdaderos, devuelve 0 si alguno es falso

        8. Alguno
            Ingresa un <it> y devuelve 1 si alguno de sus elementos es verdadero, devuelve 0 si todos son falsos

        9. Mapear
            Toma como argumento una función y un iterable, aplica esa función a cada elemento del iterable y retorna el iterable modificado
        
        10. Filtrar
            Su primer argumento es una función y su segundo un iterable, devuelve un iterable con los elementos que retornaron 
            un valor verdadero al ser pasados como argumentos a la función

        11. Lista
            Toma un <it> y lo intenta convertir  en lista, en caso de las cadenas, separando sus elementos
        
        12. Relu
            Toma un número y devuelve 0 si este número es menor a 0, sino, devuelve el valor del número

        13. Aplanar
            Ingresa un <it> y retorna una lista con los elementos del <it> sin las listas que los encapsulaban
            
            (ej [1, 2, [3, 4, [5, 6]]] -> [1, 2, 3, 4, 5, 6])
            
    Funciones Incorporadas con retorno Nada:

        1. Mostrar
            Puede recibir múltiples argumentos y los imprimira en pantalla, cada argumento estará separado por un espacio y al final de la función se imprimira de manera
            automática una nueva linea ("\n").

    Funciones del usuario:

        Las funciones son útiles cuando se quiere ejecutar determinada sección del código varias veces, a veces cambiando ciertos
        valores, un ejemplo sería:

        def f(x):
            # Aca podes poner más cosas, las funciones pueden tener más lineas 
            retorno x**2 # Aca x, el argumento, se eleva al cuadrado y se retorna para reemplazarse en el lugar en el que se llamo la función

        Para definir una función, se utiliza la palabra clave def.
        Las funciones pueden o no recibir argumentos. # Son parámetros con los cuales opera la función
        Las funciones pueden retornar valores. # Son valores que se reemplazan en el lugar donde se llamó la función

        def suma(n1, n2):
            resultado = n1 + n2
            retorno resultado

        mostrar(suma(3, 4)) # En la terminal veríamos un 7, ya que "suma(3, 4)" se reemplaza con el retorno, que en este caso es 7



Sobre el contexto de las variables

    El contexto de una variable se refiere a la sección del código donde "vive", ya sea en una función o en todo el 
    programa. Esto permite definir variables y utilizar su mismo identificador en por ejemplo, los argumentos de una 
    función, y ambos van a ser independientes entre si, sin temor a que uno sobreescriba al otro.
