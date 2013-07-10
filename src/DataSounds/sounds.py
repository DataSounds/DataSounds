#/usr/bin/env python
# -*- coding: utf-8 -*-

from StringIO import StringIO

import numpy as np

from sebastian.lilypond.interp import parse
from sebastian.midi.write_midi import SMF
from sebastian.core.transforms import stretch


def note_classes(arr, scale):
    '''
    Get note classes from data range.
    '''
    a = np.nanmin(arr)
    b = np.nanmax(arr)
    count, bins = np.histogram(arr, bins=len(scale) - 1, range=(a, b))
    return bins


def note_number(arr, scale):
    '''
    Get a relative number of notes, included in a choiced scale.
    '''
    x_notes = note_classes(arr, scale)
    mapping = np.searchsorted(x_notes, arr, side='left').astype('f8')
    mapping[np.isnan(arr)] = np.nan
    return mapping


def note_on_classes(n, arr, scale):
    if np.isnan(n):
        return np.nan

    x_notes = note_classes(arr, scale)
    return np.searchsorted(x_notes, n, side='left').astype('f8')


def build_scale(base_note, mode='major', octaves=1):
    '''
    Build a scale from a refference note.
    '''
    if mode == 'major':
        intervals = [0, 2, 4, 5, 7, 9, 11]
    elif mode == 'minor':
        intervals = [0, 2, 3, 5, 7, 8, 10]
    elif mode == 'pentatonic':
        intervals = [0, 2, 4, 7, 9]

    intervals = [n + (12 * octave)
                 for octave in range(octaves)
                 for n in intervals]

    notes = [n + ("'" * octave)
             for octave in range(octaves)
             for n in "c cis d dis e f fis g gis a ais b".split()]
    scale_names = np.roll(notes,
                          notes.index(base_note.lower().replace('#', 'is')))
    scale_notes = [scale_names[s] for s in intervals]
    return scale_notes


def note_name(number, scale):
    '''
    Transform a number to a note string, including np.nan as musical rests.
    '''
    if np.isnan(number):
        return "r"
    else:
        return scale[int(number)]


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
    for n in root_scaled:
        root.append(note_name(n, scale))
        third.append(note_name(n, scale))
        fifth.append(note_name(n, scale))

    seq1 = parse(" ".join(root))
    seq2 = parse(" ".join(third))
    seq3 = parse(" ".join(fifth))

    #chords = (seq1 * period) // (seq2 * period) // (seq3 * period)
    chords = seq1 // seq2 // seq3
    #return (chords | add({DURATION_64: chords[0][DURATION_64] * period}))
    return (chords | stretch(period))
    #return chords


def get_music(series, key='C', mode='major', octaves=2, instruments=None, period=12):
    '''
    Return a music generated from an inserted series.
    
    Parameters
    ----------
    series : an array that could be an 2d-array.
    
    key : Musical key. 
        Can be setted as a parameter while building scale.
    
    mode: Musica mode.
        'major' and 'minor' and 'pentatonic' are accetable parameters.
        
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
        
    period : parameter of chord_scaled function
    
    Returns
    -------
    midi_out : StringIO object.
        It can be written on a file or used by your way.
    
    Example
    -------
    >>> serie = np.random.random(10).reshape(2,5)
    array([[ 0.13536875,  0.42212475,  0.26360219,  0.30153336,  0.62150923],
       [ 0.49384405,  0.32503762,  0.85549822,  0.80212442,  0.70702405]])

    >>> get_music(serie, octaves=2, instruments=(0,23))
    <StringIO.StringIO instance at 0x7f98201c9d40>    
    
    '''
    midi_out = StringIO()

    series = np.array(series)
    scale = build_scale(key, mode, octaves)
    melodies = []
    for i in range(series.shape[0]):
        if all(np.isnan(series[i])):
            melody = []
            melodies.append(melody)
        else:
            notes = note_number(series[i], scale)
            melody = parse(' '.join([note_name(x, scale) for x in notes]))
            melodies.append(melody)
        
        #chords = chord_scaled(series, scale, period)
        # Transform it to a MIDI file with chords.
        #s = SMF([melody, chords], instruments=[0, 23])
    melodies = np.array(melodies)    
    if instruments == None:
        s = SMF(melodies)
    
    else:
        s = SMF(melodies, instruments)
    
    s.write(midi_out)
    
    return midi_out
