from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

class Electron_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, clipboard, parent=None):
        super(Electron_GUI, self).__init__(parent)
        self.clipboard = clipboard
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.clients.connection import connection
        cxn = connection()
        yield cxn.connect()
        self.create_layout(cxn)

    def create_layout(self, cxn):
        from common.clients.PMT_CONTROL import pmtWidget
        # from PMT2_CONTROL import pmtWidget as pmtWidget2
        # from quick_actions.quick_actions import actions_widget
        # from common.clients.LINETRIGGER_CONTROL import linetriggerWidget as lineTrig
        # from common.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        # from common.devel.bum.gui_scriptscanner2.script_scanner_gui import script_scanner_gui
        # from common.clients.drift_tracker.drift_tracker import drift_tracker
        # from common.clients.drift_tracker_global.drift_tracker_global import drift_tracker_global
        # from common.clients.SWITCH_CONTROL import switchWidget
        

        # dt = drift_tracker(reactor, cxn)
        # layout = QtGui.QHBoxLayout()
        # centralWidget = QtGui.QWidget()



        self.tabWidget = QtGui.QTabWidget()
        lightControlTab = self.makeLightWidget(reactor, cxn)
        # voltageControlTab = self.makeVoltageWidget(reactor)
        # piezoControlTab = self.makePiezoWidget(reactor)
        # script_scanner = script_scanner_gui(reactor, cxn)
        #grapherTab = yield self.makeGrapherWidget(reactor)
        # histogram = self.make_histogram_widget(reactor, cxn)
        # global_dt = drift_tracker_global(reactor, cxn)
        # dt = drift_tracker(reactor, cxn)

        # self.tabWidget.addTab(voltageControlTab,'&Trap Voltages')
        self.tabWidget.addTab(lightControlTab,'&Optics')
        #self.createGrapherTab()
        # self.tabWidget.addTab(dt, '&Drift Tracker')
        # self.tabWidget.addTab(global_dt, '&Global Drift Tracker')
        # self.tabWidget.addTab(script_scanner, '&Script Scanner')
        # self.tabWidget.addTab(histogram, '&Readout Histogram')
        # self.tabWidget.addTab(piezoControlTab, '&Piezo')
        # self.tabWidget.addTab(grapherTab, '&Grapher')
        
        gridLayout = QtGui.QGridLayout()
        #gridLayout.addWidget(scriptControl, 0, 0, 1, 1)
        gridLayout.addWidget(self.tabWidget, 0, 1, 1, 3)
        rightPanel = QtGui.QGridLayout()

        # rightPanel.addWidget(pmtWidget(reactor), 0, 0)
        # rightPanel.addWidget(pmtWidget2(reactor), 1, 0)
        # rightPanel.addWidget(actions_widget(reactor, cxn), 2, 0)
        # rightPanel.addWidget(lineTrig(reactor), 3, 0)
        # rightPanel.addWidget( switchWidget(reactor, cxn), 4, 0 )
        '''
        #Adding 729 Beams Position:
        #from common.clients.MOTOR_CONTROL import motorWidget

        rightPanel.addWidget( motorWidget(reactor), 2, 0)
        
        
        '''
        gridLayout.addLayout(rightPanel, 0, 4)
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Electron_GUI')


    def makeScriptControl(self, reactor):
        from common.clients.guiscriptcontrol.scriptcontrol import ScriptControl
        self.sc = ScriptControl(reactor, self)
        self.sc, self.experimentParametersWidget = self.sc.getWidgets()
        self.createExperimentParametersTab()
        return self.sc

    def createExperimentParametersTab(self):
        self.tabWidget.addTab(self.experimentParametersWidget, '&Experiment Parameters')

    def makeLightWidget(self, reactor, cxn):        
        from common.clients.LASERDAC_CONTROL import DAC_Control
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        from common.clients.DDS_CONTROL import DDS_CONTROL
        from common.clients.readout_histogram import readout_histogram
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(multiplexerWidget(reactor),0,0)
        gridLayout.addWidget(DAC_Control(reactor),0,1)
        # gridLayout.addWidget(DDS_CONTROL(reactor),0, 0)
        # gridLayout.addWidget(readout_histogram(reactor, cxn), 1, 1)
        widget.setLayout(gridLayout)
        return widget
    
    def makePiezoWidget(self, reactor):
        widget = QtGui.QWidget()
        from PIEZO_CONTROL import PIEZO_CONTROL
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(PIEZO_CONTROL(reactor), 0, 0)
        gridLayout.setRowStretch(1, 1)
        gridLayout.setColumnStretch(1, 1)
        widget.setLayout(gridLayout)
        return widget
        
    def makeVoltageWidget(self, reactor):        
        from DAC_CONTROL import DAC_Control
        #from PMT_CONTROL import pmtWidget
        #from PMT_CONTROL2 import pmtWidget as pmtWidget2
        from TRAPDRIVE_CONTROL import TD_CONTROL
        from TICKLE_CONTROL import Tickle_Control
        from SHUTTER_CONTROL import SHUTTER
        from PIEZO_CONTROL import PIEZO_CONTROL
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()        
        gridLayout.addWidget(DAC_Control(reactor), 0, 0)            
        #rightPanel = QtGui.QGridLayout()
        #rightPanel.addWidget(pmtWidget(reactor), 0, 0)       
        bottomPanel = QtGui.QGridLayout()
        bottomPanel.addWidget(Tickle_Control(reactor), 1, 1)      
        bottomPanel.addWidget(TD_CONTROL(reactor), 1, 0)
        bottomPanel.addWidget(SHUTTER(reactor), 1, 2) 
        #gridLayout.addLayout(rightPanel, 0, 1, 2, 1)          
        gridLayout.addLayout(bottomPanel, 1, 0)
        gridLayout.setRowStretch(0, 1)
        #rightPanel.setRowStretch(2, 1)            
        widget.setLayout(gridLayout)
        return widget
    
    @inlineCallbacks
    def createGrapherTab(self):
        grapherTab = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapherTab, '&Grapher')

    def make_histogram_widget(self, reactor, cxn):
         histograms_tab = QtGui.QTabWidget()
         from common.clients.readout_histogram import readout_histogram
         pmt_readout = readout_histogram(reactor, cxn)
         histograms_tab.addTab(pmt_readout, "PMT")
         return histograms_tab

    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.pygrapherlive.connections import CONNECTIONS
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)

    def makecontrol729Widget(self, reactor, cxn):
        from common.clients.control_729.control_729 import control_729
        widget = control_729(reactor, cxn)
        return widget
    #def makescriptscannerwidget(self, reactor, cxn):
    #    from common.clients.script_scanner_gui.script_scanner_gui 

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    clipboard = a.clipboard()
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Electron_GUI = Electron_GUI(reactor, clipboard)
    Electron_GUI.show()
    reactor.run()
