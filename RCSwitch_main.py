#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
try:
    import pyvisa
    virtual=False
except ImportError:
    virtual=True

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QTimer

# from PySide6 import QtCore, QtGui, QtWidgets
from RCSwitch import Ui_ReverbChamberRelaisController


class SWController(QMainWindow):
    def __init__(self, sw):
        super(SWController, self).__init__()
        self.sw = sw
        # 00: sig -> 40 dB -> term     usefull; safe
        # 01: sig -> TX LF             useful; direkt LF
        # 02: sig -> TX HF             usefull; direkt HF
        # 10: sig -> LF amp -> term; LF PMs    usefull; LF AMP-Test
        # 11: sig -> LF amp -> LxAnt; LF PMs    usefull; LF operation
        # 12: sig -> LF amp -> HfAnt, LF PMs    usefull, LFAmp,HFAnt operation
        # 20: sig -> HF amp -> term; HF PMs    usefull; HF AMP-Test
        # 21: sig -> HF amp -> LfAnt, HF PMs    usefull, HFAmp,LFAnt operation
        # 22: sig -> HF amp -> HfAnt, HF PMs   usefull, HF operation
        self._states12 = {'LFAMP':
                              {'LFANT': 'R1P1R2P1',
                               'HFANT': 'R1P1R2P2',
                               'TERM': 'R1P1R2P0'
                               },
                          'HFAMP':
                              {'LFANT': 'R1P2R2P1',
                                'HFANT': 'R1P2R2P2',
                               'TERM': 'R1P2R2P0'
                               },
                          'DIRECT':
                              {'LFANT': 'R1P0R2P1',
                               'HFANT': 'R1P0R2P2',
                               'TERM': 'R1P0R2P0'
                               },
                          'safe': 'R1P0R2P0'
                          }
        # LF:
        #     0dB:
        #            PM:  1010
        #            REC: 1110
        #    20dB:
        #            PM:  1100
        #            REC: 1000
        # HF:
        #     0dB:
        #            PM:  0001
        #            REC: 0101
        #    20dB:
        #            PM:  0111
        #            REC: 0011
        self._states3456 = {'LF': {'0dB': {'PM':    'R3P1R4P0R5P1R6P0',
                                           'REC':   'R3P1R4P1R5P1R6P0',
                                           'safe':  'R3P0R4P0R5P0R6P0'},
                                   '20dB': {'PM':   'R3P1R4P1R5P0R6P0',
                                            'REC':  'R3P1R4P0R5P0R6P0',
                                            'safe': 'R3P0R4P0R5P0R6P0'}
                                   },
                            'HF': {'0dB': {'PM':    'R3P0R4P0R5P0R6P1',
                                           'REC':   'R3P0R4P1R5P0R6P1',
                                           'safe':  'R3P0R4P0R5P0R6P0'},
                                   '20dB': {'PM':   'R3P0R4P1R5P1R6P1',
                                            'REC':  'R3P0R4P0R5P1R6P1',
                                            'safe': 'R3P0R4P0R5P0R6P0'}
                                   },
                            'safe': 'R3P0R4P0R5P0R6P0'
                            }
        # SG direkt in die Termination
        # PM2 und REC an 50 Ohm (REC ueber 20 dB)
        # Alle Antennen: open
        # Fwd und Rev PM: undefiniert
        self._safe = self._states12['safe'] + self._states3456['safe']      # 'R1P0R2P0R3P0R4P0R5P0R6P0'
        # print sw
        # save settings
        self.query(self._safe)
        self.query('R3P1R4P1')   # LFrx, Amp, PM
        self.RxLF = True
        self.RxAtt = True
        self.RxPM = True
        # self monitor is set to True during do_update (QTimer loop)
        # so we can handle, when another program changed relais states
        self.monitor = False
        self.setStyleSheet ("""QFrame {color: red;}
                                QFrame:disabled {color: black;}""")
        self.ui = Ui_ReverbChamberRelaisController()
        self.ui.setupUi(self)
        self.ctimer = QTimer()
        self.ctimer.start(500)
        #QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.doUpdate)
        self.ctimer.timeout.connect(self.doUpdate)

        self.ui.sgSwitch_LF.toggled.connect(self.on_sgSwitch_LF_toggled)
        self.ui.sgSwitch_HF.toggled.connect(self.on_sgSwitch_HF_toggled)
        self.ui.sgSwitch_Direct.toggled.connect(self.on_sgSwitch_Direct_toggled)

        self.ui.TxSwitch_LF.toggled.connect(self.on_TxSwitch_LF_toggled)
        self.ui.TxSwitch_HF.toggled.connect(self.on_TxSwitch_HF_toggled)
        self.ui.TxSwitch_Term.toggled.connect(self.on_TxSwitch_Term_toggled)

        self.ui.RxSwitch_LF.toggled.connect(self.on_RxSwitch_LF_toggled)
        self.ui.RxSwitch_HF.toggled.connect(self.on_RxSwitch_HF_toggled)

        self.ui.AttSwitch_On.clicked.connect(self.on_AttSwitch_On_clicked)
        self.ui.AttSwitch_Off.clicked.connect(self.on_AttSwitch_Off_clicked)

        self.ui.RxSwitch_Rec.toggled.connect(self.on_RxSwitch_Rec_toggled)
        self.ui.RxSwitch_PM.toggled.connect(self.on_RxSwitch_PM_toggled)

    def doUpdate(self):
        # print 'Pling'
        s = self.sw.query('')
        s3456 = s[11::4]
        self.monitor = True
        #print s
        rdict = dict(zip(map(int, s[1::4]), map(int, s[3::4])))   # keys: relais, value: position
        # 0000: PM2 -> 50 Ohm; REC -> 20 dB -> 50 Ohm          usefull, safe
        # 1000: Pm2 -> 50 Ohm, Rec -> 20 dB -> Rx LF           usefull, LF -> 20dB -> REC
        # 0100: PM2 -> 20 dB -> 50 Ohm, REC -> 50 Ohm          usefull, safe
        # 1100: PM2 -> 20 dB -> Rx LF, REc -> 50 Ohm           usefull, LF -> 20 dB -> PM2
        # 0010: PM2 -> 50 Ohm, REC -> 20 dB -> 50 Ohm  = 0000  usefull, safe
        # 0110: PM2 -> 20 dB -> 50 Ohm, REC -> 50 Ohm  = 0100  usefull, safe
        # 1010: PM2 -> Rx LF; REC -> 20 dB -> 50 Ohm           usefull, LF -> 0dB -> PM2
        # 1110: PM2 -> 20 dB -> 50 Ohm, REC -> RX LF           usefull, LF -> 0dB -> REC
        # 0001: PM2 -> Rx HF; REC -> 20 dB -> 50 Ohm           usefull, HF -> 0dB -> PM2
        # 1001: Pm2 -> Rx HF, Rec -> 20 dB -> Rx LF            don't use; PM and REC both exposed
        # 0101: PM2 -> 20 dB -> 50 Ohm, REC -> Rx HF           usefull; HF -> 0dB -> REC
        # 1101: PM2 -> 20 dB -> rx LF, REC -> Rx HF            don't use; PM and REC both exposed
        # 0011: PM2 -> 50 Ohm , REC -> 20 dB -> Rx HF          usefull; HF -> 20 dB -> REC
        # 0111: PM2 -> 20 dB -> rx HF, REC -> 50 Ohm           usefull; HF -> 20 dB -> PM2
        # 1011: PM2 -> Rx LF; REC -> 20 dB -> Rx HF            don't use, PM and REC both exposed
        # 1111: PM2 -> 20 dB -> RX HF, REC -> RX LF            don't use, PM and REC both exposed
        # LF:
        #     0dB:
        #            PM:  1010
        #            REC: 1110
        #    20dB:
        #            PM:  1100
        #            REC: 1000
        # HF:
        #     0dB:
        #            PM:  0001
        #            REC: 0101
        #    20dB:
        #            PM:  0111
        #            REC: 0011
        if rdict[1] == 0:  # direct
            self.ui.sgSwitch_Direct.click()
        elif rdict[1] == 1:  # LF
            self.ui.sgSwitch_LF.click()
        elif rdict[1] == 2:  # HF
            self.ui.sgSwitch_HF.click()

        if rdict[2] == 0:  # TERM
            self.ui.TxSwitch_Term.click()
        elif rdict[2] == 1:  # LogPer
            self.ui.TxSwitch_LF.click()
        elif rdict[2] == 2:  # Horn
            self.ui.TxSwitch_HF.click()


        # LF:
        #     0dB:
        #            PM:  1010
        #            REC: 1110
        #    20dB:
        #            PM:  1100
        #            REC: 1000
        # HF:
        #     0dB:
        #            PM:  0001
        #            REC: 0101
        #    20dB:
        #            PM:  0111
        #            REC: 0011
        if s3456 == '0111':
            self.ui.RxSwitch_HF.click()
            self.ui.RxSwitch_PM.click()
            self.ui.AttSwitch_On.click()
        elif s3456 == '0001':
            self.ui.RxSwitch_HF.click()
            self.ui.RxSwitch_PM.click()
            self.ui.AttSwitch_Off.click()
        elif s3456 == '0011':
            self.ui.RxSwitch_HF.click()
            self.ui.RxSwitch_Rec.click()
            self.ui.AttSwitch_On.click()
        elif s3456 == '0101':
            self.ui.RxSwitch_HF.click()
            self.ui.RxSwitch_Rec.click()
            self.ui.AttSwitch_Off.click()
        elif s3456 == '0000':
            self.ui.RxSwitch_HF.click()
            self.ui.RxSwitch_Rec.click()
            self.ui.AttSwitch_On.click()
        elif s3456 == '1100':
            self.ui.RxSwitch_LF.click()
            self.ui.RxSwitch_PM.click()
            self.ui.AttSwitch_On.click()
        elif s3456 == '1010':
            self.ui.RxSwitch_LF.click()
            self.ui.RxSwitch_PM.click()
            self.ui.AttSwitch_Off.click()
        elif s3456 == '1000':
            self.ui.RxSwitch_LF.click()
            self.ui.RxSwitch_Rec.click()
            self.ui.AttSwitch_On.click()
        elif s3456 == '1110':
            self.ui.RxSwitch_LF.click()
            self.ui.RxSwitch_Rec.click()
            self.ui.AttSwitch_Off.click()
        elif s3456 == '0000':
            self.ui.RxSwitch_LF.click()
            self.ui.RxSwitch_Rec.click()
            self.ui.AttSwitch_On.click()
        else:
            print("'invisible' switch: %r"%rdict)
        self.monitor = False

    def query(self, cmd):
        if not self.sw:
            return None
        ans=self.sw.query(cmd)
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
            ans=self.query('R1P0')

    def on_sgSwitch_LF_toggled(self, state):
        if state:
            #print "Switch 1: LF"
            ans=self.query('R1P1')

    def on_sgSwitch_HF_toggled(self, state):
        if state:
            #print "Switch 1: HF"
            ans=self.query('R1P2')

    def on_TxSwitch_LF_toggled(self, state):
        if state:
            #print "Switch 2: LF"
            ans=self.query('R2P1')

    def on_TxSwitch_HF_toggled(self, state):
        if state:
            #print "Switch 2: HF"
            ans=self.query('R2P2')

    def on_TxSwitch_Term_toggled(self, state):
        if state:
            #print "Switch 2: Term"
            ans=self.query('R2P0')

    def on_RxSwitch_LF_toggled(self, state):
        self.RxLF = state
        # if state:
            #print "Switch 3: LF"
        self._rx_logic()

    def on_RxSwitch_HF_toggled(self, state):
        self.RxLF = not(state)
        # if state:
            #print "Switch 3: HF"
        self._rx_logic()

    def on_AttSwitch_Off_clicked(self, state):
        if not self.monitor:  # we triggerd the change
            if state and self.RxLF: # this may be dangerous
                message = QMessageBox(self)
                message.setStyleSheet('color: black')
                message.setText("""
You are going to remove the attenuation from the
RX path at low frequencies.

This may damage your power meter or receiver!

Do you really want to remove the attenuation?
                                """)
                message.setWindowTitle('Warning')
                message.setIcon(QMessageBox.Icon.Question)
                message.addButton('No', QMessageBox.ButtonRole.AcceptRole)
                message.addButton('Yes', QMessageBox.ButtonRole.RejectRole)
                message.exec()
                response = message.clickedButton().text()
                if response != 'Yes':
                    self.ui.AttSwitch_On.toggle()  # switch back
                    return
        self.RxAtt = not state
        self.ui.conn_amp_direct_20.setEnabled(not state)
        self.ui.conn_amp_direct_21.setEnabled(state)
        self.ui.AttSwitch_On.setChecked(not state)

        self._rx_logic()

    def on_AttSwitch_On_clicked(self, state):
        self.RxAtt = state
        self.ui.conn_amp_direct_20.setEnabled(state)
        self.ui.conn_amp_direct_21.setEnabled(not state)
        self.ui.AttSwitch_Off.setChecked(not state)
        self._rx_logic()

    def on_RxSwitch_PM_toggled(self, state):
        self.RxPM = state
        #if state:
            #print "Switch 5: Rx PM"
        self._rx_logic()

    def on_RxSwitch_Rec_toggled(self, state):
        self.RxPM = not(state)
        #if state:
            #print "Switch 5: Rx Rec"
        self._rx_logic()
        
    def _rx_logic(self):
        lf = self.RxLF
        att = self.RxAtt
        pm = self.RxPM
        if lf:
            if att:
                if pm:
                    cmd = self._states3456['LF']['20dB']['PM']   # 'R3P1R4P1R5P0R6P0'
                else:
                    cmd = self._states3456['LF']['20dB']['REC']   # 'R3P1R4P0R5P0R6P0'
            else:
                if pm:
                    cmd = self._states3456['LF']['0dB']['PM']   # 'R3P1R4P0R5P1R6P0'
                else:
                    cmd = self._states3456['LF']['0dB']['REC']   # 'R3P1R4P1R5P1R6P0'
        else:
            if att:
                if pm:
                    cmd = self._states3456['HF']['20dB']['PM']   # 'R3P0R4P1R5P1R6P1'
                else:
                    cmd = self._states3456['HF']['20dB']['REC']   # 'R3P0R4P0R5P1R6P1'
            else:
                if pm:
                    cmd = self._states3456['HF']['0dB']['PM']   # 'R3P0R4P0R5P0R6P1'
                else:
                    cmd = self._states3456['HF']['0dB']['REC']   # 'R3P0R4P1R5P0R6P1'
        if not self.monitor:
            self.query(cmd)
        
        
def main():
    if not virtual:
        try:
            rm=pyvisa.ResourceManager('@py')
            sw=rm.open_resource('GPIB::2')
            sw.read_termination = '\n'
            sw.write_termination = '\n'
        except:
            sw = None
    else:
        sw = None

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = SWController(sw)
    window.show()
    sys.exit(app.exec())
        

if __name__ == "__main__":
    main()

