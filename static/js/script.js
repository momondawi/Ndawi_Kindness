// CRUD CANDIDATS
// ------------------------ Creer candidats --------------------
document.querySelector('#candidat-form form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        nom: document.querySelector('#nomcandidat').value.trim(),
        prenom: document.querySelector('#prenomcandidat').value.trim(),
        courriel: document.querySelector('#emailcandidat').value.trim(),
        benevole: 0,
        adresse: document.querySelector('#adressecandidat').value.trim(),
        telephone: document.querySelector('#telephonecandidat').value.trim()
    };

    try {
        const response = await fetch(this.action, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            window.location.href = "/success";
        } else {
            const errorMessage = "Le nom, le prénom et le courriel ne doivent pas dépasser 25 caractères.";
            document.querySelector('#message-erreur').textContent = errorMessage;
            document.querySelector('#message-erreur').style.display = 'block';
        }
    } catch (err) {
        console.error("Erreur lors de l'envoi : ", err);
        document.querySelector('#message-erreur').textContent = "Impossible de contacter le serveur.";
        document.querySelector('#message-erreur').style.display = 'block';
    }
});

//--------------------- Liste des candidats------------------------
//Se trouve dans script2.js