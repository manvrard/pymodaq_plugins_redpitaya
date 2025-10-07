import numpy as np
from qtpy import QtWidgets
from qtpy.QtCore import QThread

from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_redpitaya.utils import Config

from pymodaq_plugins_redpitaya.hardware.mock_sinus import MockSinus


class DAQ_1DViewer_MockSweep(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through
    inheritance via DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the
    Python wrapper of a particular instrument.

    * Should be compatible with all redpitaya flavour using the SCPI communication protocol
    * Tested with the STEMlab 125-14 version
    * PyMoDAQ >= 4.1.0

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    plugin_config = Config()

    params = comon_parameters+[
        {'title': 'Start Freq', 'name': 'start', 'type': 'float', 'value': 1000, 'suffix': 'Hz', 'siPrefix': True},
        {'title': 'Stop Freq', 'name': 'stop', 'type': 'float', 'value': 30000, 'suffix': 'Hz', 'siPrefix': True},
        {'title': 'Duration', 'name': 'duration', 'type': 'float', 'value': 20e-3, 'suffix': 's', 'siPrefix': True},
        {'title': 'Roll?', 'name': 'roll', 'type': 'bool', 'value': False},
        ]

    def ini_attributes(self):
        self.controller: MockSinus = None
        self.x_axis: Axis = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'frequency':
            self.controller.frequency = param.value()

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        if self.is_master:
            self.controller = MockSinus()
        else:
            self.controller = controller

        info = f"ok"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        pass

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """

        axis = Axis('time', units='s', data=self.controller.get_time_axis())
        data_list = self.controller.sweep(self.settings['start'],
                                          self.settings['stop'],
                                          self.settings['duration'],
                                          self.settings['roll'])
        self.dte_signal.emit(DataToExport('Redpitaya_dte',
                                          data=[DataFromPlugins(name='RedPitaya', data=list(data_list),
                                                                dim='Data1D', labels=['AI0', 'AI1'],
                                                                axes=[axis])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        return ''


if __name__ == '__main__':
    main(__file__, init=False)
