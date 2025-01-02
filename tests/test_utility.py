from datetime import date

import pytest
from albdif.utils.utility import date_range, calcola_prezzo_totale

def test_date_range():
    start_date = '2023-01-01'
    end_date = '2023-01-05'
    expected_dates = ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
    
    assert date_range(start_date, end_date) == expected_dates

def test_calcola_prezzo_totale():
    data_inizio = date(2023, 1, 1)
    data_fine = date(2023, 1, 5)
    catalogo_prezzi = [
        {'data_inizio': date(2023, 1, 1),
         'data_fine': date(2023, 1, 31),
         'prezzo_default': 100.00}
    ]

    prezzo_totale = calcola_prezzo_totale(data_inizio, data_fine, catalogo_prezzi)
    
    assert prezzo_totale == 400.00
