from imports import *
from collections import namedtuple

X_IN_BOX = '\u2327'
NULL = '\u2205'
Flag = namedtuple('Flag', ['isUncertain', 'isEstimate'])

class TranscriptionLayout(QVBoxLayout):

    defaultFont = QFont('Arial', 12)
    fontMetric = QFontMetricsF(defaultFont)

    def __init__(self, hand=None):
        QVBoxLayout.__init__(self)

        self.hand = hand
        self.fields = list()
        self.slots = list()
        self.violations = list()

        self.lineLayout = QHBoxLayout()
        self.addLayout(self.lineLayout)

        self.generateSlots()
        self.generateViolationLabels()
        self.generateFields()

        self.flagList = [False for n in range(34)]
        self.connectSlotSignals()

    def updateFlags(self, flags):
        for flag, slot in zip(flags[1:], self.slots[1:]):
            slot.updateFlags(flag)

    def generateFields(self):
        #FIELD 1 (Forearm)
        self.field1 = TranscriptionField(number=1)
        self.field1.addSlot(self.slot1)
        self.field1.addViolationLabel(self.violation1)
        #self.lineLayout.addLayout(self.field1)
        self.fields.append(self.field1)

        #FIELD 2 (Thumb)
        self.field2 = TranscriptionField(number=2)
        for j in range(2,6):
            slot = getattr(self, 'slot{}'.format(j))
            self.field2.addSlot(slot)
            self.slots.append(slot)
            violation = getattr(self, 'violation{}'.format(j))
            self.field2.addViolationLabel(violation)
        self.lineLayout.addLayout(self.field2)
        self.fields.append(self.field2)

        #FIELD 3 (Thumb/Finger contact)
        self.field3 = TranscriptionField(number=3)
        for j in range(6,16):
            slot = getattr(self, 'slot{}'.format(j))
            self.field3.addSlot(slot)
            self.slots.append(slot)
            violation = getattr(self, 'violation{}'.format(j))
            self.field3.addViolationLabel(violation)
        self.lineLayout.addLayout(self.field3)
        self.fields.append(self.field3)

        #FIELD 4 (Index)
        self.field4 = TranscriptionField(number=4)
        for j in range(16,20):
            slot = getattr(self, 'slot{}'.format(j))
            self.field4.addSlot(slot)
            self.slots.append(slot)
            violation = getattr(self, 'violation{}'.format(j))
            self.field4.addViolationLabel(violation)
        self.lineLayout.addLayout(self.field4)
        self.fields.append(self.field4)

        #FIELD 5 (Middle)
        self.field5 = TranscriptionField(number=5)
        for j in range(20,25):
            slot = getattr(self, 'slot{}'.format(j))
            self.field5.addSlot(slot)
            self.slots.append(slot)
            violation = getattr(self, 'violation{}'.format(j))
            self.field5.addViolationLabel(violation)
        self.lineLayout.addLayout(self.field5)
        self.fields.append(self.field5)

        #FIELD 6 (Ring)
        self.field6 = TranscriptionField(number=6)
        for j in range(25,30):
            slot = getattr(self, 'slot{}'.format(j))
            self.field6.addSlot(slot)
            self.slots.append(slot)
            violation = getattr(self, 'violation{}'.format(j))
            self.field6.addViolationLabel(violation)
        self.lineLayout.addLayout(self.field6)
        self.fields.append(self.field6)

        #FIELD 7 (Pinky)
        self.field7 = TranscriptionField(number=7)
        for j in range(30,35):
            slot = getattr(self, 'slot{}'.format(j))
            self.field7.addSlot(slot)
            self.slots.append(slot)
            violation = getattr(self, 'violation{}'.format(j))
            self.field7.addViolationLabel(violation)
        self.lineLayout.addLayout(self.field7)
        self.fields.append(self.field7)

    def connectSlotSignals(self):
        for slot in self.slots[1:]:
            slot.slotFlagged.connect(self.updateFlagList)

    def updateFlagList(self, slotNum, isFlagged):
        self.flagList[slotNum] = isFlagged

    def fillPredeterminedSlots(self):
        self.slot8.setText(NULL)
        self.slot9.setText('/')
        self.slot16.setText('1')
        self.slot21.setText('2')
        self.slot26.setText('3')
        self.slot31.setText('4')

    def generateSlots(self):
        #FIELD 1 (Forearm)
        self.slot1 = TranscriptionCheckBox(1)
        self.slots.append(self.slot1)

        #FIELD 2 (Thumb)
        self.slot2 = TranscriptionSlot(2, 2, '[LUO\\?]', list('LUO?'))
        self.slot3 = TranscriptionSlot(3, 2, '[{<=x\\?]', list('{<=x?'))
        self.slot4 = TranscriptionSlot(4, 2, '[EFHi\\?]', list('HEiF?'))
        self.slot5 = TranscriptionSlot(5, 2, '[EFHi\\?]', list('HEiF?'))

        #FIELD 3 (Thumb/Finger Contact)
        self.slot6 = TranscriptionSlot(6, 3, '[-tfbru\\?]', list('-tfbru?'))
        self.slot7 = TranscriptionSlot(7, 3, '[-dtpM\\?]', list('-dtpM?'))
        self.slot8 = TranscriptionSlot(8, 3, NULL, [NULL])
        self.slot9 = TranscriptionSlot(9, 3, '/', ['/'])
        self.slot10 = TranscriptionSlot(10, 3, '[-tfbru\\?]', list('-tfbru?'))
        self.slot11 = TranscriptionSlot(11, 3, '[-dmpM\\?]', list('-dmpM?'))
        self.slot12 = TranscriptionSlot(12, 3, '[-1\s]', ['-','1'])
        self.slot13 = TranscriptionSlot(13, 3, '[-2\s]', ['-','2'])
        self.slot14 = TranscriptionSlot(14, 3, '[-3\s]', ['-','3'])
        self.slot15 = TranscriptionSlot(15, 3, '[-4\s]', ['-','4'])

        #FIELD 4 (Index)
        self.slot16 = TranscriptionSlot(16, 4, '1', ['1'])
        self.slot17 = TranscriptionSlot(17, 4, '[EFHi\\?]', list('HEiF?'))
        self.slot18 = TranscriptionSlot(18, 4, '[EFHi\\?]', list('HEiF?'))
        self.slot19 = TranscriptionSlot(19, 4, '[EFHi\\?]', list('HEiF?'))

        #FIELD 5 (Middle)
        self.slot20 = TranscriptionSlot(20, 5, '[{<=\u2327x(?=-+$)\\?]', ['{','<','=','x','x+','x-','\u2327', '?'])
        self.slot21 = TranscriptionSlot(21, 5, '2', ['2'])
        self.slot22 = TranscriptionSlot(22, 5, '[EFHi\\?]', list('HEiF?'))
        self.slot23 = TranscriptionSlot(23, 5, '[EFHi\\?]', list('HEiF?'))
        self.slot24 = TranscriptionSlot(24, 5, '[EFHi\\?]', list('HEiF?'))

        #FIELD 6 (Ring)
        self.slot25 = TranscriptionSlot(25, 6, '[{<=\u2327x(?=-+$)\\?]', ['{','<','=','x','x+','x-','\u2327', '?'])
        self.slot26 = TranscriptionSlot(26, 6, '3', ['3'])
        self.slot27 = TranscriptionSlot(27, 6, '[EFHi\\?]', list('HEiF?'))
        self.slot28 = TranscriptionSlot(28, 6, '[EFHi\\?]', list('HEiF?'))
        self.slot29 = TranscriptionSlot(29, 6, '[EFHi\\?]', list('HEiF?'))

        #FIELD 7 (Middle)
        self.slot30 = TranscriptionSlot(30, 7, '[{<=\u2327x(?=-+$)\\?]', ['{','<','=','x','x+','x-','\u2327', '?'])
        self.slot31 = TranscriptionSlot(31, 7, '4', ['4'])
        self.slot32 = TranscriptionSlot(32, 7, '[EFHi]', list('HEiF?'))
        self.slot33 = TranscriptionSlot(33, 7, '[EFHi]', list('HEiF?'))
        self.slot34 = TranscriptionSlot(34, 7, '[EFHi]', list('HEiF?'))

    def isEmpty(self):
        if self.slot1.isChecked():
            return False
        for slot in self.slots[1:]:
            if slot.num in [8,9,16,21,26,31]:
                continue
            if slot.text():
                return False
        return True

    def isFilled(self):
        return not self.isEmpty()

    def generateViolationLabels(self):
        for j in range(1,35):
            setattr(self, 'violation{}'.format(j), QLabel('   '))
            widget = getattr(self, 'violation{}'.format(j))
            self.violations.append(widget)

    def clearViolationLabels(self):
        for v in self.violations:
            v.setText('')
            v.setToolTip('')

    def clearTranscriptionSlots(self):
        self.slot1.setChecked(False)
        for s in self.slots[1:]:
            s.setText('')

    def values(self):
        data = ['V' if self.slot1.isChecked() else '']
        data.extend([slot.text() if slot.text() else '' for slot in self.slots[1:]])
        return data

    def slotValues(self):
        return self.slots

    def flags(self):
        flags = [Flag(slot.isUncertain, slot.isEstimate) for slot in self.slots]
        return flags

    def blenderCode(self):
        transcription = '[{}]1[{}]2[{}]3[{}]4[{}]5[{}]6[{}]7'.format('V' if self.slot1.isChecked() else '_',
                                                                     ''.join([self[n].getText() for n in range(1,5)]),
                                                                     ''.join([self[n].getText() for n in range(5,15)]),
                                                                     ''.join([self[n].getText() for n in range(15,19)]),
                                                                     ''.join([self[n].getText() for n in range(19,24)]),
                                                                     ''.join([self[n].getText() for n in range(24,29)]),
                                                                     ''.join([self[n].getText() for n in range(29,34)]))
        return transcription

    def updateFromCopy(self, other):
        self.clearTranscriptionSlots()
        if other.slot1.isChecked():
            self.slot1.setChecked(True)
        for slot in other.slots[1:]:
            text = slot.getText(empty_text='')
            getattr(self, 'slot{}'.format(slot.num)).setText(text)

    def __str__(self):
        return ','.join(self.values())

    def str_with_underscores(self):
        return ''.join([v if v else '_' for v in self.values()])

    def __getitem__(self, num):
        return self.slots[num]

class TranscriptionCompleter(QCompleter):

    def __init__(self, options, lineEditWidget):
        super().__init__(options, lineEditWidget)
        #self.setCaseSensitivity(Qt.CaseSensitive)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.UnfilteredPopupCompletion)

class TranscriptionSlot(QLineEdit):

    slotSelectionChanged = Signal(int)
    slotFlagged = Signal(int, bool)

    def __init__(self, num, field, regex, completer_options):
        super().__init__()
        self.num = num
        self.field = field
        self.styleSheetString = ("QLineEdit{{background: {}; border: {};}} "
                                "QLineEdit:hover{{background {};border: {}; }}")
        self.defaultBackground = 'white'
        self.defaultBorder = '1px solid grey'
        self.flaggedBackground = 'pink'
        self.flaggedBorder = '2px dashed black'
        self.background = self.defaultBackground
        self.border = self.defaultBorder
        self.regex = regex
        self.isUncertain = False
        self.isEstimate = False
        qregexp = QRegExp(regex)
        qregexp.setCaseSensitivity(Qt.CaseInsensitive)
        self.setValidator(QRegExpValidator(qregexp))
        if self.num in [20,25,30]:
            self.setMaxLength(2)
            #these slots are the only ones that can contain digraphs, namely 'x+' and 'x-'
        else:
            self.setMaxLength(1)

        self.setFixedWidth(30)
        self.setFocusPolicy(Qt.TabFocus)
        completer = TranscriptionCompleter(completer_options, self)
        completer.setMaxVisibleItems(8)
        self.setCompleter(completer)
        self.completer().activated.connect(self.completerActivated)
        style = self.styleSheetString.format(self.background, self.border, self.background, self.border)
        self.setStyleSheet(style)

        if self.num == 8:
            self.setText(NULL)
            self.setEnabled(False)
            self.setToolTip('Slot 8. Represents the thumb. Always marked as {}.'.format(NULL))
        elif self.num == 9:
            self.setText('/')
            self.setEnabled(False)
            self.setToolTip('Slot 9. Represents contact. Always marked as /.')
        elif self.num == 16:
            self.setText('1')
            self.setEnabled(False)
            self.setToolTip('Slot 16. Represents index finger. Always marked as 1.')
        elif self.num == 21:
            self.setText('2')
            self.setEnabled(False)
            self.setToolTip('Slot 21. Represents middle finger. Always marked as 2.')
        elif self.num == 26:
            self.setText('3')
            self.setEnabled(False)
            self.setToolTip('Slot 26. Represents ring finger. Always marked as 3.')
        elif self.num == 31:
            self.setText('4')
            self.setEnabled(False)
            self.setToolTip('Slot 31. Represents pinky finger. Always marked as 4.')

        # set button context menu policy
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # create context menu
        self.makeMenu()

    def updateFlags(self, flag):
        if flag.isUncertain:
            self.isUncertain = True
            self.background = self.flaggedBackground
            self.changeUncertaintyAct.setChecked(True)
        else:
            self.isUncertain = False
            self.background = self.defaultBackground
            self.changeUncertaintyAct.setChecked(False)

        if flag.isEstimate:
            self.isEstimate = True
            self.border = self.flaggedBorder
            self.changeEstimateAct.setChecked(True)
        else:
            self.isEstimate = False
            self.border = self.defaultBorder
            self.changeEstimateAct.setChecked(False)

        style = self.styleSheetString.format(self.background, self.border, self.background, self.border)
        self.setStyleSheet(style)

    def removeFlags(self):
        self.isEstimate = False
        self.isUncertain = False
        self.border = self.defaultBorder
        self.background = self.defaultBackground
        self.changeEstimateAct.setChecked(False)
        self.changeUncertaintyAct.setChecked(False)
        style = self.styleSheetString.format(self.background, self.border, self.background, self.border)
        self.setStyleSheet(style)

    def makeMenu(self):
        self.popMenu = QMenu(self)
        self.changeEstimateAct = QAction('Flag as estimate', self, triggered=self.changeEstimate, checkable=True)
        self.changeUncertaintyAct = QAction('Flag as uncertain', self, triggered=self.changeUncertainty, checkable=True)
        self.popMenu.addAction(self.changeUncertaintyAct)
        self.popMenu.addAction(self.changeEstimateAct)

    def showContextMenu(self, point):
        self.popMenu.exec_(self.mapToGlobal(point))

    def changeEstimate(self, e=None):
        if self.changeEstimateAct.isChecked():
            self.border = self.flaggedBorder
            self.isEstimate = True
        else:
            self.border = self.defaultBorder
            self.isEstimate = False
        style = self.styleSheetString.format(self.background, self.border, self.background, self.border)
        self.setStyleSheet(style)

    def changeUncertainty(self, e=None):
        if self.changeUncertaintyAct.isChecked():
            self.background = self.flaggedBackground
            self.isUncertain = True
        else:
            self.background = self.defaultBackground
            self.isUncertain = False
        style = self.styleSheetString.format(self.background, self.border, self.background, self.border)
        self.setStyleSheet(style)
        self.slotFlagged.emit(self.num-1, True)

    def __eq__(self, other):
        return self.text() == other.text()

    def __ne__(self, other):
        return not self.__eq__(other)

    def getText(self, empty_text = '_'):
        return self.text() if self.text() else empty_text

    @Slot(bool)
    def changeValidatorState(self, unrestricted):
        if unrestricted:
            self.setValidator(QRegExpValidator(QRegExp('.*')))
        else:
            self.setValidator(QRegExpValidator(QRegExp(self.regex)))

    def completerActivated(self, e):
        self.setText(e)
        #add automatic tab to next widget

    def focusInEvent(self, e):
        self.completer().complete()
        self.slotSelectionChanged.emit(self.num)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setFocus(Qt.TabFocusReason)
        #ignore right clicks, the context menu should appear instead of triggering the completer

    def keyPressEvent(self, e):
        key = e.key()

        #capitalize L, U, O in slot 2
        if self.num == 2:
            if key in [76, 85, 79]: #Qt.Key_L, Qt.Key_U, Qt.Key_O
                self.setText(e.text().upper())

        #capitalize M in slot 7 (only)
        elif self.num == 7:
            if key == 77: #Qt.Key_M
                self.setText(e.text().upper())

        #capitalize E, F, H in numerous slots
        elif self.num in [4,5,17,18,19,22,23,24,27,28,29,32,33,34]:
            if key in [69, 70, 72]: #Qt.Key_E, Qt.Key_F, Qt.Key_H
                self.setText(e.text().upper())

        #allow Z, C, and S to stand in for various 'x' values that can't be typed
        elif self.num in [20, 25, 30]:
            if key == 90:# == Qt.Key_Z:
                self.completer().setCurrentRow(5)
                self.setText('x-')
            elif key == 67:# == Qt.Key_C
                self.completer().setCurrentRow(4)
                self.setText('x+')
            elif key == 83:# == Qt.Key_S
                self.completer().setCurrentRow(6)
                self.setText(X_IN_BOX)

        self.completer().complete()
        super().keyPressEvent(e)


class TranscriptionCheckBox(QCheckBox):

    slotSelectionChanged = Signal(int)

    def __init__(self, num, parent=None):
        super().__init__()
        self.num = num
        self.stateChanged.connect(lambda x: self.slotSelectionChanged.emit(0))
        self.isEstimate = False
        self.isUncertain = False

    def text(self):
        return 'V' if self.isChecked() else ''


class TranscriptionField(QGridLayout):

    slotSelectionChanged = Signal(int)

    def __init__(self, number):
        super().__init__()
        self.number = number
        self.name = 'field{}'.format(self.number)
        self.left_bracket = QLabel('[')
        self.right_bracket = QLabel(']<font size="5"><b><sub>{}</sub></b></font>'.format(self.number))
        self.transcription = QHBoxLayout()
        self.violations = QHBoxLayout()

        self.addWidget(self.left_bracket, 0, 0)
        self.addLayout(self.transcription, 0, 1)
        self.addWidget(self.right_bracket, 0, 10)
        self.addLayout(self.violations, 1, 1)

    def addSlot(self, slot):
        self.transcription.addWidget(slot)

    def addViolationLabel(self, label):
        self.violations.addWidget(label)

class TranscriptionInfo(QGridLayout):

    def __init__(self):
        super().__init__()

        titleFont = QFont('Arial', 15)
        infoFont = QFont('Arial', 12)

        self.fieldTypeTitle = QLabel('Field type')
        self.fieldTypeTitle.setFont(titleFont)
        self.fieldTypeInfo = QLabel('None selected')
        self.fieldTypeInfo.setFont(infoFont)

        self.fieldNumberTitle = QLabel('Field number')
        self.fieldNumberTitle.setFont(titleFont)
        self.fieldNumberInfo = QLabel('None selected')
        self.fieldNumberInfo.setFont(infoFont)

        self.slotNumberTitle = QLabel('Slot number')
        self.slotNumberTitle.setFont(titleFont)
        self.slotNumberInfo = QLabel('None selected')
        self.slotNumberInfo.setFont(infoFont)

        self.slotTypeTitle = QLabel('Slot type')
        self.slotTypeInfo = QLabel('None selected')
        self.slotTypeTitle.setFont(titleFont)
        self.slotTypeInfo.setFont(infoFont)
        self.slotTypeInfo.setWordWrap(True)

        self.slotOptionsTitle = QLabel('Permitted characters')
        self.slotOptionsInfo = QLabel('None selected')
        self.slotOptionsTitle.setFont(titleFont)
        self.slotOptionsInfo.setFont(infoFont)
        self.slotOptionsInfo.setWordWrap(True)

        tuples = [(self.fieldNumberTitle, self.fieldNumberInfo), (self.fieldTypeTitle, self.fieldTypeInfo),
                  (self.slotNumberTitle, self.slotNumberInfo), (self.slotTypeTitle, self.slotTypeInfo),
                  (self.slotOptionsTitle, self.slotOptionsInfo)]
        for row in range(5):
            title,info = tuples.pop(0)
            self.addWidget(title, row, 0)
            self.addWidget(info, row, 1)

        self.purposeDict = {1: 'Shows if forearm is involved',
                            2: 'Thumb oppositional positions (CM rotation)',
                            3: 'Thumb abduction/adduction(CM adduction)',
                            4: 'Thumb MCP flexion',
                            5: 'Thumb DIP flexion',
                            6: 'Thumb surface options',
                            7: 'Thumb bone options',
                            #8 always null
                            #9 always forward slash
                            10: 'Finger surface options',
                            11: 'Finger bone options',
                            12: 'Index/thumb contact',
                            13: 'Middle/thumb contact',
                            14: 'Ring/thumb contact',
                            15: 'Pinky/thumb contact',
                            #16 always 1,
                            17: 'Index MCP flexion',
                            18: 'Index PIP flexion',
                            19: 'Index DIP flexion',
                            20: 'Index/middle contact',
                            #21 always 2,
                            22: 'Middle MCP flexion',
                            23: 'Middle PIP flexion',
                            24: 'Middle DIP flexion',
                            25: 'Middle/ring contact',
                            #26 always 3
                            27: 'Ring MCP flexion',
                            28: 'Ring PIP flexion',
                            29: 'Ring DIP flexion',
                            30: 'Ring/pinky contact',
                            #31 always 4
                            32: 'Pinky MCP flexion',
                            33: 'Pinky PIP flexion',
                            34: 'Pinky DIP flexion'}
        self.optionsDict = {1: 'Either on or off (checkbox)',
                              2: 'L (lateral)\nU (unopposed)\nO (opposed)',
                              3: '{ (full abduction)\n< (neutral)\n= (adducted)',
                              4: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              5: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              6: 't (tip)\nf (friction surface)\nb (back surface)\nr (radial surface)\nu (ulnar surface)',
                              7: 'd (distal)\np (proximal)\nM (meta-carpal)',
                              #8 always null,
                              #9 always forward slash,
                              10: 't (tip)\nf (friction surface)\nb (back surface)\nr (radial surface)\nu (ulnar surface)',
                              11: 'd (distal)\nm (medial)\np (proximal)\nM (meta-carpal)',
                              12: '1 (if contact with index)\n- (if no contact)',
                              13: '2 (if contact with middle)\n- (if no contact)',
                              14: '3 (if contact with ring)\n- (if no contact)',
                              15: '4 (if contact with pinky)\n- (if no contact)',
                              #16 always 1,
                              17: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              18: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              19: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              20: ('{ (full abduction)\n< (neutral)\n= (adducted)\nx- (slightly crossed with contact)\n'
                                    'x (crossed with contact)\nx+ (ultracrossed)\n\u2327 (crossed without contact)'),
                              #21 always 2,
                              22: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              23: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              24: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              25: ('{ (full abduction)\n< (neutral)\n= (adducted)\nx- (slightly crossed with contact)\n'
                                    'x (crossed with contact)\nx+ (ultracrossed)\n\u2327 (crossed without contact)'),
                              #26 always 3,
                              27: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              28: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              29: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              30: ('{ (full abduction)\n< (neutral)\n= (adducted)\nx- (slightly crossed with contact)\n'
                                    'x (crossed with contact)\nx+ (ultracrossed)\n\u2327 (crossed without contact)'),
                              #31 always 4,
                              32: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              33: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)',
                              34: 'H (hyperextended)\nE (extended)\ni (intermediate)\nF (flexed)'
                              }

    @Slot(int)
    def transcriptionSlotChanged(self, e):
        if e == 1:
            self.fieldTypeInfo.setText('Forearm')
            self.fieldNumberInfo.setText('1')
        elif e < 6:
            self.fieldTypeInfo.setText('Thumb')
            self.fieldNumberInfo.setText('2')
        elif e < 16:
            self.fieldTypeInfo.setText('Thumb/finger contact')
            self.fieldNumberInfo.setText('3')
        elif e < 20:
            self.fieldTypeInfo.setText('Index finger')
            self.fieldNumberInfo.setText('4')
        elif e < 25:
            self.fieldTypeInfo.setText('Middle finger')
            self.fieldNumberInfo.setText('5')
        elif e < 30:
            self.fieldTypeInfo.setText('Ring finger')
            self.fieldNumberInfo.setText('6')
        else:
            self.fieldTypeInfo.setText('Pinky finger')
            self.fieldNumberInfo.setText('7')
        self.slotNumberInfo.setText(str(e))
        self.slotTypeInfo.setText(self.purposeDict[e])
        self.slotOptionsInfo.setText(self.optionsDict[e])


class TranscriptionPasteDialog(QDialog):

    def __init__(self, copiedTranscription, otherTranscriptions):
        super().__init__()
        self.setWindowTitle('Paste transcription')
        layout = QVBoxLayout()
        copyLayout = QHBoxLayout()
        layout.addLayout(copyLayout)
        copyLayout.addWidget(QLabel('The currently copied transcription is '))
        copyLayout.addWidget(QLabel(copiedTranscription.str_with_underscores()))

        layout.addWidget(QLabel('Where would you like to paste this transcription?'))

        self.transcriptions = otherTranscriptions
        radioLayout = QGridLayout()
        layout.addLayout(radioLayout)
        hand1config1 = QRadioButton(otherTranscriptions[0].str_with_underscores())
        hand1config1.setChecked(True)
        hand1config2 = QRadioButton(otherTranscriptions[1].str_with_underscores())
        hand2config1 = QRadioButton(otherTranscriptions[2].str_with_underscores())
        hand2config2 = QRadioButton(otherTranscriptions[3].str_with_underscores())

        self.transcriptionRadioButtons = QButtonGroup()
        self.transcriptionRadioButtons.addButton(hand1config1)
        self.transcriptionRadioButtons.setId(hand1config1, 0)
        self.transcriptionRadioButtons.addButton(hand1config2)
        self.transcriptionRadioButtons.setId(hand1config2, 1)
        self.transcriptionRadioButtons.addButton(hand2config1)
        self.transcriptionRadioButtons.setId(hand2config1, 2)
        self.transcriptionRadioButtons.addButton(hand2config2)
        self.transcriptionRadioButtons.setId(hand2config2, 3)

        radioLayout.addWidget(QLabel('Config 1, Hand 1'), 0, 0)
        radioLayout.addWidget(hand1config1, 0, 1)
        radioLayout.addWidget(QLabel('Config 1, Hand 2'), 1, 0)
        radioLayout.addWidget(hand1config2, 1, 1)
        radioLayout.addWidget(QLabel('Config 2, Hand 1'), 2, 0)
        radioLayout.addWidget(hand2config1, 2, 1)
        radioLayout.addWidget(QLabel('Config 2, Hand 2'), 3, 0)
        radioLayout.addWidget(hand2config2, 3, 1)

        buttonLayout = QHBoxLayout()
        layout.addLayout(buttonLayout)
        ok = QPushButton('OK')
        ok.clicked.connect(self.accept)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.reject)
        buttonLayout.addWidget(ok)
        buttonLayout.addWidget(cancel)

        self.setLayout(layout)

    def accept(self):
        selectedButton = self.transcriptionRadioButtons.checkedButton()
        id = self.transcriptionRadioButtons.id(selectedButton)
        self.transcriptionID = id
        self.selectedTranscription = self.transcriptions[id]
        super().accept()

    def reject(self):
        self.selectedTranscription = None
        super().reject()

class TranscriptionConfigTab(QWidget):

    def __init__(self, hand_number):
        QWidget.__init__(self)

        self.configLayout = QGridLayout()

        self.hand1Transcription = TranscriptionLayout(hand=1)
        self.configLayout.addLayout(self.hand1Transcription, 0, 0)
        self.hand2Transcription = TranscriptionLayout(hand=2)
        self.configLayout.addLayout(self.hand2Transcription, 1, 0)
        self.setLayout(self.configLayout)

    def clearAll(self, clearFlags=False):
        self.hand1Transcription.clearTranscriptionSlots()
        self.hand1Transcription.clearViolationLabels()
        self.hand1Transcription.fillPredeterminedSlots()

        self.hand2Transcription.clearTranscriptionSlots()
        self.hand2Transcription.clearViolationLabels()
        self.hand2Transcription.fillPredeterminedSlots()

        if clearFlags:
            for n in range(2,35):
                slot = 'slot{}'.format(n)
                getattr(self.hand1Transcription, slot).removeFlags()
                getattr(self.hand2Transcription, slot).removeFlags()

    def hand1(self):
        return self.hand1Transcription.values()

    def hand2(self):
        return self.hand2Transcription.values()

    def hands(self):
        return [self.hand1(), self.hand2()]

class TranscriptionSearchDialog(QDialog):

    def __init__(self, corpus):
        super().__init__()

        self.corpus = corpus
        self.transcriptions = None
        self.setWindowTitle('Search')


        layout = QVBoxLayout()

        self.topLayout = QHBoxLayout()
        explanation = QLabel()
        text = ('Enter the transcription you want to match in your corpus.')
        explanation.setText(text)
        explanation.setFont(QFont('Arial', 16))
        self.topLayout.addWidget(explanation)
        layout.addLayout(self.topLayout)

        self.configTabs = QTabWidget()
        self.configTabs.addTab(TranscriptionConfigTab(1), 'Config 1')
        self.configTabs.addTab(TranscriptionConfigTab(2), 'Config 2')
        layout.addWidget(self.configTabs)

        buttonLayout = QVBoxLayout()
        ok = QPushButton('Search')
        ok.clicked.connect(self.search)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.reject)
        buttonLayout.addWidget(ok)
        buttonLayout.addWidget(cancel)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def search(self):
        self.transcriptions = self.getTranscriptions()
        super().accept()

    def getTranscriptions(self):
        transcriptions = list()
        transcriptions.append(self.configTabs.widget(0).hand1Transcription)
        transcriptions.append(self.configTabs.widget(0).hand2Transcription)
        transcriptions.append(self.configTabs.widget(1).hand1Transcription)
        transcriptions.append(self.configTabs.widget(1).hand2Transcription)
        return transcriptions

class TranscriptionSearchResultDialog(QDialog):

    def __init__(self, results):
        super().__init__()
        self.setWindowTitle('Search Results')
        layout = QVBoxLayout()
        self.result = None

        resultsLayout = QHBoxLayout()

        self.resultsList = QListWidget()
        for r in results:
            self.resultsList.addItem(r.gloss)

        resultsLayout.addWidget(self.resultsList)
        layout.addLayout(resultsLayout)

        buttonLayout = QHBoxLayout()
        okButton = QPushButton('Go to this entry')
        cancelButton = QPushButton('Cancel')
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def accept(self):
        item = self.resultsList.currentItem()
        self.result = item
        super().accept()

    def reject(self):
        self.result = None
        super().reject()

class TranscriptionSelectDialog(QDialog):

    def __init__(self, transcriptions, mode='copy'):
        super().__init__()

        if mode == 'copy':
            self.setWindowTitle('Copy transcription')
        elif mode == 'blender':
            self.setWindowTitle('Handshape visualization')
        layout = QVBoxLayout()

        if mode == 'copy':
            layout.addWidget(QLabel('Which transcription do you want to copy?'))
        elif mode == 'blender':
            layout.addWidget(QLabel('Which transcription do you want to visualize?'))

        self.transcriptions = transcriptions
        radioLayout = QGridLayout()
        layout.addLayout(radioLayout)
        hand1config1 = QRadioButton(transcriptions[0].str_with_underscores())
        hand1config1.setChecked(True)
        hand1config2 = QRadioButton(transcriptions[1].str_with_underscores())
        hand2config1 = QRadioButton(transcriptions[2].str_with_underscores())
        hand2config2 = QRadioButton(transcriptions[3].str_with_underscores())
        self.transcriptionRadioButtons = QButtonGroup()
        self.transcriptionRadioButtons.addButton(hand1config1)
        self.transcriptionRadioButtons.setId(hand1config1, 0)
        self.transcriptionRadioButtons.addButton(hand1config2)
        self.transcriptionRadioButtons.setId(hand1config2, 1)
        self.transcriptionRadioButtons.addButton(hand2config1)
        self.transcriptionRadioButtons.setId(hand2config1, 2)
        self.transcriptionRadioButtons.addButton(hand2config2)
        self.transcriptionRadioButtons.setId(hand2config2, 3)

        radioLayout.addWidget(QLabel('Hand 1, Config 1'), 0, 0)
        radioLayout.addWidget(hand1config1, 0, 1)
        radioLayout.addWidget(QLabel('Hand 1, Config 2'), 1, 0)
        radioLayout.addWidget(hand1config2, 1, 1)
        radioLayout.addWidget(QLabel('Hand 2, Config 1'), 2, 0)
        radioLayout.addWidget(hand2config1, 2, 1)
        radioLayout.addWidget(QLabel('Hand 2, Config 2'), 3, 0)
        radioLayout.addWidget(hand2config2, 3, 1)

        buttonLayout = QHBoxLayout()
        layout.addLayout(buttonLayout)
        ok = QPushButton('OK')
        ok.clicked.connect(self.accept)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.reject)
        buttonLayout.addWidget(ok)
        buttonLayout.addWidget(cancel)

        self.setLayout(layout)

    def accept(self):
        selectedButton = self.transcriptionRadioButtons.checkedButton()
        self.id = self.transcriptionRadioButtons.id(selectedButton)
        self.selectedTranscription = self.transcriptions[self.id]
        if self.id in [0,2]:
            self.hand = 'R'
        else:
            self.hand = 'L'
        super().accept()

    def reject(self):
        self.selectedTranscription = None
        super().reject()

class TranscriptionFlagDialog(QDialog):

    def __init__(self, currentFlags):
        super().__init__()
        self.setWindowTitle('Set transcription flags')
        layout = QVBoxLayout()
        self.flagTable = QTableWidget()
        self.flagTable.setRowCount(4)
        self.flagTable.setColumnCount(34)
        self.flagTable.setHorizontalHeaderLabels(['Slot {}'.format(n) for n in range(1,35)])
        verticalLabels = ['Hand 1, Config 1', 'Hand 1, Config 2', 'Hand 2, Config 1', 'Hand 2, Config 2']
        self.flagTable.setVerticalHeaderLabels(verticalLabels)
        for row in range(self.flagTable.rowCount()):
            for col in range(self.flagTable.columnCount()):
                item = FlagCheckboxWidget(row, col, self.flagTable)
                self.flagTable.setCellWidget(row, col, item)
                cf = currentFlags[row][col]
                item.uncertainCheckbox.setChecked(cf.isUncertain)
                item.estimatedCheckbox.setChecked(cf.isEstimate)
        layout.addWidget(self.flagTable)
        buttonLayout = QHBoxLayout()
        okButton = QPushButton('OK')
        okButton.clicked.connect(self.accept)
        buttonLayout.addWidget(okButton)
        cancelButton = QPushButton('Cancel')
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def accept(self):
        self.flags = list()
        for r in range(self.flagTable.rowCount()):
            row = list()
            for c in range(self.flagTable.columnCount()):
                row.append(self.flagTable.cellWidget(r, c).value())
            self.flags.append(row)
        super().accept()

    def reject(self):
        self.flags = None
        super().reject()

class FlagCheckboxWidget(QWidget):

    def __init__(self, row, column, parentTable):
        super().__init__()
        layout = QVBoxLayout()
        self.row = row
        self.column = column
        self.parentTable = parentTable
        self.estimatedCheckbox = QCheckBox('Estimated')
        self.uncertainCheckbox = QCheckBox('Uncertain')
        layout.addWidget(self.uncertainCheckbox)
        layout.addWidget(self.estimatedCheckbox)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.makeMenu()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, point):
        self.popMenu.exec_(self.mapToGlobal(point))

    def makeMenu(self):
        self.popMenu = QMenu(self)
        self.matchRowAct = QAction('Make the whole row look like this cell', self, triggered=self.matchRow)
        self.matchColAct = QAction('Make the whole column look like this cell', self, triggered=self.matchColumn)
        self.popMenu.addAction(self.matchRowAct)
        self.popMenu.addAction(self.matchColAct)

    def matchRow(self):
        currentItem = self.parentTable.cellWidget(self.row, self.column)
        estimated = currentItem.estimatedCheckbox.isChecked()
        uncertain = currentItem.uncertainCheckbox.isChecked()
        for column in range(self.parentTable.columnCount()):
            item = self.parentTable.cellWidget(self.row, column)
            item.estimatedCheckbox.setChecked(estimated)
            item.uncertainCheckbox.setChecked(uncertain)

    def matchColumn(self):
        currentItem = self.parentTable.cellWidget(self.row, self.column)
        estimated = currentItem.estimatedCheckbox.isChecked()
        uncertain = currentItem.uncertainCheckbox.isChecked()
        for row in range(self.parentTable.rowCount()):
            item = self.parentTable.cellWidget(row, self.column)
            item.estimatedCheckbox.setChecked(estimated)
            item.uncertainCheckbox.setChecked(uncertain)

    def value(self):
        return (Flag(self.uncertainCheckbox.isChecked(), self.estimatedCheckbox.isChecked()))

