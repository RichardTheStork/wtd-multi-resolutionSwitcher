import maya.cmds as cmds
import pymel.core as pm
import os

def switch_resolution(selectionObj):
	print assetName, targetResolution, reference
	
	references = getChildrenObjRefence(selectionObj)
	
	if len(references) > 0:
		createReference()
	
def getChildrenObjRefence(obj):
	# allNamespaces = cmds.namespaceInfo( ":", listOnlyNamespaces=True )
	print 'OBJECT IS = ', obj
	references = cmds.ls(type='reference', l = True)
	print "REFERENCES with LS:"
	print references
	# print "REFERENCES with pm.LISTREFS:"
	# references = pm.listReferences()
	# print references
	
	refList = []
	children = cmds.listRelatives(obj,ad=True,type='transform',fullPath=True)
	print children
	if children == None or children == []:
		print 'No children found'
		return refList
	for child in children:
		# print "CHILD IS = ", child, 'from', obj
		if ":" in child:
			print child
			obj = str.split(str(child),"|")[-1]
			ns = ":"+str.rsplit(obj,":",1)[0]
			#print ns
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
        print r
        print cmds.objectType(r)
        if cmds.objectType(r) != 'locator':
            print "DELETING %s" %r
            #cmds.select(r, add = True)
            cmds.delete(r)

			
			
			
"""

	
import maya.cmds as cmds

def checkIfLocator(obj):
	shape = cmds.listRelatives(obj,shapes=True,fullPath=True)
	if shape!=None:
		if cmds.objectType(shape) == "locator":
			return True
	return False
	
def eraseContent(obj):
    tempRels = cmds.listRelatives(obj, f = True)
    
    for r in tempRels:
        if cmds.objectType(r) != 'locator':
            cmds.delete(r)
    
def loadReference(name, path):
    print name, path
    



selection = cmds.ls(selection = True)
cmds.select(clear = True)
for s in selection:
    if checkIfLocator(s):
        print 'ok', s
        eraseContent(s)        
cmds.select(selection)



"""
