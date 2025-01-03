function calcolaPrezzo() {
    let totale = 0;
    const catalogoPrezzi = document.querySelectorAll('#catalogo_prezzi .row[data-inizio]');
    const dataInizio = new Date(document.querySelector('[name="data_inizio"]').value);
    const dataFine = new Date(document.querySelector('[name="data_fine"]').value);

    // Controllo per verificare che la data di fine sia almeno il giorno dopo la data di inizio
    if (dataFine <= dataInizio) {
        document.getElementById('prezzoTotale').textContent = '';
        document.getElementById('id_costo_soggiorno').value = 0;
        return;
    }
    else {
        // Itera su ogni riga del catalogo prezzi
        catalogoPrezzi.forEach(row => {
            const inizio = new Date(row.getAttribute('data-inizio'));
            const fine = new Date(row.getAttribute('data-fine'));
            const prezzo = parseFloat(row.querySelector('.col:nth-child(3)').textContent);

            // Verifica se l'intervallo di date della prenotazione si sovrappone con l'intervallo di date della riga corrente
            if (dataInizio <= fine && dataFine >= inizio) {
                // Determina la data di inizio effettiva per il calcolo del prezzo
                const start = dataInizio > inizio ? dataInizio : inizio;
                // Determina la data di fine effettiva per il calcolo del prezzo
                const end = dataFine < fine ? dataFine : fine;
                // Calcola il numero di giorni di sovrapposizione
                // (end - start) calcola la differenza in millisecondi tra le due date
                // (1000 * 60 * 60 * 24) è il numero di millisecondi in un giorno
                // Dividendo la differenza in millisecondi per il numero di millisecondi in un giorno otteniamo il numero di giorni
                const giorni = (end - start) / (1000 * 60 * 60 * 24);
                // Aggiunge al totale il costo per i giorni di sovrapposizione
                totale += giorni * prezzo;
            }
        });

        // Aggiorna il contenuto dell'elemento con id 'prezzoTotale' con il prezzo totale calcolato
        document.getElementById('prezzoTotale').textContent = `Il totale da pagare per il tuo soggiorno è: €${totale.toFixed(2)}`;
        document.getElementById('id_costo_soggiorno').value = totale;
    }
}