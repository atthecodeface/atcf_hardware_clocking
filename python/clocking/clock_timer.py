#a Copyright
#  
#  This file 'clock_timer.py' copyright Gavin J Stark 2017-20
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

#t t_timer_control
t_timer_control = {"reset_counter":1,
                 "enable_counter":1,
                 "advance":1,
                 "retard":1,
                 "lock_to_master":1,
                 "lock_window_lsb":2,
                 "synchronize":2,
                 "synchronize_value":64,
                 "block_writes":1,
                 "bonus_subfraction_add":8,
                 "bonus_subfraction_sub":8,
                 "fractional_adder":4,
                 "integer_adder":8,
}

#t t_timer_value
t_timer_value = {"irq":1,
               "locked":1,
               "value":64,
}

#t t_timer_sec_nsec
t_timer_sec_nsec = {"valid":1,
               "sec":35,
               "nsec":30,
}

def dda_of_ratio(r):
    if r is None: return (0,0)
    (n,d) = r
    dda_add = n-1
    dda_sub = d-2-dda_add
    return (dda_add, dda_sub)
    
def find_closest_ratio(f, max):
    def ratio_compare(f, r):
        (n,d) = r
        diff = f*d - n
        if abs(diff)<1.0/max/3: return 0
        if diff<0: return -1
        return 1
    must_be_above = (0, 1)
    must_be_below = (1, 0)
    while True:
        ratio_to_test = (must_be_below[0] + must_be_above[0],
                         must_be_below[1] + must_be_above[1])
        (dda_add, dda_sub) = dda_of_ratio(ratio_to_test)
        if (dda_add>=max) or (dda_sub>=max):
            break
        c = ratio_compare(f,ratio_to_test)
        if (c==0): return ratio_to_test
        if (c==1):
            must_be_above = ratio_to_test
            pass
        else:
            must_be_below = ratio_to_test
            pass
        pass
    if must_be_above[0]==0: return None
    return must_be_above
                     
def clock_timer_adder_bonus(ns):
    ns_times_16 = (16.0*ns+1E-16)
    adder = int(ns_times_16)
    bonus = ns_times_16 - adder
    bonus = find_closest_ratio(bonus, 256)
    bonus = dda_of_ratio(bonus)
    adder = (adder // 16, adder % 16)
    #print "Adder and bonus for %f is %s, %s"%(ns, str(adder), str(bonus))
    return (adder, bonus)

def clock_timer_period(adder, bonus):
    ns_times_16 = adder[0]*16 + adder[1]
    if (bonus[0]==0) and (bonus[1]==0):
        bonus=0.
    else:
        bonus = (bonus[0]+1.) / (bonus[0] + bonus[1] + 2)
        pass
    return (ns_times_16 + bonus) / 16.0
