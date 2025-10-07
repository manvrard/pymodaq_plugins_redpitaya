import numpy as np
from qtpy import QtWidgets
from pymodaq.extensions.data_mixer.model import DataMixerModel, np  # np will be used in method eval of the formula

from pymodaq_utils.math_utils import find_index
from pymodaq_gui import utils as gutils
from pymodaq_gui.plotting.data_viewers.viewer1D import Viewer1D

from pymodaq_data.data import DataToExport, DataWithAxes, DataCalculated, DataDim, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.extensions.data_mixer.parser import (
    extract_data_names, split_formulae, replace_names_in_formula)


class SweepFFT(DataMixerModel):
    params = [
        {'title': 'nsamples before max:', 'name': 'nsamp_before', 'type': 'int', 'value': 1000},
        {'title': 'Nsamples after max:', 'name': 'nsamp_after', 'type': 'int', 'value': 1000},

        {'title': 'Get Data:', 'name': 'get_data', 'type': 'bool_push', 'value': False,
         'label': 'Get Data'},
        {'title': 'Data1D:', 'name': 'data1D', 'type': 'itemselect',
         'value': dict(all_items=[], selected=[])},
    ]

    def ini_model(self):
        self.show_data_list()
        self.data_mixer.docks['FFT'] = gutils.Dock('FFT')
        self.data_mixer.dockarea.addDock(self.data_mixer.docks['FFT'], 'right')
        widget_1D = QtWidgets.QWidget()
        self.viewer_raw = Viewer1D(widget_1D)
        self.data_mixer.docks['FFT'].addWidget(widget_1D)

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
                arg_max = np.argmax(dwa_loaded.abs())[1][0]

                shift = arg_max - self.settings['nsamp_before']
                shift = - shift
                dwa_loaded = np.roll(dwa_loaded, shift)
                dwa_loaded = dwa_loaded.isig[0: self.settings['nsamp_before'] + self.settings['nsamp_after']]
                self.viewer_raw.show_data(dwa_loaded)


                dwa_padded = dwa_loaded.pad(2**16)


                dwa_ft = dwa_padded.ft(0, axis_label='Frequency', axis_units='Hz')
                dwa_ft.get_axis_from_index(0)[0].data *= 1/(2*np.pi)

                dwa_ft = dwa_ft.isig[int(dwa_ft.size/2):]


                dwa_intensity = DataCalculated('Intensity',
                                               data=[np.atleast_1d((dwa_ft.abs()**2)[1] / (dwa_ft.abs()**2)[0])],
                                               labels=['Intensity Ratio'],
                                               axes=dwa_ft.axes
                                               )
                dwa_phase = DataCalculated('Phase', data=[np.angle(dwa_ft[1] / dwa_ft[0])],
                                           labels=['Relative Phase'], units='rad',
                                           axes=dwa_ft.axes
                                           )

                dte_processed.append(dwa_intensity)
                dte_processed.append(dwa_phase)

            except Exception as e:
                pass

        return dte_processed




