import sys
from lexer import tokenize, LexerError, Token
import grammar as Gmod
import table as Tmod
import parser as Pmod
import errors as Emod

OUTPUT_FILENAME = "reporte_sintactico.txt"

def read_source_from_args_or_stdin():
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error leyendo archivo {path}: {e}", file=sys.stderr)
            sys.exit(1)
    return sys.stdin.read()

def write_output(message, applied=None):
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write(message + ("\n" if not message.endswith("\n") else ""))
            if applied:
                f.write("\nSecuencia de producciones aplicadas:\n")
                for i, (nt, prod) in enumerate(applied, 1):
                    rhs = " ".join(prod)
                    f.write(f"{i}. {nt} → {rhs}\n")
    except Exception as e:
        print(f"No se pudo escribir el archivo {OUTPUT_FILENAME}: {e}", file=sys.stderr)

def main():
    source = read_source_from_args_or_stdin()
    if source is None:
        print("No se proporcionó entrada.", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = tokenize(source)
    except LexerError as e:
        msg = str(e)
        if "Indentation" in msg or "indent" in msg.lower():
            fake = Token(type="INDENT", lexeme="<INDENT_ERR>", line=0, col=0)
            out = Emod.format_indentation_error(fake)
        else:
            fake = Token(type="", lexeme=str(e), line=0, col=0)
            out = Emod.format_token_error(fake, ["EOF"])
        write_output(out)
        print(out)
        return

    try:
        table_pred, FIRST, FOLLOW, SELECT = Tmod.build_predictive_table(Gmod.grammar, Gmod.START_SYMBOL)
    except Exception as e:
        msg = f"Error construyendo tabla predictiva LL(1): {e}"
        print(msg, file=sys.stderr)
        sys.exit(2)

    norm_grammar = Gmod.normalize_grammar_for_ll1(Gmod.grammar)

    try:
        res = Pmod.parse(tokens, table_pred, norm_grammar, Gmod.START_SYMBOL)
        if isinstance(res, tuple) and len(res) == 3:
            ok, message, applied = res
        elif isinstance(res, tuple) and len(res) == 2:
            ok, message = res
            applied = []
        else:
            ok = False
            message = "Error: parse devolvió un resultado inesperado."
            applied = []
    except Exception as e:
        ok = False
        message = f"Error {e}"
        applied = []

    write_output(message, applied if ok else None)
    print(message)

if __name__ == "__main__":
    main()