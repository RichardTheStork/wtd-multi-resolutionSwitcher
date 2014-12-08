# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform import Application

import maya.cmds as cmds
import pymel.core as pm
import os

class StgkStarterApp(Application):
	"""
	The app entry point. This class is responsible for intializing and tearing down
	the application, handle menu registration etc.
	"""
	
	def init_app(self):
		"""
		Called as the application is being initialized
		"""
		
		# first, we use the special import_module command to access the app module
		# that resides inside the python folder in the app. This is where the actual UI
		# and business logic of the app is kept. By using the import_module command,
		# toolkit's code reload mechanism will work properly.
		# app_payload = self.import_module("app")

		# now register a *command*, which is normally a menu entry of some kind on a Shotgun
		# menu (but it depends on the engine). The engine will manage this command and 
		# whenever the user requests the command, it will call out to the callback.

		# first, set up our callback, calling out to a method inside the app module contained
		# in the python folder of the app
		# menu_callback = lambda : app_payload.dialog.show_dialog(self)

		# now register the command with the engine
		# self.engine.register_command("Show Starter Template App...", menu_callback)
		
		self.resolution = self.get_setting("target_resolution")
		self.resolutionShort = self.get_setting("target_resolution_shortname")
		
		# self.engine.register_command("Switch resolution to %s" %resolution, menu_callback)
		# self.app = self.import_module("app")
		self.switcher = self.import_module("app").switcher
		self.engine.register_command("Switch to %s" %self.resolution, self.change_ref_resolution)
		
		if self.resolution == "Lay":
			self.engine.register_command("Replace by reference.", self.replace_by_reference)
		# print dir(self)
		# print dir(self.engine)

		
	def getAssetName(self, inputName):
		print "INPUTNAME = ", inputName
		tempName = None
		if inputName.find("_") != inputName.rfind("_"):
			tempName = inputName[ : inputName.rfind("_")]
			tempName = tempName[ tempName.rfind("_")+1 : ]
		else:
			tempName = inputName[ inputName.rfind("_")+1 : ]
			print inputName
			
		# print dir(self)
		print "TEMPNAME to search in shotgun = ", tempName
		asset = self.shotgun.find_one('Asset', [['code','is', tempName ]], ['code'])
		print asset		
		return tempName, asset
		
	def getAssetReferencePublishPath(self, asset, step = None, resolution = None):
		assetPublishTemplate = self.get_template_by_name("maya_asset_publish")
		fields = {'Step': step, 'sg_asset_type': 'Prop', 'Asset': asset}
		resolutionOptions = []
		if resolution == None:
			resolutionOptions.append(None)
			resolutionOptions.append("lay")
			resolutionOptions.append("lor")
			resolutionOptions.append("hir")
		else:
			resolutionOptions.append(resolution)
		print resolutionOptions
		
		for res in resolutionOptions:
			if res != None:
				fields["Resolution"] = res
			print fields
			versionPath = self.searchLatestVersions(assetPublishTemplate, fields)
			if versionPath != 0:
				return versionPath
		return None
		
	def searchLatestVersions(self, assetPublishTemplate, fields):
		# print "Start search for versions..."
		# print assetPublishTemplate
		# print fields
		all_versions = self.tank.paths_from_template(assetPublishTemplate, fields, skip_keys=["version"])
						
		latest_version = 0
		if len(all_versions) == 0:
			# errors[s]["NoResFound"]=("No %s resolution found for %s." %(self.resolution, s))
			return latest_version
		
		for ver in all_versions:
			fields = assetPublishTemplate.get_fields(ver)
			if fields["version"] > latest_version:
				latest_version = fields["version"]
		
		latest_path = assetPublishTemplate.apply_fields(fields)		
		return latest_path
		
	def replace_by_reference(self):
		tempSel = cmds.ls(selection  = True)
		errors = {}
		originalSelection = []
		for s in tempSel:
			originalSelection.append(s)
			errors[s] = {}
		for s in tempSel:
			print "#"*5, s
			
			if s.startswith("PRP_"):
				if not self.switcher.checkIfLocator(s):
					print "### Skipping selection : %s ; type is %s"%(s, cmds.objectType(s))
					continue
					
				## 0. get assetname
				assetName, asset = self.getAssetName(s)
				
				if asset == None:
					errors[s]["noAsset"]=("No asset with name %s found in shotgun." %assetName)
					continue
				references = self.switcher.getChildrenObjRefence(s)
				if len(references) == 0:
					print "1. import reference"
					path = self.getAssetReferencePublishPath(assetName, step = "mod")
					if path == None:
						continue
					print "2. erase all content..."
					self.switcher.eraseLocatorContent(s)
					if cmds.namespaceInfo(cur=True) != ":":
						cmds.namespace( setNamespace=":")
					ns = str.split(str(s),"_",1)[-1]
					referencedFile = cmds.file(path, reference = True,namespace=ns)
					print "3. parent and move to locator"
					cmds.namespace( setNamespace=ns )
					nsContent = cmds.namespaceInfo(listNamespace=True)
					child = ""#cmds.listRelatives()
					for obj in nsContent:
						if cmds.objectType(obj) == "transform":
							if cmds.listRelatives(obj,parent=True) == None:
								child = obj
					parent = s
					cmds.parent(child, parent, relative = True)
					
			else:
				print "### Skipping selection : %s ; Doesn't start with 'PRP_'"%(s)
			
		cmds.namespace( setNamespace=":" )
				
		errorMessages = ""
		for e in errors:
			if errors[e] == {}:
				continue
			errorMessages += ("###   %s   ###\n" %e)
			for line in errors[e]:
				errorMessages += ("- %s\n" %errors[e][line])
			errorMessages += "\n"
		
		if errorMessages != "":
			cmds.confirmDialog( t = "Error window", message = errorMessages, button = ["OK"])		
		
		cmds.select(originalSelection)

		
	def change_ref_resolution(self):
		print "resolution changing to %s" %self.resolution
		print "Current context is = ", self.context.entity
		print 'shortname =', self.resolutionShort
		
		# references = cmds.ls(type='reference')
		# print "REFERENCES with LS:"
		# print references
		# print "REFERENCES with pm.LISTREFS:"
		allRefs = pm.listReferences()
		print allRefs		
		
		assetPublishTemplate = self.get_template_by_name("maya_asset_publish")
		
		selectedObjects = cmds.ls(selection = True)
		print selectedObjects
		originalSelection = []
		errors = {}
		for s in selectedObjects:
			originalSelection.append(s)
			errors[s] = {}
			
		for s in selectedObjects:
			references = None
			
			try:
				references = self.switcher.getChildrenObjRefence(s)
			except:
				print "ERROR in finding references!!!"
				errors[s]["refError"]=("ERROR in finding references")
			if len(references) > 1:
				print "!!!   MORE THAN ONE REFERENCE FOUND IN OBJECT %s   !!!" %(s)
				# print "!!!            Check what to do           !!!"
				# children = cmds.listRelatives(s,ad=True,type='transform',fullPath=True)
				# print children
				# for c in children:
					# if c.find('PRP_') != -1 and cmds.objectType(c) == 'locator':
						# print 'should rerun this script on %s' %c
			elif len(references) == 0:
				errors[s]["noRefs"]=("No references found for this object.")
						
			node = None
			for r in references:
				node = r
				
				currentPath = pm.system.FileReference(node)
				currentPath = str(currentPath)
				if currentPath.endswith("}") and currentPath.find("{") != -1:
					currentPath = currentPath[ :currentPath.find("{")]
				fields = assetPublishTemplate.get_fields(str(currentPath))
				currentResolution = None
				if "Resolution" in fields:
					currentResolution = fields['Resolution']
					if currentResolution == self.resolutionShort:
						continue
						
				fields['Resolution'] = self.resolutionShort
				print fields
				all_versions = self.tank.paths_from_template(assetPublishTemplate, fields, skip_keys=["version"])
				# now look for the highest version number...
				
				if len(all_versions) == 0:
					errors[s]["NoResFound"]=("No %s resolution found for %s." %(self.resolution, s))
					continue
				
				latest_version = 0
				for ver in all_versions:
					fields = assetPublishTemplate.get_fields(ver)
					if fields["version"] > latest_version:
						latest_version = fields["version"]
						
				print 'last version is', latest_version			
				fields["version"] = latest_version
				new_path = assetPublishTemplate.apply_fields(fields)
				
				if node != None:
					rn = pm.system.FileReference(node)
					rn.replaceWith(new_path)
				
		cmds.select(originalSelection)
		
		errorMessages = ""
		for e in errors:
			if errors[e] == {}:
				continue
			errorMessages += ("###   %s   ###\n" %e)
			for line in errors[e]:
				errorMessages += ("- %s\n" %errors[e][line])
			errorMessages += "\n"
		
		if errorMessages != "":
			cmds.confirmDialog( t = "Error window", message = errorMessages, button = ["OK"])
		