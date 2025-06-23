// Logic for the listing patients page (mainpage.html)
var modal = document.getElementById("filterModal");
var btn = document.getElementById("openFilterModal");
var span = document.getElementsByClassName("close")[0];

btn.onclick = function() {
    modal.style.display = "block";
}

span.onclick = function() {
    modal.style.display = "none";
}

function closeModal() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

function resetFilters() {
  document.getElementById('filterSex').value = ""; // Remet le sexe à 'Any Sex'
  document.getElementById('minAge').value = "";   // Efface le champ âge minimum
  document.getElementById('maxAge').value = "";   // Efface le champ âge maximum

  filterPatients(); // Applique les filtres réinitialisés pour mettre à jour l'affichage
  closeModal();     // Ferme le modal après la réinitialisation
}


function filterPatients() {
  var input = document.getElementById("searchInput").value.toUpperCase();
  var filterSex = document.getElementById("filterSex").value;
  var minAge = parseInt(document.getElementById("minAge").value, 10);
  var maxAge = parseInt(document.getElementById("maxAge").value, 10);

  var table = document.getElementById("patientsTable");
  var tr = table.getElementsByTagName("tr");

  for (var i = 1; i < tr.length; i++) {
      var td = tr[i].getElementsByTagName("td");
      var txtName = td[0].textContent || td[0].innerText;
      var age = parseInt(td[1].textContent || td[1].innerText, 10);
      var sex = td[2].textContent || td[2].innerText.toLowerCase();

      if (
          (txtName.toUpperCase().indexOf(input) > -1 || input === "") &&
          (filterSex === "" || sex === filterSex) &&
          (isNaN(minAge) || age >= minAge) &&
          (isNaN(maxAge) || age <= maxAge)
      ) {
          tr[i].style.display = "";
      } else {
          tr[i].style.display = "none";
      }
  }
}



function addPatient() {
  var name = document.getElementById('newPatientName').value;  // Récupère le nom du nouveau patient
  if (name.trim() === '') {
      alert('Please enter a name.');
      return;
  }

  var newPatient = {
      id: patients.length + 1,  // Attribue un ID simple basé sur la longueur du tableau
      name: name,
      details: 'Details will be added later'  // Mettez ici des détails par défaut ou supplémentaires
  };

  // Ajoute à la liste des patients
  patients.push(newPatient);

  // Ajoute au tableau HTML
  var table = document.getElementById('patientsTable').getElementsByTagName('tbody')[0];
  var row = table.insertRow();
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  cell1.innerHTML = newPatient.name;
  cell2.innerHTML = '<a href="specificpage.html?patientId=' + newPatient.id + '">See more</a>';

  // Réinitialise le champ de saisie
  document.getElementById('newPatientName').value = '';
}

// End of the code for the listing patients page (mainpage.html)
//-------------------------------------------------------------------------------------------------------------------
//
//-------------------------------------------------------------------------------------------------------------------
