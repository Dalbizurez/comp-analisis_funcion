import re
from nodoAST import *
import json

# === Analisis Lexico ===
# Definir los patrones para los diferentes tipos de tokens
token_patron = {

    "KEYWORD": r'\b(if|else|while|return|print|for)\b',
    "DATATYPE": r'\b(int|float|string|void)\b',
    "STRING": r'\"[a-zA-Z0-9]*\"',
    "IDENTIFIER": r'\b[a-zA-Z][a-zA-Z0-9]*\b',
    "NUMBER": r'\b\d+(\.\d+)?\b',
    "INCREMENT": r'\+\+|--',
    "ARITHMETIC": r'[\+\-\*\/]',
    "RELATIONAL": r'[<>][=<>]?|==|!=',
    "LOGICAL": r'&&|\|\||!',
    "ASSIGNMENT": r'=',
    "DELIMITER": r'[(),;{}]',
    "WHITESPACE": r'\s+',
}

def indentificar_tokens(texto):
    # Unir todos los patrones en un unico patron realizando grupos nombrados
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token, valor))
    return tokens_encontrados

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # Visualizar token actual sin consumir
    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    # Consumir token actual si es el esperado, 
    # caso contrario generar error de sintaxis 
    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        else:
            raise SyntaxError(f"Se esperaba un token de tipo {tipo_esperado} pero se encontro {token_actual}")
        
    # Comenzar analisis
    def parse(self):
        funciones = []
        while self.obtener_token_actual() and (self.obtener_token_actual()[1] != "}"):
            funciones.append(self.funcion())
        return funciones
    
    # Analizar la funcion en base a la estructura
    def funcion(self):
        tipo_retorno = self.coincidir("DATATYPE")
        nombre_funcion = self.coincidir("IDENTIFIER")
        self.coincidir("DELIMITER")
        parametros = self.parametros()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        cuerpo = self.cuerpo()
        self.coincidir("DELIMITER")
        return NodoFuncion(nombre_funcion, parametros, cuerpo)
        
    def parametros(self):
        parametros = []
        if self.obtener_token_actual()[1] == ')':
            return parametros
        tipo = self.coincidir("DATATYPE")
        nombre = self.coincidir("IDENTIFIER")
        parametros.append(NodoParametro(tipo, nombre))
        if self.obtener_token_actual()[1] and self.obtener_token_actual()[1] == ',':
            self.coincidir("DELIMITER")
            parametros.extend(self.parametros())
        return parametros
    
    def cuerpo(self):
        instrucciones = []
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == "}":
            return instrucciones
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != "return":
            instrucciones.append(self.statement())
        instrucciones.append(self.retorno())
        return instrucciones

    def retorno(self):
        self.coincidir('KEYWORD')
        return NodoRetorno(self.expression())

    def statement(self):
        actual = self.obtener_token_actual()
        nodo = None
        match actual[0]:
            case "DATATYPE":
                nodo = self.declaration()
                self.coincidir("DELIMITER")
            case "IDENTIFIER":
                nodo = self.assignment()
                self.coincidir("DELIMITER")
            case "KEYWORD":
                match actual[1]:
                    case "if":
                        nodo = self.if_else()
                    case "while":
                        nodo = self.wh_loop()
                    case "for":
                        nodo = self.f_loop()
                    case "print":
                        nodo = self.f_print()
                        self.coincidir("DELIMITER")
        return nodo

    def if_else(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        condicion = self.condition()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        bloque = self.block()
        self.coincidir("DELIMITER")
        nodoElse = None
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == "else":
            self.coincidir("KEYWORD")
            self.coincidir("DELIMITER")
            bloqueElse = self.block()
            nodoElse = NodoElse(bloqueElse)
            self.coincidir("DELIMITER")
        return NodoIf(condicion, bloque, nodoElse)

    def  block(self):
        instrucciones = []
        while self.obtener_token_actual() and self.obtener_token_actual()[0] != "DELIMITER":
            if self.obtener_token_actual()[1]=="return":
                break
            instrucciones.append(self.statement())
        return instrucciones

    def wh_loop(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        condicion = self.condition()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        bloque = self.block()
        self.coincidir("DELIMITER")
        return NodoWhile(condicion, bloque)

    def f_loop(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "IDENTIFIER":
            expresionI = self.assignment()
        else:
            expresionI = self.declaration()
        self.coincidir("DELIMITER")
        condicion = self.condition()
        self.coincidir("DELIMITER")
        expresionF = self.expression()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        bloque = self.block()
        self.coincidir("DELIMITER")
        return NodoFor(expresionI, condicion, expresionF, bloque)

    def f_print(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        self.expression()
        self.coincidir("DELIMITER")

    def condition(self):
        operando1 = ("","")
        operador = ("","")
        operando2 = ("","")
        if self.obtener_token_actual():
            if self.obtener_token_actual()[1] == "!":
                operador = self.coincidir("LOGICAL")
                operando1 = self.condition()
                nodo = NodoCondicion(operando1, operador)
                return nodo   

        operando1 = self.expression()
        if self.obtener_token_actual():
            if self.obtener_token_actual()[0] == "RELATIONAL": 
                operador = self.coincidir("RELATIONAL")
                operando2 = self.expression()
                nodo = NodoRelacional(operando1, operador, operando2)
            if self.obtener_token_actual()[0] == "LOGICAL":
                operando1 = nodo
                operador = self.coincidir("LOGICAL")
                operando2 = self.condition()
                nodo = NodoCondicion(operando1, operador, operando2)
        return nodo
    
    def declaration(self):
        self.coincidir("DATATYPE")
        var = NodoIdentificador(self.coincidir("IDENTIFIER"))
        self.coincidir("ASSIGNMENT")
        expresion = self.expression()
        return NodoAsignacion(var, expresion)
        
    def assignment(self):
        var = NodoIdentificador(self.coincidir("IDENTIFIER"))
        expresion = ("","")
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "ASSIGNMENT":
            self.coincidir("ASSIGNMENT")
            expresion = self.expression()
        elif self.obtener_token_actual() and self.obtener_token_actual()[0] == "INCREMENT":
            expresion = NodoIncrement(var, self.coincidir("INCREMENT"))
            return expresion
        return NodoAsignacion(var, expresion)

    def expression(self):
        nodo = ("","")
        siguiente = self.obtener_token_actual()[0]
        if siguiente in ["IDENTIFIER", "NUMBER", "STRING"]:
            val = self.coincidir(siguiente)
            match siguiente:
                case "IDENTIFIER":
                    nodo = NodoIdentificador(val)
                case "NUMBER":
                    nodo = NodoNumero(val)
                case "STRING":
                    nodo = NodoString(val)
            if siguiente == "IDENTIFIER" and self.obtener_token_actual() and self.obtener_token_actual()[0] == "INCREMENT":
                expresion = NodoIncrement(nodo, self.coincidir("INCREMENT"))
                return expresion
            if self.obtener_token_actual() and self.obtener_token_actual()[0] == "ARITHMETIC":
                operador = self.coincidir("ARITHMETIC")
                expresion = self.expression()
                return NodoOperacion(nodo, operador, expresion) 
            return nodo  
    
text = """
void main(){
}

int suma(int a, int b) {
    int c = a + b;
    a = 10 + 5 + b + c;
    if (a + 5 == 10){
        a--;
    } else {
        b = 5 - 4;
    }
    while(45 ||  b <= 10 && a == 48){
        int c = 5;
    }
    return c;
}
"""

text = """
void main(){
    
}

int suma(int a, int b) {
    if (a + 5 == 10 || a){
        a = "Hello";
    }
    float b = 4.56;
    while(45 ||  b <= 10 && a == 48){
        int c = 5;
    }
    a = 5;
    for (int i = 5; i <= 10; i--){
        a++;
        print(a);
    print(5);
    print("hello");
    }
    return c;
}
"""
text = """
void main(){
    
}

int suma(int a, int b) {
    a = 5 + b;

    for (int i = 5; i <= 10; i++){
        a++;
    }
    return a;  
}
"""

""" 
    if (a + b == 5){
        c = 10 + b;
    } else {
        c = 5 + b;
    }
"""

def printAst(node:NodoAST):
    obj = {}
    if isinstance(node, NodoPrograma):
        obj = {'Programa':'Programa',
                'Funciones':[printAst(f) for f in node.funciones]}
    elif isinstance(node, NodoFuncion):
        obj = {'Funcion':node.nombre[1],
                'Parametros': [printAst(p) for p in node.parametros],
                'Cuerpo': [printAst(c) for c in node.cuerpo]
                }
    elif isinstance(node, NodoParametro):
        obj = {'Tipo':node.tipo[1],
                'Nombre': node.nombre[1]}
    elif isinstance(node, NodoAsignacion):
        obj = {'Variable':{'id':printAst(node.nombre),
                'Expresion':printAst(node.expresion)}
                }
        #print(node.assembly())
    elif isinstance(node, NodoOperacion):
        obj = {'Operando1':printAst(node.operando1),
                'Operador':node.operador[1],
                'Operando2': printAst(node.operando2)}
    elif isinstance(node, NodoExpresion):
        obj = {'Valor': node.value[1],
                'Expresion': printAst(node.expression)}
    elif isinstance(node,NodoCondicion):
        obj = {'Expresion1':printAst(node.operando1),
                'Operador':node.operador[1],
                'Expresion2': printAst(node.operando2)}
    elif isinstance(node, NodoRelacional):
        obj = {'Expresion1':printAst(node.operando1),
                'Comparador':node.operador[1],
                'Expresion2': printAst(node.operando2)}
    elif isinstance(node, NodoIncrement):
        obj = {f'id: {node.id}':{'Operador': node.operador[1]}}
    elif isinstance(node, NodoIf):
        obj = {'if':{'Condicion':printAst(node.condicion),
               'CuerpoIf': [printAst(b) for b in node.bloque],
               'Else': printAst(node.elseNode)}}
        #print(node.assembly())
    elif isinstance(node, NodoElse):
        obj = {'CuerpoElse': [printAst(b) for b in node.bloque]}
    elif isinstance(node, NodoWhile):
        obj = {'while': {'Condicion':printAst(node.condicion),
                         'CuerpoWhile': [printAst(b) for b in node.bloque]
                         }}
        #print(node.assembly())
    elif isinstance(node, NodoFor):
        obj = {'for':{'Variable':printAst(node.var),
                      'Condicion':printAst(node.condicion),
                      'Expresion':printAst(node.expresion),
                      'CuerpoFor':[printAst(b) for b in node.bloque]}
               }
        print(node.assembly())
    elif isinstance(node, NodoRetorno):
        obj = {'return':printAst(node.expresion)}
    elif isinstance(node, NodoIdentificador):
        obj = {'Id':node.nombre[1]}
    elif isinstance(node, NodoNumero):
        obj = {'Val':node.valor[1]}
    elif isinstance(node, NodoString):
        obj = {'Val': node.valor[1]}
    return obj


tokens = indentificar_tokens(text)
print(tokens)
parser = Parser(tokens)
root = NodoPrograma(parser.parse())

f = open("arbol.json", "w")
f.write(json.dumps(printAst(root), indent = 1))
f.close()
print("Finalizacion sin errores")