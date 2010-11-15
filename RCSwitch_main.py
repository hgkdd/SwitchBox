# -*- coding: utf-8 -*-
import sys
try:
    import visa
    virtual=False
except ImportError:
    virtual=True

from PyQt4 import QtCore, QtGui
from RCSwitch import Ui_ReverbChamberRelaisController as ui

class SWController(QtGui.QMainWindow):
    def __init__(self, sw):
        self.sw=sw
        #print sw
        #save settings
        self.ask('R1P0R2P0R3P1R4P1R5P0R6P0')
        self.RxLF=True
        self.RxAtt=True
        self.RxPM=True
        self.monitor=False
        QtGui.QMainWindow.__init__(self)
        self.ui=ui()
        self.setStyleSheet ("""QFrame {color: red;}
                                QFrame:disabled {color: black;}""")
        self.ui.setupUi(self)
        self.ctimer = QtCore.QTimer()
        self.ctimer.start(500)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.doUpdate)

    def doUpdate(self):
        # print 'Pling'
        s=self.sw.ask('')
        self.monitor=True
        #print s
        rdict=dict(zip(map(int, s[1::4]), map(int, s[3::4]))) #keys: relais, value: position
        s456=s[15::4]
        
        if rdict[1]==0: # direct
            self.ui.sgSwitch_Direct.click()
        elif rdict[1]==1: # LF
            self.ui.sgSwitch_LF.click()
        elif rdict[1]==2: # HF
            self.ui.sgSwitch_HF.click()

        if rdict[2]==0: # TERM
            self.ui.TxSwitch_Term.click()
        elif rdict[2]==1: # LogPer
            self.ui.TxSwitch_LF.click()
        elif rdict[2]==2: # Horn
            self.ui.TxSwitch_HF.click()

        if rdict[3]==0: # HF
            self.ui.RxSwitch_HF.click()
            if s456 == '111':
                self.ui.RxSwitch_PM.click()
                self.ui.AttSwitch_On.click()
            elif s456 == '011':
                self.ui.RxSwitch_Rec.click()
                self.ui.AttSwitch_On.click()
            elif s456 == '101':
                self.ui.RxSwitch_PM.click()
                self.ui.AttSwitch_Off.click()
            elif s456 == '110':
                self.ui.RxSwitch_Rec.click()
                self.ui.AttSwitch_Off.click()
            else:
                print "'unvisible' switch: %r"%rdict
        elif rdict[3]==1: # LF
            self.ui.RxSwitch_LF.click()
            if s456 == '100':
                self.ui.RxSwitch_PM.click()
                self.ui.AttSwitch_On.click()
            elif s456 == '000':
                self.ui.RxSwitch_Rec.click()
                self.ui.AttSwitch_On.click()
            elif s456 == '010':
                self.ui.RxSwitch_PM.click()
                self.ui.AttSwitch_Off.click()
            elif s456 == '110':
                self.ui.RxSwitch_Rec.click()
                self.ui.AttSwitch_Off.click()
            else:
                print "'unvisible' switch: %r"%rdict
        self.monitor=False
        
    
    def ask(self, cmd):
        if not self.sw:
            return None
        ans=self.sw.ask(cmd)
        # print "CMD: %s\nANS: %s"%(cmd, ans)
        # rp=[int(ans[4*i+3:4*i+4]) for i in range(6)]
        # rp.insert(0, None) # rp[1]=relais_position of R1 etc
        # # print rp[1:]
        # # K1, K2, K3
        # K1='C-%d'%(rp[2]+1)
        # K2='C-%d'%(rp[1]+1)
        # K3='C-%d'%(rp[1]+1)
        # # K4
        # if rp[3]==0:
            # K4='C-NC'
        # elif rp[3]==1:
            # K4='C-NO'
        # else:
            # K4='invalid'
        # # K5 K9    
        # if rp[1]==0:
            # K5=K9='X'
        # elif rp[1]==1:
            # K5=K9='C-NC'
        # elif rp[1]==2:
            # K5=K9='C-NO'
        # else:
            # K5=K9='invalid'
        # # K6
        # if rp[6]==0:
            # K6='C-NC'
        # elif rp[6]==1:
            # K6='C-NO'
        # else:
            # K6='invalid'
        # # K7
        # if rp[4]==0:
            # K7='1-2, 3-4'
        # elif rp[4]==1:
            # K7='1-4, 2-3'
        # else:
            # K7='invalid'
        # # K8
        # if rp[5]==0:
            # K8='1-2, 3-4'
        # elif rp[5]==1:
            # K8='1-4, 2-3'
        # else:
            # K8='invalid'
        # for i in range(1,10):
            # s=eval('K%d'%i)
            # print "K%d: %s"%(i, s)
        return ans
    
    def on_sgSwitch_Direct_toggled(self, state):
        if state:
            #print "Switch 1: direct"
            ans=self.ask('R1P0')
    def on_sgSwitch_LF_toggled(self, state):
        if state:
            #print "Switch 1: LF"
            ans=self.ask('R1P1')
    def on_sgSwitch_HF_toggled(self, state):
        if state:
            #print "Switch 1: HF"
            ans=self.ask('R1P2')
    def on_TxSwitch_LF_toggled(self, state):
        if state:
            #print "Switch 2: LF"
            ans=self.ask('R2P1')
    def on_TxSwitch_HF_toggled(self, state):
        if state:
            #print "Switch 2: HF"
            ans=self.ask('R2P2')
    def on_TxSwitch_Term_toggled(self, state):
        if state:
            #print "Switch 2: Term"
            ans=self.ask('R2P0')
    def on_RxSwitch_LF_toggled(self, state):
        self.RxLF=state
        # if state:
            #print "Switch 3: LF"
        self._rx_logic()
    def on_RxSwitch_HF_toggled(self, state):
        self.RxLF=not(state)
        # if state:
            #print "Switch 3: HF"
        self._rx_logic()
    def on_AttSwitch_On_toggled(self, state):
        if not self.monitor:
            if (not state) and self.RxLF: # this may be dangerous
                message = QtGui.QMessageBox(self)
                message.setStyleSheet('color: black')
                message.setText("""
You are going to remove the attenuation from the
RX path at low frequencies.

This may damage your power meter or receiver!

Do you really want to remove the attenuation?
                                """)
                message.setWindowTitle('Warning')
                message.setIcon(QtGui.QMessageBox.Question)
                message.addButton('No', QtGui.QMessageBox.AcceptRole)
                message.addButton('Yes', QtGui.QMessageBox.RejectRole)
                message.exec_()
                response = message.clickedButton().text()
                if response != 'Yes':
                    self.ui.AttSwitch_On.toggle()
                    return
        self.RxAtt=state
        if state:
            self.ui.conn_amp_direct_20.setEnabled(True)
            self.ui.conn_amp_direct_21.setEnabled(False)
            #print "Switch 4: 20 dB"
        else:
            self.ui.conn_amp_direct_20.setEnabled(False)
            self.ui.conn_amp_direct_21.setEnabled(True)
            #print "Switch 4: 0 dB"
        
        self._rx_logic()
#    def on_AttSwitch_Off_toggled(self, state):
#        self.RxAtt=not(state)
#        if state:
#            print "Switch 4: 0 dB"
#        self._rx_logic()
    def on_RxSwitch_PM_toggled(self, state):
        self.RxPM=state
        #if state:
            #print "Switch 5: Rx PM"
        self._rx_logic()
    def on_RxSwitch_Rec_toggled(self, state):
        self.RxPM=not(state)
        #if state:
            #print "Switch 5: Rx Rec"
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
        if not self.monitor:
            self.ask(cmd)
        
        
def main():
    if not virtual:
        try:
            sw=visa.instrument('GPIB::2', term_chars = visa.LF)
        except:
            sw=None
    else:
        sw=None

    app = QtGui.QApplication(sys.argv)
    window = SWController(sw)
    window.show()
    sys.exit(app.exec_())
        

if __name__ == "__main__":
    main()

