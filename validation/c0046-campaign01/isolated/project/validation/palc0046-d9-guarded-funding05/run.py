import importlib.util,sys
from pathlib import Path
sys.path.insert(0,'tools')
work=Path(__file__).resolve().parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
funds=module('pal_funding',work/'funding_controller.py');guard=module('pal_funding_guard',work/'approach_guard.py')
guard.beam.generic.base.game=funds
if __name__=='__main__':guard.main()
