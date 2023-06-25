from .infrastructure import *
from .student import *
from .programme_requirements import *
from .prerequisites import *
from .timetabling import *

import os
import pandas as pd
module_catalogue_location = os.path.join(os.path.dirname(__file__),'..','module_catalogue','Module_catalogue.xlsx') 
module_catalogue = pd.read_excel(module_catalogue_location)