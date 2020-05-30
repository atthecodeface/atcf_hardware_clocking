#a Copyright
#  
#  This file 'test_clock_timer.py' copyright Gavin J Stark 2017-20
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#a Imports
# import structs
import math
from cdl.sim     import ThExecFile
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from regress.clocking.clock_timer import t_timer_control, t_timer_value, t_timer_sec_nsec
from regress.clocking.clock_timer import clock_timer_adder_bonus, clock_timer_period

#a Useful functions
def find_fractions_for(ns):
    adder_ns = int(ns*16)
    print("adder (%d,%d"%(adder_ns%16, adder_ns//16))
    for j in range(255):
        i = j+1
        d = int((ns*16-adder_ns)*i)
        print(i, d, "(%d,%d)"%(i-d,i), (25+d/(i+0.))/16, "(%d,%d)"%(i-d-1,i), (25+(d+1)/(i+0.))/16)
        pass
    pass
#a Globals

#a Test classes
#c c_clock_timer_test_base
class c_clock_timer_test_base(ThExecFile):
    """
    Find a slightly slower bonus fraction for 1.6ns
    """
    master_adder = (1,0)
    master_bonus = (0,0)
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(1.6)
    slave_lock = False
    lock_window_lsb = 6
    hw_clk = "clk"
    #f configure_master
    def configure_master(self, adder, bonus=(0,0)):
        self.master_timer_control__bonus_subfraction_sub.drive(bonus[1])
        self.master_timer_control__bonus_subfraction_add.drive(bonus[0])
        self.master_timer_control__fractional_adder.drive(adder[1])
        self.master_timer_control__integer_adder.drive(adder[0])
        self.master_timer_control__reset_counter.drive(1)
        self.master_timer_control__enable_counter.drive(0)
        print("Master configured for %fns %fMHz"%(clock_timer_period(adder, bonus),1000.0/clock_timer_period(adder, bonus)))
        pass
    #f configure_slave
    def configure_slave(self, adder, bonus=(0,0), lock=False):
        self.slave_timer_control__bonus_subfraction_sub.drive(bonus[1])
        self.slave_timer_control__bonus_subfraction_add.drive(bonus[0])
        self.slave_timer_control__fractional_adder.drive(adder[1])
        self.slave_timer_control__integer_adder.drive(adder[0])
        self.slave_timer_control__reset_counter.drive(1)
        self.slave_timer_control__enable_counter.drive(0)
        print("Slave configured for %fns %fMHz"%(clock_timer_period(adder, bonus),1000.0/clock_timer_period(adder, bonus)))
        if lock:
            self.master_timer_control__lock_to_master.drive(1)
            self.master_timer_control__lock_window_lsb.drive({4:0,6:1,8:2,10:3}[self.lock_window_lsb])
            pass
        else:
            self.master_timer_control__lock_to_master.drive(0)
            pass
        pass
    pass
#c c_clock_timer_test_master_0
class c_clock_timer_test_master_0(c_clock_timer_test_base):
    #f run
    def run(self):
        self.sim_msg = self.sim_message()
        self.bfm_wait(100)
        self.configure_master( adder=self.master_adder )
        self.bfm_wait(40)
        self.master_timer_control__reset_counter.drive(0)
        self.bfm_wait(40)
        self.master_timer_control__enable_counter.drive(1)
        self.bfm_wait(1000)
        master = self.master_timer_value__value.value()
        if (master<990) or (master>1010):
            self.failtest("Master clock %d out of range 990 to 1010"%master)
        self.passtest("Test completed")
        pass
    pass

#c c_clock_timer_test_master_sync_0
class c_clock_timer_test_master_sync_0(c_clock_timer_test_base):
    #f run
    def run(self):
        self.sim_msg = self.sim_message()
        self.bfm_wait(100)
        self.configure_master( adder=self.master_adder )
        self.bfm_wait(40)
        self.master_timer_control__reset_counter.drive(0)
        self.bfm_wait(40)
        self.master_timer_control__enable_counter.drive(1)
        self.bfm_wait(100)
        self.master_timer_control__synchronize.drive(3)
        self.master_timer_control__synchronize_value.drive(0x123456789abcdef0)
        self.bfm_wait(1)
        self.master_timer_control__synchronize.drive(0)
        self.bfm_wait(1000)
        master = self.master_timer_value__value.value() - 0x123456789abcdef0
        if (master<990) or (master>1010):
            self.failtest("Master clock %d out of range 990 to 1010"%master)
        self.passtest("Test completed")
        pass
    pass

#c c_clock_timer_test_master_sync_1
class c_clock_timer_test_master_sync_1(c_clock_timer_test_base):
    #f run
    def run(self):
        self.sim_msg = self.sim_message()
        self.bfm_wait(100)
        self.configure_master( adder=self.master_adder )
        self.bfm_wait(40)
        self.master_timer_control__reset_counter.drive(0)
        self.bfm_wait(40)
        self.master_timer_control__enable_counter.drive(1)
        self.bfm_wait(100)
        self.master_timer_control__synchronize.drive(1)
        self.master_timer_control__synchronize_value.drive(0x123456789abcdef0)
        self.bfm_wait(1)
        self.master_timer_control__synchronize.drive(0)
        self.bfm_wait(1000)
        master = self.master_timer_value__value.value() - 0x9abcdef0
        if (master<990) or (master>1010):
            self.failtest("Master clock %d out of range 990 to 1010"%master)
        self.passtest("Test completed")
        pass
    pass

#c c_clock_timer_test_master_sync_2
class c_clock_timer_test_master_sync_2(c_clock_timer_test_base):
    #f run
    def run(self):
        self.sim_msg = self.sim_message()
        self.bfm_wait(100)
        self.configure_master( adder=self.master_adder )
        self.bfm_wait(40)
        self.master_timer_control__reset_counter.drive(0)
        self.bfm_wait(40)
        self.master_timer_control__enable_counter.drive(1)
        self.bfm_wait(100)
        self.master_timer_control__synchronize.drive(2)
        self.master_timer_control__synchronize_value.drive(0x123456789abcdef0)
        self.bfm_wait(1)
        self.master_timer_control__synchronize.drive(0)
        self.bfm_wait(1000)
        master = self.master_timer_value__value.value() - 0x1234567800000000
        if (master<1090) or (master>1110):
            self.failtest("Master clock %d out of range 1090 to 1110"%master)
        self.passtest("Test completed")
        pass
    pass

#c c_clock_timer_test_master_slave_base
class c_clock_timer_test_master_slave_base(c_clock_timer_test_base):
    max_diff = 8
    master_sync = None
    #f run
    def run(self):
        self.sim_msg = self.sim_message()
        self.bfm_wait(100)

        self.configure_master( adder=self.master_adder, bonus=self.master_bonus )
        self.configure_slave( adder=self.slave_adder, bonus=self.slave_bonus, lock=self.slave_lock )
        self.bfm_wait(200)
        self.slave_timer_control__reset_counter.drive(0)
        self.master_timer_control__reset_counter.drive(0)
        self.bfm_wait(200) # For a slow clock period
        self.slave_timer_control__enable_counter.drive(1)
        self.master_timer_control__enable_counter.drive(1)
        if self.master_sync is not None:
            self.bfm_wait(500)
            self.master_timer_control__synchronize.drive(3)
            self.master_timer_control__synchronize_value.drive(self.master_sync)
            self.bfm_wait(1)
            self.master_timer_control__synchronize.drive(0)
            pass
        self.bfm_wait_until_test_done(10)
        master = self.master_timer_value__value.value()
        slave = self.slave_timer_value__value.value()
        diff = abs(master-slave)
        print("Difference in master/slave clocks is %d"%diff)
        if diff>self.max_diff:
            self.failtest("Difference in times is more than %d (%d) (%08x to %08x) - should have locked"%
                          (self.max_diff, diff, master, slave))
        master_sec  = self.master_timer_sec_nsec__sec.value()
        master_nsec = self.master_timer_sec_nsec__nsec.value()
        master_sec_nsec = master_sec*(10**9)+master_nsec
        if master_nsec>10**9:
            self.failtest("Master_nsec should be less than 1000,000,000 (%d)"%
                          (master_nsec))
            pass
        diff = master - master_sec_nsec
        if diff>2:
            self.failtest("Difference in sec/nsec and actual timer is more than 2 (%d) (%08x to %08x)"%
                          (diff, master, master_sec_nsec))
            pass
        slave_sec  = self.slave_timer_sec_nsec__sec.value()
        slave_nsec = self.slave_timer_sec_nsec__nsec.value()
        slave_sec_nsec = slave_sec*(10**9)+slave_nsec
        if slave_nsec>10**9:
            self.failtest("Slave_nsec should be less than 1000,000,000 (%d)"%
                          (slave_nsec))
            pass
        diff = slave - slave_sec_nsec
        if diff>self.slave_adder[0]+1:
            self.failtest("Difference in sec/nsec and actual timer is more than %d (%d) (%08x to %08x)"%
                          (self.slave_adder[0]+1, diff, slave, slave_sec_nsec))
            pass
        self.passtest("Test completed")
        pass
    pass

#c c_clock_timer_test_master_slave_0
class c_clock_timer_test_master_slave_0(c_clock_timer_test_master_slave_base):
    pass
    
#c c_clock_timer_test_master_slave_1
class c_clock_timer_test_master_slave_1(c_clock_timer_test_master_slave_base):
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(1.6002)
    slave_lock=True
    lock_window_lsb = 4
    max_diff = 2  # 600MHz
    pass

#c c_clock_timer_test_master_slave_2
class c_clock_timer_test_master_slave_2(c_clock_timer_test_master_slave_base):
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(1.5998)
    slave_lock=True
    lock_window_lsb = 4
    max_diff = 2  # 600MHz
    pass

#c c_clock_timer_test_master_slave_3
class c_clock_timer_test_master_slave_3(c_clock_timer_test_master_slave_base):
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(1.599)
    slave_lock = True
    lock_window_lsb = 4
    max_diff = 2 # 600MHz
    pass

#c c_clock_timer_test_master_slave_4
class c_clock_timer_test_master_slave_4(c_clock_timer_test_master_slave_base):
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(1.599)
    slave_lock = True
    master_sync = ((10**9)*0xfeedbeef) - 1000
    lock_window_lsb = 4
    max_diff = 2 # 600MHz
    pass

#c c_clock_timer_test_master_slave_5
class c_clock_timer_test_master_slave_5(c_clock_timer_test_master_slave_base):
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(10.0)
    slave_lock = True
    master_sync = ((10**9)*0xfeedbeee) - 1000
    lock_window_lsb = 6
    max_diff = 10 # 100MHz
    pass

#c c_clock_timer_test_master_slave_6
class c_clock_timer_test_master_slave_6(c_clock_timer_test_master_slave_base):
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(100.1)
    slave_lock = True
    master_sync = 0xdeadbeefcafef00d
    lock_window_lsb = 8
    max_diff = 100 # 10MHz
    # In theory this may not work - as the edge detection is too frequent
    # And indeed it does not, except that we have oversped the clock by 1/1600
    # and this helps catch up with the initial delay in synchronization
    pass

#c c_clock_timer_test_master_slave_7
class c_clock_timer_test_master_slave_7(c_clock_timer_test_master_slave_base):
    (slave_adder, slave_bonus) = clock_timer_adder_bonus(100.0)
    slave_lock = True
    master_sync = 0xdeadbeefcafef00d
    lock_window_lsb = 10
    max_diff = 100 # 10MHz
    pass

#a Hardware classes
#c clock_timer_test_hw
class clock_timer_test_hw(HardwareThDut):
    """
    Simple instantiation of clock_timer testbench
    """
    clock_desc = [("clk",(0,5,5)), ("slave_clk",(3,8,8))]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":12}
    module_name = "tb_clock_timer"
    # module_name = "cwv__tb_clock_timer" - does not save much time
    dut_inputs  = {"master_timer_control" : t_timer_control,
                   "slave_timer_control" : t_timer_control,
    }
    dut_outputs = { "master_timer_value":t_timer_value,
                    "master_timer_sec_nsec":t_timer_sec_nsec,
                    "slave_timer_value":t_timer_value,
                    "slave_timer_sec_nsec":t_timer_sec_nsec,
    }
    th_options = {
                 }
    loggers = {
        # "async": {"verbose":0, "filename":"ckts.log", "modules":("dut.ckts "),},
               }
    #f __init__
    def __init__(self, slave_period=None, **kwargs):
        if slave_period is not None:
            self.clock_desc = [("clk",(0,5,5)),
                               ("slave_clk",(3,slave_period//2,slave_period//2)),
            ]
            pass
        HardwareThDut.__init__(self, **kwargs)
        pass
    pass

#a Simulation test classes
#c clock_timer
class clock_timer(TestCase):
    hw = clock_timer_test_hw
    _tests = {"master_0":       (c_clock_timer_test_master_0,        12*1000, {}),
              "master_sync_0":  (c_clock_timer_test_master_sync_0,   20*1000, {}),
              "master_sync_1":  (c_clock_timer_test_master_sync_1,   20*1000, {}),
              "master_sync_2":  (c_clock_timer_test_master_sync_2,   20*1000, {}),
              "master_slave_0": (c_clock_timer_test_master_slave_0,  200*1000, {}),
              "master_slave_1": (c_clock_timer_test_master_slave_1,  5*1000*1000, {}),
              "master_slave_2": (c_clock_timer_test_master_slave_2,  5*1000*1000, {}),
              "master_slave_3": (c_clock_timer_test_master_slave_3,  5*1000*1000, {}),
              "master_slave_4": (c_clock_timer_test_master_slave_4,  1*1000*1000, {}),
              "master_slave_5": (c_clock_timer_test_master_slave_5,  5*1000*1000, {"slave_period":100}),
              "master_slave_6": (c_clock_timer_test_master_slave_6, 25*1000*1000, {"slave_period":1000}),
              "master_slave_7": (c_clock_timer_test_master_slave_7, 25*1000*1000, {"slave_period":1000}),
    }
    pass
