import re

class EvaluadorExpresiones:
    def __init__(self, expresion):
        self.expresion_str = expresion
        self.tokens = self.tokenizar(expresion)
        self.index = 0

    def tokenizar(self, expresion):
        token_pattern = re.compile(r'\s*(==|!=|<=|>=|and|or|xor|not|=>|->|\*\*|\*/|//|\*/|>>|<<|[-+*/%()<>[\]]|".*?"|\'.*?\'|[A-Za-z_]\w*|\d*\.?\d*j?)\s*')
        x = token_pattern.findall(expresion)
        y = [i for i in x if i != ""]
        return y

    def obtener_token_actual(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def consumir_token(self):
        token = self.obtener_token_actual()
        self.index += 1
        return token

    def parse_paren(self):
        if self.obtener_token_actual() == '(':
            self.consumir_token()
            result = self.expresion_logica()
            if self.obtener_token_actual() == ')':
                self.consumir_token()
            return result
        else:
            return self.parse_not()

    def parse_not(self):
        if self.obtener_token_actual() == 'not':
            self.consumir_token()
            return 1 if not self.parse_comparison() else 0
        else:
            return self.parse_comparison()

    def parse_pot(self):
        result = self.parse_factor()
        while self.obtener_token_actual() in ('**', '*/'):
            operador = self.consumir_token()
            if operador == '**':
                result = result ** self.parse_pot()
            elif operador == '*/':
                exponente = self.parse_pot()
                if exponente == 0:
                    raise ZeroDivisionError("Raíz con exponente cero")
                result = result ** (1 / exponente)
        return result

    def parse_factor(self):
        token = self.obtener_token_actual()
        if token == '(':
            return self.parse_paren()
        elif token == '-':
            self.consumir_token()
            return -self.parse_factor()
        elif token.startswith('"') or token.startswith("'"):
            return self.cadena()
        elif token == '[':
            return self.lista()
        elif token == 'not':
            return self.parse_not()
        elif re.match(r'\d*\.?\d*j?', token):
            return self.numero()
        else:
            raise ValueError(f"Token inesperado: {token}")

    def parse_term(self):
        result = self.parse_pot()
        while self.obtener_token_actual() in ('*', '/', '%', '//'):
            operador = self.consumir_token()
            if operador == '*':
                result *= self.parse_pot()
            elif operador == '/':
                divisor = self.parse_pot()
                if divisor == 0:
                    raise ZeroDivisionError("División por cero")
                result /= divisor
            elif operador == '%':
                divisor = self.parse_pot()
                if divisor == 0:
                    raise ZeroDivisionError("División por cero")
                result %= divisor
            elif operador == '//':
                divisor = self.parse_pot()
                if divisor == 0:
                    raise ZeroDivisionError("División por cero")
                result //= divisor
        return result

    def parse_expr(self):
        result = self.parse_term()
        while self.obtener_token_actual() in ('+', '-', '>>', '<<'):
            operador = self.consumir_token()
            if operador == '+':
                result += self.parse_term()
            elif operador == '-':
                result -= self.parse_term()
            elif operador == '>>':
                result >>= self.parse_term()
            elif operador == '<<':
                result <<= self.parse_term()
        return result

    def parse_comparison(self):
        result = self.parse_expr()
        while self.obtener_token_actual() in ('==', '!=', '<', '>', '<=', '>='):
            operador = self.obtener_token_actual()
            self.consumir_token()
            right = self.parse_expr()
            if operador == '==':
                result = 1 if result == right else 0
            elif operador == '!=':
                result = 1 if result != right else 0
            elif operador == '<':
                result = 1 if result < right else 0
            elif operador == '>':
                result = 1 if result > right else 0
            elif operador == '<=':
                result = 1 if result <= right else 0
            elif operador == '>=':
                result = 1 if result >= right else 0
        return result

    def expresion_logica(self):
        result = self.parse_comparison()
        while self.obtener_token_actual() in ('and', 'or', 'xor'):
            operador = self.consumir_token()
            right = self.parse_comparison()
            if operador == 'and':
                result = 1 if result and right else 0
            elif operador == 'or':
                result = 1 if result or right else 0
            elif operador == 'xor':
                result = 1 if (result and not right) or (not result and right) else 0

        return result

    def numero(self):
        token = self.consumir_token()
        try:
            if 'j' in token:
                return complex(token)
            elif '.' in token:
                return float(token)
            else:
                return int(token)
        except ValueError:
            raise ValueError(f"Número inválido: {token}")

    def cadena(self):
        token = self.consumir_token()
        return token[1:-1]  # Remover las comillas al inicio y al final

    def lista(self):
        self.consumir_token()  # consumir '['
        elementos = []
        while self.obtener_token_actual() != ']':
            elementos.append(self.expresion_logica())
            if self.obtener_token_actual() == ',':
                self.consumir_token()
        self.consumir_token()  # consumir ']'
        if self.obtener_token_actual() == '[':
            return self.lista_con_indice(elementos)
        return elementos

    def lista_con_indice(self, lista):
        while self.obtener_token_actual() == '[':
            self.consumir_token()  # consumir '['
            indice = self.expresion_logica()
            lista = lista[indice]
            if self.obtener_token_actual() == ']':
                self.consumir_token()  # consumir ']'
        return lista


def evaluar_expresion(expresion):
    evaluador = EvaluadorExpresiones(expresion)
    return evaluador.expresion_logica()
