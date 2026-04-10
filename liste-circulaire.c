#include <stdio.h>
#include <stdlib.h>

// 1. Structure
typedef struct cellule {
    int valeur;
    struct cellule * suivant;
} cellule, *liste;

// 2. Ajouter en tête
liste AjoutTete(int val, liste l) {
    liste l1 = (liste)malloc(sizeof(cellule));
    l1->valeur = val;
    if (l == NULL) {
        l1->suivant = l1;
        return l1; // Important : retourner l1 ici
    } else {
        liste l2 = l;
        l1->suivant = l;
        while (l2->suivant != l) {
            l2 = l2->suivant;
        }
        l2->suivant = l1;
        return l1;
    }
}

// 3. Ajouter à la fin
liste AjoutFin(int val, liste l) {
    liste l1, l2;
    l1 = malloc(sizeof(cellule));
    l1->valeur = val;
    if (l == NULL) {
        l1->suivant = l1;
        return l1;
    } else {
        l1->suivant = l;
        l2 = l;
        while (l2->suivant != l) {
            l2 = l2->suivant;
        }
        l2->suivant = l1;
        return l;
    }
}

// 4. Afficher
void AffListCir(liste l) {
    if (l != NULL) {
        liste l1 = l;
        do {
            printf("[%d] -> ", l1->valeur);
            l1 = l1->suivant;
        } while (l1 != l);
        printf("(retour à la tête)\n");
    } else {
        printf("Liste vide\n");
    }
}

// --- Fonctions de suppression (SuppTete, SuppFin, etc. à copier ici) ---

int main() {
    liste ma_liste = NULL;

    printf("Ajout de 10 et 20 en tete...\n");
    ma_liste = AjoutTete(10, ma_liste);
    ma_liste = AjoutTete(20, ma_liste);
    
    printf("Ajout de 5 a la fin...\n");
    ma_liste = AjoutFin(5, ma_liste);

    printf("Etat de la liste : ");
    AffListCir(ma_liste);

    return 0;
}