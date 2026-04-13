n=int(input("entrer un nombre: "))
def fact(n):
    if n==0:
        return 1
    else:
        return n*fact(n-1)
s=0
for i in range(n+1):
    s+=fact(i)
print(f"La somme des factorielles de 0 à {n} est: {s}")