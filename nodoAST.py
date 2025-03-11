class NodoAST:
    # Clase base para todos los nodos del AST
    pass

class NodoPrograma(NodoAST):
    def __init__(self, funciones):
        super().__init__()
        self.funciones = funciones

class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        super().__init__()
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

class NodoParametro(NodoAST):
    # Nodo que representa un parametro de funcion
    def __init__(self, tipo, nombre):
        super().__init__()
        self.tipo = tipo
        self.nombre = nombre

class NodoAsignacion(NodoAST):
    # Nodo que representa una asignacion de variable
    def __init__(self, nombre, expresion):
        super().__init__()
        self.nombre = nombre
        self.expresion = expresion

class NodoExpresion(NodoAST):
    def __init__(self, val, expresion):
        super().__init__()
        self.value = val
        self.expression = expresion

class NodoOperacion(NodoAST):
    # Nodo que representa una operacion artimetica
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

class NodoRetorno(NodoAST):
    # Nodo que representa la sentencia return
    def __init__(self, expresion):
        super().__init__()
        self.expresion = expresion

class NodoIdentificador(NodoAST):
    # Nodo que representa un identificador
    def __init__(self, nombre):
        super().__init__()
        self.nombre = nombre

class NodoNumero(NodoAST):
    # Nodo que representa un numero
    def __init__(self, valor):
        super().__init__()
        self.valor = valor

class NodoString(NodoAST):
    def __init__(self, val):
        super().__init__()
        self.valor = val

class NodoCondicion(NodoAST):
    # Nodo que representa una condicion
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

class NodoIf(NodoAST):
    # Nodo que representa un if
    def __init__(self, condicion, bloque):
        super().__init__()

