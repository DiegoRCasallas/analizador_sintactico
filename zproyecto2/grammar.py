# grammar.py
from copy import deepcopy

# Símbolo para epsilon
EPS = 'ε'

# Start symbol
START_SYMBOL = 'program'

# Gramática inicial (subconjunto) corregida y factorizada
# Cobertura: funciones (def), condicionales (if/elif/else), ciclos (while, for),
# declaraciones simples (asignación), expresiones aritméticas básicas, bloques por indentación,
# llamadas simples y literales (INT, FLOAT, STRING), listas y paréntesis.
#
# Notas de diseño relevantes aplicadas:
# - Factorización de producciones que compartían prefijo ID (term + call -> ID term_prime)
# - Reescritura de la estructura if/elif/else para evitar conflictos SELECT usando elif_star
# - Las keywords se representan como terminales 'KEYWORD_xxx' (p. ej. KEYWORD_def)
# - EPS se usa para epsilon
grammar = {
    # Programa: lista de sentencias seguida de EOF
    'program': [
        ['stmt_list', 'EOF']
    ],

    # Lista de sentencias: cero o más sentencias
    'stmt_list': [
        ['stmt', 'stmt_list'],
        [EPS]
    ],

    # Sentencia: simple o compuesta
    'stmt': [
        ['simple_stmt'],
        ['compound_stmt']
    ],

    # Sentencia simple: small_stmt NEWLINE
    'simple_stmt': [
        ['small_stmt', 'NEWLINE']
    ],
    'small_stmt': [
        ['ID', 'small_stmt_tail'],      # identificador -> decide entre asignacion o expresion que comienza con ID
        ['literal', 'expr_tail'],       # expresion que inicia con literal seguida de posibles operadores
        ['LPAR', 'expr', 'RPAR', 'expr_tail'],  # (expr) seguido de posibles operadores
        ['KEYWORD_pass'],
        ['KEYWORD_break'],
        ['KEYWORD_continue'],
        ['KEYWORD_return', 'expr_opt']  # return también se mantiene como small_stmt completo
    ],
        'small_stmt_tail': [
        ['ASSIGN', 'expr'],                     # asignacion: ID = expr
        ['term_prime', 'expr_tail']             # expr que empezó con ID: ID term_prime expr_tail
    ],

    'return_stmt': [
        ['KEYWORD_return', 'expr_opt']
    ],

    'expr_opt': [
        ['expr'],
        [EPS]
    ],

    'pass_stmt': [
        ['KEYWORD_pass']
    ],

    'break_stmt': [
        ['KEYWORD_break']
    ],

    'continue_stmt': [
        ['KEYWORD_continue']
    ],

    # target simplificado: ID (no destructuring)
    'target': [
        ['ID']
    ],

    # Expresiones: expr -> term expr_tail
    'expr': [
        ['term', 'expr_tail']
    ],

    'expr_tail': [
        ['BINOP', 'term', 'expr_tail'],
        [EPS]
    ],

    # term factorizado para evitar conflicto entre ID y call
    'term': [
        ['literal'],
        ['ID', 'term_prime'],
        ['list_literal'],
        ['LPAR', 'expr', 'RPAR']
    ],

    'term_prime': [
        ['LPAR', 'arg_list_opt', 'RPAR'],
        [EPS]
    ],

    'call': [
        # Mantener para compatibilidad, pero no se usa directamente (la opción está en term_prime)
        ['ID', 'LPAR', 'arg_list_opt', 'RPAR']
    ],

    'arg_list_opt': [
        ['arg_list'],
        [EPS]
    ],

    'arg_list': [
        ['expr', 'arg_list_tail']
    ],

    'arg_list_tail': [
        ['COMMA', 'expr', 'arg_list_tail'],
        [EPS]
    ],

    'list_literal': [
        ['LBRACK', 'list_elements_opt', 'RBRACK']
    ],

    'list_elements_opt': [
        ['list_elements'],
        [EPS]
    ],

    'list_elements': [
        ['expr', 'list_elements_tail']
    ],

    'list_elements_tail': [
        ['COMMA', 'expr', 'list_elements_tail'],
        [EPS]
    ],

    'literal': [
        ['INT'],
        ['FLOAT'],
        ['STRING'],
        ['KEYWORD_True'],
        ['KEYWORD_False'],
        ['KEYWORD_None']
    ],

    # Sentencias compuestas
    'compound_stmt': [
        ['if_stmt'],
        ['while_stmt'],
        ['for_stmt'],
        ['func_def']
    ],

    # If statement reescrito para evitar conflictos LL(1)
    'if_stmt': [
        ['KEYWORD_if', 'expr', 'COLON', 'suite', 'elif_star', 'else_opt']
    ],

    # cero o más elif_item
    'elif_star': [
        ['elif_item', 'elif_star'],
        [EPS]
    ],

    'elif_item': [
        ['KEYWORD_elif', 'expr', 'COLON', 'suite']
    ],

    'else_opt': [
        ['KEYWORD_else', 'COLON', 'suite'],
        [EPS]
    ],

    'while_stmt': [
        ['KEYWORD_while', 'expr', 'COLON', 'suite']
    ],

    'for_stmt': [
        ['KEYWORD_for', 'ID', 'KEYWORD_in', 'expr', 'COLON', 'suite']
    ],

    # Definición de función
    'func_def': [
        ['KEYWORD_def', 'ID', 'LPAR', 'param_list_opt', 'RPAR', 'COLON', 'suite']
    ],

    'param_list_opt': [
        ['param_list'],
        [EPS]
    ],

    'param_list': [
        ['param', 'param_list_tail']
    ],

    'param_list_tail': [
        ['COMMA', 'param', 'param_list_tail'],
        [EPS]
    ],

    'param': [
        ['ID'],
        ['ID', 'COLON', 'type_annotation']
    ],

    # type_annotation simplificado
    'type_annotation': [
        ['ID'],
        ['LBRACK', 'ID', 'RBRACK']
    ],

    # suite: simple_stmt o NEWLINE INDENT stmt_list DEDENT
    'suite': [
        ['simple_stmt'],
        ['NEWLINE', 'INDENT', 'stmt_list', 'DEDENT']
    ],


}

# --- Terminal mapping helpers -------------------------------------------------
# Lista de terminales nominales (usados por FIRST/FOLLOW y la tabla)
TERMINALS = {
    'KEYWORD_def', 'KEYWORD_if', 'KEYWORD_else', 'KEYWORD_elif', 'KEYWORD_while',
    'KEYWORD_for', 'KEYWORD_return', 'KEYWORD_pass', 'KEYWORD_break', 'KEYWORD_continue',
    'KEYWORD_in', 'KEYWORD_True', 'KEYWORD_False', 'KEYWORD_None',
    'ID', 'INT', 'FLOAT', 'STRING',
    'BINOP', 'CMP', 'ASSIGN', 'COLON', 'COMMA', 'DOT',
    'LPAR', 'RPAR', 'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE',
    'NEWLINE', 'INDENT', 'DEDENT', 'EOF'
}

# Los no terminales se deducen de la gramática
def nonterminals_from_grammar(g):
    return set(g.keys())

NONTERMINALS = nonterminals_from_grammar(grammar)

# --- Utilidades para imprimir/expresar la gramática --------------------------
def productions_list(grammar_dict):
    """Devuelve lista de tuplas (A, prod) para inspección."""
    out = []
    for A, prods in grammar_dict.items():
        for prod in prods:
            out.append((A, prod))
    return out

def pretty_print(grammar_dict):
    """Imprime la gramática de forma legible (string)."""
    lines = []
    for A, prods in grammar_dict.items():
        rhs = [" ".join(p) for p in prods]
        lines.append(f"{A} -> {' | '.join(rhs)}")
    return "\n".join(lines)

# --- Eliminación de recursión izquierda inmediata (producción A -> A alpha | beta) ---
def remove_immediate_left_recursion(g):
    """
    Elimina recursión izquierda inmediata en cada no terminal si existe.
    Devuelve una nueva gramática sin recursión izquierda inmediata.
    (No maneja recursión izquierda indirecta)
    """
    G = deepcopy(g)
    new_G = {}
    for A in G:
        prods = G[A]
        left_recursive = []
        non_recursive = []
        for prod in prods:
            if len(prod) > 0 and prod[0] == A:
                left_recursive.append(prod[1:])  # alpha
            else:
                non_recursive.append(prod)       # beta

        if left_recursive:
            A_prime = A + "_rec"
            new_prods_for_A = []
            for beta in non_recursive:
                # A -> beta A'
                if beta == [EPS]:
                    new_prods_for_A.append([A_prime])
                else:
                    new_prods_for_A.append(beta + [A_prime])
            # A' -> alpha A' | ε
            new_prods_for_A_prime = []
            for alpha in left_recursive:
                new_prods_for_A_prime.append(alpha + [A_prime])
            new_prods_for_A_prime.append([EPS])

            new_G[A] = new_prods_for_A
            new_G[A_prime] = new_prods_for_A_prime
        else:
            new_G[A] = prods
    return new_G

# --- Factorización a la izquierda simple ---
def left_factor(grammar_dict):
    """
    Realiza factorización a la izquierda simple por cada no terminal.
    Implementación básica: para cada A, agrupa producciones que comparten
    prefijo común de longitud 1 y crea un nuevo no terminal.
    Repetir hasta que no haya prefijos simples comunes.
    """
    G = deepcopy(grammar_dict)
    changed = True
    while changed:
        changed = False
        newG = {}
        for A, prods in G.items():
            # Agrupar por primer símbolo
            groups = {}
            for p in prods:
                key = p[0] if len(p) > 0 else EPS
                groups.setdefault(key, []).append(p)
            # Si algún grupo tiene más de 1 producción y key no EPS -> factorizar
            new_prods_for_A = []
            for key, group in groups.items():
                if key != EPS and len(group) > 1:
                    A_fact = A + "_fact"
                    changed = True
                    # A -> key A_fact
                    new_prods_for_A.append([key, A_fact])
                    # A_fact -> rest_of_each | ε (si rest vacía)
                    rest_prods = []
                    for prod in group:
                        if len(prod) > 1:
                            rest_prods.append(prod[1:])
                        else:
                            rest_prods.append([EPS])
                    newG[A_fact] = rest_prods
                else:
                    for prod in group:
                        new_prods_for_A.append(prod)
            newG[A] = new_prods_for_A
        G = newG
    return G

# --- Export / helper to get a normalized grammar ready for FIRST/FOLLOW ---
def normalize_grammar_for_ll1(base_grammar):
    """
    Aplica transformaciones simples: eliminar recursión izquierda inmediata
    y factorizar a la izquierda de forma iterativa.
    Devuelve la gramática transformada.
    """
    g1 = remove_immediate_left_recursion(base_grammar)
    g2 = left_factor(g1)
    return g2

# --- Mapa de palabras clave a terminales concretos --------------------------
def token_to_grammar_terminal(token_type, token_lexeme):
    """
    Convierte (token_type, token_lexeme) a nombre de terminal usado en grammar,
    e.g. ('KEYWORD', 'def') -> 'KEYWORD_def', ('INT', '42') -> 'INT'
    """
    if token_type == 'KEYWORD':
        return f"KEYWORD_{token_lexeme}"
    return token_type

# --- Ejecución rápida para inspección --------------------------------------
if __name__ == "__main__":
    print("Gramática original:")
    print(pretty_print(grammar))
    print("\n--- Normalizando para LL(1) ---\n")
    norm = normalize_grammar_for_ll1(grammar)
    print(pretty_print(norm))
