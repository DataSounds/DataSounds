#!/usr/bin/env python

from DataSounds.sounds import build_scale


def test_build_scale_major():
    scale = build_scale('C', 'major', 1)
    assert any('is' in note for note in scale) is False


def test_build_scale_minor():
    scale = build_scale('A', 'minor', 1)
    assert any('is' in note for note in scale) is False
