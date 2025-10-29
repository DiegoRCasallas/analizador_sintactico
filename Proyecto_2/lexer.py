from collections import namedtuple
import string

Token = namedtuple("Token", ["tipo", "lexema", "linea", "col"])

class ErrorLexer(Exception):
    pass

PALABRAS_CLAVE = {
    "def", "if", "else", "elif", "while", "for",
    "return", "pass", "break", "continue", "in",
    "and", "or", "not", "True", "False", "None"
}

TOKENS_MULTICARACTER = {
    "OP": ["**", "+", "-", "*", "/", "%"],
    "CMP": ["==", "!=", "<=", ">="],
    "ASSIGN": ["="],
    "SINGLE": [
        "!", "<", ">", ":", ",", ".", "(", ")", "[", "]", "{", "}"
    ]
}

MAPEO_CARACTER_UNICO = {
    ":": "COLON", ",": "COMMA", ".": "DOT", "(": "LPAR", ")": "RPAR",
    "[": "LBRACK", "]": "RBRACK", "{": "LBRACE", "}": "RBRACE",
    "<": "CMP", ">": "CMP", "!": "CMP",
    "+": "OP", "-": "OP", "*": "OP", "/": "OP", "%": "OP",
    "=": "ASSIGN"
}

CARACTERES_INICIO_ID = string.ascii_letters + "_"
CARACTERES_CONTINUACION_ID = string.ascii_letters + string.digits + "_"

def _coincidir_identificador_o_palabra_clave(texto):
    if not texto or texto[0] not in CARACTERES_INICIO_ID:
        return None, 0

    longitud = 1
    while longitud < len(texto) and texto[longitud] in CARACTERES_CONTINUACION_ID:
        longitud += 1

    lexema = texto[:longitud]
    tipo = "KEYWORD" if lexema in PALABRAS_CLAVE else "ID"
    return tipo, lexema

def _coincidir_numero(texto):
    if not texto or texto[0] not in string.digits:
        return None, 0

    tiene_punto = False
    longitud = 0
    while longitud < len(texto) and texto[longitud] in string.digits:
        longitud += 1

    if longitud < len(texto) and texto[longitud] == '.':
        if longitud + 1 < len(texto) and texto[longitud + 1] in string.digits:
            tiene_punto = True
            longitud += 1
            while longitud < len(texto) and texto[longitud] in string.digits:
                longitud += 1
        elif longitud + 1 == len(texto) or texto[longitud+1] not in CARACTERES_CONTINUACION_ID:
             pass
        else:
             pass

    if tiene_punto:
        return "FLOAT", texto[:longitud]
    else:
        return "INT", texto[:longitud]

def _coincidir_cadena(texto):
    if not texto:
        return None, 0

    # Soportar prefijos comunes de cadenas como f"...", r'...', b"...", fr"..." etc.
    prefijo_len = 0
    # limitar prefijo a máximo 2 caracteres para evitar reconocer identificadores largos
    while prefijo_len < 2 and prefijo_len < len(texto) and texto[prefijo_len] in 'frbFRB':
        prefijo_len += 1

    if prefijo_len > 0 and prefijo_len < len(texto) and texto[prefijo_len] in ('\'', '"'):
        inicio_comilla = prefijo_len
    elif texto[0] in ('\'', '"'):
        inicio_comilla = 0
    else:
        return None, 0

    caracter_comilla = texto[inicio_comilla]
    longitud = inicio_comilla + 1
    escapado = False

    while longitud < len(texto):
        caracter = texto[longitud]
        if escapado:
            escapado = False
        elif caracter == '\\':
            escapado = True
        elif caracter == caracter_comilla:
            # devolver el lexema incluyendo el posible prefijo
            return "STRING", texto[:longitud + 1]
        longitud += 1

    return None, 0

def _coincidir_simbolo(texto):
    if not texto:
        return None, 0

    todos_tokens_multicaracter = sorted([
        ('**', 'OP'), ('==', 'CMP'), ('!=', 'CMP'), ('<=', 'CMP'), ('>=', 'CMP'), 
        ('+', 'OP'), ('-', 'OP'), ('*', 'OP'), ('/', 'OP'), ('%', 'OP'),
        ('=', 'ASSIGN'), ('<', 'CMP'), ('>', 'CMP'),
        (':', 'COLON'), (',', 'COMMA'), ('.', 'DOT'),
        ('(', 'LPAR'), (')', 'RPAR'), ('[', 'LBRACK'), (']', 'RBRACK'),
        ('{', 'LBRACE'), ('}', 'RBRACE')
    ], key=lambda x: len(x[0]), reverse=True)

    for lexema_prueba, tipo_prueba in todos_tokens_multicaracter:
        if texto.startswith(lexema_prueba):
            return tipo_prueba, lexema_prueba

    return None, 0


def _obtener_siguiente_token(linea_texto, pos):
    inicio_pos = pos
    while inicio_pos < len(linea_texto) and linea_texto[inicio_pos] in ' \t':
        inicio_pos += 1

    if inicio_pos == len(linea_texto):
        return None, None, inicio_pos

    texto_actual = linea_texto[inicio_pos:]

    tipo, lexema = _coincidir_cadena(texto_actual)
    if tipo:
        return tipo, lexema, inicio_pos + len(lexema)

    if texto_actual.startswith('#'):
        return "COMMENT", texto_actual, len(linea_texto)

    tipo, lexema = _coincidir_identificador_o_palabra_clave(texto_actual)
    if tipo:
        return tipo, lexema, inicio_pos + len(lexema)

    tipo, lexema = _coincidir_numero(texto_actual)
    if tipo:
        return tipo, lexema, inicio_pos + len(lexema)

    tipo, lexema = _coincidir_simbolo(texto_actual)
    if tipo:
        return tipo, lexema, inicio_pos + len(lexema)

    return "MISMATCH", texto_actual[0], inicio_pos + 1


def tokenizar(fuente):
    fuente = fuente.replace('\r\n', '\n').replace('\r', '\n')
    tokens = []
    pila_indentacion = [0]
    lineas = fuente.splitlines(True)
    num_linea = 0

    for linea_cruda in lineas:
        num_linea += 1
        # Ignorar líneas en blanco (no producen tokens). Esto evita NEWLINE extras
        # que rompan el análisis sintáctico en lugares vacíos.
        if linea_cruda.strip() == "":
            continue

        espacios_inicio = 0
        col = 1
        for ch in linea_cruda:
            if ch == " ":
                espacios_inicio += 1
                col += 1
            elif ch == "\t":
                espacios_inicio += 4
                col += 1
            else:
                break
        
        texto_linea_tras_indentacion = linea_cruda[col - 1:]
        
        if espacios_inicio > pila_indentacion[-1]:
            pila_indentacion.append(espacios_inicio)
            tokens.append(Token("INDENT", "<INDENT>", num_linea, 1))
        else:
            while espacios_inicio < pila_indentacion[-1]:
                pila_indentacion.pop()
                tokens.append(Token("DEDENT", "<DEDENT>", num_linea, col))
            if espacios_inicio != pila_indentacion[-1]:
                raise ErrorLexer(f"Error de sangría en línea {num_linea}. Nivel actual: {espacios_inicio}, Esperado: {pila_indentacion[-1]}")
        # Si después del indent/dedent la línea comienza con comentario, no debemos generar
        # un token NEWLINE adicional: las líneas de comentario se ignoran (pero conservamos
        # los tokens INDENT/DEDENT que se hayan emitido anteriormente).
        if texto_linea_tras_indentacion.lstrip().startswith("#"):
            # simplemente omitir la línea de comentario
            continue
        
        pos = col - 1
        texto_linea = linea_cruda.rstrip("\n")

        while pos < len(texto_linea):
            tipo, lexema, siguiente_pos = _obtener_siguiente_token(texto_linea, pos)
            
            if pos < siguiente_pos and all(c in ' \t' for c in texto_linea[pos:siguiente_pos]):
                pos = siguiente_pos
                continue

            if tipo is None:
                break
            
            col_token = pos + 1

            if tipo == "COMMENT":
                pos = len(texto_linea)
                continue
            elif tipo == "MISMATCH":
                 raise ErrorLexer(f"Carácter ilegal {lexema!r} en línea {num_linea} col {col_token}")
            else:
                tokens.append(Token(tipo, lexema, num_linea, col_token))
            
            pos = siguiente_pos

        tokens.append(Token("NEWLINE", "\\n", num_linea, len(texto_linea) + 1))

    while len(pila_indentacion) > 1:
        pila_indentacion.pop()
        tokens.append(Token("DEDENT", "<DEDENT>", num_linea + 1, 1))

    tokens.append(Token("EOF", "<EOF>", num_linea + 1, 1))
    return tokens