import cassava

def test_not_providing_conf_persists_defaults_changes_ok():
    """
    Initially the header_row config item in the class variable DEFAULTS is
    None.  If no conf kwarg is passed to the constructor, then it uses
    DEFAULTS (directly, not a copy) as its configuration dict.  In this case,
    if we change a configuration item, then it should persist for subsequent
    instances (for a given import session)
    """

    f = cassava.Cassava()
    assert f.conf['header_row'] is None
    f.conf['header_row'] = 0
    del f
    f = cassava.Cassava()
    assert f.conf['header_row'] == 0

