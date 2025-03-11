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
        self.condition()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        self.block()
        self.coincidir("DELIMITER")
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == "else":
            self.coincidir("KEYWORD")
            self.coincidir("DELIMITER")
            self.block()
            self.coincidir("DELIMITER")

    def  block(self):
        while self.obtener_token_actual() and self.obtener_token_actual()[0] != "DELIMITER":
            if self.obtener_token_actual()[1]=="return":
                break
            self.statement()

    def wh_loop(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        self.condition()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        self.block()
        self.coincidir("DELIMITER")

    def f_loop(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "IDENTIFIER":
            self.assignment()
        else:
            self.declaration()
        self.coincidir("DELIMITER")
        self.condition()
        self.coincidir("DELIMITER")
        self.expression()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        self.block()
        self.coincidir("DELIMITER")

    def f_print(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        self.expression()
        self.coincidir("DELIMITER")

    def condition(self):
        operando1 = self.expression()
        operador = ("" "")
        operando2 = ("" "")
        if self.obtener_token_actual():
            if self.obtener_token_actual()[0] == "RELATIONAL": 
                operador = self.coincidir("RELATIONAL")
                operando2 = self.expression()
            if self.obtener_token_actual()[0] == "LOGICAL":
                operador = self.coincidir("LOGICAL")
                operando2 = self.condition()
        return NodoCondicion(operando1, operador, operando2)
    
    def declaration(self):
        self.coincidir("DATATYPE")
        var = self.coincidir("IDENTIFIER")
        self.coincidir("ASSIGNMENT")
        expresion = self.expression()
        return NodoAsignacion(var, expresion)
        
    def assignment(self):
        var = self.coincidir("IDENTIFIER")
        expresion = ("","")
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "ASSIGNMENT":
            self.coincidir("ASSIGNMENT")
            expresion = self.expression()
        elif self.obtener_token_actual() and self.obtener_token_actual()[0] == "INCREMENT":
            expresion = self.coincidir("INCREMENT")
        return NodoAsignacion(var, expresion)

    def expression(self):
        siguiente = self.obtener_token_actual()[0] 
        if self.obtener_token_actual and (self.obtener_token_actual()[0]== "IDENTIFIER" or self.obtener_token_actual()[0] == "NUMBER" or self.obtener_token_actual()[0] == "STRING"): 
            val = self.coincidir(siguiente)
            if siguiente == "IDENTIFIER" and self.obtener_token_actual() and self.obtener_token_actual()[0] == "INCREMENT":
                expresion = self.coincidir("INCREMENT")
                return NodoExpresion(val, expresion)
            if self.obtener_token_actual() and self.obtener_token_actual()[0] == "ARITHMETIC":
                operador = self.coincidir("ARITHMETIC")
                expresion = self.expression()
                return NodoOperacion(val, operador, expresion)   
    
text = """
void main(){
}

int suma(int a, int b) {
    int c = a + b;
    a = 10 + 5 + b + c;
    if (a + 5 == 10){
        a;
    }
    return c;
}
"""

#text = """
#void main(){
#    
#}
#
#int suma(int a, int b) {
#    if (a + 5 == 10 || a){
#        a = "Hello";
#    }
#    float b = 4.56;
#    while(45 ||  b <= 10 && a == 48){
#        int c = 5;
#    }
#    a = 5;
#    for (int i = 5; i <= 10; i--){
#        a++;
#        print(a);
#    print(5);
#    print("hello");
#    }
#    return c;
#}
#"""


def printAst(node:NodoAST):
    if isinstance(node, NodoPrograma):
        return {'Programa':'Programa',
                'Funciones':[printAst(f) for f in node.funciones]}
    elif isinstance(node, NodoFuncion):
        return {'Funcion':node.nombre[1],
                'Parametros': [printAst(p) for p in node.parametros],
                'Cuerpo': [printAst(c) for c in node.cuerpo]
                }
    elif isinstance(node, NodoParametro):
        return {'Tipo':node.tipo[1],
                'Nombre': node.nombre[1]}
    elif isinstance(node, NodoAsignacion):
        return {'Variable':node.nombre[1],
                'Expresion':printAst(node.expresion)
                }
    elif isinstance(node, NodoAsignacion):
        return {'Variable': node.nombre[1],
                'Expresion':printAst(node.expresion)
                }
    elif isinstance(node, NodoOperacion):
        return {'Operando1':node.operando1[1],
                'Operador':node.operador[1],
                'Operando2': printAst(node.operando2)}
    elif isinstance(node, NodoExpresion):
        return {'Valor': node.value[1],
                'Expresion': printAst(node.expression)}
    return {}


tokens = indentificar_tokens(text)
print(tokens)
parser = Parser(tokens)
root = NodoPrograma(parser.parse())
print(json.dumps(printAst(root), indent = 1))
print("Finalizacion sin errores")