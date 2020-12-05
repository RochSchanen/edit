# here we build from wx some platform
# independent objects to be used in
# the editor control

# here a list of predefined colors is built

# colors
from wx import Colour
_colours = {}

def createColour(name, R, G, B):
    # add color to dictionary
    _colours[name] = Colour(R,G,B)
    # done
    return

createColour('txt', 230, 230, 230) # normal text color
createColour('bgd',  52,  61,  70) # normal text background
createColour('tSl', 160, 160, 180) # selected text color
createColour('bSl',  70,  80,  90) # selected text background
createColour('emp', 150, 150, 200) # emphasised text color

# for each color a solid color brush is build as default

# brushes
from wx import Brush, BRUSHSTYLE_SOLID
_brushes = {}

def createSolidBrush(brushName, colourName):
    # make brush
    brush = Brush()
    brush.SetStyle(BRUSHSTYLE_SOLID)
    brush.SetColour(_colours[colourName])
    # add brush
    _brushes[brushName] = brush
    # done
    return

for c in _colours.keys():
    createSolidBrush(c, c)

# we need character definitions for
# the editor, there is going to be a
# dictionary of autorised character
# codes associated with bitmaps

# the printable character set:
_printableCharSet = []

def createPrintableCharSet():
    # make the standard printable ascii table
    printascii = list(map(chr, range(32, 126)))
    # add to set
    _printableCharSet.extend(printascii)
    # add extra (uk keyboard, no Alt Gr) characters
    _printableCharSet.extend(['¬','£','~'])
    # add extra (editor symbols) characters
    _printableCharSet.extend(['¶'])  
    return

# fonts (all fonts must be monospace for the screen to work)
from wx import Font
_fonts = {}

def createFont(
        name = 'mono',
        face = "Monospace",
        size = 10):
    # make font
    font = Font()
    font.SetFaceName(face)
    font.SetPointSize(size)
    # add to dictionary
    _fonts[name] = font
    # done
    return

# bitmaps
from wx import MemoryDC, NullBitmap
_printableCharBitmaps = {}
_cw, _ch = None, None

def createCharBitmap(setName, fontName, frgd, bkgd):

        global _cw, _ch

        # create device context
        dc = MemoryDC()               
        # set font
        dc.SetFont(_fonts[fontName])
        # get font size
        _cw, _ch = dc.GetTextExtent(' ')
        BitmapSet = {}
        for c in _printableCharSet:
            # create bitmap
            bitmap = Bitmap(_cw, _ch, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(bitmap)
            # set background
            dc.SetBackground(_brushes[bkgd])
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(_colours[frgd])
            # write character
            dc.DrawText(c,0,0)
            # record
            BitmapSet[c] = bitmap
        # release bitmap
        dc.SelectObject(NullBitmap)
        # record set
        _printableCharBitmaps[setName] = BitmapSet
        # done
        return

# font and 

class charSet():

    def __init__(self):
        return

def createCharBitmaps():
    createFont('mono', 'Monospace', 10)
    createCharBitmap('normal',  'mono', 'txt', 'bgd')
    createCharBitmap('selText', 'mono', 'tSl', 'bSl')
    createCharBitmap('numbers', 'mono', 'emp', 'bgd')
    createCharBitmap('cursor',  'mono', 'bgd', 'txt')
    return

if __name__ == '__main__':

    import wx

    def setFramePosition(frame):
        # adjust frame position
        scrw, scrh = 3840, 1200 # screen size
        w, h = frame.Panel.BackgroundBitmap.GetSize()
        frame.SetPosition(wx.Point(scrw/4-w/2, scrh/2-h/2))
        return

    def TestText(bmp, text, x, y, name):
        # get reference to bitmap set
        b = _printableCharBitmaps[name]
        # get characters geometry
        cw, ch = b[' '].GetSize()
        # create device context
        dc = MemoryDC()
        # select
        dc.SelectObject(bmp)
        # draw text
        for c in text:
            dc.DrawBitmap(b[c], x*cw, y*ch)
            x += 1
        # release bitmap
        dc.SelectObject(NullBitmap)
        # done
        return

    import base
    base._ESCAPE = True

    class App(base.App):

        def Start(self):

            createCharBitmaps()

            t = TextScreen(4, 128)

            # TestText(self.Panel.BackgroundBitmap,
            #     ''.join(_printableCharSet), 1, 1, 'normal')

            # TestText(self.Panel.BackgroundBitmap,
            #     ''.join(_printableCharSet), 1, 2, 'selText')

            # TestText(self.Panel.BackgroundBitmap,
            #     ''.join(_printableCharSet), 1, 3, 'numbers')

            # TestText(self.Panel.BackgroundBitmap,
            #     ''.join(_printableCharSet), 1, 4, 'cursor')

            self.Panel.BackgroundBitmap = t.bitmap

            # done
            setFramePosition(self.Frame)
            self.Panel.Refresh()
            return

    App().MainLoop()
