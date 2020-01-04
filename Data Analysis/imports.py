from enum import Enum
import numpy as np
import pyxdf
import matplotlib.pyplot as plt


from neurodsp import filt
from neurodsp import spectral
from neurodsp.timefrequency import amp_by_time, freq_by_time, phase_by_time

import scipy.signal as signal
from sklearn.decomposition import FastICA