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

            dwa_loaded = dte.get_data_from_full_name(self.settings['data1D']['selected'][0])

            dwa_ft = dwa_loaded.ft(1, axis_label='Frequency', axis_units='Hz')
            dwa_ft.get_axis_from_index(0)[0].data *= 1/(2*np.pi)

            #%%
            peaks = dwa_ft.abs().find_peaks(height=100)
            arg_max = np.argmax(dwa_ft.abs())

            #%%


            index_0 = int(dwa_loaded.shape[1] /2)

            dwa_ft_square = (dwa_ft.abs()**2)

            frequency = np.abs(dwa_ft.axes[0].get_data()[arg_max])
            intensity = dwa_ft_square.isig[arg_max]
            phase = np.angle(np.array([data_array[index_max] for data_array in dwa_ft.isig[index, index_0:]]))
            #%%
            dwa_intensity = DataCalculated('Intensity', data=[intensity[1,:] /
                                                              intensity[0,:]],
                                           labels=['Intensity'],
                                           axes=[Axis('Frequency', units='Hz', data=frequency)])
            dwa_phase = DataCalculated('Phase', data=[np.unwrap(phase[1,:] - phase[0,:])],
                                       labels=['Phase'], units='rad',
                                       axes=[Axis('Frequency', units='Hz', data=frequency)])

            dte_processed.append(DataCalculated('Intensity',
                                                data=[intensity],
                                                labels=['Intensity'],
                                                axes=[Axis('Frequency', units='Hz', data=frequency)]),
                                 DataCalculated('Phase',
                                                data=[phase],
                                                labels=['Phase'],
                                                axes=[Axis('Frequency', units='Hz', data=frequency)]))


        return dte_processed




