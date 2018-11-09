import sys
import fitz
import PySimpleGUI as sg
from sys import exit
import tkinter as tk


# ------------------------------------------------------------------------------
# read the page data
# ------------------------------------------------------------------------------
def get_page(pno, dlist_tab, doc, zoom=0, max_screen_size=None):
    """
    Return a PNG image for a document page number. If zoom is other than 0, one of the 4 page quadrants are zoomed-in instead and the corresponding clip returned.
    """
    dlist = dlist_tab[pno]  # get display list
    if not dlist:  # create if not yet there
        dlist_tab[pno] = doc[pno].getDisplayList()
        dlist = dlist_tab[pno]
    r = dlist.rect  # page rectangle

    zoom_0 = 1
    if max_screen_size:
        zoom_0 = min(1, max_screen_size[0] / r.width, max_screen_size[1] / r.height)
        if zoom_0 == 1:
            zoom_0 = min(max_screen_size[0] / r.width, max_screen_size[1] / r.height)
    mat_0 = fitz.Matrix(zoom_0, zoom_0)

    mp = r.tl + (r.br - r.tl) * 0.5  # rect middle point
    mt = r.tl + (r.tr - r.tl) * 0.5  # middle of top edge
    ml = r.tl + (r.bl - r.tl) * 0.5  # middle of left edge
    mr = r.tr + (r.br - r.tr) * 0.5  # middle of right egde
    mb = r.bl + (r.br - r.bl) * 0.5  # middle of bottom edge
    mat = fitz.Matrix(2, 2)  # zoom matrix
    if zoom == 1:  # top-left quadrant
        clip = fitz.Rect(r.tl, mp)
    elif zoom == 4:  # bot-right quadrant
        clip = fitz.Rect(mp, r.br)
    elif zoom == 2:  # top-right
        clip = fitz.Rect(mt, mr)
    elif zoom == 3:  # bot-left
        clip = fitz.Rect(ml, mb)
    if zoom == 0:  # total page
        pix = dlist.getPixmap(alpha=False, matrix=mat_0)
    else:
        pix = dlist.getPixmap(alpha=False, matrix=mat, clip=clip)
    return pix.getPNGData()  # return the PNG image


def view_result_pdf(fname):
    document = fitz.open(fname)
    page_count = len(document)

    # storage for page display lists
    dlist_tab_param = [None] * page_count

    title = "Display of '%s', pages: %i" % (fname, page_count)

    # get physical screen dimension to determine the page image max size
    root = tk.Tk()
    max_width = root.winfo_screenwidth() - 20
    max_height = root.winfo_screenheight() - 135
    max_size = (max_width, max_height)
    root.destroy()
    del root

    window = sg.Window(title, return_keyboard_events=True, use_default_focus=False)

    cur_page = 0
    data = get_page(cur_page, dlist_tab_param, document, 0, max_size)  # show page 1 for start
    image_elem = sg.Image(data=data)
    goto = sg.InputText(str(cur_page + 1), size=(5, 1), do_not_clear=True)

    # Column layout
    col = [[sg.Text("Please enter one object and click submit; click OK when all changes are complete")],
           [sg.Text('Add'), sg.Input('ex. 4.00', key='_ADD_')],
           [sg.Text('Remove'), sg.Input('ex. 2', key='_REMOVE_')],
           [sg.Text('Reorder'), sg.Input('Please enter new order of labels', key='_REORDER_')],
           [sg.Submit(), sg.OK()]]

    layout =[
        [
            sg.Button('Prev'),
            sg.Button('Next'),
            sg.Text('Page:'),
            goto,
            sg.Text("Zoom:"),
            sg.Button('Top-L'),
            sg.Button('Top-R'),
            sg.Button('Bot-L'),
            sg.Button('Bot-R'),
        ],
        [image_elem, sg.Column(col)],
        [sg.Button('Complete')]
    ]

    window.Layout(layout)
    my_keys = ("Next", "Next:34", "Prev", "Prior:33", "Quit", "Top-L", "Top-R",
               "Bot-L", "Bot-R", "MouseWheel:Down", "MouseWheel:Up", "Submit", "OK")
    zoom_buttons = ("Top-L", "Top-R", "Bot-L", "Bot-R")

    old_page = 0
    old_zoom = 0  # used for zoom on/off
    # the zoom buttons work in on/off mode.

    while True:
        event, values = window.Read(timeout=100)
        zoom = 0
        force_page = False
        if event is None:
            break

        if event in ("Escape:27",) or event in ("Quit"):
            break
        if event[0] == chr(13):  # surprise: this is 'Enter'!
            try:
                cur_page = int(values[0]) - 1  # check if valid
                while cur_page < 0:
                    cur_page += page_count
            except:
                cur_page = 0  # this guy's trying to fool me
            goto.Update(str(cur_page + 1))

        elif event in ("Next", "Next:34", "MouseWheel:Down"):
            cur_page += 1
        elif event in ("Prev", "Prior:33", "MouseWheel:Up"):
            cur_page -= 1
        elif event == "Top-L":
            zoom = 1
        elif event == "Top-R":
            zoom = 2
        elif event == "Bot-L":
            zoom = 3
        elif event == "Bot-R":
            zoom = 4

        # sanitize page number
        if cur_page >= page_count:  # wrap around
            cur_page = 0
        while cur_page < 0:  # we show conventional page numbers
            cur_page += page_count

        # prevent creating same data again
        if cur_page != old_page:
            zoom = old_zoom = 0
            force_page = True

        if event in zoom_buttons:
            if 0 < zoom == old_zoom:
                zoom = 0
                force_page = True

            if zoom != old_zoom:
                force_page = True

        if force_page:
            data = get_page(cur_page, dlist_tab_param, document, zoom, max_size)
            image_elem.Update(data=data)
            old_page = cur_page
        old_zoom = zoom

        # update page number field
        if event in my_keys or not values[0]:
            goto.Update(str(cur_page + 1))
