# Calcul Brisage Dofus

Ce projet est un outil en Python destiné à aider les joueurs de Dofus à calculer le **brisage** (ou le nombre de runes générées) d’un objet en se basant sur ses statistiques. L’outil interroge l’API [dofusdb.fr](https://api.dofusdb.fr/) pour récupérer les données d’un objet (via son nom) et calcule les valeurs théoriques ou personnalisées à l’aide d’une formule intégrant le niveau de l’objet et des coefficients spécifiques à chaque statistique.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Versions du Script](#versions-du-script)
- [Installation](#installation)
- [Utilisation - Version CLI](#utilisation---version-cli)
- [Utilisation - Version GUI](#utilisation---version-gui)
- [Compilation en .exe (PyInstaller)](#compilation-en-exe-pyinstaller)
- [Structure du code](#structure-du-code)
- [Personnalisation](#personnalisation)
- [Organisation du dépôt](#organisation-du-dépôt)
- [License](#license)

---

## Fonctionnalités

- **Recherche d’objets :**

  - Recherche insensible à la casse et aux accents grâce à la normalisation des chaînes.
  - Utilisation du paramètre `slug.fr[$search]` pour interroger l’API.
  - Gestion de la pagination via les paramètres `$limit` et `$skip` afin de récupérer tous les résultats.

- **Filtrage :**

  - Filtrage par nom (correspondance partielle après normalisation).
  - Filtrage par type d’équipement autorisé (ex. Amulette, Anneau, Arme, Bottes, Bouclier, Cape, Ceinture, Chapeau, Arc, Baguette, Bâton, Dague, Épée, Marteau, Pelle, Hache, Outil, Pioche, Faux, Arme magique, Lance).

- **Extraction et calcul des statistiques :**

  - Récupération des statistiques via le champ `"effects"` de l’API.
  - Gestion des effets positifs et négatifs (par ex. si un objet va de -50 à 0, on sait gérer la stat négative).
  - Possibilité de forcer l’utilisation de la valeur maximale pour certaines statistiques (PA, PM, PO, Invocations).

- **Calcul du brisage :**

  - Formule de base (simplifiée) :
    ```python
    poids = (valeur_stat * poids_rune * level * 0.0150) + 1
    ```
    avec prise en compte d’un coefficient de brisage (par défaut 100 %) et d’un éventuel focus sur une statistique.
  - Gestion distincte des effets négatifs (valeur min par défaut pour la saisie manuelle).

- **Affichage des résultats :**
  - En CLI : utilisation de **Rich** pour un tableau formaté.
  - En GUI : interface Tkinter avec thème sombre, champs de saisie et affichage dans un Treeview.

---

## Versions du Script

Le projet propose **deux versions** :

1. **CLI** : `brisage_cli.py`

   - S’exécute en console, pose les questions interactives (nom de l’objet, valeurs de stats, etc.) et affiche les résultats via **Rich**.

2. **GUI** : `brisage_window.py`
   - Propose une interface graphique Tkinter (fenêtre noire, texte blanc, boutons gris).
   - Gère la recherche de l’objet, la sélection, le choix du mode (stats théoriques ou valeurs manuelles), le coefficient, le focus sur une stat, etc.
   - Affiche les résultats dans un Notebook avec onglets et un Treeview pour les statistiques.

---

## Installation

### Prérequis

- Python 3.6 ou supérieur

### Installation des dépendances

Utilisez `pip` pour installer les dépendances requises :

```bash
pip install requests rich
```

_(Pour la version GUI, Tkinter est fourni nativement avec Python sur la plupart des plateformes.)_

---

## Utilisation - Version CLI

Pour lancer la version **CLI** :

```bash
python brisage_cli.py
```

Le script vous demandera successivement :

1. **Le nom de l’objet**
2. **Le choix d’un objet dans la liste**
3. **L’utilisation des stats théoriques ou la saisie manuelle**
4. **Le coefficient de brisage** et un **focus** éventuel sur une statistique

Les résultats du brisage s’affichent sous forme de tableaux Rich (jets MIN, MOYEN, MAX ou valeurs manuelles).

---

## Utilisation - Version GUI

Pour lancer la version **GUI** :

```bash
python brisage_window.py
```

Vous verrez apparaître une fenêtre :

1. **Recherche d’objet** :  
   Saisissez le nom de l’objet (par exemple “Gélano” ou “Cape Hôte”).
2. **Sélection dans la liste** :  
   Choisissez l’objet exact parmi ceux proposés.
3. **Choix du mode** :
   - “Stats théoriques” : calcule les jets MIN, MOYEN, MAX.
   - “Valeurs manuelles” : vous pourrez modifier chaque statistique. Les stats négatives prennent par défaut la valeur la plus basse (ex. -50).
4. **Coefficient et focus** :  
   Entrez un pourcentage (100 par défaut) et/ou le nom d’une statistique à “focus”.
5. **Résultats** :  
   S’affichent dans un tableau via un Notebook (onglets).

L’interface est conçue pour être minimaliste et intuitive, avec un thème sombre (fond #1a1a1a, texte blanc).

---

## Compilation en .exe (PyInstaller)

Pour générer un exécutable **autonome** (sans dépendance à des fichiers externes), utilisez [PyInstaller](https://www.pyinstaller.org/) :

```bash
pyinstaller --onefile --windowed --icon=dofus_icon.ico brisage_window.py
```

- **`--onefile`** : crée un unique fichier .exe.
- **`--windowed`** : masque la console.
- **`--icon=dofus_icon.ico`** : intègre l’icône personnalisée dans l’exécutable.

Vous pouvez également préciser le dossier de sortie :

```bash
pyinstaller --onefile --windowed --icon=dofus_icon.ico --distpath "build" brisage_window.py
```

Ainsi, le fichier .exe sera généré dans le dossier `build`.

### Remarques sur l’icône

- Pour Windows, privilégiez un fichier `.ico` contenant plusieurs résolutions (16×16, 32×32, 48×48, 256×256).
- Une fois compilé avec `--icon`, l’icône est intégrée dans le .exe. Vous n’avez pas besoin d’avoir `dofus_icon.ico` à côté de l’exécutable.
- Dans le code, la ligne `self.iconbitmap("icon.ico")` affichera la bonne icône si vous lancez le script en Python pur.
  - Une fois compilé, Windows utilisera aussi l’icône intégrée pour l’exécutable.

---

## Structure du code

- **`search_items_by_name`**  
  Interroge l’API avec les paramètres `$limit` et `$skip` pour récupérer tous les résultats et applique un filtrage local (normalisation, filtrage par type).

- **`parse_item_stats`**  
  Extrait les statistiques de l’objet à partir du champ `"effects"`. Gère la distinction entre effets positifs et négatifs grâce à `"characteristicOperator"`. Si la stat est négative (ex. -50 à 0), la valeur par défaut en mode manuel sera la plus basse.

- **`calculate_brissage`**  
  Calcule le nombre de runes garanties et le pourcentage de chance d’un +1 selon la formule intégrant le niveau de l’objet et le poids de la rune (`POIDS_RUNES`).

- **CLI** :

  - **`brisage_cli.py`**
    - `main()` interagit en ligne de commande (nom de l’objet, sélection, stats, etc.).
    - `display_table` utilise la bibliothèque **Rich** pour un rendu coloré.

- **GUI** :
  - **`brisage_window.py`**
    - Interface Tkinter avec plusieurs frames (recherche, résultats, options, saisie manuelle, affichage).
    - Thème sombre (fond #1a1a1a, texte blanc), bouton gris moyen, usage de `ttk.Notebook` pour séparer les onglets.
    - `iconbitmap("icon.ico")` pour définir l’icône (lorsqu’on exécute en direct).

---

## Personnalisation

- **Mapping des effets** :  
  Le dictionnaire `EFFECT_ID_TO_STAT` associe les IDs d’effet renvoyés par l’API aux noms des statistiques (ex. 118 -> "Force").
- **Poids des runes** :  
  Le dictionnaire `POIDS_RUNES` définit l’impact de chaque statistique dans le calcul du brisage (ex. "Vitalité" = 0.2, "Force" = 1.0, "PA" = 100.0, etc.).

Modifiez ces tables en fonction de vos besoins ou des évolutions du jeu.

---

## Organisation du dépôt

- **`brisage_cli.py`** : version console (CLI)
- **`brisage_window.py`** : version fenêtre (GUI)
- **`dofus_icon.ico`** : icône utilisée pour la fenêtre et pour la compilation en exécutable
- **`README.md`** : ce fichier de documentation
- **`.gitignore`** : liste des fichiers/dossiers ignorés (incluant éventuellement le dossier `build/` ou les .exe générés)

Le .exe final (issu de PyInstaller) peut être distribué via la section _Releases_ du dépôt.

---

## License
