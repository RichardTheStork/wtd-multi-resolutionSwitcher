import maya.cmds as cmds

tempSel = cmds.ls(selection = True)


objectsToChange = {}
wantedResolution = "hir"
for i in tempSel:
    currentLocatorName = ""
        
    shape = cmds.listRelatives(i,shapes=True,fullPath=True)
    print shape
    
    if cmds.objectType(shape) == 'locator':
        print i, "is", cmds.objectType(shape)
        
    else:
        print "Not what we look for", i
        print cmds.objectType(shape)
        continue
    
    print "Go on..."