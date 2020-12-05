import base

# allow exit() through the escape key
base._ESCAPE = True

class App(base.App):


    def _OnKeyDown(self, event):

        # get special key code
        key = event.GetKeyCode()

        # check for ESCAPE key
        if key == WXK_ESCAPE:
            self._quitRequest(event)

        # CURSOR MOTION AND SELECTION
        case = {        # MOD_NONE          # MOD_CONTROL
            WXK_UP    : [self.moveUp,       self.Nop],
            WXK_DOWN  : [self.moveDown,     self.Nop],
            WXK_HOME  : [self.moveHome,     self.moveTop],
            WXK_END   : [self.moveEnd,      self.moveBottom],
            WXK_LEFT  : [self.moveLeft,     self.shiftLeft],
            WXK_RIGHT : [self.moveRight,    self.shiftRight]}
        # check key case
        if key in case.keys():
            M = event.GetModifiers()
            # check modifiers are none other than...
            if M & (MOD_CONTROL+MOD_SHIFT) == M:
                C = 1 if M & MOD_CONTROL else 0 # CONTTROL BIT
                S = 1 if M & MOD_SHIFT   else 0 # SHIFT BIT
                if case[key][C]():
                    if S: self.setBlockEnd()   # extend block
                    else: self.setBlockBegin() # release block

        # RETURN/ENTER:
        if event.GetModifiers() == MOD_NONE:
            if key in [WXK_RETURN, WXK_NUMPAD_ENTER]:
                if self.blockSelected():
                    self.deleteBlock()
                self.splitLine()
                self.setBlockBegin()

        # DELETE/BACKSPACE:
        case = {
            WXK_BACK   : self.deleteBack,
            WXK_DELETE : self.deleteAhead}
        if event.GetModifiers() == MOD_NONE:
            if key in case.keys():
                if self.blockSelected():
                    self.deleteBlock()
                    self.setBlockBegin()
                else: case[key]()

        # CONTROL C/V/X/A:
        case = {
            'A' : self.selectAll,
            'C' : self.copyBlock,
            'X' : self.cutBlock,
            'V' : self.pasteClipboard}
        if event.GetModifiers() == MOD_CONTROL:
            if chr(key) in case.keys():
                case[chr(key)]()

        # TAB
        if key == WXK_TAB:
            # if self.blockSelected():
            #     if event.GetModifiers() == MOD_NONE:
            #         self.shiftBlockForward()
            #     if event.GetModifiers() == MOD_SHIFT:
            #         self.shiftBlockBackward()
            # else:
            if event.GetModifiers() == MOD_NONE:
                self.shiftTabRight()
                self.setBlockBegin()
            # if event.GetModifiers() == MOD_SHIFT:
            #     self.shiftTabLeft()
            #     self.setBlockBegin()

        # add one level undo/redo
        # add save, close, open

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
        # done
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
