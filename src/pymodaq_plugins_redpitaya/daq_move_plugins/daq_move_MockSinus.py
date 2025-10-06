
from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.utils import ThreadCommand  # object used to send info back to the main thread

from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_redpitaya.hardware.mock_sinus import MockSinus

from pymodaq_data import Q_

from pymodaq_plugins_redpitaya.utils import Config

plugin_config = Config()


class DAQ_Move_MockSinus(DAQ_Move_base):
    """ Instrument plugin class for Red Pitaya

       """
    is_multiaxes = False
    _axis_names: Union[List[str], Dict[str, int]] = ['frequency']
    _controller_units: Union[str, List[str]] = ['Hz']
    _epsilon: Union[float, List[float]] = 0.1
    data_actuator_type = DataActuatorType.DataActuator

    params = [
                ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)
    # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # the target value. It is the developer responsibility to put here a meaningful value

    def ini_attributes(self):
        self.controller: MockSinus = None
        pass

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = DataActuator(data=self.controller.frequency,
                           units='Hz')
        pos = self.get_position_with_scaling(pos)

        return pos

    def close(self):
        """Terminate the communication protocol"""
        ...

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ...


    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        if self.is_master:  # is needed when controller is master
            self.controller = MockSinus()
        else:
            self.controller = controller

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """
        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one

        self.controller.frequency = value.value('Hz')

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        self.move_abs(self.target_value)

    def move_home(self):
        """Call the reference method of the controller"""
        pass

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""
        pass


if __name__ == '__main__':
    main(__file__)
