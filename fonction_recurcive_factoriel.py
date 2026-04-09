def factoriel(n):
    if n==0:
        return 1
    else:
        return n*factoriel(n-1)
nbr=int(input("entrer un nombre:"))
print(f"le factoriel de {nbr} est {factoriel(nbr)}")