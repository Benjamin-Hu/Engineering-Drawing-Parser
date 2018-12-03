# run.py forked from wxPython

import wx
import sys
from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel

# ----------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent, edit_mode):
        # Setting up panel and sizers
        wx.Panel.__init__(self, parent, -1)
        hsizer = wx.BoxSizer( wx.HORIZONTAL )
        vsizer = wx.BoxSizer( wx.VERTICAL )

        # Special wxpython PDF button panel
        self.buttonpanel = pdfButtonPanel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        # PDF viewer
        self.viewer = pdfViewer(self,wx.ID_ANY,wx.DefaultPosition,wx.DefaultSize,wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)

        # Adding button panel and viewer to vertical sizer
        vsizer.Add(self.buttonpanel, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        vsizer.Add(self.viewer, 1, wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        # Adding relevant buttons (or none at all)
        loadbutton = wx.Button(self, wx.ID_ANY, "Load PDF file", wx.DefaultPosition, wx.DefaultSize, 0)
        vsizer.Add(loadbutton, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        if edit_mode:
            addbutton = wx.Button(self, wx.ID_ANY, "Add Dimension",
                                wx.DefaultPosition, wx.DefaultSize, 0 )
            vsizer.Add(addbutton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Completing sizing setup
        hsizer.Add(vsizer, 1, wx.GROW|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

        # Introduce button panel and viewer to each other
        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel

        # Binding all of the buttons
        self.Bind(wx.EVT_BUTTON, self.OnLoadButton, loadbutton)
        if edit_mode:
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
        self.viewer.Bind(wx.EVT_LEFT_DOWN, lambda event: self.AddLeftClick(event, add_list))

    # Able to take any relevant lists
    def AddLeftClick(self, event, point_list):
        panel_point = self.viewer.ScreenToClient(wx.GetMousePosition())
        pointwx = wx.Point(0,0)
        scrolled = self.viewer.CalcUnscrolledPosition(pointwx)
        print(scrolled)
        print(panel_point)
        scrolled.__iadd__(panel_point)
        print(scrolled)
        point_list.append(scrolled)
        print(point_list)

# ----------------------------------------------------------------------


class FullApp(wx.App):
    def __init__(self):
        # Setting up the app
        wx.App.__init__(self, redirect=False)
        self.frame = wx.Frame(None, -1, "Engineering Drawing Parser", size=(600, 500))

        # Creating a menu bar and proper window features
        self.frame.CreateStatusBar()
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(wx.ID_EXIT, "Exit\tCtrl-Q", "Exit demo")
        self.Bind(wx.EVT_MENU, self.OnExitApp, item)
        menuBar.Append(menu, "&File")
        self.frame.SetMenuBar(menuBar)
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        # User begins to choose their options and files
        dlg = wx.FileDialog(self.frame, wildcard=r"*.pdf")
        if dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            upload_file = dlg.GetPath()
            wx.EndBusyCursor()
        dlg.Destroy()

        # Setting up the panel now that requested option is known
        panel = TestPanel(self.frame, True)
        self.frame.Show(True)

    def OnExitApp(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()

# ----------------------------------------------------------------------


# Print versions for debugging purposes
print("Python %s" % sys.version)
print("wx.version: %s" % wx.version())

app = FullApp()
app.MainLoop()