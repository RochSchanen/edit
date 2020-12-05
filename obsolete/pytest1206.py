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
from wx import PENSTYLE_TRANSPARENT

from wx import BITMAP_SCREEN_DEPTH

from wx import MemoryDC
from wx import NullBitmap

from wx import Pen
from wx import Brush
from wx import Colour
from wx import Font
from wx import Bitmap
from wx import Point # only in Frame.SetPosition()

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
from wx import WXK_NUMPAD_ENTER
from wx import WXK_CONTROL_A
from wx import WXK_CONTROL_C
from wx import WXK_TAB
from wx import EVT_CHAR
from wx import MOD_NONE
from wx import MOD_CONTROL
from wx import MOD_SHIFT
# from wx import MOD_ALT

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
        # transparent
        pen = Pen()
        pen.SetStyle(PENSTYLE_TRANSPARENT)
        self.pens['transparent'] = pen
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
        # add extra (uk keyboard, no Alt Gr) characters
        self.charSet.extend(['¬','£','~'])
        # add extra (editor symbols) characters
        self.charSet.extend(['¶'])  
        # subsets
        self.lowRoman = 'abcdefghijklmnopqrstuvwxyz'
        self.upRoman  = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.numeric  = '0123456789'
        self.alphabet = self.lowRoman + self.upRoman
        self.alphanum = self.alphabet + self.numeric
        self.word     = self.alphanum + '_'
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
            # create bitmap
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
            # create bitmap
            bitmap = Bitmap(cw, ch, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(bitmap)
            # set background
            dc.SetBackground(Brush(Colour(70, 80, 90)))
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(Colour(160,160,180))
            # write character (make space a center dot)
            if c == ' ': dc.DrawText(c,0,0)
            else: dc.DrawText(c,0,0)
            # create reference to bitmap
            self.selectedChars[c] = bitmap

        # NUMBER CHARACTERS
        self.numberChars = {}
        # create bitmaps
        for c in ' 0123456789':
            # create bitmap
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
        self.bmpBuf = Bitmap(
            width *cw,              # bitmap width
            height*ch,              # bitmap heigh
            BITMAP_SCREEN_DEPTH)    # bitmap depth
        # create device context
        dc = MemoryDC()               
        # select buffer
        dc.SelectObject(self.bmpBuf)
        # set background
        dc.SetBackground(self.brushes['bkgd'])
        # clear buffer
        dc.Clear()
        # release bitmap
        dc.SelectObject(NullBitmap)
        # hook BackgroundBitmap to bitmapBuffer handle
        self.Panel.BackgroundBitmap = self.bmpBuf
        # record geometry
        self.screenSize = width, height
        # done        
        return

    def setFramePosition(self):
        # adjust frame position
        scrw, scrh = 3840, 1200 # screen size
        w, h = self.Panel.BackgroundBitmap.GetSize()
        self.Frame.SetPosition(Point(scrw/4-80*8/2, 200))
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
        dc.SelectObject(self.bmpBuf)
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
        c1, r1, c2, r2 = self.getBlockGeometry()
        # set brush
        dc.SetBrush(Brush(Colour(100,100,100)))
        dc.SetPen(self.pens['transparent'])

        # draw text
        x, y = 0, -1
        for line in self.chrBuf[Y:]:
            y += 1
            if y+st >= rw-sb: break
            # draw line number
            self.drawText(dc, f'{y+Y:4d}', 0, y+st, self.numberChars)
            # the line is outside of the block
            if y+Y < r1 or y+Y > r2:
                self.drawText(dc, line[X:], x+sl, y+st, self.normalChars)
                continue
            # block is inside if the line
            if r1 == r2:
                self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
                self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
                self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
                continue
            # line at the start of the block
            if y+Y == r1:
                self.drawText(dc, line[X:]+'¶',   x+sl, y+st, self.selectedChars)
                self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
                continue
            # line at the end of the block
            if y+Y == r2:
                self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
                self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
                continue
            # line is inside the block
            self.drawText(dc, line[X:]+'¶', x+sl, y+st, self.selectedChars)

        # draw cursor
        x, y = self.cursor
        x1, y1, y2 = (x+sl)*cw, (y+st)*ch, (y+st+1)*ch-1
        dc.SetPen(self.pens['cursor'])
        dc.DrawLine(x1, y1, x1, y2)

        # done
        dc.SelectObject(NullBitmap)
        return

    def shiftToColumn(self, c):
        # get geometry and state
        cl, rw = self.screenSize
        sl, sr, st, sb = 5, 15, 5, 5
        X, Y = self.scroll
        x, y = self.cursor

        # left shift
        if x+X > c:
            x = c-X
            # check boundary
            b = 0
            if x < b:
                x = b
                X = c-b
                # check limit
                if X < 0:
                    X = 0
                    x = c

        # right shift
        if x+X < c:
            x = c-X
            # check boundary
            b = cl-(sl+sr) 
            if x > b:
                x = b
                X = c-b
            # there is no scroll
            # limit to the right

        # done
        self.cursor = x, y
        self.scroll = X, Y
        return

    def shiftToRow(self, r):
        # get geometry and state
        cl, rw = self.screenSize
        sl, sr, st, sb = 5, 15, 5, 5
        X, Y = self.scroll
        x, y = self.cursor

        # up shift
        if y+Y > r:
            y = r-Y
            # check boundary
            b = 0
            if y < b:
                y = b
                Y = r-b
                # check limit
                if Y < 0:
                    Y = 0
                    y = r

        # down shift
        if y+Y < r:
            y = r-Y
            # check boundary
            b = rw-(st+sb)-1 
            if y > b:
                y = b
                Y = r-b
            # there is no scroll
            # limit to the bottom

        # done
        self.cursor = x, y
        self.scroll = X, Y
        return

    def moveBottom(self):
        l = len(self.chrBuf)
        self.shiftToRow(l-1)
        self.moveEnd()
        return True

    def moveTop(self):
        x, y = 0, 0
        X, Y = 0, 0 
        # done
        self.cursor = x, y
        self.scroll = X, Y
        return True

    def splitLine(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line and split
        line = self.chrBuf[y+Y]
        left, right = line[:x+X], line[x+X:]
        # current line keeps left string
        self.chrBuf[y+Y] = left
        # get indent from left spaces
        indent = len(left) - len(left.lstrip())
        # insert new line with indented right string
        self.chrBuf.insert(y+Y+1, indent*' '+right)
        # place cursor
        self.moveDown()
        self.shiftToColumn(indent)
        # done
        return True

    def deleteBack(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check left screen limit
        if x+X > 0:
            self.moveLeft()            
            self.deleteAhead()
            return True
        # check top screen limit
        if y+Y > 0:
            self.moveUp()
            self.moveEnd()            
            self.deleteAhead()
            return True
        # nop
        return False

    def deleteAhead(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.chrBuf[y+Y])
        # check end-of-buffer
        if x+X < len(line):
            # delete one character
            line.pop(x+X)
            self.chrBuf[y+Y] = ''.join(line)
            return True
        # check end-of-buffers
        if y+Y < len(self.chrBuf)-1:
            # update buffer
            self.chrBuf[y+Y] = ''.join(line)
            # adjoint next buffer
            self.chrBuf[y+Y] += self.chrBuf[y+Y+1]
            # delete next buffer
            self.chrBuf.pop(y+Y+1)
            # done
            return True
        # nop
        return False

    def insertChar(self, c):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.chrBuf[y+Y])
        # insert char
        line.insert(x+X, chr(c))
        # update buffer
        self.chrBuf[y+Y] = ''.join(line)
        # move right
        self.shiftToColumn(x+X+1)
        return True

    def moveUp(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check start-of-buffers
        if y+Y > 0:
            self.shiftToRow(y+Y-1)
            l = len(self.chrBuf[y+Y-1])
            if x+X > l: self.shiftToColumn(l)
            return True
        # nop
        return

    def moveDown(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check end-of-buffers
        if y+Y < len(self.chrBuf)-1:
            self.shiftToRow(y+Y+1)
            l = len(self.chrBuf[y+Y+1])
            if x+X > l: self.shiftToColumn(l)
            return True
        # nop
        return

    def moveHome(self):
        self.shiftToColumn(0)
        return True

    def moveEnd(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line length
        l = len(self.chrBuf[y+Y])
        # shift
        self.shiftToColumn(l)
        return True

    def moveLeft(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check start-of-buffer
        if (x+X) > 0:
            self.shiftToColumn(x+X-1)
            return True
        if (y+Y) > 0:
            self.shiftToRow(y+Y-1)
            self.moveEnd()
            return True
        # nop
        return False

    def moveRight(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check end-of-buffer
        if (x+X) < len(self.chrBuf[y+Y]):
            self.shiftToColumn(x+X+1)
            return True
        if (y+Y) < len(self.chrBuf)-1:
            self.shiftToRow(y+Y+1)
            self.shiftToColumn(0)
            return True
        # nop
        return False

    def setBlockBegin(self):
        x, y = self.cursor
        X, Y = self.scroll
        self.blockBegin = x+X, y+Y
        self.blockEnd = self.blockBegin
        return

    def setBlockEnd(self):
        x, y = self.cursor
        X, Y = self.scroll
        self.blockEnd = x+X, y+Y
        return

    def getBlockGeometry(self):
        c1, r1 = self.blockBegin
        c2, r2 = self.blockEnd
        # order block boundaries
        if r1 == r2:
            if c1 > c2:
                # reverse order
                return c2, r2, c1, r1
        if r1 > r2:
            # reverse order
            return c2, r2, c1, r1
        # straight order
        return c1, r1, c2, r2

    def blockSelected(self):
        b = self.blockBegin
        e = self.blockEnd
        return not b == e

    def deleteBlock(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get block geometry
        c1, r1, c2, r2 = self.getBlockGeometry()

        # one line block
        if r1 == r2:
            # get line
            line = self.chrBuf[y+Y]
            # delete
            self.chrBuf[y+Y] = line[:c1]+line[c2:]
            # move to blockBegin
            self.shiftToColumn(c1)

        # multi-lines block
        else:
            startLeft = self.chrBuf[r1][:c1]
            endRight  = self.chrBuf[r2][c2:]
            # collect parts into one line
            self.chrBuf[r1] = startLeft + endRight
            # delete full lines
            del self.chrBuf[r1+1:r2+1]
            # move to blockBegin
            self.shiftToRow(r1)
            self.shiftToColumn(c1)

        # deselect block
        self.setBlockBegin()
        return True

    def copyBlock(self):
        # clear previous data
        self.clipboard = []
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get block geometry
        c1, r1, c2, r2 = self.getBlockGeometry()

        # one line block
        if r1 == r2:
            line = self.chrBuf[y+Y][c1:c2]
            self.clipboard.append(line)

        # multi-lines block
        else:
            firstline = self.chrBuf[r1][c1:]
            self.clipboard.append(firstline)
            for r in range(r1+1,r2):
                newline = self.chrBuf[r]
                self.clipboard.append(newline)
            lastline = self.chrBuf[r2][:c2]
            self.clipboard.append(lastline)

        # done
        return

    def cutBlock(self):
        self.copyBlock()
        self.deleteBlock()
        return

    def pasteClipboard(self):
        # check if copy not empty
        if self.clipboard:

            # make a shallow copy
            buffer = self.clipboard.copy()

            # get state
            X, Y = self.scroll
            x, y = self.cursor

            # remove and save current line
            line = self.chrBuf.pop(y+Y)
            
            # split line at cursor position
            left, right = line[:x+X], line[x+X:]
            
            # add left to the first line of the buffer
            buffer[0] = left + buffer[0]
            
            # save position for repositioning the cursor
            l = len(buffer[-1])
            
            # add right to the last line of the buffer
            buffer[-1] = buffer[-1] + right
            
            # insert buffer
            for i, line in enumerate(buffer):
                self.chrBuf.insert(y+Y+i, line)
            
            # re-position the cursor
            self.shiftToRow(y+Y+i)
            self.shiftToColumn(l)
            
            # deselect block
            self.setBlockBegin()
            # done
            return True

        # nop
        return False

    def shiftLeft(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = ''.join(reversed(self.chrBuf[y+Y]))

        # check start-of-line
        if x+X > 0:
            k = len(line)-(x+X)
            if line[k] in self.word:
                for i, c in enumerate(line[k:]):
                    if c not in self.word: break
                else: i+=1
                self.shiftToColumn(x+X-i)
                return True
            if line[k] not in self.word:
                for i, c in enumerate(line[k:]):
                    if c in self.word: break
                else: i+=1
                self.shiftToColumn(x+X-i)
                return True

        # check start-of-lines
        if (y+Y) > 0:
            self.shiftToRow(y+Y-1)
            self.moveEnd()
            return True

        # nop
        return False

    def shiftRight(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = self.chrBuf[y+Y]

        # check end-of-line
        if x+X < len(line):
            k = x+X
            if line[k] in self.word:
                for i, c in enumerate(line[x+X:]):
                    if c not in self.word: break
                else: i+=1
                self.shiftToColumn(x+X+i)
                return True
            if line[k] not in self.word:
                for i, c in enumerate(line[x+X:]):
                    if c in self.word: break
                else: i+=1
                self.shiftToColumn(x+X+i)
            return True

        # check end-of-lines
        if (y+Y) < len(self.chrBuf)-1:
            self.shiftToRow(y+Y+1)
            self.shiftToColumn(0)
            return True
            
        # nop
        return False

    def selectAll(self):
        self.moveBottom()
        self.blockBegin = 0, 0
        self.setBlockEnd()
        return True

    def shiftTab(self):
        tabSize = 4
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line and split
        line = self.chrBuf[y+Y]
        left, right = line[:x+X], line[x+X:]
        # get next tab number
        nextTab = (x+X)//tabSize+1
        # compute spaces
        spaces = tabSize*nextTab-(x+X)
        # insert new spaces
        self.chrBuf[y+Y] = left+spaces*' '+right
        # adjust cursor position
        self.shiftToColumn(x+Y+spaces)
        return True

    def _OnKeyDown(self, event):

        # get special key code
        key = event.GetKeyCode()

        # check for ESCAPE key
        if key == WXK_ESCAPE:
            self._quitRequest(event)

        # LEFT/RIGHT/UP/DOWN/HOME/END:
        
        # build case structure
        case = {
            WXK_UP    : self.moveUp,
            WXK_DOWN  : self.moveDown,
            WXK_HOME  : self.moveHome,
            WXK_END   : self.moveEnd,
            WXK_LEFT  : self.moveLeft,
            WXK_RIGHT : self.moveRight}
        # motion only
        if event.GetModifiers() == MOD_NONE:
            if key in case.keys():
                case[key]()
                self.setBlockBegin()
                self.refreshBuffer()
                self.Panel.Refresh()
        # motion with shift key pressed
        if event.GetModifiers() == MOD_SHIFT:
            if key in case.keys():
                if case[key]():
                    # move block extent
                    self.setBlockEnd()
                    self.refreshBuffer()
                    self.Panel.Refresh()

        # CONTROL LEFT/RIGHT/HOME/END:
        
        # build case structure
        case = {
            WXK_LEFT   : self.shiftLeft,
            WXK_RIGHT  : self.shiftRight,
            WXK_END    : self.moveBottom,
            WXK_HOME   : self.moveTop}
        if event.GetModifiers() == MOD_CONTROL:
            if key in case.keys():
                if case[key]():
                    self.setBlockBegin()
                    self.refreshBuffer()
                    self.Panel.Refresh()
        if event.GetModifiers() == (MOD_CONTROL+MOD_SHIFT):
            if key in case.keys():
                if case[key]():
                    self.setBlockEnd()
                    self.refreshBuffer()
                    self.Panel.Refresh()

        # RETURN/ENTER:

        if event.GetModifiers() == MOD_NONE:
            if key == WXK_RETURN or key == WXK_NUMPAD_ENTER:
                if self.splitLine():
                    self.setBlockBegin()
                    self.refreshBuffer()
                    self.Panel.Refresh()

        # DELETE/BACKSPACE:

        # build case structure
        case = {
            WXK_BACK   : self.deleteBack,
            WXK_DELETE : self.deleteAhead}
        if event.GetModifiers() == MOD_NONE:
            if key in case.keys():
                if self.blockSelected():
                    self.deleteBlock()
                    self.refreshBuffer()
                    self.Panel.Refresh()
                else:
                    if case[key]():
                        self.refreshBuffer()
                        self.Panel.Refresh()

        # CONTROL C/V/X/A:

        # build case structure
        case = {
            'A' : self.selectAll,
            'C' : self.copyBlock,
            'X' : self.cutBlock,
            'V' : self.pasteClipboard}
        if event.GetModifiers() == MOD_CONTROL:
            if chr(key) in case.keys():
                if case[chr(key)]():
                    self.refreshBuffer()
                    self.Panel.Refresh()

        # TAB

        if event.GetModifiers() == MOD_NONE:
            if key == WXK_TAB:
                if self.shiftTab():
                    self.setBlockBegin()
                    self.refreshBuffer()
                    self.Panel.Refresh()

        # done
        event.Skip()
        return

    def _OnChar(self, event):
        # get unicode value
        key = event.GetUnicodeKey()
        # check charset
        if chr(key) in self.charSet:
            if self.blockSelected():
                self.deleteBlock()
            self.insertChar(key)
            self.setBlockBegin()
            self.refreshBuffer()
            self.Panel.Refresh()
        # done
        return

    def Start(self):
        
        self.createBrushes()
        self.createPens()
        self.createFonts()
        self.createCharSet()
        self.createCharBitmaps()
        self.createBufferBitmap(85, 40)
        self.setFramePosition()

        self.clipboard = []
        self.scroll = 0, 0
        self.cursor = 0, 0
        self.blockBegin = 0, 0
        self.blockEnd   = 0, 0
        self.chrBuf = ['']
        
        self.refreshBuffer()
        self.Panel.Refresh()
        
        self.Bind(EVT_CHAR, self._OnChar)
        
        return

App().MainLoop()
