# -*- coding: utf-8 -*-

from . import maintenance
from . import lease
from . import tenant
from . import change_state_wizard  
from . import rent_roll_wizard  
from . import mentinance_roll_wizard  



# Keep the booking wizard import guarded to avoid partial-module circular
# import errors during Odoo module bootstrap.
try:
    from . import booking
except ImportError:
    pass