import cdl_desc
from cdl_desc import CdlModule, CdlSimVerilatedModule, CModel, CSrc

class Library(cdl_desc.Library):
    name="clocking"
    pass

class ClockingModules(cdl_desc.Modules):
    name = "clocking"
    src_dir      = "cdl"
    tb_src_dir   = "tb_cdl"
    libraries = {"std":True}
    cdl_include_dirs = ["cdl"]
    export_dirs = cdl_include_dirs + [ src_dir ]
    modules = []
    modules += [ CdlModule("clocking_eye_tracking") ]
    modules += [ CdlModule("clocking_phase_measure") ]
    pass

class TimerModules(cdl_desc.Modules):
    name = "clock_timer"
    src_dir      = "cdl"
    tb_src_dir   = "tb_cdl"
    libraries = {"std":True}
    cdl_include_dirs = ["cdl"]
    export_dirs = cdl_include_dirs + [ src_dir ]
    modules = []
    modules += [ CdlModule("clock_timer") ]
    modules += [ CdlModule("clock_timer_async") ]
    modules += [ CdlModule("clock_timer_as_sec_nsec") ]
    pass

