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
    modules += [ CdlModule("tb_clocking", src_dir=tb_src_dir) ]
    modules += [ CdlModule("tb_clock_timer", src_dir=tb_src_dir) ]
    # Without cwv:  Ran 12 tests in 94.743s :real 1m34.834s: user: 1m17.309s sys 0m49.748s
    # With cwv:     Ran 12 tests in 87.201s :real 1m27.292s: user: 1m7.740s sys 0m51.569s
    # modules += [ CdlSimVerilatedModule("cwv__tb_clock_timer",
    #                                    cdl_filename="tb_clock_timer",
    #                                   src_dir=tb_src_dir,
    #                                   verilog_filename="tb_clock_timer",
    #                                   # extra_verilog=["../std/srw_srams.v", "../std/mrw_srams.v"]
    #                                   ) ]
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

