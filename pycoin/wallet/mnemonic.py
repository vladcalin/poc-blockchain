import os.path
import random

words_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'words.txt')


def mnemonic_generate_sequence(words=24):
    if words <= 0:
        raise ValueError('Invalid mnemonic word length: {}'.format(words))
    with open(words_file) as f:
        items = f.read().split('\n')
    system_rand = random.SystemRandom()
    return system_rand.sample(items, words)
