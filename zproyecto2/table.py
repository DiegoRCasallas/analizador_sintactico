# table.py
from collections import defaultdict
import grammar as Gmod
import sets as Smod

def build_predictive_table(grammar, start_symbol):
    """
    Construye una tabla predictiva LL(1) con clave (A, terminal) -> production (list).
    Internamente usa compute_all_sets de sets.py que devuelve FIRST, FOLLOW, SELECT, PARSE_TABLE.
    Si detecta conflicto LL(1) propagatea la excepción ValueError desde build_parse_table.
    Devuelve: (table, FIRST, FOLLOW, SELECT)
      - table: dict (A, terminal) -> production (list of symbols)
      - FIRST, FOLLOW, SELECT: conjuntos calculados para inspección y pruebas
    """
    # Normalizar la gramática para LL(1)
    norm_g = Gmod.normalize_grammar_for_ll1(grammar)

    # Calcular conjuntos y tabla intermedia (tabla con índices)
    FIRST, FOLLOW, SELECT, parse_table_idx = Smod.compute_all_sets(norm_g, start_symbol)

    # Convertir la tabla de índices a tabla con producciones concretas
    table = {}
    for (A, idx), sel_set in SELECT.items():
        prod = norm_g[A][idx]  # producción concreta
        for term in sel_set:
            key = (A, term)
            if key in table:
                # Debe corresponder al mismo prod; si no, hay conflicto (lo mismo que build_parse_table habría detectado)
                existing = table[key]
                if existing != prod:
                    raise ValueError(f"Conflict in predictive table for {A} on terminal {term}: {existing} vs {prod}")
            else:
                table[key] = prod
    return table, FIRST, FOLLOW, SELECT

def expected_tokens_for_nonterminal(nonterminal, table):
    """
    Dado un no terminal y la tabla predictiva (A,terminal)->prod,
    devuelve la lista de terminales esperados (ordenada) que tienen una entrada en la tabla.
    Útil para formar el mensaje de error: 'se esperaba: "t1", "t2", ...'
    """
    expected = sorted({ term for (A, term), prod in table.items() if A == nonterminal })
    return expected

def productions_for_nonterminal(nonterminal, grammar):
    """
    Devuelve la lista de producciones (listas) para un no terminal en la gramática normalizada.
    """
    norm_g = Gmod.normalize_grammar_for_ll1(grammar)
    return norm_g.get(nonterminal, [])

def pretty_print_table(table, max_entries=200):
    """
    Devuelve una cadena con una impresión legible de la tabla (muestra hasta max_entries).
    """
    lines = []
    count = 0
    for (A, term), prod in sorted(table.items(), key=lambda x: (x[0][0], x[0][1])):
        lines.append(f"M[{A}, {term}] = {' '.join(prod)}")
        count += 1
        if count >= max_entries:
            break
    return "\n".join(lines)

# Ejecución rápida para inspección
if __name__ == "__main__":
    import grammar as G
    try:
        table, FIRST, FOLLOW, SELECT = build_predictive_table(G.grammar, G.START_SYMBOL)
        print("Algunas entradas de la tabla predictiva LL(1):")
        print(pretty_print_table(table, max_entries=80))
        # Ejemplo de consulta de tokens esperados para 'stmt'
        expected = expected_tokens_for_nonterminal('stmt', table)
        print("\nTokens esperados para 'stmt':", expected)
    except ValueError as e:
        print("Error construyendo tabla predictiva LL(1):", e)
