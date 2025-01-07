# Clocking and real-time clock library

This library contains some global clocking and real-time clock timer modules.

TODO: change the '16' in the eye tracking to something more sensible

TODO: change the clock design period configuration

TODO: split out `t_timer_config`

## Real-time clock / timer modules

The real-time clock modules generate a `t_timer_value` which is a
64-bit timer value that can be distributed across a device and across
clock domains, such that the timer value is the same at any point on
the device.

The purpose of the timer value is to support a 64-bit global nanosecond
clock that can be used as a 'nanoseconds since' an epoch - for PTP
this would be 1 January 1970 00:00:00 TAI, which is 31 December 1969
23:59:51.999918 UTC. A 64-bit nanosecond timestamp with this epoch
wraps roughly in the year 2106.

Each clock module is provided with a base clock configuration that
specifies the precise design frequency of the clock; the actual clock
itself will vary over time from this value, of course.

## `clock_timer`_module

The `clock_timer` module uses a `t_timer_control` to generate a
`t_timer_value`, which is a monotonically increasing 64-bit timer
value. It maintains a 64-bit integer and a fractional nanosecond
value, and each clock is configured with its design clock period in
fractional nanosecond so that the timer increment correctly.

The timer control has a fractional component to permit, for example, a
*nanosecond* timer that is clocked at, say, 600MHz; in this case the
timer is ticked every 1.666ns, and so an addition in each cycle of
0xa to a 4-bit fractional component and a 1 integer component. The
timer_control has, therfore, a fixed-point adder value with a 4-digit
fractional component.

In addition a synchronous advance/retard option is provided for.  Each
time advance is seen going high (i.e. positive edge of advance) then
on an addition the timer will increment by a bonus half design clock
period value.  Each time retard is seen going high the timer will
reduces its increment by only a half design clock period value.

### Subfraction - move this to a 24-bit + exponent add instead, with a 64.24 timer value

With only a 4-bit fraction of a nanosecond for a 600MHz clock this
would actually lead to a timer that would be only 99.61% accurate.

Hence a further subfraction capability is supported; this permits a
further 1/16th of a nanosecond (or whatever the timer unit is) to be
added for (A+1) cycles out of every (A+S+2).

Furthermore, there is a synchronize control. When this is asserted, on the next
clock edge where the clock is loaded with the 64-bit synchronization value.

## `t_timer_control` - split

Note: This type currently contains too much information.

The control of the clock timer is to provide a synchronous reset and
enable control, plus the advance and retard controls.

It has an additional control signal that is propagated which disables
out-of-band writes to a downstream clock timer value; if this is
deasserted and there are other means to set a timer (by a CSR write,
for example) then such writes are permitted and the downstream timer
is not guaranteed to be synchronized throughout the system; if this is
asserted then out-of-band writes to the timer value are **not**
permitted and should be blocked by any CSR-like write mechanism.

```
    bit     reset_counter                       "Assert to reset the timer counter to 0; this takes precedence over enable_counter";
    bit     enable_counter                      "Assert to enable the timer counter; otherwise it holds its value";
    bit     advance                             "If enable_counter is asserted, a positive edge moves the clock on by a bonus half of the design clock period";
    bit     retard                              "If enable_counter is asserted, a positive edge moves the clock on by only half of the design clock period";
    bit     block_writes                        "If the timer has a seperate read/write interface, block writes";
```

The design configuration of the clock timer provides the design clock period for the clock of the timer

```

    bit[8]  bonus_subfraction_add               "A fractional 1/16 is added to the timer every @a (add+1) / (@a add + @a sub + 2) cycles; if zero and @a sub is zero then no fractional add is performed";
    bit[8]  bonus_subfraction_sub               "Used with @a add for fractional addition; (@sub + 1) is subtracted from the dda accumulator if that is +ve";
    bit[4]  fractional_adder                    "f in fraction f/16 to add per cycle";
    bit[8]  integer_adder                       "integer amount to add to timer counter per cycle";
```

The clock timer lock control is used to specify how a slave clock
timer module should lock on to a master clock timer module; this
indicates the time period over which the slave should determine if it
should advance or retard its timer value by half a clock period.

```
    bit     lock_to_master                      "Used by slaves to enable locking to a master when they are asynchronous; if this is clear then the slave does not advance or retard";
    t_timer_lock_window_lsb lock_window_lsb     "Used by slaves to control the synchronization loop bandwidth";
    bit[2]  synchronize                         "Two bits to indicate whether to write top or bottom halves";
    bit[64] synchronize_value                   "Value to synchronize to";
```

async uses synchronize, reset, enable and `lock_to_master` on master control in

async uses slave control in adder values only

```
    bit     reset_counter                       "Assert to reset the timer counter to 0; this takes precedence over enable_counter";
    bit     enable_counter                      "Assert to enable the timer counter; otherwise it holds its value";
    bit     advance                             "When enabled, a positive edge moves the clock on by half the amount more";
    bit     retard                              "When enabled, a positive edge moves the clock on by half the amount less than normal";
    bit     lock_to_master                      "Used by slaves to enable locking to a master when they are asynchronous";
    t_timer_lock_window_lsb lock_window_lsb     "Used by slaves to control the synchronization loop bandwidth";
    bit[2]  synchronize                         "Two bits to indicate whether to write top or bottom halves";
    bit[64] synchronize_value                   "Value to synchronize to";
    bit     block_writes                        "If the timer has a seperate read/write interface, block writes";
    bit[8]  bonus_subfraction_add               "A fractional 1/16 is added to the timer every @a (add+1) / (@a add + @a sub + 2) cycles; if zero and @a sub is zero then no fractional add is performed";
    bit[8]  bonus_subfraction_sub               "Used with @a add for fractional addition; (@sub + 1) is subtracted from the dda accumulator if that is +ve";
    bit[4]  fractional_adder                    "f in fraction f/16 to add per cycle";
    bit[8]  integer_adder                       "integer amount to add to timer counter per cycle";
} t_timer_control;
```

```
    bit[64] value   "64-bit timer value, reflecting the value in the timer counter";
    bit     irq     "Unused at present; Asserted if comparator >= timer value";
    bit     locked  "Asserted if the timer has locked (held low unless in a slave clock domain)";
} t_timer_value;
```

```
bit valid        "If deasserted, the data is not currently valid";
bit[35] sec      "Qualified by 'valid', seconds since epoch of timer_value";
bit[30] nsec     "Qualified by 'valid', nanoseconds since epoch of timer_value";
} t_timer_sec_nsec;
```

## `clock_timer_async` module

This module implements an asynchronous clock timer crossing, usually
from a fast clock to a slow clock (although this is not a
requirement).

The slave clock has its own design clock period, and it then inherits
from the master the control of the timer (for reset, enable, etc).

Initially the slave should be synchronized; thereafter it can track
the master clock timer value by monitoring when that value changes
from one power-of-two nanoseconds compared to when the slave clock
timer value performs the same change.

The module provides its own `t_timer_value` out which can be used by
other clients within its clock domain; it also supplies a
`t_timer_control` output that can be used by other clock timer modules
in its clock domain, or to cross into other clock domains.

The `lock_window_lsb` indicates the number of clock timer nanoseconds
that make up a monitoring period; the slave clock timer value is
compared with the master clock timer value for sixteen monitoring
periods, and if it is ahead of the master time clock at the end of two
more periods than it was behind then the slave clock is retarded, and
if it is behind the master time clock at the end of two more periods
than it was ahead then the slave clock is advanced. Hence the fine
adjustment (by half a design clock period) occurs at most once every
16 monitoring periods.

The monitoring period must be no more than the design clock period
divided by 32, divided by the (relative) precision of the clocks
(relative indicating the sum of the ppm of master and slave
clocks). The 'divide by 32' comes from the adjustment of *half* a
design clock period for every 16 monitoring periods.

So, for a 10MHz clock with 200ppm precision: if a monitoring period of
10us is used (i.e. 100 clocks) then the correction performed is half
of the design clock period every 160us; in this time (with 200ppm
precision) then it might be out by 200E-6 times 160E-6 or 32ns; the
actual design period of the clock is 100ns, and hence half is 50ns,
which is greater than 32ns, so this monitoring period is adequate.

The monitoring period is actually specified as a power-of-two of
**ns**, by monitoring specific bits of the clock timer value. So here
8.192us would be used.

The minimum monitoring period is perhaps 16 target clocks (for synchronization)?

```
Freq (MHz)   ppm    Req mp (ns)    Act mp (ns)  Tgt clks
  1000       200      156               64        64
  1000       100      312              256        256
  250        200      625              256        64
  250        100      1250            1024        256
  100        200      1562            1024        102
  100        100      3125            1024        102
   50        200      3125            1024        51
   50        100      6250            4096        204
   10        200      15625           4096        40
   10        100      31250           4096        40
    5        200      31250           1024        5*
    5        100      62500           4096        20
    1        200      156250          4096        4*
    1        100      312500          4096        4*
```


##  `clock_timer_as_sec_nsec` module

On some occasions a `t_timer_value` may not be what is required by a
client, rather a seconds and nanosecond within the second. This module
provides a conversion into such a value.

This module tracks the incoming `timer_value` and produces (with a
cycle of delay) a sec/nsec version of the `timer_value`. It does this
by maintaining a 32-bit value that is the bottom 32-bits of the
starting `t_timer_value` nanosecond of the current second (plus how
many seconds that is since the epoch). As 1 billion = 10^9 (30 bits),
the bottom 9 bits are zero (1 billion is in fact 0x3b9aca00). Note
also that 64 bits of nanoseconds is 35 bits of seconds - up to
0x44b82fa09). It also maintains this value *plus* one billion.

At any time it subtracts from the latest `t_timer_value` the start of
the *current* second, and also separately the start of the *next*
second. If the timer value is *less* than that for the start of the
next second then it must refer to the current second with a nanosecond
offset from the first subtraction; otherwise it is for the current
second *plus one*, with a nanosecond offset from the second
subtraction (and the module will move on one second).

To initialize this process the module includes a 'modulo 1 billion'
state machine; when the incoming `t_timer_value` performns a
significant jump (on enable, or synchronize, etc) then the modulo
state machine kicks in and takes 34 cycles to perform a
modulus-and-remainder-one-billion calculation. Once this has been
done, the value tracking can start - however, it may be a few cycles
before the second value is correct (as the `t_timer_value` could have
moved forwards a second during the calculation).

## Clocking modules

To support receiving data on SGMII and similar SERDES interfaces, some
clocking modules are provided that measure the phase width (in 'delay
taps') of a clock, and which track the validity of delayed data pins
captured using different delay tap values (to track data eye
validity).

A standard use for SGMII is to use the `clocking_phase_measure` module
with a delayed version of `sgmii_rxclk` and a receive data clock that
is a quarter of `sgmii_rxclk` to measure the phase width in delay taps
of the device 'delay' module; then the `sgmii_rxd` pin pair (positive
and negative) are fed through delay modules to 4-bit deserializers
that operate on `sgmii_rxclk`, whose delays are controlled by a
`clocking_eye_tracking` module. The negative data has its delay
constantly adjusted to track the width and center of the serial data
'eye', and the positive data has its delay tweaked to maintain it in
the centre of the eye. This requires the same delay to be applicable
to both positive and negative data in, thus relying on the delay
modules being matched (which they should be on silicon) and the signal
traces being matched (which they should be on the board).

This configuration provides stable serialized receive data that tracks
the center of the SERDES input data eye even if the temperature and
voltage of the board change over time. The quality of the eye and the
tracking are reported by the `clocking_eye_tracking` module.

## `clocking_phase_measure` module

This module is used to measure the phase difference and half-period of
a faster external clock and the clock for this module (which must be
an integer times slower), using a (technology dependent) delay tap
module, with the units for the measurements in 'delay taps' of that
module.

The module is designed to be used to find the clock period (in delay
taps) of a fast clock, which can then be used to control a delay
module that delays a data pin and its inverse data pin that are tied
to that fast clock, to track the eye of the data (by comparing
synchronized edges of the two pins using a data delay and an
inverse-data eye-tracking delay).

The delay tap module should take the to-be-measured clock signal in
and delay it (by a configurable delay), then synchronize it to *this*
modules clk input, and presents that back to this module (as
`sync_value`).

This module can request that a delay be loaded into the delay tap
module, which will be acknowledge by that module. Then this module
will check the `sync_value` is stable for a period of
`delay_capture_count` (32) cycles; hence this module can map a *delay*
into a *is stable* for that delay. If it is not stable then the delay
value indicates a phase difference that is approximately that which
maps an edge of the fast clock to the edge of this module's clock.

This module waits for a phase measurement request; when it receives
one, it starts with a delay of 0 and increases this gradually -
looking for the first delay value that produces an *edge*. Then it
keeps increasing the value until it produces a *stable* (not-edge)
value, and records this delay. It then increases the delay again until
it produces a *stable* value that is the inverse of the first *stable*
value, and it records this delay.

The difference between the two delays (if found!) should be the delay
value of half of the fast clock period, and the initial delay
indicates a delay to an edge. The response also can indicate that the
measurement aborted - due to not finding stable values at any delay,
for example.

## `clocking_eye_tracking` module

This module requires a SERDES-pair of input signals to be deserialized
using separate delay modules (with separate delay configurations). The
deserializers must capture 4 bits at the input clock, and present the
data at the 'data_clk' which is a quarter of the bit data rate.

The *positive* data input should be used as the true data input. The
delay for this is adjusted to try to ensure that it is in the middle
of the 'eye' of the data.

The *negative* data input has its delay changed (around that of the
data input) to find the left edge and right edge of the 'eye' of the
data; in theory, within the 'eye', the negative data should have
falling edge transitions whenever the positive data has rising edge
transitions, and vice versa. The quality can then be the number of
correct edges minus the number of incorrect edges - if no edges are
present, then there is 'no quality' (not a negative or positive
value). If this is accumulated over 100 sets of data, then the quality
is good if the value is bigger than (for example) 128 (assuming that
the data pattern provides an average of 1 transition every four
clocks)

The module operates (when enabled) by assuming the input data is in
the center of the eye; it then tries to find the left edge of the eye
and then it tries to find the right edge of the eye. The attempts has
a 'edge delay' value which starts with the center delay, and then it
uses a 'delta' to this and runs the data quality algorithm - if a
delta has poor quality then half the delta is used and the algorithm
retries (stopping if the delta delay is 0); if good then it accepts
the delta delta as the new 'edge delay' and retries.

The eye width determined with this algorithm should be a reasonable
percentage of the phase width of the clock, if the signal integrity is
good and the data is within the eye.

If the data is approximately on the eye center then this algorithm
finds a reasonable value for the left and right edges of the eye; this
can produce a new eye centre, and the data delay can be tracked toward
that (if tracking is enabled).

If the eye width is too small then this will indicate that the signal
integrity is poor or the data is not actually tracking within the
eye - the center *may* then seek to a new data delay value, moving the
data hopefully to within the eye.

The ability to enable the eye state machine, and the control of
tracking and seeking is provided through the `t_eye_track_request`
input; the quality of the eye is provided in the
`t_eye_track_response`.

It is legal for the client to statically drive the request; the
phase_width *should* be driven by a `clocking_phase_measure` module,
though.

# Commonmark notes

Heading: #; subheading ##; subsubheading ###.

*Italics*, **Bold**, and `inline code`. Or _italics_, __bold__.

> Block quotes

* Item list

1. Numeric list

2. Numeric list

```
Code block
```

[link](http://stuff "Title for link")

![Image description](http://a.jpg "Image title")


