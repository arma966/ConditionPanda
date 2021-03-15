import JsonExport as je

fileDir = "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\Scripts\\FilesDemo\\LattePanda20210314144404"
dataDict = je.buildDataDictionary(fileDir)
rawDict = je.buildRawDictionary(fileDir)

shot = je.getShot(dataDict["AST"])

dataDictName = shot + "KPI"
rawDictName = shot + "Raw"
je.to_json(dataDict, dataDictName)
je.to_json(rawDict, rawDictName)