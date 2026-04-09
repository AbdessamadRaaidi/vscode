def absolut(n):
    if n<0:
        return -n
    else:
        return n
nombre=int(input("entrer un nombre:"))
(lambda n: print(f"la valeur absolute de {n} est {(-n) if n<0 else n}"))(nombre)
print(f"la valeur absolute de {nombre} est {absolut(nombre)}")