# main.py
import sys
from lexer import tokenize, LexerError, Token
import grammar as Gmod
import table as Tmod
import parser as Pmod
import errors as Emod

OUTPUT_FILENAME = "reporte_sintactico.txt"

def main():
    # Leer todo el programa de la entrada estándar
    # dentro de main() en main.py, en lugar de: source = sys.stdin.read()
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
        with open(input_path, "r", encoding="utf-8") as f:
            source = f.read()
    else:
        source = sys.stdin.read()

    if source is None:
        print("No input provided.", file=sys.stderr)
        sys.exit(1)

    # Tokenizar
    try:
        tokens = tokenize(source)
    except LexerError as e:
        # Lexer error: formatear como error de indentación si el mensaje lo sugiere,
        # si no, devolver un mensaje genérico con posición desconocida (0,0).
        msg = str(e)
        # Intento heurístico: si la excepción menciona "Indentation" o "Indentation error"
        if "Indentation" in msg or "indent" in msg.lower():
            # No tenemos token donde ocurrió; construir token ficticio con línea 0 col 0
            fake = Token(type="INDENT", lexeme="<INDENT_ERR>", line=0, col=0)
            out = Emod.format_indentation_error(fake)
        else:
            fake = Token(type="", lexeme=str(e), line=0, col=0)
            out = Emod.format_token_error(fake, ["EOF"])
        write_output(out)
        print(out)
        return

    # Construir tabla predictiva LL(1)
    try:
        table_pred, FIRST, FOLLOW, SELECT = Tmod.build_predictive_table(Gmod.grammar, Gmod.START_SYMBOL)
    except Exception as e:
        # Si la gramática no es LL(1) o hay conflicto, reportar y salir
        msg = f"Error construyendo tabla predictiva LL(1): {e}"
        print(msg, file=sys.stderr)
        # Es útil fallar con mensaje en stderr; no generamos reporte de sintaxis en este caso
        sys.exit(2)

    # Normalizar la gramática (la tabla se construyó sobre la gramática normalizada)
    norm_grammar = Gmod.normalize_grammar_for_ll1(Gmod.grammar)

    # Parsear
    ok, message = Pmod.parse(tokens, table_pred, norm_grammar, Gmod.START_SYMBOL)

    # Escribir resultado en archivo de salida y a stdout
    write_output(message)
    print(message)

def write_output(text):
    """Escribe el texto final en OUTPUT_FILENAME (sobrescribe si existe)."""
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write(text + ("\n" if not text.endswith("\n") else ""))
    except Exception as e:
        print(f"Warning: no se pudo escribir el archivo {OUTPUT_FILENAME}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
