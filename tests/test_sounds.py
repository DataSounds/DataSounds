#!/usr/bin/env python

import numpy as np


from DataSounds.sounds import build_scale, note_number, note_name, get_music


def test_build_scale_major():
    scale = build_scale('C', 'major', 1)
    assert scale == 'c d e f g a b'.split()


def test_build_scale_minor():
    scale = build_scale('A', 'minor', 1)
    assert scale == 'a b c d e f g'.split()


def test_build_scale_pentatonic():
    scale = build_scale('C', 'pentatonic', 1)
    assert scale == ['c', 'd', 'e', 'g', 'a']


def test_build_scale_pentatonic_two_octaves():
    scale = build_scale('D', 'pentatonic', 2)
    assert scale == ['d', 'e', 'f#', 'a', 'b', "d'", "e'", "f#'", "a'", "b'"]


def test_note_number():
    scale = build_scale('C', 'major', 1)
    assert all(note_number([1, 2, 3, 4], scale) == [0, 2, 4, 6])


def test_build_note_name():
    scale = build_scale('C', 'major', 1)
    notes = note_number([1, 2, 3, 4, np.nan], scale)
    assert [note_name(x, scale) for x in notes] == ['c', 'e', 'g', 'b', 'r']


def test_get_music():
    series = [np.random.rand(24).reshape(2, 12), np.random.rand(30)]
    inst = [[0,23], [0]]
    testMuz = []
    for i, item in enumerate(series):
        testMuz.append(get_music(item, key='D', mode='pentatonic',
                  octaves=2, instruments=inst[i]))
    assert len(testMuz[0].getvalue()) == 281
    assert len(testMuz[1].getvalue()) == 314
