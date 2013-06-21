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


def get_music(series, period=12, key='C', mode='major', octaves=2):
    '''
    Return a music generated from an inserted series.
    '''
    midi_out = StringIO()

    if all(np.isnan(series)):
        s = SMF([])
        s.write(midi_out)
    else:
        scale = build_scale(key, mode, octaves)

        notes = note_number(series, scale)
        melody = parse(' '.join([note_name(x, scale) for x in notes]))

        #chords = chord_scaled(series, scale, period)

        # Transform it to a MIDI file with chords.
        #s = SMF([melody, chords], instruments=[0, 23])
        s = SMF([melody])
        s.write(midi_out)

    return midi_out
