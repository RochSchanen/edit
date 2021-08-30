# editor.py

from wx import Colour                       # colours
from wx import Brush, BRUSHSTYLE_SOLID      # brushes
from wx import Font                         # fonts
from wx import MemoryDC, NullBitmap         # DC
from wx import Bitmap, BITMAP_SCREEN_DEPTH  # bitmaps
from wx import Pen, PENSTYLE_SOLID          # pens
from wx import WXK_RIGHT, WXK_LEFT          # keyboard     
from wx import WXK_DOWN, WXK_UP             # keyboard
from wx import WXK_HOME, WXK_END            # keyboard
from wx import MOD_CONTROL, MOD_SHIFT       # keyboard
from wx import WXK_DELETE, WXK_BACK         # keyboard
from wx import WXK_RETURN, WXK_NUMPAD_ENTER # keyboard
from wx import WXK_CONTROL_A, WXK_CONTROL_C # keyboard
from wx import WXK_CONTROL_V, WXK_CONTROL_X # keyboard
from wx import WXK_TAB                      # keyboard

class Screen():

    # INITIALISE ##############################################################

    def __init__(self, columns, rows):
        # get geometry
        sl, sr, st, sb = self._borders
        # record parameters
        self.screenSize = columns+sl+sr, rows+st+sb
        # create character set
        self.CS = CharacterSet()
        # get character geometry
        _cw, _ch = self.CS.get(' ').GetSize()
        # record parameters
        self.charSize = _cw, _ch 
        # create pens
        self.createSolidPen('_borders', 80, 80, 80)
        self.createSolidPen('_borderLeft', 150, 50, 50)
        self.createSolidPen('_cursor', 255, 180, 100, width = 2)
        # define bitmap parameters
        w, h, d = (columns+sl+sr)*_cw, (rows+st+sb)*_ch, BITMAP_SCREEN_DEPTH        
        # create screen bitmap
        self.bitmapBuffer = Bitmap(w, h, d)
        # create blank bitmap (see comment for _BlankScreen)
        self.bitmapBlank = self._BlankScreen(w, h, d)
        # create empty buffer
        self.textBuffer = ['']
        # done
        self._refresh()
        return

    # --- windows FIX ---
    # symptoms:
    # _CLEAR is too slow on windows 10
    # _CLEAR is fine on ubuntu 20.4
    # fix:
    # the code tries to stay close to the equivalent of
    # a video text mode style where the screen is cleared
    # by filling it up with spacescharacters. however the
    # dc.DrawBitmap(c, x*cw, y*ch) command seems to be
    # slowing the out on windows 10 (it was working fine
    # on linux ubuntu 20.4) so a bitmapBlank buffer is
    # build to accelerate the screen _Clear method.
    def _BlankScreen(self, w, h, d):
        b = Bitmap(w, h, d)
        dc = MemoryDC()
        dc.SelectObject(b)
        self._clear(dc)
        dc.SelectObject(NullBitmap)
        return b

    # PENS ####################################################################

    # list of pens that are easely accessible

    _pens = {}

    def createSolidPen(self, name, R, G, B, width = 1):
        pen = Pen()
        pen.SetWidth(width)
        pen.SetStyle(PENSTYLE_SOLID)
        pen.SetColour(Colour(R, G, B))
        self._pens[name] = pen
        return

    # REFRESH BUFFER ##########################################################

    _borders = 5, 5, 3, 3
    # _borders = 7, 1, 1, 1

    # (use video character?)
    def drawBorders(self, dc):
        cl, rw = self.screenSize
        sl, sr, st, sb = self._borders
        cw, ch = self.charSize
        x3, x4 = 0*cw, cl*cw
        x1, y1 = (sl-0.5)*cw, (st-0.5)*ch
        x2, y2 = (cl-sr+0.5)*cw, (rw-sb+0.5)*ch
        dc.SetPen(self._pens['_borderLeft'])
        dc.DrawLine(x1, y1, x1, y2)
        dc.SetPen(self._pens['_borders'])
        dc.DrawLine(x2, y1, x2, y2)
        dc.DrawLine(x3, y1, x4, y1)
        dc.DrawLine(x3, y2, x4, y2)
        return

    cursor = 0, 0

    # (use video characters?)
    def drawCursor(self, dc):
        # get geometry
        cw, ch = self.charSize
        sl, sr, st, sb = self._borders
        # get cursor state
        x, y = self.cursor
        # get line coordinates
        x1, y1, y2 = (x+sl)*cw, (y+st)*ch, (y+st+1)*ch-1
        # set pen
        dc.SetPen(self._pens['_cursor'])
        # draw cursor line
        dc.DrawLine(x1, y1, x1, y2)
        return

    bitmapBlank = None

    # _CLEAR is too slow on windows 10
    # _CLEAR is fine on ubuntu 20.4
    # the code maps to a text mode style where the
    # screen is cleared by filling it up with spaces characters
    # howwever the dc.DrawBitmap(c, x*cw, y*ch) command is too
    # slow on windows 10 (ok with linux ubuntu 20.4)
    # so a blankScreen buffer is build on first call to accelerate
    # screen clear function. Unfortunately, the cursor now leaves
    # a trace at position 0, 0. This needs fixing

    blankScreen = None

    def _clear(self, dc):
        # clear using bitmapBlank
        if self.bitmapBlank:
            dc.DrawBitmap(self.bitmapBlank, 0, 0)
            # done
            return
        # clear dc using spaces (texture)
        cw, ch = self.charSize
        cl, rw = self.screenSize
        # get normal space character bitmap
        c = self.CS.get(' ', 'nrm')
        # fill screen
        for x in range(cl):
            for y in range(rw):
              dc.DrawBitmap(c, x*cw, y*ch)
        # done
        return

    def getBlockGeometry(self):
        c1, r1 = self.blockBegin
        c2, r2 = self.blockEnd
        reverse = (c2, r2, c1, r1)
        if r1 > r2: return reverse
        if r1 == r2 and c1 > c2: return reverse
        return c1, r1, c2, r2

    def isSelected(self, c, r):
        c1, r1, c2, r2 = self.getBlockGeometry()
        if r < r1 or r > r2: return False
        if r == r1 and c < c1: return False
        if r == r2 and c >= c2: return False
        return True

    scroll = 0, 0

    def _refresh(self):
        # get geometry
        X, Y = self.scroll
        cw, ch = self.charSize
        sl, sr, st, sb = self._borders
        cl, rw = self.screenSize
        # create device context
        dc = MemoryDC()               
        # select bitmap
        dc.SelectObject(self.bitmapBuffer)
        # clear buffer
        self._clear(dc)
        # draw _borders
        self.drawBorders(dc)
        # draw each lines
        for y, line in enumerate(self.textBuffer[Y:]):
            # check for last visible line
            if y+st >= rw-sb: break
            # get line number
            lineNumber = f'{y+Y:{sl-1}d}'
            # draw number
            for x, c in enumerate(lineNumber):
                # get character position
                u, v = x*cw, (y+st)*ch
                # draw character
                dc.DrawBitmap(self.CS.get(c, 'emp'), u, v)
            # draw line
            # x = 0 # empty line jumps straight to else case
            for x, c in enumerate(line[X:]+'¶'):
                # check for last visible character
                if x+sl >= cl-sr: break
                # check if character selected
                selected = self.isSelected(x+X, y+Y)
                # adjust display style
                style = 'sel' if selected else 'nrm'
                # get screen position
                u, v = (x+sl)*cw, (y+st)*ch
                # draw character
                dc.DrawBitmap(self.CS.get(c, style), u, v)
        # draw cursor
        self.drawCursor(dc)
        # done
        dc.SelectObject(NullBitmap)
        return

    # JUMP, GOTO ##############################################################

    # c is the character position in the line
    # x is the position in the screen
    # X is the scrolling horizontal shift
    # we must keep X+x == c at the end of any action

    _triggers = 10, 10, 5, 5
    # _triggers = 10, 10, 5, 5

    def jumpRight(self, c):
        # get geometry and state and boundaries
        tl, tr, tt, tb = self._triggers
        sl, sr, st, sb = self._borders
        cl, rw = self.screenSize
        X, Y = self.scroll
        x, y = self.cursor
        # jump to the right at new position c
        x = c-X             # new cursor pos
        b = cl-(sl+sr)-tr-1 # calculate boundary
        if x > b:           # check boundary (True if crossed)
            x = b           # place cursor at the boundary
            X = c-b         # scroll screen respecting the constraint x+X==c
            # there no limit to scrolling the screen to the right
        # done
        self.cursor = x, y
        self.scroll = X, Y
        return

    def jumpLeft(self, c):
        # get geometry and state
        tl, tr, tt, tb = self._triggers
        sl, sr, st, sb = self._borders
        cl, rw = self.screenSize
        X, Y = self.scroll
        x, y = self.cursor
        # jump to the left at new position c
        x = c-X             # new cursor position
        b = tl              # calculate boundary
        if x < b:           # check boundary (True if crossed)
            x = b           # place cursor at the boundary
            X = c-b         # scroll screen respecting the constraint x+X==c
            # there is a limit to scrolling the screen to the left
            if X < 0:       # scrolling cannot be negative
                X = 0       # place scroll position at the boundary
                x = c       # place cursor respecting the constraint x+X==c
        # done
        self.cursor = x, y
        self.scroll = X, Y
        return

    def gotoColumn(self, c):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check direction
        if c > x+X : self.jumpRight(c)
        if c < x+X : self.jumpLeft(c)
        # done
        return

    # r is the line position in the text buffer
    # y is the position in the screen
    # Y is the scrolling vertical shift
    # we must keep y+Y == r at the end of any action

    def jumpDown(self, r):
        # get geometry and state
        tl, tr, tt, tb = self._triggers
        sl, sr, st, sb = self._borders
        cl, rw = self.screenSize
        X, Y = self.scroll
        x, y = self.cursor
        # jump down to row r
        y = r-Y             # new cursor pos
        b = rw-(st+sb)-tb-1 # calculate boundary
        if y > b:           # check boundary (True if crossed)
            y = b           # place cursor at the boundary
            Y = r-b         # scroll screen respecting the constraint y+Y==r
            # there no limit to scrolling the screen down
        # done
        self.cursor = x, y
        self.scroll = X, Y
        return

    def jumpUp(self, r):
        # get geometry and state
        tl, tr, tt, tb = self._triggers
        sl, sr, st, sb = self._borders
        cl, rw = self.screenSize
        X, Y = self.scroll
        x, y = self.cursor
        # jump up to row r
        y = r-Y             # new cursor position
        b = tt              # calculate boundary
        if y < b:           # check boundary (True if crossed)
            y = b           # place cursor at the boundary
            Y = r-b         # scroll screen respecting the constraint y+Y==r
            # there is a limit to scrolling the screen to the top
            if Y < 0:       # scrolling cannot be negative
                Y = 0       # place scroll position at the boundary
                y = r       # place cursor respecting the constraint y+Y==r
        # done
        self.cursor = x, y
        self.scroll = X, Y
        return

    def gotoRow(self, r):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check direction
        if r > y+Y : self.jumpDown(r)
        if r < y+Y : self.jumpUp(r)
        # done
        return

    # MOVE RIGHT, LEFT, DOWN, UP ##############################################

    # motions of the cursor must respect
    # the content of the text buffer

    def moveRight(self):
        # get geometry and state
        X, Y = self.scroll
        x, y = self.cursor
        # check end-of-buffer
        if (x+X) < len(self.textBuffer[y+Y]):
            self.gotoColumn(x+X+1)
            return True
        if (y+Y) < len(self.textBuffer)-1:
            self.gotoRow(y+Y+1)
            self.gotoColumn(0)
            return True
        # nop
        return False

    def moveLeft(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check start-of-buffer
        if (x+X) > 0:
            self.gotoColumn(x+X-1)
            return True
        if (y+Y) > 0:
            self.gotoRow(y+Y-1)
            self.moveEnd()
            return True
        # nop
        return False

    def moveDown(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check end-of-buffers
        if y+Y < len(self.textBuffer)-1:
            self.gotoRow(y+Y+1)
            l = len(self.textBuffer[y+Y+1])
            if x+X > l: self.gotoColumn(l)
            return True
        # nop
        return

    def moveUp(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # check start-of-buffers
        if y+Y > 0:
            self.gotoRow(y+Y-1)
            l = len(self.textBuffer[y+Y-1])
            if x+X > l: self.gotoColumn(l)
            return True
        # nop
        return

    # MOVE START, END, TOP, BOTTOM ############################################

    def moveStart(self):
        # goto the begining of the line
        self.gotoColumn(0)
        return True

    def moveEnd(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # goto the end of the line
        self.gotoColumn(len(self.textBuffer[y+Y]))
        return True

    def moveTop(self):
        # go to top-left corner
        self.gotoRow(0)
        self.gotoColumn(0)
        return True

    def moveBottom(self):
        # go to bottom-right corner
        l = len(self.textBuffer)
        self.gotoRow(l-1)
        self.moveEnd()
        return True

    # MOVE TO NEXT WORD (START OR END) ########################################

    wordSet = ''.join([
        'abcdefghijklmnopqrstuvwxyz',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        '0123456789',
        '_'])

    def wordRight(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = self.textBuffer[y+Y]
        # check end-of-line
        if x+X < len(line):
            k = x+X
            if line[k] in self.wordSet:
                for i, c in enumerate(line[x+X:]):
                    if c not in self.wordSet: break
                else: i+=1
                self.gotoColumn(x+X+i)
                return True
            if line[k] not in self.wordSet:
                for i, c in enumerate(line[x+X:]):
                    if c in self.wordSet: break
                else: i+=1
                self.gotoColumn(x+X+i)
            return True
        # check end-of-lines
        if (y+Y) < len(self.textBuffer)-1:
            self.gotoRow(y+Y+1)
            self.gotoColumn(0)
            return True
        # nop
        return False

    def wordLeft(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = ''.join(reversed(self.textBuffer[y+Y]))
        # check start-of-line
        if x+X > 0:
            k = len(line)-(x+X)
            if line[k] in self.wordSet:
                for i, c in enumerate(line[k:]):
                    if c not in self.wordSet: break
                else: i+=1
                self.gotoColumn(x+X-i)
                return True
            if line[k] not in self.wordSet:
                for i, c in enumerate(line[k:]):
                    if c in self.wordSet: break
                else: i+=1
                self.gotoColumn(x+X-i)
                return True
        # check start-of-lines
        if (y+Y) > 0:
            self.gotoRow(y+Y-1)
            self.moveEnd()
            return True
        # nop
        return False

    # INSERT OR DELETE CHARACTERS OR LINES ####################################

    def insertChar(self, c):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.textBuffer[y+Y])
        # insert char
        line.insert(x+X, chr(c))
        # update buffer
        self.textBuffer[y+Y] = ''.join(line)
        # move right
        self.gotoColumn(x+X+1)
        return True

    def splitLine(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line and split
        line = self.textBuffer[y+Y]
        left, right = line[:x+X], line[x+X:]
        # current line keeps left string
        self.textBuffer[y+Y] = left
        # get indent from left spaces
        indent = len(left) - len(left.lstrip())
        # insert new line with indented right string
        self.textBuffer.insert(y+Y+1, indent*' '+right)
        # place cursor
        self.moveDown()
        self.gotoColumn(indent)
        # done
        return True

    def deleteAhead(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line
        line = list(self.textBuffer[y+Y])
        # check end-of-buffer
        if x+X < len(line):
            # delete one character
            line.pop(x+X)
            self.textBuffer[y+Y] = ''.join(line)
            return True
        # check end-of-buffers
        if y+Y < len(self.textBuffer)-1:
            # update buffer
            self.textBuffer[y+Y] = ''.join(line)
            # adjoint next buffer
            self.textBuffer[y+Y] += self.textBuffer[y+Y+1]
            # delete next buffer
            self.textBuffer.pop(y+Y+1)
            # done
            return True
        # nop
        return False

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

    # BLOCK SELECTION #########################################################

    blockBegin = 0, 0
    blockEnd   = 0, 0

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

    def blockSelected(self):
        b = self.blockBegin
        e = self.blockEnd
        return not b == e

    def selectAll(self):
        self.moveBottom()
        self.blockBegin = 0, 0
        self.setBlockEnd()
        return True

    # COPY/PASTE/DELETE BLOCK #################################################

    def deleteBlock(self):
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get block geometry
        c1, r1, c2, r2 = self.getBlockGeometry()
        # one line block
        if r1 == r2:
            # get line
            line = self.textBuffer[y+Y]
            # delete
            self.textBuffer[y+Y] = line[:c1]+line[c2:]
            # move to blockBegin
            self.gotoColumn(c1)
        # multi-lines block
        else:
            startLeft = self.textBuffer[r1][:c1]
            endRight  = self.textBuffer[r2][c2:]
            # collect parts into one line
            self.textBuffer[r1] = startLeft + endRight
            # delete full lines
            del self.textBuffer[r1+1:r2+1]
            # move to blockBegin
            self.gotoRow(r1)
            self.gotoColumn(c1)
        # done
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
            line = self.textBuffer[y+Y][c1:c2]
            self.clipboard.append(line)
        # multi-lines block
        else:
            firstline = self.textBuffer[r1][c1:]
            self.clipboard.append(firstline)
            for r in range(r1+1,r2):
                newline = self.textBuffer[r]
                self.clipboard.append(newline)
            lastline = self.textBuffer[r2][:c2]
            self.clipboard.append(lastline)
        # done
        return

    def cutBlock(self):
        self.copyBlock()
        self.deleteBlock()
        self.setBlockBegin()
        return

    def pasteClipboard(self):
        # delete block first
        if self.blockSelected():
            self.deleteBlock()
        # check if clipboard not empty
        if self.clipboard:
            # make a shallow copy
            buffer = self.clipboard.copy()
            # get state
            X, Y = self.scroll
            x, y = self.cursor
            # remove and save current line
            line = self.textBuffer.pop(y+Y)
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
                self.textBuffer.insert(y+Y+i, line)
            # re-position the cursor
            self.gotoRow(y+Y+i)
            self.gotoColumn(l)
            # deselect block
            self.setBlockBegin()
            # done
            return True
        # nop
        return False

    # TABULATION ##############################################################

    def insertTab(self):
        tabSize = 4
        # get state
        X, Y = self.scroll
        x, y = self.cursor
        # get line and split
        line = self.textBuffer[y+Y]
        left, right = line[:x+X], line[x+X:]
        # get next tab number
        nextTab = (x+X)//tabSize+1
        # compute spaces
        spaces = tabSize*nextTab-(x+X)
        # insert new spaces
        self.textBuffer[y+Y] = left+spaces*' '+right
        # adjust cursor position
        self.gotoColumn(x+X+spaces)
        return True

    def deleteTab(self):
        # to implement
        return

    # PROCESS KEYBOARD INPUT CHARACTERS #######################################

    def Nop(self):
        return False

    def processChar(self, event):
        # get unicode from event
        key = event.GetUnicodeKey()
        # check charset
        if chr(key) in self.CS._CharSet:
            if self.blockSelected():
                self.deleteBlock()
            self.insertChar(key)
            self.setBlockBegin()
        # get key code from event
        key = event.GetKeyCode()
        # CURSOR MOTION AND SELECTION
        case = {        # MOD_NONE       # MOD_CONTROL
            WXK_HOME  : [self.moveStart, self.moveTop],
            WXK_END   : [self.moveEnd,   self.moveBottom],
            WXK_UP    : [self.moveUp,    self.Nop],
            WXK_DOWN  : [self.moveDown,  self.Nop],
            WXK_LEFT  : [self.moveLeft,  self.wordLeft],
            WXK_RIGHT : [self.moveRight, self.wordRight]}
        # check key case
        if key in case.keys():
            M = event.GetModifiers()
            # check modifiers are none other than...
            if M & (MOD_CONTROL+MOD_SHIFT) == M:
                C = 1 if M & MOD_CONTROL else 0 # CONTTROL BIT
                S = 1 if M & MOD_SHIFT   else 0 # SHIFT BIT
                case[key][C]()
                if S: self.setBlockEnd()   # extend block
                else: self.setBlockBegin() # release block
        # RETURN/ENTER:
        if not event.GetModifiers():
            if key in [WXK_RETURN, WXK_NUMPAD_ENTER]:
                if self.blockSelected():
                    self.deleteBlock()
                self.splitLine()
                self.setBlockBegin()
        # DELETE/BACKSPACE:
        case = {
            WXK_BACK   : self.deleteBack,
            WXK_DELETE : self.deleteAhead}
        if not event.GetModifiers():
            if key in case.keys():
                if self.blockSelected():
                    self.deleteBlock()
                    self.setBlockBegin()
                else: case[key]()
        # CONTROL C/V/X/A:
        case = {
            WXK_CONTROL_A : self.selectAll,
            WXK_CONTROL_C : self.copyBlock,
            WXK_CONTROL_X : self.cutBlock,
            WXK_CONTROL_V : self.pasteClipboard}
        if event.GetModifiers() == MOD_CONTROL:
            if key in case.keys(): case[key]()
        # TAB
        if not event.GetModifiers():
            if key == WXK_TAB:
                if self.blockSelected():
                    self.deleteBlock()
                self.insertTab()
                self.setBlockBegin()
        #done
        self._refresh()
        return

# BUILD CHARACTER BITMAP SETS #################################################

# for windows 10 : install font found in data
# to do : make a bitmap character table that
# can be used independently from any platform

class CharacterSet():

    _colours = {}
    _brushes = {}
    _CharSet = []
    _fonts = {}
    _CharBitmaps = {}

    def __init__(self):
        # make colours
        self._createColour('txt', 230, 230, 230) # normal text forecolor
        self._createColour('bgd',  52,  61,  70) # normal text background
        self._createColour('slF', 230, 230, 230) # selected text forecolor
        self._createColour('slB', 100, 100, 100) # selected text background
        self._createColour('emp', 150, 150, 200) # emphasised text color
        # make solid brushes
        for c in self._colours.keys(): self._createSolidBrush(c, c)
        # make character set
        self._createPrintableCharSet()
        # make font
        # self._createFont('mono', 'MonoSpace', 11)
        # self._createFont('mono', 'Ubuntu Mono', 11)
        # self._createFont('mono', 'Ubuntu Mono', 15)
        # self._createFont('mono', 'Ubuntu Mono', 11)
        self._createFont('mono', 'Ac437 IBM VGA 8x16', 12)

        # make character bitmaps
        self._createCharBitmap('nrm', 'mono', 'txt', 'bgd')
        self._createCharBitmap('sel', 'mono', 'slF', 'slB')
        self._createCharBitmap('emp', 'mono', 'emp', 'bgd')
        self._createCharBitmap('cur', 'mono', 'bgd', 'txt')

        # done
        return

    def get(self, character, charSet = 'nrm'):
        s = self._CharBitmaps[charSet]
        return s[character]

    def _createColour(self, name, R, G, B):
        # add color to dictionary
        self._colours[name] = Colour(R,G,B)
        # done
        return

    def _createSolidBrush(self, brushName, colourName):
        # make brush
        brush = Brush()
        brush.SetStyle(BRUSHSTYLE_SOLID)
        brush.SetColour(self._colours[colourName])
        # add brush
        self._brushes[brushName] = brush
        # done
        return

    def _createPrintableCharSet(self):
        # make the standard  ascii table
        printascii = list(map(chr, range(32, 126)))
        # add to set
        self._CharSet.extend(printascii)
        # add extra characters (uk keyboard, no Alt Gr)
        self._CharSet.extend(['¬','£','~'])
        # add extra characters (editor symbols)
        self._CharSet.extend(['¶'])  
        # done
        return

    def _createFont(self, name, face, size):
        # make font
        font = Font()
        font.SetFaceName(face)
        font.SetPointSize(size)
        # add to dictionary
        self._fonts[name] = font
        # done
        return

    def _createCharBitmap(self, name, font, foreground, background):
        # create device context
        dc = MemoryDC()               
        # set font
        dc.SetFont(self._fonts[font])
        # get font size
        _cw, _ch = dc.GetTextExtent(' ')
        BitmapSet = {}
        for c in self._CharSet:
            # create bitmap
            bitmap = Bitmap(_cw, _ch, BITMAP_SCREEN_DEPTH)
            # select bitmap
            dc.SelectObject(bitmap)
            # set background
            dc.SetBackground(self._brushes[background])
            # clear bitmap
            dc.Clear()
            # set text color
            dc.SetTextForeground(self._colours[foreground])
            # record reference
            BitmapSet[c] = bitmap
            # check alternate drawing 1
            if name == 'nrm' and c == '¶':
                dc.DrawText(' ',0,0)
                continue
            # check alternate drawing 2
            if name == 'sel' and c == ' ':
                dc.DrawText('·',0,0)
                continue
            # draw character
            dc.DrawText(c,0,0) 
        # release bitmap
        dc.SelectObject(NullBitmap)
        # record set
        self._CharBitmaps[name] = BitmapSet
        # done
        return
