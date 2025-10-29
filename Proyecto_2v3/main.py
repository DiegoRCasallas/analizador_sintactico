import sys
from lexer import tokenizar, ErrorLexer, Token
import grammar as Gmod
import table as Tmod
import parser as Pmod
import errors as Emod

NOMBRE_ARCHIVO_SALIDA = "reporte_sintactico.txt"

def leer_fuente_desde_argumentos_o_entrada():
    if len(sys.argv) >= 2:
        ruta = sys.argv[1]
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error leyendo archivo {ruta}: {e}", file=sys.stderr)
            sys.exit(1)
    return sys.stdin.read()

def escribir_salida(mensaje, aplicadas=None):
    try:
        with open(NOMBRE_ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
            f.write(mensaje + ("\n" if not mensaje.endswith("\n") else ""))
            if aplicadas:
                f.write("\nSecuencia de producciones aplicadas:\n")
                for i, (nt, prod) in enumerate(aplicadas, 1):
                    rhs = " ".join(prod)
                    f.write(f"{i}. {nt} → {rhs}\n")
    except Exception as e:
        print(f"Advertencia: no se pudo escribir el archivo {NOMBRE_ARCHIVO_SALIDA}: {e}", file=sys.stderr)

def principal():
    fuente = leer_fuente_desde_argumentos_o_entrada()
    if fuente is None:
        print("No se proporcionó entrada.", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = tokenizar(fuente)
    except ErrorLexer as e:
        falso = Token(tipo="INDENT", lexema=str(e), linea=e.linea, col=e.col)
        salida = Emod.formatear_error_indentacion(falso)
        escribir_salida(salida)
        print(salida)
        return


    try:
        tabla_pred, FIRST, FOLLOW, SELECT = Tmod.construir_tabla_predictiva(Gmod.gramatica, Gmod.SIMBOLO_INICIAL)
    except Exception as e:
        msg = f"Error construyendo tabla predictiva LL(1): {e}"
        print(msg, file=sys.stderr)
        sys.exit(2)

    gramatica_normalizada = Gmod.normalizar_gramatica_para_ll1(Gmod.gramatica)

    try:
        res = Pmod.analizar(tokens, tabla_pred, gramatica_normalizada, Gmod.SIMBOLO_INICIAL)
        if isinstance(res, tuple) and len(res) == 3:
            ok, mensaje, aplicadas = res
        elif isinstance(res, tuple) and len(res) == 2:
            ok, mensaje = res
            aplicadas = []
        else:
            ok = False
            mensaje = "Error interno: analizar devolvió un resultado inesperado."
            aplicadas = []
    except Exception as e:
        ok = False
        mensaje = f"ANALIZADOR LANZÓ EXCEPCIÓN: {e}"
        aplicadas = []

    escribir_salida(mensaje, aplicadas if ok else None)
    print(mensaje)

if __name__ == "__main__":
    principal()