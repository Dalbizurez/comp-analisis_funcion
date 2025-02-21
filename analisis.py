import re

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
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
            self.funcion()
    
    # Analizar la funcion en base a la estructura
    def funcion(self):
        self.coincidir("DATATYPE")
        self.coincidir("IDENTIFIER")
        self.coincidir("DELIMITER")
        self.parametros()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        self.cuerpo()
        self.coincidir("DELIMITER")
        
    def parametros(self):
        self.coincidir("DATATYPE")
        self.coincidir("IDENTIFIER")
        if self.obtener_token_actual()[1] and self.obtener_token_actual()[1] == ',':
            self.coincidir("DELIMITER")
            self.parametros()
    
    def cuerpo(self):
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != "return":
            self.statement()
        self.coincidir('KEYWORD')
        self.coincidir("IDENTIFIER")

    def statement(self):
        actual = self.obtener_token_actual()
        match actual[0]:
            case "DATATYPE":
                self.declaration()
                self.coincidir("DELIMITER")
            case "IDENTIFIER":
                self.assignment()
                self.coincidir("DELIMITER")
            case "KEYWORD":
                match actual[1]:
                    case "if":
                        self.if_else()
                    case "while":
                        self.wh_loop()
                    case "for":
                        self.f_loop()
                    case "print":
                        self.f_print()
                        self.coincidir("DELIMITER")

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
        self.expression()
        if self.obtener_token_actual():
            if self.obtener_token_actual()[0] == "RELATIONAL": 
                self.coincidir("RELATIONAL")
                self.expression()
            if self.obtener_token_actual()[0] == "LOGICAL":
                self.coincidir("LOGICAL")
                self.condition()
    
    def declaration(self):
        self.coincidir("DATATYPE")
        self.coincidir("IDENTIFIER")
        self.coincidir("ASSIGNMENT")
        self.expression()
        

    def assignment(self):
        self.coincidir("IDENTIFIER")
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "ASSIGNMENT":
            self.coincidir("ASSIGNMENT")
            self.expression()
        elif self.obtener_token_actual() and self.obtener_token_actual()[0] == "INCREMENT":
            self.coincidir("INCREMENT")

    def expression(self):
        siguiente = self.obtener_token_actual()[0] 
        if self.obtener_token_actual and (self.obtener_token_actual()[0]== "IDENTIFIER" or self.obtener_token_actual()[0] == "NUMBER" or self.obtener_token_actual()[0] == "STRING"): 
            self.coincidir(siguiente)
            if siguiente == "IDENTIFIER" and self.obtener_token_actual() and self.obtener_token_actual()[0] == "INCREMENT":
                self.coincidir("INCREMENT")
            if self.obtener_token_actual() and self.obtener_token_actual()[0] == "ARITHMETIC":
                self.coincidir("ARITHMETIC")
                self.expression()   
    
#text = """
#int suma(int a, int b) {
#    int c = a + b;
#    a = 10 + 5 + b + c;
#    if (a + 5 == 10){
#        a;
#    }
#    return c;
#}
#"""

text = """
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

tokens = indentificar_tokens(text)
print(tokens)
parser = Parser(tokens)
parser.parse()
print("Finalizacion sin errores")