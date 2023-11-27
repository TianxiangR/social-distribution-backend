from .server_adapters.I_am_teapot_adapter import IAmTeaPotAdapter
from .server_adapters.ctrl_alt_defeat_adapter import CtrlAltDefeatAdapter

iAmTeaPotAdapter = IAmTeaPotAdapter()
ctrlAltDefeatAdapter = CtrlAltDefeatAdapter()

API_LOOKUP = {
  iAmTeaPotAdapter.host: iAmTeaPotAdapter,
  ctrlAltDefeatAdapter.host: ctrlAltDefeatAdapter
}

