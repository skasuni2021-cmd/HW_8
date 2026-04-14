#region imports
import numpy as np
import PyQt5.QtWidgets as qtw
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from LeastSquares import LeastSquaresFit_Class
#endregion

#region class definitions
class Pump_Model():
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

        self.HeadCoefficients = np.array([])
        self.EfficiencyCoefficients = np.array([])

        self.LSFitHead = LeastSquaresFit_Class()
        self.LSFitEff = LeastSquaresFit_Class()


class Pump_Controller():
    def __init__(self):
        self.Model = Pump_Model()
        self.View = Pump_View()

    #region functions to modify data of the model
    def ImportFromFile(self, data):
        """
        Process the list of strings in data to build the pump model.
        :param data: lines from the pump data file
        """
        # Pump name is the first line
        self.Model.PumpName = data[0].strip()

        # data[2] is the units line (e.g., "gpm     ft       %")
        units_line = data[2].split()
        self.Model.FlowUnits = units_line[0]
        self.Model.HeadUnits = units_line[1]

        # Numeric data starts at line index 3
        self.SetData(data[3:])
        self.updateView()

    def SetData(self, data):
        '''
        Parse three columns of data (flow, head, efficiency) and build arrays.
        :param data: list of strings, each containing three numbers separated by spaces
        '''
        # Clear existing data
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData = np.array([])

        for line in data:
            if line.strip():  # skip empty lines
                cells = line.split()          # split on whitespace
                self.Model.FlowData = np.append(self.Model.FlowData, float(cells[0]))
                self.Model.HeadData = np.append(self.Model.HeadData, float(cells[1]))
                self.Model.EffData = np.append(self.Model.EffData, float(cells[2]))

        # Fit polynomials
        self.LSFit()

    def LSFit(self):
        '''Fit quadratic to Head data (degree 2) and cubic to Efficiency data (degree 3).'''
        self.Model.LSFitHead.x = self.Model.FlowData
        self.Model.LSFitHead.y = self.Model.HeadData
        self.Model.LSFitHead.LeastSquares(2)   # quadratic for head

        self.Model.LSFitEff.x = self.Model.FlowData
        self.Model.LSFitEff.y = self.Model.EffData
        self.Model.LSFitEff.LeastSquares(3)    # cubic for efficiency
    #endregion

    #region functions interacting with view
    def setViewWidgets(self, w):
        self.View.setViewWidgets(w)

    def updateView(self):
        self.View.updateView(self.Model)
    #endregion


class Pump_View():
    def __init__(self):
        """
        Placeholder widgets; they will be replaced when setViewWidgets is called.
        """
        self.LE_PumpName = qtw.QLineEdit()
        self.LE_FlowUnits = qtw.QLineEdit()
        self.LE_HeadUnits = qtw.QLineEdit()
        self.LE_HeadCoefs = qtw.QLineEdit()
        self.LE_EffCoefs = qtw.QLineEdit()
        self.ax = None
        self.canvas = None

    def updateView(self, Model):
        """
        Update all GUI widgets with the current model data.
        """
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        """
        Create the plot: head (primary y-axis) and efficiency (secondary y-axis) vs flow.
        """
        # Get fitted curves (quadratic for head, cubic for efficiency)
        head_x, head_y, head_R2 = Model.LSFitHead.GetPlotInfo(2, npoints=500)
        eff_x, eff_y, eff_R2 = Model.LSFitEff.GetPlotInfo(3, npoints=500)

        # Clear previous plot
        self.ax.clear()

        # Primary axis: Head
        self.ax.plot(head_x, head_y, 'b-', label=f'Head ({Model.HeadUnits})')
        self.ax.scatter(Model.FlowData, Model.HeadData, color='blue', marker='o', zorder=5)
        self.ax.set_xlabel(f'Flow ({Model.FlowUnits})')
        self.ax.set_ylabel(f'Head ({Model.HeadUnits})', color='blue')
        self.ax.tick_params(axis='y', labelcolor='blue')
        self.ax.grid(True, linestyle='--', alpha=0.7)

        # Secondary axis: Efficiency
        ax2 = self.ax.twinx()
        ax2.plot(eff_x, eff_y, 'r-', label=f'Efficiency (%)')
        ax2.scatter(Model.FlowData, Model.EffData, color='red', marker='s', zorder=5)
        ax2.set_ylabel('Efficiency (%)', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        # Title and legends
        self.ax.set_title(f'Pump Performance: {Model.PumpName}')
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax.legend(lines1 + lines2, labels1 + labels2, loc='best')

        # Redraw the canvas
        self.canvas.draw()

    def setViewWidgets(self, w):
        """
        w is a list: [LE_PumpName, LE_FlowUnits, LE_HeadUnits, LE_HeadCoefs, LE_EffCoefs, ax, canvas]
        """
        (self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits,
         self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas) = w
#endregion