from .server_adapters.I_am_teapot_adapter import IAmTeaPotAdapter
from .server_adapters.ctrl_alt_defeat_adapter import CtrlAltDefeatAdapter
from .server_adapters.restless_clients_adapter import RestLessClientsAdapter

iAmTeaPotAdapter = IAmTeaPotAdapter()
ctrlAltDefeatAdapter = CtrlAltDefeatAdapter()
restLesClientsAdapter = RestLessClientsAdapter()

API_LOOKUP = {
  iAmTeaPotAdapter.host: iAmTeaPotAdapter,
  ctrlAltDefeatAdapter.host: ctrlAltDefeatAdapter,
  # restLesClientsAdapter.host: restLesClientsAdapter
}

