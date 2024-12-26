from albdif.models import Proprieta


def test_proprieta(user, host):
    Proprieta.objects.create(
        host=host,
        descrizione="bla bla",
        principale=True,
    )
    try:
        Proprieta.objects.create(
            host=host,
            descrizione="bla bla",
            principale=True
        )
    except Exception as e:
        assert "Esiste già una proprietà principale." in str(e)

