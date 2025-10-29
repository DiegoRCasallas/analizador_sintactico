# lexer_no_regex.py
from collections import namedtuple
import string

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

class LexerError(Exception):
    """Excepción personalizada para errores del lexer."""
    pass

# Palabras clave y tipos de token
KEYWORDS = {
    "def", "if", "else", "elif", "while", "for",
    "return", "pass", "break", "continue", "in",
    "and", "or", "not", "True", "False", "None"
}

# Operadores y delimitadores de múltiples y un solo carácter.
# El orden es **CRUCIAL** aquí, ya que el tokenizador intentará hacer coincidir
# las cadenas más largas primero (por ejemplo, '==' antes que '=').
MULTI_CHAR_TOKENS = {
    "OP": ["**", "+", "-", "*", "/", "%"],
    "CMP": ["==", "!=", "<=", ">="],
    "ASSIGN": ["="], # Se deja aquí por simplicidad aunque solo sea un carácter
    "SINGLE": [
        "!", "<", ">", ":", ",", ".", "(", ")", "[", "]", "{", "}"
    ]
}

# Aplanamos los tokens de un solo carácter para una búsqueda más rápida,
# pero aún necesitamos mantener los de múltiples caracteres por separado.
SINGLE_CHAR_MAP = {
    ":": "COLON", ",": "COMMA", ".": "DOT", "(": "LPAR", ")": "RPAR",
    "[": "LBRACK", "]": "RBRACK", "{": "LBRACE", "}": "RBRACE",
    "<": "CMP", ">": "CMP", "!": "CMP", # '<', '>' y '!' son CMP si no son parte de un token doble
    "+": "OP", "-": "OP", "*": "OP", "/": "OP", "%": "OP",
    "=": "ASSIGN" # Se trata como ASSIGN si no se encuentra '=='
}

# Caracteres válidos para ID
ID_START_CHARS = string.ascii_letters + "_"
ID_CONTINUE_CHARS = string.ascii_letters + string.digits + "_"

def _match_identifier_or_keyword(text):
    """Intenta hacer coincidir un ID o una KEYWORD."""
    if not text or text[0] not in ID_START_CHARS:
        return None, 0

    length = 1
    while length < len(text) and text[length] in ID_CONTINUE_CHARS:
        length += 1

    lexeme = text[:length]
    typ = "KEYWORD" if lexeme in KEYWORDS else "ID"
    return typ, lexeme

def _match_number(text):
    """Intenta hacer coincidir un INT o un FLOAT."""
    if not text or text[0] not in string.digits:
        return None, 0

    has_dot = False
    length = 0
    while length < len(text) and text[length] in string.digits:
        length += 1

    # Revisar por un punto decimal para FLOAT
    if length < len(text) and text[length] == '.':
        # Asegurarse de que haya dígitos después del punto
        if length + 1 < len(text) and text[length + 1] in string.digits:
            has_dot = True
            length += 1
            while length < len(text) and text[length] in string.digits:
                length += 1
        elif length + 1 == len(text) or text[length+1] not in ID_CONTINUE_CHARS:
             # Si el '.' es el último carácter o le sigue algo no permitido para un número,
             # asumimos que es el token 'DOT' y volvemos al INT
             pass
        else:
             # Caso como 1.foo - el '.' es parte del número hasta ahora,
             # pero no va seguido de un dígito, por lo que podría ser un error
             # o el '.' podría ser un DOT, pero el lexer es greedier.
             # Para simplificar y seguir la lógica de un lexer simple:
             # Si no hay dígitos después del punto, no es un float completo aquí.
             # Si terminamos justo después del punto, emitir el INT
             # y dejar que el bucle principal maneje el DOT.
             pass

    # Si se detuvo en un '.', volvemos al estado de solo INT
    if has_dot:
        return "FLOAT", text[:length]
    else:
        return "INT", text[:length]

def _match_string(text):
    """Intenta hacer coincidir un literal de STRING (con comillas simples o dobles)."""
    if not text or text[0] not in ('\'', '\"'):
        return None, 0

    quote_char = text[0]
    length = 1
    escaped = False

    while length < len(text):
        char = text[length]
        if escaped:
            # Cualquier cosa después de un '\' es tratada como parte de la cadena
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == quote_char:
            # Fin de la cadena
            return "STRING", text[:length + 1]
        
        length += 1

    # Cadena no terminada (Error de Lexer, pero devolvemos lo que tenemos para manejo externo)
    return None, 0 # El bucle principal manejará el MISMATCH

def _match_symbol(text):
    """Intenta hacer coincidir símbolos (OP, CMP, ASSIGN, delimitadores)."""
    if not text:
        return None, 0

    # 1. Intentar coincidencias de múltiples caracteres (Crucial: orden de las cadenas más largas primero)
    for token_type, tokens in MULTI_CHAR_TOKENS.items():
        # Simplificación: combinamos los tokens de MULTI_CHAR_TOKENS en una sola lista,
        # ordenados por longitud descendente para asegurar la coincidencia de las cadenas más largas
        # (ej. '==' antes que '=')

        # Esto es lo que se tiene que hacer:
        all_multi_tokens = sorted([
            ('**', 'OP'), ('==', 'CMP'), ('!=', 'CMP'), ('<=', 'CMP'), ('>=', 'CMP'), 
            ('+', 'OP'), ('-', 'OP'), ('*', 'OP'), ('/', 'OP'), ('%', 'OP'),
            ('=', 'ASSIGN'), ('<', 'CMP'), ('>', 'CMP'),
            (':', 'COLON'), (',', 'COMMA'), ('.', 'DOT'),
            ('(', 'LPAR'), (')', 'RPAR'), ('[', 'LBRACK'), (']', 'RBRACK'),
            ('{', 'LBRACE'), ('}', 'RBRACE')
        ], key=lambda x: len(x[0]), reverse=True)

        for lexeme_test, typ_test in all_multi_tokens:
            if text.startswith(lexeme_test):
                # Caso especial para '*' ya que puede ser OP o parte de '**'
                # Ya hemos comprobado '**' primero.
                # Caso especial para '=' ya que puede ser ASSIGN o parte de '=='
                # Ya hemos comprobado '==' primero.
                return typ_test, lexeme_test

    # Si llega aquí, significa que el símbolo es un solo carácter que no
    # formaba parte de una secuencia de caracteres más larga ya identificada.
    # Dado que ya se comprobó con la lista ordenada, este código ya no es necesario,
    # ya que se cubre en 'all_multi_tokens'. Lo mantenemos solo para claridad.
    # if text[0] in SINGLE_CHAR_MAP:
    #     return SINGLE_CHAR_MAP[text[0]], text[0]

    return None, 0


def _get_next_token(line_text, pos):
    """
    Intenta hacer coincidir el siguiente token en 'line_text' a partir de 'pos'.
    Devuelve (tipo, lexema, nueva_pos) o (None, None, pos) si no hay coincidencia
    (excluyendo SKIP/COMMENT que se manejan en el bucle principal).
    """
    # Siempre omitir espacios en blanco al inicio (SKIP, NEWLINE y COMMENT se manejan afuera)
    start_pos = pos
    while start_pos < len(line_text) and line_text[start_pos] in ' \t':
        start_pos += 1

    if start_pos == len(line_text):
        return None, None, start_pos # Solo espacios o fin de línea

    current_text = line_text[start_pos:]

    # Prioridad: STRING
    typ, lexeme = _match_string(current_text)
    if typ:
        return typ, lexeme, start_pos + len(lexeme)

    # Prioridad: COMENTARIO (solo si es el primer carácter significativo)
    if current_text.startswith('#'):
        return "COMMENT", current_text, len(line_text) # Consumir hasta el final de la línea

    # Prioridad: ID/KEYWORD
    typ, lexeme = _match_identifier_or_keyword(current_text)
    if typ:
        return typ, lexeme, start_pos + len(lexeme)

    # Prioridad: Número (FLOAT o INT)
    typ, lexeme = _match_number(current_text)
    if typ:
        # Los números son difíciles sin regex debido al punto.
        # Volvemos a intentarlo si solo coincide un INT.
        # Si un INT coincide y el siguiente carácter es '.',
        # necesitamos asegurarnos de que no sea parte de un FLOAT que falló,
        # o que no sea un 'DOT'. La lógica de _match_number ya maneja esto
        # buscando dígitos después del '.'.
        return typ, lexeme, start_pos + len(lexeme)

    # Prioridad: SÍMBOLO (OP, CMP, ASSIGN, Delimitadores)
    # **IMPORTANTE**: La lógica de _match_symbol ya garantiza que las coincidencias
    # de varios caracteres (ej., '==') se comprueben antes que los de un solo carácter (ej., '=').
    typ, lexeme = _match_symbol(current_text)
    if typ:
        return typ, lexeme, start_pos + len(lexeme)


    # MISMATCH
    # Si no coincide nada de lo anterior, es un error de token.
    # Tomar el siguiente carácter para el mensaje de error.
    return "MISMATCH", current_text[0], start_pos + 1


# --- Función Principal de Tokenización ---

def tokenize(source):
    """
    Tokeniza la cadena de código fuente similar a Python sin usar regex.

    Devuelve una lista de Token(type, lexeme, line, col), incluyendo tokens INDENT/DEDENT/NEWLINE/EOF.

    Genera LexerError en caracteres ilegales o sangría no coincidente.
    """
    source = source.replace('\r\n', '\n').replace('\r', '\n')
    tokens = []
    indent_stack = [0]  # Pila de niveles de sangría (recuento de espacios)
    lines = source.splitlines(True)  # Mantiene los finales de línea
    line_no = 0

    for raw_line in lines:
        line_no += 1
        # Si la línea es solo un salto de línea (vacío), produce NEWLINE y continúa
        if raw_line.strip() == "":
            tokens.append(Token("NEWLINE", "\\n", line_no, 1))
            continue

        # 1. Manejo de Sangría (Indentación)
        leading = 0
        col = 1
        for ch in raw_line:
            if ch == " ":
                leading += 1
                col += 1
            elif ch == "\t":
                leading += 4
                col += 1
            else:
                break
        
        # El resto de la línea después de la sangría
        line_text_after_indent = raw_line[col - 1:]

        # Si la línea, después de la sangría, comienza con comentario, tratar como NEWLINE (sin cambio de sangría)
        if line_text_after_indent.lstrip().startswith("#"):
            # Buscar el fin del comentario para saber la columna del NEWLINE
            comment_end_col = len(raw_line.rstrip('\n')) + 1
            tokens.append(Token("NEWLINE", "\\n", line_no, comment_end_col))
            continue
        
        # INDENT / DEDENT handling
        if leading > indent_stack[-1]:
            indent_stack.append(leading)
            tokens.append(Token("INDENT", "<INDENT>", line_no, 1))
        else:
            while leading < indent_stack[-1]:
                indent_stack.pop()
                # Columna del DEDENT es el inicio de la línea lógica (col)
                tokens.append(Token("DEDENT", "<DEDENT>", line_no, col))
            if leading != indent_stack[-1]:
                raise LexerError(f"Error de sangría en línea {line_no}. Nivel actual: {leading}, Esperado: {indent_stack[-1]}")
        
        # 2. Tokenizar el resto de la línea
        pos = col - 1 # Posición de inicio después de la sangría
        line_text = raw_line.rstrip("\n")

        while pos < len(line_text):
            typ, lexeme, next_pos = _get_next_token(line_text, pos)
            
            # Esto maneja 'SKIP' (espacios intermedios) y el avance de posición
            if pos < next_pos and all(c in ' \t' for c in line_text[pos:next_pos]):
                pos = next_pos
                continue

            if typ is None:
                # Si _get_next_token devuelve None, significa que solo había espacios restantes
                break # Fin de la línea lógica
            
            # La columna del token es la posición de inicio (1-based)
            token_col = pos + 1

            if typ == "COMMENT":
                # La lógica de _get_next_token ya consumió hasta el final de la línea.
                pos = len(line_text) # Ir al final de la línea
                continue
            elif typ == "MISMATCH":
                 raise LexerError(f"Carácter ilegal {lexeme!r} en línea {line_no} col {token_col}")
            else:
                tokens.append(Token(typ, lexeme, line_no, token_col))
            
            pos = next_pos # Avanzar a la posición después del token

        # Al final de una línea lógica, emitir NEWLINE
        tokens.append(Token("NEWLINE", "\\n", line_no, len(line_text) + 1))

    # 3. Después de todas las líneas, desenrollar las sangrías restantes
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "<DEDENT>", line_no + 1, 1))

    # 4. Token EOF
    tokens.append(Token("EOF", "<EOF>", line_no + 1, 1))
    return tokens