'''
AutoTeach software
Developed by Yehoram YosuBash and Stacey McKinney
Modified by Sarah Hoover
The goal of this software is to automatically teach the wafer engine
robot the locations of the different stations in space and thus
calibrate these locations to ensure repeatability, consistency, and
safety while minimizing human-error and subjectivity

Z_Teach section of this code:
Python script which perfroms the following:
 1. Establish connection to a controller.
 2. collects and stores time stamped paramter data for all stations
 3. Allow manual movement to the teach location at load ports
 4. Perform Auto-Teach of Z position using laser fixture
'''

import clr
import time
import math
import datetime

# from Variables import * # change this later??

#ctcPath = "D:\\BAI\\API.2.6.0.6_AutoTeach_Test\\CTC"
ctcPath = "C:\\BAI\\Autoteach\\CTC\\Scripts\\EFEM.Startup.py"
# execfile( "C:\\BAI\\API.2.6.0.6_AutoTeachTest\\autoteachtest\\CTC\\Scripts\\EFEM.Startup.py" )
# execfile("D:\\BAI\\API.2.6.0.6_AutoTeach_Test\\CTC\\Scripts\\EFEM.Startup.py")
# execfile( "C:\\BAI\\Api.2.6.0.100 Test 276\\CTC\\Scripts\\EFEM.Startup.py" )
#execfile("C:\\BAI\\Api.2.6.0.100\\CTC\\Scripts\\EFEM.Startup.py")
execfile("C:\\BAI\\Autoteach\\CTC\\Scripts\\EFEM.Startup.py")

clr.AddReference("BAI.ServiceLib.dll")
from System.Globalization import *
from System.IO import *

from BAI.General import *
from BAI.Systems.Common import *
from BAI.Systems.Data.Motion import *
from BAI.Systems.Modules.EFEM import *
from BAI.Systems.Devices.LoadPort import *
from BAI.Systems.Devices.CarrierId import *
from BAI.Systems.Devices.LightTower import *
from BAI.Systems.Devices.WaferAligner import *
from BAI.Systems.Devices.WaferEngine import *
from BAI.Systems.Devices.WaferIdReader import *
from BAI.Systems.Common.Exceptions import *
from BAI.Systems.Common.Controls import *
from BAI.Systems.Common.Carriers import *
from BAI.Systems.Common.Carriers.Controls import *
from BAI.Systems.Devices import *
from BAI.Systems.Data.Motion import *
from BAI.Systems.Modules import *
from BAI.Maint.Devices import *
from BAI.Maint.Modules import *
from BAI.Maint.Devices.Loadport import *
from BAI.Maint.Devices.WaferAligner import *
from BAI.Maint.Devices.WaferEngine import *
from BAI.Maint.HwComp.Motion.PLCOpen import *
from System.IO import *
from System.Globalization import *
from BAI.Service.Common import *
from BAI.Service.Common.Persist import *
from BAI.Service.Devices import *
from BAI.Service.Devices.Robot import *
from BAI.Service.Devices.WaferEngine import *
from BAI.Service.Modules.EFEM import *
from BAI.Systems.Devices.WaferEngine.PathFinding import MathHelper
from BAI.Infras.General import DirectoryUtil
from BAI.Maint.HwComp.Motion.PLCOpen import *
from System.Reflection import *
from System import *
from System.Collections.Generic import Dictionary
import sys
import BAI

clr.AddReference("System.Core")
from System.Reflection import *
from System import *
import time
import math

efsv = EfemServiceProxy("EFEM", "CTC")
cal = ServiceType.Calib
we = efsv.GetWaferEngineService()
ef = EfemRemoteProxy("EFEM", "CTC")
io = BAI.Maint.HwComm.IobComm.IobCommMaintRemoteProxy("EFEM.IobComm", "CTC")
io.DioWriteBit(0, 0, 0)
# EE = ""
ee1 = ""
ee2 = ""
#teachstn = ""
teachslot = "Slot12"
numLPs = 0
targetOffset = 0
sensorOffset = 0
MinXA = 0
MaxXA = 0
MinXB = 0
MaxXB = 0
MinXC = 0
MaxXC = 0
MinXD = 0
MaxXD = 0
MinZ1 = 0
MaxZ1 = 0
MinZ2 = 0
MaxZ2 = 0
MinT = 0
MaxT = 0
MinEEGet = 0
MaxEEGet = 0
MinEEPut = 0
MaxEEPut = 0
TopDive = 0
BottomDive = 0
PlusZOff = 0
MinusZOff = 0
getOffset = 0
slotNumber = 0
fstep = 0
rstep = 0
stnA = 0
stnB = 0
stnC = 0
stnD = 0
isAEG = False
alignerLocation = ""

class SizeError(Exception):
    pass

def ReadDataFromFile(fileName, numLP):
    global MinXA, MaxXA, MinXB, MaxXB, MinXC, MaxXC, MinXD, MaxXD
    global MinZ1, MaxZ1, MinZ2, MaxZ2, MinT, MaxT, MinEEGet, MaxEEGet, MinEEPut, MaxEEPut
    global TopDive, BottomDive, PlusZOff, MinusZOff, getOffset
    global slotNumber, fstep, rstep, stnA, stnB, stnC, stnD
    global targetOffset, sensorOffset
    # opens a file in read-only mode
    file = open(fileName, 'r')

    # fileData = file.readlines() # fileData is a list where each item is a line in the file

    # clear the first few lines
    for i in range(0, 5, 1):
        file.readline()

    # read in the offsets
    targetOffset = int(file.readline().split(",")[1])
    sensorOffset = int(file.readline().split(",")[1])

    # clear lines
    for i in range(0, 2, 1):
        file.readline()

    # there has to be a more efficient/elegant way to do this
    # brainstorm and come back
    try:
        # READ IN THE LOCATIONS OF THE LOADPORTS
        arr = file.readline().split(",")
        if numLP == 2:
            MinXB = int(arr[1])
            MaxXB = int(arr[2])
        elif numLP == 3:
            MinXC = int(arr[1])
            MaxXC = int(arr[2])
        elif numLP == 4:
            MinXD = int(arr[1])
            MaxXD = int(arr[2])
        # second line
        arr = file.readline().split(",")
        if numLP == 2:
            MinXA = int(arr[1])
            MaxXA = int(arr[2])
        elif numLP == 3:
            MinXB = int(arr[1])
            MaxXB = int(arr[2])
        elif numLP == 4:
            MinXC = int(arr[1])
            MaxXC = int(arr[2])
        # third line
        arr = file.readline().split(",")
        if numLP == 3:
            MinXA = int(arr[1])
            MaxXA = int(arr[2])
        elif numLP == 4:
            MinXB = int(arr[1])
            MaxXB = int(arr[2])
        # fourth line
        arr = file.readline().split(",")
        if numLP == 4:
            MinXA = arr[1]
            MaxXA = arr[2]
        # READ IN Z, THETA, AND EE LOCATIONS
        arr = file.readline().split(",")
        MinZ1 = int(arr[1])
        MaxZ1 = int(arr[2])
        if MinZ1 >= MaxZ1:
            raise SizeError(arr[0])
        arr = file.readline().split(",")
        MinZ2 = int(arr[1])
        MaxZ2 = int(arr[2])
        if MinZ2 >= MaxZ2:
            raise SizeError(arr[0])
        arr = file.readline().split(",")
        MinT = int(arr[1])
        MaxT = int(arr[2])
        if MinT >= MaxT:
            raise SizeError(arr[0])
        arr = file.readline().split(",")
        MinEEGet = int(arr[1])
        MaxEEGet = int(arr[2])
        if MinEEGet >= MaxEEGet:
            raise SizeError(arr[0])
        arr = file.readline().split(",")
        MinEEPut = int(arr[1])
        MaxEEPut = int(arr[2])
        if MinEEPut >= MaxEEPut:
            raise SizeError(arr[0])
    except IndexError:
        print("There is data missing from the file")
        print("Please make sure all data is entered correctly")
    except ValueError:
        print("There is unreadable data found in the file")
        print("Please make sure all data is entered correctly")
    except SizeError:
        print("Ensure maximum value is larger than minimum value for" + arr[0].ToString())
    except:
        print("An error occured while obtaining data from file")
        print("Please make sure all data is entered correctly")

    file.readline()
    file.readline()
    try:
        # READ IN OFFSET PARAMTERS
        arr = file.readline().split(",")
        TopDive = float(arr[1])  # this should only be applied to AEG
        arr = file.readline().split(",")
        BottomDive = float(arr[1])  # this should only be applied to AEG
        arr = file.readline().split(",")
        PlusZOff = float(arr[1])
        arr = file.readline().split(",")
        MinusZOff = float(arr[1])
        arr = file.readline().split(",")
        getOffset = float(arr[1])  # this should only be applied to AEG
        # if not using AEG, change occurs later in code

        file.readline()
        file.readline()

        # READ IN TEACH PARAMETERS
        arr = file.readline().split(",")
        slotNumber = int(arr[1])
        arr = file.readline().split(",")
        fstep = float(arr[1])
        arr = file.readline().split(",")
        rstep = float(arr[1])

        file.readline()
        file.readline()

        # READ IN THE STATION NAMES
        arr = file.readline().split(",")
        stnA = arr[1]
        arr = file.readline().split(",")
        stnB = arr[1]
        arr = file.readline().split(",")
        stnC = arr[1]
        arr = file.readline().split(",")
        stnD = arr[1]

    except IndexError:
        print("There is data missing from the file")
        print("Please make sure all data is entered correctly")
    except ValueError:
        print("There is unreadable data found in the file")
        print("Please make sure all data is entered correctly")
    except:
        print("An error occured while obtaining data from file")
        print("Please make sure all data is entered correctly")

    file.readline()
    file.readline()
    print("All data has been read into the variables")
    file.close()


#	path = "C:\\BAI\\EFEM_TeachData_" + now + ".xml"
#	path = "C:\\ASML\\Yieldstar\\Bin\\CTC\\EFEM_TeachData_" + now + ".xml"
def ReadPrevTeach():
    from datetime import datetime, date, time
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    message = "Saving Station Teach Data"
    path = "C:\\BAI\\AutoTeach\\EFEM_TeachData_" + now + ".xml"
    efsv.LoadStationDataFromDisk(cal)
    ees = we.GetEndEffecters(cal)
    newFile = StreamWriter(path, False);
    newFile.WriteLine("<TeachData Module=\"EFEM\">")
    for ee in ees:
        if (ee == "EE1" or ee == "EE2"):
            newFile.WriteLine("<DataOwner Name=\"" + ee + "\">")
            stations = we.GetStationNames(cal, ee)
            for s in stations:
                # print ee + " station " + s
                data = we.GetStationData(cal, ee, s)
                newFile.WriteLine(data.ToXmlString(CultureInfo.InvariantCulture))
        newFile.WriteLine("</DataOwner>")
    newFile.WriteLine("</TeachData>")
    newFile.Flush()
    newFile.Close()
    message = "Teach data for all stations printed to " + "\n" + path


# print (message)

class TestForm(Form):
    def __init__(self):
        global ee1, ee2, alignerLocation
        self.Text = "System Configuration"

        self.saveDataBox = CheckBox()
        self.saveDataBox.Text = "Save Current Teach Locations"
        self.saveDataBox.Location = Point(50, 50)
        self.saveDataBox.Enabled = True
        self.saveDataBox.CheckedChanged += self.saveDataBoxChanged

        button = Button()
        button.Text = "Start"
        button.Location = Point(10, 215)
        button.DialogResult = DialogResult.OK
        button.Click += self.buttonPressed

        button2 = Button()
        button2.Text = "Cancel"
        button2.Location = Point(100, 215)
        button2.DialogResult = DialogResult.Cancel

        numberLPList = ["2", "3", "4"]
        self.lpDropDown = ComboBox()
        for item in numberLPList:
            self.lpDropDown.Items.Add(item)
        self.lpDropDown.Text = "Number of Load Ports"
        self.lpDropDown.Enabled = True
        self.lpDropDown.Location = Point(10, 30)
        self.lpDropDown.TextChanged += self.lpDDChanged

        EETypes = ["Vacuum", "Passive", "Active Edge Grip", "Null"]  # TODO should I add film frame
        self.EEDropDown1 = ComboBox()
        for item in EETypes:
            self.EEDropDown1.Items.Add(item)
        self.EEDropDown1.Text = "EE1 Type"
        self.EEDropDown1.Enabled = True
        self.EEDropDown1.Location = Point(155, 30)
        self.EEDropDown1.TextChanged += self.ee1DDChanged

        self.EEDropDown2 = ComboBox()
        for item in EETypes:
            self.EEDropDown2.Items.Add(item)
        self.EEDropDown2.Text = "EE2 Type"
        self.EEDropDown2.Enabled = True
        self.EEDropDown2.Location = Point(155, 60)
        self.EEDropDown2.TextChanged += self.ee2DDChanged

        self.AlignerLocDropDown = ComboBox()
        self.AlignerLocDropDown.Text = "Aligner Location"
        self.AlignerLocDropDown.Enabled = False
        self.AlignerLocDropDown.Location = Point(10, 60)
        self.AlignerLocDropDown.TextChanged += self.alDDChanged

        self.Controls.Add(button)
        self.Controls.Add(button2)
        self.Controls.Add(self.lpDropDown)
        self.Controls.Add(self.EEDropDown1)
        self.Controls.Add(self.EEDropDown2)
        self.Controls.Add(self.AlignerLocDropDown)

        self.saveData = self.saveDataBox.Checked
        # numLPs = self.lpDropDown.Text
        ee1 = self.EEDropDown1.Text
        if ee1 == "Active Edge Grip":
            ee1 == "AEG"
        ee2 = self.EEDropDown2.Text
        if ee2 == "Active Edge Grip":
            ee2 == "AEG"
        self.alignLoc = self.AlignerLocDropDown.Text

    def buttonPressed(self, sender, args):
        global alignerLocation
        logTimeStamp("btn pressed")
        #fileName = "I:\\data.txt"
        fileName = "D:\\data.txt"
        ReadDataFromFile(fileName, numLPs)
        alignerLocation = self.alignLoc
        logTimeStamp("Data has been read into variables")
        time.sleep(0.25)
        # TestForm.chooseGui(self)

    def saveDataBoxChanged(self, sender, args):
        logTimeStamp("Teach data to be saved")
        self.saveData = self.saveDataBox.Check

    def lpDDChanged(self, sender, args):
        global numLPs
        numLPs = int(self.lpDropDown.Text)
        logTimeStamp("LP Drop Down selected")
        logTimeStamp("There are " + numLPs.ToString() + " Load Ports")
        self.AlignerLocDropDown.Text = "Aligner Location"
        self.AlignerLocDropDown.Items.Clear()
        self.AlignerLocDropDown.Items.Add("Left")
        self.AlignerLocDropDown.Items.Add("Right")
        for i in range(0, numLPs, 1):
            self.AlignerLocDropDown.Items.Add("Load Port " + chr(65 + i))
        self.AlignerLocDropDown.Items.Add("Custom")  # TODO deal with this later
        self.AlignerLocDropDown.Enabled = True  # must select the number of load ports first

    def ee1DDChanged(self, sender, args):
        global ee1
        ee1 = self.EEDropDown1.Text
        if ee1 == "Active Edge Grip":
            ee1 = "AEG"
        logTimeStamp("EE1 drop down selected")
        logTimeStamp("EE1 type: " + ee1)
        if ee1 == "Null":
            logTimeStamp("There is no EE present EE1 location")

    def ee2DDChanged(self, sender, args):
        global ee2
        ee2 = self.EEDropDown2.Text
        if ee2 == "Active Edge Grip":
            ee2 = "AEG"
        logTimeStamp("EE2 drop down selected")
        logTimeStamp("EE2 type: " + ee2)
        if ee2 == "Null":
            logTimeStamp("There is no EE present EE2 location")

    def alDDChanged(self, sender, args):
        self.alignLoc = self.AlignerLocDropDown.Text
        logTimeStamp("Aligner Location selected")
        logTimeStamp("Aligner Location is: " + self.alignLoc)


class TestForm2(Form):
    def __init__(self):
        global numLPs
        self.Text = "Teach Specifications"

        self.textBox = TextBox()
        self.textBox.Location = Point(30, 30)
        self.textBox.Text = "Select the desired end effector\nand location to be taught"
        self.textBox.Height = 90
        self.textBox.Width = 100

        self.button3 = Button()
        self.button3.Text = "Start"
        self.button3.Enabled = False
        self.button3.Location = Point(20, 200)
        self.button3.DialogResult = DialogResult.OK
        self.button3.Click += self.button3Pressed

        self.textBox1 = TextBox()
        self.textBox1.Location = Point(20, 110)
        self.textBox1.Height = 30
        self.textBox1.Width = 150
        self.textBox1.Text = "Aligner PN"
        self.textBox1.Enabled = False

        button4 = Button()
        button4.Text = "Quit"
        button4.Enabled = True
        button4.Location = Point(130, 200)
        button4.DialogResult = DialogResult.Cancel

        self.ChoosingEE = ComboBox()
        if ee1 != "Null":
            self.ChoosingEE.Items.Add("EE1: " + ee1)
        if ee2 != "Null":
            self.ChoosingEE.Items.Add("EE2: " + ee2)
        self.ChoosingEE.Text = "Which EE"
        self.ChoosingEE.Enabled = True
        self.ChoosingEE.Location = Point(20, 60)
        self.ChoosingEE.TextChanged += self.chooseEEChanged

        self.ChoosingLoc = ComboBox()
        for i in range(0, int(numLPs), 1):
            self.ChoosingLoc.Items.Add("Load Port " + chr(65 + i))
        self.ChoosingLoc.Items.Add("Aligner")
        self.ChoosingLoc.Text = "Which Location"
        self.ChoosingLoc.Enabled = True
        self.ChoosingLoc.Location = Point(20, 90)
        self.ChoosingLoc.TextChanged += self.chooseLocChanged

        self.Controls.Add(self.button3)
        self.Controls.Add(button4)
        self.Controls.Add(self.textBox)
        self.Controls.Add(self.textBox1)
        self.Controls.Add(self.ChoosingEE)
        self.Controls.Add(self.ChoosingLoc)

        self.EE = self.ChoosingEE.Text[0:3].upper()
        self.teachstn = namePort(self.ChoosingLoc.Text)
        self.alignerPN = self.textBox1.Text

    def button3Pressed(self, sender, args):
        logTimeStamp("Teach button pressed")
        ReadPrevTeach()
        print("Successfully saved all previous data")
        Unteach(self.EE, self.teachstn)
        if self.teachstn == "WaferAligner":
            teachAligner(self.alignerPN, alignerLocation, numLPs, self.EE)
        else:
            # TODO: gui remains open because call from here, not from run() method
            learn(self.EE, self.teachstn)

    def chooseEEChanged(self, sender, args):
        self.EE = self.ChoosingEE.Text[0:3].upper()
        logTimeStamp("EE chosen")
        logTimeStamp("EE chosen is: " + self.EE)
        self.button3.Enabled = True

    def chooseLocChanged(self, sender, args):
        self.teachstn = namePort(self.ChoosingLoc.Text)
        logTimeStamp("Teach Location chosen")
        print("TEACHSTN LINE 525: ")
        print(self.teachstn) # why is this None when aligner is chosen?
        print(type(self.teachstn))
        logTimeStamp("Teach Location is: " + self.teachstn)
        if self.teachstn == "WaferAligner":
            self.textBox1.Enabled = True

    def namePort(str):
        print(str)
        if str == "Load Port A":
            return "PortA"
        if str == "Load Port B":
            return "PortB"
        if str == "Load Port C":
            return "PortC"
        if str == "Load Port D":
            return "PortD"
        if str == "Aligner":
            return "WaferAligner"


class TestFormError(Form):
    def __init__(self):
        logTimeStamp("Error being displayed to gui")
        label = Label()
        label.Text = "An error has occured\nPlease view log file for details\nSystem Exiting"
        label.Location = Point(50, 180)
        label.Height = 30
        label.Width = 50
        self.Controls.Add(label)


# end of gui class definitions


# will rough step to trigger a change in sensor then fine step backwards to "untrigger" it
# moveForward is a boolean which is True iff the value should increase when FIRST finding
#    trigger point (i.e. when an end effector is extending moveForward would be True)
# NOTE: this method cannot be used with the theta axis without modification
def sensorTrigger(axis, moveForward, bit=2, needGripMiddle=False):  # default is use of the high bit
    initialSensorVal = io.DioReadBit(1, bit)
    rough = rstep
    fine = -fstep
    if not moveForward:
        rough = -rough
        fine = -fine  # so will be equivalent to fstep
    while 1:
        Rv = io.DioReadBit(1, bit)
        if Rv != initialSensorVal:  # sensor value has changed
            break
        ef.MoveRelative(axis, NumberWithUnit(rough, "mm"))
    time.sleep(1)
    if needGripMiddle and isAEG:
        ef.ApplyWaferRestraint(EE)
    while 2:
        Rv = io.DioReadBit(1, bit)
        if Rv == initialSensorVal:
            break
        ef.MoveRelative(axis, NumberWithUnit(fine, "mm"))
    time.sleep(1)
    ef.MoveRelative(axis, NumberWithUnit(-fine, "mm"))
    time.sleep(1)


def convertToFloat(val, unit="mm"):
    unit = " " + unit
    val1 = NumberWithUnit.ToString(val)
    val2 = val1.rstrip(unit)
    val3 = float(val2)
    return val3



def verifyWafPres(ee, descriptor=""):
    logTimeStamp("Verifying wafer is present on " + ee)
    isPresent = isWafThere(ee, descriptor)
    try:
        if not isPresent:
            message = "No wafer on EE " + descriptor + "\n\rPlace wafer on EE and retry"
            raise Exception(message)
    except:
        displayError(message)
        raise
    logTimeStamp("Wafer successfully found on " + ee)


def verifyWafAbs(ee, descriptor=""):
    logTimeStamp("Verifying wafer is absent on " + ee)
    isPresent = isWafThere(ee, descriptor)
    try:
        if isPresent:
            message = "wafer detected on EE" + descriptor + "\n\r Stopping teach!!!"
            raise Exception(message)
    except:
        displayError(message)
        raise
    logTimeStamp("Wafer successfully not found on " + ee)


def isWafThere(ee, descriptor=""):
    WafPres = int(ef.MapWaferPresenceOnHost(ee))
    try:
        if WafPres == -2:
            message = "Unknown wafer state on EE" + descriptor + "\n\rPlace wafer on EE and retry"
            raise Exception(message)
    except:
        displayError(message)
        raise
    if WafPres == 1:
        return True
    return False


def checkValidLoc(theta, x, stn):
    logTimeStamp("Checking that x and theta are at valid positions for Z teach")
    logTimeStamp("Current theta: " + theta.ToString())
    logTimeStamp("Current X: " + x.ToString())
    logTimeStamp("Current Station: " + stn)
    message = "" # keping the compiler happy
    try:
        if theta < MinT or theta > MaxT:
            message = "Theta out of auto-teach range, EE not extended"
            raise Exception(message)
        elif stnA == stn:
            if x < MinXA or x > MaxXA:
                message = "X out of auto-teach range for station A, EE not extended"
                raise Exception(message)
        elif stnB == stn:
            if x < MinXB or x > MaxXB:
                message = "X out of auto-teach range for station B, EE not extended"
                raise Exception(message)
        elif stnC == stn:
            if x < MinXC or x > MaxXC:
                message = "X out of auto-teach range for station C, EE not extended"
                raise Exception(message)
        elif stnD == stn:
            if x < MinXD or x > MaxXD:
                message = "X out of auto-teach range for station D, EE not extended"
                raise Exception(message)
    except:
        displayError(message)
        raise


def checkValidEERange(ee, PosEE):
    try:
        if PosEE < MinEEPut or PosEE > MaxEEPut:
            message = "EE Put out of auto-teach range\n\rExiting auto-teach"
            ef.RetractEndEffecter(ee)
            raise Exception(message)
    except:
        displayError(message)


def checkZRange(ee, z):
    try:
        if ee == "EE1":
            if z < MinZ1 or z > MaxZ1:
                message = "Z out of auto-teach range\n\rexiting auto-teach"
                raise Exception(message)
        elif ee == "EE2":
            if z < MinZ2 or z > MaxZ2:
                message = "Z out of auto-teach range\n\rexiting auto-teach"
                raise Exception(message)
    except:
        displayError(message)
        raise


def ZDown2mm():
    logTimeStamp("Moving Z down 2 mm")
    ef.SetActiveRobotMotionProfile("Low")
    ef.MoveRelative("Z", NumberWithUnit(-2, "mm"))


def ZUp2mm():
    logTimeStamp("Moving Z up 2 mm")
    ef.SetActiveRobotMotionProfile("Low")
    ef.MoveRelative("Z", NumberWithUnit(2, "mm"))


def RetEE():
    logTimeStamp("Retracting EE")
    EE = self.chooseEE.Value
    ef.RetractEndEffecter(EE)


def ClearAlarm():
    logTimeStamp("Clearing alarm")
    ef.ClearAlarm()


def HomeRobot():
    logTimeStamp("Homing robot")
    ef.SetMotionServo("True")
    ef.HomeAllAxes()


def displayError(msg):
    TestFormError()
    logTimeStamp(msg)
    sys.exit()


def FindNewZ(Zh, Zl):  # both are in NWU form
    PosZh = convertToFloat(Zh)
    PosZl = convertToFloat(Zl)
    math = (PosZh - PosZl) / 2.0
    zMove = PosZl + math + .005  # New slot 12 Z
    CenterZ = (zMove - ((slotNumber - 1) * 10))
    return NumberWithUnit(CenterZ, "mm")  # new slot 1 Z





def changeStation(teachstn, EE, axis, NewPos):
    stn = [teachstn, "Slot"]
    dot = "."
    stn = dot.join(stn)
    ees = we.GetEndEffecters(cal)
    stations = we.GetStationNames(cal, EE)
    for s in stations:
        if s == stn:
            logTimeStamp(EE + " " + s + " " + axis)
            data = we.GetStationData(cal, EE, s)
            endEffecter = data.EndEffecter
            stationName = data.StationName
            indexName = data.IndexName
            indexAxis = data.IndexAxis
            startIndex = data.StartIndex
            locations = data.NumberOfLocations
            orgCoord = data.GetCoordinates()
            newCoord = Dictionary[String, NumberWithUnit]()
            keys = orgCoord.Keys
            for k in keys:
                v = orgCoord[k]
                n = NumberWithUnit(v.Number, v.Unit)
                if k != axis:
                    newCoord.Add(k, n)
                else:
                    newCoord.Add(k, NewPos)
    changed = RoboticStation(endEffecter, stationName, indexName, indexAxis, startIndex, locations, newCoord)
    we.SetStationData(cal, EE, stationName, changed)
    efsv.SaveStationDataToDisk(cal)
    logTimeStamp("Station parameters updated")


def MvToReadyPut(EE, teachstn):
    teachslot = "Slot12"
    # Format teach station and teach slot into proper format for API
    dot = "."
    stn = dot.join([teachstn, teachslot])
    ef.SetActiveRobotMotionProfile("Low")
    ef.MoveToReadyPut(EE, stn)




def teachOneZStn(ee, stn):
    MvToReadyPut(ee, stn)
    ExtendEE(ee, stn)
    ef.ReleaseWaferRestraint(ee)
    ZDownToTeach(ee)
    # make sure that here the EE moves 2 mm forward if it is an AEG EE
    AutoTeachZ(ee, stn)


# should this only read in data for the singular location we are in?
# or call once for all locations?
def GetStnData(self, numLPs):  # , event):
    from datetime import datetime, date, time
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    message = "Saving Station Teach Data"

    # here is where we want to read in data from a file
    fileName = "D:\\data.txt"
    ReadDataFromFile(fileName, numLPs)
    # do I have o save the data?
    # where and how


def ExtendEE(EE, teachstn):
    ef.SetActiveRobotMotionProfile("Low")
    PosTheta = convertToFloat(ef.GetAxisPosition("Theta"), "degree")  # Get current Theta while parked at station
    PosX = convertToFloat(ef.GetAxisPosition("X"))
    checkValidLoc(PosTheta, PosX, teachstn)

    axis = "EEPut"
    efsv.LoadStationDataFromDisk(cal)
    dot = "."
    stn = dot.join([teachstn, "Slot"])
    ees = we.GetEndEffecters(cal)

    data = we.GetStationData(cal, EE, stn)
    coords = data.GetCoordinates()
    nb = coords[axis]
    ef.MoveAbsolute(EE, nb)


def ZDownToTeach(EE):
    verifyWafPres(EE)
    ef.ReleaseWaferRestraint(EE)
    ef.SetActiveRobotMotionProfile("Low")
    ef.MoveRelative("Z", NumberWithUnit(-22, "mm"))


def AutoTeachZ(EE, teachstn):
    io.DioWriteBit(0, 0, 0)  # make sure output is low to enable sensor
    # Format teach station and teach slot into proper format for API
    dot = "."
    stn = dot.join([teachstn, teachslot])
    #
    Rh = io.DioReadBit(1, 2)  # Define high level input bit from sensor
    Rl = io.DioReadBit(1, 1)  # Define low level input bit from sensor
    Rg = io.DioReadBit(1, 0)  # Define good range input bit from sensor
    #  Begin the teaching sequence
    PosTheta = convertToFloat(ef.GetAxisPosition("Theta"), "degree")
    PosX = convertToFloat(ef.GetAxisPosition("X"))
    checkValidLoc(PosTheta, PosX, teachstn)

    ef.SetActiveRobotMotionProfile("Home")
    message = "Z Teach Beginning\n\rPlease wait about 1 minute"
    # TODO is this stillthe approximate amount of time?
    # un program after done and modify appropriately
    logTimeStamp(message)
    PosEE = convertToFloat(ef.GetAxisPosition(EE))
    checkValidEERange(EE, PosEE)

    time.sleep(1)
    ef.ReleaseWaferRestraint(EE)
    time.sleep(1)
    ef.MoveRelative("Z", NumberWithUnit(-10, "mm"))
    time.sleep(1)
    ef.SetWaferPresenceOnHost(EE, WaferPresenceState.Absent)
    verifyWafAbs(EE, " while Z down ")

    # toggle output bit on and off to set sensor zero with wafer on shelf
    io.DioWriteBit(0, 0, 1)
    time.sleep(1)
    io.DioWriteBit(0, 0, 0)
    time.sleep(2)
    if isAEG:
        ef.MoveRelative(EE, NumberWithUnit(2, "mm"))  # move forward to make sure tips clear substrate during z up

    ef.MoveRelative("Z", NumberWithUnit(4, "mm"))
    # CHECK here because not totally sure here
    sensorTrigger("Z", True, 2, True)
    time.sleep(2)  # settle and then grip the wafer
    ef.ApplyWaferRestraint(EE)
    if isAEG:  # move back to the actual wafer position at station
        ef.MoveRelative(EE, NumberWithUnit(-2, "mm"))
    ef.MoveRelative("Z", NumberWithUnit(-2, "mm"))  # move down to be below sensor transition points
    sensorTrigger("Z", True)
    PosZh = ef.GetAxisPosition("Z")  # read transition point and record as high point
    # move down in fine step until low transition point found
    print("High: " + PosZh.Number.ToString())
    sensorTrigger("Z", False, 1)
    PosZl = ef.GetAxisPosition("Z")
    print("1020")
    NewZ = FindNewZ(PosZh, PosZl)
    print("1022")
    logTimeStamp("Successfully found both low and high points")
    print("High: " + PosZh.Number.ToString())
    print("Low: " + PosZl.Number.ToString())
    print("New: " + NewZ.Number.ToString())

    ef.SetActiveRobotMotionProfile("Low")
    PosZn = convertToFloat(ef.GetAxisPosition("Z"))

    checkZRange(EE, PosZn)
    changeStation(teachstn, EE, "BaseZ", NewZ)
    TestForm2()




# called before the teach code is executed, this method overwrites existing teach
# data with predicted median approximate values
def Unteach(ee, loc):
    if ee == "EE1":
        midZ = (MaxZ1 + MinZ1) / 2
    else:
        midZ = (MaxZ1 + MinZ1) / 2
    if loc == "PortA":
        midX = (MaxXA + MinXA) / 2
    elif loc == "PortB":
        midX = (MaxXB + MinXB) / 2
    elif loc == "PortC":
        midX = (MaxXC + MinXC) / 2
    elif loc == "PortD":
        midX = (MaxXD + MinXD) / 2

    midT = (MaxT + MinT) / 2
    midEEGet = (MaxEEGet + MinEEGet) / 2
    midEEPut = (MaxEEPut + MinEEPut) / 2

    changeStation(loc, ee, "Z", NumberWithUnit(midZ, "mm"))
    changeStation(loc, ee, "X", NumberWithUnit(midX, "mm"))
    changeStation(loc, ee, "Theta", NumberWithUnit(midT, "mm"))
    changeStation(loc, ee, "EEGet", NumberWithUnit(midEEGet, "mm"))
    changeStation(loc, ee, "EEPut", NumberWithUnit(midEEPut, "mm"))


# this method reads data relating to the generic teach position of the aligner
# and moves the EE to the correct position
def readGenericAlignerPos(PN, alignerPos, numLPs, EE):
    ef.RetractEndEffecter(EE)
    alignerPos = alignerPos.lower()
    fileName = "D:\\aligner_definition.txt"
    file = open(fileName, 'r')
    # clear first two lines
    file.readline()
    file.readline()
    while file.hasLine():
        try:
            line = file.readline()
        except:
            break
        array = line.split()
        if (array[0].lower() == alignerPos) and (int(array[1][0]) == numLPs):
            readInAlignerOffsets(EE, file, PN)
            # TODO HOW TO DO BELOW
            xChange = calcThetaChange(XOffset, array[3])
            xVal = NumberWithUnit(array[2], "mm")
            rVal = NumberWithUnit(array[3] + R, "mm")
            tVal = NumberWithUnit(array[4] + T, "degree")
            zVal = NumberWithUnit(array[5] + ZOffset, "mm")
            ef.MoveAbsolute("X", xVal)
            ef.MoveAbsolute("Z", zVal)
            ef.MoveAbsolute("Theta", tVal)
            ef.MoveAbsolute(EE, rVal)
            return
    message = "Error: aligner location is not saved in memory and unable to locate"
    logTimeStamp("Aligner rough position must be saved in file before teaching\n" +
                 "otherwise unable to locate aligner")
    displayError("Error: aligner location is not saved in memory and unable to locate")


def readInAlignerOffsets(EE, file, PN):
    global ZOffset, XOffset, T, R, PlusZ, MinusZ
    topLine = "PN				Z	X	T	R	+Z	-Z\n"
    infoLine = ""
    while True:
        line = file.readline()
        if line == topLine:
            break
    while True:
        line = file.readline()
        array = line.split()
        if array[0] == PN:
            array[1] = ZOffset
            array[2] = XOffset
            array[3] = T
            array[4] = R
            array[5] = PlusZ
            array[6] = MinusZ

    message = "Unable to find teaching offset"
    logTimeStamp("Aligner offsets with fixture not provided\nStopping teach")
    displayError(message)
    return



def intFromString(str):
    newStr = ""
    for char in str:
        if char.isnumeric() or char == '-':
            newStr += char
    return newStr


# obtains current saved teach location data and then modifies that
# location by parameter "amount"
def adjustStationData(stn, axis, EE, amount):
    if stn == "WaferAligner":
        stn = "WaferAligner.Chuck"
    data = we.GetStationData(cal, EE, stn)
    data1 = data.ToString().split(' (')
    for coord in data1:
        coordArr = coord.slit("=")
        coordAxis = coordArr[0]
        numStr = coordArr[1]
        if coordAxis == axis:
            val = intFromString(numStr)
    newVal = val + amount
    if axis == "Theta":
        unit = "degree"
    else:
        unit == "mm"
    newTeachPos = NumberWithUnit(newVal, unit)
    changeStation(stn, EE, axis, newTeachPos)




def run():
    ef.ClearAlarm()
    ef.SetMotionServo(True)
    ef.SetActiveRobotMotionProfile("Low")
    form = TestForm()
    ret = form.ShowDialog()
    form2 = TestForm2()
    ret2 = form2.ShowDialog()

def ExitTeaching():
    # sys.exit()
    logTimeStamp("Exiting teach")
    print("Exiting teach")