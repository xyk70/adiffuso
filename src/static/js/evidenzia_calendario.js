document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prenotazioneForm');
    const catalogoPrezzi = document.getElementById('catalogo_prezzi');

    function updateCatalogoPrezzi() {
        const dataInizio = new Date(form.querySelector('[name="data_inizio"]').value);
        const dataFine = new Date(form.querySelector('[name="data_fine"]').value);

        catalogoPrezzi.querySelectorAll('.row').forEach(row => {
            if (row.getAttribute('data-inizio')) {
                const rowInizio = new Date(row.getAttribute('data-inizio'));
                const rowFine = new Date(row.getAttribute('data-fine'));

                if (dataInizio <= rowFine && dataFine >= rowInizio) {
                    row.className = 'row align-items-center bg-warning p-3 border';
                }
                else {
                    row.className = 'row align-items-center bg-light p-3 border';
                }
            }
        });
    }

    form.addEventListener('change', updateCatalogoPrezzi);
    updateCatalogoPrezzi(); // Attiva il js al caricamento della pagina
});
