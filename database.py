import sqlite3
from candidat import Candidat


class Administrateur:
    def __init__(self, nom, prenom, courriel,
                 mot_de_passe_hash, mot_de_passe_salt, id=None,
                 reset_token=None, reset_token_expiration=None,
                 suspension=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.courriel = courriel
        self.mot_de_passe_hash = mot_de_passe_hash
        self.mot_de_passe_salt = mot_de_passe_salt
        self.reset_token = reset_token
        self.reset_token_expiration = reset_token_expiration
        self.suspension = suspension


class Database:

    def __init__(self):
        self.connection = None

    # --------------------Connections--------------------

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/database.db')
        return self.connection

    def deconnection(self):
        if self.connection is not None:
            self.connection.close()

    # -------------------Administrateur----------------------

    def login(self, courriel):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT nom, prenom, courriel, mot_de_passe_salt, "
                       "mot_de_passe_hash, suspension FROM "
                       "administrateur WHERE courriel = ?", (courriel,))
        return cursor.fetchone()

    def courriel_existe(self, courriel):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM administrateur WHERE courriel LIKE ?",
                       ('%' + courriel + '%',))
        utilisateur_existe = cursor.fetchall()
        if len(utilisateur_existe) == 0:
            return False
        else:
            return True

    def create_administrateur(self, administrateur):
        connection = self.get_connection()
        connection.execute(
            "INSERT INTO administrateur (nom, prenom, courriel, "
            "mot_de_passe_hash, mot_de_passe_salt, reset_token, "
            "reset_token_expiration, "
            "suspension) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (administrateur.nom, administrateur.prenom,
             administrateur.courriel, administrateur.mot_de_passe_hash,
             administrateur.mot_de_passe_salt, administrateur.reset_token,
             administrateur.reset_token_expiration,
             administrateur.suspension)
        )
        connection.commit()

    def get_administrateurs(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM administrateur")
        administrateurs = cursor.fetchall()
        liste_administrateurs = [Administrateur(
                                                id=row[0], nom=row[1],
                                                prenom=row[2], courriel=row[3],
                                                mot_de_passe_hash=row[4],
                                                mot_de_passe_salt=row[5],
                                                reset_token=row[6],
                                                reset_token_expiration=row[7],
                                                suspension=row[8])
                                 for row in administrateurs]
        return liste_administrateurs

    def update_administrateur(self, admin):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE administrateur SET nom = ?, prenom = ?, "
            "courriel = ?, mot_de_passe_hash = ?, "
            "mot_de_passe_salt = ? WHERE id = ?",
            (admin.nom, admin.prenom, admin.courriel,
             admin.mot_de_passe_hash, admin.mot_de_passe_salt, admin.id)
        )
        connection.commit()

    def delete_administrateur(self, administrateur_id):
        connection = self.get_connection()
        connection.execute("DELETE FROM administrateur WHERE id = ?",
                           (administrateur_id,))
        connection.commit()
        return True

    def get_administrateur_by_id(self, administrateur_id):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT id, nom, prenom, courriel, "
                       "suspension FROM administrateur WHERE id = ?",
                       (administrateur_id,))
        administrateur = cursor.fetchone()
        if administrateur:
            return Administrateur(id=administrateur[0],
                                  nom=administrateur[1],
                                  prenom=administrateur[2],
                                  courriel=administrateur[3],
                                  suspension=administrateur[4],
                                  mot_de_passe_hash=None,
                                  mot_de_passe_salt=None)
        return None

    def get_administrateur_by_mail(self, courriel):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM administrateur WHERE courriel = ?",
                       (courriel,))
        administrateur = cursor.fetchone()
        if administrateur:
            return Administrateur(
                id=administrateur[0],
                nom=administrateur[1],
                prenom=administrateur[2],
                courriel=administrateur[3],
                mot_de_passe_hash=administrateur[4],
                mot_de_passe_salt=administrateur[5]
            )
        return None

    def suspendre_administrateur(self, administrateur):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE administrateur set suspension = ? WHERE id = ?",
                       (administrateur.suspension, administrateur.id)
                       )
        connection.commit()

    def set_reset_token(self, user_id, token, expiration):
        connection = self.get_connection()
        connection.execute(
            "UPDATE administrateur SET reset_token = ?, "
            "reset_token_expiration = ? WHERE id = ?",
            (token, expiration, user_id)
        )
        connection.commit()

    def get_administrateur_by_token(self, token):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT id, nom, prenom, courriel, reset_token, "
                       "reset_token_expiration FROM administrateur "
                       "WHERE reset_token = ?",
                       (token,))
        row = cursor.fetchone()
        if row:
            return Administrateur(
                id=row[0],
                nom=row[1],
                prenom=row[2],
                courriel=row[3],
                mot_de_passe_hash=None,
                mot_de_passe_salt=None,
                reset_token=row[4],
                reset_token_expiration=row[5]
            )
        return None

    def update_motdepasse(self, user_id, hashed_password, salt):
        connection = self.get_connection()
        connection.execute(
            "UPDATE administrateur SET mot_de_passe_hash = ?, "
            "mot_de_passe_salt = ? WHERE id = ?",
            (hashed_password, salt, user_id)
        )
        connection.commit()

    def invalidate_reset_token(self, user_id):
        connection = self.get_connection()
        connection.execute(
            "UPDATE administrateur SET reset_token = NULL, "
            "reset_token_expiration = NULL WHERE id = ?",
            (user_id,)
        )
        connection.commit()

    # --------------------Candidats et bénévoles----------------------

    def create_candidat(self, candidat):
        connection = self.get_connection()
        connection.execute(
            "INSERT INTO candidat (nom, prenom, "
            "courriel, benevole, adresse, telephone) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (candidat.nom, candidat.prenom,
             candidat.courriel, candidat.benevole,
             candidat.adresse, candidat.telephone)
        )
        connection.commit()

    def update_candidat(self, candidat_id):
        connection = self.get_connection()
        connection.execute(
            "UPDATE candidat set benevole = 1 WHERE id = ? ",
            (candidat_id,)
        )
        connection.commit()

    def get_candidats(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM candidat "
                       "WHERE benevole = 0")
        candidats = cursor.fetchall()
        liste_candidats = [Candidat(id=row[0], nom=row[1],
                                    prenom=row[2], courriel=row[3],
                                    benevole=row[4], adresse=row[5],
                                    telephone=row[6])
                           for row in candidats]
        return liste_candidats

    def get_benevoles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM candidat "
                       "WHERE benevole = 1")
        benevoles = cursor.fetchall()
        liste_benevoles = [Candidat(id=row[0], nom=row[1], prenom=row[2],
                                    courriel=row[3], benevole=row[4],
                                    adresse=row[5], telephone=row[6])
                           for row in benevoles]
        return liste_benevoles

    def delete_candidat(self, candidat_id):
        connection = self.get_connection()
        connection.execute("DELETE FROM candidat WHERE id = ?",
                           (candidat_id,))
        connection.commit()
        return True

    def get_candidat_by_id(self, candidat_id):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM candidat "
                       "WHERE id = ?",
                       (candidat_id,))
        candidat = cursor.fetchone()
        if candidat is None:
            return None
        else:
            return (Candidat(candidat[0], candidat[1],
                             candidat[2], candidat[3],
                             candidat[4], candidat[5],
                             candidat[6]))

    def update_allinfo_candidat(self, candidat):
        connection = self.get_connection()
        connection.execute(
            "UPDATE candidat SET nom = ?, prenom = ?, "
            "courriel = ?, adresse = ?, telephone = ? WHERE id = ?",
            (candidat.nom, candidat.prenom,
             candidat.courriel, candidat.adresse,
             candidat.telephone, candidat.id)
        )
        connection.commit()

    def rechercher_benevoles(self, nom, prenom):
        connection = self.get_connection()
        cursor = connection.cursor()

        if nom and prenom:
            cursor.execute("SELECT * FROM candidat "
                           "WHERE nom LIKE ? AND prenom LIKE ?",
                           (f"%{nom}%", f"%{prenom}%"))
        elif nom:
            cursor.execute("SELECT * FROM candidat "
                           "WHERE nom LIKE ?",
                           (f"%{nom}%",))
        elif prenom:
            cursor.execute("SELECT * FROM candidat "
                           "WHERE prenom LIKE ? ",
                           (f"%{prenom}%",))
        else:
            cursor.execute("SELECT * FROM candidat")

        resultats = cursor.fetchall()
        return [Candidat(*row) for row in resultats]
