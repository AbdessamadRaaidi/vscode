T = ['a', 'b', 'c', 'd', 'e']
J = ['f', 'g', 'h', 'i', 'j']
H = []
for i in range(len(T)):
    H.append(f"{T[i]}*{J[i]}")

resultat = " + ".join(H)
print(f"Résultat: {resultat}")