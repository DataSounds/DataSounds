#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO


import numpy as np

from sebastian.lilypond.interp import parse
from sebastian.midi.write_midi import SMF
from sebastian.core.transforms import stretch
from sebastian.core import notes


def note_classes(arr, scale):
    '''
    Get note classes from data range.

    Parameters
    ----------
    arr : arr
        array to be arranged as note classes.
    scale : an `build_scale` object
        Consists of a Tone scaled. (C maj, pentatonic C, C min, etc.)

    Returns
    -------
    Parametreized values of musical notes based on input array.
    '''
    minr = np.nanmin(arr)
    maxr = np.nanmax(arr)
    _, bins = np.histogram(arr, bins=len(scale) - 1, range=(minr, maxr))
    return bins


def note_number(arr, scale):
    '''
    Get a relative number of notes, included in a choiced scale.

    Parameters
    ----------
    arr : arr
        array to be arranged as note classes.
    scale : an `build_scale` object

    Returns
    -------
    mapping : arr
        Note number of input array parameterized with choiced scale.
        Note number follows the Sebastian sequence, and it can be
        visualized for any number with:
        sebastian.core.notes.name('2') will return musical note "E".
    '''
    x_notes = note_classes(arr, scale)
    mapping = np.searchsorted(x_notes, arr, side='left').astype('f8')
    mapping[np.isnan(arr)] = np.nan
    return mapping


def note_on_classes(note, arr, scale):
    if np.isnan(note):
        return np.nan

    x_notes = note_classes(arr, scale)
    return np.searchsorted(x_notes, note, side='left').astype('f8')


def pentatonic_scale(tonic):
    '''
    Pentatonic scale, based on Major Pentatonic.
    Not implemented on Sebastian.

    References
    ----------
    http://en.wikipedia.org/wiki/Pentatonic_scale
    '''
    return [tonic + i for i in [0, 2, 4, 1, 3]]


def blues_scale(tonic):
    '''
    Blues scale

    References
    ----------
    http://en.wikipedia.org/wiki/Blues_scale
    '''
    return [tonic + i for i in [0, 2, 4, -1, 1, 3, 5]]


def build_scale(key, mode='major', octaves=1):
    '''
    Build a scale from a refference note.

    Parameters
    ----------
    key : Musical key.
        Can be setted as a parameter while building scale.
        Key should be written as "C", for C and "C#" for C sharp and
        "Cb" for C flat.

    mode : Musica mode.
        'major' and 'minor' and 'pentatonic' are accetable parameters.

    octaves : int
        number of octaves to be evaluated.

    Returns
    -------
    scale_notes : sebastian.core.elements
        Sequence of scale notes.
    '''
    if mode == 'major':
        scale = notes.major_scale
    elif mode == 'minor':
        scale = notes.minor_scale
    elif mode == 'pentatonic':
        scale = pentatonic_scale
    elif mode == 'blues':
        scale = blues_scale

    scale_notes = [notes.name(s).lower() + ("'" * octave)
                   for octave in range(octaves)
                   for s in scale(notes.value(key))]
    return scale_notes


def note_name(number, scale):
    '''
    Transform a number to a note string, including np.nan as musical rests.
    '''
    if np.isnan(number):
        return "r"
    else:
        return scale[int(number)].replace('#', 'is')


def chord_scaled(arr, scale, period=12):
    '''
    Scales an note's array
    '''
    remainder = arr.size % period
    if remainder:
        fill = period - remainder
        arr = np.append(arr, np.zeros(fill) * np.nan)

    arr_scaled = np.int32([np.nansum(row) / len(row)
                           for row in arr.reshape((-1, period))])

    root_scaled = [note_on_classes(note, arr, scale) for note in arr_scaled]
    root = []
    third = []
    fifth = []
    for note in root_scaled:
        root.append(note_name(note, scale))
        third.append(note_name(note, scale))
        fifth.append(note_name(note, scale))

    seq1 = parse(" ".join(root))
    seq2 = parse(" ".join(third))
    seq3 = parse(" ".join(fifth))

    # chords = (seq1 * period) // (seq2 * period) // (seq3 * period)
    chords = seq1 // seq2 // seq3
    # return (chords | add({DURATION_64: chords[0][DURATION_64] * period}))
    return (chords | stretch(period))
    # return chords


def get_music(series, key='C', mode='major', octaves=2,
              instruments=None, period=12):
    '''
    Returns music generated from an inserted series.

    Parameters
    ----------
    series : an array that could be an 2d-array.

    key : Musical key.
        Can be setted as a parameter while building scale.
        Key should be written as "C", for C and "C#" for C sharp and
        "Cb" for C flat.

    mode : Music mode.
        'major', 'minor' and 'pentatonic' are accetable parameters.
        More options of modes on `build_scale`.

    octaves : Number of available scales for musical construction.
        As higher are the octaves higher pitch differeneces will occur
        while representing your data.

    instruments : list of MIDI instruments.
        General MIDI Level 1 Instrument Patch Map can be found at:
        http://en.wikipedia.org/wiki/General_MIDI
        Gran Piano is the default usage value '[0]' if any instruments
        are declared.
        Fewer examples:
        [0] Acoustic Grand Piano
        [18] Rock Organ
        [23] Tango Accordion
        [32] Acoustic Bass
        [73] Flute

    period : int
        parameter of chord_scaled function.

    Returns
    -------
    midi_out : BytesIO object.
        It can be written on a file or used by your way.

    Example
    -------
    >>> serie = np.random.random(10).reshape(2,5)
    array([[ 0.13536875,  0.42212475,  0.26360219,  0.30153336,  0.62150923],
       [ 0.49384405,  0.32503762,  0.85549822,  0.80212442,  0.70702405]])

    >>> get_music(serie, octaves=2, instruments=(0,23))
    <io.BytesIO instance at 0x7f98201c9d40>

    '''
    midi_out = BytesIO()

    series = np.array(series)
    scale = build_scale(key, mode, octaves)
    melodies = []
    if len(series.shape) == 1:
        if all(np.isnan(series)):
            melody = []
            melodies.append(melody)
        else:
            snotes = note_number(series, scale)
            melody = parse(' '.join([note_name(x, scale) for x in snotes]))
            melodies.append(melody)
    else:
        for i in range(series.shape[0]):
            if all(np.isnan(series[i])):
                melody = []
                melodies.append(melody)
            else:
                snotes = note_number(series[i], scale)
                melody = parse(' '.join([note_name(x, scale) for x in snotes]))
                melodies.append(melody)
        
            # chords = chord_scaled(series, scale, period)
            # Transform it to a MIDI file with chords.
            # s = SMF([melody, chords], instruments=[0, 23])
    if instruments is None:
        s = SMF(melodies)
    else:
        s = SMF(melodies, instruments)

    s.write(midi_out)
    return midi_out

def w2Midi(name, BytesIo):
    '''
    Writes the output of `get_music` inside a '.midi' file on disk.

    Parameters
    ----------
    name : str
        name of file
    BytesIo : get_music output variable
        varible of music generated with `get_music`
    '''
    Muz_file = open(str(name)+'.midi', 'w')
    Muz_file.write(BytesIo.getvalue())
    Muz_file.close()
