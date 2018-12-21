from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextBoxVertical, LTTextBoxHorizontal
import math


def parse_layout(page, layout, output):
    # Function to parse layout
    for lt_obj in layout:
        output.write(lt_obj.__class__.__name__)  # Print obj name
        output.write("\n")                       # Print new line
        output.write(str(page))                  # Print page number
        output.write("\n")
        output.write(str(lt_obj.bbox))           # Print box coords
        output.write("\n")                       # Print new line
        if isinstance(lt_obj, LTTextBoxVertical):        # Only print text boxes
            output.write(lt_obj.get_text())      # Print text
            output.write("\n")                   # Print new line
        elif isinstance(lt_obj, LTTextBoxHorizontal):    # Only print text boxes
            output.write(lt_obj.get_text())      # Print text
            output.write("\n")                   # Print new line


def output_txt(file_path, save_file):
    fp = open(file_path, 'rb')   # Open specified file
    parser = PDFParser(fp)      # Use PDFParser
    doc = PDFDocument(parser)   # Use PDFDocument
    rsrcmgr = PDFResourceManager()  # ???
    laparams = LAParams(1.0/1e256, 2.0, 1.0/1e256, 0.1, 0.5, True, True)    # Sets parameters for parsing
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    page_number = 1
    for page in PDFPage.create_pages(doc):
        sizeArray = page.mediabox
        page_width = sizeArray[2]
        page_height = sizeArray[3]
        print(page_width, page_height)
        interpreter.process_page(page)
        layout = device.get_result()
        parse_layout(page_number, layout, save_file)
        page_number += 1
    return page_width, page_height
