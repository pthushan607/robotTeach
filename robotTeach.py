
#variables for current tool specifications
global currentLoadPort
global effemType
global toggleVacuum
global togglePlunger
global moveForward
global loadPortMin
global loadPortMax
global currentZMax
global currentZMin
global thetaMin
global thetaMax
global eeGetMax
global eeGetMin
global eePutMax
global eePutMin
global fineStepSize
global roughStepSize


def guisetup():
    import PySimpleGUI as sg


    guiValues = []
## GUI variables

    robotNames = ['Reliance' , 'Razor' , 'WE']
    efemWidth = ['2-wide', '3-wide', '4-wide']
    loadPorts = ['LoadPortA', 'LoadPortB', 'LoadPortC', 'LoadPortD']
    options = ['Yes', 'No']
    optionsTwo = ['Left', 'Right']
    optionsThree = ['Front', 'Back']
    eeType = ['AEG', 'VBGFork', 'VBGPaddle', 'PCB', 'PEC']
    zOption = ['Z1', 'Z2']

    sg.theme('dark grey 7')


# GUI

    layout = [[sg.Text('Robot Type?'), sg.InputOptionMenu(robotNames)],
            [sg.Text('EFEM Width?'), sg.InputOptionMenu(efemWidth)],
            [sg.Text('Which station are you teaching?'), sg.InputOptionMenu(loadPorts)],
            [sg.Text('Is Traverser Installed?'), sg.InputOptionMenu(options)],
            [sg.Text('EE Type?'), sg.InputOptionMenu(eeType)],
            [sg.Text('Which Z?'), sg.InputOptionMenu(zOption)],
            [sg.Text('Is aligner installed?'), sg.InputOptionMenu(options)],
            [sg.Text('Is aligner left or right side?'), sg.InputOptionMenu(optionsTwo)],
            [sg.Text('Is aligner CCD front of Efem or Back of Efem?'), sg.InputOptionMenu(optionsThree)],
            [sg.Text('Aligner Station?'), sg.InputText()],
            [sg.Button('OK'), sg.Button('Quit')]
            ]

    window = sg.Window('Robot Teach', layout)

    while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break
            if event == 'OK':
                window.close()
                for x in values:
                    guiValues.append(values[x])

    window.close()




    return guiValues

# using the GUI and config updates the required variables
def getconfigvalues():

    import xml.etree.ElementTree as ET
    root = ET.parse('config.xml').getroot()

    #[robot type, ee width, station, traverser, ee type, which z, is aligner installed, alinger left or right, ccd front or back, alinger station]
    userInput = guisetup()
    currentLoadPort = userInput[2]
    currentEEType = userInput[4]
    currentZ = userInput[5]

    ## returns current loadport with the location min and max
    if currentLoadPort:
        for tag in root.findall("Ports/" + str(currentLoadPort)):
            loadPortLocationMin = int(tag.get('LocationMin'))
            loadPortLocationMax = int(tag.get('LocationMax'))
            print(loadPortLocationMin, loadPortLocationMax)

    # returns effems types with associated boolean values
    if currentEEType:
        for tag in root.findall("Effems/" + str(currentEEType)):
            toggleVacuum = (tag.get('ToggleVacuum'))
            togglePlunger = (tag.get('TogglePlunger'))
            moveForward = (tag.get('MoveForward'))
            print(toggleVacuum, togglePlunger, moveForward)

    if currentZ:
        for tag in root.findall("Zs/"+str(currentZ)):
            currentZMin = int(tag.get('LocationMin'))
            currentZMax = int(tag.get('LocationMax'))

    # gets the other dimensions from config
    for tag in root.findall('OtherDimension'):
        thetaMin = tag.get('RotationMin')
        thetaMax = tag.get('RotationMax')
        eeGetMax = tag.get('GetLocationMax')
        eeGetMin = tag.get('GetLocationMin')
        eePutMax = tag.get('PutLocationMax')
        eePutMin = tag.get('PutLocationMin')
        fineStepSize = tag.get('FineStepSize')
        roughStepSize = tag.get('RoughStepSize')
        print(thetaMin)
getconfigvalues()





