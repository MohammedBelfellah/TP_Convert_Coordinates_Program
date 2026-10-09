import unittest

from conversion_geodesique import (
    geodesiques_vers_xyz,
    xyz_vers_geodesiques,
)


class TestConversionGeodesique(unittest.TestCase):

    def setUp(self):
        """Paramètres WGS84 utilisés pour chaque test."""
        self.a = 6378137.0
        f = 1 / 298.257223563
        self.b = self.a * (1 - f)

        # Tolérances de comparaison.
        self.tolerance_angle = 1e-8  # Degrés
        self.tolerance_hauteur = 1e-4  # Mètres : 0,1 mm

    def verifier_aller_retour(self, latitude, longitude, hauteur):
        """Convertit dans les deux sens et compare les résultats."""

        # 1. Coordonnées géodésiques → cartésiennes.
        X, Y, Z = geodesiques_vers_xyz(latitude, longitude, hauteur, self.a, self.b)

        # 2. Le résultat devient l'entrée de la conversion inverse.
        latitude_retour, longitude_retour, hauteur_retour = xyz_vers_geodesiques(
            X, Y, Z, self.a, self.b
        )

        # 3. Comparer les latitudes.
        self.assertAlmostEqual(
            latitude_retour,
            latitude,
            delta=self.tolerance_angle,
            msg="La latitude retrouvée est incorrecte.",
        )

        # 4. Comparer les longitudes, sauf aux pôles.
        if abs(latitude) == 90:
            self.assertIsNone(longitude_retour)
        else:
            self.assertIsNotNone(longitude_retour)

            # +180° et -180° représentent le même méridien.
            difference_longitude = (longitude_retour - longitude + 180) % 360 - 180

            self.assertAlmostEqual(
                difference_longitude,
                0,
                delta=self.tolerance_angle,
                msg="La longitude retrouvée est incorrecte.",
            )

        # 5. Comparer les hauteurs.
        self.assertAlmostEqual(
            hauteur_retour,
            hauteur,
            delta=self.tolerance_hauteur,
            msg="La hauteur retrouvée est incorrecte.",
        )

    def test_aller_retour(self):
        """Vérifie plusieurs positions et hauteurs."""
        cas = [
            # Nom, latitude, longitude, hauteur.
            ("Équateur Greenwich", 0, 0, 0),
            ("Nord Est", 35, 45, 100),
            ("Nord Ouest", 35, -5, 100),
            ("Sud Est", -30, 135, 500),
            ("Sud Ouest", -45, -135, 200),
            ("Méridien 180°", 20, 180, 0),
            ("Méridien -180°", -20, -180, 0),
            ("Hauteur négative", 30, 10, -100),
            ("Grande hauteur", 50, 80, 1_000_000),
            ("Proche du pôle Nord", 89.999999, 40, 50),
            ("Proche du pôle Sud", -89.999999, -70, 50),
            ("Pôle Nord", 90, 0, 100),
            ("Pôle Sud", -90, 0, 100),
        ]

        for nom, latitude, longitude, hauteur in cas:
            with self.subTest(cas=nom):
                self.verifier_aller_retour(latitude, longitude, hauteur)

    def test_point_connu(self):
        """
        Contrôle indépendant :
        latitude 0°, longitude 0°, hauteur 0 → (a, 0, 0).
        """
        X, Y, Z = geodesiques_vers_xyz(0, 0, 0, self.a, self.b)

        self.assertAlmostEqual(X, self.a, delta=1e-6)
        self.assertAlmostEqual(Y, 0, delta=1e-6)
        self.assertAlmostEqual(Z, 0, delta=1e-6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
