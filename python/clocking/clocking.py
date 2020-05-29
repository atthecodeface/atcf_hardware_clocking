#a Copyright
#  
#  This file 'clocking.py' copyright Gavin J Stark 2017-20
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

#t t_phase_measure_request
t_phase_measure_request = {"valid":1}

#t t_phase_measure_response
t_phase_measure_response = {"ack":1, "abort":1, "valid":1, "delay":9, "initial_delay":9, "initial_value":1}

#t t_eye_track_request
t_eye_track_request = {"enable":1, "seek_enable":1, "track_enable":1, "measure":1, "phase_width":9, "min_eye_width":9}

#t t_eye_track_response
t_eye_track_response = {"measure_ack":1, "locked":1, "eye_data_valid":1, "data_delay":9, "eye_width":9, "eye_center":9}

