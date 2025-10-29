def es_primo(n):
    # Un número menor que 2 no es primo
    if n < 2:
        return False
    # Verificar divisibilidad desde 2 hasta la raíz cuadrada de n
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# Programa principal
numero = int(input("Ingresa un número: "))

if es_primo(numero):
    print(f"{numero} es un número primo.")
else:
    print(f"{numero} no es un número primo.")
