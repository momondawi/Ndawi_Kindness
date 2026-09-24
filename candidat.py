class Candidat:
    def __init__(self, id, nom, prenom, courriel, benevole,
                 adresse, telephone):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.courriel = courriel
        self.benevole = benevole
        self.adresse = adresse
        self.telephone = telephone

    def get_all_benevoles(self):
        return {
            'nom': self.nom,
            'prenom': self.prenom,
            'courriel': self.courriel,
            'adresse': self.adresse,
            'telephone': self.telephone
        }

    def all_info(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'courriel': self.courriel,
            'benevole': self.benevole,
            'adresse': self.adresse,
            'telephone': self.telephone
        }


insert_schema = {
    'type': 'object',
    'required': ['nom', 'prenom', 'courriel', 'benevole',
                 'adresse', 'telephone'],
    'properties': {
        'nom': {
            'type': 'string',
            'maxLength': 25
        },
        'prenom': {
            'type': 'string',
            'maxLength': 25
        },
        'courriel': {
            'type': 'string',
            'format': 'email'
        },
        'adresse': {
            'type': 'string',
        },
        'telephone': {
            'type': 'string',
        },
        'benevole': {
            'type': 'number',
            'enum': [0, 1]
        }
    },
    'additionalProperties': False
}
