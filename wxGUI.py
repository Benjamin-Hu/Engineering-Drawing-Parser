# run.py forked from wxPython

import wx
import sys
from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel
import wx.adv

# ----------------------------------------------------------------------


class menuPanel(wx.Panel):
    def __init__(self, parent):
        # Setting up panel and sizers
        wx.Panel.__init__(self, parent, -1)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Adding relevant buttons and images
        image = wx.Image('logo.png', wx.BITMAP_TYPE_ANY)
        image.Rescale(200, 200, wx.IMAGE_QUALITY_HIGH)
        imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(image))
        vsizer.Add(imageBitmap, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        lineDivider = wx.StaticLine(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LI_HORIZONTAL)
        vsizer.Add(lineDivider, 0, wx.ALL | wx.EXPAND, 5)

        self.parseButton = wx.Button(self, wx.ID_ANY, "Parse a Bubbled Drawing", wx.DefaultPosition, wx.DefaultSize, 0 )
        vsizer.Add(self.parseButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.manualButton = wx.Button(self, wx.ID_ANY, "Manually Bubble a Drawing", wx.DefaultPosition, wx.DefaultSize, 0)
        vsizer.Add(self.manualButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.autoButton = wx.Button(self, wx.ID_ANY, "Automatically Bubble a Drawing", wx.DefaultPosition, wx.DefaultSize, 0)
        vsizer.Add(self.autoButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.aboutButton = wx.Button(self, wx.ID_ANY, "About", wx.DefaultPosition, wx.DefaultSize, 0)
        vsizer.Add(self.aboutButton, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        # Completing sizing setup
        hsizer.Add(vsizer, 1, wx.GROW|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

# ----------------------------------------------------------------------


class viewerPanel(wx.Panel):
    def __init__(self, parent, edit_mode):
        # Setting up panel and sizers
        wx.Panel.__init__(self, parent, -1)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)

        # Special wxpython PDF button panel
        self.buttonpanel = pdfButtonPanel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        # PDF viewer
        self.viewer = pdfViewer(self,wx.ID_ANY,wx.DefaultPosition,wx.DefaultSize,wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)

        # Adding button panel and viewer to vertical sizer
        self.vsizer.Add(self.buttonpanel, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        self.vsizer.Add(self.viewer, 1, wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        # Adding relevant buttons (or none at all)
        self.loadbutton = wx.Button(self, wx.ID_ANY, "Load PDF file", wx.DefaultPosition, wx.DefaultSize, 0)
        self.vsizer.Add(self.loadbutton, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.addbutton = wx.Button(self, wx.ID_ANY, "Add Dimension", wx.DefaultPosition, wx.DefaultSize, 0)
        self.vsizer.Add(self.addbutton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.addbutton.Hide()

        # Completing sizing setup
        self.hsizer.Add(self.vsizer, 1, wx.GROW|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        self.SetSizer(self.hsizer)
        self.SetAutoLayout(True)

        # Introduce button panel and viewer to each other
        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel

        # Binding all of the buttons
        self.Bind(wx.EVT_BUTTON, self.OnLoadButton, self.loadbutton)
        add_points = []
        self.addbutton.Bind(wx.EVT_BUTTON, lambda event: self.OnAddButton(event, add_points))

    def OnLoadButton(self, event):
        dlg = wx.FileDialog(self, wildcard=r"*.pdf")
        if dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            self.viewer.LoadFile(dlg.GetPath())
            wx.EndBusyCursor()
        dlg.Destroy()

    def OnAddButton(self, event, add_list):
        print("Debug: Adding values...")
        print(self.viewer.Xpagepixels, self.viewer.Ypagepixels)
        self.viewer.Bind(wx.EVT_LEFT_DOWN, lambda event: self.AddLeftClick(event, add_list))

    # Able to take any relevant lists
    def AddLeftClick(self, event, point_list):
        panel_point = self.viewer.ScreenToClient(wx.GetMousePosition())
        pointwx = wx.Point(0,0)
        scrolled = self.viewer.CalcUnscrolledPosition(pointwx)
        scrolled.__iadd__(panel_point)
        if scrolled.x < self.viewer.Xpagepixels and scrolled.y < self.viewer.Ypagepixels*self.viewer.numpages:
            print(scrolled)
            point_list.append(scrolled)

# ----------------------------------------------------------------------


class FullFrame(wx.Frame):
    def __init__(self):
        # Setting up the app
        wx.Frame.__init__(self, parent=None, title="Engineering Drawing Parser", size=(1024, 576))
        self.CenterOnScreen()

        # Creating a menu bar and proper window features
        self.CreateStatusBar()
        menuBar = wx.MenuBar()
        menuOption = wx.Menu()
        self.SetMenuBar(menuBar)

        menuBar.Append(menuOption, "&File")
        aboutMe = menuOption.Append(wx.ID_ANY, "&About")
        self.Bind(wx.EVT_MENU, self.OnAboutBox, aboutMe)
        mainMenu = menuOption.Append(wx.ID_ANY, "&Main Menu\tEsc")
        self.Bind(wx.EVT_MENU, self.OnMainMenu, mainMenu)
        exit = menuOption.Append(wx.ID_EXIT, "Exit\tCtrl+Q", "Exit Program")
        self.Bind(wx.EVT_MENU, self.OnExitApp, exit)
        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        # Setting up main menu and viewer panels
        self.menu = menuPanel(self)
        self.viewPanel = viewerPanel(self, None)
        self.viewPanel.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.menu, 1, wx.EXPAND)
        self.sizer.Add(self.viewPanel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        # Binding relevant buttons from lower level panels
        edit_mode = None
        self.menu.manualButton.Bind(wx.EVT_BUTTON, lambda event: self.OnManualButton(event, edit_mode))
        self.menu.parseButton.Bind(wx.EVT_BUTTON, lambda event: self.OnParseButton(event, edit_mode))
        self.Bind(wx.EVT_BUTTON, self.OnAboutBox, self.menu.aboutButton)

        '''
        dlg = wx.FileDialog(self.viewFrame, wildcard=r"*.pdf")
        if dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            upload_file = dlg.GetPath()
            wx.EndBusyCursor()
        dlg.Destroy()
        '''

        # Setting up the panel now that requested option is known



    def OnExitApp(self, evt):
        self.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()

    def OnAboutBox(self, event):
        description = """
        The Engineering Drawing Parser is a cross-platform tool
        used to interpret bubbled engineering drawings and specifications,
        as well as create bubbled drawings. Features include automatic
        recognition of dimensions, auto-bubbling and exporting .csv data.
        """
        licence = """
        The Engineering Drawing Parser is free software; you can redistribute
        it and/or modify it under the terms of the GNU General Public License as
        published by the Free Software Foundation.
        """
        info = wx.adv.AboutDialogInfo()
        info.SetIcon(wx.Icon('logo.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Engineering Drawing Parser')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetWebSite('https://github.com/Benjamin-Hu/Engineering-Drawing-Parser')
        info.SetLicence(licence)
        info.AddDeveloper('Benjamin Hu')

        wx.adv.AboutBox(info)

    def OnMainMenu(self, event):
        self.viewPanel.Hide()
        self.menu.Show()
        self.Layout()

    def OnManualButton(self, event, edit):
        edit = True
        self.viewPanel.addbutton.Show()
        self.viewPanel.Show()
        self.menu.Hide()
        self.Layout()

    def OnParseButton(self, event, edit):
        edit = False
        self.viewPanel.addbutton.Hide()
        self.viewPanel.Show()
        self.menu.Hide()
        self.Layout()

# ----------------------------------------------------------------------


# Print versions for debugging purposes
print("Python %s" % sys.version)
print("wx.version: %s" % wx.version())

app = wx.App(False)
frame = FullFrame()
frame.Show()
app.MainLoop()