# %% md
# # Full Wave Rectifier
# ## Let's draw the circuit first
# For that I will use schemdraw
# ### v1.0

# %% Draw
import schemdraw
schemdraw.use('svg')
elm=schemdraw.elements
d=schemdraw.Drawing()
d+=elm.Line().right()
d+=elm.Line(unit=0.5).up()
d+=elm.SourceSin(unit=4).reverse().up().at((0, 0))
d+=elm.Line().right()
d+=elm.Line(unit=0.5).down()
d+=elm.Diode(unit=3/1.4).theta(-45).hold()
d+=elm.Diode(unit=3/1.4).theta(-135).reverse()
d.push()
d+=elm.Line(unit=.5).left()
d+=elm.Ground()
d.pop()
d+=elm.Diode(unit=3/1.4).theta(-45)
d+=elm.Diode(unit=3/1.4).theta(45)
d+=elm.Line(unit=0.5).right()
d.push()
d+=elm.Gap(unit=1)
d+=elm.Line(unit=.5)
d+=elm.Resistor(unit=1.5).down().label('$R_L$', loc='bottom')
d+=elm.Ground()
d.pop()

# %% unfiltered
uf=schemdraw.Drawing(file='rectifier_full_ckt.svg', backend='svg')
uf+=elm.ElementDrawing(d)
uf.push()
uf+=elm.Line(unit=1).right()
uf.pop()
uf.draw()

# %% with capacitor filter
f=schemdraw.Drawing(file='rectifier_full_c_ckt.svg', backend='svg')
f+=elm.ElementDrawing(uf)
f+=elm.Capacitor(unit=1.5).down()
f+=elm.Ground()
f.draw()

# %% with inductor capacitor filter
lf=schemdraw.Drawing(file='rectifier_full_lc_ckt.svg', backend='svg')
lf+=elm.ElementDrawing(d)
lf+=elm.Inductor(unit=1).right().hold()
lf+=elm.Capacitor(unit=1.5).down()
lf+=elm.Ground()
lf.draw()

# %% md
# ## Now the simulation
# For this I will use PySpice

# %% import
import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# %% setup
logger = Logging.setup_logging()

# %% ckt
ckt = Circuit("Full Wave Rectifier")
ckt.include('../model_library/diode.lib')
source=ckt.SinusoidalVoltageSource('input', 'input', 'input2', amplitude=10@u_V, frequency=50@u_Hz)
ckt.D('1', 'input', 'load', model='1N4148')
ckt.D('2', ckt.gnd, 'input', model='1N4148')
ckt.D('3', 'input2', 'load', model='1N4148')
ckt.D('4', ckt.gnd, 'input2', model='1N4148')
ckt.R('l', 'load', ckt.gnd, 100@u_Ohm)

# %% simulate
simulator = ckt.simulator()
analysis = simulator.transient(step_time=source.period/200, end_time=source.period*3)

# %% c filter
ckt.C('f', 'load', ckt.gnd, 1@u_mF)

# %% simulate c filter
simulator = ckt.simulator()
cfanalysis = simulator.transient(step_time=source.period/200, end_time=source.period*3)

# %% lc filter
ckt.Rl.detach()
ckt.L('f', 'load', 'loadr', 1@u_H)
ckt.R('', 'loadr', ckt.gnd, 100@u_Ohm)

# %% simulate lc filter
simulator = ckt.simulator()
lcfanalysis = simulator.transient(step_time=source.period/200, end_time=source.period*3)

# %% md
# ### Now let's plot the data
# For this I will use matplotlib

# %% import
import matplotlib.pyplot as plt

# %% plot data
fig, ax=plt.subplots()
ax.set(title="Half Wave Rectifier", ylabel='Voltage in V', xlabel='Time in x0.1 ms')
ax.grid()
ax.axhline(y=0, color='black')
ax.axvline(x=0, color='black')
ax.plot(analysis.input-analysis.input2, label='input')
ax.plot(analysis.load, label='unfiltered output')
ax.plot(cfanalysis.load, label='C filtered output')
ax.plot(lcfanalysis.loadr, label='LC filtered output')
plt.legend()
plt.show()
plt.savefig('rectifier_full_plt.svg')
