class NoMatchingOrder(Exception):
    pass


class MaxDurationReached(Exception):
    pass


class TooManyPriceParts(Exception):
    pass


class CellAssignmentOverlap(Exception):

    def __init__(self, cell1, cell2):
        self.cell1 = cell1
        self.cell2 = cell2

    def __str__(self):
        return 'Cell1: [{}], Cell2: [{}]'.format(self.cell1, self.cell2)


class MissingDescriptionPart(Exception):
    pass


class UnsupportedFileType(Exception):
    pass
