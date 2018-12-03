# Forked from wxPython

import wx
import sys

try:
    from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel
    havePyPdf = True
except ImportError:
    havePyPdf = False

# ----------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        hsizer = wx.BoxSizer( wx.HORIZONTAL )
        vsizer = wx.BoxSizer( wx.VERTICAL )
        self.buttonpanel = pdfButtonPanel(self, wx.ID_ANY,
                                wx.DefaultPosition, wx.DefaultSize, 0)
        vsizer.Add(self.buttonpanel, 0,
                                wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        self.viewer = pdfViewer( self, wx.ID_ANY, wx.DefaultPosition,
                                wx.DefaultSize, wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
        vsizer.Add(self.viewer, 1, wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        loadbutton = wx.Button(self, wx.ID_ANY, "Load PDF file",
                                wx.DefaultPosition, wx.DefaultSize, 0 )
        vsizer.Add(loadbutton, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        addbutton = wx.Button(self, wx.ID_ANY, "Add Dimension",
                                wx.DefaultPosition, wx.DefaultSize, 0 )
        vsizer.Add(addbutton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        hsizer.Add(vsizer, 1, wx.GROW|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

        # introduce buttonpanel and viewer to each other
        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel

        self.Bind(wx.EVT_BUTTON, self.OnLoadButton, loadbutton)

        add_points = []
        addbutton.Bind(wx.EVT_BUTTON, lambda event: self.OnAddButton(event, add_points))

    def OnLoadButton(self, event):
        dlg = wx.FileDialog(self, wildcard=r"*.pdf")
        if dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            self.viewer.LoadFile(dlg.GetPath())
            wx.EndBusyCursor()
        dlg.Destroy()

    def OnAddButton(self, event, add_list):
        print("Adding values...")
        self.viewer.Bind(wx.EVT_LEFT_DOWN, lambda event: self.ChooseLeftClick(event, add_list))

    def ChooseLeftClick(self, event, point_list):
        panel_point = self.viewer.ScreenToClient(wx.GetMousePosition())
        pointwx = wx.Point(0,0)
        scrolled = self.viewer.CalcUnscrolledPosition(pointwx)
        print(scrolled)
        print(panel_point)
        scrolled.__iadd__(panel_point)
        print(scrolled)
        point_list.append(scrolled)
        print(point_list)

# ---------------------------------------------------------------------


def runTest(frame, nb, log):
    if havePyPdf:
        win = TestPanel(nb, log)
        return win
    else:
        from wx.lib.msgpanel import MessagePanel
        win = MessagePanel(nb,
                           'This demo requires either the\n'
                           'PyMuPDF see http://pythonhosted.org/PyMuPDF\n'
                           'or\n'
                           'PyPDF2 see http://pythonhosted.org/PyPDF2\n'
                           'package installed.\n',
                           'Sorry', wx.ICON_WARNING)
        return win

# ----------------------------------------------------------------------


class FullApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        self.frame = wx.Frame(None, -1, "Engineering Drawing Parser", size=(600, 500))
        self.frame.CreateStatusBar()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(wx.ID_EXIT, "Exit\tCtrl-Q", "Exit demo")
        self.Bind(wx.EVT_MENU, self.OnExitApp, item)
        menuBar.Append(menu, "&File")

        self.frame.SetMenuBar(menuBar)
        panel = TestPanel(self.frame)
        self.frame.Show(True)
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

    def OnExitApp(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()

# ----------------------------------------------------------------------


# stuff for debugging
print("Python %s" % sys.version)
print("wx.version: %s" % wx.version())

app = FullApp()
app.MainLoop()