
# from wx import Point # only in Frame.SetPosition()

# from wx import WXK_ESCAPE
# from wx import WXK_HOME
# from wx import WXK_END
# from wx import WXK_DELETE
# from wx import WXK_BACK
# from wx import WXK_LEFT
# from wx import WXK_RIGHT
# from wx import WXK_UP
# from wx import WXK_DOWN
# from wx import WXK_RETURN
# from wx import WXK_NUMPAD_ENTER
# from wx import WXK_CONTROL_A
# from wx import WXK_CONTROL_C
# from wx import WXK_TAB
# from wx import EVT_CHAR
# from wx import MOD_NONE
# from wx import MOD_CONTROL
# from wx import MOD_SHIFT
# from wx import MOD_ALT


#     def setFramePosition(self):
#         # adjust frame position
#         scrw, scrh = 3840, 1200 # screen size
#         w, h = self.Panel.BackgroundBitmap.GetSize()
#         self.Frame.SetPosition(Point(scrw/4-80*8/2, 200))
#         return

#     def drawText(self, dc, text, x, y, charBitmap):
#         cw, ch = self.charSize
#         cl, rw = self.screenSize
#         sl, sr, st, sb = 5, 15, 5, 5
#         for c in text:
#             if x >= cl-sr: break
#             dc.DrawBitmap(charBitmap[c], x*cw, y*ch)
#             x += 1
#         # done
#         return

#     def refreshBuffer(self):
#         # get geometry
#         X, Y = self.scroll
#         cw, ch = self.charSize
#         sl, sr, st, sb = 5, 15, 5, 5
#         cl, rw = self.screenSize
#         # create device context
#         dc = MemoryDC()               
#         # select
#         dc.SelectObject(self.bmpBuf)
#         # set background
#         dc.SetBackground(self.brushes['bkgd'])
#         # and clear buffer
#         dc.Clear()

#         # draw margins
#         x3, x4 = 0*cw, cl*cw
#         x1, y1 = (sl-0.5)*cw, (st-0.5)*ch
#         x2, y2 = (cl-sr+0.5)*cw, (rw-sb+0.5)*ch
#         dc.SetPen(self.pens['margin'])
#         dc.DrawLine(x1, y1, x1, y2)
#         dc.DrawLine(x2, y1, x2, y2)
#         dc.DrawLine(x3, y1, x4, y1)
#         dc.DrawLine(x3, y2, x4, y2)

#         # get block geometry
#         c1, r1, c2, r2 = self.getBlockGeometry()
#         # set brush
#         dc.SetBrush(Brush(Colour(100,100,100)))
#         dc.SetPen(self.pens['transparent'])

#         # draw text
#         x, y = 0, -1
#         for line in self.chrBuf[Y:]:
#             y += 1
#             if y+st >= rw-sb: break
#             # draw line number
#             self.drawText(dc, f'{y+Y:4d}', 0, y+st, self.numberChars)
#             # the line is outside of the block
#             if y+Y < r1 or y+Y > r2:
#                 self.drawText(dc, line[X:], x+sl, y+st, self.normalChars)
#                 continue
#             # block is inside if the line
#             if r1 == r2:
#                 self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
#                 self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
#                 self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
#                 continue
#             # line at the start of the block
#             if y+Y == r1:
#                 self.drawText(dc, line[X:]+'¶',   x+sl, y+st, self.selectedChars)
#                 self.drawText(dc, line[X:c1], x+sl, y+st, self.normalChars)
#                 continue
#             # line at the end of the block
#             if y+Y == r2:
#                 self.drawText(dc, line[X:],   x+sl, y+st, self.normalChars)
#                 self.drawText(dc, line[X:c2], x+sl, y+st, self.selectedChars)
#                 continue
#             # line is inside the block
#             self.drawText(dc, line[X:]+'¶', x+sl, y+st, self.selectedChars)

#         # draw cursor
#         x, y = self.cursor
#         x1, y1, y2 = (x+sl)*cw, (y+st)*ch, (y+st+1)*ch-1
#         dc.SetPen(self.pens['cursor'])
#         dc.DrawLine(x1, y1, x1, y2)

#         # done
#         dc.SelectObject(NullBitmap)
#         return

#     def shiftToColumn(self, c):
#         # get geometry and state
#         cl, rw = self.screenSize
#         sl, sr, st, sb = 5, 15, 5, 5
#         X, Y = self.scroll
#         x, y = self.cursor

#         # left shift
#         if x+X > c:
#             x = c-X
#             # check boundary
#             b = 0
#             if x < b:
#                 x = b
#                 X = c-b
#                 # check limit
#                 if X < 0:
#                     X = 0
#                     x = c

#         # right shift
#         if x+X < c:
#             x = c-X
#             # check boundary
#             b = cl-(sl+sr) 
#             if x > b:
#                 x = b
#                 X = c-b
#             # there is no scroll
#             # limit to the right

#         # done
#         self.cursor = x, y
#         self.scroll = X, Y
#         return

#     def shiftToRow(self, r):
#         # get geometry and state
#         cl, rw = self.screenSize
#         sl, sr, st, sb = 5, 15, 5, 5
#         X, Y = self.scroll
#         x, y = self.cursor

#         # up shift
#         if y+Y > r:
#             y = r-Y
#             # check boundary
#             b = 0
#             if y < b:
#                 y = b
#                 Y = r-b
#                 # check limit
#                 if Y < 0:
#                     Y = 0
#                     y = r

#         # down shift
#         if y+Y < r:
#             y = r-Y
#             # check boundary
#             b = rw-(st+sb)-1 
#             if y > b:
#                 y = b
#                 Y = r-b
#             # there is no scroll
#             # limit to the bottom

#         # done
#         self.cursor = x, y
#         self.scroll = X, Y
#         return

#     def moveBottom(self):
#         l = len(self.chrBuf)
#         self.shiftToRow(l-1)
#         self.moveEnd()
#         return True

#     def moveTop(self):
#         x, y = 0, 0
#         X, Y = 0, 0 
#         # done
#         self.cursor = x, y
#         self.scroll = X, Y
#         return True

#     def splitLine(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get line and split
#         line = self.chrBuf[y+Y]
#         left, right = line[:x+X], line[x+X:]
#         # current line keeps left string
#         self.chrBuf[y+Y] = left
#         # get indent from left spaces
#         indent = len(left) - len(left.lstrip())
#         # insert new line with indented right string
#         self.chrBuf.insert(y+Y+1, indent*' '+right)
#         # place cursor
#         self.moveDown()
#         self.shiftToColumn(indent)
#         # done
#         return True

#     def deleteBack(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # check left screen limit
#         if x+X > 0:
#             self.moveLeft()            
#             self.deleteAhead()
#             return True
#         # check top screen limit
#         if y+Y > 0:
#             self.moveUp()
#             self.moveEnd()            
#             self.deleteAhead()
#             return True
#         # nop
#         return False

#     def deleteAhead(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get line
#         line = list(self.chrBuf[y+Y])
#         # check end-of-buffer
#         if x+X < len(line):
#             # delete one character
#             line.pop(x+X)
#             self.chrBuf[y+Y] = ''.join(line)
#             return True
#         # check end-of-buffers
#         if y+Y < len(self.chrBuf)-1:
#             # update buffer
#             self.chrBuf[y+Y] = ''.join(line)
#             # adjoint next buffer
#             self.chrBuf[y+Y] += self.chrBuf[y+Y+1]
#             # delete next buffer
#             self.chrBuf.pop(y+Y+1)
#             # done
#             return True
#         # nop
#         return False

#     def insertChar(self, c):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get line
#         line = list(self.chrBuf[y+Y])
#         # insert char
#         line.insert(x+X, chr(c))
#         # update buffer
#         self.chrBuf[y+Y] = ''.join(line)
#         # move right
#         self.shiftToColumn(x+X+1)
#         return True

#     def moveUp(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # check start-of-buffers
#         if y+Y > 0:
#             self.shiftToRow(y+Y-1)
#             l = len(self.chrBuf[y+Y-1])
#             if x+X > l: self.shiftToColumn(l)
#             return True
#         # nop
#         return

#     def moveDown(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # check end-of-buffers
#         if y+Y < len(self.chrBuf)-1:
#             self.shiftToRow(y+Y+1)
#             l = len(self.chrBuf[y+Y+1])
#             if x+X > l: self.shiftToColumn(l)
#             return True
#         # nop
#         return

#     def moveHome(self):
#         self.shiftToColumn(0)
#         return True

#     def moveEnd(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get line length
#         l = len(self.chrBuf[y+Y])
#         # shift
#         self.shiftToColumn(l)
#         return True

#     def moveLeft(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # check start-of-buffer
#         if (x+X) > 0:
#             self.shiftToColumn(x+X-1)
#             return True
#         if (y+Y) > 0:
#             self.shiftToRow(y+Y-1)
#             self.moveEnd()
#             return True
#         # nop
#         return False

#     def moveRight(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # check end-of-buffer
#         if (x+X) < len(self.chrBuf[y+Y]):
#             self.shiftToColumn(x+X+1)
#             return True
#         if (y+Y) < len(self.chrBuf)-1:
#             self.shiftToRow(y+Y+1)
#             self.shiftToColumn(0)
#             return True
#         # nop
#         return False

#     def setBlockBegin(self):
#         x, y = self.cursor
#         X, Y = self.scroll
#         self.blockBegin = x+X, y+Y
#         self.blockEnd = self.blockBegin
#         return

#     def setBlockEnd(self):
#         x, y = self.cursor
#         X, Y = self.scroll
#         self.blockEnd = x+X, y+Y
#         return

#     def getBlockGeometry(self):
#         c1, r1 = self.blockBegin
#         c2, r2 = self.blockEnd
#         # order block boundaries
#         if r1 == r2:
#             if c1 > c2:
#                 # reverse order
#                 return c2, r2, c1, r1
#         if r1 > r2:
#             # reverse order
#             return c2, r2, c1, r1
#         # straight order
#         return c1, r1, c2, r2

#     def blockSelected(self):
#         b = self.blockBegin
#         e = self.blockEnd
#         return not b == e

#     def deleteBlock(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get block geometry
#         c1, r1, c2, r2 = self.getBlockGeometry()

#         # one line block
#         if r1 == r2:
#             # get line
#             line = self.chrBuf[y+Y]
#             # delete
#             self.chrBuf[y+Y] = line[:c1]+line[c2:]
#             # move to blockBegin
#             self.shiftToColumn(c1)

#         # multi-lines block
#         else:
#             startLeft = self.chrBuf[r1][:c1]
#             endRight  = self.chrBuf[r2][c2:]
#             # collect parts into one line
#             self.chrBuf[r1] = startLeft + endRight
#             # delete full lines
#             del self.chrBuf[r1+1:r2+1]
#             # move to blockBegin
#             self.shiftToRow(r1)
#             self.shiftToColumn(c1)

#         # deselect block
#         # self.setBlockBegin()
#         return True

#     def copyBlock(self):
#         # clear previous data
#         self.clipboard = []
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get block geometry
#         c1, r1, c2, r2 = self.getBlockGeometry()

#         # one line block
#         if r1 == r2:
#             line = self.chrBuf[y+Y][c1:c2]
#             self.clipboard.append(line)

#         # multi-lines block
#         else:
#             firstline = self.chrBuf[r1][c1:]
#             self.clipboard.append(firstline)
#             for r in range(r1+1,r2):
#                 newline = self.chrBuf[r]
#                 self.clipboard.append(newline)
#             lastline = self.chrBuf[r2][:c2]
#             self.clipboard.append(lastline)

#         # done
#         return

#     def cutBlock(self):
#         self.copyBlock()
#         self.deleteBlock()
#         self.setBlockBegin()
#         return

#     def pasteClipboard(self):
#         # delete block first
#         if self.blockSelected():
#             self.deleteBlock()
#         # check if clipboard not empty
#         if self.clipboard:
#             # make a shallow copy
#             buffer = self.clipboard.copy()
#             # get state
#             X, Y = self.scroll
#             x, y = self.cursor
#             # remove and save current line
#             line = self.chrBuf.pop(y+Y)
#             # split line at cursor position
#             left, right = line[:x+X], line[x+X:]
#             # add left to the first line of the buffer
#             buffer[0] = left + buffer[0]
#             # save position for repositioning the cursor
#             l = len(buffer[-1])
#             # add right to the last line of the buffer
#             buffer[-1] = buffer[-1] + right
#             # insert buffer
#             for i, line in enumerate(buffer):
#                 self.chrBuf.insert(y+Y+i, line)
#             # re-position the cursor
#             self.shiftToRow(y+Y+i)
#             self.shiftToColumn(l)
#             # deselect block
#             self.setBlockBegin()
#             # done
#             return True
#         # nop
#         return False

#     def shiftLeft(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get line
#         line = ''.join(reversed(self.chrBuf[y+Y]))

#         # check start-of-line
#         if x+X > 0:
#             k = len(line)-(x+X)
#             if line[k] in self.word:
#                 for i, c in enumerate(line[k:]):
#                     if c not in self.word: break
#                 else: i+=1
#                 self.shiftToColumn(x+X-i)
#                 return True
#             if line[k] not in self.word:
#                 for i, c in enumerate(line[k:]):
#                     if c in self.word: break
#                 else: i+=1
#                 self.shiftToColumn(x+X-i)
#                 return True

#         # check start-of-lines
#         if (y+Y) > 0:
#             self.shiftToRow(y+Y-1)
#             self.moveEnd()
#             return True

#         # nop
#         return False

#     def shiftRight(self):
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get line
#         line = self.chrBuf[y+Y]

#         # check end-of-line
#         if x+X < len(line):
#             k = x+X
#             if line[k] in self.word:
#                 for i, c in enumerate(line[x+X:]):
#                     if c not in self.word: break
#                 else: i+=1
#                 self.shiftToColumn(x+X+i)
#                 return True
#             if line[k] not in self.word:
#                 for i, c in enumerate(line[x+X:]):
#                     if c in self.word: break
#                 else: i+=1
#                 self.shiftToColumn(x+X+i)
#             return True

#         # check end-of-lines
#         if (y+Y) < len(self.chrBuf)-1:
#             self.shiftToRow(y+Y+1)
#             self.shiftToColumn(0)
#             return True

#         # nop
#         return False

#     def selectAll(self):
#         self.moveBottom()
#         self.blockBegin = 0, 0
#         self.setBlockEnd()
#         return True

#     def shiftTabRight(self):
#         tabSize = 4
#         # get state
#         X, Y = self.scroll
#         x, y = self.cursor
#         # get line and split
#         line = self.chrBuf[y+Y]
#         left, right = line[:x+X], line[x+X:]
#         # get next tab number
#         nextTab = (x+X)//tabSize+1
#         # compute spaces
#         spaces = tabSize*nextTab-(x+X)
#         # insert new spaces
#         self.chrBuf[y+Y] = left+spaces*' '+right
#         # adjust cursor position
#         self.shiftToColumn(x+Y+spaces)
#         return True

#     def Nop(self):
#         return False

#     def _OnKeyDown(self, event):

#         # get special key code
#         key = event.GetKeyCode()

#         # check for ESCAPE key
#         if key == WXK_ESCAPE:
#             self._quitRequest(event)

#         # CURSOR MOTION AND SELECTION
#         case = {        # MOD_NONE          # MOD_CONTROL
#             WXK_UP    : [self.moveUp,       self.Nop],
#             WXK_DOWN  : [self.moveDown,     self.Nop],
#             WXK_HOME  : [self.moveHome,     self.moveTop],
#             WXK_END   : [self.moveEnd,      self.moveBottom],
#             WXK_LEFT  : [self.moveLeft,     self.shiftLeft],
#             WXK_RIGHT : [self.moveRight,    self.shiftRight]}
#         # check key case
#         if key in case.keys():
#             M = event.GetModifiers()
#             # check modifiers are none other than...
#             if M & (MOD_CONTROL+MOD_SHIFT) == M:
#                 C = 1 if M & MOD_CONTROL else 0 # CONTTROL BIT
#                 S = 1 if M & MOD_SHIFT   else 0 # SHIFT BIT
#                 if case[key][C]():
#                     if S: self.setBlockEnd()   # extend block
#                     else: self.setBlockBegin() # release block

#         # RETURN/ENTER:
#         if event.GetModifiers() == MOD_NONE:
#             if key in [WXK_RETURN, WXK_NUMPAD_ENTER]:
#                 if self.blockSelected():
#                     self.deleteBlock()
#                 self.splitLine()
#                 self.setBlockBegin()

#         # DELETE/BACKSPACE:
#         case = {
#             WXK_BACK   : self.deleteBack,
#             WXK_DELETE : self.deleteAhead}
#         if event.GetModifiers() == MOD_NONE:
#             if key in case.keys():
#                 if self.blockSelected():
#                     self.deleteBlock()
#                     self.setBlockBegin()
#                 else: case[key]()

#         # CONTROL C/V/X/A:
#         case = {
#             'A' : self.selectAll,
#             'C' : self.copyBlock,
#             'X' : self.cutBlock,
#             'V' : self.pasteClipboard}
#         if event.GetModifiers() == MOD_CONTROL:
#             if chr(key) in case.keys():
#                 case[chr(key)]()

#         # TAB
#         if key == WXK_TAB:
#             # if self.blockSelected():
#             #     if event.GetModifiers() == MOD_NONE:
#             #         self.shiftBlockForward()
#             #     if event.GetModifiers() == MOD_SHIFT:
#             #         self.shiftBlockBackward()
#             # else:
#             if event.GetModifiers() == MOD_NONE:
#                 self.shiftTabRight()
#                 self.setBlockBegin()
#             # if event.GetModifiers() == MOD_SHIFT:
#             #     self.shiftTabLeft()
#             #     self.setBlockBegin()

#         # add one level undo/redo
#         # add save, close, open

#         # done
#         event.Skip()
#         return

#     def _OnChar(self, event):
#         # get unicode value
#         key = event.GetUnicodeKey()
#         # check charset
#         if chr(key) in self.charSet:
#             if self.blockSelected():
#                 self.deleteBlock()
#             self.insertChar(key)
#             self.setBlockBegin()
#         # done
#         self.refreshBuffer()
#         self.Panel.Refresh()
#         return

#     def Start(self):
        
#         self.createBrushes()
#         self.createPens()
#         self.createFonts()
#         self.createCharSet()
#         self.createCharBitmaps()
#         self.createBufferBitmap(85, 40)
#         self.setFramePosition()

#         self.clipboard = []
#         self.scroll = 0, 0
#         self.cursor = 0, 0
#         self.blockBegin = 0, 0
#         self.blockEnd   = 0, 0
#         self.chrBuf = ['']
        
#         self.refreshBuffer()
#         self.Panel.Refresh()
        
#         self.Bind(EVT_CHAR, self._OnChar)
        
#         return

# App().MainLoop()


