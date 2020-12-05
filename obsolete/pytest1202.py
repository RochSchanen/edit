import base

# from wx import FONTWEIGHT_NORMAL
# from wx import FONTENCODING_DEFAULT
# from wx import FONTFAMILY_ROMAN
# from wx import FONTSTYLE_NORMAL
# from wx import Rect
# from wx import Image
# from wx import EVT_SIZE

from wx import PENSTYLE_SOLID
from wx import BRUSHSTYLE_SOLID
from wx import BITMAP_SCREEN_DEPTH
from wx import MemoryDC
from wx import NullBitmap
from wx import Pen
from wx import Brush
from wx import Colour
from wx import Font
from wx import Bitmap
from wx import Point
from wx import WXK_ESCAPE
from wx import WXK_HOME
from wx import WXK_END
from wx import WXK_DELETE
from wx import WXK_BACK
from wx import WXK_LEFT
from wx import WXK_RIGHT
from wx import WXK_UP
from wx import WXK_DOWN
from wx import WXK_RETURN
from wx import EVT_CHAR
from wx import MOD_NONE
from wx import MOD_CONTROL
from wx import MOD_SHIFT
from wx import MOD_ALT

# allow exit() through the escape key
base._ESCAPE = True

class App(base.App):

    def createPens(self):
        # PENS
        self.pens = {}
        # margin
        pen = Pen()
        pen.SetWidth(1)
        pen.SetStyle(PENSTYLE_SOLID)
        pen.SetColour(Colour(180, 50, 50))
        self.pens['margin'] = pen
        # cursor
        pen = Pen()
        pen.SetWidth(2)
        pen.SetStyle(PENSTYLE_SOLID)
        pen.SetColour(Colour(255, 255, 255))
        self.pens['cursor'] = pen
        # done
        return

    def createBrushes(self):
        # BRUSHES
        self.brushes = {}
        # background brush
        brush = Brush()
        brush.SetStyle(BRUSHSTYLE_SOLID)
        brush.SetColour(Colour(52, 61, 70))
        self.brushes['bkgd'] = brush
        # done
        return

    def createFonts(self):
        # FONTS
        self.fonts = {}
        # monospace
        font = Font()
        font.SetFaceName("Monospace")
        font.SetPointSize(10)
        self.fonts['monospace'] = font
        # done
        return

    def createCharSet(self):
        # standard printable ascii table
        self.charSet = list(map(chr, range(32, 126)))
        # add extra characters
        self.charSet.append('£')
        self.charSet.append('~')
        return

    def createCharBitmaps(self):
        # create device context
        dc = MemoryDC()               
        # set font
        dc.SetFont(self.fonts['monospace'])
        # get font size (monospace)
        cw, ch = dc.GetTextExtent(' ')
        # record geometry
        self.charSize = cw, ch
        # NORMAL CHARACTERS
        self.normalChars = {}
        # create bitmaps
        for c in self.charSet:
            # create black and white bitmap
            bitmap = Bitmap(cw, ch, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(bitmap)
            # set background
            dc.SetBackground(self.brushes['bkgd'])
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(Colour(230,230,230))
            # write character
            dc.DrawText(c,0,0)
            # create reference to bitmap
            self.normalChars[c] = bitmap
        # SELECTED CHARACTERS
        self.selectedChars = {}
        # create bitmaps
        for c in self.charSet:
            # create black and white bitmap
            bitmap = Bitmap(cw, ch, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(bitmap)
            # set background
            dc.SetBackground(Brush(Colour(100,100,100)))
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(Colour(230,230,230))
            # write character
            dc.DrawText(c,0,0)
            # create reference to bitmap
            self.selectedChars[c] = bitmap
        # NUMBER CHARACTERS
        self.numberChars = {}
        # create bitmaps
        for c in ' 0123456789':
            # create black and white bitmap
            bitmap = Bitmap(cw, ch, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(bitmap)
            # set background
            dc.SetBackground(self.brushes['bkgd'])
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(Colour(150,150,200))
            # write character
            dc.DrawText(c,0,0)
            # create reference to bitmap
            self.numberChars[c] = bitmap
        # release bitmap
        dc.SelectObject(NullBitmap)
        # done
        return

    def createBufferBitmap(self, width, height):
        # get geometry
        cw, ch = self.charSize
        # create bitmap buffer
        self.bitmapBuffer = Bitmap(
            width *cw,              # bitmap width
            height*ch,              # bitmap heigh
            BITMAP_SCREEN_DEPTH)    # bitmap depth
        # create device context
        dc = MemoryDC()               
        # select buffer
        dc.SelectObject(self.bitmapBuffer)
        # set background
        dc.SetBackground(self.brushes['bkgd'])
        # clear buffer
        dc.Clear()
        # release bitmap
        dc.SelectObject(NullBitmap)
        # hook BackgroundBitmap to bitmapBuffer handle
        self.Panel.BackgroundBitmap = self.bitmapBuffer
        # record geometry
        self.screenSize = width, height
        # done        
        return

    def setFramePosition(self):
        # adjust frame position
        scrw, scrh = 3840, 1200 # screen size
        w, h = self.Panel.BackgroundBitmap.GetSize()
        self.Frame.SetPosition(Point(scrw/4-80*8/2, 500))
        return

    def drawText(self, dc, text, x, y, charBitmap):
        cw, ch = self.charSize
        cl, rw = self.screenSize
        sl, sr, st, sb = 5, 15, 5, 5
        for c in text:
            if x >= cl-sr: break
            dc.DrawBitmap(charBitmap[c], x*cw, y*ch)
            x += 1
        # done
        return

    def refreshBuffer(self):
        # get geometry
        X, Y = self.scroll
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # create device context
        dc = MemoryDC()               
        # select
        dc.SelectObject(self.bitmapBuffer)
        # set background
        dc.SetBackground(self.brushes['bkgd'])
        # and clear buffer
        dc.Clear()
        # draw margins
        x3, x4 = 0*cw, cl*cw
        x1, y1 = (sl-0.5)*cw, (st-0.5)*ch
        x2, y2 = (cl-sr+0.5)*cw, (rw-sb+0.5)*ch
        dc.SetPen(self.pens['margin'])
        dc.DrawLine(x1, y1, x1, y2)
        dc.DrawLine(x2, y1, x2, y2)
        dc.DrawLine(x3, y1, x4, y1)
        dc.DrawLine(x3, y2, x4, y2)

        # get block geometry
        r1, c1 = self.blockBegin
        r2, c2 = self.blockEnd
        block = False

        # draw text
        x, y = 0, 0
        for line in self.characterBuffer[Y:]:
            # draw line number
            self.drawText(dc, f'{y+Y:4d}', 0, y+st, self.numberChars)
            # the line is outside of the block
            if y+Y < r1 or y+Y > r2:
                self.drawText(dc, line[X:], x+sl, y+st, self.normalChars)
                # done
                y += 1
                if y+st >= rw-sb: break
                continue
            # block is inside if the line
            if r1 == r2:
                # draw normal text
                # self.drawText(dc, line[X:], x+sl, y+st, self.normalChars)
                # # block has size zero
                # if c1 == c2: 
                #     # done
                #     y += 1
                #     if y+st >= rw-sb: break
                #     continue
                # block has finite size
                self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
                self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
                self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
                # done
                y += 1
                if y+st >= rw-sb: break
                continue
            # line at the start of the block
            if y+Y == r1:
                self.drawText(dc, line[X:],   x+sl, y+st, self.selectedChars)
                self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
                # done
                y += 1
                if y+st >= rw-sb: break
                continue
            # line at the end of the block
            if y+Y == r2:
                self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
                self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
                # done
                y += 1
                if y+st >= rw-sb: break
                continue
            # line in the middle of the block
            self.drawText(dc, line[X:], x+sl, y+st, self.selectedChars)
            y += 1
            if y+st >= rw-sb: break

        # draw cursor
        x, y = self.cursor
        x1, y1, y2 = (x+sl)*cw, (y+st)*ch, (y+st+1)*ch-1
        dc.SetPen(self.pens['cursor'])
        dc.DrawLine(x1, y1, x1, y2)

        # done
        dc.SelectObject(NullBitmap)
        return

    def moveBottom(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # # get state
        # X, Y = self.scroll
        # x, y = self.cursor
        # # get line
        # line = list(self.characterBuffer[y+Y])
        # # get length
        # ln = len(line)
        x, y = 0, rw-(st+sb)-1
        X, Y = 0, len(self.characterBuffer)-1-y
        # record new state
        self.cursor = x, y
        self.scroll = X, Y
        # done
        self.moveEnd()
        return True

    def moveTop(self):
        # get geometry
        # cw, ch = self.charSize
        # sl, sr, st, sb = 5, 15, 5, 5
        # cl, rw = self.screenSize
        # # get state
        # X, Y = self.scroll
        # x, y = self.cursor
        # # get line
        # line = list(self.characterBuffer[y+Y])
        # # get length
        # ln = len(line)
        x, y = 0, 0
        X, Y = 0, 0 
        # done
        self.cursor = x, y
        self.scroll = X, Y
        self.refreshBuffer()
        return True

    def splitLine(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.characterBuffer[y+Y])
        # get length
        ln = len(line)
        # check end-of-buffer
        if x+X < ln:
            # keep left hand side
            self.characterBuffer[y+Y] = ''.join(line[:x+X])
            # copy right hand side
            self.characterBuffer.insert(y+Y+1, ''.join(line[x+X:]))
        else:
            # new empty buffer
            self.characterBuffer.insert(y+Y+1, '')
        # record new state
        self.scroll = X, Y
        self.cursor = x, y
        self.moveDown()
        self.moveHome()
        # done
        return True

    def deleteBack(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.characterBuffer[y+Y])
        # get length
        ln = len(line)
        # check left screen limit
        if x+X > 0:
            self.moveLeft()            
            self.deleteAhead()
            # done
            return True
        # check top screen limit
        if y+Y > 0:
            self.moveUp()
            self.moveEnd()            
            self.deleteAhead()
            # done
            return True
        # nop
        return False

    def deleteAhead(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.characterBuffer[y+Y])
        # get length
        ln = len(line)
        # check end-of-buffer
        if x+X < ln:
            # delete one character
            line.pop(x+X)
            self.characterBuffer[y+Y] = ''.join(line)
            self.refreshBuffer()
            return True
        # check end-of-buffers
        if y+Y < len(self.characterBuffer)-1:
            # update buffer
            self.characterBuffer[y+Y] = ''.join(line)
            # adjoint next buffer
            self.characterBuffer[y+Y] += self.characterBuffer[y+Y+1]
            # delete next buffer
            self.characterBuffer.pop(y+Y+1)
            # done
            self.refreshBuffer()
            return True
        # nop
        return False

    def insertChar(self, c):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.characterBuffer[y+Y])
        # get length
        ln = len(line)
        # insert char
        line.insert(x+X, chr(c))
        # update buffer
        self.characterBuffer[y+Y] = ''.join(line)
        # record new state
        self.cursor = x, y
        self.scroll = X, Y
        # move right
        self.moveRight()
        return True

    def moveUp(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check start-of-buffers
        if y+Y > 0:
            # move up
            y -= 1
            # check limit
            if y < 0 and Y > 0:
                y = 0
                Y -= 1
            # get line
            line = list(self.characterBuffer[y+Y])
            # get length
            ln = len(line)
            # adjust colummn position
            if x+X > ln:
                x = ln-X
                # check limit
                if x < sl:
                    x = sl
                    X = ln - sl
                    # check limit
                    if X < 0:
                        X = 0
                        x = ln
            # done
            self.cursor = x, y
            self.scroll = X, Y
            self.refreshBuffer()
            return True
        # nop
        return

    def moveDown(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check end-of-buffers
        if y+Y < len(self.characterBuffer)-1:
            # move down
            y += 1
            # check limit
            if y > rw-(st+sb)-1:
                y = rw-(st+sb)-1
                Y += 1
            # get line
            line = list(self.characterBuffer[y+Y])
            # get length
            ln = len(line)
            # adjust colummn position
            if x+X > ln:
                x = ln-X
                # check limit
                if x < sl:
                    x = sl
                    X = ln - sl
                    # check limit
                    if X < 0:
                        X = 0
                        x = ln
            # done
            self.cursor = x, y
            self.scroll = X, Y
            self.refreshBuffer()
            return True
        # nop
        return

    def moveHome(self):
        # # get geometry
        # cw, ch = self.charSize
        # sl, sr, st, sb = 5, 15, 5, 5
        # cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # # get line
        # line = list(self.characterBuffer[y+Y])
        # # get length
        # ln = len(line)
        # go buffer start
        x, X = 0, 0
        # done
        self.cursor = x, y
        self.scroll = X, Y
        self.refreshBuffer()
        return True

    def moveEnd(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.characterBuffer[y+Y])
        # get length
        ln = len(line)
        # go buffer end
        x = ln-X
        # check scroll limit
        if x > cl-(sl+sr):
            x = cl-(sl+sr)
            X = ln-cl+(sl+sr)
        # done
        self.cursor = x, y
        self.scroll = X, Y
        self.refreshBuffer()
        return True

    def moveLeft(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.characterBuffer[y+Y])
        # get length
        ln = len(line)
        # check start-of-buffer
        if (x+X) > 0:
            # move left
            x -= 1
            # check scroll limit
            if x < 0 and X > 0:
                x = 0
                X -= 1
            # done
            self.cursor = x, y
            self.scroll = X, Y
            self.refreshBuffer()
            return True
        # nop
        return False

    def moveRight(self):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.characterBuffer[y+Y])
        # get length
        ln = len(line)
        # check end-of-buffer
        if (x+X) < ln:
            # move right
            x += 1
            # check scroll limit
            if x > cl-(sl+sr):
                x = cl-(sl+sr)
                X += 1
            # done
            self.cursor = x, y
            self.scroll = X, Y
            self.refreshBuffer()
            return True
        # nop
        return False

    def Start(self):
        self.createBrushes()
        self.createPens()
        self.createFonts()
        self.createCharSet()
        self.createCharBitmaps()
        self.createBufferBitmap(85, 40)
        self.setFramePosition()
        self.scroll = 0, 0
        self.cursor = 0, 0
        self.blockBegin = 1, 0
        self.blockEnd   = 3, 0
        # set default buffer (test buffer)
        self.characterBuffer = [
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ' 123456789 123456789 123456789 123456789 123456789',
            ]

        self.refreshBuffer()
        self.Panel.Refresh()

        # bind character events
        self.Bind(EVT_CHAR, self._OnChar)

        # done
        return

    def _OnKeyDown(self, event):
        # get special key code
        key = event.GetKeyCode()
        # check for ESCAPE key
        if key == WXK_ESCAPE:
            self._quitRequest(event)
        if event.GetModifiers() == MOD_NONE:
            # build case structure
            case = {
                WXK_RETURN : self.splitLine,
                WXK_BACK   : self.deleteBack,
                WXK_DELETE : self.deleteAhead,
                WXK_UP     : self.moveUp,
                WXK_DOWN   : self.moveDown,
                WXK_HOME   : self.moveHome,
                WXK_END    : self.moveEnd,
                WXK_LEFT   : self.moveLeft,
                WXK_RIGHT  : self.moveRight}
            if key in case.keys():
                if case[key]():
                    self.Panel.Refresh()
        if event.GetModifiers() & MOD_CONTROL:
            # build case structure
            case = {
                WXK_END    : self.moveBottom,
                WXK_HOME   : self.moveTop}
            if key in case.keys():
                if case[key]():
                    self.Panel.Refresh()
        # done
        event.Skip()
        return

    def _OnChar(self, event):
        # get unicode value
        key = event.GetUnicodeKey()
        # check charset
        if chr(key) in self.charSet:
            if self.insertChar(key):
                self.Panel.Refresh()
        # done
        return

App().MainLoop()
