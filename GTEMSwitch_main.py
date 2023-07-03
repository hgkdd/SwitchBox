# -*- coding: utf-8 -*-
import sys

try:
    import pyvisa

    virtual = False
except ImportError:
    virtual = True

from PyQt5 import QtCore, QtWidgets
from GTEMSwitch import Ui_GTEMRelaisController as ui


class SWController(QtWidgets.QMainWindow):
    def __init__(self, sw):
        self.sw = sw
        # print sw
        # save settings
        self.query('R1P4R2P0R3P1R4P0')
        QtWidgets.QMainWindow.__init__(self)
        self.ui = ui()
        self.setStyleSheet("""QFrame {color: red;}
                                QFrame:disabled {color: black;}""")
        self.ui.setupUi(self)
        self.ctimer = QtCore.QTimer()
        self.ctimer.start(500)
        # QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.doUpdate)
        self.ctimer.timeout.connect(self.doUpdate)

    def doUpdate(self):
        # print 'Pling'
        s = self.sw.query('')
        print(s)
        rdict = dict(zip(map(int, s[1::4]), map(int, s[3::4])))  # keys: relais, value: position

        if rdict[1] == 1:  # LF
            self.ui.sgSwitch_LF.click()
        elif rdict[1] == 2:  # HF
            self.ui.sgSwitch_HF.click()
        elif rdict[1] == 4:  # HF
            self.ui.sgSwitch_Direct.click()

        if rdict[2] == 0:  # TERM
            self.ui.TxSwitch_Term.click()
        elif rdict[2] == 1:  # GTEM
            self.ui.TxSwitch_GTEM.click()

        if rdict[3] == 0:  # GTEM
            self.ui.RxSwitch_GTEM.click()
        elif rdict[3] == 1:  # TERM
            self.ui.RxSwitch_Term.click()

        if rdict[4] == 0:  # 30M
            self.ui.RxSwitch_30M.click()
        elif rdict[4] == 1:  # 3G
            self.ui.RxSwitch_3G.click()

    def query(self, cmd):
        if not self.sw:
            return None
        ans = self.sw.query(cmd)
        # print "CMD: %s\nANS: %s"%(cmd, ans)
        rp = [int(ans[4 * i + 3:4 * i + 4]) for i in range(4)]
        rp.insert(0, None)  # rp[1]=relais_position of R1 etc
        # print rp[1:]
        # K1, K2, K3
        K1 = 'C-%d' % (rp[1])
        K2 = 'C-%d' % (rp[1])
        K3 = 'C-%d' % (rp[1])
        K4 = 'C-%d' % (rp[1])
        # K5, K6
        if rp[2] == 0:
            K5 = 'C-NC'
            K6 = 'C-NC'
        elif rp[2] == 1:
            K5 = 'C-NO'
            K6 = 'C-NO'
        else:
            K5 = K6 = 'invalid'
        for i in range(1, 7):
            s = eval('K%d' % i)
            # print "K%d: %s"%(i, s)
        return ans

    def on_sgSwitch_Direct_toggled(self, state):
        if state:
            # print "Switch 1: direct"
            ans = self.query('R1P4')

    def on_sgSwitch_LF_toggled(self, state):
        if state:
            # print "Switch 1: LF"
            ans = self.query('R1P1')

    def on_sgSwitch_HF_toggled(self, state):
        if state:
            # print "Switch 1: HF"
            ans = self.query('R1P2')

    def on_TxSwitch_GTEM_toggled(self, state):
        if state:
            # print "Switch 2: GTEM"
            self.ui.RxSwitch_Term.click()
            ans = self.query('R2P1')

    def on_TxSwitch_Term_toggled(self, state):
        if state:
            # print "Switch 2: Term"
            ans = self.query('R2P0')

    def on_RxSwitch_GTEM_toggled(self, state):
        if state:
            # print "Switch 3: GTEM"
            self.ui.TxSwitch_Term.click()
            ans = self.query('R3P0')

    def on_RxSwitch_Term_toggled(self, state):
        if state:
            # print "Switch 3: TERM"
            ans = self.query('R3P1')

    def on_RxSwitch_30M_toggled(self, state):
        if state:
            # print "Switch 4: 30M"
            ans = self.query('R4P0')

    def on_RxSwitch_3G_toggled(self, state):
        if state:
            # print "Switch 4: 3G"
            ans = self.query('R4P1')


def main():
    if not virtual:
        try:
            rm = pyvisa.ResourceManager()
            sw = rm.open_resource('GPIB::8')
            sw.read_termination = '\n'
            sw.write_termination = '\n'
        except:
            sw = None
    else:
        sw = None

    app = QtWidgets.QApplication(sys.argv)
    window = SWController(sw)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
