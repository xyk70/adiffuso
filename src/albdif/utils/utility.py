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