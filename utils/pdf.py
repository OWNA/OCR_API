import numpy as np
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure
from pdfminer.layout import LTChar, LTText, LTAnno


from utils.files import SimpleWord


rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)



class PDFFile(object):

    def __init__(self, filename, offset=0):
        self.filename = filename
        self.offset = offset
        self.page_count = 0
        self.words = []

    def parse_layout(self, layout):
        """Function to recursively parse the layout tree."""
        # The dimensions are given in points (1 / 72 of an inch)
        # We transform it to pixels in such a way that the smallest
        # dimension (height or width) measures 2448 in width.
        for lt_obj in layout:
            if (isinstance(lt_obj, LTTextLine)):
                text = lt_obj.get_text().lstrip().rstrip()
                x0, y0, x1, y1 = np.array(lt_obj.bbox)
                xL = x0 * self.scale
                xR = x1 * self.scale
                yT = (self.height - y1) * self.scale
                yB = (self.height - y0) * self.scale
                if text:
                    page_num = self.offset + self.page_count
                    self.words.append(SimpleWord(
                        text, xL, xR, yT, yB, page_num))
            elif (isinstance(lt_obj, LTFigure) or
                  isinstance(lt_obj, LTTextBox)):
                self.parse_layout(lt_obj)


    def parse(self):
        fp = open(self.filename, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            layout = device.get_result()
            _, _, width, height = layout.bbox
            min_dimension = min(width, height)
            self.width = width
            self.height = height
            self.scale = 2448 / min_dimension
            self.pixels_per_inch = 72 * self.scale
            self.parse_layout(layout)
            self.page_count += 1
        fp.close()


    def debug(self):
        for word in self.words:
            print word


if __name__ == '__main__':
    pdf_file = PDFFile('data/production/structure/138/file.pdf')
    pdf_file.parse()
    pdf_file.debug()
