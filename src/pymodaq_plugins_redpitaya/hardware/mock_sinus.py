import numpy as np

from pymodaq_utils.math_utils import gauss1D

class MockSinus:

    def __init__(self):
        self._frequency = 1234  #Hz
        self._frequency_0 = 12340  #Hz resonance
        self._dfrequency_0 = 1567 #Hz width of the resonance
        self.Npts = 1024

    def get_window(self):
        return 5 / self._frequency

    def get_time_axis(self):
        return np.linspace(-self.get_window() /2, self.get_window()/2, self.Npts )

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, frequency: float):
        if frequency >= 0.:
            self._frequency = frequency

    def get_envelop(self, frequency: float):
        return 3 * (gauss1D(frequency, self._frequency_0, self._dfrequency_0)) + 1.0

    def get_phase(self, frequency: float):
        return np.arctan((frequency-self._frequency_0) / self._dfrequency_0)

    def snap(self) -> tuple[np.ndarray, np.ndarray]:
        return (np.sin(2*np.pi*self._frequency*self.get_time_axis()),
                self.get_envelop(self.frequency) * np.sin(2*np.pi*self._frequency*self.get_time_axis()
                                                          + self.get_phase(self.frequency)))

