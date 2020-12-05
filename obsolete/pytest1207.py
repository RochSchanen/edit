import base

from wx import PENSTYLE_SOLID, BRUSHSTYLE_SOLID, PENSTYLE_TRANSPARENT
from wx import BITMAP_SCREEN_DEPTH, MemoryDC, NullBitmap
from wx import Pen, Brush, Colour, Font, Bitmap, Point
from wx import WXK_ESCAPE, WXK_HOME, WXK_END, WXK_DELETE, WXK_BACK
from wx import WXK_LEFT, WXK_RIGHT, WXK_UP, WXK_DOWN, WXK_RETURN
from wx import WXK_NUMPAD_ENTER, WXK_CONTROL_A, WXK_CONTROL_C, WXK_TAB
from wx import MOD_NONE, MOD_CONTROL, MOD_SHIFT, EVT_CHAR

base._ESCAPE = True

class App(base.App):

    def createPens(self):
        self.pens = {}
        pen = Pen()
        pen.SetWidth(1)
        pen.SetStyle(PENSTYLE_SOLID)
        pen.SetColour(Colour(180, 50, 50))
        self.pens['margin'] = pen
        pen = Pen()
        pen.SetWidth(2)
        pen.SetStyle(PENSTYLE_SOLID)
        pen.SetColour(Colour(255, 255, 255))
        self.pens['cursor'] = pen
        pen = Pen()
        pen.SetStyle(PENSTYLE_TRANSPARENT)
        self.pens['transparent'] = pen
        # done
        return

    def createBrushes(self):
        self.brushes = {}
        brush = Brush()
        brush.SetStyle(BRUSHSTYLE_SOLID)
        brush.SetColour(Colour(52, 61, 70))
        self.brushes['bkgd'] = brush
        return

    def createFonts(self):
        self.fonts = {}
        font = Font()
        font.SetFaceName("Monospace")
        font.SetPointSize(10)
        self.fonts['monospace'] = font
        return

    def createCharSet(self):
        self.charSet = list(map(chr, range(32, 126)))
        self.charSet.extend(['¬','£','~'])
        self.charSet.extend(['¶'])  
        self.lowRoman = 'abcdefghijklmnopqrstuvwxyz'
        self.upRoman  = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.numeric  = '0123456789'
        self.alphabet = self.lowRoman + self.upRoman
        self.alphanum = self.alphabet + self.numeric
        self.word     = self.alphanum + '_'
        return

    def createCharBitmaps(self):
        dc = MemoryDC()               
        dc.SetFont(self.fonts['monospace'])
        cw, ch = dc.GetTextExtent(' ')
        self.charSize = cw, ch
        self.normalChars = {}
        for c in self.charSet:
            bitmap = Bitmap(cw, ch, BITMAP_SCREEN_DEPTH)
            dc.SelectObject(bitmap)
            dc.SetBackground(self.brushes['bkgd'])
            dc.Clear()
            dc.SetTextForeground(Colour(230,230,230))
            dc.DrawText(c,0,0)
            self.normalChars[c] = bitmap
        self.selectedChars = {}
        for c in self.charSet:
            bitmap = Bitmap(cw, ch, BITMAP_SCREEN_DEPTH)
            dc.SelectObject(bitmap)
            dc.SetBackground(Brush(Colour(70, 80, 90)))
            dc.Clear()
            dc.SetTextForeground(Colour(160,160,180))
            if c == ' ': dc.DrawText(c,0,0)
            else: dc.DrawText(c,0,0)
            self.selectedChars[c] = bitmap
        self.numberChars = {}
        for c in ' 0123456789':
            bitmap = Bitmap(cw, ch, BITMAP_SCREEN_DEPTH)
            dc.SelectObject(bitmap)
            dc.SetBackground(self.brushes['bkgd'])
            dc.Clear()
            dc.SetTextForeground(Colour(150,150,200))
            dc.DrawText(c,0,0)
            self.numberChars[c] = bitmap
        dc.SelectObject(NullBitmap)
        return

    def createBufferBitmap(self, width, height):
        cw, ch = self.charSize
        self.bmpBuf = Bitmap(
            width *cw,              # bitmap width
            height*ch,              # bitmap heigh
            BITMAP_SCREEN_DEPTH)    # bitmap depth
        dc = MemoryDC()               
        dc.SelectObject(self.bmpBuf)
        dc.SetBackground(self.brushes['bkgd'])
        dc.Clear()
        dc.SelectObject(NullBitmap)
        self.Panel.BackgroundBitmap = self.bmpBuf
        self.screenSize = width, height
        return

    def setFramePosition(self):
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
        X, Y = self.scroll
        cw, ch = self.charSize
        sl, sr, st, sb = 5, 15, 5, 5
        cl, rw = self.screenSize
        dc = MemoryDC()               
        dc.SelectObject(self.bmpBuf)
        dc.SetBackground(self.brushes['bkgd'])
        dc.Clear()
        x3, x4 = 0*cw, cl*cw
        x1, y1 = (sl-0.5)*cw, (st-0.5)*ch
        x2, y2 = (cl-sr+0.5)*cw, (rw-sb+0.5)*ch
        dc.SetPen(self.pens['margin'])
        dc.DrawLine(x1, y1, x1, y2)
        dc.DrawLine(x2, y1, x2, y2)
        dc.DrawLine(x3, y1, x4, y1)
        dc.DrawLine(x3, y2, x4, y2)
        c1, r1, c2, r2 = self.getBlockGeometry()
        dc.SetBrush(Brush(Colour(100,100,100)))
        dc.SetPen(self.pens['transparent'])
        x, y = 0, -1
        for line in self.chrBuf[Y:]:
            y += 1
            if y+st >= rw-sb: break
            self.drawText(dc, f'{y+Y:4d}', 0, y+st, self.numberChars)
            if y+Y < r1 or y+Y > r2:
                self.drawText(dc, line[X:], x+sl, y+st, self.normalChars)
                continue
            if r1 == r2:
                self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
                self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
                self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
                continue
            if y+Y == r1:
                self.drawText(dc, line[X:]+'¶',   x+sl, y+st, self.selectedChars)
                self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
                continue
            if y+Y == r2:
                self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
                self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
                continue
            self.drawText(dc, line[X:]+'¶', x+sl, y+st, self.selectedChars)
        x, y = self.cursor
        x1, y1, y2 = (x+sl)*cw, (y+st)*ch, (y+st+1)*ch-1
        dc.SetPen(self.pens['cursor'])
        dc.DrawLine(x1, y1, x1, y2)
        dc.SelectObject(NullBitmap)
        return

    def shiftToColumn(self, c):
        cl, rw = self.screenSize
        sl, sr, st, sb = 5, 15, 5, 5
        X, Y = self.scroll
        x, y = self.cursor
        if x+X > c:
            x = c-X
            b = 0
            if x < b:
                x = b
                X = c-b
                if X < 0:
                    X = 0
                    x = c
        if x+X < c:
            x = c-X
            b = cl-(sl+sr) 
            if x > b:
                x = b
                X = c-b
        self.cursor = x, y
        self.scroll = X, Y
        return

    def shiftToRow(self, r):
        cl, rw = self.screenSize
        sl, sr, st, sb = 5, 15, 5, 5
        X, Y = self.scroll
        x, y = self.cursor
        if y+Y > r:
            y = r-Y
            b = 0
            if y < b:
                y = b
                Y = r-b
                if Y < 0:
                    Y = 0
                    y = r
        if y+Y < r:
            y = r-Y
            b = rw-(st+sb)-1 
            if y > b:
                y = b
                Y = r-b
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
        self.cursor = x, y
        self.scroll = X, Y
        return True

    def splitLine(self):
        X, Y = self.scroll
        x, y = self.cursor
        line = self.chrBuf[y+Y]
        left, right = line[:x+X], line[x+X:]
        self.chrBuf[y+Y] = left
        indent = len(left) - len(left.lstrip())
        self.chrBuf.insert(y+Y+1, indent*' '+right)
        self.moveDown()
        self.shiftToColumn(indent)
        return True

    def deleteBack(self):
        X, Y = self.scroll
        x, y = self.cursor
        if x+X > 0:
            self.moveLeft()            
            self.deleteAhead()
            return True
        if y+Y > 0:
            self.moveUp()
            self.moveEnd()            
            self.deleteAhead()
            return True
        # nop
        return False

    def deleteAhead(self):
        X, Y = self.scroll
        x, y = self.cursor
        line = list(self.chrBuf[y+Y])
        if x+X < len(line):
            line.pop(x+X)
            self.chrBuf[y+Y] = ''.join(line)
            return True
        if y+Y < len(self.chrBuf)-1:
            self.chrBuf[y+Y] = ''.join(line)
            self.chrBuf[y+Y] += self.chrBuf[y+Y+1]
            self.chrBuf.pop(y+Y+1)
            return True
        return False

    def insertChar(self, c):
        X, Y = self.scroll
        x, y = self.cursor
        line = list(self.chrBuf[y+Y])
        line.insert(x+X, chr(c))
        self.chrBuf[y+Y] = ''.join(line)
        self.shiftToColumn(x+X+1)
        return True

    def moveUp(self):
        X, Y = self.scroll
        x, y = self.cursor
        if y+Y > 0:
            self.shiftToRow(y+Y-1)
            l = len(self.chrBuf[y+Y-1])
            if x+X > l: self.shiftToColumn(l)
            return True
        return

    def moveDown(self):
        X, Y = self.scroll
        x, y = self.cursor
        if y+Y < len(self.chrBuf)-1:
            self.shiftToRow(y+Y+1)
            l = len(self.chrBuf[y+Y+1])
            if x+X > l: self.shiftToColumn(l)
            return True
        return

    def moveHome(self):
        self.shiftToColumn(0)
        return True

    def moveEnd(self):
        X, Y = self.scroll
        x, y = self.cursor
        l = len(self.chrBuf[y+Y])
        self.shiftToColumn(l)
        return True

    def moveLeft(self):
        X, Y = self.scroll
        x, y = self.cursor
        if (x+X) > 0:
            self.shiftToColumn(x+X-1)
            return True
        if (y+Y) > 0:
            self.shiftToRow(y+Y-1)
            self.moveEnd()
            return True
        return False

    def moveRight(self):
        X, Y = self.scroll
        x, y = self.cursor
        if (x+X) < len(self.chrBuf[y+Y]):
            self.shiftToColumn(x+X+1)
            return True
        if (y+Y) < len(self.chrBuf)-1:
            self.shiftToRow(y+Y+1)
            self.shiftToColumn(0)
            return True
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
        if r1 == r2:
            if c1 > c2:
                return c2, r2, c1, r1
        if r1 > r2:
            return c2, r2, c1, r1
        return c1, r1, c2, r2

    def blockSelected(self):
        b = self.blockBegin
        e = self.blockEnd
        return not b == e

    def deleteBlock(self):
        X, Y = self.scroll
        x, y = self.cursor
        c1, r1, c2, r2 = self.getBlockGeometry()
        if r1 == r2:
            line = self.chrBuf[y+Y]
            self.chrBuf[y+Y] = line[:c1]+line[c2:]
            self.shiftToColumn(c1)
        else:
            startLeft = self.chrBuf[r1][:c1]
            endRight  = self.chrBuf[r2][c2:]
            self.chrBuf[r1] = startLeft + endRight
            del self.chrBuf[r1+1:r2+1]
            self.shiftToRow(r1)
            self.shiftToColumn(c1)
        self.setBlockBegin()
        return True

    def copyBlock(self):
        self.clipboard = []
        X, Y = self.scroll
        x, y = self.cursor
        c1, r1, c2, r2 = self.getBlockGeometry()
        if r1 == r2:
            line = self.chrBuf[y+Y][c1:c2]
            self.clipboard.append(line)
        else:
            firstline = self.chrBuf[r1][c1:]
            self.clipboard.append(firstline)
            for r in range(r1+1,r2):
                newline = self.chrBuf[r]
                self.clipboard.append(newline)
            lastline = self.chrBuf[r2][:c2]
            self.clipboard.append(lastline)
        return

    def cutBlock(self):
        self.copyBlock()
        self.deleteBlock()
        return

    def pasteClipboard(self):
        if self.clipboard:
            buffer = self.clipboard.copy()
            X, Y = self.scroll
            x, y = self.cursor
            line = self.chrBuf.pop(y+Y)
            left, right = line[:x+X], line[x+X:]
            buffer[0] = left + buffer[0]
            l = len(buffer[-1])
            buffer[-1] = buffer[-1] + right
            for i, line in enumerate(buffer):
                self.chrBuf.insert(y+Y+i, line)
            self.shiftToRow(y+Y+i)
            self.shiftToColumn(l)
            self.setBlockBegin()
            return True
        return False

    def shiftLeft(self):
        X, Y = self.scroll
        x, y = self.cursor
        line = ''.join(reversed(self.chrBuf[y+Y]))
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
        if (y+Y) > 0:
            self.shiftToRow(y+Y-1)
            self.moveEnd()
            return True
        return False

    def shiftRight(self):
        X, Y = self.scroll
        x, y = self.cursor
        line = self.chrBuf[y+Y]
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
        if (y+Y) < len(self.chrBuf)-1:
            self.shiftToRow(y+Y+1)
            self.shiftToColumn(0)
            return True
        return False

    def selectAll(self):
        self.moveBottom()
        self.blockBegin = 0, 0
        self.setBlockEnd()
        return True

    def shiftTab(self):
        tabSize = 4
        X, Y = self.scroll
        x, y = self.cursor
        line = self.chrBuf[y+Y]
        left, right = line[:x+X], line[x+X:]
        nextTab = (x+X)//tabSize+1
        spaces = tabSize*nextTab-(x+X)
        self.chrBuf[y+Y] = left+spaces*' '+right
        self.shiftToColumn(x+Y+spaces)
        return True

    def _OnKeyDown(self, event):
        key = event.GetKeyCode()
        if key == WXK_ESCAPE:
            self._quitRequest(event)
        case = {
            WXK_UP    : self.moveUp,
            WXK_DOWN  : self.moveDown,
            WXK_HOME  : self.moveHome,
            WXK_END   : self.moveEnd,
            WXK_LEFT  : self.moveLeft,
            WXK_RIGHT : self.moveRight}
        if event.GetModifiers() == MOD_NONE:
            if key in case.keys():
                case[key]()
                self.setBlockBegin()
                self.refreshBuffer()
                self.Panel.Refresh()
        if event.GetModifiers() == MOD_SHIFT:
            if key in case.keys():
                if case[key]():
                    # move block extent
                    self.setBlockEnd()
                    self.refreshBuffer()
                    self.Panel.Refresh()
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
        if event.GetModifiers() == MOD_NONE:
            if key == WXK_RETURN or key == WXK_NUMPAD_ENTER:
                if self.splitLine():
                    self.setBlockBegin()
                    self.refreshBuffer()
                    self.Panel.Refresh()
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
        if event.GetModifiers() == MOD_NONE:
            if key == WXK_TAB:
                if self.shiftTab():
                    self.setBlockBegin()
                    self.refreshBuffer()
                    self.Panel.Refresh()
        event.Skip()
        return

    def _OnChar(self, event):
        key = event.GetUnicodeKey()
        if chr(key) in self.charSet:
            if self.blockSelected():
                self.deleteBlock()
            self.insertChar(key)
            self.setBlockBegin()
            self.refreshBuffer()
            self.Panel.Refresh()
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
