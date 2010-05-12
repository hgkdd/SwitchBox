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
        self.ask('R1P0R2P0R3P1R4P1R5P0R6P0')
        self.RxLF=True
        self.RxAtt=True
        self.RxPM=True
        QtGui.QMainWindow.__init__(self)
        self.ui=ui()
        self.ui.setupUi(self)
    
    def ask(self, cmd):
        ans=self.sw.ask(cmd)
        print "CMD: %s\nANS: %s"%(cmd, ans)
        rp=[int(ans[4*i+3:4*i+4]) for i in range(6)]
        rp.insert(0, None) # rp[1]=relais_position of R1 etc
        print rp[1:]
        # K1, K2, K3
        K1='C-%d'%(rp[2]+1)
        K2='C-%d'%(rp[1]+1)
        K3='C-%d'%(rp[1]+1)
        # K4
        if rp[3]==0:
            K4='C-NC'
        elif rp[3]==1:
            K4='C-NO'
        else:
            K4='invalid'
        # K5 K9    
        if rp[1]==0:
            K5=K9='X'
        elif rp[1]==1:
            K5=K9='C-NC'
        elif rp[1]==2:
            K5=K9='C-NO'
        else:
            K5=K9='invalid'
        # K6
        if rp[6]==0:
            K6='C-NC'
        elif rp[6]==1:
            K6='C-NO'
        else:
            K6='invalid'
        # K7
        if rp[4]==0:
            K7='1-2, 3-4'
        elif rp[4]==1:
            K7='1-4, 2-3'
        else:
            K7='invalid'
        # K8
        if rp[5]==0:
            K8='1-2, 3-4'
        elif rp[5]==1:
            K8='1-4, 2-3'
        else:
            K8='invalid'
        for i in range(1,10):
            s=eval('K%d'%i)
            print "K%d: %s"%(i, s)
        return ans
    
    def on_sgSwitch_Direct_toggled(self, state):
        if state:
            print "Switch 1: direct"
            ans=self.ask('R1P0')
    def on_sgSwitch_LF_toggled(self, state):
        if state:
            print "Switch 1: LF"
            ans=self.ask('R1P1')
    def on_sgSwitch_HF_toggled(self, state):
        if state:
            print "Switch 1: HF"
            ans=self.ask('R1P2')
    def on_TxSwitch_LF_toggled(self, state):
        if state:
            print "Switch 2: LF"
            ans=self.ask('R2P1')
    def on_TxSwitch_HF_toggled(self, state):
        if state:
            print "Switch 2: HF"
            ans=self.ask('R2P2')
    def on_TxSwitch_Term_toggled(self, state):
        if state:
            print "Switch 2: Term"
            ans=self.ask('R2P0')
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
        self.ask(cmd)
        
        
def main():
    sw=visa.instrument('GPIB::2', term_chars = visa.LF)
    
    app = QtGui.QApplication(sys.argv)
    window = SWController(sw)
    window.show()
    sys.exit(app.exec_())
        

if __name__ == "__main__":
    main()

