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
t=0
facto = lambda f, n: 1 if n == 0 else n * f(f, n - 1)
for i in range(n+1):
    t+=facto(facto, i)
print(f"La somme des factorielles de 0 à {n} est: {t}")