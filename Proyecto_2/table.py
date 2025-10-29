from collections import defaultdict
import grammar as Gmod
import sets as Smod

def build_predictive_table(grammar, start_symbol):
    norm_g = Gmod.normalize_grammar_for_ll1(grammar)

    FIRST, FOLLOW, SELECT, parse_table_idx = Smod.compute_all_sets(norm_g, start_symbol)

    table = {}
    for (A, idx), sel_set in SELECT.items():
        prod = norm_g[A][idx]
        for term in sel_set:
            key = (A, term)
            if key in table:
                existing = table[key]
                if existing != prod:
                    raise ValueError(f"Conflicto en la tabla predictiva para {A} en el terminal {term}: {existing} vs {prod}")
            else:
                table[key] = prod
    return table, FIRST, FOLLOW, SELECT

def expected_tokens_for_nonterminal(nonterminal, table):
    expected = sorted({ term for (A, term), prod in table.items() if A == nonterminal })
    return expected

def productions_for_nonterminal(nonterminal, grammar):
    norm_g = Gmod.normalize_grammar_for_ll1(grammar)
    return norm_g.get(nonterminal, [])

def pretty_print_table(table, max_entries=200):
    lines = []
    count = 0
    for (A, term), prod in sorted(table.items(), key=lambda x: (x[0][0], x[0][1])):
        lines.append(f"M[{A}, {term}] = {' '.join(prod)}")
        count += 1
        if count >= max_entries:
            break
    return "\n".join(lines)

if __name__ == "__main__":
    import grammar as G
    try:
        table, FIRST, FOLLOW, SELECT = build_predictive_table(G.grammar, G.START_SYMBOL)
        print("Algunas entradas de la tabla predictiva LL(1):")
        print(pretty_print_table(table, max_entries=80))
        expected = expected_tokens_for_nonterminal('stmt', table)
        print("\nTokens esperados para 'stmt':", expected)
    except ValueError as e:
        print("Error construyendo tabla predictiva LL(1):", e)