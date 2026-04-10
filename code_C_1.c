#include <stdlib.h>
#include <stdio.h>

// declaration de la liste
struct ElementList {
    int val;
    struct ElementList *suivant;
};

typedef struct ElementList Liste;


// creer un nouveau element
Liste * element_nv(int val){
    Liste *nv_elem = NULL;
    nv_elem = (Liste*) malloc(sizeof(Liste));

    if(nv_elem == NULL){
        printf("Erreur allocation mémoire\n");
        exit(1);
    }

    nv_elem->val = val;
    nv_elem->suivant = NULL;

    return nv_elem;
}


// Liberer espace d'un element
void *  freeElem(Liste* elem){
    free(elem);
    return NULL;
}


// retourner la taille d'une liste
int taille_liste(Liste *L){
    int len = 0;

    while(L != NULL){
        L = L->suivant;
        len++;
    }

    return len;
}


// parcourir une liste
void afficher_liste(Liste *L){
    int i;

    for(i = 0; L != NULL; i++, L = L->suivant){
        printf("Element %d = %d\n", i, L->val);
    }
}


// Ajouter un element au debut de la liste
Liste * liste_push(Liste* L, Liste* elem){
    elem->suivant = L;
    return elem;
}


// Inserer a une position donnee
void insertElemtPos(Liste *p, Liste *elem){
    elem->suivant = p->suivant;
    p->suivant = elem;
}


// Ajouter un element a la fin de la liste
Liste * list_append(Liste *L, Liste *elem){

    Liste* iter;

    if(L == NULL){
        return liste_push(L, elem);
    }

    iter = L;

    while(iter->suivant != NULL){
        iter = iter->suivant;
    }

    insertElemtPos(iter, elem);

    return L;
}


// programme principal
int main(){

    Liste *tete = NULL;

    tete = list_append(tete, element_nv(10));
    tete = list_append(tete, element_nv(20));
    tete = list_append(tete, element_nv(30));

    afficher_liste(tete);

    printf("Taille = %d\n", taille_liste(tete));

    return 0;
}
