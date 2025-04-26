import json
import unicodedata
import requests
import math
from rich.console import Console
from rich.table import Table

ALLOWED_EQUIPMENT_NAMES = {
    "amulette", "anneau", "arme", "bottes", "bouclier", "cape", "ceinture",
    "chapeau", "arc", "baguette", "bâton", "dague", "épée", "marteau", "pelle",
    "hache", "outil", "pioche", "faux", "arme magique", "lance"
}

# Mapping des effectId vers le nom de la stat tel qu’indiqué sur les items
EFFECT_ID_TO_STAT = {
    # POSITIFS

    # Statistiques de base
    125: "Vitalité",
    126: "Intelligence",
    119: "Agilité",
    118: "Force",
    123: "Chance",
    138: "Puissance",
    
    # Autres statistiques
    158: "Pods",
    174: "Initiative",
    
    176: "Prospection",
    124: "Sagesse",
    115: "% Critique",
    178: "Soins",
    
    # Actions
    111: "PA",
    128: "PM",
    117: "PO",
    182: "Invocations",
    
    # Autres équipements
    795: "Arme de chasse",
    
    # Dommages
    112: "Dommages",
    422: "Dommages Terre",
    424: "Dommages Feu",
    426: "Dommages Eau",
    430: "Dommage Neutre",
    428: "Dommages Air",
    
    # % Résistances
    210: "% Résistance Terre",
    211: "% Résistance Eau",
    212: "% Résistance Air",
    213: "% Résistance Feu",
    214: "% Résistance Neutre",
    
    # Résistances fixes
    244: "Résistances Neutre",
    240: "Résistances Terre",
    243: "Résistances Feu",
    241: "Résistances Eau",
    242: "Résistances Air",
    
    # Autres résistances
    420: "Résistances Critiques",
    416: "Résistances Poussée",
    
    # Esquives et agression
    752: "Fuite",
    753: "Tacle",
    
    # Retraits et esquives
    410: "Retrait PA",
    412: "Retrait PM",
    161: "Esquive PM",
    160: "Esquive PA",
    
    # Dommages spéciaux
    418: "Dommages Critiques",
    414: "Dommages Poussée",
    220: "Dommages Renvoyés",
    
    # Pièges
    226: "Puissance Pièges",
    225: "Dommages Pièges",
    
    # Pourcentages sur les dégâts
    2812: "% Dommages aux sorts",
    2808: "% Dommages d'armes",
    2805: "% Dommages distance",
    2800: "% Dommages mêlée",
    
    # Pourcentages sur les résistances
    2803: "% Résistance mêlée",
    2807: "% Résistance distance",



    ##########################################
    # NEGATIFS
    # Statistiques de base
    153: "Vitalité",
    155: "Intelligence",
    154: "Agilité",
    157: "Force",
    152: "Chance",
    186: "Puissance",
    
    # Autres statistiques
    159: "Pods",
    175: "Initiative",
    
    177: "Prospection",
    156: "Sagesse",
    171: "% Critique",
    179: "Soins",
    
    # Actions
    168: "PA",
    169: "PM",
    
    # Dommages
    145: "Dommages",
    423: "Dommages Terre",
    425: "Dommages Feu",
    427: "Dommages Eau",
    431: "Dommage Neutre",
    429: "Dommages Air",
    
    # % Résistances
    215: "% Résistance Terre",
    216: "% Résistance Eau",
    217: "% Résistance Air",
    218: "% Résistance Feu",
    219: "% Résistance Neutre",
    
    # Résistances fixes
    249: "Résistances Neutre",
    245: "Résistances Terre",
    248: "Résistances Feu",
    246: "Résistances Eau",
    247: "Résistances Air",
    
    # Autres résistances
    421: "Résistances Critiques",
    417: "Résistances Poussée",
    
    # Esquives et agression
    754: "Fuite",
    755: "Tacle",
    
    # Retraits et esquives
    411: "Retrait PA",
    413: "Retrait PM",
    163: "Esquive PM",
    162: "Esquive PA",
    
    # Dommages spéciaux
    419: "Dommages Critiques",
    415: "Dommages Poussée",
  
    # Pourcentages sur les dégâts
    2813: "% Dommages aux sorts",
    2809: "% Dommages d'armes",
    2804: "% Dommages distance",
    2801: "% Dommages mêlée",
    
    # Pourcentages sur les résistances
    2802: "% Résistance mêlée",
    2806: "% Résistance distance",
}

# Table de correspondance pour le poids des runes selon la stat.
POIDS_RUNES = {
    # Statistiques de base
    "Vitalité": 0.2,
    "Intelligence": 1.0,
    "Agilité": 1.0,
    "Force": 1.0,
    "Chance": 1.0,
    "Puissance": 2.0,
    
    # Autres statistiques
    "Pods": 0.25,
    "Initiative": 0.1,
    
    "Prospection": 3.0,
    "Sagesse": 3.0,
    "% Critique": 10.0,
    "Soins": 10.0,
    
    # Actions
    "PA": 100.0,
    "PM": 90.0,
    "PO": 51.0,
    "Invocations": 30.0,
    
    # Équipement spécifique
    "Arme de chasse": 5.0,
    
    # Dommages
    "Dommages": 20.0,
    "Dommages Terre": 5.0,
    "Dommages Feu": 5.0,
    "Dommages Eau": 5.0,
    "Dommage Neutre": 5.0,
    "Dommages Air": 5.0,
    
    # Pourcentages de résistances
    "% Résistance Terre": 6.0,
    "% Résistance Eau": 6.0,
    "% Résistance Air": 6.0,
    "% Résistance Feu": 6.0,
    "% Résistance Neutre": 6.0,
    
    # Résistances fixes
    "Résistances Neutre": 2.0,
    "Résistances Terre": 2.0,
    "Résistances Feu": 2.0,
    "Résistances Eau": 2.0,
    "Résistances Air": 2.0,
    
    # Autres résistances
    "Résistances Critiques": 2.0,
    "Résistances Poussée": 2.0,
    
    # Esquives et agression
    "Fuite": 4.0,
    "Tacle": 4.0,
    
    # Retraits et esquives
    "Retrait PA": 7.0,
    "Retrait PM": 7.0,
    "Esquive PM": 7.0,
    "Esquive PA": 7.0,
    
    # Dommages spéciaux
    "Dommages Critiques": 5.0,
    "Dommages Poussée": 5.0,
    "Dommages Renvoyés": 10.0,
    
    # Pièges
    "Puissance Pièges": 2.0,
    "Dommages Pièges": 5.0,
    
    # Pourcentages sur les dégâts
    "% Dommages aux sorts": 15.0,
    "% Dommages d'armes": 15.0,
    "% Dommages distance": 15.0,
    "% Dommages mêlée": 15.0,
    
    # Pourcentages sur les résistances
    "% Résistance mêlée": 15.0,
    "% Résistance distance": 15.0,
}

def normalize_text(txt):
    """
    Retire les accents et met en minuscules pour faire
    une comparaison insensible à la casse et aux accents.
    """
    # Convertir en forme "NFD" et éliminer les diacritiques (accents)
    txt = unicodedata.normalize('NFD', txt)
    txt = ''.join(c for c in txt if unicodedata.category(c) != 'Mn')
    # Mettre en minuscules
    return txt.lower()

def search_items_by_name(name, lang="fr"):
    base_url = "https://api.dofusdb.fr/items"
    normalized_input = normalize_text(name)
    params = {
        f"slug.{lang}[$search]": normalized_input,
        "lang": lang,
        "$limit": 50,
        "$skip": 0
    }
    all_data = []
    while True:
        resp = requests.get(base_url, params=params)
        resp.raise_for_status()
        response_json = resp.json()
        data = response_json.get("data", [])
        all_data.extend(data)
        if len(data) < params["$limit"]:
            break
        params["$skip"] += params["$limit"]
    wanted = normalize_text(name)
    filtered = [item for item in all_data
                if isinstance(item, dict) and wanted in normalize_text(item.get("name", {}).get(lang, ""))]
    allowed = {s.lower() for s in ALLOWED_EQUIPMENT_NAMES}
    final_results = []
    for item in filtered:
        type_name = item.get("type", {}).get("name", {}).get(lang, "")
        if type_name.lower() in allowed:
            final_results.append(item)
    return final_results
def select_item_interactively(items, lang="fr"):
    if not items:
        print("Aucun objet correspondant n'a été trouvé.")
        return None

    print("\nObjets trouvés :")
    for i, it in enumerate(items, start=1):
        name_obj = it.get("name", {}).get(lang, "Inconnu")
        lvl = it.get("level", "?")
        print(f"{i}) {name_obj} (niveau {lvl})")
    
    while True:
        choice = input(f"\nChoisissez un objet (1-{len(items)}) : ").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(items):
                return items[idx - 1]
        except ValueError:
            pass
        print("Choix invalide. Veuillez saisir un nombre entre 1 et", len(items))

def get_item_details(item_id):
    url = f"https://api.dofusdb.fr/items/{item_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def parse_item_stats(item_data):
    effects = item_data.get("effects", [])
    stats = []
    ALWAYS_USE_MAX = {111, 128, 117, 182}  # PA, PM, PO, Invocations
    NO_VALUE_EFFECTS = {795}

    for eff in effects:
        effect_id = eff.get("effectId")
        info = EFFECT_ID_TO_STAT.get(effect_id)
        if not info:
            continue            
        stat_name = info  # Ici, vous pouvez stocker le nom sans signe
        operator = eff.get("characteristicOperator", "+")
        val_from = eff.get("from", 0)
        val_to   = eff.get("to", 0)
        if effect_id in NO_VALUE_EFFECTS:
            val_from = 1
            val_to = 1
        if val_to == 0:
            val_to = val_from
        real_min = min(val_from, val_to)
        real_max = max(val_from, val_to)
        
        # Si c'est un effet pour lequel vous forcez la valeur max (PA, etc.)
        if effect_id in ALWAYS_USE_MAX and val_to > 0:
            real_min = val_to
            real_max = val_to

        # Appliquer le signe si nécessaire
        if operator == "-":
            # Si l'API renvoie déjà un intervalle négatif, ne modifiez rien.
            if real_min >= 0:
                real_min = -real_min
                real_max = -real_max
        stats.append({
            "statName": stat_name,
            "min": real_min,
            "max": real_max
        })
    return stats


def ask_theoretical_or_custom(stats_list):
    print("\nL'objet possède les stats suivantes :")
    for s in stats_list:
        print(f"- {s['statName']}: de {s['min']} à {s['max']}")
    while True:
        choice = input("\nUtiliser les stats théoriques ? (o/n, par défaut o) : ").strip().lower()
        if choice == "":
            choice = "o"
        if choice in ["o", "oui"]:
            return True
        elif choice in ["n", "non"]:
            return False
        else:
            print("Réponse invalide. Répondez par 'o' ou 'n'.")

def ask_coefficient():
    coeff_str = input("\nEntrez le coefficient (par défaut 100%) : ").strip()
    if coeff_str == "":
        return 100.0
    try:
        return float(coeff_str)
    except ValueError:
        print("Valeur invalide, utilisation de 100%.")
        return 100.0

def ask_focus():
    focus = input("\nY a-t-il un focus sur une stat spécifique ? (nom exact ou vide) : ").strip()
    return focus if focus else None

def calculate_brissage(stats_dict, level, coefficient=100.0, focus=None):
    """
    Calcule le brisage pour un ensemble de stats.
    - stats_dict: { "Vitalité": valeur, "Force": valeur, ... }
    - level: niveau de l'objet
    - coefficient: pourcentage (ex. 100.0 => 100%)
    - focus: nom EXACT de la stat (ex. "Vitalité") ou None

    Retourne un dict {stat: (nb_runes, chance_en_%)}.

    LOGIQUE:
      - S'il n'y a pas de focus, on calcule stat par stat (comme avant).
      - S'il y a un focus, on additionne (poidsFocus) + 0.5*(poidsOthers),
        on applique le coefficient, puis on convertit tout en runes de la stat focusée.
    """

    # --- CAS SANS FOCUS : on calcule stat par stat ---
    if not focus:
        results = {}
        for stat_name, value in stats_dict.items():
            if stat_name in {"PA", "PM", "PO", "Invocations"} and value >= 0 and value <= 1:
                value = 1
            if value <= 0:
                continue
            poids_rune = POIDS_RUNES.get(stat_name, 1)
            if stat_name == "Pods":
                # Si la stat est "Pods" on divise value par 2.5
                value = value / 2.5
            poids = ((value * poids_rune * level * 0.0150) + 1)
            # Application du coefficient
            poids *= (coefficient / 100.0)

            # Conversion en runes
            nb_runes_float = poids / poids_rune
            if poids_rune < 1:
                nb_runes = int(poids)
                reste = (poids - nb_runes) * 100.0
            else:
                nb_runes = int(nb_runes_float)
                reste_float  = (poids % poids_rune) / poids_rune * 100.0
                reste = int(reste_float)
            results[stat_name] = (nb_runes, reste)
        return results

    # --- CAS AVEC FOCUS : on fusionne tout en runes de la stat focusée ---
    # 1) Identifier la stat focusée (en ignorant la casse)
    focus_stat = None
    for stat_name in stats_dict.keys():
        if stat_name.lower() == focus.lower():
            focus_stat = stat_name
            break

    # Si l'objet ne possède pas la stat focusée, on retourne un dict vide
    if not focus_stat:
        return {}

    # 2) Calculer le poids de chaque stat
    poids_focus = 0.0
    poids_others = 0.0

    for stat_name, value in stats_dict.items():
        if value <= 0:
            continue
        poids_rune = POIDS_RUNES.get(stat_name, 1)
        w = ((value * poids_rune * level * 0.0150) + 1)

        if stat_name.lower() == focus.lower():
            poids_focus += w  # On ajoute la stat focus en entier
        else:
            # print w 
            poids_others += w  # On ajoutera les autres stats à 0.5

    # 3) Additionner focus + 0.5 * others
    total = poids_focus + 0.5 * poids_others

    # 4) Appliquer le coefficient
    total *= (coefficient / 100.0)

    if focus_stat == "Pods":
        # Si la stat est "Pods" on divise value par 2.5
        total = total / 2.5

    # 5) Convertir ce total en runes de la stat focus
    if POIDS_RUNES.get(focus_stat, 1) < 1:
        nb_runes = int(total)
        reste = (total - nb_runes) * 100.0
    else:
        poids_rune_focus = POIDS_RUNES.get(focus_stat, 1)
        nb_runes_float = total/ poids_rune_focus
        nb_runes = int(nb_runes_float)
        reste_float = (total % poids_rune_focus) / poids_rune_focus * 100.0
        reste = int(reste_float)
    return {focus_stat: (nb_runes, reste)}

def display_table(results, title="Résultats du brisage"):
    console = Console()
    table = Table(title=title)

    table.add_column("Stat", justify="left", style="cyan", no_wrap=True)
    table.add_column("Runes garanties", justify="right", style="green")
    table.add_column("Chance d'un +1", justify="right", style="magenta")

    for stat, (count, chance) in results.items():
        table.add_row(stat, str(count), f"{chance:.2f}%")

    console.print(table)


def main():
    item_name = input("Entrez le nom de l'objet : ").strip()
    if not item_name:
        print("Nom vide, arrêt.")
        return

    found_items = search_items_by_name(item_name, lang="fr")
    chosen_item = select_item_interactively(found_items, lang="fr")
    if not chosen_item:
        return

    item_details = get_item_details(chosen_item["id"])
    level = item_details.get("level", 40)  # Si non défini, utiliser 40 par défaut
    print(f"\nObjet sélectionné : {item_details.get('name', {}).get('fr', 'Inconnu')} (niveau {level})")

    stats_list = parse_item_stats(item_details)
    # print(json.dumps(item_details, indent=2, ensure_ascii=False))
    use_theoretical = ask_theoretical_or_custom(stats_list)

    coefficient = ask_coefficient()
    focus_stat = ask_focus()

    if use_theoretical:
        stats_min = {}
        stats_moy = {}
        stats_max = {}
        for s in stats_list:
            name = s["statName"]
            mini = s["min"]
            maxi = s["max"]
            moy = int((mini + maxi) / 2)
            stats_min[name] = mini
            stats_moy[name] = moy
            stats_max[name] = maxi

        res_min = calculate_brissage(stats_min, level, coefficient, focus_stat)
        res_moy = calculate_brissage(stats_moy, level, coefficient, focus_stat)
        res_max = calculate_brissage(stats_max, level, coefficient, focus_stat)

        display_table(res_min, title="Brisage (jet MIN)")
        display_table(res_moy, title="Brisage (jet MOYEN)")
        display_table(res_max, title="Brisage (jet MAX)")
    else:
        manual_stats = {}
        for s in stats_list:
            name = s["statName"]
            val_str = input(f"Entrez la valeur pour {name} (entre {s['min']} et {s['max']}): ")
            try:
                val = int(val_str)
            except ValueError:
                print(f"Valeur invalide, utilisation de {s['min']}")
                val = s["min"]
            manual_stats[name] = val

        res_manual = calculate_brissage(manual_stats, level, coefficient, focus_stat)
        display_table(res_manual, title="Brisage (valeurs manuelles)")

if __name__ == "__main__":
    main()
