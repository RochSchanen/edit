# from wx import Bitmap, BITMAP_SCREEN_DEPTH
# from wx import MemoryDC, NullBitmap
from wx import Point 
from wx import EVT_CHAR

import base
base._ESCAPE = True

from editor import Screen

# def setFramePosition(frame):
#     # adjust frame position
#     scrw, scrh = 3840, 1200 # screen size
#     w, h = frame.Panel.BackgroundBitmap.GetSize()
#     frame.SetPosition(Point(int(scrw/4-w/2), int(scrh/2-h/2)))
#     return

class App(base.App):

    def Start(self):

        # create editor screen
        self.screen = Screen(80, 50)

        # refer BackgroundBitmap to bitmapBuffer
        self.Panel.BackgroundBitmap = \
            self.screen.bitmapBuffer

        # # set default position
        # setFramePosition(self.Frame)

        # bind printable character events
        # to the screen processChar method
        self.Bind(EVT_CHAR, self.onChar)

        # done
        # self.Panel.Refresh()
        return

    def onChar(self, event):
        self.screen.processChar(event)
        self.Panel.Refresh()
        return

App().MainLoop()

