import tkinter as tk
from tkinter import ttk, messagebox
import unicodedata
import requests
import math

# --- CONSTANTES ET MAPPAGES ---

ALLOWED_EQUIPMENT_NAMES = {
    "amulette", "anneau", "arme", "bottes", "bouclier", "cape", "ceinture",
    "chapeau", "arc", "baguette", "bâton", "dague", "épée", "marteau", "pelle",
    "hache", "outil", "pioche", "faux", "arme magique", "lance"
}

EFFECT_ID_TO_STAT = {
    # POSITIFS
    125: "Vitalité",
    126: "Intelligence",
    119: "Agilité",
    118: "Force",
    123: "Chance",
    138: "Puissance",
    158: "Pods",
    174: "Initiative",
    176: "Prospection",
    124: "Sagesse",
    115: "% Critique",
    178: "Soins",
    111: "PA",
    128: "PM",
    117: "PO",
    182: "Invocations",
    795: "Arme de chasse",
    112: "Dommages",
    422: "Dommages Terre",
    424: "Dommages Feu",
    426: "Dommages Eau",
    430: "Dommage Neutre",
    428: "Dommages Air",
    210: "% Résistance Terre",
    211: "% Résistance Eau",
    212: "% Résistance Air",
    213: "% Résistance Feu",
    214: "% Résistance Neutre",
    244: "Résistances Neutre",
    240: "Résistances Terre",
    243: "Résistances Feu",
    241: "Résistances Eau",
    242: "Résistances Air",
    420: "Résistances Critiques",
    416: "Résistances Poussée",
    752: "Fuite",
    753: "Tacle",
    410: "Retrait PA",
    412: "Retrait PM",
    161: "Esquive PM",
    160: "Esquive PA",
    418: "Dommages Critiques",
    414: "Dommages Poussée",
    220: "Dommages Renvoyés",
    226: "Puissance Pièges",
    225: "Dommages Pièges",
    2812: "% Dommages aux sorts",
    2808: "% Dommages d'armes",
    2805: "% Dommages distance",
    2800: "% Dommages mêlée",
    2803: "% Résistance mêlée",
    2807: "% Résistance distance",
    # NEGATIFS
    153: "Vitalité",
    155: "Intelligence",
    154: "Agilité",
    157: "Force",
    152: "Chance",
    186: "Puissance",
    159: "Pods",
    175: "Initiative",
    177: "Prospection",
    156: "Sagesse",
    171: "% Critique",
    179: "Soins",
    168: "PA",
    169: "PM",
    145: "Dommages",
    423: "Dommages Terre",
    425: "Dommages Feu",
    427: "Dommages Eau",
    431: "Dommage Neutre",
    429: "Dommages Air",
    215: "% Résistance Terre",
    216: "% Résistance Eau",
    217: "% Résistance Air",
    218: "% Résistance Feu",
    219: "% Résistance Neutre",
    249: "Résistances Neutre",
    245: "Résistances Terre",
    248: "Résistances Feu",
    246: "Résistances Eau",
    247: "Résistances Air",
    421: "Résistances Critiques",
    417: "Résistances Poussée",
    754: "Fuite",
    755: "Tacle",
    411: "Retrait PA",
    413: "Retrait PM",
    163: "Esquive PM",
    162: "Esquive PA",
    419: "Dommages Critiques",
    415: "Dommages Poussée",
    2813: "% Dommages aux sorts",
    2809: "% Dommages d'armes",
    2804: "% Dommages distance",
    2801: "% Dommages mêlée",
    2802: "% Résistance mêlée",
    2806: "% Résistance distance",
}

POIDS_RUNES = {
    "Vitalité": 0.2,
    "Intelligence": 1.0,
    "Agilité": 1.0,
    "Force": 1.0,
    "Chance": 1.0,
    "Puissance": 2.0,
    "Pods": 0.25,
    "Initiative": 0.1,
    "Prospection": 3.0,
    "Sagesse": 3.0,
    "% Critique": 10.0,
    "Soins": 10.0,
    "PA": 100.0,
    "PM": 90.0,
    "PO": 51.0,
    "Invocations": 30.0,
    "Arme de chasse": 5.0,
    "Dommages": 20.0,
    "Dommages Terre": 5.0,
    "Dommages Feu": 5.0,
    "Dommages Eau": 5.0,
    "Dommage Neutre": 5.0,
    "Dommages Air": 5.0,
    "% Résistance Terre": 6.0,
    "% Résistance Eau": 6.0,
    "% Résistance Air": 6.0,
    "% Résistance Feu": 6.0,
    "% Résistance Neutre": 6.0,
    "Résistances Neutre": 2.0,
    "Résistances Terre": 2.0,
    "Résistances Feu": 2.0,
    "Résistances Eau": 2.0,
    "Résistances Air": 2.0,
    "Résistances Critiques": 2.0,
    "Résistances Poussée": 2.0,
    "Fuite": 4.0,
    "Tacle": 4.0,
    "Retrait PA": 7.0,
    "Retrait PM": 7.0,
    "Esquive PM": 7.0,
    "Esquive PA": 7.0,
    "Dommages Critiques": 5.0,
    "Dommages Poussée": 5.0,
    "Dommages Renvoyés": 10.0,
    "Puissance Pièges": 2.0,
    "Dommages Pièges": 5.0,
    "% Dommages aux sorts": 15.0,
    "% Dommages d'armes": 15.0,
    "% Dommages distance": 15.0,
    "% Dommages mêlée": 15.0,
    "% Résistance mêlée": 15.0,
    "% Résistance distance": 15.0,
}

def normalize_text(txt):
    txt = unicodedata.normalize('NFD', txt)
    txt = ''.join(c for c in txt if unicodedata.category(c) != 'Mn')
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

def get_item_details(item_id):
    url = f"https://api.dofusdb.fr/items/{item_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def parse_item_stats(item_data):
    effects = item_data.get("effects", [])
    stats = []
    ALWAYS_USE_MAX = {111, 128, 117, 182}  # PA, PM, PO, Invocations
    for eff in effects:
        effect_id = eff.get("effectId")
        info = EFFECT_ID_TO_STAT.get(effect_id)
        if not info:
            continue
        stat_name = info
        operator = eff.get("characteristicOperator", "+")
        val_from = eff.get("from", 0)
        val_to   = eff.get("to", 0)
        real_min = min(val_from, val_to)
        real_max = max(val_from, val_to)
        if effect_id in ALWAYS_USE_MAX and val_to > 0:
            real_min = val_to
            real_max = val_to
        if operator == "-" and real_min >= 0:
            real_min = -real_min
            real_max = -real_max
        stats.append({
            "statName": stat_name,
            "min": real_min,
            "max": real_max
        })
    return stats

def calculate_brissage(stats_dict, level, coefficient=100.0, focus=None):
    # focus=None => pas de focus
    if not focus:
        results = {}
        for stat_name, value in stats_dict.items():
            if stat_name in {"PA", "PM", "PO", "Invocations"} and value >= 0 and value <= 1:
                value = 1
            if value <= 0:
                continue
            poids_rune = POIDS_RUNES.get(stat_name, 1)
            poids = ((value * poids_rune * level * 0.0150) + 1)
            poids *= (coefficient / 100.0)

            if poids_rune < 1:
                nb_runes = int(poids)
                reste = (poids - nb_runes) * 100.0
            else:
                nb_runes_float = poids / poids_rune
                nb_runes = int(nb_runes_float)
                reste = int(((poids % poids_rune) / poids_rune * 100.0))
            results[stat_name] = (nb_runes, reste)
        return results

    # CAS AVEC FOCUS
    focus_stat = None
    for stat_name in stats_dict.keys():
        if stat_name.lower() == focus.lower():
            focus_stat = stat_name
            break
    if not focus_stat:
        return {}
    poids_focus = 0.0
    poids_others = 0.0
    for stat_name, value in stats_dict.items():
        if stat_name in {"PA", "PM", "PO", "Invocations"} and value >= 0 and value <= 1:
            value = 1
        if value <= 0:
            continue
        poids_rune = POIDS_RUNES.get(stat_name, 1)
        w = ((value * poids_rune * level * 0.0150) + 1)
        if stat_name.lower() == focus.lower():
            poids_focus += w
        else:
            poids_others += w
    total = poids_focus + 0.5 * poids_others
    total *= (coefficient / 100.0)
    if poids_rune < 1:
        nb_runes = int(total)
        reste = (total - nb_runes) * 100.0
    else:
        poids_rune_focus = POIDS_RUNES.get(focus_stat, 1)
        nb_runes_float = total
        nb_runes = int(nb_runes_float)
        reste = int(((total % poids_rune_focus) / poids_rune_focus * 100.0))
    return {focus_stat: (nb_runes, reste)}


class BrisageApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dofus 3.0 - Calculateur de taux d'obtention de rune")
        try:
            self.iconbitmap("dofus_icon.ico")  # Chemin vers votre icône
        except Exception:
            pass

        # Thème sombre
        self.bg_color = "#1a1a1a"
        self.fg_color = "#FFFFFF"
        self.btn_bg = "#444444"
        self.btn_fg = "#FFFFFF"
        self.configure(bg=self.bg_color)
        self.geometry("600x500")
        
        # Variables
        self.found_items = []
        self.selected_item = None
        self.item_details = None
        self.stats_list = []
        self.mode_var = tk.StringVar(value="theorique")
        self.coeff_var = tk.StringVar(value="100")
        self.focus_var = tk.StringVar(value="Aucune")  # Par défaut "Aucune"
        self.manual_entries = {}
        
        # Frames
        self.search_frame = tk.Frame(self, bg=self.bg_color)
        self.results_frame = tk.Frame(self, bg=self.bg_color)
        self.options_frame = tk.Frame(self, bg=self.bg_color)
        self.manual_frame = tk.Frame(self, bg=self.bg_color)
        self.result_frame = tk.Frame(self, bg=self.bg_color)
        
        self.create_search_frame()
        self.create_results_frame()
        self.create_options_frame()
        self.create_manual_frame()
        self.create_result_frame()
        
        # Style ttk
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=self.bg_color, fieldbackground=self.bg_color, foreground=self.fg_color)
        self.style.configure("Treeview.Heading", background=self.btn_bg, foreground=self.btn_fg)
        
        self.show_frame(self.search_frame)

    def show_frame(self, frame):
        for f in (self.search_frame, self.results_frame, self.options_frame, self.manual_frame, self.result_frame):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    # --- Frame de recherche ---
    def create_search_frame(self):
        for widget in self.search_frame.winfo_children():
            widget.destroy()
        lbl = tk.Label(self.search_frame, text="Entrez le nom de l'objet :", font=("Arial", 12),
                       bg=self.bg_color, fg=self.fg_color)
        lbl.pack(pady=20, padx=20)
        self.item_entry = tk.Entry(self.search_frame, width=40, font=("Arial", 12),
                                   bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color)
        self.item_entry.pack(pady=10, padx=20)
        btn = tk.Button(self.search_frame, text="Rechercher", command=self.search_items,
                        font=("Arial", 12), bg=self.btn_bg, fg=self.btn_fg)
        btn.pack(pady=20)
    
    def search_items(self):
        name = self.item_entry.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom d'objet.")
            return
        try:
            self.found_items = search_items_by_name(name, lang="fr")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {e}")
            return
        if not self.found_items:
            messagebox.showinfo("Information", "Aucun objet correspondant n'a été trouvé.")
            return
        self.populate_results()
        self.show_frame(self.results_frame)
    
    # --- Frame des résultats de recherche ---
    def create_results_frame(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        lbl = tk.Label(self.results_frame, text="Objets trouvés :", font=("Arial", 12),
                       bg=self.bg_color, fg=self.fg_color)
        lbl.pack(pady=20)
        self.items_listbox = tk.Listbox(self.results_frame, width=80, font=("Arial", 10),
                                        bg=self.bg_color, fg=self.fg_color, selectbackground=self.fg_color,
                                        selectforeground=self.bg_color)
        self.items_listbox.pack(pady=10, padx=20, fill="both", expand=True)
        btn = tk.Button(self.results_frame, text="Sélectionner l'objet", command=self.select_item,
                        font=("Arial", 12), bg=self.btn_bg, fg=self.btn_fg)
        btn.pack(pady=20)
        btn_back = tk.Button(self.results_frame, text="Retour", command=lambda: self.show_frame(self.search_frame),
                             font=("Arial", 10), bg=self.btn_bg, fg=self.btn_fg)
        btn_back.pack(pady=10)
    
    def populate_results(self):
        self.items_listbox.delete(0, tk.END)
        for idx, item in enumerate(self.found_items, start=1):
            name_obj = item.get("name", {}).get("fr", "Inconnu")
            lvl = item.get("level", "?")
            self.items_listbox.insert(tk.END, f"{idx}) {name_obj} (niveau {lvl})")
    
    def select_item(self):
        try:
            index = self.items_listbox.curselection()[0]
        except IndexError:
            messagebox.showerror("Erreur", "Veuillez sélectionner un objet dans la liste.")
            return
        self.selected_item = self.found_items[index]
        try:
            self.item_details = get_item_details(self.selected_item["id"])
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des détails : {e}")
            return
        self.stats_list = parse_item_stats(self.item_details)
        self.populate_options()
        self.show_frame(self.options_frame)
    
    # --- Frame des options (théorique vs manuel) ---
    def create_options_frame(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.item_info_lbl = tk.Label(self.options_frame, text="", font=("Arial", 12),
                                      bg=self.bg_color, fg=self.fg_color)
        self.item_info_lbl.pack(pady=20)
        mode_frame = tk.Frame(self.options_frame, bg=self.bg_color)
        mode_frame.pack(pady=10)
        lbl_mode = tk.Label(mode_frame, text="Choix du mode :", font=("Arial", 12),
                            bg=self.bg_color, fg=self.fg_color)
        lbl_mode.grid(row=0, column=0, padx=10)
        rb_theo = tk.Radiobutton(mode_frame, text="Stats théoriques", variable=self.mode_var, value="theorique",
                                 font=("Arial", 10), bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color)
        rb_theo.grid(row=0, column=1, padx=10)
        rb_manual = tk.Radiobutton(mode_frame, text="Valeurs manuelles", variable=self.mode_var, value="manuel",
                                   font=("Arial", 10), bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color)
        rb_manual.grid(row=0, column=2, padx=10)

        coeff_frame = tk.Frame(self.options_frame, bg=self.bg_color)
        coeff_frame.pack(pady=10)
        lbl_coeff = tk.Label(coeff_frame, text="Coefficient (%):", font=("Arial", 12),
                             bg=self.bg_color, fg=self.fg_color)
        lbl_coeff.grid(row=0, column=0, padx=10)
        self.coeff_entry = tk.Entry(coeff_frame, textvariable=self.coeff_var, width=10, font=("Arial", 12),
                                    bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color)
        self.coeff_entry.grid(row=0, column=1, padx=10)

        focus_frame = tk.Frame(self.options_frame, bg=self.bg_color)
        focus_frame.pack(pady=10)
        lbl_focus = tk.Label(focus_frame, text="Focus sur la stat :", font=("Arial", 12),
                             bg=self.bg_color, fg=self.fg_color)
        lbl_focus.grid(row=0, column=0, padx=10)

        # Liste des stats disponibles + "Aucune"
        stats_focus_options = ["Aucune"] + sorted(POIDS_RUNES.keys(), key=str.lower)
        # Combobox (liste déroulante) au lieu d'un Entry
        self.focus_combobox = ttk.Combobox(
            focus_frame,
            values=stats_focus_options,
            textvariable=self.focus_var,
            state="readonly",
            width=20
        )
        self.focus_combobox.set("Aucune")  # Valeur par défaut
        self.focus_combobox.grid(row=0, column=1, padx=10)

        btn_valider = tk.Button(self.options_frame, text="Valider", command=self.process_options,
                                font=("Arial", 12), bg=self.btn_bg, fg=self.btn_fg)
        btn_valider.pack(pady=20)
        btn_back = tk.Button(self.options_frame, text="Retour", command=lambda: self.show_frame(self.results_frame),
                             font=("Arial", 10), bg=self.btn_bg, fg=self.btn_fg)
        btn_back.pack(pady=10)
    
    def populate_options(self):
        name_obj = self.item_details.get("name", {}).get("fr", "Inconnu")
        level = self.item_details.get("level", 40)
        self.item_info_lbl.config(text=f"Objet sélectionné : {name_obj} (niveau {level})")
    
    def process_options(self):
        try:
            coeff = float(self.coeff_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Coefficient invalide. Utilisez 100 par défaut.")
            coeff = 100.0

        # Si l'utilisateur choisit "Aucune", on considère qu'il n'y a pas de focus
        chosen_focus = self.focus_var.get()
        if chosen_focus == "Aucune":
            chosen_focus = None

        mode = self.mode_var.get()
        self.coeff_var.set(str(coeff))

        if mode == "theorique":
            stats_min = {}
            stats_moy = {}
            stats_max = {}
            for s in self.stats_list:
                name = s["statName"]
                mini = s["min"]
                maxi = s["max"]
                moy = int((mini + maxi) / 2)
                stats_min[name] = mini
                stats_moy[name] = moy
                stats_max[name] = maxi
            self.theoretical_stats = {
                "jet MIN": stats_min,
                "jet MOYEN": stats_moy,
                "jet MAX": stats_max,
            }
            self.display_theoretical_results(coeff, chosen_focus)
        else:
            self.populate_manual_frame()
            self.show_frame(self.manual_frame)
    
    # --- Frame pour saisie des valeurs manuelles ---
    def create_manual_frame(self):
        for widget in self.manual_frame.winfo_children():
            widget.destroy()
        self.manual_inputs_frame = tk.Frame(self.manual_frame, bg=self.bg_color)
        self.manual_inputs_frame.pack(pady=20, fill="both", expand=True)
        btn_calc = tk.Button(self.manual_frame, text="Calculer le brisage", command=self.calculate_manual,
                             font=("Arial", 12), bg=self.btn_bg, fg=self.btn_fg)
        btn_calc.pack(pady=20)
        btn_back = tk.Button(self.manual_frame, text="Retour", command=lambda: self.show_frame(self.options_frame),
                             font=("Arial", 10), bg=self.btn_bg, fg=self.btn_fg)
        btn_back.pack(pady=10)
    
    def populate_manual_frame(self):
        for widget in self.manual_inputs_frame.winfo_children():
            widget.destroy()
        self.manual_entries = {}
        unique_stats = {}
        for s in self.stats_list:
            stat = s["statName"]
            if stat not in unique_stats:
                unique_stats[stat] = (s["min"], s["max"])
        row = 0
        for stat, (mini, maxi) in unique_stats.items():
            lbl = tk.Label(self.manual_inputs_frame, text=f"{stat} (entre {mini} et {maxi}) :", font=("Arial", 10),
                           bg=self.bg_color, fg=self.fg_color)
            lbl.grid(row=row, column=0, padx=10, pady=5, sticky="e")
            ent = tk.Entry(self.manual_inputs_frame, width=10, font=("Arial", 10),
                           bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color)
            default_value = mini if maxi <= 0 else maxi
            ent.insert(0, str(default_value))
            ent.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            self.manual_entries[stat] = ent
            row += 1
    
    def calculate_manual(self):
        stats_manual = {}
        for stat, ent in self.manual_entries.items():
            try:
                val = int(ent.get().strip())
            except ValueError:
                messagebox.showinfo("Information", f"Valeur invalide pour {stat}, utilisation de la valeur minimale.")
                for s in self.stats_list:
                    if s["statName"] == stat:
                        val = s["min"]
                        break
            stats_manual[stat] = val
        try:
            coeff = float(self.coeff_entry.get())
        except ValueError:
            coeff = 100.0

        # Récupérer la valeur de la ComboBox
        chosen_focus = self.focus_var.get()
        if chosen_focus == "Aucune":
            chosen_focus = None

        level = self.item_details.get("level", 40)
        res = calculate_brissage(stats_manual, level, coeff, chosen_focus)
        self.display_result({"Brisage (valeurs manuelles)": res})
    
    # --- Frame des résultats ---
    def create_result_frame(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        btn_back = tk.Button(self.result_frame, text="Retour à l'accueil", command=lambda: self.show_frame(self.search_frame),
                             font=("Arial", 12), bg=self.btn_bg, fg=self.btn_fg)
        btn_back.pack(pady=20)
        self.notebook = ttk.Notebook(self.result_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
    
    def display_theoretical_results(self, coeff, focus):
        self.create_result_frame()
        level = self.item_details.get("level", 40)
        for label, stats in self.theoretical_stats.items():
            res = calculate_brissage(stats, level, coeff, focus)
            tab = tk.Frame(self.notebook, bg=self.bg_color)
            self.populate_treeview(tab, res)
            self.notebook.add(tab, text=label)
        self.show_frame(self.result_frame)
    
    def display_result(self, result_dict):
        self.create_result_frame()
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.populate_treeview(tab, list(result_dict.values())[0])
        self.notebook.add(tab, text=list(result_dict.keys())[0])
        self.show_frame(self.result_frame)
    
    def populate_treeview(self, parent, results):
        columns = ("stat", "runes", "chance")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        tree.heading("stat", text="Stat")
        tree.heading("runes", text="Runes garanties")
        tree.heading("chance", text="Chance d'un +1")
        tree.column("stat", width=150)
        tree.column("runes", width=120, anchor="center")
        tree.column("chance", width=150, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=20)
        for stat, (count, chance) in results.items():
            tree.insert("", tk.END, values=(stat, count, f"{chance:.2f}%"))

if __name__ == "__main__":
    app = BrisageApp()
    app.mainloop()
