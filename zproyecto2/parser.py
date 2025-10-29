# parser.py
from collections import deque
import grammar as Gmod
import table as Tmod
from lexer import Token

EPS = 'ε'
ENDMARK = '$'

# Mapeo legible para mostrar tokens esperados en mensajes de error
# Para terminales que ya son símbolos literales en la gramática devolvemos
# su representación de programador (por ejemplo KEYWORD_def -> "def", COMMA -> ",").
READABLE = {
    'COLON': ':',
    'COMMA': ',',
    'DOT': '.',
    'LPAR': '(',
    'RPAR': ')',
    'LBRACK': '[',
    'RBRACK': ']',
    'LBRACE': '{',
    'RBRACE': '}',
    'ASSIGN': '=',
    'NEWLINE': 'NEWLINE',
    'INDENT': 'INDENT',
    'DEDENT': 'DEDENT',
    'EOF': 'EOF',
    'ID': 'identifier',
    'INT': 'integer',
    'FLOAT': 'float',
    'STRING': 'string',
    'BINOP': 'operator',
}

def token_to_terminal(token):
    """
    Convierte un token (tipo, lexema) a un terminal de la gramática.
    Usa token_to_grammar_terminal de grammar.py para keywords.
    Normaliza OP/CMP a BINOP para este subconjunto.
    """
    ttype = token.type
    lex = token.lexeme
    if ttype == 'KEYWORD':
        return f"KEYWORD_{lex}"
    if ttype == 'OP' or ttype == 'CMP':
        return 'BINOP'
    # tipos ya coincidentes
    return ttype

def readable_of_terminal(term):
    """Devuelve una representación legible para mostrar en mensajes de error."""
    if term in READABLE:
        return READABLE[term]
    if term.startswith('KEYWORD_'):
        return term.split('KEYWORD_', 1)[1]
    return term

def format_token_error(token, expected_list):
    """
    Formatea el mensaje de error sintáctico:
    <linea, col> Error sintactico: se encontro: "<lexema>"; se esperaba: "t1", "t2", ...
    Para errores específicos de indentación se usa: <linea, col>Error sintactico: falla de indentacion
    """
    # Manejar caso especial: INDENT/DEDENT/indentation failures are normally lexer's job.
    if expected_list == ['INDENTATION_ERROR']:
        return f"<{token.line}, {token.col}>Error sintactico: falla de indentacion"
    lex = token.lexeme.replace('"', '\\"')
    expected_fmt = ', '.join(f'"{e}"' for e in expected_list)
    return f'<{token.line}, {token.col}> Error sintactico: se encontro: "{lex}"; se esperaba: {expected_fmt}.'

def gather_expected_for_nonterminal(nonterminal, table):
    """
    Dado un no terminal y la tabla predictiva devuelve la lista de tokens esperados (legible).
    """
    expected_terms = Tmod.expected_tokens_for_nonterminal(nonterminal, table)
    # Convertir a representación legible
    readable = [readable_of_terminal(t) for t in expected_terms]
    return readable if readable else [readable_of_terminal('EOF')]

def parse(tokens, table, grammar, start_symbol, debug=False):
    from collections import deque

    stack = deque()
    stack.append('EOF')
    stack.append(start_symbol)

    cursor = 0
    n = len(tokens)
    if n == 0:
        return False, '<0, 0> Error sintactico: se encontro: ""; se esperaba: "EOF".'

    if tokens[-1].type != 'EOF':
        tokens = tokens + [Token('EOF', '<EOF>', tokens[-1].line, tokens[-1].col + 1)]
        n += 1

    applied_productions = []

    while stack:
        top = stack.pop()
        cur = tokens[cursor]
        cur_term = token_to_terminal(cur)

        if debug:
            print(f"[DEBUG] stack_top={top}  cur=({cursor}){cur.type}:{cur.lexeme}  cur_term={cur_term}")

        if top == EPS:
            continue

        if top not in grammar:
            if top == cur_term:
                cursor += 1
                if top == 'EOF':
                    return True, "El analisis sintactico ha finalizado exitosamente.", applied_productions
                continue
            else:
                expected = [readable_of_terminal(top)]
                msg = format_token_error(cur, expected)
                return False, msg, []
        else:
            key = (top, cur_term)
            prod = table.get(key)
            if prod is None:
                expected = Tmod.expected_tokens_for_nonterminal(top, table)
                expected_readable = [readable_of_terminal(t) for t in expected] or [readable_of_terminal('EOF')]
                msg = format_token_error(cur, expected_readable)
                return False, msg, []
            applied_productions.append((top, prod))
            for sym in reversed(prod):
                if sym != EPS:
                    stack.append(sym)

        if cursor >= n:
            last = tokens[-1]
            return False, format_token_error(last, [readable_of_terminal('EOF')]), []

    if cursor < n and tokens[cursor].type == 'EOF':
        return True, "El analisis sintactico ha finalizado exitosamente.", applied_productions
    if cursor >= n:
        return True, "El analisis sintactico ha finalizado exitosamente.", applied_productions

    cur = tokens[cursor]
    return False, format_token_error(cur, [readable_of_terminal('EOF')]), []



# Módulo ejecutable para pruebas rápidas integradas
if __name__ == "__main__":
    # Ejemplo de uso integrando lexer, table y grammar
    from lexer import tokenize, LexerError
    import table as T
    import grammar as G

    src = """def foo(x):
    if x > 0:
        return x + 1
    else:
        return 0
"""
    try:
        toks = tokenize(src)
    except LexerError as e:
        print("LexerError:", e)
        raise

    try:
        table_pred, FIRST, FOLLOW, SELECT = T.build_predictive_table(G.grammar, G.START_SYMBOL)
    except Exception as e:
        print("Error building predictive table:", e)
        raise

    ok, message = parse(toks, table_pred, G.normalize_grammar_for_ll1(G.grammar), G.START_SYMBOL)
    print(message)
