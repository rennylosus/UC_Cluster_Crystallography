from cap_auto.cap_control import CAPInstance
from pathlib import Path

par_file = Path(r"path/to/data/RA3-13do/pre_RA3-13do.par")


cap = CAPInstance(par_file=par_file, start_now=True, raise_on_error=False, min_cap_version='44.100', max_cap_version='44.200')