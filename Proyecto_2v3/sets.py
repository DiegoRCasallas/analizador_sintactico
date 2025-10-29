from copy import deepcopy

EPS = 'ε'
MARCA_FIN = '$'

def simbolos_de_gramatica(gramatica):
    no_terminales = set(gramatica.keys())
    usados = set()
    for prods in gramatica.values():
        for prod in prods:
            for simb in prod:
                usados.add(simb)
    terminales = set(simb for simb in usados if simb not in no_terminales and simb != EPS)
    return no_terminales, terminales

def calcular_first(gramatica):
    G = deepcopy(gramatica)
    no_terminales, terminales = simbolos_de_gramatica(G)

    FIRST = { simb: set() for simb in no_terminales.union(terminales) }
    for t in terminales:
        FIRST[t].add(t)
    cambiado = True
    while cambiado:
        cambiado = False
        for A in no_terminales:
            for prod in G[A]:
                if prod == [EPS]:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        cambiado = True
                    continue
                agregar_eps = True
                for X in prod:
                    antes = len(FIRST[A])
                    FIRST[A].update(x for x in FIRST.get(X, set()) if x != EPS)
                    if EPS in FIRST.get(X, set()):
                        agregar_eps = True
                    else:
                        agregar_eps = False
                        break
                    if len(FIRST[A]) > antes:
                        cambiado = True
                if agregar_eps:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        cambiado = True
    return FIRST

def first_de_secuencia(secuencia, FIRST):
    resultado = set()
    if secuencia == []:
        resultado.add(EPS)
        return resultado
    for X in secuencia:
        fx = FIRST.get(X, set())
        resultado.update(x for x in fx if x != EPS)
        if EPS in fx:
            continue
        else:
            break
    else:
        resultado.add(EPS)
    return resultado

def calcular_follow(gramatica, FIRST, simbolo_inicial):
    G = deepcopy(gramatica)
    no_terminales, terminales = simbolos_de_gramatica(G)
    FOLLOW = { A: set() for A in no_terminales }
    FOLLOW[simbolo_inicial].add(MARCA_FIN)

    cambiado = True
    while cambiado:
        cambiado = False
        for A in no_terminales:
            for prod in G[A]:
                for i, B in enumerate(prod):
                    if B not in no_terminales:
                        continue
                    beta = prod[i+1:] if i+1 < len(prod) else []
                    first_beta = first_de_secuencia(beta, FIRST)
                    antes = len(FOLLOW[B])
                    FOLLOW[B].update(x for x in first_beta if x != EPS)
                    if EPS in first_beta or beta == []:
                        FOLLOW[B].update(FOLLOW[A])
                    if len(FOLLOW[B]) > antes:
                        cambiado = True
    return FOLLOW

def calcular_select(gramatica, FIRST, FOLLOW):
    G = deepcopy(gramatica)
    select = {}
    for A, prods in G.items():
        for idx, prod in enumerate(prods):
            if prod == [EPS]:
                select[(A, idx)] = set(FOLLOW[A])
            else:
                first_alpha = first_de_secuencia(prod, FIRST)
                sel = set(x for x in first_alpha if x != EPS)
                if EPS in first_alpha:
                    sel.update(FOLLOW[A])
                select[(A, idx)] = sel
    return select

def construir_tabla_analisis(gramatica, select):
    tabla = {}
    for (A, idx), terminales in select.items():
        for a in terminales:
            clave = (A, a)
            if clave in tabla:
                raise ValueError(f"Conflicto en tabla de análisis para {A} en terminal {a}: ya existe {tabla[clave]}, intentando {idx}")
            tabla[clave] = idx
    return tabla

def calcular_todos_conjuntos(gramatica, simbolo_inicial):
    FIRST = calcular_first(gramatica)
    FOLLOW = calcular_follow(gramatica, FIRST, simbolo_inicial)
    SELECT = calcular_select(gramatica, FIRST, FOLLOW)
    TABLA_ANALISIS = construir_tabla_analisis(gramatica, SELECT)
    return FIRST, FOLLOW, SELECT, TABLA_ANALISIS

if __name__ == "__main__":
    import grammar as Gmod
    g = Gmod.normalizar_gramatica_para_ll1(Gmod.gramatica)
    FIRST, FOLLOW, SELECT, TABLA = calcular_todos_conjuntos(g, Gmod.SIMBOLO_INICIAL)
    print("Primeros:")
    for k in sorted(FIRST):
        print(k, ":", FIRST[k])
    print("\nSiguientes:")
    for k in sorted(FOLLOW):
        print(k, ":", FOLLOW[k])
    print("\nEntradas:")
    for k in list(SELECT.keys())[:20]:
        print(k, "->", SELECT[k])
    print("\nEntradas de la tabla de análisis:")
    for k in list(TABLA.keys())[:20]:
        print(k, ":", TABLA[k])