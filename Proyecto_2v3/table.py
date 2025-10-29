from collections import defaultdict
import grammar as Gmod
import sets as Smod

def construir_tabla_predictiva(gramatica, simbolo_inicial):
    gramatica_norm = Gmod.normalizar_gramatica_para_ll1(gramatica)

    FIRST, FOLLOW, SELECT, tabla_indices = Smod.calcular_todos_conjuntos(gramatica_norm, simbolo_inicial)

    tabla = {}
    for (A, idx), conjunto_sel in SELECT.items():
        prod = gramatica_norm[A][idx]
        for terminal in conjunto_sel:
            clave = (A, terminal)
            if clave in tabla:
                existente = tabla[clave]
                if existente != prod:
                    raise ValueError(f"Conflicto en tabla predictiva para {A} en terminal {terminal}: {existente} vs {prod}")
            else:
                tabla[clave] = prod
    return tabla, FIRST, FOLLOW, SELECT

def terminales_esperados_para_no_terminal(no_terminal, tabla):
    esperados = sorted({ terminal for (A, terminal), prod in tabla.items() if A == no_terminal })
    return esperados

def producciones_para_no_terminal(no_terminal, gramatica):
    gramatica_norm = Gmod.normalizar_gramatica_para_ll1(gramatica)
    return gramatica_norm.get(no_terminal, [])

def imprimir_tabla_bonita(tabla, max_entradas=200):
    lineas = []
    contador = 0
    for (A, terminal), prod in sorted(tabla.items(), key=lambda x: (x[0][0], x[0][1])):
        lineas.append(f"M[{A}, {terminal}] = {' '.join(prod)}")
        contador += 1
        if contador >= max_entradas:
            break
    return "\n".join(lineas)

if __name__ == "__main__":
    import grammar as G
    try:
        tabla, FIRST, FOLLOW, SELECT = construir_tabla_predictiva(G.gramatica, G.SIMBOLO_INICIAL)
        print("Algunas entradas de la tabla predictiva LL(1):")
        print(imprimir_tabla_bonita(tabla, max_entradas=80))
        esperados = terminales_esperados_para_no_terminal('sentencia', tabla)
        print("\nTokens esperados para 'sentencia':", esperados)
    except ValueError as e:
        print("Error construyendo tabla predictiva LL(1):", e)