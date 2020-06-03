from os import mkdir
import sys
from odbAccess import*
from textRepr import*
from abaqusConstants import *
import time
import visualization
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from abaqus import session

def executePlugin(stepName,frames,setName,instanceName,instanceSetName,folderPath,folderName,fileName):
	startTotal = time.time()
	print " "
	print " "
	print " "
	folderPath += "\\exported\\"
	folderPath += folderName
	try:  
    		os.makedirs(folderPath)
	except OSError as error:
		error

	odb = openOdb(fileName)
	session.mdbData.summary()
	o1 = session.openOdb(fileName)
	session.viewports['Viewport: 1'].setValues(displayedObject=o1)
	
	framesList = parseToFrames(frames)
	for frame in framesList:
		exportModel(stepName, frame, setName, instanceName, instanceSetName, folderPath, odb)
	stopTotal = time.time()
	print "TOTAL EXPORT TIME " + str(stopTotal - startTotal) + "s"
##############################################################
#######model exporter
##############################################################

def exportModel(step, frame, setName, instanceName, instanceSetName, fileName, odb):
	start = time.time()
	fileName += "\\"
	fileName += str(frame)
	fileName += "\\"
	
	if setName == "" and instanceName == "":
		setName = " ALL ELEMENTS"

	print "STARTING EXPORTING"
	print "STARTING EXPORTING COORD"

	modelPath = fileName + "model\\"
	try:  
	    os.makedirs(modelPath)
	except OSError as error:
		error
	
	myFile = open(modelPath+'COORD.txt','w')
	for i in range(len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes)):
		tmpExportValue = odb.rootAssembly.nodeSets[" ALL NODES"].nodes[i]
		nodesCounter = len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes[i])
		if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
			for node in range(nodesCounter):
				myFile.write(str(tmpExportValue[node].coordinates[0]) + " " + str(tmpExportValue[node].coordinates[1]) + " " + str(tmpExportValue[node].coordinates[2]) + "\n")
		else:
			for node in range(nodesCounter):
				myFile.write(str(tmpExportValue[node].coordinates[0]) + " " + str(tmpExportValue[node].coordinates[1])  + "\n")
	myFile.close()
	
	print "COORD EXPORTED"
	print " "

	print "STARTING EXPORTING U"
	print "EXPORTING U1"
	myFile = open(modelPath+'U1.txt','w')
	tmpExportValue = odb.steps[step].frames[frame].fieldOutputs["U"].values
	for node in range(len(odb.steps[step].frames[frame].fieldOutputs["U"].values)):
		myFile.write(str(tmpExportValue[node].data[0])+'\n')
	myFile.close()
	print "U1 EXPORTED"

	print "EXPORTING U2"
	myFile = open(modelPath+'U2.txt','w')
	tmpExportValue = odb.steps[step].frames[frame].fieldOutputs["U"].values
	for node in range(len(odb.steps[step].frames[frame].fieldOutputs["U"].values)):
		myFile.write(str(tmpExportValue[node].data[1])+'\n')
	myFile.close()
	print "U2 EXPORTED"

	if len(tmpExportValue[0].data) == 3:
		print "EXPORTING U3"
		myFile = open(modelPath+'U3.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs["U"].values
		for node in range(len(odb.steps[step].frames[frame].fieldOutputs["U"].values)):
			myFile.write(str(tmpExportValue[node].data[2])+'\n')
		myFile.close()
		print "U3 EXPORTED"
	print "U EXPORTED"
	print " "

	print "EXPORTING SCALE FACTOR"
	session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF, ))
	myFile = open(modelPath+'scale_factor.txt','w')
	myFile.write(str(session.viewports["Viewport: 1"].odbDisplay.commonOptions.autoDeformationScaleValue))
	myFile.close()
	print "SCALE FACTOR EXPORTED"
	print " "


	print "EXPORTING ELEMENTS"
	myFile = open(modelPath+'ELEMENTS.txt','w')

#OFFSET
	offset = 0
	elementOffset = 0
	nodesListTmp = []
	if len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes) > 1:
		offset = len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes[0])
	offset = 0 #OFFSET DO ZMIANY
	
	elementsIndexesList = []

	if setName != " ALL ELEMENTS" and instanceName == "":
		instanceKeyList = odb.rootAssembly.instances.keys()
		tmpOffsetCounter = instanceKeyList.index(odb.rootAssembly.elementSets[setName].instanceNames[0])
		for i in range(tmpOffsetCounter):
			offset += len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes[i])
			elementOffset += len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[i])
	elif instanceName != "":
		instanceKeyList = odb.rootAssembly.instances.keys()
		tmpOffsetCounter = instanceKeyList.index(instanceName)
		for i in range(tmpOffsetCounter):
			offset += len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes[i])
			elementOffset += len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[i])
	
	if setName != " ALL ELEMENTS" and instanceName == "":
		for i in range(len(odb.rootAssembly.elementSets[setName].elements[0])):
			nodesListTmp.append(odb.rootAssembly.elementSets[setName].elements[0][i].connectivity[0] + offset - 1)
			nodesListTmp.append(odb.rootAssembly.elementSets[setName].elements[0][i].connectivity[1] + offset - 1)
			nodesListTmp.append(odb.rootAssembly.elementSets[setName].elements[0][i].connectivity[2] + offset - 1)
			nodesListTmp.append(odb.rootAssembly.elementSets[setName].elements[0][i].connectivity[3] + offset - 1)
	elif instanceName != "":
		for i in range(len(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements)):
			nodesListTmp.append(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements[i].connectivity[0] + offset - 1)
			nodesListTmp.append(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements[i].connectivity[1] + offset - 1)
			nodesListTmp.append(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements[i].connectivity[2] + offset - 1)
			nodesListTmp.append(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements[i].connectivity[3] + offset - 1)
	nodesList = removeRedundant(nodesListTmp)

	if instanceName != "":
		loopRange = 1#len(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements)
	else:
		loopRange = len(odb.rootAssembly.elementSets[setName].elements)

	for i in range(loopRange):
		if instanceName == "":
			tmpExportValue = odb.rootAssembly.elementSets[setName].elements[i]
			elementsCounter = len(odb.rootAssembly.elementSets[setName].elements[i])
		else:
			tmpExportValue = odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements
			elementsCounter = len(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements)
		for element in range(elementsCounter):
			if len(tmpExportValue[element].connectivity) == 3:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + '\n')
			elif len(tmpExportValue[element].connectivity) == 4:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[3] - 1 + offset) + '\n')
			elif len(tmpExportValue[element].connectivity) == 6:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[3] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[4] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[5] - 1 + offset) + '\n')
			elif len(tmpExportValue[element].connectivity) == 8:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[3] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[4] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[5] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[6] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[7] - 1 + offset) + '\n')
			elif len(tmpExportValue[element].connectivity) == 10:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[3] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[4] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[5] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[6] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[7] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[8] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[9] - 1 + offset) + '\n')
			elif len(tmpExportValue[element].connectivity) == 10:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[3] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[4] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[5] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[6] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[7] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[8] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[9] - 1 + offset) + '\n')
			elif len(tmpExportValue[element].connectivity) == 12:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[3] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[4] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[5] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[6] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[7] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[8] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[9] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[10] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[11] - 1 + offset) + '\n')
			elif len(tmpExportValue[element].connectivity) == 20:
				myFile.write(str(tmpExportValue[element].connectivity[0] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[1] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[2] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[3] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[4] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[5] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[6] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[7] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[8] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[9] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[10] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[11] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[12] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[13] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[14] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[15] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[16] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[17] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[18] - 1 + offset) + ' ' +
				str(tmpExportValue[element].connectivity[19] - 1 + offset) + '\n')
			elementsIndexesList.append(tmpExportValue[element].label + elementOffset - 1)
		offset += len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes[i])
	myFile.close()
	print "ELEMENTS EXPORTED"
	print " "
##############################################################
#######values exporter
##############################################################
	fieldOutputsKeys = odb.steps[step].frames[frame].fieldOutputs.keys()
	for fieldOutput in range(len(fieldOutputsKeys)):
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].elementLabel) == "None":
			elementValue = False
		else:
			elementValue = True
		arrayLength = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values)
		try:  
			os.makedirs(fileName+fieldOutputsKeys[fieldOutput])  
		except OSError as error:
			error

		print "STARTING EXPORTING "+fieldOutputsKeys[fieldOutput]
		if len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels) > 0:
			if setName == " ALL ELEMENTS":
				for componentLabel in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels)):
					print "EXPORTING "+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]
					myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\'+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+'.txt','w')
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(arrayLength):
						myFile.write(str(tmpExportValue[value].data[componentLabel]) + '\n')
					if elementValue:
						myFile.write("ELEMENT")
					else:
						myFile.write("NODAL")
					print odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+" EXPORTED"
				myFile.close()
			elif setName != "" or instanceName != "":
				if elementValue:
					for componentLabel in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels)):
						print "EXPORTING "+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]
						myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\'+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+'.txt','w')
						tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
						for value in range(len(elementsIndexesList)):
							myFile.write(str(tmpExportValue[elementsIndexesList[value]].data[componentLabel]) + '\n')
						myFile.write("ELEMENT")
						print odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+" EXPORTED"
						myFile.close()
				else:
					nodeCounterTmp = 0
					for componentLabel in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels)):
						print "EXPORTING "+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]
						myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\'+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+'.txt','w')
						tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
						for value in range(len(tmpExportValue)):
							if value == nodesList[nodeCounterTmp]:
								myFile.write(str(tmpExportValue[value].data[componentLabel]) + '\n')
								nodeCounterTmp+=1
								if nodeCounterTmp == len(nodesList):
									break
							else:
								myFile.write('None\n')
						nodeCounterTmp = 0
						myFile.write("NODAL")
						print odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+" EXPORTED"
						myFile.close()

		else:
			print "EXPORTING "+ fieldOutputsKeys[fieldOutput]
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\value.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].data) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
				print fieldOutputsKeys[fieldOutput]+" EXPORTED"
				myFile.close()
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].data) + '\n')
					myFile.write("ELEMENT")
					print fieldOutputsKeys[fieldOutput]+" EXPORTED"
					myFile.close()
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].data) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
					print fieldOutputsKeys[fieldOutput]+" EXPORTED"
					myFile.close()
#INV3
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].inv3) != "None":
			print "EXPORTING INV3"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\inv3.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].inv3) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].inv3) + '\n')
						myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].inv3) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "INV3 EXPORTED"
#MAGNITUDE
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].magnitude) != "None":
			print "EXPORTING MAGNITUDE"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\magnitude.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].magnitude) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].magnitude) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].magnitude) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "MAGNITUDE EXPORTED"
#MAX_IN_PLAIN_PRINCIPAL
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].maxInPlanePrincipal) != "None":
			print "EXPORTING MAX_IN_PLAIN_PRINCIPAL"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\maxInPlanePrincipal.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].maxInPlanePrincipal) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].maxInPlanePrincipal) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].maxInPlanePrincipal) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "MAX_IN_PLAIN_PRINCIPAL EXPORTED"
#MIN_IN_PLAIN_PRINCIPAL
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].minInPlanePrincipal) != "None":
			print "EXPORTING MIN_IN_PLAIN_PRINCIPAL"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\minInPlanePrincipal.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].minInPlanePrincipal) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].minInPlanePrincipal) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].minInPlanePrincipal) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "MIN_IN_PLAIN_PRINCIPAL EXPORTED"
#OUT_OF_PLAIN_PRINCIPAL
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].outOfPlanePrincipal) != "None":
			print "EXPORTING OUT_OF_PLAIN_PRINCIPAL"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\outOfPlanePrincipal.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].outOfPlanePrincipal) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].outOfPlanePrincipal) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].outOfPlanePrincipal) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "OUT_OF_PLAIN_PRINCIPAL EXPORTED"
#MAX_PRINCIPAL
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].maxPrincipal) != "None":
			print "EXPORTING MAX_PRINCIPAL"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\maxPrincipal.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].maxPrincipal) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].maxPrincipal) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].maxPrincipal) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "MAX_PRINCIPAL EXPORTED"
#MID_PRINCIPAL
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].midPrincipal) != "None":
			print "EXPORTING MID_PRINCIPAL"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\midPrincipal.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].midPrincipal) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].midPrincipal) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].midPrincipal) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "MID_PRINCIPAL EXPORTED"
#MIN_PRINCIPAL
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].minPrincipal) != "None":
			print "EXPORTING MIN_PRINCIPAL"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\minPrincipal.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].minPrincipal) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].minPrincipal) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].minPrincipal) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "MIN_PRINCIPAL EXPORTED"
#MISES
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].mises) != "None":
			print "EXPORTING MISES"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\mises.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].mises) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].mises) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].mises) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "MISES EXPORTED"
#PRESS
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].press) != "None":
			print "EXPORTING PRESS"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\press.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].press) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].press) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].press) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "PRESS EXPORTED"
#TRESCA
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].tresca) != "None":
			print "EXPORTING TRESCA"
			myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\tresca.txt','w')
			if setName == " ALL ELEMENTS":
				tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
				for value in range(arrayLength):
					myFile.write(str(tmpExportValue[value].tresca) + '\n')
				if elementValue:
					myFile.write("ELEMENT")
				else:
					myFile.write("NODAL")
			elif setName != "" or instanceName != "":
				if elementValue:
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(elementsIndexesList)):
						myFile.write(str(tmpExportValue[elementsIndexesList[value]].tresca) + '\n')
					myFile.write("ELEMENT")
				else:
					nodeCounterTmp = 0
					tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
					for value in range(len(tmpExportValue)):
						if value == nodesList[nodeCounterTmp]:
							myFile.write(str(tmpExportValue[value].tresca) + '\n')
							nodeCounterTmp+=1
							if nodeCounterTmp == len(nodesList):
								break
						else:
							myFile.write('None\n')
					nodeCounterTmp = 0
					myFile.write("NODAL")
			myFile.close()
			print "TRESCA EXPORTED"

		print fieldOutputsKeys[fieldOutput]+" EXPORTED"
		print " "

##############################################################
#######end of exporter
##############################################################
	end = time.time()
	print "EXPORT TOOK " + str(end - start) + "s"

##############################################################
#######parsers
##############################################################
def parseToFrames(string):
	frameList = []
	if string == "":
		return frameList
	tmp = ""
	counter = 0
	lastSign = "-"
	for i in string:
		if i == ",":
			lastSign = ","
		if i == "-":
			lastSign = "-"

	if lastSign == "-":
		string += ","

	for i in range(len(string)):
		if string[counter] == ",":
			frameList.append(int(tmp))
			tmp = ""
		elif string[counter] == "-":
			tmpInt1 = int(tmp)
			tmp = ""
			for j in range(counter+1,len(string)):
				if string[j] == ",":
					tmpInt2 = int(tmp)
					tmp = ""
					counter += 1
					break
				else:
					tmp += string[j]
				counter += 1
			for j in range(tmpInt1,tmpInt2+1):
				frameList.append(j)
		else:
			tmp += string[counter]
		counter += 1
		if counter == len(string):
			break
	if tmp != "":
		frameList.append(int(tmp))
	return frameList

def removeRedundant(listTmp):
	listTmp.sort()
	listTmp2 = []
	prev = -1
	for i in range(len(listTmp)):
		if prev != listTmp[i]:
			listTmp2.append(listTmp[i])
			prev = listTmp[i]
	return listTmp2