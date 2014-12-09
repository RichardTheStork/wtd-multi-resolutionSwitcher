import maya.cmds as cmds
import pymel.core as pm
import os

def switch_resolution(selectionObj):
	references = getChildrenObjRefence(selectionObj)
	
	if len(references) > 0:
		createReference()
	
def getChildrenObjRefence(obj):
	references = cmds.ls(type='reference', l = True)
	# references = pm.listReferences()
	
	refList = []
	children = cmds.listRelatives(obj,ad=True,type='transform',fullPath=True)
	if children == None or children == []:
		print 'No children found'
		return refList
	for child in children:
		if ":" in child:
			print child
			obj = str.split(str(child),"|")[-1]
			ns = ":"+str.rsplit(obj,":",1)[0]
			curRef = ''
			for ref in references:
				if ref != 'sharedReferenceNode':
					nsRef = cmds.referenceQuery(ref,namespace=True)
					if ns == nsRef:
						curRef = ref
			refList += [str(curRef)]
	return refList
	
def checkIfLocator(obj):
	shape = cmds.listRelatives(obj,shapes=True,fullPath=True)
	if shape!=None:
		if cmds.objectType(shape) == "locator":
			return True
	return False
	
def eraseLocatorContent(obj):
    tempRels = cmds.listRelatives(obj, f = True)
    
    for r in tempRels:
        if cmds.objectType(r) != 'locator':
            cmds.delete(r)

	