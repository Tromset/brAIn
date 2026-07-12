# brAIn

## But :

Créer une structure de penser reproduisant le cerveau pour les LLMs :

### LLMs :

[Claude](1)

[ChatGPT](2)

[Gemini](3)

[Qwen](4)

[Llama](5)

[Gemma](6)
## Régles :
1. Les dossiers sont reliés par un Hub qui les guide
2. Les fichiers sont reliés par des hyperliens 
3. Tout les fichiers sont en .md
4. Le reste du code est écrit dans le fichier .md avec ```` 
5. Les MCPs et configs plus profonde en .json
6. Dans chaque dossier un fichier .yaml qui donne les variables du dossier/projet
---
### Exemples :

### Hyperliens :

````
|Hub------>|----->|Dossier 1------|
           |----->|Dossier 2------|
           |----->|Dossier 3------|------>|---->| Fichier 1    |-------------->|<------|
           |----->|Dossier 4------|       |---->| Fichier 2    |-------------->|<------| : Tous reliés par des hyperliens
           |----->|Dossier 5------|       |---->| Fichier 3    |-------------->|<------|
           |----->|Dossier 6------|       |---->| Fichier yaml |----->Variables|<------| : Surtout lui
````
````
# Blablabla

## Blablabla

### Blablabla

Blablabla : [Blablabla](Blablabla.md)
````
### Code :

````md
#Site Madame Martin :
````
```` html
<html>
    <body>
            <hero>
                <p><h1> Salut à tous </h1>
                C'est Madame Martin </p>
            </hero>
    </body>
</html>
````
*Le code est dans le fichier markdown.*

## Fonctionnement Technique

````yaml
Client|----Dossier/Projet--->|Cloud/Github
                                  |
brAIn|----------Relié à-----------|---------|
  |                                         |Et l'envoie sur le Cloud
  |                                         |
  Transforme le dossier/projet en cerveau---| 

````

## Objectif

Créer un repo qui permet de transformer n'importe quel dossier en paradis pour IA et le poster en open-source sur Github.

### Structure du repo :

````yaml
|README.md----->| Description
|Prompt.md----->|Pour les LLMs genre Claude afin de les faire transformer le projet en brAIn
|brAIn.md------>|Technologie
|Audit.md------>|Présentation d'audits qui ont identifiés des changements radicaux de consommention de tokens sur le dossier/repo
````
<!-- Pour Claude: Trouve une meilleure architecture de repo et applique la tout en gardant mon idée de base, aussi écrire le code dont je parle et organiser le projet plus ergonomiquement, ensuite prendre un repo comme cyclades-workspace et le transformer en brAIn et run un audit des améliorations et le mettre dans Audit.md , traduis aussi le repo en anglais, et on sera tout bon. -->
## Références :

Claude : [1](https://claude.ai/)

ChatGPT : [2](https://chatgpt.ai/)

Gemini : [3](https://gemini.ai/)

Qwen : [4](https://github.com/Qwen/qwen)

Llama : [5](https://github.com/Llama/Llama)

Gemma : [6](https://github.com/Gemma/gemma4)



