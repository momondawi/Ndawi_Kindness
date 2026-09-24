//--------------------- la partie create se trouve dans script.js -----------------
//--------------------- Liste des candidats ------------------------
document.addEventListener("DOMContentLoaded", async () => {
    const tableBody = document.querySelector("#candidatlist tbody");
    try {
        const response = await fetch("/api/candidats");
        if (!response.ok) throw new Error("Erreur lors de la récupération des candidats.");

        const candidats = await response.json();

        candidats.forEach((candidat, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <th scope="row">${index + 1}</th>
                <td>${candidat.nom}</td>
                <td>${candidat.prenom}</td>
                <td>${candidat.courriel}</td>
                <td>${candidat.adresse}</td>
                <td>${candidat.telephone}</td>
                <td>
                    <a href="/accepter_candidat/${candidat.id}" class="btn btn-success btn-sm">Accepter</a>
                    <a href="/candidat/${candidat.id}" class="btn btn-warning btn-sm">Modifier</a>
                    <a href="#" data-id="${candidat.id}" class="btn btn-danger btn-sm delete-candidat">Supprimer</a>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error(error);
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="7" class="text-center text-danger">Erreur lors du chargement des candidats.</td>`;
        tableBody.appendChild(row);
    }
});


//-------------------------- liste des benevoles -----------------------------
document.addEventListener("DOMContentLoaded", async () => {
    const tableBody2 = document.querySelector("#benevole tbody");
    try {
        const response2 = await fetch("/api/benevoles");
        if (!response2.ok) throw new Error("Erreur lors de la récupération des bénévoles.");

        const benevoles = await response2.json();

        benevoles.forEach((benevole, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <th scope="row">${index + 1}</th>
                <td>${benevole.nom}</td>
                <td>${benevole.prenom}</td>
                <td>${benevole.courriel}</td>
                <td>${benevole.adresse}</td>
                <td>${benevole.telephone}</td>
            `;
            tableBody2.appendChild(row);
        });
    } catch (error) {
        console.error(error);
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="7" class="text-center text-danger">Erreur lors du chargement des bénévoles.</td>`;
        tableBody2.appendChild(row);
    }
});

//----------------------- Supprimer un candidat ------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.querySelector("#candidatlist tbody");
    tableBody.addEventListener("click", async (e) => {
        if (e.target.classList.contains("delete-candidat")) {
            e.preventDefault();

            const candidatId = e.target.getAttribute("data-id");

            if (confirm("Voulez-vous vraiment supprimer ce candidat ?")) {
                try {
                    const response = await fetch(`/api/candidat/${candidatId}`, { method: "DELETE" });

                    if (!response.ok) {
                        const errorData = await response.json();
                        console.error("Erreur : ", errorData.error);
                        alert(`Erreur : ${errorData.error}`);
                    } else {
                        alert("Candidat supprimé avec succès !");
                        e.target.closest("tr").remove();
                    }
                } catch (error) {
                    console.error("Erreur réseau :", error);
                    alert("Erreur réseau. Impossible de supprimer le candidat.");
                }
            }
        }
    });
});

//-------------------------- Modifier un candidat -----------------------------
document.addEventListener("DOMContentLoaded", () => {
    const formElement = document.getElementById("updatecandidat-form");
    const candidatId = formElement.getAttribute("data-id");

    document.getElementById("btn-update").addEventListener("click", async () => {
        const data = {
            nom: document.getElementById("nomcandidat").value,
            prenom: document.getElementById("prenomcandidat").value,
            courriel: document.getElementById("emailcandidat").value,
            adresse: document.getElementById("adressecandidat").value,
            telephone: document.getElementById("telephonecandidat").value,
            benevole: 0
        };

        try {
            const response = await fetch(`/api/candidat/${candidatId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                alert("Candidat modifié avec succès !");
                window.location.href = "/candidats";
            } else {
                const error = await response.json();
                alert(`Erreur : ${error.message}`);
            }
        } catch (error) {
            console.error("Erreur réseau :", error);
            alert("Une erreur réseau s'est produite.");
        }
    });
});

//---------------------Recherche-------------------------
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-recherche");
    const listeResultats = document.getElementById("liste-resultats");
    const btnPrev = document.getElementById("btn-prev");
    const btnNext = document.getElementById("btn-next");

    let currentPage = 1;
    let totalPages = 1;
    const resultsPerPage = 5;

    // Fonction pour effectuer une recherche
    const rechercher = async () => {
        const nom = document.getElementById("nom").value.trim();
        const prenom = document.getElementById("prenom").value.trim();

        try {
            const response = await fetch(`/api/recherche?nom=${nom}&prenom=${prenom}`);
            const resultats = await response.json();

            afficherResultats(resultats);
        } catch (error) {
            console.error("Erreur lors de la recherche :", error);
        }
    };

    // Fonction pour afficher les résultats avec pagination
    const afficherResultats = (resultats) => {
        listeResultats.innerHTML = "";

        // Calculer le nombre total de pages
        totalPages = Math.ceil(resultats.length / resultsPerPage);

        // Afficher les résultats de la page courante
        const startIndex = (currentPage - 1) * resultsPerPage;
        const endIndex = startIndex + resultsPerPage;
        const resultatsPage = resultats.slice(startIndex, endIndex);

        resultatsPage.forEach((benevole) => {
            const item = document.createElement("li");
            item.className = "list-group-item";
            if (benevole.benevole === 1) {
                item.textContent = `${benevole.nom} ${benevole.prenom} - ${benevole.courriel} - ${benevole.adresse} - ${benevole.telephone} - Candidat`;
            }
            item.textContent = `${benevole.nom} ${benevole.prenom} - ${benevole.courriel} - ${benevole.adresse} - ${benevole.telephone} - Bénévole`;
            listeResultats.appendChild(item);
        });

        // Activer/désactiver les boutons de pagination
        btnPrev.disabled = currentPage === 1;
        btnNext.disabled = currentPage === totalPages || totalPages === 0;
    };

    // Écouter le clic sur le bouton "Rechercher"
    document.getElementById("btn-rechercher").addEventListener("click", () => {
        currentPage = 1;
        rechercher();
    });

    // Gérer la pagination
    btnPrev.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            rechercher();
        }
    });

    btnNext.addEventListener("click", () => {
        if (currentPage < totalPages) {
            currentPage++;
            rechercher();
        }
    });
});
