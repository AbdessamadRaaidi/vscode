#include <stdio.h>
#include <stdlib.h>

// Ta structure
typedef struct cellule {
    int valeur;
    struct cellule *suivant;
} cellule, *liste;

// Fonction pour ajouter un élément au début
liste ajouter(liste L, int v) {
    liste n = malloc(sizeof(cellule));
    if (n == NULL) return L; 
    n->valeur = v;
    n->suivant = L;
    return n;
}

// Fonction pour afficher
void afficher(liste L) {
    while (L != NULL) {
        printf("[%d] -> ", L->valeur);
        L = L->suivant;
    }
    printf("NULL\n");
}

int main() {
    liste ma_liste = NULL;
    ma_liste = ajouter(ma_liste, 10);
    ma_liste = ajouter(ma_liste, 20);
    
    printf("Resultat : ");
    afficher(ma_liste);
    
    return 0;
}