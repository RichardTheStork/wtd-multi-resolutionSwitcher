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
	
	children = cmds.listRelatives(obj,ad=True,type='transform',fullPath=True)
	refList = []
	for child in children:
		print "CHILD IS = ", child, 'from', obj
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
	