# -*- coding: utf-8 -*-
import sys
import visa

from PyQt4 import QtCore, QtGui
from RCSwitch import Ui_ReverbChamberRelaisController as ui


class SWController(QtGui.QMainWindow):
    def __init__(self, sw):
        self.sw=sw
        print sw
        #save settings
        self.sw.ask('R1P0R2P0R3P1R4P1R5P0R6P0'*2)
        self.RxLF=True
        self.RxAtt=True
        self.RxPM=True
        QtGui.QMainWindow.__init__(self)
        self.ui=ui()
        self.ui.setupUi(self)
        
    def on_sgSwitch_Direct_toggled(self, state):
        if state:
            print "Switch 1: direct"
            ans=self.sw.ask('R1P0'*2)
    def on_sgSwitch_LF_toggled(self, state):
        if state:
            print "Switch 1: LF"
            ans=self.sw.ask('R1P1'*2)
    def on_sgSwitch_HF_toggled(self, state):
        if state:
            print "Switch 1: HF"
            ans=self.sw.ask('R1P2'*2)
    def on_TxSwitch_LF_toggled(self, state):
        if state:
            print "Switch 2: LF"
            ans=self.sw.ask('R2P1'*2)
    def on_TxSwitch_HF_toggled(self, state):
        if state:
            print "Switch 2: HF"
            ans=self.sw.ask('R2P2'*2)
    def on_TxSwitch_Term_toggled(self, state):
        if state:
            print "Switch 2: Term"
            ans=self.sw.ask('R2P0'*2)
    def on_RxSwitch_LF_toggled(self, state):
        self.RxLF=state
        if state:
            print "Switch 3: LF"
        self._rx_logic()
    def on_RxSwitch_HF_toggled(self, state):
        self.RxLF=not(state)
        if state:
            print "Switch 3: HF"
        self._rx_logic()
    def on_AttSwitch_On_toggled(self, state):
        self.RxAtt=state
        if state:
            print "Switch 4: 20 dB"
        self._rx_logic()
    def on_AttSwitch_Off_toggled(self, state):
        self.RxAtt=not(state)
        if state:
            print "Switch 4: 0 dB"
        self._rx_logic()
    def on_RxSwitch_PM_toggled(self, state):
        self.RxPM=state
        if state:
            print "Switch 5: Rx PM"
        self._rx_logic()
    def on_RxSwitch_Rec_toggled(self, state):
        self.RxPM=not(state)
        if state:
            print "Switch 5: Rx Rec"
        self._rx_logic()
        
    def _rx_logic(self):
        lf=self.RxLF
        att=self.RxAtt
        pm=self.RxPM
        if lf:
            if att:
                if pm:
                    cmd='R3P1R4P1R5P0R6P0'
                else:
                    cmd='R3P1R4P0R5P0R6P0'                
            else:
                if pm:
                    cmd='R3P1R4P0R5P1R6P0'                
                else:
                    cmd='R3P1R4P1R5P1R6P0'                
        else:
            if att:
                if pm:
                    cmd='R3P0R4P1R5P1R6P1'
                else:
                    cmd='R3P0R4P0R5P1R6P1'                
            else:
                if pm:
                    cmd='R3P0R4P0R5P0R6P1'                
                else:
                    cmd='R3P0R4P1R5P0R6P1'                        
        self.sw.ask(cmd*2)
        
        
def main():
    sw=visa.instrument('GPIB::2')
    
    app = QtGui.QApplication(sys.argv)
    window = SWController(sw)
    window.show()
    sys.exit(app.exec_())
        

if __name__ == "__main__":
    main()

