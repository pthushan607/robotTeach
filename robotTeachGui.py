import PySimpleGUI as sg

##GUI variables

robotNames = ['Reliance' , 'Razor' , 'WE']
efemWidth = ['2-wide', '3-wide', '4-wide']
loadPorts = ['Station-A', 'Station-B', 'Station-C', 'Station-D']
options = ['Yes', 'No']
optionsTwo = ['Left', 'Right']
optionsThree = ['Front', 'Back']
eeType = ['AEG', 'VBG Fork', 'VBG Paddle', 'PCB', 'PEC']

sg.theme('dark grey 7')

layout = [[sg.Text('Robot Type?'), sg.InputOptionMenu(robotNames)],
          [sg.Text('EFEM Width?'), sg.InputOptionMenu(efemWidth)],
          [sg.Text('Which station are you teaching?'), sg.InputOptionMenu(loadPorts)],
          [sg.Text('Is Traverser Installed?'), sg.InputOptionMenu(options)],
          [sg.Text('EE Type?'), sg.InputOptionMenu(eeType)],
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
            for x in range(9):
                print(values[x])
                window.close()

window.close()
