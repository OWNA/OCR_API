import mmh3
from nltk import ngrams
from util import generate_random_seeds, jaccard_similarity


class ShingledText:
    def __init__(self, text, random_seed=5, shingle_length=10, minhash_size=200):
        split_text = text.split()
        text = ''.join(split_text).lower()

        self.text = ngrams(text, shingle_length)
        self.minhash = None
        self.shingles = None

        if len(text) < shingle_length:
            return

        self.minhash = []
        self.shingles = []

        for shingle in ngrams(text, shingle_length):
            self.shingles.append(shingle)

        for hash_seed in generate_random_seeds(minhash_size, random_seed):
            min_value = float('inf')
            for shingle in ngrams(text, shingle_length):
                value = mmh3.hash(' '.join(shingle), hash_seed)
                min_value = min(min_value, value)
            self.minhash.append(min_value)

    def minhash_similarity(self, other_shingled_text):
        if self.minhash and other_shingled_text.minhash:
            return jaccard_similarity(set(self.minhash),
                                      set(other_shingled_text.minhash))
        else:
            return 0

    def similarity(self, other_shingled_text, debug=False):
        if self.shingles and other_shingled_text.shingles:
            return jaccard_similarity(set(self.shingles),
                                      set(other_shingled_text.shingles),
                                      debug)
        else:
            return 0
