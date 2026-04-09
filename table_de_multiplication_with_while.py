def table_de_multiplication(n):
    i = 1
    while i <= 10:
        print(f"{n} x {i} = {n * i}")
        i += 1
nombre = int(input("Entrez un nombre pour afficher sa table de multiplication : "))
table_de_multiplication(nombre)