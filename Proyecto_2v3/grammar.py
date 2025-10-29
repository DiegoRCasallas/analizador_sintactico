from copy import deepcopy

EPS = 'ε'

SIMBOLO_INICIAL = 'programa'

gramatica = {
    'programa': [
        ['lista_sentencias', 'EOF']
    ],

    'lista_sentencias': [
        ['sentencia', 'lista_sentencias'],
        [EPS]
    ],

    'sentencia': [
        ['sentencia_simple'],
        ['sentencia_compuesta']
    ],

    'sentencia_simple': [
        ['sentencia_pequena', 'NEWLINE']
    ],
    'sentencia_pequena': [
        ['ID', 'cola_sentencia_pequena'],
        ['literal', 'cola_expr'],
        ['LPAR', 'expr', 'RPAR', 'cola_expr'],
        ['KEYWORD_pass'],
        ['KEYWORD_break'],
        ['KEYWORD_continue'],
        ['KEYWORD_return', 'expr_opcional']
    ],
        'cola_sentencia_pequena': [
        ['ASSIGN', 'expr'],
        ['cola_termino', 'cola_expr']
    ],

    'sentencia_return': [
        ['KEYWORD_return', 'expr_opcional']
    ],

    'expr_opcional': [
        ['expr'],
        [EPS]
    ],

    'sentencia_pass': [
        ['KEYWORD_pass']
    ],

    'sentencia_break': [
        ['KEYWORD_break']
    ],

    'sentencia_continue': [
        ['KEYWORD_continue']
    ],

    'objetivo': [
        ['ID']
    ],

    'expr': [
        ['termino', 'cola_expr']
    ],

    'cola_expr': [
        ['BINOP', 'termino', 'cola_expr'],
        [EPS]
    ],

    'termino': [
        ['literal'],
        ['ID', 'cola_termino'],
        ['literal_lista'],
        ['LPAR', 'expr', 'RPAR']
    ],

    'cola_termino': [
        ['LPAR', 'lista_args_opcional', 'RPAR'],
        [EPS]
    ],

    'llamada': [
        ['ID', 'LPAR', 'lista_args_opcional', 'RPAR']
    ],

    'lista_args_opcional': [
        ['lista_args'],
        [EPS]
    ],

    'lista_args': [
        ['expr', 'cola_lista_args']
    ],

    'cola_lista_args': [
        ['COMMA', 'expr', 'cola_lista_args'],
        [EPS]
    ],

    'literal_lista': [
        ['LBRACK', 'elementos_lista_opcional', 'RBRACK']
    ],

    'elementos_lista_opcional': [
        ['elementos_lista'],
        [EPS]
    ],

    'elementos_lista': [
        ['expr', 'cola_elementos_lista']
    ],

    'cola_elementos_lista': [
        ['COMMA', 'expr', 'cola_elementos_lista'],
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

    'sentencia_compuesta': [
        ['sentencia_if'],
        ['sentencia_while'],
        ['sentencia_for'],
        ['def_funcion']
    ],

    'sentencia_if': [
        ['KEYWORD_if', 'expr', 'COLON', 'bloque', 'elif_estrella', 'sino_opcional']
    ],

    'elif_estrella': [
        ['item_elif', 'elif_estrella'],
        [EPS]
    ],

    'item_elif': [
        ['KEYWORD_elif', 'expr', 'COLON', 'bloque']
    ],

    'sino_opcional': [
        ['KEYWORD_else', 'COLON', 'bloque'],
        [EPS]
    ],

    'sentencia_while': [
        ['KEYWORD_while', 'expr', 'COLON', 'bloque']
    ],

    'sentencia_for': [
        ['KEYWORD_for', 'ID', 'KEYWORD_in', 'expr', 'COLON', 'bloque']
    ],

    'def_funcion': [
        ['KEYWORD_def', 'ID', 'LPAR', 'lista_params_opcional', 'RPAR', 'COLON', 'bloque']
    ],

    'lista_params_opcional': [
        ['lista_params'],
        [EPS]
    ],

    'lista_params': [
        ['param', 'cola_lista_params']
    ],

    'cola_lista_params': [
        ['COMMA', 'param', 'cola_lista_params'],
        [EPS]
    ],

    'param': [
        ['ID'],
        ['ID', 'COLON', 'anotacion_tipo']
    ],

    'anotacion_tipo': [
        ['ID'],
        ['LBRACK', 'ID', 'RBRACK']
    ],

    'bloque': [
        ['sentencia_simple'],
        ['NEWLINE', 'INDENT', 'lista_sentencias', 'DEDENT']
    ],
}

TERMINALES = {
    'KEYWORD_def', 'KEYWORD_if', 'KEYWORD_else', 'KEYWORD_elif', 'KEYWORD_while',
    'KEYWORD_for', 'KEYWORD_return', 'KEYWORD_pass', 'KEYWORD_break', 'KEYWORD_continue',
    'KEYWORD_in', 'KEYWORD_True', 'KEYWORD_False', 'KEYWORD_None',
    'ID', 'INT', 'FLOAT', 'STRING',
    'BINOP', 'CMP', 'ASSIGN', 'COLON', 'COMMA', 'DOT',
    'LPAR', 'RPAR', 'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE',
    'NEWLINE', 'INDENT', 'DEDENT', 'EOF'
}

def no_terminales_de_gramatica(g):
    return set(g.keys())

NO_TERMINALES = no_terminales_de_gramatica(gramatica)

def lista_producciones(gramatica_dict):
    salida = []
    for A, prods in gramatica_dict.items():
        for prod in prods:
            salida.append((A, prod))
    return salida

def imprimir_bonito(gramatica_dict):
    lineas = []
    for A, prods in gramatica_dict.items():
        rhs = [" ".join(p) for p in prods]
        lineas.append(f"{A} -> {' | '.join(rhs)}")
    return "\n".join(lineas)

def eliminar_recursion_izquierda_inmediata(g):
    G = deepcopy(g)
    nueva_G = {}
    for A in G:
        prods = G[A]
        recursivas = []
        no_recursivas = []
        for prod in prods:
            if len(prod) > 0 and prod[0] == A:
                recursivas.append(prod[1:])
            else:
                no_recursivas.append(prod)

        if recursivas:
            A_prima = A + "_rec"
            nuevas_prods_para_A = []
            for beta in no_recursivas:
                if beta == [EPS]:
                    nuevas_prods_para_A.append([A_prima])
                else:
                    nuevas_prods_para_A.append(beta + [A_prima])
            nuevas_prods_para_A_prima = []
            for alpha in recursivas:
                nuevas_prods_para_A_prima.append(alpha + [A_prima])
            nuevas_prods_para_A_prima.append([EPS])

            nueva_G[A] = nuevas_prods_para_A
            nueva_G[A_prima] = nuevas_prods_para_A_prima
        else:
            nueva_G[A] = prods
    return nueva_G

def factorizar_izquierda(gramatica_dict):
    G = deepcopy(gramatica_dict)
    cambiado = True
    while cambiado:
        cambiado = False
        nuevaG = {}
        for A, prods in G.items():
            grupos = {}
            for p in prods:
                clave = p[0] if len(p) > 0 else EPS
                grupos.setdefault(clave, []).append(p)
            nuevas_prods_para_A = []
            for clave, grupo in grupos.items():
                if clave != EPS and len(grupo) > 1:
                    A_fact = A + "_fact"
                    cambiado = True
                    nuevas_prods_para_A.append([clave, A_fact])
                    restos = []
                    for prod in grupo:
                        if len(prod) > 1:
                            restos.append(prod[1:])
                        else:
                            restos.append([EPS])
                    nuevaG[A_fact] = restos
                else:
                    for prod in grupo:
                        nuevas_prods_para_A.append(prod)
            nuevaG[A] = nuevas_prods_para_A
        G = nuevaG
    return G

def normalizar_gramatica_para_ll1(gramatica_base):
    g1 = eliminar_recursion_izquierda_inmediata(gramatica_base)
    g2 = factorizar_izquierda(g1)
    return g2

def token_a_terminal_gramatica(tipo_token, lexema_token):
    if tipo_token == 'KEYWORD':
        return f"KEYWORD_{lexema_token}"
    return tipo_token

if __name__ == "__main__":
    print("Gramática original:")
    print(imprimir_bonito(gramatica))
    print("\n--- Normalizando para LL(1) ---\n")
    norm = normalizar_gramatica_para_ll1(gramatica)
    print(imprimir_bonito(norm))