# sets.py
from copy import deepcopy

EPS = 'ε'
ENDMARK = '$'  # símbolo artificial para EOF in FOLLOW

def symbols_from_grammar(grammar):
    """Devuelve (nonterminals, terminals) según la gramática."""
    nonterminals = set(grammar.keys())
    used = set()
    for prods in grammar.values():
        for prod in prods:
            for sym in prod:
                used.add(sym)
    terminals = set(sym for sym in used if sym not in nonterminals and sym != EPS)
    return nonterminals, terminals

def compute_first(grammar):
    """
    Calcula FIRST para todos los símbolos (terminales y no terminales).
    Devuelve dict: symbol -> set(strings) donde los terminales aparecen como ellos mismos,
    y EPS se incluye si el símbolo puede derivar ε.
    """
    G = deepcopy(grammar)
    nonterminals, terminals = symbols_from_grammar(G)

    FIRST = { sym: set() for sym in nonterminals.union(terminals) }
    # FIRST of terminals is the terminal itself
    for t in terminals:
        FIRST[t].add(t)
    # iterate until no change
    changed = True
    while changed:
        changed = False
        for A in nonterminals:
            for prod in G[A]:
                # prod is a list of symbols (possibly [EPS])
                if prod == [EPS]:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
                    continue
                add_eps = True
                for X in prod:
                    # add FIRST(X) \ {EPS} to FIRST(A)
                    before = len(FIRST[A])
                    FIRST[A].update(x for x in FIRST.get(X, set()) if x != EPS)
                    if EPS in FIRST.get(X, set()):
                        # continue to next symbol
                        add_eps = True
                    else:
                        add_eps = False
                        break
                    if len(FIRST[A]) > before:
                        changed = True
                if add_eps:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
    return FIRST

def first_of_sequence(seq, FIRST):
    """
    Dado una secuencia de símbolos (lista), calcula FIRST(seq).
    Devuelve un conjunto de terminales y puede incluir EPS.
    """
    result = set()
    if seq == []:
        result.add(EPS)
        return result
    for X in seq:
        fx = FIRST.get(X, set())
        result.update(x for x in fx if x != EPS)
        if EPS in fx:
            continue
        else:
            break
    else:
        # todos producían EPS
        result.add(EPS)
    return result

def compute_follow(grammar, FIRST, start_symbol):
    """
    Calcula FOLLOW para todos los no terminales de la gramática.
    FOLLOW uses ENDMARK ('$') as end-of-input symbol.
    Devuelve dict nonterminal -> set(terminals ∪ {ENDMARK}).
    """
    G = deepcopy(grammar)
    nonterminals, terminals = symbols_from_grammar(G)
    FOLLOW = { A: set() for A in nonterminals }
    FOLLOW[start_symbol].add(ENDMARK)

    changed = True
    while changed:
        changed = False
        for A in nonterminals:
            for prod in G[A]:
                # recorrer cada símbolo B en prod
                for i, B in enumerate(prod):
                    if B not in nonterminals:
                        continue
                    beta = prod[i+1:] if i+1 < len(prod) else []
                    first_beta = first_of_sequence(beta, FIRST)
                    # añadir FIRST(beta) - {EPS} a FOLLOW(B)
                    before = len(FOLLOW[B])
                    FOLLOW[B].update(x for x in first_beta if x != EPS)
                    if EPS in first_beta or beta == []:
                        # añadir FOLLOW(A) a FOLLOW(B)
                        FOLLOW[B].update(FOLLOW[A])
                    if len(FOLLOW[B]) > before:
                        changed = True
    return FOLLOW

def compute_select(grammar, FIRST, FOLLOW):
    """
    Para cada producción A -> alpha, calcula SELECT(A, prod_index)
    Devuelve dict: (A, idx) -> set(terminals)
    """
    G = deepcopy(grammar)
    select = {}
    for A, prods in G.items():
        for idx, prod in enumerate(prods):
            if prod == [EPS]:
                # SELECT = FOLLOW(A)
                select[(A, idx)] = set(FOLLOW[A])
            else:
                first_alpha = first_of_sequence(prod, FIRST)
                sel = set(x for x in first_alpha if x != EPS)
                if EPS in first_alpha:
                    sel.update(FOLLOW[A])
                select[(A, idx)] = sel
    return select

# Utility para construir la tabla predictiva M[A, a]
def build_parse_table(grammar, select):
    """
    Construye la tabla LL(1) como dict: (A, terminal) -> production_index
    Si hay conflicto (múltiples producciones para la misma celda), lanza ValueError.
    """
    table = {}
    for (A, idx), terminals in select.items():
        for a in terminals:
            key = (A, a)
            if key in table:
                # conflicto LL(1)
                raise ValueError(f"Conflict in parse table for {A} on terminal {a}: already {table[key]}, trying {idx}")
            table[key] = idx
    return table

# Convenience function to run full computation
def compute_all_sets(grammar, start_symbol):
    """
    Devuelve (FIRST, FOLLOW, SELECT, PARSE_TABLE)
    """
    FIRST = compute_first(grammar)
    FOLLOW = compute_follow(grammar, FIRST, start_symbol)
    SELECT = compute_select(grammar, FIRST, FOLLOW)
    PARSE_TABLE = build_parse_table(grammar, SELECT)
    return FIRST, FOLLOW, SELECT, PARSE_TABLE

# Example quick test if executed directly (no assertions, solo inspección)
if __name__ == "__main__":
    import grammar as Gmod
    g = Gmod.normalize_grammar_for_ll1(Gmod.grammar)
    FIRST, FOLLOW, SELECT, TABLE = compute_all_sets(g, Gmod.START_SYMBOL)
    print("FIRST (sample):")
    for k in sorted(FIRST):
        print(k, ":", FIRST[k])
    print("\nFOLLOW (sample):")
    for k in sorted(FOLLOW):
        print(k, ":", FOLLOW[k])
    print("\nSome SELECT entries:")
    for k in list(SELECT.keys())[:20]:
        print(k, "->", SELECT[k])
    print("\nParse table entries (sample):")
    for k in list(TABLE.keys())[:20]:
        print(k, ":", TABLE[k])
