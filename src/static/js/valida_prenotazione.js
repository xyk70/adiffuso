function validateAndCalculate() {
    const dataInizio = new Date(document.getElementById('id_data_inizio').value);
    const dataFine = new Date(document.getElementById('id_data_fine').value);
    const errorMessage = document.getElementById('errorMessage');
    const confirmButton = document.getElementById('confirmButton');
    const today = new Date();

    if (dataInizio <= today) {
        errorMessage.textContent = 'La data di inizio deve essere futura';
        confirmButton.disabled = true;
    } else if (dataFine <= dataInizio) {
        errorMessage.textContent = 'La data di fine deve essere successiva alla data di inizio';
        confirmButton.disabled = true;
    } else {
        errorMessage.textContent = '';
        calcolaPrezzo();
        if (document.getElementById('id_costo_soggiorno').value === 0) {
            confirmButton.disabled = true;
        } else {
            confirmButton.disabled = false;
        }
    }
    $('#confirmModal').modal('show');
}
