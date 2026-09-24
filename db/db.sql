CREATE TABLE administrateur(
    id INTEGER PRIMARY KEY,
    nom VARCHAR(25),
    prenom VARCHAR(25),
    courriel VARCHAR(15),
    mot_de_passe_hash TEXT NON NULL,
    mot_de_passe_salt TEXT NON NULL,
    reset_token TEXT,
    reset_token_expiration DATETIME,
    suspension INTEGER,
    suspension_expiration DATETIME
);

CREATE TABLE candidat(
    id INTEGER PRIMARY KEY,
    nom VARCHAR(25),
    prenom VARCHAR(25),
    courriel VARCHAR(15),
    benevole INT,
    adresse TEXT,
    telephone TEXT
);


-- email = firstadmin@gmail.com, password = passer123
INSERT INTO administrateur (nom, prenom, courriel, mot_de_passe_hash, mot_de_passe_salt)  VALUES ("admin", "first", "firstadmin@gmail.com", "37a80fe897666eb0eb94334064cdbbd0000a4aebe3f13f1334f5615205f0202e2762f5488af85f66d14849712222b71677702c1152111c32a5b87c67a067a9dd", "818ab61ec04141748ba230818cbb4c3f");