from string import ascii_uppercase
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
import io

BOX_UNIT = 12


def pdf_label(string, file, text_width, text_height, x, y, page_width, page_height):
    file.saveState()
    data = [[string]]
    t = Table(data, 1 * [text_width], 1 * [text_height])
    t.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('TEXTCOLOR', (0, 0), (-1, -1), colors.red),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.red),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.red),
                           ]))

    t.wrapOn(file, page_width, page_height)
    t.drawOn(file, x, y)
    file.restoreState()


def empty_space(array, figure, dim_x, dim_y, bubble_width, bubble_height):
    bubble_x1 = 1
    bubble_y1 = 1
    bubble_x2 = -1
    bubble_y2 = -1
    if figure == "LTTextBoxHorizontal":
        while bubble_x1 < 10:
            try:
                if array[dim_x + bubble_x1][dim_y] == False:
                    if bubble_width == 1:
                        array[dim_x + bubble_x1][dim_y]  = True
                        return dim_x + bubble_x1, dim_y
                    elif bubble_width == 3 and array[dim_x + bubble_x1 + 1][dim_y] == False and array[dim_x + bubble_x1 + 2][dim_y] == False:
                        array[dim_x + bubble_x1][dim_y] = True
                        return dim_x + bubble_x1, dim_y
                if array[dim_x + bubble_x2][dim_y] == False:
                    if bubble_width == 1:
                        array[dim_x + bubble_x2][dim_y] = True
                        return dim_x + bubble_x2, dim_y
                    elif bubble_width == 3 and array[dim_x + bubble_x2 + 1][dim_y] == False and array[dim_x + bubble_x2 + 2][dim_y] == False:
                        array[dim_x + bubble_x2][dim_y] = True
                        return dim_x + bubble_x2, dim_y
            except IndexError:
                print("Index out of range")
            bubble_x1 += 1
            bubble_x2 -= 1
        return dim_x, dim_y
    elif figure == "LTTextBoxVertical":
        while bubble_y1 < 10:
            try:
                if array[dim_x][dim_y + bubble_y1] == False:
                    if bubble_width == 1:
                        array[dim_x][dim_y + bubble_y1] = True
                        return dim_x, dim_y + bubble_y1
                    elif bubble_width == 3 and array[dim_x + 1][dim_y + bubble_y1] == False and array[dim_x + 2][dim_y + bubble_y1] == False:
                        array[dim_x][dim_y + bubble_y1] = True
                        return dim_x, dim_y + bubble_y1
                if array[dim_x][dim_y + bubble_y2] == False:
                    if bubble_width == 1:
                        array[dim_x][dim_y + bubble_y2] = True
                        return dim_x, dim_y + bubble_y2
                    elif bubble_width == 3 and array[dim_x + 1][dim_y + bubble_y2] == False and array[dim_x + 2][dim_y + bubble_y2] == False:
                        array[dim_x][dim_y + bubble_y2] = True
                        return dim_x, dim_y + bubble_y2
            except IndexError:
                print("Index out of range")
            bubble_y1 += 1
            bubble_y2 -= 1
        return dim_x, dim_y
    else:
        return dim_x, dim_y


def print_dims(dim_array, pdf_file, csv, outputStream):
    counter = 1
    max_page = 0
    packet = io.BytesIO()
    width, height = letter
    last_page = 0
    # create a new PDF with Reportlab
    c = canvas.Canvas(packet, pagesize=letter)

    for dimension1 in dim_array:
        if dimension1.page_number != last_page and last_page != 0:
            c.showPage()
        if dimension1.copies == 1:
            dimension1.label = str(counter)
            pdf_label(dimension1.label, c, BOX_UNIT, BOX_UNIT, dimension1.label_x, dimension1.label_y, width, height)
            csv.write(str(dimension1.label) + "," + str(dimension1.nominal) + "," + str(dimension1.tolerance))
            csv.write("\n")
        elif dimension1.copies > 1:
            duplicate = 0
            pdf_label(str(counter) + "A-" + ascii_uppercase[dimension1.copies-1], c, BOX_UNIT*3, BOX_UNIT, dimension1.label_x, dimension1.label_y, width, height)
            while duplicate < dimension1.copies:
                dimension1.label = str(counter) + ascii_uppercase[duplicate]
                csv.write(str(dimension1.label) + "," + str(dimension1.nominal) + "," + str(dimension1.tolerance))
                csv.write("\n")
                duplicate += 1
        counter += 1
        last_page = dimension1.page_number
        if dimension1.page_number > max_page:
            max_page = dimension1.page_number
    c.save()
    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(pdf_file)
    output = PdfFileWriter()
    page_no = 0
    print(max_page)
    while page_no < max_page:
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.getPage(page_no)
        page.mergePage(new_pdf.getPage(page_no))
        output.addPage(page)
        page_no += 1
    # finally, write "output" to a real file
    output.write(outputStream)

