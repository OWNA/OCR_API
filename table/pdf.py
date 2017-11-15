from pyPdf import PdfFileReader
import json
import tabula

from table.line import TableLine, remove_outliers, contain_header_words
from table.labeller import MetaInfo, label_columns


def segment_pdf(filename):
    pdf = PdfFileReader(open(filename,'rb'))
    num_pages = pdf.getNumPages()
    pages = range(1, num_pages + 1)

    output = tabula.read_pdf(
        filename, spreadsheet=True, output_format='json', pages=pages)
    all_lines = []
    if not output:
        output = tabula.read_pdf(filename, output_format='json', pages=pages)
    if not output:
        return all_lines, []
    for output_table in output:
        for v in output_table['data']:
            if len(v) < 2:
                continue
            all_lines.append([])
            for c in v:
                text = c['text'].lstrip().rstrip()
                text = text.replace('\r', '')
                all_lines[-1].append(text)
    lines = remove_outliers(all_lines)
    meta_info = MetaInfo([])
    for line in all_lines:
        if contain_header_words(' '.join(line)) and not line in lines:
            meta_info = MetaInfo([], line)
    return lines, meta_info


def segment_and_label_pdf(filename):
    lines, meta_info = segment_pdf(filename)
    if not lines:
        return lines, []
    labels = label_columns(lines, meta_info)
    return lines, labels
