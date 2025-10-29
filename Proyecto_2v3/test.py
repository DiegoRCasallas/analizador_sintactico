if source[i:i+3] == '"""':
    # iniciar cadena multilínea
    j = i + 3
while j < len(source) and source[j:j+3] != '"""':
        j += 1
    if j >= len(source):
        raise LexerError("Cadena multilínea sin cierre", line, col)
    lexeme = source[i:j+3]
    tokens.append(Token("STRING", lexeme, line, col))
    i = j + 3
    continue
