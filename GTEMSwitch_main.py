# -*- coding: utf-8 -*-
import sys
try:
    import visa
    virtual=False
except ImportError:
    virtual=True

from PyQt4 import QtCore, QtGui
from GTEMSwitch import Ui_GTEMRelaisController as ui

class SWController(QtGui.QMainWindow):
    def __init__(self, sw):
        self.sw=sw
        print sw
        #save settings
        self.ask('R1P4R2P0R3P1R4P0')
        QtGui.QMainWindow.__init__(self)
        self.ui=ui()
        self.setStyleSheet ("""QFrame {color: red;}
                                QFrame:disabled {color: black;}""")
        self.ui.setupUi(self)
    
    def ask(self, cmd):
        if not self.sw:
            return None
        ans=self.sw.ask(cmd)
        print "CMD: %s\nANS: %s"%(cmd, ans)
        rp=[int(ans[4*i+3:4*i+4]) for i in range(4)]
        rp.insert(0, None) # rp[1]=relais_position of R1 etc
        print rp[1:]
        # K1, K2, K3
        K1='C-%d'%(rp[1])
        K2='C-%d'%(rp[1])
        K3='C-%d'%(rp[1])
        K4='C-%d'%(rp[1])
        # K5, K6
        if rp[2]==0:
            K5='C-NC'
            K6='C-NC'
        elif rp[2]==1:
            K5='C-NO'
            K6='C-NO'
        else:
            K5=K6='invalid'
        for i in range(1,7):
            s=eval('K%d'%i)
            print "K%d: %s"%(i, s)
        return ans
    
    def on_sgSwitch_Direct_toggled(self, state):
        if state:
            print "Switch 1: direct"
            ans=self.ask('R1P4')
    def on_sgSwitch_LF_toggled(self, state):
        if state:
            print "Switch 1: LF"
            ans=self.ask('R1P1')
    def on_sgSwitch_HF_toggled(self, state):
        if state:
            print "Switch 1: HF"
            ans=self.ask('R1P2')
    def on_TxSwitch_GTEM_toggled(self, state):
        if state:
            print "Switch 2: GTEM"
            ans=self.ask('R2P1')
    def on_TxSwitch_Term_toggled(self, state):
        if state:
            print "Switch 2: Term"
            ans=self.ask('R2P0')
    def on_RxSwitch_GTEM_toggled(self, state):
        if state:
            print "Switch 3: GTEM"
            ans=self.ask('R3P0')
    def on_RxSwitch_Term_toggled(self, state):
        if state:
            print "Switch 3: TERM"
            ans=self.ask('R3P1')
    def on_RxSwitch_30M_toggled(self, state):
        if state:
            print "Switch 4: 30M"
            ans=self.ask('R4P0')
    def on_RxSwitch_3G_toggled(self, state):
        if state:
            print "Switch 4: 3G"
            ans=self.ask('R4P1')
        
def main():
    if not virtual:
        try:
            sw=visa.instrument('GPIB::4', term_chars = visa.LF)
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

