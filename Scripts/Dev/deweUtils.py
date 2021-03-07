from datetime import datetime

def DeweInit(dw, DataDir, SetupFile):
    print("Initializing Dewesoft... ")
    
    dw.Init()
    dw.Enabled = 1
    dw.Visible = 1
    print('done.')
    
    # set window dimensions
    dw.Top = 0
    dw.Left = 0
    dw.Width = 1024
    dw.Height = 768
    
    # build channel list
    dw.Data.BuildChannelList()
    
    with open(SetupFile, 'r') as file:
        data = file.read()
    file.close
    
    dw.LoadSetupFromXML(data)
    
    dw.SetMainDataDir(DataDir)
    
def getMeasName():
    MeasName = str(datetime.now())
    MeasName = MeasName[:MeasName.find('.')]
    MeasName = MeasName.replace(':','')
    MeasName = MeasName.replace('-','')
    MeasName = MeasName.replace(' ','')
    return MeasName