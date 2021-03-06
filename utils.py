import wfdb
from scipy.fftpack import rfft, irfft, fftfreq
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np


def load_waveform_file(path):
    """Load NumPy (.npy) file."""
    data = np.load(path)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    return data


def _resample_waveform(waveform, fs, new_fs):
    """Resample training sample to set sample frequency."""

    if len(waveform.shape) == 1:
        waveform = waveform.reshape(-1, 1)
    length, leads_num = waveform.shape

    # Get time array
    time = np.arange(length) * 1 / fs

    # Generate new resampling time array
    times_rs = np.arange(0, time[-1], 1 / new_fs)

    interpolated_waves = np.zeros((len(times_rs), leads_num))

    # Setup interpolation function for every leads
    for lean_n in range(leads_num):
        interp_func = interpolate.interp1d(x=time, y=waveform[:, lean_n], kind='linear')

        # Interpolate contiguous segment
        sample_rs = interp_func(times_rs)
        interpolated_waves[:, lean_n] = sample_rs

    return interpolated_waves

def read_mit_data(file):
    NEW_FS = 200
    LENGTH = 10

    def smooth_line(y, fd):
        # fd - частота дискретизации
        W = fftfreq(y.size, 1 / fd)
        f_signal = rfft(y)
        cut_f_signal = f_signal.copy()
        cut_f_signal[(W < 0.25), :] = 0
        cut_f_signal[(W > 60), :] = 0
        cut_signal = irfft(cut_f_signal)
        return cut_signal

    record = wfdb.rdrecord(file)
    print(record.fs)
    # data = smooth_line(record.adc()[:, 0], record.fs)
    data = record.adc().astype(np.float16)
    if record.fs != NEW_FS:
        data = _resample_waveform(data, fs=record.fs, new_fs=NEW_FS)
    data = data[:NEW_FS * LENGTH, :] # 10 sec
    if len(data) < NEW_FS * LENGTH:
        tmp = np.zeros((NEW_FS * LENGTH, 12))
        tmp[:len(data), :] = data
        data = tmp
    data /= 1000 # mV
    return data.transpose()

def read_npy_data(file):
    NEW_FS = 200
    LENGTH = 10

    def smooth_line(y, fd):
        # fd - частота дискретизации
        W = fftfreq(y.size, 1 / fd)
        f_signal = rfft(y)
        cut_f_signal = f_signal.copy()
        cut_f_signal[(W < 0.25), :] = 0
        cut_f_signal[(W > 60), :] = 0
        cut_signal = irfft(cut_f_signal)
        return cut_signal

    data = load_waveform_file(file)
    data = _resample_waveform(data, fs=500, new_fs=NEW_FS)
    data = data[:NEW_FS * LENGTH, :] # 10 sec
    if len(data) < NEW_FS * LENGTH:
        tmp = np.zeros((NEW_FS * LENGTH, 12))
        tmp[:len(data), :] = data
        data = tmp
    data /= 1000 # mV
    return data.transpose()


def read_mit_fig(file):
    def smooth_line(y, fd):
        # fd - частота дискретизации
        W = fftfreq(y.size, 1 / fd)
        f_signal = rfft(y)
        cut_f_signal = f_signal.copy()
        cut_f_signal[(W < 0.25)] = 0
        cut_f_signal[(W > 60)] = 0
        cut_signal = irfft(cut_f_signal)
        return cut_signal

    plt.cla()
    record = wfdb.rdrecord(file)
    fig = wfdb.plot_items(signal=smooth_line(record.p_signal[:, 0], record.fs),
                        title='V1', time_units='seconds',
                        fs=record.fs,
                        figsize=(10,2), return_fig=True)#, ecg_grids='all')

    return fig


def resample_waveform(waveform, src_fs, dst_fs):
    """Resample training sample to set sample frequency."""

    if len(waveform.shape) == 1:
        waveform = waveform.reshape(-1, 1)
    length, leads_num = waveform.shape

    # Get time array
    time = np.arange(length) * 1 / src_fs

    # Generate new resampling time array
    times_rs = np.arange(0, time[-1], 1 / dst_fs)

    interpolated_waves = np.zeros((len(times_rs), leads_num))

    # Setup interpolation function for every leads
    for lean_n in range(leads_num):
        interp_func = interpolate.interp1d(x=time, y=waveform[:, lean_n],  kind='linear')

        # Interpolate contiguous segment
        sample_rs = interp_func(times_rs)
        interpolated_waves[:, lean_n] = sample_rs

    return interpolated_waves