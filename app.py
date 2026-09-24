from flask import (Flask, render_template, request,
                   g, redirect, url_for, session, jsonify, send_from_directory)
from database import Administrateur, Database
from flask_mail import Mail, Message
from datetime import timedelta, datetime
from functools import wraps
from flask_json_schema import JsonValidationError, JsonSchema
from candidat import Candidat, insert_schema
import re
import secrets
import hashlib
import uuid

app = Flask(__name__)
schema = JsonSchema(app)

app.config.update(
    SECRET_KEY=secrets.token_hex(16),
    SESSION_COOKIE_NAME='Session_de_mon_site',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
)

email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{1,25}$'
regex_mdp = (r"^(?=.*[A-Z])(?=.*[0-9])(?=.*[#\$%&'*+/=?@])[A-Za-z0-9#"
             r"$%&'*+/=?@]{8,}$")
regex_longueur = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]{1,25}$"


app.config.from_object('config')
mail = Mail(app)


mdp_correct = re.compile(regex_mdp).match


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html"), 200


@app.route("/a-propos")
def apropos():
    return render_template("a-propos.html"), 200


@app.route("/services")
def services():
    return render_template("services.html"), 200


@app.route("/missions")
def missions():
    return render_template("missions.html"), 200


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template("contact.html"), 200

    if request.method == 'POST':
        raison = request.form.get('raison')
        mail = request.form['email']
        message = request.form['message']

        erreur = "Remplissez tous les champs, l'email doit être correct."
        succes = "Ton message a été envoyé."

        if not mail or not message or not re.match(email_regex, mail):
            return render_template("contact.html",
                                   erreur=erreur,
                                   email=mail,
                                   message=message), 400

        else:
            return render_template("contact.html",
                                   succes=succes), 302


# -------------------------------- Projet 2 ----------------------------------


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        users = dict(session).get('id', None)
        if users:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('administration'))
    return decorated_function


def get_db():
    database = getattr(g, '_database', None)
    if database is None:
        g._database = Database()
    return g._database


def deconnection():
    database = getattr(g, "_database", None)
    if database is not None:
        database.deconnection()


def courriel_existe(courriel):
    return get_db().courriel_existe(courriel)


def valider_mdp(str):
    try:
        if mdp_correct(str) is not None:
            return True
    except Exception:
        pass
    return False


def verifier_authentification(courriel, mot_de_passe):
    utilisateur = get_db().login(courriel)
    if utilisateur:

        try:
            salt = utilisateur[3]
            hashed_password = utilisateur[4]
        except Exception:
            print("Erreur : la structure du tuple utilisateur est incorrecte.")
            return False

        hashed_input_password = hashlib.sha512(
            (mot_de_passe + salt).encode('utf-8')).hexdigest()

        if hashed_password == hashed_input_password:
            return utilisateur
    return False


def valider_longeur(chaine):
    return bool(re.match(regex_longueur, chaine))


@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for validation_error in e.errors]
    return jsonify({'error': e.message, 'errors': errors}), 400


@app.route("/administration", methods=['GET', 'POST'])
def administration():
    if session.get('id'):
        return redirect(url_for("candidate_system")), 302

    if request.method == 'GET':
        return render_template("administration.html"), 200

    if request.method == 'POST':
        courriel = request.form.get('emailAuth')
        mot_de_passe = request.form.get('motdepasseAuth')

        if not courriel or not mot_de_passe:
            message_erreur = "Tous les champs doivent être remplis."
            return render_template("administration.html",
                                   emailAuth=courriel,
                                   message_erreur=message_erreur), 400

        utilisateur = verifier_authentification(courriel, mot_de_passe)
        if not utilisateur:
            message_erreur = "Courriel ou mot de passe incorrect"
            return render_template("administration.html",
                                   emailAuth=courriel,
                                   message_erreur=message_erreur), 400

        if utilisateur[5] == 1:
            message_erreur = "Votre compte est momentanément suspendu."
            return render_template("administration.html",
                                   emailAuth=courriel,
                                   message_erreur=message_erreur), 400

        session['id'] = utilisateur[0]
        session['prenom'] = utilisateur[1]
        session['nom'] = utilisateur[2]
        session['courriel'] = utilisateur[3]
        session.permanent = True

        return redirect(url_for("candidate_system")), 301


@app.route("/success")
def success():
    return render_template("success.html"), 200


@app.route("/admin_system")
@login_required
def admin_system():
    liste_administrateurs = get_db().get_administrateurs()
    return render_template("admin-system.html",
                           administrateurs=liste_administrateurs), 200


@app.route("/accepter_candidat/<int:candidat_id>")
@login_required
def accepter_candidat(candidat_id):
    get_db().update_candidat(candidat_id)
    return redirect(url_for('candidate_system')), 301


@app.route("/supprimer_administrateur/<int:administrateur_id>")
@login_required
def supprimer_administrateur(administrateur_id):
    get_db().delete_administrateur(administrateur_id)
    return redirect(url_for('admin_system')), 301


@app.route("/ajouter_administrateur", methods=['GET', 'POST'])
@login_required
def ajouter_administrateur():
    if request.method == 'GET':
        return render_template("create-admin.html"), 200

    else:
        nom = request.form['nomadmin']
        prenom = request.form['prenomadmin']
        courriel = request.form['emailadmin']
        password = request.form['motdepasseadmin']
        passwordconfirmed = request.form['motdepasseconfirmer']

        if (not nom or not prenom or not courriel or not password
                or not passwordconfirmed
                or not valider_longeur(nom) or not valider_longeur(prenom)
                or not re.match(email_regex, courriel)
                or not re.match(regex_mdp, password)):
            message_erreur = ("Tous les champs doivent être correctement "
                              "remplis.")
            return render_template("create-admin.html",
                                   nomadmin=nom,
                                   prenomadmin=prenom,
                                   emailadmin=courriel,
                                   message_erreur=message_erreur), 400

        if password != passwordconfirmed:
            message_erreur = "Les mots de passe ne correspondent pas."
            return render_template("create-admin.html",
                                   nomadmin=nom,
                                   prenomadmin=prenom,
                                   emailadmin=courriel,
                                   message_erreur=message_erreur), 400

        if courriel_existe(courriel):
            message_erreur = ("Ce courriel existe déjà dans la liste "
                              "des administrateurs.")
            return render_template("create-admin.html",
                                   nomadmin=nom,
                                   prenomadmin=prenom,
                                   emailadmin=courriel,
                                   message_erreur=message_erreur), 400

        mot_de_passe_salt = uuid.uuid4().hex
        mot_de_passe_hash = hashlib.sha512(str(password + mot_de_passe_salt
                                               ).encode("utf-8")).hexdigest()
        admincree = Administrateur(nom, prenom, courriel,
                                   mot_de_passe_hash, mot_de_passe_salt,
                                   suspension=0)
        get_db().create_administrateur(admincree)

        msg = Message("Confirmation de création de votre "
                      "compte administrateur",
                      recipients=[courriel])
        msg.body = (f"Bonjour {prenom},\n\nVotre compte administrateur a "
                    f"été créé avec succès. Pour une première connexion, "
                    f"veuillez appuyer sur mot de passe oublié et suivre le "
                    f"processus. \n\nVoici votre courriel {courriel} à "
                    f"renseigner.")
        mail.send(msg)
        return redirect(url_for('admin_success')), 301


@app.route("/admin_success")
@login_required
def admin_success():
    return render_template("admin-success.html"), 200


@app.route("/modifier_administrateur/<int:administrateur_id>",
           methods=['GET', 'POST'])
@login_required
def modifier_administrateur(administrateur_id):
    if request.method == 'GET':
        admin = get_db().get_administrateur_by_id(administrateur_id)
        if admin is None:
            return "Administrateur introuvable", 404
        return render_template("modifier-admin.html",
                               administrateur=admin), 200

    else:
        nom = request.form.get('nomadmin')
        prenom = request.form.get('prenomadmin')
        courriel = request.form.get('emailadmin')
        password = request.form.get('motdepasseadmin')
        passwordconfirmed = request.form.get('motdepasseconfirmer')

        if not (nom and prenom and courriel and password and
                passwordconfirmed):
            message_erreur = ("Tous les champs doivent être remplis "
                              "correctement.")
            admin_temp = Administrateur(id=administrateur_id, nom=nom,
                                        prenom=prenom, courriel=courriel,
                                        mot_de_passe_hash=None,
                                        mot_de_passe_salt=None)
            return render_template("modifier-admin.html",
                                   administrateur=admin_temp,
                                   message_erreur=message_erreur), 400

        existing_user = get_db().get_administrateur_by_mail(courriel)
        if existing_user and existing_user.id != administrateur_id:
            message_erreur = ("Ce courriel est déjà utilisé par un autre "
                              "administrateur.")
            admin_temp = Administrateur(id=administrateur_id, nom=nom,
                                        prenom=prenom, courriel=courriel,
                                        mot_de_passe_hash=None,
                                        mot_de_passe_salt=None)
            return render_template("modifier-admin.html",
                                   administrateur=admin_temp,
                                   message_erreur=message_erreur), 400

        if password != passwordconfirmed:
            message_erreur = "Les mots de passe ne correspondent pas."
            admin_temp = Administrateur(id=administrateur_id, nom=nom,
                                        prenom=prenom, courriel=courriel,
                                        mot_de_passe_hash=None,
                                        mot_de_passe_salt=None)
            return render_template("modifier-admin.html",
                                   administrateur=admin_temp,
                                   message_erreur=message_erreur), 400

        mot_de_passe_salt = uuid.uuid4().hex
        mot_de_passe_hash = hashlib.sha512((password + mot_de_passe_salt
                                            ).encode('utf-8')).hexdigest()
        adminmodifier = Administrateur(nom=nom, prenom=prenom,
                                       courriel=courriel,
                                       mot_de_passe_hash=mot_de_passe_hash,
                                       mot_de_passe_salt=mot_de_passe_salt,
                                       id=administrateur_id)

        get_db().update_administrateur(adminmodifier)

        msg = Message("Modification de votre compte administrateur",
                      recipients=[courriel])
        msg.body = (f"Bonjour {prenom},\n\nVotre compte administrateur a "
                    f"été mis à jour avec succès. Si vous n'arrivez pas "
                    f"à vous authentifier, veuillez faire mot de passe "
                    f"oublié et "
                    f"suivre le processus. \n\n Voici votre "
                    f"courriel {courriel}")
        mail.send(msg)

        return redirect(url_for('admin_success')), 301


@app.route("/suspendre_administrateur/<int:administrateur_id>")
@login_required
def suspendre_administrateur(administrateur_id):
    utilisateur = get_db().get_administrateur_by_id(administrateur_id)
    utilisateur.suspension = 1
    get_db().suspendre_administrateur(utilisateur)
    return redirect(url_for("admin_system")), 301


@app.route("/annuler_suspension/<int:administrateur_id>")
@login_required
def annuler_suspension(administrateur_id):
    utilisateur = get_db().get_administrateur_by_id(administrateur_id)
    utilisateur.suspension = 0
    get_db().suspendre_administrateur(utilisateur)
    return redirect(url_for("admin_system")), 301


@app.route("/forget_password", methods=['GET', 'POST'])
def forget_password():
    if request.method == 'GET':
        return render_template("mot-de-passe-oublie.html"), 200

    else:
        courriel = request.form.get('emailforget')
        if courriel_existe(courriel):
            user = get_db().get_administrateur_by_mail(courriel)
            reset_token = uuid.uuid4().hex
            expiration = datetime.now() + timedelta(hours=1)

            get_db().set_reset_token(user.id, reset_token, expiration)
            reset_url = url_for('reinitialisermotdepasse',
                                token=reset_token,
                                _external=True)
            msg = Message("Réinitialisation de votre mot de passe",
                          recipients=[courriel])
            msg.body = (f"Bonjour {user.prenom},\n\nCliquez sur ce lien "
                        f"pour réinitialiser "
                        f"votre mot de passe : {reset_url}\nCe lien est "
                        f"valable pendant une heure.")
            mail.send(msg)

            return redirect(url_for('admin_success')), 301

        else:
            message_erreur = "Le courriel n'est pas trouvé."
            return render_template("mot-de-passe-oublie.html",
                                   message_erreur=message_erreur), 400


@app.route("/reinitialisermotdepasse/<token>", methods=['GET', 'POST'])
def reinitialisermotdepasse(token):
    if request.method == 'GET':
        utilisateur = get_db().get_administrateur_by_token(token)

        if not utilisateur or utilisateur.reset_token_expiration is None:
            message_erreur = "L'utilisateur n'est pas trouvé"
            return render_template("administrateur.html",
                                   message_erreur=message_erreur), 400

        expiration_datetime = datetime.strptime(
            utilisateur.reset_token_expiration, "%Y-%m-%d %H:%M:%S.%f")
        if expiration_datetime < datetime.now():
            return redirect(url_for('token_invalide')), 301

        return render_template("reinitialisermotdepasse.html",
                               utilisateur=utilisateur), 200

    if request.method == 'POST':
        utilisateur = get_db().get_administrateur_by_token(token)
        if not utilisateur:
            return redirect(url_for('token_invalide')), 400

        new_password = request.form['motdepasseoublie']
        new_password_confirm = request.form['motdepasseconfirmed']

        if new_password != new_password_confirm:
            message_erreur = "Les mots de passe ne correspondent pas."
            return render_template("reinitialisermotdepasse.html",
                                   message_erreur=message_erreur), 400
        elif not re.match(regex_mdp, new_password):
            message_erreur = "Le mot de passe ne respecte pas les critères."
            return render_template("reinitialisermotdepasse.html",
                                   message_erreur=message_erreur), 400
        else:
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(
                (new_password + salt).encode('utf-8')).hexdigest()

            get_db().update_motdepasse(utilisateur.id, hashed_password, salt)
            get_db().invalidate_reset_token(utilisateur.id)

            return redirect(url_for('motdepasse_succes'))


@app.route("/token_invalide")
def token_invalide():
    return render_template("token-invalide.html"), 200


@app.route("/motdepasse_succes")
def motdepasse_succes():
    return render_template("motdepasse-success.html"), 200


@app.route("/deconnexion")
def deconnexion():
    deconnection()
    session.pop('id', None)
    session.pop('nom', None)
    session.pop('prenom', None)
    session.pop('courriel', None)
    return redirect(url_for("home")), 302


# -----------------------------Projet 3------------------------------


@app.route("/candidat", methods=['GET'])
def afficher_formulaire_candidat():
    return render_template("candidat.html"), 200


@app.route("/api/candidat", methods=['POST'])
@schema.validate(insert_schema)
def candidat():
    data = request.get_json()
    candidatcree = Candidat(
        None,
        data['nom'],
        data['prenom'],
        data['courriel'],
        data['benevole'],
        data['adresse'],
        data['telephone']
    )
    get_db().create_candidat(candidatcree)
    return jsonify({"message": "Candidat créé avec succès!"}), 201


@app.route("/candidats", methods=['GET'])
@login_required
def candidate_system():
    return render_template("candidate-system.html"), 200


@app.route("/api/candidats", methods=['GET'])
@login_required
def api_get_candidats():
    liste_candidats = get_db().get_candidats()
    return jsonify([candidat.all_info() for candidat in liste_candidats]), 200


@app.route("/list_benevole")
@login_required
def list_benevole():
    return render_template("list-benevole.html"), 200


@app.route("/api/benevoles", methods=['GET'])
@login_required
def api_get_benevoles():
    liste_benevoles = get_db().get_benevoles()
    return jsonify([benevole.get_all_benevoles()
                    for benevole in liste_benevoles]), 200


@app.route("/api/candidat/<int:id>", methods=['DELETE'])
@login_required
def delete_candidat(id):
    try:
        candidat = get_db().get_candidat_by_id(id)
        if candidat is None:
            return jsonify({"error": "Candidat introuvable"}), 404
        get_db().delete_candidat(id)
        return jsonify({"message": "Candidat supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/candidat/<int:id>", methods=['GET'])
@login_required
def get_one_candidat(id):
    candidat = get_db().get_candidat_by_id(id)
    if not candidat:
        return "Candidat introuvable", 404
    return render_template("modifier-candidat.html",
                           candidat=candidat), 200


@app.route("/api/candidat/<int:id>", methods=['GET'])
@login_required
def api_get_candidat(id):
    candidat = get_db().get_candidat_by_id(id)
    return jsonify(candidat.all_info()), 200


@app.route("/api/candidat/<int:id>", methods=['PUT'])
@login_required
def update_candidat(id):
    data = request.get_json()
    candidat = Candidat(id,
                        data['nom'],
                        data['prenom'],
                        data['courriel'],
                        data['benevole'],
                        data['adresse'],
                        data['telephone']
                        )
    get_db().update_allinfo_candidat(candidat)
    return jsonify({"message": "Candidat modifié avec succès!"}), 201


@app.route("/rechercher_candidats", methods=['GET'])
@login_required
def rechercher_candidats():
    return render_template("recherche.html"), 200


@app.route("/api/recherche", methods=['GET'])
@login_required
def rechercher_benevoles():
    nom = request.args.get('nom', '').strip()
    prenom = request.args.get('prenom', '').strip()
    resultats = get_db().rechercher_benevoles(nom, prenom)
    resultats_json = [benevole.all_info() for benevole in resultats]
    return jsonify(resultats_json), 200


@app.route("/api/doc", methods=["GET"])
def documentation():
    return send_from_directory("static/docs", "api.raml"), 200


if __name__ == '__main__':
    app.run()
