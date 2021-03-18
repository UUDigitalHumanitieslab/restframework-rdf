from .utils import invalid_xml_remove

INVALID_STR = '''La trilogie a en eet
comptabilisé plus de 26 millions de vente.'''
VALID_STR = '''La trilogie a en e et
comptabilisé plus de 26 millions de vente.'''


def test_xml_sanitize():
    assert VALID_STR == invalid_xml_remove(VALID_STR)
    assert INVALID_STR[18] == chr(0x1b) == '\x1b'
    sanitized_str = invalid_xml_remove(INVALID_STR)
    assert sanitized_str[18] == chr(0x20) == ' '
