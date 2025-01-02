from datetime import datetime, timedelta


def date_range(start_date, end_date):
    """
    Genera un elenco di date compreso tra data_inizio e data_fine, inclusi gli estremi.

    :param start_date: Data di inizio in formato 'yyyy-mm-dd'
    :param end_date: Data di fine in formato 'yyyy-mm-dd'
    :return: Elenco delle date comprese nel periodo specificato
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    date_list = []
    current_date = start

    while current_date <= end:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_list

def calcola_prezzo_totale(data_inizio, data_fine, catalogo_prezzi):
    """
    Calcola il prezzo totale del soggiorno in base alle date di inizio e fine e al catalogo prezzi.

    :param data_inizio: Data di inizio in formato 'yyyy-mm-dd'
    :param data_fine: Data di fine in formato 'yyyy-mm-dd'
    :param catalogo_prezzi: Catalogo prezzi: json con chiavi 'data_inizio', 'data_fine' e 'prezzo_giornaliero'
    :return prezzo_totale: Prezzo totale del soggiorno
    """
    prezzo_totale = 0

    for p in catalogo_prezzi:
        if data_inizio >= p['data_inizio'] and data_fine <= p['data_fine']:
            prezzo_totale += (data_fine - data_inizio).days * p['prezzo_default']

    return prezzo_totale
