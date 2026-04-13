n=int(input("entrer un nombre:"))
def parfait(n):
    s=0
    for i in range(1,n):
        if n%i==0:
            s+=i
    if s==n:
        return print("le nombre est parfait")
    else:
        return print("le nombre n'est pas parfait")
parfait(n)