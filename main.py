import parserFunction
import dimensionFilter
import draw
from draw import BOX_UNIT
import GUI
import tkinter as tk
from tkinter import filedialog
import os
import sys
import PySimpleGUI as sg
import math

created_file = open('parsedPDF.txt', "r+", encoding="utf-8-sig")
created_file.truncate(0)
csv_text = open('Inspection Standard CSV.txt', 'w')
csv_text_path = os.path.abspath('Inspection Standard CSV.txt')
bubbled_pdf = open('Result.pdf', "wb")
bubbled_pdf_path = os.path.abspath("Result.pdf")

if len(sys.argv) == 1:
    pdf = sg.PopupGetFile('PDF Browser', 'PDF file to open', file_types=(("PDF Files", "*.pdf"),))
    if pdf is None:
        sg.Popup('Cancelling - no file supplied')
        exit(0)
else:
    pdf = sys.argv[1]

parserFunction.output_txt(pdf, created_file)

created_file.seek(0)
valid_dims = []
line_objects = []
coordinate_map = [[False for x in range(math.ceil(900/BOX_UNIT))] for y in range(math.ceil(1300/BOX_UNIT))]
dimensionFilter.file_input(created_file, valid_dims, line_objects, coordinate_map)

draw.print_dims(valid_dims, pdf, csv_text, bubbled_pdf, coordinate_map)
created_file.close()
csv_text.close()
bubbled_pdf.close()
os.startfile(csv_text_path)
GUI.view_result_pdf(bubbled_pdf_path)
