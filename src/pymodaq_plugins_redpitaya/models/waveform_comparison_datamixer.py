import numpy as np

from pymodaq.extensions.data_mixer.model import DataMixerModel, np  # np will be used in method eval of the formula

from pymodaq_utils.math_utils import find_index


from pymodaq_data.data import DataToExport, DataWithAxes, DataCalculated, DataDim, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.extensions.data_mixer.parser import (
    extract_data_names, split_formulae, replace_names_in_formula)


class WaveformComparison(DataMixerModel):
    params = [
        {'title': 'Get Data:', 'name': 'get_data', 'type': 'bool_push', 'value': False,
         'label': 'Get Data'},
        {'title': 'Data1D:', 'name': 'data1D', 'type': 'itemselect',
         'value': dict(all_items=[], selected=[])},
    ]

    def ini_model(self):
        self.show_data_list()

    def show_data_list(self):
        dte = self.modules_manager.get_det_data_list()
        data_list1D = dte.get_full_names('data1D')
        self.settings.child('data1D').setValue(dict(all_items=data_list1D, selected=[]))

    def update_settings(self, param: Parameter):
        if param.name() == 'get_data':
            self.show_data_list()

    def process_dte(self, dte: DataToExport):
        dte_processed = DataToExport('computed')
        if len(self.settings['data1D']['selected']) !=  0:
            try:
                dwa_loaded = dte.get_data_from_full_name(self.settings['data1D']['selected'][0])

                dwa_ft = dwa_loaded.ft(0, axis_label='Frequency', axis_units='Hz')
                dwa_ft.get_axis_from_index(0)[0].data *= 1/(2*np.pi)

                #%%
                peaks = dwa_ft.abs().find_peaks(height=100)
                arg_max = int(np.argmax(dwa_ft.abs()).value())

                dwa_ft_square = (dwa_ft.abs()**2)

                frequency = np.abs(dwa_ft.axes[0].get_data()[arg_max])
                intensity = dwa_ft_square.isig[arg_max]
                intensity_ratio = (intensity[1] / intensity[0])
                phase = np.angle(dwa_ft.isig[arg_max])
                relative_phase = np.unwrap(phase[1] - phase[0])
                #%%
                dwa_intensity = DataCalculated('Intensity', data=[intensity_ratio],
                                               labels=['Intensity Ratio'],
                                               )
                dwa_phase = DataCalculated('Phase', data=[relative_phase],
                                           labels=['Relative Phase'], units='rad',
                                           )
                dwa_frequency = DataCalculated('Frequency', data=[np.array([frequency])],
                                           labels=['Relative Phase'], units='rad',
                                           )

                dte_processed.append(dwa_intensity)
                dte_processed.append(dwa_phase)
                dte_processed.append(dwa_frequency)
            except:
                pass
        return dte_processed




