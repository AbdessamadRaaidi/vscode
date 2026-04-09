def table_de_multiplication(nombre):
    for i in range(1, 11):
        print(f"{nombre} x {i} = {nombre * i}")
nombre_saisi = int(input("Entrez un nombre pour afficher sa table de multiplication : "))
table_de_multiplication(nombre_saisi)