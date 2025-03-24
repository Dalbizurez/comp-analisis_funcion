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

    def assembly(self):
        pass

class NodoOperacion(NodoAST):
    # Nodo que representa una operacion artimetica
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

    def assembly(self):
        codigo = []

        codigo.append(self.operando1.assembly())
        codigo.append("push ax")
        codigo.append(self.operando2.assembly())
        codigo.append("push ax")
        
        codigo.append("push bx")
        codigo.append("push ax")

        match self.operador[1]:
            case '+':
                op = "ADD ax, bx"
            case '-':
                op = "SUB ax, bx"
            case '*':
                op = "MUL bx"
            case '/':
                op = "DIV bx"
        codigo.append(op)

        return "\n".join(codigo)


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

    def assembly(self):
        return f"mov ax, [{self.nombre[1]}]"

class NodoNumero(NodoAST):
    # Nodo que representa un numero
    def __init__(self, valor):
        super().__init__()
        self.valor = valor
    def assembly(self):
        return f"mov ax, {self.nombre[1]}"

class NodoString(NodoAST):
    def __init__(self, val):
        super().__init__()
        self.valor = val

    def assembly(self):
        return f"  mov ax, {self.valor[1]}"

class NodoCondicion(NodoAST):
    # Nodo que representa una condicion
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

    def assembly(self):
        codigo = []
        op1 = (self.operando1.assembly())
        match self.operador[0]:
            case "RELATIONAL":
                case 
        

class NodoIncrement(NodoAST):
    # Nodo que representa un incremento o decremento
    def __init__(self, operador):
        super().__init__()
        self.operador = operador

class NodoElse(NodoAST):
    # Nodo que representa un bloque de un if_else
    def __init__(self, bloque):
        super().__init__()
        self.bloque = bloque


class NodoIf(NodoAST):
    # Nodo que representa un if
    def __init__(self, condicion, bloque, elseNode = None):
        super().__init__()
        self.condicion = condicion
        self.bloque = bloque
        self.elseNode = elseNode
    
    def assembly(self):
        codigo = []


class NodoWhile(NodoAST):
    def __init__(self, condicion, bloque):
        super().__init__()
        self.condicion = condicion
        self.bloque = bloque

class NodoFor(NodoAST):
    def __init__(self, expresionI, condicion, expresionF, bloque):
        super().__init__()
        self.var = expresionI
        self.condicion = condicion
        self.expresion = expresionF
        self.bloque = bloque
