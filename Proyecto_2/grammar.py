from copy import deepcopy

EPS = 'ε'

START_SYMBOL = 'program'

grammar = {
    'program': [
        ['stmt_list', 'EOF']
    ],

    'stmt_list': [
        ['stmt', 'stmt_list'],
        [EPS]
    ],

    'stmt': [
        ['simple_stmt'],
        ['compound_stmt']
    ],

    'simple_stmt': [
        ['small_stmt', 'NEWLINE']
    ],
    'small_stmt': [
        ['ID', 'small_stmt_tail'],
        ['literal', 'expr_tail'],
        ['LPAR', 'expr', 'RPAR', 'expr_tail'],
        ['KEYWORD_pass'],
        ['KEYWORD_break'],
        ['KEYWORD_continue'],
        ['KEYWORD_return', 'expr_opt']
    ],
        'small_stmt_tail': [
        ['ASSIGN', 'expr'],
        ['term_prime', 'expr_tail']
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

    'target': [
        ['ID']
    ],

    'expr': [
        ['term', 'expr_tail']
    ],

    'expr_tail': [
        ['BINOP', 'term', 'expr_tail'],
        [EPS]
    ],

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

    'compound_stmt': [
        ['if_stmt'],
        ['while_stmt'],
        ['for_stmt'],
        ['func_def']
    ],

    'if_stmt': [
        ['KEYWORD_if', 'expr', 'COLON', 'suite', 'elif_star', 'else_opt']
    ],

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

    'type_annotation': [
        ['ID'],
        ['LBRACK', 'ID', 'RBRACK']
    ],

    'suite': [
        ['simple_stmt'],
        ['NEWLINE', 'INDENT', 'stmt_list', 'DEDENT']
    ],
}

TERMINALS = {
    'KEYWORD_def', 'KEYWORD_if', 'KEYWORD_else', 'KEYWORD_elif', 'KEYWORD_while',
    'KEYWORD_for', 'KEYWORD_return', 'KEYWORD_pass', 'KEYWORD_break', 'KEYWORD_continue',
    'KEYWORD_in', 'KEYWORD_True', 'KEYWORD_False', 'KEYWORD_None',
    'ID', 'INT', 'FLOAT', 'STRING',
    'BINOP', 'CMP', 'ASSIGN', 'COLON', 'COMMA', 'DOT',
    'LPAR', 'RPAR', 'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE',
    'NEWLINE', 'INDENT', 'DEDENT', 'EOF'
}

def nonterminals_from_grammar(g):
    return set(g.keys())

NONTERMINALS = nonterminals_from_grammar(grammar)

def productions_list(grammar_dict):
    out = []
    for A, prods in grammar_dict.items():
        for prod in prods:
            out.append((A, prod))
    return out

def pretty_print(grammar_dict):
    lines = []
    for A, prods in grammar_dict.items():
        rhs = [" ".join(p) for p in prods]
        lines.append(f"{A} -> {' | '.join(rhs)}")
    return "\n".join(lines)

def remove_immediate_left_recursion(g):
    G = deepcopy(g)
    new_G = {}
    for A in G:
        prods = G[A]
        left_recursive = []
        non_recursive = []
        for prod in prods:
            if len(prod) > 0 and prod[0] == A:
                left_recursive.append(prod[1:])
            else:
                non_recursive.append(prod)

        if left_recursive:
            A_prime = A + "_rec"
            new_prods_for_A = []
            for beta in non_recursive:
                if beta == [EPS]:
                    new_prods_for_A.append([A_prime])
                else:
                    new_prods_for_A.append(beta + [A_prime])
            new_prods_for_A_prime = []
            for alpha in left_recursive:
                new_prods_for_A_prime.append(alpha + [A_prime])
            new_prods_for_A_prime.append([EPS])

            new_G[A] = new_prods_for_A
            new_G[A_prime] = new_prods_for_A_prime
        else:
            new_G[A] = prods
    return new_G

def left_factor(grammar_dict):
    G = deepcopy(grammar_dict)
    changed = True
    while changed:
        changed = False
        newG = {}
        for A, prods in G.items():
            groups = {}
            for p in prods:
                key = p[0] if len(p) > 0 else EPS
                groups.setdefault(key, []).append(p)
            new_prods_for_A = []
            for key, group in groups.items():
                if key != EPS and len(group) > 1:
                    A_fact = A + "_fact"
                    changed = True
                    new_prods_for_A.append([key, A_fact])
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

def normalize_grammar_for_ll1(base_grammar):
    g1 = remove_immediate_left_recursion(base_grammar)
    g2 = left_factor(g1)
    return g2

def token_to_grammar_terminal(token_type, token_lexeme):
    if token_type == 'KEYWORD':
        return f"KEYWORD_{token_lexeme}"
    return token_type

if __name__ == "__main__":
    print("Gramática original:")
    print(pretty_print(grammar))
    print("\nLL1\n")
    norm = normalize_grammar_for_ll1(grammar)
    print(pretty_print(norm))