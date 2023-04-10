"""
this is moving the robot to the correct place using the gui and config file
teaching of the robot will basically work like this:
    gui and moving the default values will be done in robotTeach.py
    once that is done the robot will be moved to location slot 13

"""
from robotTeach import *
import RPi.GPIO as GPIO
import time

#moves to the slot number 13 which is from the config file
def AutoTeachZ():

    GPIO.setmode(GPIO.BOARD)
    # for high
    GPIO.setup(5, GPIO.OUT)
    # for good
    GPIO.setup(6, GPIO.OUT)
    # for low
    GPIO.setup(13, GPIO.OUT)
    # runs the GUI and sets all of the default values
    getconfigvalues()

    #io.DioWriteBit(0, 0, 0)  # make sure output is low to enable sensor
    #use three GIPO for LEDs

    teachslot = "Slot"+slotNumber  # define teach slot
    slotNo = slotNumber
    fstep = fineStepSize  # fine step size for teach motion
    qstep = roughStepSize  # rough step size for teach motion
    # Define nominal teach paramters for ASML JCP
    TopDive = 3
    BottomDive = -2
    PlusZOff = 3
    MinusZOff = 3.15
    currentMinX = loadPortMin
    currentMaxX = loadPortMax
    currentMaxZ = MaxZaxZ
    currentMinZ = MinZinZ
    MaxT = maxT
    MinT = minT
    MaxEEGet = eeGetMax
    MinEEGet = eeGetMin
    MaxEEPut = eePutMax
    MinEEPut = eePutMin
    GetOffset = 2
    # Define available stations for teaching
    EEType = "AEG"  # sets EE type to perfrom 2mm R offset for AEG during pick
    EE = effemType  # Gets EE selected from GUI input
    teachstn = currentLoadPort  # Gets teach station from GUI input
    # Format teach station and teach slot into proper format for API
    stn = [teachstn, teachslot]
    dot = "."
    stn = dot.join(stn)
    #
    Rh = io.DioReadBit(1, 2)  # Define high level input bit from sensor
    Rl = io.DioReadBit(1, 1)  # Define low level input bit from sensor
    Rg = io.DioReadBit(1, 0)  # Define good range input bit from sensor
    #  Begine the teaching sequence
    #
    #  Get Axis positions at the station location (should update to get from param file instead)
    #
    PosTheta = ef.GetAxisPosition("Theta")  # Get current Theta while parked at station
    PosTheta1 = NumberWithUnit.ToString(PosTheta)  # convert to string
    PosTheta2 = PosTheta1.rstrip(" degree")  # strip unit
    PosTheta3 = float(PosTheta2)  # convert to floating point so math works
    PosX = ef.GetAxisPosition("X")
    PosX1 = NumberWithUnit.ToString(PosX)
    PosX2 = PosX1.rstrip(" mm")
    PosX3 = float(PosX2)
    #
    # Check if the Theta and X positions are within nominal range to allow auto-teaching
    #
    try:
        if PosTheta3 < MinT or PosTheta3 > MaxT:
            message = "Theta out of auto-teach range\n\rexiting auto-teach"
            raise Exception(message)
        elif teachstn:
            if PosX3 < currentMinX or PosX3 > currentMaxX:
                message = "X out of auto-teach range\n\rexiting auto-teach"
                raise Exception(message)
    except:  # Halt auto teach and display message
        raise

    ef.SetActiveRobotMotionProfile("Low")
    message = "Z Teach Beginning\n\rPlease wait about 1 minute"
    print(message)
    #
    # Check if EE position is in safe nominal range for teaching
    #
    PosEE = ef.GetAxisPosition(EE)
    PosEE1 = NumberWithUnit.ToString(PosEE)
    PosEE2 = PosEE1.rstrip(" mm")
    PosEE3 = float(PosEE2)
    try:
        if PosEE3 < MinEEPut or PosEE3 > MaxEEPut:
            message = "EE Put out of auto-teach range\n\rexiting auto-teach"
            ef.RetractEndEffecter(EE)
            raise Exception(message)
    except:
        # Exit teach and display message if EE is out of range
        self.panelDisplay.Label = message
        print(message)

    #
    #
    # Check to make sure a wfer is present on EE
    #
    #
    # WafPres = ef.GetWaferPresenceOnHost(EE)
    # try:
    #	if WafPres == 0:
    #		message = "No wafer on EE\n\rPlace wafer on EE and press GRIP button"
    #		self.panelDisplay.Label = message
    #		raise Exception(message)
    # except:
    # Exit teach and display message if EE is out of range
    #	self.panelDisplay.Label = message
    #	raise
    # try:
    #	if WafPres == -2:
    #		message = "Unknown wafer state on EE\n\rPlace wafer on EE and press GRIP button"
    #		self.panelDisplay.Label = message
    #		raise Exception(message)
    # except:
    # Exit teach and display message if EE is out of range
    #	self.panelDisplay.Label = message
    #	raise
    ef.ReleaseWaferRestraint(EE)
    ef.SetActiveRobotMotionProfile("Home")
    # ef.MoveRelative("Z",NumberWithUnit(-16,"mm"))
    #
    # Verify wafer is no longer gripped
    #
    WafPres = ef.MapWaferPresenceOnHost(EE)
    try:
        if WafPres == 1:
            message = "wafer detected on EE while Z down\n\r stopping teach"
            print(message)
            raise Exception(message)
    except:
        # Exit teach and display message if EE is out of range
        print(message)
        raise
    try:
        if WafPres == -2:
            message = "Unknown wafer state on EE\n\r stopping teach"
            print(message)
            raise Exception(message)
    except:
        # Exit teach and display message if EE is out of range
        print(message)
        raise

    # toggle output bit on and off to set sensor zero with wafer on shelf
    io.DioWriteBit(0, 0, 1)
    time.sleep(1)
    io.DioWriteBit(0, 0, 0)
    time.sleep(2)
    if EE == "AEG":  # move forward to mnmake sure tips clear substrate during z up
        ef.MoveRelative(EE, NumberWithUnit(2, "mm"))
    ZMove = 152

    # ef.MoveRelative("Z",NumberWithUnit(12,"mm"))	# jump up 12mm to save time
    #
    # Verify wafer is gripped again
    #
    #
    WafPres = ef.MapWaferPresenceOnHost(EE)
    try:
        if WafPres == 0:
            message = "Wafer not detected after Z up\n\r stopping teach"
            print(message)
            raise Exception(message)
    except:
        # Exit teach and display message if EE is out of range
        print(message)
        raise
    try:
        if WafPres == -2:
            message = "Unknown wafer state on EE after Z up\n\r stopping teach"
            print(message)
            raise Exception(message)
    except:
        # Exit teach and display message if EE is out of range
        print(message)
        raise

    # move up to high transition on and then down to off and apply wafer restraint
    while 20:
        Rh = io.DioReadBit(1, 2)
        if Rh == 0:
            GIPO.output(13, True)
            break
        ef.MoveRelative("Z", NumberWithUnit(qstep, "mm"))
        GIPO.output(13, False)
    time.sleep(2)
    while 21:
        Rh = io.DioReadBit(1, 2)
        if Rh == 1:
            GIPO.output(5, True)
            break
        ef.MoveRelative("Z", NumberWithUnit(-fstep, "mm"))
        GIPO.output(5, False)
    time.sleep(2)  # settle and then grip the wafer
    ef.ApplyWaferRestraint(EE)
    if EEType == "AEG":  # move back to the actual wafer position at station
        ef.MoveRelative(EE, NumberWithUnit(-2, "mm"))
    ef.MoveRelative("Z", NumberWithUnit(-2, "mm"))  # move down to be below sensor transition points
    # with wafer gripped step up in rough steps to high transition and then down in fine step until it is back off
    while 8:
        Rh = io.DioReadBit(1, 2)
        if Rh == 0:
            GIPO.output(13, True)
            break
        ef.MoveRelative("Z", NumberWithUnit(fstep, "mm"))
        GIPO.output(13, False)
    time.sleep(2)
    while 9:
        Rh = io.DioReadBit(1, 2)
        if Rh == 1:
            GIPO.output(5, True)
            break
        ef.MoveRelative("Z", NumberWithUnit(-fstep, "mm"))
        GIPO.output(5, False)
    PosZh = ef.GetAxisPosition("Z")  # read transition point and record as high point
    time.sleep(2)
    # move down in fine step until low transition point found
    while 10:
        Rh = io.DioReadBit(1, 1)
        if Rh == 0:
            GIPO.output(5, True)
            break
        ef.MoveRelative("Z", NumberWithUnit(-fstep, "mm"))
        GIPO.output(6, True)

    PosZl = ef.GetAxisPosition("Z")
    # convert axis positions for math
    PosZh1 = NumberWithUnit.ToString(PosZh)
    PosZh2 = PosZh1.rstrip(" mm")
    PosZh3 = float(PosZh2)
    PosZl1 = NumberWithUnit.ToString(PosZl)
    PosZl2 = PosZl1.rstrip(" mm")
    PosZl3 = float(PosZl2)
    # Calculate the center of high and low transition points to get new Z @ teach slot
    math = PosZh3 - PosZl3
    math = math / 2
    # convert slot 12 Z to slot 1 Z to store
    zMove = PosZl3 + math + .005  # New slot 12 Z
    CenterZ = (zMove - ((slotNo - 1) * 10))
    NewZ = NumberWithUnit(CenterZ, "mm")  # new slot 1 Z
    ef.MoveAbsolute("Z", NumberWithUnit(zMove, "mm"))
    ef.SetActiveRobotMotionProfile("Low")
    # ef.RetractEndEffecter(EE)
    PosZn = ef.GetAxisPosition("Z")
    PosZn1 = NumberWithUnit.ToString(PosZn)
    PosZn2 = PosZn1.rstrip(" mm")
    PosZn3 = float(PosZn2)
    #
    # Chek for which EE is selected and then verify Z is in nomnal range
    #
    try:
        if currentZ:
            if PosZn3 < currentMinZ or PosZn3 > currentMinZ:
                message = "Z out of auto-teach range\n\r exiting auto-teach"
                print(message)
                raise Exception(message)
    except:
        # Halt auto teach and display message
        print(message)
        raise
    #
    axis = "BaseZ"
    efsv.LoadStationDataFromDisk(cal)
    stn = [teachstn, "Slot"]
    dot = "."
    stn = dot.join(stn)
    ees = we.GetEndEffecters(cal)
    stations = we.GetStationNames(cal, EE)
    # loop through station paramters and change the 'axis' parameters only (BaseZ)
    for s in stations:
        if s == stn:
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
                if k != axis:
                    v = orgCoord[k]
                    n = NumberWithUnit(v.Number, v.Unit)
                    newCoord.Add(k, n)
                if k == axis:
                    wq = orgCoord[k]
                    nb = NumberWithUnit(wq.Number, wq.Unit)
                    newCoord.Add(k, NewZ)
            changed = RoboticStation(endEffecter, stationName, indexName, indexAxis, startIndex, locations, newCoord)
            we.SetStationData(cal, EE, stationName, changed)
            efsv.SaveStationDataToDisk(cal)
    message = "Teach Completed\n\r New Z position is: " + str(NewZ) + "\n\r Z position was: " + str(nb)
    print(message)