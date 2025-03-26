class NodoAST:
    # Clase base para todos los nodos del AST
    pass

class NodoPrograma(NodoAST):
    def __init__(self, funciones):
        super().__init__()
        self.funciones = funciones
    
    def assembly(self):
        return self.funciones.assembly()

class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        super().__init__()
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

    def assembly():
        pass

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

    def assembly(self):
        codigo = []
        codigo.append(self.expresion.assembly())
        codigo.append(self.nombre.assembly())
        codigo.append("POP bx ; Sacamos el resultado de la expresion anterior para guardar en la variable")
        codigo.append("MOV ax, bx")
        return "\n".join(codigo)

class NodoExpresion(NodoAST):
    def __init__(self, val, expresion):
        super().__init__()
        self.value = val
        self.expression = expresion

    def assembly(self):
        return self.expression.assembly()

class NodoOperacion(NodoAST):
    # Nodo que representa una operacion artimetica
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

    def assembly(self):
        codigo = []
        codigo.append("; Codigo de operacion aritmetica")

        codigo.append(self.operando1.assembly())
        codigo.append("PUSH ax")
        codigo.append(self.operando2.assembly())
        codigo.append("PUSH ax")
        
        codigo.append("POP bx")
        codigo.append("POP ax")
        codigo.append("; Operacion")
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
        codigo.append("PUSH ax ; Almacenar resultado")
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
        return f"MOV ax, [{self.nombre[1]}]"

class NodoNumero(NodoAST):
    # Nodo que representa un numero
    def __init__(self, valor):
        super().__init__()
        self.valor = valor
    def assembly(self):
        return f"MOV ax, {self.valor[1]}"

class NodoString(NodoAST):
    def __init__(self, val):
        super().__init__()
        self.valor = val

    def assembly(self):
        return f"MOV ax, {self.valor[1]}"

class NodoCondicion(NodoAST):
    # Nodo que representa una condicion
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

    def assembly(self):
        codigo = []
        codigo.append("; Codigo de condicion en un if")
        codigo.append(self.operando1.assembly())
        codigo.append(self.operando2.assembly())
        codigo.append("PUSH ax")
        codigo.append(f"POP bx")
        codigo.append(f"POP ax")
        match self.operador[0]:
            case "LOGICAL":
                match self.operador[1]:
                    case "&&":
                        op = "AND ax, bx"
                    case "||":
                        op = "OR ax, bx"
                    case "!":
                        op = "NOT ax"
                codigo.append(op)
        codigo.append("PUSH ax")

        return "\n".join(codigo)        

class NodoRelacional(NodoAST):
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

    def assembly(self):
        codigo = []
        codigo.append("; Codigo de comparacion relacional")
        codigo.append(self.operando1.assembly())
        codigo.append("PUSH ax")
        codigo.append(self.operando2.assembly())
        codigo.append("PUSH ax")
        codigo.append(f"POP bx")
        codigo.append(f"POP ax")
        codigo.append(f"CMP ax, bx")
        codigo.append("; Fin relacional")
        return "\n".join(codigo)


        

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
    
    def assembly(self):
        return self.bloque.assembly()


class NodoIf(NodoAST):
    # Nodo que representa un if
    def __init__(self, condicion, bloque, elseNode = None):
        super().__init__()
        self.condicion = condicion
        self.bloque = bloque
        self.elseNode = elseNode
    
    def assembly(self):
        codigo = []
        codigo.append(self.condicion.assembly())

        ifLabel = f"{id(self)}_if:"
        elseLabel = ""
        codigo.append(ifLabel)
        if self.bloque:
            codigo.append("\n".join([s.assembly() for s in self.bloque]))
        if self.elseNode:
            elseLabel = f"{id(self)}_else:"
            codigo.append(elseLabel)   
            codigo.append(NodoElse(self.elseNode).assembly())

        return "\n".join(codigo)


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
