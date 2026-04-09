nombre=int(input("entrer un nombre:"))
(lambda n: [print(f"{n} x {i} = {n*i}") for i in range(1, 11)])(nombre)