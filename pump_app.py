#region imports
import sys
import os
from pathlib import Path

import PyQt5.QtWidgets as qtw
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pump import Ui_Form
from Pump_MVC import Pump_Controller
#endregion

#region class definitions
class PumpCurve_GUI_Class(Ui_Form, qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.AssignSignals()
        self.FilePath = os.getcwd()          # start in current directory
        self.FileName = ""

        # Create matplotlib canvas and axes
        self.canvas = FigureCanvasQTAgg(Figure(figsize=(5, 3), tight_layout=True, frameon=True))
        self.ax = self.canvas.figure.add_subplot()
        # Add canvas to the form (row 5, column 0, span 1 row, 4 columns)
        self.GL_Output.addWidget(self.canvas, 5, 0, 1, 4)

        self.myPump = Pump_Controller()
        self.setViewWidgets()

        self.show()

    def AssignSignals(self):
        self.PB_Exit.clicked.connect(self.Exit)
        self.CMD_Open.clicked.connect(self.ReadAndCalculate)

    def setViewWidgets(self):
        """
        Pass the GUI widgets to the controller so the view can update them.
        """
        w = [self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits,
             self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas]
        self.myPump.setViewWidgets(w)

    def ReadAndCalculate(self):
        """
        Open file dialog, read the selected file, and process the data.
        """
        if self.OpenFile():
            with open(self.FileName, 'r') as f:
                data = f.readlines()
            self.myPump.ImportFromFile(data)
            return True
        return False

    def OpenFile(self):
        """
        Show file open dialog, remember the directory, and store the file name.
        """
        fname = qtw.QFileDialog.getOpenFileName(
            self, "Open Pump Data File", self.FilePath,
            "Text files (*.txt);;All files (*.*)"
        )
        ok = len(fname[0]) > 0
        if ok:
            self.FileName = fname[0]
            self.FilePath = str(Path(fname[0]).parents[0]) + '/'
            self.TE_Filename.setText(self.FileName)
        return ok

    def Exit(self):
        qapp.exit()
#endregion

#region function definitions
def main():
    _ = PumpCurve_GUI_Class()
    qapp.exec_()
#endregion

#region function calls
if __name__ == "__main__":
    qapp = qtw.QApplication(sys.argv)
    main()
#endregion