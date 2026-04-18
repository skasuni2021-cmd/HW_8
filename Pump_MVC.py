#region imports
import numpy as np
import PyQt5.QtWidgets as qtw
#endregion

from LeastSquares import LeastSquaresFit_Class


#region class definitions
class Pump_Model:
    """
    This is the pump model. It just stores data.
    """
    def __init__(self):
        self.PumpName = ""
        self.FlowUnits = ""
        self.HeadUnits = ""

        self.FlowData = np.array([])
        self.HeadData = np.array([])
        self.EffData = np.array([])

        self.LSFitHead = LeastSquaresFit_Class()
        self.LSFitEff = LeastSquaresFit_Class()


class Pump_Controller:
    def __init__(self):
        self.Model = Pump_Model()
        self.View = Pump_View()

    def ImportFromFile(self, data):
        """
        This processes the list of strings in data to build the pump model
        """
        self.Model.PumpName = data[0].strip()

        # If line 2 is blank and line 3 has units, keep this:
        L = data[2].split()
        self.Model.FlowUnits = L[0].strip()
        self.Model.HeadUnits = L[1].strip()

        self.SetData(data[3:])
        self.updateView()

    def SetData(self, data):
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData = np.array([])

        for line in data:
            cells = line.split()
            if len(cells) >= 3:
                self.Model.FlowData = np.append(self.Model.FlowData, float(cells[0].strip()))
                self.Model.HeadData = np.append(self.Model.HeadData, float(cells[1].strip()))
                self.Model.EffData = np.append(self.Model.EffData, float(cells[2].strip()))

        self.LSFit()

    def LSFit(self):
        self.Model.LSFitHead.x = self.Model.FlowData
        self.Model.LSFitHead.y = self.Model.HeadData
        self.Model.LSFitHead.LeastSquares(3)

        self.Model.LSFitEff.x = self.Model.FlowData
        self.Model.LSFitEff.y = self.Model.EffData
        self.Model.LSFitEff.LeastSquares(3)

    def setViewWidgets(self, w):
        self.View.setViewWidgets(w)

    def updateView(self):
        self.View.updateView(self.Model)


class Pump_View:
    def __init__(self):
        self.LE_PumpName = qtw.QLineEdit()
        self.LE_FlowUnits = qtw.QLineEdit()
        self.LE_HeadUnits = qtw.QLineEdit()
        self.LE_HeadCoefs = qtw.QLineEdit()
        self.LE_EffCoefs = qtw.QLineEdit()
        self.ax = None
        self.canvas = None

    def updateView(self, Model):
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        headx, heady, headRSq = Model.LSFitHead.GetPlotInfo(3, npoints=500)
        effx, effy, effRSq = Model.LSFitEff.GetPlotInfo(3, npoints=500)

        axes = self.ax
        axes.clear()

        axes.plot(Model.FlowData, Model.HeadData, 'bo', label='Head Data')
        axes.plot(headx, heady, 'b-', label=f'Head Fit (R²={headRSq:.4f})')

        axes.plot(Model.FlowData, Model.EffData, 'ro', label='Efficiency Data')
        axes.plot(effx, effy, 'r-', label=f'Efficiency Fit (R²={effRSq:.4f})')

        axes.set_xlabel(Model.FlowUnits)
        axes.set_ylabel(f'Head ({Model.HeadUnits}) / Efficiency')
        axes.set_title(Model.PumpName)
        axes.legend()
        axes.grid(True)

        self.canvas.draw()

    def setViewWidgets(self, w):
        self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits, self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas = w
#endregion
