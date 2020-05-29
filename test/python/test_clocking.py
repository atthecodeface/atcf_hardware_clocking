#a Copyright
#  
#  This file 'test_clocking.py' copyright Gavin J Stark 2017-20
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

#t t_bit_delay_config - for std.bit_delay
t_bit_delay_config = { "op":2, "select":1, "value":9}

#t t_bit_delay_response - for std.bit_delay
t_bit_delay_response = { "op_ack":1, "delay_value":9, "sync_value":1}

#a Imports
# import structs
import math
from cdl.sim     import ThExecFile
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
#from .clock_timer import clock_timer_adder_bonus, clock_timer_period
from regress.clocking.clock_timer import clock_timer_adder_bonus, clock_timer_period
from regress.clocking.clocking    import t_phase_measure_request, t_phase_measure_response, t_eye_track_request, t_eye_track_response

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
#c c_clocking_phase_measure_test_base
class c_clocking_phase_measure_test_base(ThExecFile):
    th_name = "c_clocking_phase_measure_test_base"
    verbose = False
    #f run
    def run(self) -> None:
        self.sim_msg = self.sim_message()
        self.bfm_wait(10)
        # simple_tb.base_th.run_start(self)
        self.passtest("Test completed")
        pass

#c c_clocking_phase_measure_test_0
class c_clocking_phase_measure_test_0(c_clocking_phase_measure_test_base):
    def wait_for_delay(self):
        toggle = 0
        if self.delay in self.stable_values:
            self.sync_value = self.stable_values[self.delay]
        else:
            toggle = 1
            pass
        while self.delay_config_cpm__op.value()!=1:
            self.sync_value = self.sync_value ^ toggle
            self.delay_response__sync_value.drive(self.sync_value)
            if self.measure_response__valid.value():
                return True
            self.bfm_wait(1)
            pass
        self.measure_request__valid.drive(0)
        self.delay_response__op_ack.drive(1)
        self.bfm_wait(1)
        self.delay_response__op_ack.drive(0)
        self.bfm_wait(4)
        self.delay = self.delay_config_cpm__value.value()
        return False
    #f run
    def run(self):
        self.sim_msg = self.sim_message()
        self.bfm_wait(100)
        self.stable_values = {0:0,1:0,2:0,
                              31:1,32:1,33:1,34:1,35:1,
                              66:0,67:0,68:0,69:0,70:0,
                              101:1,102:1,103:1,104:1}
        self.delay = 0
        self.sync_value = 0
        self.measure_request__valid.drive(1)
        self.wait_for_delay()
        self.measure_request__valid.drive(0)
        while True:
            if self.wait_for_delay():
                break
            pass

        result = { "initial_value":self.measure_response__initial_value.value(),
                   "initial_delay":self.measure_response__initial_delay.value(),
                   "delay":self.measure_response__delay.value(),
                   }
        self.compare_expected("initial value", 1,  result["initial_value"])
        self.compare_expected("initial delay", 31, result["initial_delay"])
        self.compare_expected("delay",         35, result["delay"])
        self.bfm_wait(10)
        self.measure_request__valid.drive(1)
        self.bfm_wait_until_test_done(10)
        self.passtest("Completed")
        pass

#c c_clocking_eye_tracking_test_base
class c_clocking_eye_tracking_test_base(c_clocking_phase_measure_test_base):
    pass
#c c_clocking_eye_tracking_test_0
class c_clocking_eye_tracking_test_0(c_clocking_eye_tracking_test_base):
    phase_width = 73
    eye_center  = int(phase_width*2.2)
    eye_width = phase_width//2
    #f update_random_data
    def update_random_data(self):
        self.random_data = (self.random_data>>4) | ((self.random_data*0xfedcaf81) & 0xf00000000000)
        pass
    #f find_data_quality
    def find_data_quality(self, delay):
        phases = (delay - self.eye_center + 4*self.phase_width + self.phase_width//2) // self.phase_width
        dist = (delay - self.eye_center + self.phase_width) % self.phase_width
        if dist>self.phase_width//2: # -pw/2 to +pw/2
            dist -= self.phase_width
            pass
        dist = abs(dist) # 0 to +pw/2
        err = dist - self.eye_width//2
        if err<=0:
            quality=1
            pass
        else:
            quality = math.pow(err,-0.3)
            pass
        #print delay, self.eye_center, self.phase_width, dist, err, phases, quality
        return (phases,quality)
    #f data_of_quality
    def data_of_quality(self, quality, step=17):
        (phases, quality) = quality
        data = self.random_data >> phases
        if quality>0.99:
            data = data & 0x1f
        elif (quality>0.75):
            if ((data>>step)&7)==7: data = data>>1
            pass
        elif (quality>0.5):
            if ((data>>step)&3)==3: data = data>>1
            pass
        else:
            data = data ^ (data>>step)
            pass
        return data
    #f eye_track_bfam_wait
    def eye_track_bfm_wait(self, cycles):
        for i in range(cycles):
            if self.eye_track_response__eye_data_valid.value():
                self.eye_track_measure_complete = True
                pass
            self.bfm_wait(1)
            pass
        pass
    #f feed_data_after_delay
    def feed_data_after_delay(self):
        while self.delay_config_cet__op.value()==0:
            self.bfm_wait(1)
            pass
        delay_value = self.data_delay
        if self.delay_config_cet__select.value(): delay_value = self.tracking_delay
        if self.delay_config_cet__op.value()==1:  delay_value = self.delay_config_cet__value.value()
        elif self.delay_config_cet__op.value()==3: delay_value -= 1
        elif self.delay_config_cet__op.value()==2: delay_value += 1
        if self.delay_config_cet__select.value():
            self.tracking_delay = delay_value
            pass
        else:
            self.data_delay = delay_value
            #print("Set data_delay to ",delay_value)
            pass
        self.bfm_wait(10)
        self.delay_response__op_ack.drive(1)
        self.bfm_wait(1)
        self.delay_response__op_ack.drive(0)
        data_quality     = self.find_data_quality(self.data_delay)
        tracking_quality = self.find_data_quality(self.tracking_delay)
        for i in range(200):
            data_p = self.data_of_quality(data_quality,     step=17)
            data_n = self.data_of_quality(tracking_quality, step=23)
            self.update_random_data()
            self.data_p_in.drive(data_p&0xf)
            self.data_n_in.drive(data_n^0xf)
            self.eye_track_bfm_wait(1)
            if self.eye_track_measure_complete:
                self.eye_track_request__measure.drive(0)
                return
            pass
        pass
    #f run
    def run(self):
        self.sim_msg = self.sim_message()
        self.bfm_wait(100)
        self.data_delay = 0
        self.tracking_delay = 0
        self.random_data = 0xf1723622
        print("Eye %d to %d, center %d"%(self.eye_center-self.eye_width//2, self.eye_center+self.eye_width//2, self.eye_center))
        self.bfm_wait(10)
        self.eye_track_request__enable.drive(1)
        self.eye_track_request__track_enable.drive(1)
        self.eye_track_request__seek_enable.drive(1)
        self.eye_track_request__min_eye_width.drive(16)
        self.eye_track_request__phase_width.drive(self.phase_width)
        self.bfm_wait(10)
        self.eye_track_measure_complete = False            
        self.feed_data_after_delay()
        for i in range(50):
            self.eye_track_request__measure.drive(1)
            self.eye_track_measure_complete = False            
            while not self.eye_track_measure_complete:
                self.feed_data_after_delay()
                pass
            pass
        self.bfm_wait_until_test_done(10)
        self.eye_track_request__enable.drive(0)
        self.bfm_wait(1)
        self.passtest("Completed")
        pass

#a Hardware classes
#c clocking_test_hw
class clocking_test_hw(HardwareThDut):
    """
    Simple instantiation of clocking testbench
    """
    clock_desc = [("clk",(0,1,1))]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "tb_clocking"
    dut_inputs  = {"delay_response" :t_bit_delay_response,
                   "measure_request":t_phase_measure_request,
                   "eye_track_request":t_eye_track_request,
                   "data_p_in":4,
                   "data_n_in":4,
    }
    dut_outputs = { "delay_config_cpm":t_bit_delay_config,
                    "delay_config_cet":t_bit_delay_config,
                    "measure_response": t_phase_measure_response,
                    "eye_track_response": t_eye_track_response,
    }
    th_options = {
                 }
    th_exec_file_object_fn = c_clocking_phase_measure_test_0
    loggers = {#"itrace": {"verbose":0, "filename":"itrace.log", "modules":("dut.trace "),},
               }
    pass

#a Simulation test classes
#c clocking_phase_measure
class clocking_phase_measure(TestCase):
    hw = clocking_test_hw
    def test_simple(self):
        self.run_test(hw_args={"verbosity":0, "th_exec_file_object_fn":c_clocking_phase_measure_test_0}, run_time=10000)
        pass
    pass

#c clocking_eye_tracking
class clocking_eye_tracking(TestCase):
    hw = clocking_test_hw
    def test_simple(self):
        self.run_test(hw_args={"verbosity":0, "th_exec_file_object_fn":c_clocking_eye_tracking_test_0}, run_time=350*1000)
        pass
    pass

