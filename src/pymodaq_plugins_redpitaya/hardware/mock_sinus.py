import numpy as np
from typing import Union

from pymodaq_utils.math_utils import gauss1D

class MockSinus:

    def __init__(self):
        self._frequency = 1234  #Hz
        self._frequency_0 = 12340  #Hz resonance
        self._dfrequency_0 = 1567 #Hz width of the resonance
        self.max_freq = 30000 # Hz
        self.sampling = 1 / (10*self.max_freq)
        self.Npts = 2**13+1

    def get_window(self):
        return self.sampling * self.Npts

    def get_time_axis(self):
        return np.linspace(-self.get_window() /2, self.get_window()/2, self.Npts, endpoint=True)

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, frequency: float):
        if frequency >= 0.:
            self._frequency = frequency

    def get_envelop(self, frequency: Union[float, np.ndarray]) -> np.ndarray:
        return 3 * (gauss1D(frequency, self._frequency_0, self._dfrequency_0)) + 1.0

    def get_phase(self, frequency: Union[float, np.ndarray]) -> np.ndarray:
        return np.arctan((frequency-self._frequency_0) / self._dfrequency_0)

    def snap(self) -> tuple[np.ndarray, np.ndarray]:
        return (np.sin(2*np.pi*self._frequency*self.get_time_axis()),
                self.get_envelop(self.frequency) * np.sin(2*np.pi*self._frequency*self.get_time_axis()
                                                          + self.get_phase(self.frequency)))

    def sweep(self, start, stop, duration, roll = False):
        frequencies = np.linspace(start, stop, int(duration / self.sampling))

        while len(frequencies) < self.Npts:
            frequencies = np.concatenate((frequencies, frequencies))
        if len(frequencies) > self.Npts:
            frequencies = frequencies[:self.Npts]
        if roll:
            frequencies = np.roll(frequencies, np.random.randint(0, self.Npts))

        return (np.sin(2*np.pi*frequencies*self.get_time_axis()),
                self.get_envelop(frequencies) * np.sin(2*np.pi*frequencies*self.get_time_axis()
                                                          + self.get_phase(frequencies)))


