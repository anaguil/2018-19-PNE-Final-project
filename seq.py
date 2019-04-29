class Seq:
    """A class for representing sequences"""
    def __init__(self, strbases):
        self.strbases = strbases

    def len(self):
        return len(self.strbases)

    def complement(self):
        complement_sequence = ""
        dictionary_bases = {"A":"T", "C":"G", "G":"C", "T":"A"}
        for base_1 in self.strbases:
            for base, complement in dictionary_bases.items():
                if base_1 == base:
                    complement_sequence += complement
        complement = Seq(complement_sequence)
        return complement

    def reverse(self):
        reverse_sequence = self.strbases[::-1]
        reverse = Seq(reverse_sequence)
        return reverse

    def count(self, base):
        return (self.strbases).count(base)

    def perc(self, base):
        tl = len(self.strbases)
        counter = self.strbases.count(base)
        perc = round((100 * counter)/ tl,1)
        return perc
