T=[0]*10
b=True
for i in range(10):
    T[i]=int(input(f"entrer le {i+1} element:"))
for i in range(1, 10):
    if T[i-1]+1!=T[i]:
        print("la liste n'est pas consécutive")
        b=False
        break
if b:
            print("la liste est consécutive")