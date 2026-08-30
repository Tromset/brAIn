# Prompt pour tout agent IA

## Objectif :

Rendre le projet inclusif aux autres modèles d'IA.

## Prompt :

> Dans le projet cible, crée deux dossiers à la racine :
>
> - `Agents/` contient toutes les informations nécessaires pour travailler : contexte, objectifs, contraintes, décisions, variables et tâches.
> - `Code/` contient uniquement les vrais fichiers source que les agents doivent modifier.
>
> Trie les fichiers existants selon leur rôle sans perdre d'information. Avant de modifier `Code/`, lis les fichiers pertinents dans `Agents/`. Ajoute dans chaque dossier un `README.md` qui décrit son contenu et un `brain.yaml` qui route chaque besoin vers le bon fichier. Relie tous les fichiers par des liens relatifs et vérifie qu'aucun lien n'est cassé.

## Comment set-up ce système

1. L'utilisateur ou son IA renseigne dans `Agents/` le contexte, l'objectif, les contraintes, les décisions et les tâches du projet.
2. L'agent consulte le hub et le `brain.yaml` de `Agents/` pour sélectionner uniquement les informations utiles.
3. L'agent travaille sur les fichiers exécutables dans `Code/`.
4. Les hubs relient le contexte et le code pour conserver une navigation claire.

Exemple complet : [examples/after/](examples/after/README.md), avec le [contexte des agents](examples/after/Agents/README.md) séparé du [code exécutable](examples/after/Code/README.md).
