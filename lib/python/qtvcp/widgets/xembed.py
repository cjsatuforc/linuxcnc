import sys
import os
import subprocess

from PyQt5.QtCore import QSize, QEvent, pyqtProperty
from PyQt5.QtGui import QWindow, QResizeEvent
from PyQt5.QtWidgets import QWidget

from qtvcp.widgets.widget_baseclass import _HalWidgetBase
from qtvcp.lib import xembed

class XEmbeddable(QWidget):
    def __init__(self, parent=None):
        super(XEmbeddable, self).__init__(parent)

    def embed(self, command):
        try:
            self.external_id = self.launch_xid(command)
            window = QWindow.fromWinId(self.external_id)
            self.container = QWidget.createWindowContainer(window, self)
            self.show()
            return True
        except  Exception,e:
            print 'Error Embedding program: ',command
            print e
            return False

    def event(self, event):
        if event.type() ==  QEvent.Resize:
            w = QResizeEvent.size(event)
            try:
                self.container.resize(w.width(), w.height())
            except:
                pass
        return True

    def launch_xid(self,cmd):
        c = cmd.split()
        #print c
        self.ob = subprocess.Popen(c,stdin = subprocess.PIPE,
                                   stdout = subprocess.PIPE)
        sid = self.ob.stdout.readline()
        print 'XID:',sid
        return int(sid)

class XEmbed(XEmbeddable, _HalWidgetBase):
    def __init__(self, parent=None):
        super(XEmbed, self).__init__(parent)
        self.command = None

    def _hal_init(self):
        # send embedded program our X window id so it can forward events to us.
        wid = int(self.QTVCP_INSTANCE_.winId())
        print 'parent wind id', wid
        os.environ['QTVCP_FORWARD_EVENTS_TO'] = str(wid)
        result = self.embed(self.command)
        if result:
            self.x11mess = xembed.X11ClientMessage(self.external_id)


    def send_x11_message(self,):
        self.x11mess.send_client_message()

    def set_command(self, data):
        self.command = data
    def get_command(self):
        return self.command
    def reset_command(self):
        self.command = None

    command_string = pyqtProperty(str, get_command, set_command, reset_command)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ex = XEmbed()
    ex.embed('halcmd loadusr gladevcp --xid  ../../gladevcp/offsetpage.glade')
    ex.show()
    ex.setWindowTitle('embed')
    sys.exit(app.exec_())
