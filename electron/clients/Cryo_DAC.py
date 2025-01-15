from PyQt4 import QtGui, QtCore, uic
from numpy import *
# from qtui.QCustomSpinBoxION import QCustomSpinBoxION
from qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks, returnValue
import sys
# sys.path.append('/home/LabRAD/common/okfpgaservers/dacserver/')
from common.okfpgaservers.dacserver.DacConfiguration import hardwareConfiguration as hc
# from DacConfiguration import hardwareConfiguration as hc


UpdateTime = 100 # ms
SIGNALID = 270836
SIGNALID2 = 270835

class MULTIPOLE_CONTROL(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(MULTIPOLE_CONTROL, self).__init__(parent)
        self.updating = False
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks    
    def makeGUI(self):
        self.multipoles = yield self.dacserver.get_multipole_names()
        self.controls = {k: QCustomSpinBox(k, (-20.,20.)) for k in self.multipoles}
        self.multipoleValues = {k: 0.0 for k in self.multipoles}
        
        for k in self.multipoles:
            self.ctrlLayout.addWidget(self.controls[k])        
        self.multipoleFileSelectButton = QtGui.QPushButton('Set C File')
        self.ctrlLayout.addWidget(self.multipoleFileSelectButton)

        self.inputUpdated = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)   

        for k in self.multipoles:
            self.controls[k].onNewValues.connect(self.inputHasUpdated)
        self.multipoleFileSelectButton.released.connect(self.selectCFile)
        self.setLayout(self.ctrlLayout)
        yield self.followSignal(0, 0)	
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        yield self.setupListeners()
        self.ctrlLayout = QtGui.QVBoxLayout()
        yield self.makeGUI()
        
    def inputHasUpdated(self):
        self.inputUpdated = True
        for k in self.multipoles:
            self.multipoleValues[k] = round(self.controls[k].spinLevel.value(), 3)
        
    def sendToServer(self):
        if self.inputUpdated:
            self.dacserver.set_multipole_values(self.multipoleValues.items())
            self.inputUpdated = False
    
    @inlineCallbacks        
    def selectCFile(self):
        fn = QtGui.QFileDialog().getOpenFileName()
        self.updating = True
        yield self.dacserver.set_control_file(str(fn))
        for i in range(self.ctrlLayout.count()): self.ctrlLayout.itemAt(i).widget().close()
        self.updating = False
        yield self.makeGUI()
        self.inputHasUpdated()
        
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID) 
        
    @inlineCallbacks
    def followSignal(self, x, s):
        if self.updating: return
        multipoles = yield self.dacserver.get_multipole_values()
        for (k,v) in multipoles:
            self.controls[k].setValueNoSignal(v)          

    def closeEvent(self, x):
        self.reactor.stop()  

class CHANNEL_CONTROL (QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(CHANNEL_CONTROL, self).__init__(parent)
        self.reactor = reactor
        self.makeGUI()
        self.connect()
     
    def makeGUI(self):
        self.dacDict = dict(hc.elec_dict.items())# + hc.sma_dict.items())
        self.controls = {k: QCustomSpinBox(k, self.dacDict[k].allowedVoltageRange) for k in self.dacDict.keys()}
        elecList = hc.elec_dict.keys()
        elecList.sort()
        print elecList

        layout = QtGui.QGridLayout()
        # if bool(hc.sma_dict):
        #     smaBox = QtGui.QGroupBox('SMA Out')
        #     smaLayout = QtGui.QVBoxLayout()
        #     smaBox.setLayout(smaLayout)
        elecBox0 = QtGui.QGroupBox('Top Ground')
        elecLayout0 = QtGui.QGridLayout()
        elecBox0.setLayout(elecLayout0)
        layout.addWidget(elecBox0, 0, 0)
        #elecLayout0.addWidget(self.controls['tg'], 0, 0)
        elecBox1 = QtGui.QGroupBox('Top Electrodes')
        elecLayout1 = QtGui.QGridLayout()
        elecBox1.setLayout(elecLayout1)
        layout.addWidget(elecBox1, 1, 0)
        # QtGui.QGridLayout.addWidget(QtGui.QGroupBox('Electrodes'), 0, 3)

        # for s in hc.sma_dict:
        #     smaLayout.addWidget(self.controls[s], alignment = QtCore.Qt.AlignRight)
        
        
        # if bool(hc.centerElectrode):
        #     elecList.pop(hc.centerElectrode-1)
        
        for i,e in enumerate(elecList):
            # if e[0:2] == 'bl':
            #     print len(elecList)/4 - int(i)
            #     elecLayout1.addWidget(self.controls[e], len(elecList)/4 - int(i), 2)
            # elif e[0:2] == 'br':
            #     print len(elecList)/2 - int(i)
            #     elecLayout1.addWidget(self.controls[e], len(elecList)/2 - int(i), 3)
            if e[0:2] == 'tl':
                elecLayout1.addWidget(self.controls[e], 3*len(elecList)/4 - int(i)+1, 0)
            elif e[0:2] == 'tr':
                elecLayout1.addWidget(self.controls[e], 4*len(elecList)/4 - int(i), 1)
            # elif e[0:2] =='tg':
        # if bool(hc.centerElectrode):
        #     self.controls[str(hc.centerElectrode).zfill(2)].title.setText('TOP')
        #     elecLayout.addWidget(self.controls[str(hc.centerElectrode).zfill(2)], len(elecList)/2, 1) 

        elecBox2 = QtGui.QGroupBox('Bottom Electrodes')
        elecLayout2 = QtGui.QGridLayout()
        elecBox2.setLayout(elecLayout2)
        layout.addWidget(elecBox2, 1, 1)

        for i,e in enumerate(elecList):
            if e[0:2] == 'bl':
                elecLayout2.addWidget(self.controls[e], len(elecList)/4 - int(i), 0)
            elif e[0:2] == 'br':
                elecLayout2.addWidget(self.controls[e], len(elecList)/2 - int(i), 3)

        spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
        # if bool(hc.sma_dict):
        #     smaLayout.addItem(spacer)        
        self.inputUpdated = False                
        self.timer = QtCore.QTimer(self)        
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
        for k in self.dacDict.keys():
            self.controls[k].onNewValues.connect(self.inputHasUpdated(k))

        layout.setColumnStretch(1, 1)                   
        self.setLayout(layout)

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        yield self.setupListeners()
        yield self.followSignal(0, 0)

    def inputHasUpdated(self, name):
        def iu():
            self.inputUpdated = True
            self.changedChannel = name
        return iu

    def sendToServer(self):
        if self.inputUpdated:            
            self.dacserver.set_individual_analog_voltages([(self.changedChannel, round(self.controls[self.changedChannel].spinLevel.value(), 3))]*17)
            self.inputUpdated = False
            
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):
        print 'notified here'
        print self.dacserver.get_analog_voltages()
        av = yield self.dacserver.get_analog_voltages()
        for (c, v) in av:
            self.controls[c].setValueNoSignal(v)

    def closeEvent(self, x):
        self.reactor.stop()        

class CHANNEL_MONITOR(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(CHANNEL_MONITOR, self).__init__(parent)
        self.reactor = reactor        
        self.makeGUI()
        self.connect()
       
        
    def makeGUI(self):      
        self.dacDict = dict(hc.elec_dict.items())# + hc.sma_dict.items())
        self.displays = {k: QtGui.QLCDNumber() for k in self.dacDict.keys()}  
        elecList = hc.elec_dict.keys()
        elecList.sort()

        layout = QtGui.QGridLayout()

        elecBox0 = QtGui.QGroupBox('Top Ground')
        elecLayout0 = QtGui.QGridLayout()
        elecBox0.setLayout(elecLayout0)
        layout.addWidget(elecBox0, 0, 0)
        elecLayout0.addWidget(QtGui.QLabel('tg'), 0, 2)
        #elecLayout0.addWidget(self.displays['tg'], 0, 3)

        elecBox1 = QtGui.QGroupBox('Top Electrodes')
        elecLayout1 = QtGui.QGridLayout()
        elecLayout1.setColumnStretch(1, 2)
        elecLayout1.setColumnStretch(3, 2)
        elecLayout1.setColumnStretch(5, 2)
        elecBox1.setLayout(elecLayout1)
        layout.addWidget(elecBox1, 1, 1)
        

        for i,e in enumerate(elecList):
            # if bool(hc.sma_dict):            
            #     self.displays[k].setAutoFillBackground(True)
            if e[0:2] == 'tl':
                # print 3*len(elecList)/4 - int(i)
                elecLayout1.addWidget(QtGui.QLabel(e), 3*len(elecList)/4 - int(i), 0)
                elecLayout1.addWidget(self.displays[e], 3*len(elecList)/4 - int(i), 1)
            elif e[0:2] == 'tr':
                # print len(elecList) - int(i)-1
                elecLayout1.addWidget(QtGui.QLabel(e), len(elecList) - int(i)-1, 4)
                elecLayout1.addWidget(self.displays[e], len(elecList) - int(i)-1, 5)

        elecBox2 = QtGui.QGroupBox('Bottom Electrodes')
        elecLayout2 = QtGui.QGridLayout()
        elecLayout2.setColumnStretch(1, 2)
        elecLayout2.setColumnStretch(3, 2)
        elecLayout2.setColumnStretch(5, 2)
        elecBox2.setLayout(elecLayout2)
        layout.addWidget(elecBox2, 2, 1)
        

        for i,e in enumerate(elecList):
            # if bool(hc.sma_dict):            
            #     self.displays[k].setAutoFillBackground(True)
            if e[0:2] == 'bl':
                # print len(elecList)/4 - int(i) - 1
                elecLayout2.addWidget(QtGui.QLabel(e), len(elecList)/4 - int(i)-1, 0)
                elecLayout2.addWidget(self.displays[e], len(elecList)/4 - int(i)-1, 1)
            elif e[0:2] == 'br':
                # print len(elecList)/2 - int(i) - 1
                elecLayout2.addWidget(QtGui.QLabel(e), len(elecList)/2 - int(i)-1, 4)
                elecLayout2.addWidget(self.displays[e], len(elecList)/2 - int(i)-1, 5)
 

 

        self.setLayout(layout)  
                
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        self.ionInfo = {}
        yield self.setupListeners()
        yield self.followSignal(0, 0)    
        for i in hc.notused_dict:        #Sets unused channels to about 0V
            yield self.dacserver.set_individual_digital_voltages_u([(i, 32768)])     

                  
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):        
        av = yield self.dacserver.get_analog_voltages()
        brightness = 210
        darkness = 255 - brightness           
        for (k, v) in av:
            print k
            print v
            self.displays[k].display(float(v)) 
            if abs(v) > 30:
                self.displays[k].setStyleSheet("QWidget {background-color: orange }")
            else:
                R = int(brightness + v*darkness/30.)
                G = int(brightness - abs(v*darkness/30.))
                B = int(brightness - v*darkness/30.)
                hexclr = '#%02x%02x%02x' % (R, G, B)
                self.displays[k].setStyleSheet("QWidget {background-color: "+hexclr+" }")

    def closeEvent(self, x):
        self.reactor.stop()

class DAC_Control(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(DAC_Control, self).__init__(parent)
        self.reactor = reactor   

        channelControlTab = self.buildChannelControlTab()        
        multipoleControlTab = self.buildMultipoleControlTab()
        # scanTab = self.buildScanTab()
        tab = QtGui.QTabWidget()
        tab.addTab(multipoleControlTab,'&Multipoles')
        tab.addTab(channelControlTab, '&Channels')
        # tab.addTab(scanTab, '&Scans')
        self.setWindowTitle('Cryostat DAC Control')
        self.setCentralWidget(tab)
    
    def buildMultipoleControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_MONITOR(self.reactor),0,0)
        gridLayout.addWidget(MULTIPOLE_CONTROL(self.reactor),0,1)
        widget.setLayout(gridLayout)
        return widget

    def buildChannelControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_CONTROL(self.reactor),0,0)
        widget.setLayout(gridLayout)
        return widget
        
    def buildScanTab(self):
        from SCAN_CONTROL import Scan_Control_Tickle
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(Scan_Control_Tickle(self.reactor, 'Ex1'), 0, 0)
        gridLayout.addWidget(Scan_Control_Tickle(self.reactor, 'Ey1'), 0, 1)
        widget.setLayout(gridLayout)
        return widget
    
    def closeEvent(self, x):
        self.reactor.stop()  

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DAC_Control = DAC_Control(reactor)
    DAC_Control.show()
    reactor.run()
