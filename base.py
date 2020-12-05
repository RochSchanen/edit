# 'base.py'
# content: The App/Frame/Panel classes.
# author: Roch schanen
# created: 2020 Mars 21
# repository: https://github.com/RochSchanen/rochpygui

# todo: should I use "BufferedPaintDC" instead of "DCPaint" at #1

# wxpython: https://www.wxpython.org/
# import wx

from sys import exit

from wx import Panel, Frame, App, Exit
from wx import DefaultPosition, DefaultSize
from wx import ID_ANY, NO_BORDER, DEFAULT_FRAME_STYLE
from wx import RESIZE_BORDER, MAXIMIZE_BOX
from wx import EVT_PAINT, EVT_KEY_DOWN
from wx import WXK_ESCAPE
from wx import PaintDC

# simple Panel class
class _basePanel(Panel):
    # superseed the __init__ method
    def __init__(self, parent):
        # call parent class __init__()
        Panel.__init__(
            self,
            parent = parent,
            id     = ID_ANY,
            pos    = DefaultPosition,
            size   = DefaultSize,
            style  = NO_BORDER,
            name   = "")
        # BackgroundBitmap
        self.BackgroundBitmap = None
        # bind paint event
        self.Bind(EVT_PAINT, self._OnPaint)
        # done
        return

    def _OnPaint(self, event):
        # redraw if BackgroundBitmap is defined
        if self.BackgroundBitmap: 
            dc = PaintDC(self) #1
            dc.DrawBitmap(self.BackgroundBitmap, 0, 0)
        return

# simple Frame class
class _baseFrm(Frame):
    # superseed the __init__ method
    def __init__(self):
        # call parent class __init__()
        Frame.__init__(
            self,
            parent = None,
            id     = ID_ANY,
            title  = "",
            pos    = DefaultPosition,
            size   = DefaultSize,
            style  = DEFAULT_FRAME_STYLE
                    ^ RESIZE_BORDER
                    ^ MAXIMIZE_BOX,
            name   = "")
        # Create panel
        self.Panel = _basePanel(self)
        # done
        return

# set _ESCAPE = True to allow the ESCAPE key
#  when developping projects. The default is:
_ESCAPE = False

import wx

# simple App class
class App(App):

    # default user init method
    def OnInit(self):
        # create a reference to Self ?
        self.App = self
        # create and show Frame
        self.Frame = _baseFrm()     
        # create a reference to Panel
        self.Panel = self.Frame.Panel
        # call user Start()
        self.Start()
        # adjust widow size to BackgroundBitmap size
        if self.Frame.Panel.BackgroundBitmap:
            w, h = self.Frame.Panel.BackgroundBitmap.GetSize()
            self.Frame.SetClientSize((w, h))
        # bind key event to exit() on ESCAPE pressed event
        self.Bind(EVT_KEY_DOWN, self._OnKeyDown)
        # now show the frame
        self.Frame.Show(True)
        # done
        return True

    # User's code:
    def Start(self):
        # User module should Superseeded this method 
        pass

    # Exit on Esc: Debugging/Development stage
    def _OnKeyDown(self, event):
        key = event.GetKeyCode()
        if _ESCAPE:
            if key == WXK_ESCAPE:
                self._quitRequest(event)
                return
        self.OnKeyDown(event)
        event.Skip() # forward event
        return

    def OnKeyDown(self, event):
        pass

    # def __del__(self):
    #     return

    def _quitRequest(self, event):
        exit()
        return


if __name__ == "__main__":

    # allow exit() through the escape key
    _ESCAPE = True

    class App(App):

        def Start(self):
            # self.SetMenuBar()
            return

    App().MainLoop()











    # def SetMenuBar(self):
        
    #     M1 = wx.Menu()
        
    #     M1.Append(
    #         wx.ID_NEW,
    #         "&New File Name",
    #         "select a new filename",
    #         kind = wx.ITEM_NORMAL)

    #     M1.Append(
    #         wx.ID_SAVE,
    #         "&Save Config File",
    #         "save current configuration to file",
    #         kind = wx.ITEM_NORMAL)

    #     I1 = wx.MenuItem(
    #         parentMenu = M1,
    #         id         = wx.ID_EXIT,
    #         text       = "&Quit\tCTRL+Q",
    #         helpString = "quit application",
    #         kind = wx.ITEM_NORMAL,
    #         subMenu    = None)

    #     self.Bind(wx.EVT_MENU, self._quitRequest, I1)

    #     M1.Append(I1)

    #     M2 = wx.Menu()

    #     M2.Append(
    #         wx.ID_SPELL_CHECK,
    #         "&Spell Check\tCTRL+T",
    #         "spell check on/off",
    #         kind = wx.ITEM_CHECK)

    #     MB = wx.MenuBar()
    #     MB.Append(M1, "&File")
    #     MB.Append(M2, "&Option")

    #     self.Frame.SetMenuBar(MB)

    #     SB = wx.StatusBar(
    #         parent = self.Frame,
    #         id     = ID_ANY, 
    #         style  = wx.STB_DEFAULT_STYLE,
    #         name   = "")

    #     self.Frame.SetStatusBar(SB)

    #     return

# STB_DEFAULT_STYLE
# STB_ELLIPSIZE_END
# STB_ELLIPSIZE_MIDDLE
# STB_ELLIPSIZE_START
# STB_SHOW_TIPS
# STB_SIZEGRIP

# ITEM_CHECK
# ITEM_DROPDOWN
# ITEM_MAX
# ITEM_NORMAL
# ITEM_RADIO
# ITEM_SEPARATOR
