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
    Conversion directe de X, Y, Z en latitude, longitude et hauteur.

    Entrées :
        X, Y, Z, a, b : mètres.

    Sorties :
        latitude, longitude : degrés.
        hauteur : mètres.
        Longitude = None sur l'axe des pôles.

    Formule approchée adaptée aux ellipsoïdes terrestres
    et aux points proches de la surface ou au-dessus.
    """
    verifier_ellipsoide(a, b)

    if not all(math.isfinite(valeur) for valeur in (X, Y, Z)):
        raise ValueError("Les coordonnées doivent être des nombres finis.")

    # 1. Distance du point à l'axe des pôles.
    p = math.hypot(X, Y)

    # 2. Cas particuliers : centre et pôles.
    if p == 0:
        if Z == 0:
            raise ValueError(
                "Au centre de l'ellipsoïde, la conversion n'est pas unique."
            )

        latitude_deg = 90.0 if Z > 0 else -90.0
        longitude_deg = None
        h = abs(Z) - b

        return latitude_deg, longitude_deg, h

    # 3. Paramètres de l'ellipsoïde.
    e2 = calculer_excentricite(a, b)
    f = (a - b) / a

    # 4. Distance du point au centre de l'ellipsoïde.
    # r = sqrt(X² + Y² + Z²).
    r = math.hypot(p, Z)

    # 5. Longitude.
    longitude = math.atan2(Y, X)

    # 6. Angle auxiliaire mu, utilisé par la méthode directe.
    # Cet angle est calculé en radians.
    mu = math.atan2(Z * ((1 - f) + a * e2 / r), p)

    # 7. Latitude calculée directement, sans itérations.
    numerateur = Z * (1 - f) + e2 * a * math.sin(mu) ** 3

    denominateur = (1 - f) * (p - e2 * a * math.cos(mu) ** 3)

    latitude = math.atan2(numerateur, denominateur)

    # 8. Hauteur ellipsoïdale.
    h = (
        p * math.cos(latitude)
        + Z * math.sin(latitude)
        - a * math.sqrt(1 - e2 * math.sin(latitude) ** 2)
    )

    # 9. Conversion des angles en degrés.
    latitude_deg = math.degrees(latitude)
    longitude_deg = math.degrees(longitude)

    return latitude_deg, longitude_deg, h
