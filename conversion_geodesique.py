import math


def calculer_excentricite(a, b):
    """Retourne e² à partir des demi-axes a et b."""
    return (a**2 - b**2) / a**2


def calculer_N(latitude, a, e2):
    """Calcule la grande normale N. Latitude en radians."""
    return a / math.sqrt(1 - e2 * math.sin(latitude)**2)


def verifier_ellipsoide(a, b):
    """Vérifie que les dimensions de l'ellipsoïde sont valides."""
    if not all(math.isfinite(valeur) for valeur in (a, b)):
        raise ValueError("Les demi-axes doivent être des nombres finis.")

    if not 0 < b <= a:
        raise ValueError("Il faut respecter : 0 < b <= a.")


def geodesiques_vers_xyz(latitude_deg, longitude_deg, h, a, b):
    """
    Convertit latitude, longitude et hauteur en X, Y, Z.

    Entrées :
        latitude_deg, longitude_deg : degrés
        h, a, b : mètres

    Sortie :
        X, Y, Z : mètres
    """
    verifier_ellipsoide(a, b)

    valeurs = (latitude_deg, longitude_deg, h)
    if not all(math.isfinite(valeur) for valeur in valeurs):
        raise ValueError("Les coordonnées doivent être des nombres finis.")

    if not -90 <= latitude_deg <= 90:
        raise ValueError("La latitude doit être entre -90° et 90°.")

    if not -180 <= longitude_deg <= 180:
        raise ValueError("La longitude doit être entre -180° et 180°.")

    # 1. Convertir les angles en radians.
    latitude = math.radians(latitude_deg)
    longitude = math.radians(longitude_deg)

    # 2. Calculer les paramètres nécessaires.
    e2 = calculer_excentricite(a, b)
    N = calculer_N(latitude, a, e2)

    # 3. Appliquer les formules de conversion.
    X = (N + h) * math.cos(latitude) * math.cos(longitude)
    Y = (N + h) * math.cos(latitude) * math.sin(longitude)
    Z = (N * (1 - e2) + h) * math.sin(latitude)

    # Aux pôles, X et Y sont exactement nuls.
    if abs(latitude_deg) == 90:
        X = 0.0
        Y = 0.0

    return X, Y, Z


def xyz_vers_geodesiques(X, Y, Z, a, b):
    """
    Convertit X, Y, Z en latitude, longitude et hauteur.

    Méthode adaptée aux points proches de la surface terrestre
    ou au-dessus, pas aux points profondément à l'intérieur.

    Entrées :
        X, Y, Z, a, b : mètres

    Sortie :
        latitude et longitude : degrés
        hauteur : mètres

    Sur l'axe des pôles, la longitude retournée est None :
    elle est indéterminée.
    """
    verifier_ellipsoide(a, b)

    if not all(math.isfinite(valeur) for valeur in (X, Y, Z)):
        raise ValueError("Les coordonnées doivent être des nombres finis.")

    # 1. Distance à l'axe des pôles.
    # hypot(X, Y) calcule sqrt(X² + Y²).
    p = math.hypot(X, Y)

    # 2. Traiter les cas particuliers.
    if p == 0:
        if Z == 0:
            raise ValueError(
                "Au centre de l'ellipsoïde, la conversion n'est pas unique."
            )

        latitude_deg = 90.0 if Z > 0 else -90.0
        longitude_deg = None
        h = abs(Z) - b

        return latitude_deg, longitude_deg, h

    # 3. Calculer la longitude.
    longitude = math.atan2(Y, X)

    # 4. Première estimation de la latitude.
    e2 = calculer_excentricite(a, b)
    latitude = math.atan2(Z, p * (1 - e2))

    tolerance = 1e-12  # Radians
    maximum_iterations = 50

    # 5. Améliorer progressivement la latitude.
    for iteration in range(maximum_iterations):
        N = calculer_N(latitude, a, e2)

        nouvelle_latitude = math.atan2(
            Z + e2 * N * math.sin(latitude),
            p
        )

        difference = abs(nouvelle_latitude - latitude)
        latitude = nouvelle_latitude

        if difference < tolerance:
            break
    else:
        # Ce bloc s'exécute si la boucle finit sans "break".
        raise ValueError("La latitude n'a pas convergé après 50 itérations.")

    # 6. Calculer la hauteur avec la latitude finale.
    h = (
        p * math.cos(latitude)
        + Z * math.sin(latitude)
        - a * math.sqrt(1 - e2 * math.sin(latitude)**2)
    )

    # 7. Convertir les angles en degrés.
    latitude_deg = math.degrees(latitude)
    longitude_deg = math.degrees(longitude)

    return latitude_deg, longitude_deg, h
