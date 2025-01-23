def test_imports():
    """Verify that all models can be imported"""
    from vcon_pydantic import (
        VconModel,
        PartyModel,
        DialogModel,
        CivicAddressModel,
        PartyHistoryModel,
    )

    # Import from original package to verify interop
    from vcon.dialog import Dialog
    from vcon.party import Party
    from vcon.party import PartyHistory
    from vcon.civic_address import CivicAddress
    from vcon.vcon import Vcon

    assert VconModel is not None
    assert PartyModel is not None
    assert DialogModel is not None
    assert CivicAddressModel is not None
    assert PartyHistoryModel is not None
    assert Dialog is not None
    assert Party is not None
    assert PartyHistory is not None
    assert CivicAddress is not None
    assert Vcon is not None
