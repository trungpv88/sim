import pygame
import thread
import os.path


def play_closing_sound():
    thread_play("sound/door.ogg")


def play_opening_sound():
    thread_play("sound/knock.ogg")


def play_buzz_sound():
    thread_play("sound/doorbell.ogg")


def play_message_sound():
    thread_play("sound/chimeup.ogg")


def thread_play(path):
    try:
        if os.path.exists(path):
            thread.start_new_thread(play, (path,))
    except:
        raise


def play(path):
    try:
        init_mixer()
        pygame.init()
        clock = pygame.time.Clock()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            clock.tick(1000)
    except:
        print "Can not play audio file"
        raise


def get_mixer_args():
    """
    Get arguments for audio module
    :return:
    """
    pygame.mixer.init()
    freq, size, chan = pygame.mixer.get_init()
    return freq, size, chan


def init_mixer():
    """
    Initialize parameters for audio module
    :return:
    """
    try:
        buffer_size = 3072
        freq, size, chan = get_mixer_args()
        pygame.mixer.init(freq, size, chan, buffer_size)
    except:
        print "Can not initialize parameters for audio module."
        raise