# Analizador sintáctico
Autores: Diego Casallas, José Nicolás Lesmes

## Ejecución

En Linux se ejeucuta con
```
cat test.py | python3 main.py
```

o

```
python3 main.py test.py
```

En Windows se ejecuta con el comando:
```
python main.py test.py
```
El analisis se hace en el archivo llamado "test.py" a traves de la terminal de Linux o en Power Shell de Windows

<img width="801" height="84" alt="image" src="https://github.com/user-attachments/assets/21a185cd-d41e-4ea2-8b7c-b0d14477ebb1" />

<img width="839" height="57" alt="image" src="https://github.com/user-attachments/assets/d9198e5b-b63b-408b-80f4-ea84ab847c71" />


## Flujo de Control Completo - Diagrama
```
┌─────────────────────────────────────────┐
│ Inicio de principal()                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Leer código fuente                      │
│ (archivo o stdin)                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Tokenizar                               │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │ ¿ErrorLexer?   │
       └───────┬────────┘
               │
         Yes ──┤         No
               │          │
               ▼          ▼
    ┌──────────────┐  ┌──────────────────────┐
    │ Formatear    │  │ Construir tabla      │
    │ error léxico │  │ predictiva           │
    └──────┬───────┘  └──────────┬───────────┘
           │                     │
           │              ┌──────┴───────┐
           │              │ ¿Conflicto?  │
           │              └──────┬───────┘
           │                     │
           │               Yes ──┤   No
           │                     │    │
           │                     ▼    ▼
           │            ┌────────────────────┐
           │            │ sys.exit(2)        │
           │            └────────────────────┘
           │                                  │
           │                                  ▼
           │                     ┌──────────────────────┐
           │                     │ Normalizar gramática │
           │                     └──────────┬───────────┘
           │                                │
           │                                ▼
           │                     ┌──────────────────────┐
           │                     │ Analizar sintaxis    │
           │                     └──────────┬───────────┘
           │                                │
           │                         ┌──────┴───────┐
           │                         │ ¿Excepción?  │
           │                         └──────┬───────┘
           │                                │
           │                          Yes ──┤   No
           │                                │    │
           │                                ▼    ▼
           │                         ┌─────────────────┐
           │                         │ Capturar error  │
           │                         │ ok = False      │
           │                         └─────────┬───────┘
           │                                   │
           └───────────────────────────────────┘
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │ Escribir resultado  │
                                    │ (archivo + stdout)  │
                                    └─────────────────────┘
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │ Fin                 │
                                    └─────────────────────┘