import tkinter as tk
from tkinter import ttk

from conversion_geodesique import geodesiques_vers_xyz, xyz_vers_geodesiques


DEMI_GRAND_AXE_WGS84 = 6378137.0
APLATISSEMENT_WGS84 = 1 / 298.257223563
DEMI_PETIT_AXE_WGS84 = DEMI_GRAND_AXE_WGS84 * (1 - APLATISSEMENT_WGS84)


def convertir_texte_en_nombre(texte, nom_grandeur):
    """Convertit une saisie en nombre et accepte la virgule décimale."""
    texte_normalise = texte.strip().replace(",", ".")

    if not texte_normalise:
        raise ValueError(f"Le champ « {nom_grandeur} » est obligatoire.")

    try:
        return float(texte_normalise)
    except ValueError as erreur:
        raise ValueError(
            f"Le champ « {nom_grandeur} » doit contenir un nombre valide."
        ) from erreur


class InterfaceConversionGeodesique:
    """Fenêtre unique permettant les deux conversions de coordonnées."""

    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Conversion de coordonnées géodésiques")
        self.fenetre.minsize(650, 650)

        self.sens_conversion = tk.StringVar(value="vers_cartesiennes")
        self.type_ellipsoide = tk.StringVar(value="wgs84")
        self.valeur_a = tk.StringVar(value=f"{DEMI_GRAND_AXE_WGS84:.3f}")
        self.valeur_b = tk.StringVar(value=f"{DEMI_PETIT_AXE_WGS84:.3f}")
        self.valeurs_entree = [tk.StringVar() for _ in range(3)]
        self.valeurs_resultat = [tk.StringVar(value="—") for _ in range(3)]
        self.message_etat = tk.StringVar(
            value="Saisissez les coordonnées, puis cliquez sur Convertir."
        )

        self.etiquettes_entree = []
        self.etiquettes_resultat = []

        self._configurer_styles()
        self._creer_contenu()
        self._mettre_a_jour_ellipsoide()
        self._mettre_a_jour_champs()

    def _configurer_styles(self):
        style = ttk.Style(self.fenetre)
        style.configure("Titre.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("SousTitre.TLabel", foreground="#4b5563")
        style.configure("Resultat.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Succes.TLabel", foreground="#16794b")
        style.configure("Erreur.TLabel", foreground="#b42318")

    def _creer_contenu(self):
        conteneur = ttk.Frame(self.fenetre, padding=24)
        conteneur.grid(row=0, column=0, sticky="nsew")
        self.fenetre.columnconfigure(0, weight=1)
        self.fenetre.rowconfigure(0, weight=1)
        conteneur.columnconfigure(0, weight=1)

        ttk.Label(
            conteneur,
            text="Conversion de coordonnées géodésiques",
            style="Titre.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            conteneur,
            text="Angles en degrés et longueurs en mètres",
            style="SousTitre.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 18))

        self._creer_zone_ellipsoide(conteneur, 2)
        self._creer_zone_sens(conteneur, 3)
        self._creer_zone_coordonnees(conteneur, 4)
        self._creer_zone_resultats(conteneur, 5)

        zone_actions = ttk.Frame(conteneur)
        zone_actions.grid(row=6, column=0, sticky="ew", pady=(18, 0))
        zone_actions.columnconfigure(0, weight=1)

        ttk.Button(
            zone_actions,
            text="Réinitialiser",
            command=self._reinitialiser,
        ).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(
            zone_actions,
            text="Convertir",
            command=self._effectuer_conversion,
        ).grid(row=0, column=2)

        self.etiquette_etat = ttk.Label(
            conteneur,
            textvariable=self.message_etat,
            style="SousTitre.TLabel",
            wraplength=590,
        )
        self.etiquette_etat.grid(row=7, column=0, sticky="w", pady=(14, 0))

        self.fenetre.bind("<Return>", lambda evenement: self._effectuer_conversion())

    def _creer_zone_ellipsoide(self, parent, ligne):
        zone = ttk.LabelFrame(parent, text=" Ellipsoïde ", padding=12)
        zone.grid(row=ligne, column=0, sticky="ew", pady=(0, 12))
        zone.columnconfigure(1, weight=1)

        ttk.Radiobutton(
            zone,
            text="WGS84",
            variable=self.type_ellipsoide,
            value="wgs84",
            command=self._mettre_a_jour_ellipsoide,
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))
        ttk.Radiobutton(
            zone,
            text="Personnalisé",
            variable=self.type_ellipsoide,
            value="personnalise",
            command=self._mettre_a_jour_ellipsoide,
        ).grid(row=0, column=1, sticky="w")

        ttk.Label(zone, text="Demi-grand axe a (m)").grid(
            row=1, column=0, sticky="w", pady=(12, 4)
        )
        ttk.Label(zone, text="Demi-petit axe b (m)").grid(
            row=1, column=1, sticky="w", pady=(12, 4)
        )

        self.champ_a = ttk.Entry(zone, textvariable=self.valeur_a)
        self.champ_a.grid(row=2, column=0, sticky="ew", padx=(0, 12))
        self.champ_b = ttk.Entry(zone, textvariable=self.valeur_b)
        self.champ_b.grid(row=2, column=1, sticky="ew")

    def _creer_zone_sens(self, parent, ligne):
        zone = ttk.LabelFrame(parent, text=" Sens de conversion ", padding=12)
        zone.grid(row=ligne, column=0, sticky="ew", pady=(0, 12))

        ttk.Radiobutton(
            zone,
            text="Géodésiques → cartésiennes",
            variable=self.sens_conversion,
            value="vers_cartesiennes",
            command=self._mettre_a_jour_champs,
        ).grid(row=0, column=0, sticky="w", padx=(0, 24))
        ttk.Radiobutton(
            zone,
            text="Cartésiennes → géodésiques",
            variable=self.sens_conversion,
            value="vers_geodesiques",
            command=self._mettre_a_jour_champs,
        ).grid(row=0, column=1, sticky="w")

    def _creer_zone_coordonnees(self, parent, ligne):
        zone = ttk.LabelFrame(parent, text=" Coordonnées d'entrée ", padding=12)
        zone.grid(row=ligne, column=0, sticky="ew", pady=(0, 12))

        for colonne in range(3):
            zone.columnconfigure(colonne, weight=1)
            etiquette = ttk.Label(zone)
            etiquette.grid(row=0, column=colonne, sticky="w", padx=(0, 8))
            self.etiquettes_entree.append(etiquette)

            champ = ttk.Entry(zone, textvariable=self.valeurs_entree[colonne])
            champ.grid(row=1, column=colonne, sticky="ew", padx=(0, 8), pady=(4, 0))

            if colonne == 0:
                self.premier_champ = champ

    def _creer_zone_resultats(self, parent, ligne):
        zone = ttk.LabelFrame(parent, text=" Résultats ", padding=12)
        zone.grid(row=ligne, column=0, sticky="ew")

        for colonne in range(3):
            zone.columnconfigure(colonne, weight=1)
            etiquette = ttk.Label(zone)
            etiquette.grid(row=0, column=colonne, sticky="w", padx=(0, 8))
            self.etiquettes_resultat.append(etiquette)

            ttk.Label(
                zone,
                textvariable=self.valeurs_resultat[colonne],
                style="Resultat.TLabel",
            ).grid(row=1, column=colonne, sticky="w", padx=(0, 8), pady=(4, 0))

    def _mettre_a_jour_ellipsoide(self):
        if self.type_ellipsoide.get() == "wgs84":
            self.valeur_a.set(f"{DEMI_GRAND_AXE_WGS84:.3f}")
            self.valeur_b.set(f"{DEMI_PETIT_AXE_WGS84:.3f}")
            etat = "disabled"
        else:
            etat = "normal"

        self.champ_a.configure(state=etat)
        self.champ_b.configure(state=etat)

    def _mettre_a_jour_champs(self):
        if self.sens_conversion.get() == "vers_cartesiennes":
            noms_entree = (
                "Latitude φ (°)",
                "Longitude λ (°)",
                "Hauteur h (m)",
            )
            noms_resultat = ("X (m)", "Y (m)", "Z (m)")
        else:
            noms_entree = ("X (m)", "Y (m)", "Z (m)")
            noms_resultat = (
                "Latitude φ (°)",
                "Longitude λ (°)",
                "Hauteur h (m)",
            )

        for etiquette, texte in zip(self.etiquettes_entree, noms_entree):
            etiquette.configure(text=texte)

        for etiquette, texte in zip(self.etiquettes_resultat, noms_resultat):
            etiquette.configure(text=texte)

        self._effacer_coordonnees()
        self.premier_champ.focus_set()

    def _lire_ellipsoide(self):
        a = convertir_texte_en_nombre(self.valeur_a.get(), "Demi-grand axe a")
        b = convertir_texte_en_nombre(self.valeur_b.get(), "Demi-petit axe b")
        return a, b

    def _effectuer_conversion(self):
        try:
            a, b = self._lire_ellipsoide()

            if self.sens_conversion.get() == "vers_cartesiennes":
                latitude = convertir_texte_en_nombre(
                    self.valeurs_entree[0].get(), "Latitude"
                )
                longitude = convertir_texte_en_nombre(
                    self.valeurs_entree[1].get(), "Longitude"
                )
                hauteur = convertir_texte_en_nombre(
                    self.valeurs_entree[2].get(), "Hauteur"
                )
                x, y, z = geodesiques_vers_xyz(
                    latitude, longitude, hauteur, a, b
                )
                resultats = (f"{x:.4f}", f"{y:.4f}", f"{z:.4f}")
            else:
                x = convertir_texte_en_nombre(self.valeurs_entree[0].get(), "X")
                y = convertir_texte_en_nombre(self.valeurs_entree[1].get(), "Y")
                z = convertir_texte_en_nombre(self.valeurs_entree[2].get(), "Z")
                latitude, longitude, hauteur = xyz_vers_geodesiques(x, y, z, a, b)
                longitude_affichee = (
                    "Indéterminée" if longitude is None else f"{longitude:.10f}"
                )
                resultats = (
                    f"{latitude:.10f}",
                    longitude_affichee,
                    f"{hauteur:.4f}",
                )

            for variable, valeur in zip(self.valeurs_resultat, resultats):
                variable.set(valeur)

            self.message_etat.set("Conversion effectuée avec succès.")
            self.etiquette_etat.configure(style="Succes.TLabel")
        except ValueError as erreur:
            self._effacer_resultats()
            self.message_etat.set(f"Erreur : {erreur}")
            self.etiquette_etat.configure(style="Erreur.TLabel")

    def _effacer_resultats(self):
        for variable in self.valeurs_resultat:
            variable.set("—")

    def _effacer_coordonnees(self):
        for variable in self.valeurs_entree:
            variable.set("")

        self._effacer_resultats()
        self.message_etat.set(
            "Saisissez les coordonnées, puis cliquez sur Convertir."
        )
        self.etiquette_etat.configure(style="SousTitre.TLabel")

    def _reinitialiser(self):
        self.sens_conversion.set("vers_cartesiennes")
        self.type_ellipsoide.set("wgs84")
        self._mettre_a_jour_ellipsoide()
        self._mettre_a_jour_champs()


def lancer_interface():
    """Crée et affiche l'interface graphique."""
    fenetre = tk.Tk()
    InterfaceConversionGeodesique(fenetre)
    fenetre.mainloop()


if __name__ == "__main__":
    lancer_interface()
