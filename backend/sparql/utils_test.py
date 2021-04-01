from .utils import invalid_xml_remove
import os.path as op

HERE = op.dirname(op.abspath(__file__))

INVALID_STR = '''La trilogie a en eet
comptabilisé plus de 26 millions de vente.'''

VALID_STR = '''La trilogie a en e et
comptabilisé plus de 26 millions de vente.'''

FULL_STR = """Babelio, Missbouquin (id_12_a) --- Et voilà ça y est ! j'ai enfin lu le premier tome de Millenium ! Harcelée
par deux de mes meilleures amies (l'une a fini par me l'offrir), j'ai pris
mon courage à deux mains et me suis attaquée à la série qui a connu
un succès immense depuis sa publication en 2005. La trilogie a en eet
comptabilisé plus de 26 millions de vente.
Pour moi, ce n'était pas gagné d'avance. Je l'ai commencé avec réti-
cence car je n'aime pas le genre du roman policier / roman noir. Je suis
trop sensible et assez impressionnable donc je m'en passe très bien.
On m'a cependant assuré que Millenium allait me plaire, etc etc. Bien.
Alors je le commence le mardi matin dans le RER. Je le lis tranquille,
j'accroche bien. Mardi passe. Mercredi, je rentre plus tôt d'une formation
et comme je le fais parfois, je continue ma lecture en marchant (non non
ne vous inquiétez pas, il ne va rien m'arriver). Incapable de décrocher, je
me laisse 30 minutes le temps de boire un thé, en continuant ma lecture.
Il était 18h. Finalement, je repose le bouquin à 21H30. Terminé.
C'est un véritable page-turner comme on appelle ces romans qui sont à
la limite de l'addiction, tant une page appelle la suivante, tant l'histoire
est prenante. Effectivement, j'ai été impressionnée par l'ampleur de ce
roman assez complexe, mêlant crimes et arnaques financières, avec au
centre un journaliste et une jeune femme sous tutelle et assez...spéciale"""


def test_xml_sanitize():
    assert VALID_STR == invalid_xml_remove(VALID_STR)
    assert INVALID_STR[18] == chr(0x1b) == '\x1b'
    sanitized_str = invalid_xml_remove(INVALID_STR)
    assert sanitized_str[18] == chr(0x20) == ' '
    print(len(FULL_STR), len(invalid_xml_remove(FULL_STR)))
    assert FULL_STR == invalid_xml_remove(FULL_STR)


def test_sanitize_file():
    fp1 = op.join(HERE, 'testfiles', '1.txt')

    with open(fp1, 'r') as f1:
        c1 = f1.read()
        c1_san = invalid_xml_remove(c1)
        assert c1[319] == chr(0x1b) == '\x1b'
        assert c1_san[319] == chr(0x20) == ' '
        assert len(c1) == len(c1_san)
