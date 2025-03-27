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
        codigo.append("POP bx ; Sacamos el resultado de la expresion anterior para guardar en la variable")
        codigo.append(f"MOV {self.nombre.name()}, bx")
        #codigo.append("MOV ax, bx")
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

        codigo.append(f"{self.operando1.assembly()}")
        codigo.append(f"{self.operando2.assembly()}")
        
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

    def name(self):
        return f"{self.nombre[1]}"

    def assembly(self):
        return f"MOV ax, {self.nombre[1]}\nPUSH ax"

class NodoNumero(NodoAST):
    # Nodo que representa un numero
    def __init__(self, valor):
        super().__init__()
        self.valor = valor
    def assembly(self):
        return f"PUSH {self.valor[1]}"

class NodoString(NodoAST):
    def __init__(self, val):
        super().__init__()
        self.valor = val

    def assembly(self):
        return f"PUSH {self.valor[1]}"

class NodoCondicion(NodoAST):
    # Nodo que representa una condicion
    def __init__(self, operando1, operador, operando2):
        super().__init__()
        self.operando1 = operando1
        self.operador = operador
        self.operando2 = operando2

    def assembly(self, tag):
        codigo = []
        codigo.append("; Codigo para una condicion logica")
        codigo.append(self.operando1.assembly())
        codigo.append(self.operando2.assembly())
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

    def assembly(self, tag = ""):
        codigo = []
        codigo.append("; Codigo de comparacion relacional")
        codigo.append(self.operando1.assembly())
        codigo.append(self.operando2.assembly())
        codigo.append(f"POP bx")
        codigo.append(f"POP ax")
        codigo.append(f"CMP ax, bx")
        jmp = ""
        match self.operador[1]:
            case "==":
                jmp = "JE"
            case "<=":
                jmp = "JLE"
            case ">=":
                jmp = "JGE"
            case "<":
                jmp = "JL"
            case ">":
                jmp = "JG"
            case "!=":
                jmp = "JNE"

        codigo.append(f"{jmp} {tag}")
        codigo.append("; Fin relacional")
        return "\n".join(codigo)        

class NodoIncrement(NodoAST):
    # Nodo que representa un incremento o decremento
    def __init__(self, id, operador):
        super().__init__()
        self.id = id
        self.operador = operador

    def assembly(self):
        codigo = f"{'INC' if self.operador[1] == '++' else 'DEC'} {self.id.name()}"
        return codigo

class NodoElse(NodoAST):
    # Nodo que representa un bloque de un if_else
    def __init__(self, bloque):
        super().__init__()
        self.bloque = bloque
    
    def assembly(self):
        return "\n".join([s.assembly() for s in self.bloque])


class NodoIf(NodoAST):
    # Nodo que representa un if
    def __init__(self, condicion, bloque, elseNode = None):
        super().__init__()
        self.condicion = condicion
        self.bloque = bloque
        self.elseNode = elseNode
    
    def assembly(self):
        ifLabel = f"if_{id(self)}"
        elseLabel = f"else_{id(self)}"
        continueLabel = f"continue_{id(self)}"
        codigo = []
        codigo.append(self.condicion.assembly(ifLabel))

        codigo.append(f"JMP {elseLabel}")
        codigo.append(f"{ifLabel}:")
        if self.bloque:
            codigo.append("\n".join([s.assembly() for s in self.bloque]))
        codigo.append(f"JMP {continueLabel}")

        if self.elseNode:
            codigo.append(f"{elseLabel}:")   
            codigo.append(self.elseNode.assembly())
            codigo.append(f"JMP {continueLabel}")
        codigo.append(f"{continueLabel}:")
        return "\n".join(codigo)


class NodoWhile(NodoAST):
    def __init__(self, condicion, bloque):
        super().__init__()
        self.condicion = condicion
        self.bloque = bloque
    
    def assembly(self):
        whileLabel = f"while_{id(self)}"
        endloopLabel = f"continue_{id(self)}"
        codigo = []
        codigo.append(self.condicion.assembly(whileLabel))
        codigo.append(f"JMP {endloopLabel}")
        codigo.append(f"{whileLabel}:")
        codigo.append("\n".join([s.assembly() for s in self.bloque]))
        codigo.append(self.condicion.assembly(whileLabel))
        endloopLabel = f"continue_{id(self)}"
        codigo.append(f"{endloopLabel}:")
        return "\n".join(codigo)

class NodoFor(NodoAST):
    def __init__(self, expresionI, condicion, expresionF, bloque):
        super().__init__()
        self.var = expresionI
        self.condicion = condicion
        self.expresion = expresionF
        self.bloque = bloque

    def assembly(self):
        loopLable = f"for_{id(self)}"
        codigo = []
        codigo.append(self.var.assembly())
        codigo.append(f"{loopLable}:")

        codigo.append("\n".join([s.assembly() for s in self.bloque]))

        codigo.append(self.expresion.assembly())
        codigo.append(self.condicion.assembly(loopLable))

        return "\n".join(codigo)
