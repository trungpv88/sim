import pygame
import thread


def play_closing_sound():
    path = "sound/door.ogg"
    thread_play(path)


def play_opening_sound():
    path = 'sound/knock.ogg'
    thread_play(path)


def play_buzz_sound():
    path = 'sound/doorbell.ogg'
    thread_play(path)


def play_message_sound():
    path = 'sound/chimeup.ogg'
    thread_play(path)


def thread_play(path):
    thread.start_new_thread(play, (path,))


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
    Get arguments for audio module in pygame
    :return:
    """
    pygame.mixer.init()
    freq, size, chan = pygame.mixer.get_init()
    return freq, size, chan


def init_mixer():
    """
    Initialize parameters for audio module in pygame
    :return:
    """
    try:
        buffer_size = 3072
        freq, size, chan = get_mixer_args()
        pygame.mixer.init(freq, size, chan, buffer_size)
    except:
        print "Can not initialize parameters for audio module."
        raise