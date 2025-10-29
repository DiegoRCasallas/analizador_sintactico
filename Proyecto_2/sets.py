from copy import deepcopy

EPS = 'ε'
ENDMARK = '$'

def symbols_from_grammar(grammar):
    nonterminals = set(grammar.keys())
    used = set()
    for prods in grammar.values():
        for prod in prods:
            for sym in prod:
                used.add(sym)
    terminals = set(sym for sym in used if sym not in nonterminals and sym != EPS)
    return nonterminals, terminals

def compute_first(grammar):
    G = deepcopy(grammar)
    nonterminals, terminals = symbols_from_grammar(G)

    FIRST = { sym: set() for sym in nonterminals.union(terminals) }
    for t in terminals:
        FIRST[t].add(t)
    changed = True
    while changed:
        changed = False
        for A in nonterminals:
            for prod in G[A]:
                if prod == [EPS]:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
                    continue
                add_eps = True
                for X in prod:
                    before = len(FIRST[A])
                    FIRST[A].update(x for x in FIRST.get(X, set()) if x != EPS)
                    if EPS in FIRST.get(X, set()):
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
        result.add(EPS)
    return result

def compute_follow(grammar, FIRST, start_symbol):
    G = deepcopy(grammar)
    nonterminals, terminals = symbols_from_grammar(G)
    FOLLOW = { A: set() for A in nonterminals }
    FOLLOW[start_symbol].add(ENDMARK)

    changed = True
    while changed:
        changed = False
        for A in nonterminals:
            for prod in G[A]:
                for i, B in enumerate(prod):
                    if B not in nonterminals:
                        continue
                    beta = prod[i+1:] if i+1 < len(prod) else []
                    first_beta = first_of_sequence(beta, FIRST)
                    before = len(FOLLOW[B])
                    FOLLOW[B].update(x for x in first_beta if x != EPS)
                    if EPS in first_beta or beta == []:
                        FOLLOW[B].update(FOLLOW[A])
                    if len(FOLLOW[B]) > before:
                        changed = True
    return FOLLOW

def compute_select(grammar, FIRST, FOLLOW):
    G = deepcopy(grammar)
    select = {}
    for A, prods in G.items():
        for idx, prod in enumerate(prods):
            if prod == [EPS]:
                select[(A, idx)] = set(FOLLOW[A])
            else:
                first_alpha = first_of_sequence(prod, FIRST)
                sel = set(x for x in first_alpha if x != EPS)
                if EPS in first_alpha:
                    sel.update(FOLLOW[A])
                select[(A, idx)] = sel
    return select

def build_parse_table(grammar, select):
    table = {}
    for (A, idx), terminals in select.items():
        for a in terminals:
            key = (A, a)
            if key in table:
                raise ValueError(f"Conflicto en la tabla de análisis para {A} en el terminal {a}: ya existe {table[key]}, intentando {idx}")
            table[key] = idx
    return table

def compute_all_sets(grammar, start_symbol):
    FIRST = compute_first(grammar)
    FOLLOW = compute_follow(grammar, FIRST, start_symbol)
    SELECT = compute_select(grammar, FIRST, FOLLOW)
    PARSE_TABLE = build_parse_table(grammar, SELECT)
    return FIRST, FOLLOW, SELECT, PARSE_TABLE

if __name__ == "__main__":
    import grammar as Gmod
    g = Gmod.normalize_grammar_for_ll1(Gmod.grammar)
    FIRST, FOLLOW, SELECT, TABLE = compute_all_sets(g, Gmod.START_SYMBOL)
    print("Primeros):")
    for k in sorted(FIRST):
        print(k, ":", FIRST[k])
    print("\nSiguientes:")
    for k in sorted(FOLLOW):
        print(k, ":", FOLLOW[k])
    print("\nPredicción:")
    for k in list(SELECT.keys())[:20]:
        print(k, "->", SELECT[k])
    print("\nEntradas de la tabla de análisis:")
    for k in list(TABLE.keys())[:20]:
        print(k, ":", TABLE[k])