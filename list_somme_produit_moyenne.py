T = []
for i in range(10):
    T.append(int(input(f"entrer les elements {i+1} de la liste: ")))
somme = sum(T)
produit = 1
for x in T:
    produit *= x
moyenne = somme / len(T) if len(T) > 0 else 0
for i in range(len(T)):
    print(f"Element {i+1}: {T[i]}")
print(f"La somme des éléments de la liste est: {somme}")
print(f"Le produit des éléments de la liste est: {produit}")
print(f"La moyenne des éléments de la liste est: {moyenne}")