T = [0] * 10
for i in range(10):
    T[i] = int(input(f"Entrer le {i+1} élément: "))

def max_liste(T):
    maximum = T[0]
    for i in range(1, len(T)):
        if maximum < T[i]:
            maximum = T[i]
    return maximum

def indice_min(T):
    minimum = T[0]
    for i in range(1, len(T)):
        if minimum > T[i]:
            minimum = T[i]
    return T.index(minimum)

print(f"Le max de la liste est {max_liste(T)}")
print(f"L'indice du min de la liste est {indice_min(T)}")