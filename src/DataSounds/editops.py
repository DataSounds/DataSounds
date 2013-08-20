#!/usr/bin/env python
# -*- coding: utf-8 -*-

from difflib import SequenceMatcher
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from sebastian.lilypond.interp import parse
from sebastian.midi.write_midi import SMF

from DataSounds.sounds import build_scale


def tone_down(note, scale):
    pos = scale.index(note[0])
    if pos <= 0:
        tone = scale[-1][0] + ','
    return tone


def tone_up(note, scale):
    pos = scale.index(note[0])
    tone = scale[(pos + 1) % len(scale)]
    if pos == len(scale) - 1:
        if ',' in note:
            note = note[:-1]
        else:
            tone = tone + "'"
    return tone


def get_music(a, b, key='C', mode='major'):
    midi_out = StringIO()

    scale = build_scale(key, mode, octaves=1)
    matcher = SequenceMatcher(None, a, b)

    tone = key.lower()
    melodies = [tone]
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        next_note = None
        if tag == 'replace':
            next_note = 'r'
        elif tag == 'equal':
            next_note = tone
        elif tag == 'delete':
            tone = tone_down(tone, scale)
            next_note = tone
        elif tag == 'insert':
            tone = tone_up(tone, scale)
            next_note = tone
        melodies += [next_note] * ((i2 - i1) or 1)
    s = SMF([parse(" ".join(melodies))])

    s.write(midi_out)
    return midi_out
