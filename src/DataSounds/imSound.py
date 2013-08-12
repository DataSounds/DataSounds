#!/usr/bin/env python

from StringIO import StringIO

import pygame.mixer
import matplotlib.pyplot as plt
from sebastian.lilypond.interp import parse
from sebastian.midi.write_midi import SMF, write

from DataSounds.sounds import build_scale, note_number, note_name


class ImageSound(object):
    '''
    Class to produce sonification interaction with mouse pointer on
    images. Generally 2D images are dificult to sonify while resulting
    a scientific meaning of sounds displayed.

    Trough imSound tool, the images now can be sonified and
    turns easier to get sounds of colors intensities.

    Example:
    --------
    import imSound
    import numpy as np

    data = np.arange(100).reshape(10,10)
    a = imSound.ImageSound(data)
    a.play_move()
    '''
    def __init__(self, data):
        '''
        data : image as numpy array.
        '''
        self.data = data

    def play_music(self, x, y):
        '''
        Generate sounds from data to be used for each coordinate.
        x and y are the coordinates of any image point.
        '''
        scale = build_scale('C', mode='major', octaves=1)
        notes = note_number(self.data, scale)
        if self.data.shape[1] > self.data.shape[0]:
            note = notes[y, x]
        else:
            note = notes[x, y]

        melody = parse(note_name(note, scale))
        midi_out = StringIO()
        write('Oc.midi', [melody])

        pygame.mixer.init()

        music = pygame.mixer.Sound('Oc.midi')
        pygame.mixer.music.load('Oc.midi')
        pygame.mixer.music.play()

    def play_move(self):
        '''
        return an plt.imshow of your loaded image as an imSond object.
        While mouse is on the image colors, a sound is displayed too.

        Example:
        --------
        import imSound
        import numpy as np

        data = np.arange(100).reshape(10,10)
        a = imSound.ImageSound(data)
        a.play_move()
        '''
        def on_move(event):
            x, y = event.xdata, event.ydata
            print('x = %s & y = %s' % (x, y))
            self.play_music(x, y)

        # pygame.mixer.stop()

        fig = plt.figure()
        fig.canvas.mpl_connect('motion_notify_event', on_move)
        ax = fig.add_subplot(111)
        ax.imshow(self.data)
        plt.show()
