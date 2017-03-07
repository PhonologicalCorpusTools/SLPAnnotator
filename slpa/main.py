import traceback
import itertools
import os
import sys
import subprocess
from enum import Enum
from .imports import *
from .handshapes import *
from .lexicon import *
from .binary import *
from .transcriptions import *
from .constraints import *
from .settings import Settings
from slpa import __version__ as currentSLPAversion

FONT_NAME = 'Arial'
FONT_SIZE = 12

class QApplicationMessaging(QApplication):
    messageFromOtherInstance = Signal(bytes)

    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self._key = 'SLPA'
        self._timeout = 1000
        self._locked = False
        socket = QLocalSocket(self)
        socket.connectToServer(self._key, QIODevice.WriteOnly)
        if not socket.waitForConnected(self._timeout):
            self._server = QLocalServer(self)
            # noinspection PyUnresolvedReferences
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)
        else:
            self._locked = True
        socket.disconnectFromServer()

    def __del__(self):
        if not self._locked:
            self._server.close()

    def event(self, e):
        if e.type() == QEvent.FileOpen:
            self.messageFromOtherInstance.emit(bytes(e.file(), 'UTF-8'))
            return True
        else:
            return QApplication.event(self, e)

    def isRunning(self):
        return self._locked

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.messageFromOtherInstance.emit(socket.readAll().data())

    def sendMessage(self, message):
        socket = QLocalSocket(self)
        socket.connectToServer(self._key, QIODevice.WriteOnly)
        socket.waitForConnected(self._timeout)
        socket.write(bytes(message, 'UTF-8'))
        socket.waitForBytesWritten(self._timeout)
        socket.disconnectFromServer()

class FeaturesDialog(QDialog):

    def __init__(self, settings, parent=None):
        super().__init__()
        self.setWindowTitle('Define major feature values')
        self.majorLocations, self.minorLocations, movements, orientations = settings

        layout = QVBoxLayout()

        listLayout = QHBoxLayout()

        majorLocationLayout = QVBoxLayout()
        self.majorLocationList = QListWidget()
        self.majorLocationList.clicked.connect(self.changeMinorList)
        for location in self.majorLocations:
            self.majorLocationList.addItem(location)
        addMajorLocationButton = QPushButton('Add major location')
        addMajorLocationButton.clicked.connect(self.addMajorLocation)
        removeMajorLocationButton = QPushButton('Remove major location')
        removeMajorLocationButton.clicked.connect(self.removeMajorLocation)
        majorLocationLayout.addWidget(self.majorLocationList)
        majorLocationLayout.addWidget(addMajorLocationButton)
        majorLocationLayout.addWidget(removeMajorLocationButton)

        minorLocationLayout = QVBoxLayout()
        self.minorLocationList = QListWidget()
        for location in self.minorLocations[self.majorLocations[0]]:
            self.minorLocationList.addItem(location)
        addMinorLocationButton = QPushButton('Add minor location')
        addMinorLocationButton.clicked.connect(self.addMinorLocation)
        removeMinorLocationButton = QPushButton('Remove minor location')
        removeMinorLocationButton.clicked.connect(self.removeMinorLocation)
        minorLocationLayout.addWidget(self.minorLocationList)
        minorLocationLayout.addWidget(addMinorLocationButton)
        minorLocationLayout.addWidget(removeMinorLocationButton)

        movementLayout = QVBoxLayout()
        self.movementList = QListWidget()
        for movement in movements:
            self.movementList.addItem(movement)
        addMovementButton = QPushButton('Add movement')
        addMovementButton.clicked.connect(self.addMovement)
        removeMovementButton = QPushButton('Remove movement')
        removeMovementButton.clicked.connect(self.removeMovement)
        movementLayout.addWidget(self.movementList)
        movementLayout.addWidget(addMovementButton)
        movementLayout.addWidget(removeMovementButton)

        orientationLayout = QVBoxLayout()
        self.orientationList = QListWidget()
        for orientation in orientations:
            self.orientationList.addItem(orientation)
        addOrientationButton = QPushButton('Add orientation')
        addOrientationButton.clicked.connect(self.addOrientation)
        removeOrientationButton = QPushButton('Remove orientation')
        removeOrientationButton.clicked.connect(self.removeOrientation)
        orientationLayout.addWidget(self.orientationList)
        orientationLayout.addWidget(addOrientationButton)
        orientationLayout.addWidget(removeOrientationButton)

        listLayout.addLayout(majorLocationLayout)
        listLayout.addLayout(minorLocationLayout)
        listLayout.addLayout(movementLayout)
        listLayout.addLayout(orientationLayout)

        layout.addLayout(listLayout)

        buttonLayout = QHBoxLayout()
        okButton = QPushButton('OK')
        cancelButton = QPushButton('Cancel')
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def changeMinorList(self):
        selectedMajorFeature = self.majorLocationList.currentItem()
        name = selectedMajorFeature.text()
        self.minorLocationList.clear()
        try:
            for location in self.minorLocations[name]:
                self.minorLocationList.addItem(location)
        except KeyError:
            pass

    def addMajorLocation(self):
        dialog = FeatureEntryDialog()
        result = dialog.exec_()
        if result:
            name = dialog.featureNameEdit.text()
            if name:
                self.majorLocationList.addItem(name)

    def removeMajorLocation(self):
        listItems = self.majorLocationList.selectedItems()
        for item in listItems:
            self.majorLocationList.takeItem(self.majorLocationList.row(item))

    def addMinorLocation(self):
        dialog = FeatureEntryDialog()
        result = dialog.exec_()
        if result:
            name = dialog.featureNameEdit.text()
            if name:
                self.minorLocationList.addItem(name)

    def removeMinorLocation(self):
        listItems = self.minorLocationList.selectedItems()
        for item in listItems:
            self.minorLocationList.takeItem(self.minorLocationList.row(item))

    def addMovement(self):
        dialog = FeatureEntryDialog()
        result = dialog.exec_()
        if result:
            name = dialog.featureNameEdit.text()
            if name:
                self.movementList.addItem(name)

    def removeMovement(self):
        pass


    def addOrientation(self):
        dialog = FeatureEntryDialog()
        result = dialog.exec_()
        if result:
            name = dialog.featureNameEdit.text()
            if name:
                self.orientationList.addItem(name)

    def removeOrientation(self):
        pass


class FeatureEntryDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enter new feature name')
        layout = QHBoxLayout()
        self.featureNameEdit = QLineEdit()
        self.okButton = QPushButton('OK')
        self.cancelButton = QPushButton('Cancel')
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        layout.addWidget(self.featureNameEdit)
        layout.addWidget(self.okButton)
        layout.addWidget(self.cancelButton)
        self.setLayout(layout)


class MajorFeatureLayout(QVBoxLayout):

    def __init__(self, settings):
        QVBoxLayout.__init__(self)
        self.majorLocations, self.minorLocations, self.movements, self.orientations = settings
        self.major = QComboBox()
        self.major.addItem('Major Location')
        for location in self.majorLocations:
            self.major.addItem(location)
        self.major.currentIndexChanged.connect(self.changeMinorLocation)
        self.minor = QComboBox()
        self.minor.addItem('Minor Location')
        self.movement = QComboBox()
        self.movement.addItem('Movement')
        for movement in self.movements:
            self.movement.addItem(movement)
        self.orientation = QComboBox()
        self.orientation.addItem('Orientation')
        for orientation in self.orientations:
            self.orientation.addItem(orientation)
        self.addWidget(self.major)
        self.addWidget(self.minor)
        self.addWidget(self.movement)
        self.addWidget(self.orientation)

    def changeMinorLocation(self):
        majorText = self.major.currentText()
        self.minor.clear()
        for location in self.minorLocations[majorText]:
            self.minor.addItem(location)

    def reset(self):
        self.major.setCurrentIndex(0)
        self.movement.setCurrentIndex(0)
        self.orientation.setCurrentIndex(0)

class ConfigLayout(QGridLayout):

    def __init__(self, n, handshapes, hand2):
        QGridLayout.__init__(self)
        self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)

        # self.forearmButton = QCheckBox('1. Forearm')
        # self.addWidget(self.forearmButton, 0, 1)
        self.addLayout(handshapes, 0, 2)
        self.handShapeMatch = QPushButton('Make Hand 2 = Hand 1')
        self.addWidget(self.handShapeMatch, 1, 0)
        self.hand2 = hand2
        self.handShapeMatch.clicked.connect(self.hand2.match)

class GlossLayout(QHBoxLayout):
    def __init__(self, parent = None, comboBoxes = None):
        QHBoxLayout.__init__(self)
        defaultFont = QFont(FONT_NAME, FONT_SIZE)
        self.setContentsMargins(-1,-1,-1,0)
        self.glossEdit = QLineEdit()
        self.glossEdit.setFont(defaultFont)
        self.glossEdit.setPlaceholderText('Gloss')
        self.addWidget(self.glossEdit)

class HandConfigurationNames(QVBoxLayout):
    def __init__(self):
        QVBoxLayout.__init__(self)
        self.addWidget(QLabel(''))
        self.addWidget(QLabel('1. Global'))
        self.addWidget(QLabel('2. Thumb'))
        self.addWidget(QLabel('3. Thumb/Finger'))
        self.addWidget(QLabel('4. Index'))
        self.addWidget(QLabel('5. Middle'))
        self.addWidget(QLabel('6. Ring'))
        self.addWidget(QLabel('7. Pinky'))

class HandConfigTab(QWidget):

    def __init__(self, hand_number):
        QWidget.__init__(self)

        self.configLayout = QGridLayout()

        self.hand1Transcription = TranscriptionLayout(hand=1)
        self.configLayout.addLayout(self.hand1Transcription, 0, 0)
        self.hand2Transcription = TranscriptionLayout(hand=2)
        self.configLayout.addLayout(self.hand2Transcription, 1, 0)

        self.setLayout(self.configLayout)

    def clearAll(self):
        self.hand1Transcription.slot1.setChecked(False)
        for slot in self.hand1Transcription.slots[1:]:
            slot.setText('')

        self.hand2Transcription.slot1.setChecked(False)
        for slot in self.hand2Transcription.slots[1:]:
            slot.setText('')

    def hand1(self):
        return self.hand1Transcription.values()

    def hand2(self):
        return self.hand2Transcription.values()

    def hands(self):
        return [self.hand1(), self.hand2()]


class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        #self.setMedia()
        self.looping = False
        self.videoItem = QGraphicsVideoItem()
        self.videoItem.setSize(QSizeF(640, 480))
        scene = QGraphicsScene(self)
        graphicsView = QGraphicsView(scene)
        scene.addItem(self.videoItem)
        self.layout = QVBoxLayout()
        self.layout.addWidget(graphicsView)
        self.makeButtons()
        self.setLayout(self.layout)
        self.mediaPlayer.setVideoOutput(self.videoItem)

    def makeButtons(self):
        self.buttonLayout = QHBoxLayout()

        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(self.play)
        self.buttonLayout.addWidget(self.playButton)

        self.loopButton = QPushButton('Loop media')
        self.loopButton.clicked.connect(self.loop)
        self.buttonLayout.addWidget(self.loopButton)

        self.pauseButton = QPushButton('Pause')
        self.pauseButton.clicked.connect(self.pause)
        self.buttonLayout.addWidget(self.pauseButton)

        self.stopButton = QPushButton('Stop')
        self.stopButton.clicked.connect(self.stop)
        self.buttonLayout.addWidget(self.stopButton)

        self.changeMediaButton = QPushButton('Change media file')
        self.changeMediaButton.clicked.connect(self.changeMedia)
        self.buttonLayout.addWidget(self.changeMediaButton)

        self.layout.addLayout(self.buttonLayout)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            pass
        else:
            path = getMediaFilePath('reasonable-English.mp4')
            file = QMediaContent(QUrl.fromLocalFile(QFileInfo(path).absoluteFilePath()))
            self.mediaPlayer.setMedia(file)
            self.mediaPlayer.play()

    def setMedia(self):
        path = getMediaFilePath('reasonable-English.mp4')
        file = QMediaContent(QUrl.fromLocalFile(QFileInfo(path).absoluteFilePath()))
        self.mediaPlayer.setMedia(file)

    def pause(self):

        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            pass
        elif self.mediaPlayer.state() == QMediaPlayer.PausedState:
            self.pauseButton.setText('Pause')
            self.mediaPlayer.play()
        else:
            self.mediaPlayer.pause()
            self.pauseButton.setText('Unpause')

    def stop(self):
        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            pass
        else:
            self.mediaPlayer.stop()

    def loop(self):
        if not self.looping:
            self.looping = True
            self.loopButton.setText('Stop looping')
        else:
            self.looping = False
            self.loopButton.setText('Loop media')

    def changeMedia(self):
        pass

class HandShapeImage(QLabel):

    def __init__(self, path, reversed=False, parent=None):
        super().__init__()
        self.image = QPixmap(path)
        self.isReversed = False
        self.setPixmap(self.image)
        self.mapping = {0: 'hand.png',
                        1: 'hand.png',
                        2: 'hand_thumb_selected.png',
                        3: 'hand_thumb_finger_contact.png',
                        4: 'hand_index_selected.png',
                        5: 'hand_middle_selected.png',
                        6: 'hand_ring_selected.png',
                        7: 'hand_pinky_selected.png'}
        self.reversed_mapping = {n:'reversed_'+self.mapping[n] for n in self.mapping}
        self.mappingChoice = self.mapping

    @Slot(int)
    def transcriptionSlotChanged(self, e):
        file_name = 'hand_slot{}.png'.format(e)
        self.setPixmap(QPixmap(getMediaFilePath(file_name)))

    @Slot(bool)
    def useReverseImage(self, e):
        self.mappingChoice = self.reversed_mapping

    @Slot(bool)
    def useNormalImage(self, e):
        self.mappingChoice = self.mapping


class MainWindow(QMainWindow):
    transcriptionRestrictionsChanged = Signal(bool)

    def __init__(self,app):
        app.messageFromOtherInstance.connect(self.handleMessage)
        super(MainWindow, self).__init__()
        self.setWindowTitle('SLP-Annotator')
        self.createActions()
        self.createMenus()

        self.restrictedTranscriptions = True
        self.constraints = dict()
        self.readSettings()

        self.wrapper = QWidget()#placeholder for central widget in QMainWindow
        self.corpus = None
        self.globalLayout = QHBoxLayout()

        #Make video player
        # self.videoPlayer = VideoPlayer()
        # self.globalLayout.addWidget(self.videoPlayer)

        layout = QVBoxLayout()

        # Render handshape in Blender
        self.openBlenderButton = QPushButton('Open Blender')
        self.openBlenderButton.clicked.connect(self.launchBlender)
        layout.addWidget(self.openBlenderButton)

        #Make save button
        self.saveButton = QPushButton('Add word to corpus')
        layout.addWidget(self.saveButton)

        # Make "check transcription" button
        self.checkTranscriptionButton = QPushButton('Check transcription')
        self.checkTranscriptionButton.clicked.connect(self.checkTranscription)
        layout.addWidget(self.checkTranscriptionButton)

        #Make gloss entry
        self.gloss = GlossLayout(parent=self)
        layout.addLayout(self.gloss)

        #Make tabs for each configuration
        self.configTabs = QTabWidget()
        self.configTabs.addTab(HandConfigTab(1), 'Config 1')
        self.configTabs.addTab(HandConfigTab(2), 'Config 2')
        layout.addWidget(self.configTabs)

        #Make hand image and accompanying info
        self.infoPanel = QHBoxLayout()
        self.handImage = HandShapeImage(getMediaFilePath('hand.png'))
        self.infoPanel.addWidget(self.handImage)
        self.transcriptionInfo = TranscriptionInfo()
        self.infoPanel.addLayout(self.transcriptionInfo)
        layout.addLayout(self.infoPanel)


        #Connect transcription signals to hand image and transcription info slots
        for k in [0,1]:
            for slot in self.configTabs.widget(k).hand1Transcription.slots[1:]:
                slot.slotSelectionChanged.connect(self.handImage.useNormalImage)
                slot.slotSelectionChanged.connect(self.handImage.transcriptionSlotChanged)
                slot.slotSelectionChanged.connect(self.transcriptionInfo.transcriptionSlotChanged)
                self.transcriptionRestrictionsChanged.connect(slot.changeValidatorState)
            for slot in self.configTabs.widget(k).hand2Transcription.slots[1:]:
                slot.slotSelectionChanged.connect(self.handImage.useReverseImage)
                slot.slotSelectionChanged.connect(self.handImage.transcriptionSlotChanged)
                slot.slotSelectionChanged.connect(self.transcriptionInfo.transcriptionSlotChanged)
                self.transcriptionRestrictionsChanged.connect(slot.changeValidatorState)

        #Add major features (location, movement, orientation)
        self.featuresLayout = MajorFeatureLayout([self.majorLocations, self.minorLocations, self.movements, self.orientations])
        layout.addLayout(self.featuresLayout)

        self.globalLayout.addLayout(layout)

        self.wrapper.setLayout(self.globalLayout)
        self.setCentralWidget(self.wrapper)

        self.saveButton.clicked.connect(self.saveCorpus)

        self.makeCorpusDock()

        self.showMaximized()

        self.defineTabOrder()

    def defineTabOrder(self):
        self.setTabOrder(self.saveButton, self.checkTranscriptionButton)
        self.setTabOrder(self.checkTranscriptionButton, self.gloss.glossEdit)
        self.setTabOrder(self.gloss.glossEdit, self.configTabs.widget(0))
        self.setTabOrder(self.configTabs.widget(0), self.configTabs.widget(0).hand1Transcription[0])
        for k in range(1,35):
            try:
                self.setTabOrder(self.configTabs.widget(0).hand1Transcription[k],
                                 self.configTabs.widget(0).hand1Transcription[k+1])
            except IndexError:
                pass
        self.setTabOrder(self.configTabs.widget(0).hand1Transcription[-2],
                         self.configTabs.widget(0).hand1Transcription[-1])
        self.setTabOrder(self.configTabs.widget(0).hand1Transcription[-1],
                         self.configTabs.widget(0).hand2Transcription[0])
        for k in range(1,35):
            try:
                self.setTabOrder(self.configTabs.widget(0).hand2Transcription[k],
                                 self.configTabs.widget(0).hand2Transcription[k+1])
            except IndexError:
                pass
        self.setTabOrder(self.configTabs.widget(0).hand2Transcription[-2],
                         self.configTabs.widget(0).hand2Transcription[-1])
        self.setTabOrder(self.configTabs.widget(0).hand2Transcription[-1],
                         self.configTabs.widget(1))
        self.setTabOrder(self.configTabs.widget(1),
                         self.configTabs.widget(1).hand1Transcription[0])
        for k in range(1,35):
            try:
                self.setTabOrder(self.configTabs.widget(1).hand1Transcription[k],
                         self.configTabs.widget(1).hand1Transcription[k+1])
            except IndexError:
                pass
        self.setTabOrder(self.configTabs.widget(1).hand1Transcription[-2],
                         self.configTabs.widget(1).hand1Transcription[-1])
        self.setTabOrder(self.configTabs.widget(1).hand1Transcription[-1],
                         self.configTabs.widget(1).hand2Transcription[0])
        for k in range(1,35):
            try:
                self.setTabOrder(self.configTabs.widget(1).hand2Transcription[k],
                                self.configTabs.widget(1).hand2Transcription[k+1])
            except IndexError:
                pass
        self.setTabOrder(self.configTabs.widget(1).hand2Transcription[-2],
                         self.configTabs.widget(1).hand2Transcription[-1])
        self.setTabOrder(self.configTabs.widget(1).hand2Transcription[-1],
                         self.featuresLayout.major)
        self.setTabOrder(self.featuresLayout.major, self.featuresLayout.minor)
        self.setTabOrder(self.featuresLayout.minor, self.featuresLayout.movement)
        self.setTabOrder(self.featuresLayout.movement, self.featuresLayout.orientation)

    def writeSettings(self):
        self.settings = QSettings('UBC Phonology Tools', application='SLP-Annotator')
        self.settings.beginGroup('constraints')
        for c in MasterConstraintList:
            name = c[0]
            self.settings.setValue(name, self.constraints[name])
        # self.settings.setValue('medialJointConstraint', self.constraints['medialJointConstraint'])
        # self.settings.setValue('noEmptySlotsConstraint', self.constraints['noEmptySlotsConstraint'])
        # self.settings.setValue('distalMedialCorrespondanceConstraint', self.constraints['distalMedialCorrespondanceConstraint'])
        self.settings.endGroup()

        self.settings.beginGroup('transcriptions')
        self.settings.setValue('restrictedTranscriptions', self.setRestrictionsAct.isChecked())
        self.settings.endGroup()

        self.settings.beginGroup('features')
        self.settings.setValue('majorLocations',
                                        ['Head', 'Arm', 'Trunk', 'Non-dominant', 'Neutral'])
        self.settings.setValue('minorLocations',
                                        {'Head': ['Cheek nose', 'Chin', 'Eye', 'Forehead',
                                                    'Head top', 'Mouth', 'Under chin', 'Upper lip'],
                                        'Arm': ['Elbow (back)', 'Elbow (front)', 'Forearm (back)', 'Forearm (front)',
                                                    'Forearm (ulnar)', 'Upper arm','Wrist (back)', 'Wrist (front)'],
                                        'Trunk': ['Clavicle', 'Hips', 'Neck', 'Neutral', 'Shoulder',
                                                    'TorsoBottom', 'TorsoMid', 'TorsoTop', 'Waist'],
                                        'Non-dominant': ['Finger (back)', 'Finger (front)', 'Finger (radial)',
                                                         'Finger (ulnar)', 'Heel', 'Palm (front)', 'Palm (back)'],
                                        'Neutral': ['FingerRadial', 'Neutral', 'Palm']})
        self.settings.setValue('movements',
                                        ['Arc', 'Circular', 'Straight', 'Back and forth', 'No movement', 'Multiple'])
        self.settings.setValue('orientations',
                                        ['Front', 'Back', 'Side', 'Up', 'Down'])
        self.settings.endGroup()

    def readSettings(self):
        self.settings = QSettings('UBC Phonology Tools', application='SLP-Annotator')

        self.settings.beginGroup('constraints')
        for c in MasterConstraintList:
            name = c[0]
            self.constraints[name] = self.settings.value(name, type=bool)
        # self.constraints['medialJointConstraint'] = self.settings.value('medialJointConstraint', type=bool)
        # self.constraints['distalMedialCorrespondanceConstraint'] = self.settings.value('distalMedialCorrespondanceConstraint', type=bool)
        # self.constraints['noEmptySlotsConstraint'] = self.settings.value('noEmptySlotsConstraint', type=bool)
        self.settings.endGroup()

        self.settings.beginGroup('transcriptions')
        self.restrictedTranscriptions = self.settings.value('restrictedTranscriptions', type=bool)
        self.setRestrictionsAct.setChecked(self.restrictedTranscriptions)
        self.transcriptionRestrictionsChanged.emit(self.restrictedTranscriptions)
        self.settings.endGroup()

        self.settings.beginGroup('features')
        self.majorLocations = self.settings.value('majorLocations',
                                                  defaultValue=['Head', 'Arm', 'Trunk', 'Non-dominant', 'Neutral'])
        self.minorLocations = self.settings.value('minorLocations',
                                                  defaultValue={'Head': ['Cheek nose', 'Chin', 'Eye', 'Forehead',
                                                    'Head top', 'Mouth', 'Under chin', 'Upper lip'],
                                        'Arm': ['Elbow (back)', 'Elbow (front)', 'Forearm (back)', 'Forearm (front)',
                                                    'Forearm (ulnar)', 'Upper arm','Wrist (back)', 'Wrist (front)'],
                                        'Trunk': ['Clavicle', 'Hips', 'Neck', 'Neutral', 'Shoulder',
                                                    'TorsoBottom', 'TorsoMid', 'TorsoTop', 'Waist'],
                                        'Non-dominant': ['Finger (back)', 'Finger (front)', 'Finger (radial)',
                                                         'Finger (ulnar)', 'Heel', 'Palm (front)', 'Palm (back)'],
                                        'Neutral': ['FingerRadial', 'Neutral', 'Palm']})
        self.movements = self.settings.value('movements',
                                             defaultValue=['Arc', 'Circular', 'Straight', 'Back and forth',
                                                           'No movement', 'Multiple'])
        self.orientations = self.settings.value('orientations',
                                                defaultValue=['Front', 'Back', 'Side', 'Up', 'Down'])
        self.settings.endGroup()

    def closeEvent(self, e):
        self.writeSettings()
        super().closeEvent()

    def checkTranscription(self):
        alert = TranscriptionMessageBox(self.constraints, self.configTabs)
        alert.exec_()
        return

    def launchBlender(self):
        blenderPath = r'C:\Program Files\Blender Foundation\Blender\blender.exe'
        if not os.path.exists(blenderPath):
            blenderPath = r'C:\Program Files (x86)\Blender Foundation\Blender\blender.exe'
        if not os.path.exists(blenderPath):
            blenderPath = '~/Application/blender.app'
        blenderFile = os.path.join(os.getcwd(), 'handForPCT.blend')
        blenderScript = os.path.join(os.getcwd(), 'position_hand.py')

        code = self.configTabs.widget(0).hand1Transcription.blenderCode()
        with open(os.path.join(os.getcwd(), 'handCode.txt'), mode='w', encoding='utf-8') as f:
            f.write(code)

        proc = subprocess.Popen(
            [blenderPath,
              blenderFile,
             #'--background',
              "--python", blenderScript])
        proc.communicate()
        # try:
        #     outs, errs = proc.communicate(timeout=15)
        # except TimeoutExpired:
        #     proc.kill()
        #     outs, errs = proc.communicate()

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())


    def makeCorpusDock(self):
        self.corpusDock = QDockWidget()
        self.corpusDock.setWindowTitle('Corpus')
        self.corpusDock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.corpusDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dockWrapper = QWidget()
        self.dockLayout = QVBoxLayout()
        self.dockWrapper.setLayout(self.dockLayout)
        self.corpusDock.setWidget(self.dockWrapper)
        self.addDockWidget(Qt.RightDockWidgetArea, self.corpusDock)

    def loadCorpus(self):
        file_path = QFileDialog.getOpenFileName(self,
                'Open Corpus File', os.getcwd(), '*.corpus')
        file_path = file_path[0]
        if not file_path:
            return
        self.clearLayout(self.dockLayout)
        self.newGloss(giveWarning=False)
        self.corpus = load_binary(file_path)
        for sign in self.corpus:
            data = sign.data()
            self.addButtonToDock(data)
        self.showMaximized()

    def saveCorpus(self):
        if not self.gloss.glossEdit.text():
            alert = QMessageBox()
            alert.setWindowTitle('Missing gloss')
            alert.setText('Please enter a gloss before saving')
            alert.exec_()
            return

        kwargs = self.generateKwargs()
        if self.corpus is None:
            alert = QMessageBox()
            alert.setWindowTitle('No corpus loaded')
            alert.setText('You must have a corpus loaded before you can save words. What would you like to do?')
            alert.addButton('Add this word to an existing corpus', QMessageBox.AcceptRole)
            alert.addButton('Create a new corpus', QMessageBox.RejectRole)
            alert.exec_()
            role = alert.buttonRole(alert.clickedButton())
            if role ==  1:#create new corpus
                savename = QFileDialog.getSaveFileName(self, 'Save Corpus File', os.getcwd(), '*.corpus')
                path = savename[0]
                if not path:
                    return
                if not path.endswith('.corpus'):
                    path = path + '.corpus'
                kwargs['file_mode'] = 'w'
                kwargs['path'] = path
                kwargs['name'] = os.path.split(path)[1].split('.')[0]
                self.corpus = Corpus(kwargs)

            elif role == 0: #load existing corpus and add to it
                self.loadCorpus()

        else: #corpus exists
            kwargs['path'] = self.corpus.path
            kwargs['file_mode'] = 'a'
            if kwargs['gloss'] in self.corpus.wordlist:
                alert = QMessageBox()
                alert.setWindowTitle('Duplicate entry')
                alert.setText('A word with the gloss {} already exists in your corpus. '
                                'What do you want to do?'.format(kwargs['gloss']))
                alert.addButton('Overwrite exising word', QMessageBox.AcceptRole)
                alert.addButton('Go back and edit the gloss', QMessageBox.RejectRole)
                alert.exec_()
                role = alert.buttonRole(alert.clickedButton())
                if role == 0:#overwrite
                    pass
                elif role == 1:#edit
                    return

        self.addButtonToDock(kwargs)
        self.corpus.addWord(Sign(kwargs))
        save_binary(self.corpus, kwargs['path'])
        QMessageBox.information(self, 'Success', 'Corpus successfully updated!')

    def addButtonToDock(self, kwargs):
        button = DataButton(kwargs)
        button.sendData.connect(self.loadHandShape)
        self.corpusDock.widget().layout().addWidget(button)

    def newCorpus(self):
        self.corpus = None
        self.newGloss()
        self.clearLayout(self.dockLayout)

    def loadHandShape(self, buttonData):

        self.gloss.glossEdit.setText(buttonData['gloss'])
        config1 = self.configTabs.widget(0)
        config2 = self.configTabs.widget(1)

        config1hand1 = buttonData['config1hand1']
        for num, slot in enumerate(config1.hand1Transcription.slots):
            if num == 0:
                slot.setChecked(config1hand1[0])
            else:
                slot.setText(config1hand1[num])

        config1hand2 = buttonData['config1hand2']
        for num, slot in enumerate(config1.hand2Transcription.slots):
            if num == 0:
                slot.setChecked(config1hand2[0])
            else:
                slot.setText(config1hand2[num])

        config2hand1 = buttonData['config2hand1']
        for num, slot in enumerate(config2.hand1Transcription.slots):
            if num == 0:
                slot.setChecked(config2hand1[0])
            else:
                slot.setText(config2hand1[num])

        config2hand2 = buttonData['config2hand2']
        for num, slot in enumerate(config2.hand2Transcription.slots):
            if num == 0:
                slot.setChecked(config2hand2[0])
            else:
                slot.setText(config2hand2[num])

        for name in ['major', 'minor', 'movement', 'orientation']:
            widget = getattr(self.featuresLayout, name)
            index = widget.findText(buttonData[name])
            if index == -1:
                index = 0
            widget.setCurrentIndex(index)

    def generateSign(self):
        data = {'config1': None, 'config2': None,
                'major': None, 'minor': None, 'movement': None, 'orientation': None}
        config1 = self.configTabs.widget(0).findChildren(TranscriptionLayout)
        data['config1'] = [config1[0].text(), config1[1].text()]
        config2 = self.configTabs.widget(1).findChildren(TranscriptionLayout)
        data['config2'] = [config2[0].text(), config2[1].text()]
        gloss = self.gloss.glossEdit.text().strip()
        data['gloss'] = gloss
        major = self.featuresLayout.major.currentText()
        data['major'] = 'None' if major == 'Major Location' else major
        minor = self.featuresLayout.minor.currentText()
        data['minor'] = 'None' if minor == 'Minor Location' else minor
        movement = self.featuresLayout.movement.currentText()
        data['movement'] = 'None' if movement == 'Movement' else movement
        orientation = self.featuresLayout.orientation.currentText()
        data['orientation'] = 'None' if orientation == 'Orientation' else orientation
        return Sign(data)

    def generateKwargs(self):
        kwargs = {'path': None, 'file_mode': None,
                'config1': None, 'config2': None,
                'major': None, 'minor': None, 'movement': None, 'orientation': None}
        config1 = self.configTabs.widget(0)#.findChildren(TranscriptionLayout)
        kwargs['config1'] = [config1.hand1(), config1.hand2()]
        config2 = self.configTabs.widget(1)#.findChildren(TranscriptionLayout)
        kwargs['config2'] = [config2.hand1(), config2.hand2()]
        gloss = self.gloss.glossEdit.text().strip()
        kwargs['gloss'] = gloss
        major = self.featuresLayout.major.currentText()
        kwargs['major'] = 'None' if major == 'Major Location' else major
        minor = self.featuresLayout.minor.currentText()
        kwargs['minor'] = 'None' if minor == 'Minor Location' else minor
        movement = self.featuresLayout.movement.currentText()
        kwargs['movement'] = 'None' if movement == 'Movement' else movement
        orientation = self.featuresLayout.orientation.currentText()
        kwargs['orientation'] = 'None' if orientation == 'Orientation' else orientation
        return kwargs

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&Menu")
        self.fileMenu.addAction(self.newCorpusAct)
        self.fileMenu.addAction(self.loadCorpusAct)
        self.fileMenu.addAction(self.saveCorpusAct)
        self.fileMenu.addAction(self.newGlossAct)
        self.fileMenu.addAction(self.exportCorpusAct)
        self.fileMenu.addAction(self.quitAct)
        self.settingsMenu = self.menuBar().addMenu('&Settings')
        self.settingsMenu.addAction(self.setRestrictionsAct)
        self.settingsMenu.addAction(self.setConstraintsAct)
        self.featuresMenu = self.menuBar().addMenu('&Features')
        self.featuresMenu.addAction(self.defineFeaturesAct)

    def createActions(self):

        self.newCorpusAct = QAction('&New corpus...',
                                    self,
                                    statusTip="Start a new corpus", triggered = self.newCorpus)

        self.loadCorpusAct = QAction( "&Load corpus...",
                self,
                statusTip="Load a corpus", triggered=self.loadCorpus)

        self.saveCorpusAct = QAction( "&Save corpus...",
                self,
                statusTip="Save a corpus", triggered=self.saveCorpus)

        self.newGlossAct = QAction('&New gloss',
                self,
                statusTip='Clear current info and make a new gloss',
                triggered=self.newGloss)

        self.quitAct = QAction( "&Quit",
                self,
                statusTip="Quit", triggered=self.closeEvent)

        self.exportCorpusAct = QAction('&Export corpus as csv',
                                    self,
                                    statusTip='Save corpus as csv for opening as a spreadsheet',
                                    triggered=self.exportCorpus)

        self.setRestrictionsAct = QAction('Allow &unrestricted transcriptions',
                                    self,
                                    statusTip = 'If on, anything can be entered into transcriptions',
                                    triggered = self.setTranscriptionRestrictions,
                                    checkable = True)
        self.setConstraintsAct = QAction('Select anatomical/phonological constraints',
                                    self,
                                    statusTip = 'Select constraints on transcriptions',
                                    triggered = self.setConstraints)
        self.defineFeaturesAct = QAction('View/edit major feature values...',
                                        self,
                                        statusTip = 'View/edit major feature values',
                                        triggered = self.defineFeatures)

    def defineFeatures(self):
        dialog = FeaturesDialog([self.majorLocations, self.minorLocations, self.movements, self.orientations])
        results = dialog.exec_()
        if results:
            self.featuresLayout.major.clear()
            for item in dialog.majorLocationList:
                self.featuresLayout.major.addItem(item)
                print(item)
            self.featuresLayout.minor.clear()
            for item in dialog.minorLocationList:
                self.featuresLayout.minor.addItem(item)
            self.featuresLayout.movement.clear()
            for item in dialog.movementList:
                self.featuresLayout.movement.addItem(item)
            self.featuresLayout.orientation.clear()
            for item in dialog.orientationList:
                self.featuresLayout.orientation.addItem(item)

    def setConstraints(self):
        dialog = ConstraintsDialog(self.constraints)
        constraints = dialog.exec_()
        if constraints:
            for c in MasterConstraintList:
                self.constraints[c[0]] = getattr(dialog, c[0]).isChecked()
            # self.constraints['distalMedialCorrespondanceConstraint'] = dialog.distalMedialCorrespondanceConstraint.isChecked()
            # self.constraints['medialJointConstraint'] = dialog.medialJointConstraint.isChecked()
            # self.constraints['noEmptySlotsConstraint'] = dialog.noEmptySlotsConstraint.isChecked()

    def setTranscriptionRestrictions(self):
        restricted = self.setRestrictionsAct.isChecked()
        self.restrictedTranscriptions = restricted
        self.transcriptionRestrictionsChanged.emit(restricted)

    def exportCorpus(self):

        dialog = ExportCorpusDialog()
        results = dialog.exec_()

        if results:
            path = dialog.fileNameEdit.text()
            include_fields = dialog.includeFields.isChecked()
            blank_space = dialog.blankSpaceEdit.text()
            x_in_box = dialog.xInBoxEdit.text()
            if not blank_space:
                blank_space = ''
            output = [word.export(include_fields=include_fields, blank_space=blank_space, x_in_box=x_in_box)
                      for word in self.corpus]

            with open(path, encoding='utf-8', mode='w') as f:
                print(Sign.headers, file=f)
                for word in output:
                    print(word, file=f)

            QMessageBox.information(self, 'Success', 'Corpus successfully exported!')


    def sizeHint(self):
        sz = QMainWindow.sizeHint(self)
        minWidth = self.menuBar().sizeHint().width()
        if sz.width() < minWidth:
            sz.setWidth(minWidth)
        if sz.height() < 400:
            sz.setHeight(400)
        return sz

    def handleMessage(self):
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

    def cleanUp(self):
        # Clean up everything
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)

    def newGloss(self, giveWarning=True):
        if giveWarning:
            alert = QMessageBox()
            alert.setWindowTitle('Warning')
            alert.setText('This will erase the information for the current word, '
                          'and you will lose any unsaved changes.\n What would you like to do?')
            alert.addButton('Continue without saving', QMessageBox.AcceptRole)
            alert.addButton('Go back', QMessageBox.RejectRole)
            alert.exec_()
            role = alert.buttonRole(alert.clickedButton())
            if role == 0:#AcceptRole:
                pass
            elif role == 1:#RejectRole
                return
        self.gloss.glossEdit.setText('')
        self.configTabs.widget(0).clearAll()
        self.configTabs.widget(1).clearAll()
        self.featuresLayout.reset()

class ConstraintsDialog(QDialog):

    def __init__(self, constraints):
        super().__init__()

        self.setWindowTitle('Select constraints')

        layout = QVBoxLayout()

        for c in MasterConstraintList:
            checkBox = QCheckBox(c[1].explanation)
            setattr(self, c[0], checkBox)
            if constraints[c[0]]:
                checkBox.setChecked(True)
            layout.addWidget(checkBox)


        # self.medialJointConstraint = QCheckBox('No medial joint can be marked H')
        # if constraints['medialJointConstraint']:
        #     self.medialJointConstraint.setChecked(True)
        # layout.addWidget(self.medialJointConstraint)
        #
        # self.distalMedialCorrespondanceConstraint = QCheckBox('Distal and medial joints must match in flexion')
        # if constraints['distalMedialCorrespondanceConstraint']:
        #     self.distalMedialCorrespondanceConstraint.setChecked(True)
        # layout.addWidget(self.distalMedialCorrespondanceConstraint)
        #
        # self.noEmptySlotsConstraint = QCheckBox('All transcription slots must contain a value')
        # if constraints['noEmptySlotsConstraint']:
        #     self.noEmptySlotsConstraint.setChecked(True)
        # layout.addWidget(self.noEmptySlotsConstraint)


        buttonLayout = QHBoxLayout()
        selectAllButton = QPushButton('Select all')
        selectAllButton.clicked.connect(self.selectAll)
        buttonLayout.addWidget(selectAllButton)
        removeAllButton = QPushButton('Unselect all')
        removeAllButton.clicked.connect(self.removeAll)
        buttonLayout.addWidget(removeAllButton)
        ok = QPushButton('OK')
        cancel = QPushButton('Cancel')
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttonLayout.addWidget(ok)
        buttonLayout.addWidget(cancel)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def selectAll(self):
        for c in MasterConstraintList:
            getattr(self, c[0]).setChecked(True)
        # self.medialJointConstraint.setChecked(True)
        # self.distalMedialCorrespondanceConstraint.setChecked(True)
        # self.noEmptySlotsConstraint.setChecked(True)

    def removeAll(self):
        for c in MasterConstraintList:
            getattr(self, c[0]).setChecked(False)
        # self.medialJointConstraint.setChecked(False)
        # self.distalMedialCorrespondanceConstraint.setChecked(False)
        # self.noEmptySlotsConstraint.setChecked(False)



class ExportCorpusDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Export Corpus')

        layout = QVBoxLayout()

        fileNameLayout = QHBoxLayout()
        self.fileNameEdit = QLineEdit('')
        self.fileNameEdit.setPlaceholderText('')
        selectLocationButton = QPushButton('Select save location...')
        selectLocationButton.clicked.connect(self.getSaveName)
        fileNameLayout.addWidget(selectLocationButton)
        fileNameLayout.addWidget(self.fileNameEdit)
        layout.addLayout(fileNameLayout)

        outputOptionsLayout = QVBoxLayout()
        blankSpaceLabel = QLabel('\n\nWhich character should be used to represent empty transcription slots?\n'
                                 'Mouse over the text box for details.')
        blankSpaceLabel.setWordWrap(True)
        self.blankSpaceEdit = QLineEdit('')
        self.blankSpaceEdit.setMaximumWidth(100)
        self.blankSpaceEdit.setToolTip('If you want empty slots to appear as blank spaces, then type one space.'
                                  '\nIf you do not want empty slots represented at all in the output, type nothing.')

        self.includeFields = QCheckBox('Include fields in transcription?')
        self.includeFields.setToolTip('If checked, transcriptions will be delimited by square brackets '
                                  'and numbers representing fields.\n'
                                  'If not checked, transcriptions will be one long string.')

        xinBoxLabel = QLabel('Some programs have trouble displaying the "ultracrossed" symbol (x-in-a-box). If you '
                                  'would like to have an alternative symbol in the output file, enter it below.')
        xinBoxLabel.setWordWrap(True)
        self.xInBoxEdit = QLineEdit('')
        self.xInBoxEdit.setMaximumWidth(100)

        outputOptionsLayout.addWidget(self.includeFields)
        outputOptionsLayout.addWidget(blankSpaceLabel)
        # outputOptionsLayout.addWidget(blankSpaceLabel2)
        outputOptionsLayout.addWidget(self.blankSpaceEdit)

        outputOptionsLayout.addWidget(xinBoxLabel)
        outputOptionsLayout.addWidget(self.xInBoxEdit)
        layout.addLayout(outputOptionsLayout)

        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton('OK')
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)
        self.okButton.clicked.connect(self.accept)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def getSaveName(self):
        savename = QFileDialog.getSaveFileName(self, 'Export Corpus as CSV', os.getcwd(), '*.csv')
        path = savename[0]
        if not path:
            return
        if not path.endswith('.csv'):
            path = path + '.csv'
        self.fileNameEdit.setText(path)

    def accept(self):
        if os.path.exists(os.path.split(self.fileNameEdit.text())[0]):
            super().accept()
        else:
            if not self.fileNameEdit.text():
                text = 'Please enter a file name'
            else:
                text = ('The file name you supplied is not valid. Use the "Select save location..." '
                          'button to select a folder on your computer, and then a enter a name for your output file.')
            alert = QMessageBox()
            alert.setWindowTitle('File name error')
            alert.setText(text)
            alert.exec_()

class DataButton(QPushButton):

    sendData = Signal(dict)
    def __init__(self, data):
        QPushButton.__init__(self)
        self.gloss = data['gloss']
        self.setText(self.gloss)
        self.config1hand1, self.config1hand2 = data['config1']
        self.config2hand1, self.config2hand2 = data['config2']
        self.major = data['major']
        self.minor = data['minor']
        self.movement = data['movement']
        self.orientation = data['orientation']
        self.setData()
        self.clicked.connect(self.emitData)

    def setData(self):
        self.data ={'major': self.major, 'minor': self.minor,
                    'movement':self.movement, 'orientation': self.orientation,
                    'config1hand1': self.config1hand1, 'config1hand2': self.config1hand2,
                    'config2hand1': self.config2hand1, 'config2hand2': self.config2hand2,
                    'gloss': self.gloss}

    def emitData(self):
        self.sendData.emit(self.data)



def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(item.pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError): # deleted or no close method
            pass
        try:
            item.deleteLater()
        except (RuntimeError, AttributeError): # deleted or no deleteLater method
            pass

def sortData(data):
    if data == 'gloss':
        return 0
    elif data == 'config1':
        return 1
    elif data == 'config2':
        return 2
    elif data == 'major':
        return 3
    elif data == 'minor':
        return 4
    elif data == 'movement':
        return 5
    elif data == 'orientation':
        return 6

def loadcsvCorpus(path):
    with open(path, mode='r', encoding='utf-8') as file:
        headers = file.readline().strip().split(',')
        for line in file:
            line = line.split(',')
            data = {headers[n]: line[n] for n in range(len(headers))}
            button = DataButton(data)
            button.sendData.connect(self.loadHandShape)
            self.corpusDock.widget().layout().addWidget(button)

def getMediaFilePath(filename):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', filename)
    return path