import base

from wx import PENSTYLE_SOLID, BRUSHSTYLE_SOLID, BITMAP_SCREEN_DEPTH
from wx import FONTWEIGHT_NORMAL, FONTENCODING_DEFAULT
from wx import FONTFAMILY_ROMAN, FONTSTYLE_NORMAL

from wx import WXK_ESCAPE, WXK_HOME, WXK_END, WXK_DELETE, WXK_BACK
from wx import WXK_LEFT, WXK_RIGHT, WXK_UP, WXK_DOWN
from wx import EVT_CHAR, EVT_SIZE

from wx import Pen, Brush, Colour, Font, Point, Rect
from wx import Image, Bitmap, NullBitmap, MemoryDC

from numpy import ones, frombuffer

# allow exit() through the escape key
base._ESCAPE = True

class App(base.App):

    def invertBitmap(self, bitmap):
        data = self.dataFromBitmap(bitmap)
        # build white color data of the same shape
        white = 255*ones(data.shape,'uint8')
        # return the difference: complementary colors
        return self.bitmapFromData(white - data)

    def bitmapFromData(self, data):
        # get the data shape
        height, width, depth = data.shape
        # flatten to byte string
        flatdata = data.tostring()
        # create image of the right shape
        image = Image(width, height)     
        # load image with byte string
        image.SetData(flatdata)
        # convert image to bitmap
        bitmap = image.ConvertToBitmap()
        # done
        return bitmap

    def dataFromBitmap(self, bitmap):
        depth = 3 # the byte depth 
        # get the bitmap shape
        width, height = bitmap.GetSize()
        # convert to image
        image = bitmap.ConvertToImage()
        # flatten to byte string
        flatdata = image.GetData()
        # convert to one dimensional data array
        linear = frombuffer(flatdata, 'uint8')
        # re-shape into three dimentional array
        data = linear.reshape(height, width, depth)
        # done
        return data

    def Start(self):

        # define colors
        self.colours = {}
        self.colours['bkgd']   = Colour( 52,  61,  70)
        self.colours['text']   = Colour(255, 255, 255)
        self.colours['numb']   = Colour(160, 160, 160)
        self.colours['sepr']   = Colour(200, 120, 120)
        self.colours['selbgd'] = Colour( 92, 101, 110)
        self.colours['seltxt'] = Colour(255, 255, 255)

        # brushes
        self.brushes = {}
        # normal background
        b = Brush()
        b.SetStyle(BRUSHSTYLE_SOLID)
        b.SetColour(self.colours['bkgd'])
        self.brushes['bkgd'] = b

        # selected background
        b = Brush()
        b.SetStyle(BRUSHSTYLE_SOLID)
        b.SetColour(self.colours['selbgd'])
        self.brushes['selbgd'] = b

        # pens
        self.pens = {}
        p = Pen()
        p.SetColour(self.colours['sepr'])
        p.SetWidth(1)
        p.SetStyle(PENSTYLE_SOLID)
        self.pens['sepr'] = p

        # create device context to work on bitmaps
        dc = MemoryDC()               

        # define font
        self.fonts = {}
        f = Font()
        f.SetFamily(FONTFAMILY_ROMAN)
        f.SetFaceName("Monospace")
        f.SetEncoding(FONTENCODING_DEFAULT)
        f.SetStyle(FONTSTYLE_NORMAL)
        f.SetWeight(FONTWEIGHT_NORMAL)
        f.SetUnderlined(False)
        f.SetPointSize(10)
        self.fonts['monospace'] = f

        # select font
        f = 'monospace'

        # get font size
        dc.SetFont(self.fonts[f])
        w, h = dc.GetTextExtent(' ')

        # build character dictionary
        self.rawChars = {}
        # standard printable ascii table
        for c in range(32, 126):
            self.rawChars[chr(c)] = None
        # extra characters (UK)
        self.rawChars['£'] = None
        # save character size
        self.rawChars['Size'] = w, h

        # set background color
        dc.SetBackground(self.brushes['bkgd'])

        # build characters bitmaps
        for C in self.rawChars.keys():
            if C == 'Size': continue
            # instanciate character bitmap
            self.rawChars[C] = Bitmap(w, h, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(self.rawChars[C])
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(self.colours['text'])
            # draw character shape and color
            dc.DrawText(C, 0, 0)
        # done
        dc.SelectObject(NullBitmap)

        # build selected dictionary
        self.selChars = {}
        # standard printable ascii table
        for c in range(32, 126):
            self.selChars[chr(c)] = None
        # extra characters (UK)
        self.selChars['£'] = None
        # save character size
        self.selChars['Size'] = w, h

        # set background color
        dc.SetBackground(self.brushes['selbgd'])

        # build selected bitmaps
        for C in self.selChars.keys():
            if C == 'Size': continue
            # instanciate character bitmap
            self.selChars[C] = Bitmap(w, h, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(self.selChars[C])
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(self.colours['seltxt'])
            # draw character shape and color
            dc.DrawText(C, 0, 0)
        # done
        dc.SelectObject(NullBitmap)

        # create bitmap buffer display and clear buffer
        self.bitmapBuffer = Bitmap(
            128*w,                  # bitmap width
             10*h,                  # bitmap height
            BITMAP_SCREEN_DEPTH)    # bitmap depth
        dc.SelectObject(self.bitmapBuffer)
        dc.SetBackground(self.brushes['bkgd'])
        dc.Clear()
        dc.SelectObject(NullBitmap)

        # reference BackgroundBitmap to bitmapBuffer
        self.Panel.BackgroundBitmap = self.bitmapBuffer

        # adjust frame position
        scrw, scrh = 3840, 1200 # screen size
        w, h = self.Panel.BackgroundBitmap.GetSize()
        self.Frame.SetPosition(Point(scrw/4-128*8/2, 800))

        # draw text string
        dc.SelectObject(self.bitmapBuffer)

        t = list("hello")
        # select buffer
        # draw text
        X = 0
        w, h = self.rawChars['Size']
        for c in t:
            dc.DrawBitmap(self.rawChars[c], X, 0)
            X += w

        t = list("World!")
        # select buffer
        # draw text
        X = 0
        w, h = self.selChars['Size']
        for c in t:
            dc.DrawBitmap(self.selChars[c], X, h)
            X += w

        # release bitmap
        dc.SelectObject(NullBitmap)

        # done
        return

App().MainLoop()
