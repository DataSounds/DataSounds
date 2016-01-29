#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

import numpy as np
from sys import platform
import subprocess
from DataSounds.external.sebastian.lilypond.interp import parse
from DataSounds.external.sebastian.midi.write_midi import SMF
from DataSounds.external.sebastian.core.transforms import stretch
from DataSounds.external.sebastian.core import notes


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
    Build a scale from a key note.

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
    Transform a number to a note string, including np.nan as
    musical rests.
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
        "Cb" for C flat, or any other key note (e.g. D, E, F, G, A, B).

    mode : Music mode.
        'major', 'minor' and 'pentatonic' are accetable parameters.
        More options of modes on `build_scale`.

    octaves : Number of available scales for musical construction.
        As higher are the octaves higher pitch differeneces will occur
        while representing your data.

    instruments : list of MIDI instruments.
        General MIDI Level 1 Instrument Patch Map can be found at:
        http://en.wikipedia.org/wiki/General_MIDI
        Acoustic Grand Piano is the default usage value '[0]' if any
        instruments are declared.
        Fewer examples:
        [0] Acoustic Grand Piano
        [18] Rock Organ
        [23] Tango Accordion
        [32] Acoustic Bass
        [73] Flute

        Complete list:
        +---------------------------------------------------+
        |Piano                                              |
        +===================================================+
        | 0 Acoustic Grand Piano  | 1 Bright Acoustic Piano |
        +-------------------------+-------------------------+
        | 2 Electric Grand Piano  | 3 Honky-tonk Piano      |
        +-------------------------+-------------------------+
        | 4 Electric Piano 1      | 5 Electric Piano 2      |
        +-------------------------+-------------------------+
        | 6 Harpsichord           | 7 Clavinet              |
        +-------------------------+-------------------------+

        +---------------------------------------------------+
        |Chromatic Percussion                               |
        +===================================================+
        | 8 Celesta               | 9 Glockenspiel          |
        +-------------------------+-------------------------+
        | 10 Music Box            | 11 Vibraphone           |
        +-------------------------+-------------------------+
        | 12 Marimba              | 13 Xylophone            |
        +-------------------------+-------------------------+
        | 14 Tubular Bells        | 15 Dulcimer             |
        +-------------------------+-------------------------+

        +---------------------------------------------------+
        |Organ                                              |
        +===================================================+
        | 16 Drawbar Organ        | 17 Percussive Organ     |
        +-------------------------+-------------------------+
        | 18 Rock Organ           | 19 Church Organ         |
        +-------------------------+-------------------------+
        | 20 Reed Organ           | 21 Accordion            |
        +-------------------------+-------------------------+
        | 22 Harmonica            | 23 Tango Accordion      |
        +-------------------------+-------------------------+

        +-----------------------------------------------------+
        |Guitar                                               |
        +=====================================================+
        | 24 Acoustic Guitar(nylon)| 25 Acoustic Guitar(steel)|
        +--------------------------+--------------------------+
        | 26 Electric Guitar(jazz) | 27 Electric Guitar(clean)|
        +--------------------------+--------------------------+
        | 28 Electric Guitar(muted)| 29 Overdriven Guitar     |
        +--------------------------+--------------------------+
        | 30 Distortion Guitar     | 31 Guitar Harmonics      |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        |Bass                                                 |
        +=====================================================+
        | 32 Acoustic Bass         | 32 Electric Bass (finger)|
        +--------------------------+--------------------------+
        | 34 Electric Bass (pick)  | 35 Fretless Bass         |
        +--------------------------+--------------------------+
        | 36 Slap Bass 1           | 37 Slap Bass 2           |
        +--------------------------+--------------------------+
        | 38 Synth Bass 1          | 39 Synth Bass 2          |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        |Strings                                              |
        +=====================================================+
        | 40 Violin                | 41 Viola                 |
        +--------------------------+--------------------------+
        | 42 Cello                 | 43 Contrabass            |
        +--------------------------+--------------------------+
        | 44 Tremolo String        | 45 Pizzicato Strings     |
        +--------------------------+--------------------------+
        | 46 Orchestral Harp       | 47 Timpani               |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        |Enseble                                              |
        +=====================================================+
        | 48 String Ensemble 1     | 49 String Ensemble 2     |
        +--------------------------+--------------------------+
        | 50 Synth Strings 1       | 51 Synth Strings 2       |
        +--------------------------+--------------------------+
        | 52 Choir Aahs            | 53 Voice Oohs            |
        +--------------------------+--------------------------+
        | 54 Synth Choir           | 55 Orchestra Hit         |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        |Brass                                                |
        +=====================================================+
        | 56 Trumpet               | 57 Trombone              |
        +--------------------------+--------------------------+
        | 58 Tuba                  | 59 Muted Trumpet         |
        +--------------------------+--------------------------+
        | 60 French Horn           | 61 Brass Section         |
        +--------------------------+--------------------------+
        | 62 Synth Brass 1         | 63 Synth Brass 2         |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        | Reed                                                |
        +=====================================================+
        | 64 Soprano Sax           | 65 Alto Sax              |
        +--------------------------+--------------------------+
        | 66 Tenor Sax             | 67 Baritone Sax          |
        +--------------------------+--------------------------+
        | 68 Oboe                  | 69 English Horn          |
        +--------------------------+--------------------------+
        | 70 Bassoon               | 71 Clarinet              |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        | Pipe                                                |
        +=====================================================+
        | 72 Piccolo               | 73 Flute                 |
        +--------------------------+--------------------------+
        | 74 Recorder              | 75 Pan Flute             |
        +--------------------------+--------------------------+
        | 76 Blown bottle          | 77 Shakuhachi            |
        +--------------------------+--------------------------+
        | 78 Whistle               | 79 Ocarina               |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        | Synth Lead                                          |
        +=====================================================+
        | 80 Lead 1 (square)       | 81 Lead 2 (sawtooth)     |
        +--------------------------+--------------------------+
        | 82 Lead 3 (calliope)     | 83 Lead 4 chiff          |
        +--------------------------+--------------------------+
        | 84 Lead 5 (charang)      | 85 Lead 6 (voice)        |
        +--------------------------+--------------------------+
        | 86 Lead 7 (fifths)       | 87 Lead 8 (bass + lead)  |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        | Synth Pad                                           |
        +=====================================================+
        | 88 Pad 1 (new age)       | 89 Pad 2 (warm)          |
        +--------------------------+--------------------------+
        | 90 Pad 3 (polysynth)     | 91 Pad 4 (choir)         |
        +--------------------------+--------------------------+
        | 92 Pad 5 (bowed)         | 93 Pad 6 (metallic)      |
        +--------------------------+--------------------------+
        | 94 Pad 7 (halo)          | 95 Pad 8 (sweep)         |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        | Synth Effects                                       |
        +=====================================================+
        | 96 FX 1 (rain)           | 97 FX 2 (soundtrack)     |
        +--------------------------+--------------------------+
        | 98 FX 3 (crystal)        | 99 FX 4 (atmosphere)     |
        +--------------------------+--------------------------+
        | 100 FX 5 (brightness)    | 101 FX 6 (goblins)       |
        +--------------------------+--------------------------+
        | 102 FX 7 (echoes)        | 103 FX 8 (sci-fi)        |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        | Ethnic                                              |
        +=====================================================+
        | 104 Sitar                | 105 Banjo                |
        +--------------------------+--------------------------+
        | 106 Shamisen             | 107 Koto                 |
        +--------------------------+--------------------------+
        | 108 Kalimba              | 109 Bagpipe              |
        +--------------------------+--------------------------+
        | 110 Fiddle               | 111 Shanai               |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        | Percussive                                          |
        +=====================================================+
        | 112 Tinkle Bell          | 113 Agogo                |
        +--------------------------+--------------------------+
        | 114 Steel Drums          | 115 Woodblock            |
        +--------------------------+--------------------------+
        | 116 Taiko Drum           | 117 Melodic Tom          |
        +--------------------------+--------------------------+
        | 118 Synth Drum           | 119 Reverse Cymbal       |
        +--------------------------+--------------------------+

        +-----------------------------------------------------+
        |Sound effects                                        |
        +=====================================================+
        | 120 Guitar Fret Noise    | 121 Breath Noise         |
        +--------------------------+--------------------------+
        | 122 Seashore             | 123 Bird Tweet           |
        +--------------------------+--------------------------+
        | 124 Telephone Ring       | 125 Helicopter           |
        +--------------------------+--------------------------+
        | 126 Applause             | 127 Gunshot              |
        +--------------------------+--------------------------+

    period : int
        parameter of chord_scaled function.

    Returns
    -------
    midi_out : BytesIO object.
        It can be written on a file or used by your way.

    Example
    -------
    >>> data = np.random.random(10).reshape(2,5)
    array([[ 0.13536875,  0.42212475,  0.26360219,  0.30153336,
            0.62150923],
            [ 0.49384405,  0.32503762,  0.85549822,  0.80212442,
            0.70702405]])

    >>> get_music(data, octaves=2, instruments=(0,23))
    <io.BytesIO at 0x7f98201c9d40>

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
    muz_file = open(str(name)+'.midi', 'wb')
    muz_file.write(BytesIo.getvalue())
    muz_file.close()

def play(file):
    """Use system program to play MIDI files
    We try here to use timidity as default software. Please, see `timidity
    documentation<http://timidity.sourceforge.net/install.html>`_.

    Parameters
    ----------
    name : str
        name of file

    Example
    -------
    >>> file = "music.mid"
    >>> play(file)
   """
    # linux
    if platform == "linux" or platform == "linux2":
        if subprocess.call("timidity") == 0:
            try:
                subprocess.call(["timidity", str(file)])
            except OSError:
                print("You do not have appropriate software installed to "
                    "play MIDI files. See Timidity instalation "
                    "http://timidity.sourceforge.net/install.html")

        else:
            try: subprocess.call(["totem", str(file)])
            except OSError:
                print("Maybe you do not have 'fluid-soundfont-gm' installed "
                    "to use it with totem.")

    # MAC OS X
    elif _platform == "darwin":
        if subprocess.call("timidity") == 0:
            try:
                subprocess.call(["timidity", str(file)])
            except:
                print("You do not have appropriate software installed to "
                    "play MIDI files. See Timidity instalation "
                    "http://timidity.sourceforge.net/install.html")
        else:
            try:
                subprocess.call(["open", str(file)])
            except OSError:
                print("Seems that your 'open' program cannot play MIDI files")
    # Windows
    elif _platform == "win32":
        try:
            subprocess.call(["timidity", str(file)])
        except OSError:
            print("You do not have appropriate software installed to "
                  "play MIDI files. See Timidity instalation "
                  "http://timidity.sourceforge.net/install.html")
