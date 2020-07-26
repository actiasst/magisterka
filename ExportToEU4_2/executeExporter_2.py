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

def executePlugin(stepName,frames,setName,instanceName,instanceSetName,folderPath,folderName,fileName,fieldOutput,value,min,max):
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
		exportModel(stepName, frame, setName, instanceName, instanceSetName, folderPath, odb, fieldOutput, value, min, max)
	stopTotal = time.time()
	print "TOTAL EXPORT TIME " + str(stopTotal - startTotal) + "s"
##############################################################
#######model exporter
##############################################################

def exportModel(step, frame, setName, instanceName, instanceSetName, fileName, odb, fieldOutput, value, min, max):
	start = time.time()
	fileName += "\\"
	fileName += str(frame)
	fileName += "\\"

	print "STARTING EXPORTING"

	modelPath = fileName + "model\\"
	try:  
		os.makedirs(modelPath)
	except OSError as error:
		error
	
	elementsInstancesNames = []
	elementsOffsetTable = {}
	nodesInstancesNames = []
	nodesOffsetTable = {}
	initiateFunction(odb, step, frame, elementsInstancesNames, elementsOffsetTable, nodesInstancesNames, nodesOffsetTable)

	exportScaleFactor(modelPath)
	exportCOORD(odb, modelPath, nodesInstancesNames, step, frame)
	exportU(odb, modelPath, step, frame)
	if fieldOutput != "":
		nodesElementsTab = exportFieldoutputFromRange(odb, modelPath, elementsInstancesNames, elementsOffsetTable, nodesOffsetTable, fieldOutput, value, min, max, step, frame)
		exportSet(odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable, nodesElementsTab)
	elif instanceName != "":
		nodesElementsTab = exportInstanceSetElements(odb, modelPath, elementsInstancesNames, nodesOffsetTable, instanceName, instanceSetName, elementsOffsetTable, step, frame)
		exportSet(odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable, nodesElementsTab)
	elif setName != "":
		nodesElementsTab = exportSetElements(odb, modelPath, elementsInstancesNames, nodesOffsetTable, setName, elementsOffsetTable, step, frame)
		exportSet(odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable, nodesElementsTab)
	else:
		exportElements(odb, modelPath, elementsInstancesNames, nodesOffsetTable)
		exportValues(odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable)

	
##############################################################
#######end of exporter
##############################################################
	end = time.time()
	print "EXPORT TOOK " + str(end - start) + "s"

##############################################################
#######functions
##############################################################
def initiateFunction(odb, step, frame, elementsInstancesNames, elementsOffsetTable, nodesInstancesNames, nodesOffsetTable):
	values = odb.steps[step].frames[frame].fieldOutputs["S"].values
	for i in range(len(odb.steps[step].frames[frame].fieldOutputs["S"].values)):
		if values[i].elementLabel == 1 and values[i].integrationPoint == 1:
			if str(values[i].instance) != "None":
				elementsOffsetTable[values[i].instance.name] = i-1
				elementsInstancesNames.append(values[i].instance.name)

	values = odb.steps[step].frames[frame].fieldOutputs["U"].values
	for i in range(len(odb.steps[step].frames[frame].fieldOutputs["U"].values)):
		if values[i].nodeLabel == 1:
			if str(values[i].instance) != "None":
				nodesOffsetTable[values[i].instance.name] = i-1
				nodesInstancesNames.append(values[i].instance.name)
			else:
				nodesOffsetTable[""] = i-1
				nodesInstancesNames.append("")

def exportScaleFactor(modelPath):
	session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF, ))
	myFile = open(modelPath+'scale_factor.txt','w')
	myFile.write(str(session.viewports["Viewport: 1"].odbDisplay.commonOptions.autoDeformationScaleValue))
	myFile.close()

def exportCOORD(odb, modelPath, nodesInstancesNames, step, frame):
	myFile = open(modelPath+'COORD.txt','w')
	for j in range(len(nodesInstancesNames)):
		if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
			nodes = odb.rootAssembly.instances[nodesInstancesNames[j]].nodes
			for k in range(len(odb.rootAssembly.instances[nodesInstancesNames[j]].nodes)):
				myFile.write(str(nodes[k].coordinates[0]) + " " + str(nodes[k].coordinates[1]) + " " + str(nodes[k].coordinates[2]) + "\n")
		else:
			nodes = odb.rootAssembly.instances[nodesInstancesNames[j]].nodes
			for k in range(len(odb.rootAssembly.instances[nodesInstancesNames[j]].nodes)):
				myFile.write(str(nodes[k].coordinates[0]) + " " + str(nodes[k].coordinates[1]) + "\n")
	myFile.close()

def exportElements(odb, modelPath, elementsInstancesNames, nodesOffsetTable):
	myFile = open(modelPath+'ELEMENTS.txt','w')
	for i in range(len(elementsInstancesNames)):
		for j in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements)):
			if odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j][0].instanceNames[0] == elementsInstancesNames[i]:
				elements = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j]
				for k in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j])):
					for x in range(len(elements[k].connectivity)):
						myFile.write(str(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]) + " ")
					myFile.write("\n")
				break
	myFile.close()

def exportFieldoutputFromRange(odb, modelPath, elementsInstancesNames, elementsOffsetTable, nodesOffsetTable, fieldOutput, valueName, min, max, step, frame):
	tab = []
	tab.append([])
	tab.append([])
	if valueName == "value":
		index = -1
	elif valueName == "inv3":
		index = -2
	elif valueName == "magnitude":
		index = -3
	elif valueName == "maxInPlanePrincipal":
		index = -4
	elif valueName == "maxPrincipal":
		index = -5
	elif valueName == "midPrincipal":
		index = -6
	elif valueName == "minInPlanePrincipal":
		index = -7
	elif valueName == "minPrincipal":
		index = -8
	elif valueName == "mises":
		index = -9
	elif valueName == "outOfPlanePrincipal":
		index = -10
	elif valueName == "press":
		index = -11
	elif valueName == "tresca":
		index = -12
	else:
		index = odb.steps[step].frames[frame].fieldOutputs[fieldOutput].componentLabels.index(valueName)
	value = odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values
	if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
		dimension = 3
	else:
		dimension = 2
	myFile = open(modelPath+'ELEMENTS.txt','w')
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[0].elementLabel) != "None":
		for i in range(len(elementsInstancesNames)):
			elementOffset = elementsOffsetTable[elementsInstancesNames[i]]
			for j in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements)):
				if odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j][0].instanceNames[0] == elementsInstancesNames[i]:
					elements = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j]
					for k in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j])):
						if dimension == 2 and len(elements[k].connectivity) == 6:
							amountCounter = 3
						elif dimension == 2 and len(elements[k].connectivity) == 8:
							amountCounter = 4
						elif dimension == 3 and len(elements[k].connectivity) == 10:
							amountCounter = 6
						elif dimension == 3 and len(elements[k].connectivity) == 20:
							amountCounter = 8
						else:
							amountCounter = 1
						tmpValue = 0
						if index >= 0:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].data[index]
						elif index == -1:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].data
						elif index == -2:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].inv3
						elif index == -3:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].magnitude
						elif index == -4:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].maxInPlanePrincipal
						elif index == -5:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].maxPrincipal
						elif index == -6:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].midPrincipal
						elif index == -7:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].minInPlanePrincipal
						elif index == -8:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].minPrincipal
						elif index == -9:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].mises
						elif index == -10:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].outOfPlanePrincipal
						elif index == -11:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].press
						elif index == -12:
							for y in range(amountCounter):
								tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].tresca
						tmpValue /= amountCounter
						if tmpValue >= min:
							if tmpValue <= max:
								for z in range(amountCounter):
									tab[1].append((elements[k].label + elementOffset)*amountCounter + z)
								for x in range(len(elements[k].connectivity)):
									myFile.write(str(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]) + " ")
									tab[0].append(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]])
								myFile.write("\n")
					break
	else:
		for i in range(len(elementsInstancesNames)):
			elementOffset = elementsOffsetTable[elementsInstancesNames[i]]
			for j in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements)):
				if odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j][0].instanceNames[0] == elementsInstancesNames[i]:
					elements = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j]
					for k in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j])):
						if dimension == 2 and len(elements[k].connectivity) == 6:
							amountCounter = 3
						elif dimension == 2 and len(elements[k].connectivity) == 8:
							amountCounter = 4
						elif dimension == 3 and len(elements[k].connectivity) == 10:
							amountCounter = 6
						elif dimension == 3 and len(elements[k].connectivity) == 20:
							amountCounter = 8
						else:
							amountCounter = 1
						condition = False
						if index >= 0:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data[index] >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data[index] <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -1:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -2:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].inv3 >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].inv3 <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -3:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].magnitude >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].magnitude <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -4:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxInPlanePrincipal >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxInPlanePrincipal <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -5:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxPrincipal >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxPrincipal <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -6:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].midPrincipal >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].midPrincipal <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -7:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minInPlanePrincipal >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minInPlanePrincipal <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -8:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minPrincipal >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minPrincipal <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -9:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].mises >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].mises <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -10:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].outOfPlanePrincipal >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].outOfPlanePrincipal <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -11:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].press >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].press <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						elif index == -12:
							for x in range(len(elements[k].connectivity)):
								if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].tresca >= min:
									if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].tresca <= max:
										condition = True
									else:
										condition = False
										break
								else:
									condition = False
									break
						if condition:
							for z in range(amountCounter):
								tab[1].append((elements[k].label + elementOffset)*amountCounter + z)
							for x in range(len(elements[k].connectivity)):
								myFile.write(str(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]) + " ")
								tab[0].append(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]])
							myFile.write("\n")
					break
	myFile.close()
	tab[0] = removeRedundant(tab[0])
	tab[1] = removeRedundant(tab[1])
	return tab

def exportSetElements(odb, modelPath, elementsInstancesNames, nodesOffsetTable, setName, elementsOffsetTable, step, frame):
	tab = []
	tab.append([])
	tab.append([])
	myFile = open(modelPath+'ELEMENTS.txt','w')
	elements = odb.rootAssembly.elementSets[setName].elements[0]
	if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
		for i in range(len(odb.rootAssembly.elementSets[setName].elements[0])):
			for x in range(len(elements[i].connectivity)):
				myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
				tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
			myFile.write("\n")
			if len(elements[i].connectivity) == 20:
				for j in range(8):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*8 + j)
			elif len(elements[i].connectivity) == 10:
				for j in range(6):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*6 + j)
			else:
				tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
	else:
		for i in range(len(odb.rootAssembly.elementSets[setName].elements[0])):
			for x in range(len(elements[i].connectivity)):
				myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
				tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
			myFile.write("\n")
			if len(elements[i].connectivity) == 8:
				for j in range(4):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*4 + j)
			elif len(elements[i].connectivity) == 6:
				for j in range(3):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*3 + j)
			else:
				tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
	myFile.close()
	tab[0] = removeRedundant(tab[0])
	tab[1] = removeRedundant(tab[1])
	return tab

def exportInstanceSetElements(odb, modelPath, elementsInstancesNames, nodesOffsetTable, instanceName, instanceSetName, elementsOffsetTable, step, frame):
	tab = []
	tab.append([])
	tab.append([])
	myFile = open(modelPath+'ELEMENTS.txt','w')
	elements = odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements
	if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
		for i in range(len(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements)):
			for x in range(len(elements[i].connectivity)):
				myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
				tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
			myFile.write("\n")
			if len(elements[i].connectivity) == 20:
				for j in range(8):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*8 + j)
			elif len(elements[i].connectivity) == 10:
				for j in range(6):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*6 + j)
			else:
				tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
	else:
		for i in range(len(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements)):
			for x in range(len(elements[i].connectivity)):
				myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
				tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
			myFile.write("\n")
			if len(elements[i].connectivity) == 8:
				for j in range(4):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*4 + j)
			elif len(elements[i].connectivity) == 6:
				for j in range(3):
					tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*3 + j)
			else:
				tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
	myFile.close()
	tab[0] = removeRedundant(tab[0])
	tab[1] = removeRedundant(tab[1])
	return tab

def exportU(odb, modelPath, step, frame):
	values = odb.steps[step].frames[frame].fieldOutputs["U"].values
	if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
		myFile1 = open(modelPath+'U1.txt','w')
		myFile2 = open(modelPath+'U2.txt','w')
		myFile3 = open(modelPath+'U3.txt','w')
		for i in range(len(odb.steps[step].frames[frame].fieldOutputs["U"].values)):
			myFile1.write(str(values[i].data[0]) + "\n")
			myFile2.write(str(values[i].data[1]) + "\n")
			myFile3.write(str(values[i].data[2]) + "\n")
		myFile1.close()
		myFile2.close()
		myFile3.close()
	else:

		myFile1 = open(modelPath+'U1.txt','w')
		myFile2 = open(modelPath+'U2.txt','w')
		for i in range(len(odb.steps[step].frames[frame].fieldOutputs["U"].values)):
			myFile1.write(str(values[i].data[0]) + "\n")
			myFile2.write(str(values[i].data[1]) + "\n")
		myFile1.close()
		myFile2.close()

def exportValues(odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable):
	tabFilesHandler = []
	fieldOutputKeys = odb.steps[step].frames[frame].fieldOutputs.keys()
	for i in range(len(fieldOutputKeys)):
		try:  
			os.makedirs(fileName + fieldOutputKeys[i])
		except OSError as error:
			error
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values[0].elementLabel) != "None":
			fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
			for j in range(len(fieldOutputComponentLabelsKeys)):
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".txt",'w')
				for k in range(len(elementsInstancesNames)):
					index = elementsOffsetTable[elementsInstancesNames[k]]
					if k != len(elementsInstancesNames) - 1:
						size = elementsOffsetTable[elementsInstancesNames[k+1]] - index
					else:
						size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values) - index - 1
					values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
					offset = elementsOffsetTable[elementsInstancesNames[k]] + 1
					for x in range(size):
						myFile.write(str(values[x + offset].data[j]) + "\n")
				myFile.write("ELEMENT")
				myFile.close()
			if len(fieldOutputComponentLabelsKeys) == 0:
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.txt",'w')
				for k in range(len(elementsInstancesNames)):
					index = elementsOffsetTable[elementsInstancesNames[k]]
					if k != len(elementsInstancesNames) - 1:
						size = elementsOffsetTable[elementsInstancesNames[k+1]] - index
					else:
						size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values) - index - 1
					values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
					offset = elementsOffsetTable[elementsInstancesNames[k]] + 1
					for x in range(size):
						myFile.write(str(values[x + offset].data) + "\n")
				myFile.write("ELEMENT")
				myFile.close()
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.txt","w"))
			for k in range(len(elementsInstancesNames)):
				index = elementsOffsetTable[elementsInstancesNames[k]]
				if k != len(elementsInstancesNames) - 1:
					size = elementsOffsetTable[elementsInstancesNames[k+1]] - index
				else:
					size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values) - index - 1
				values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
				offset = elementsOffsetTable[elementsInstancesNames[k]] + 1
				for x in range(size):
					tabFilesHandler[0].write(str(values[x + offset].inv3) + "\n")
					tabFilesHandler[1].write(str(values[x + offset].magnitude) + "\n")
					tabFilesHandler[2].write(str(values[x + offset].maxInPlanePrincipal) + "\n")
					tabFilesHandler[3].write(str(values[x + offset].maxPrincipal) + "\n")
					tabFilesHandler[4].write(str(values[x + offset].midPrincipal) + "\n")
					tabFilesHandler[5].write(str(values[x + offset].minInPlanePrincipal) + "\n")
					tabFilesHandler[6].write(str(values[x + offset].minPrincipal) + "\n")
					tabFilesHandler[7].write(str(values[x + offset].mises) + "\n")
					tabFilesHandler[8].write(str(values[x + offset].outOfPlanePrincipal) + "\n")
					tabFilesHandler[9].write(str(values[x + offset].press) + "\n")
					tabFilesHandler[10].write(str(values[x + offset].tresca) + "\n")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].write("ELEMENT")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].close()
			tabFilesHandler = []
		else:
			fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
			for j in range(len(fieldOutputComponentLabelsKeys)):
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".txt",'w')
				size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)
				values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
				for x in range(size):
					myFile.write(str(values[x].data[j]) + "\n")
				myFile.write("NODAL")
				myFile.close()
			if len(fieldOutputComponentLabelsKeys) == 0:
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.txt",'w')
				size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)
				values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
				for x in range(size):
					myFile.write(str(values[x].data) + "\n")
				myFile.write("NODAL")
				myFile.close()
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.txt","w"))
			size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)
			values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
			for x in range(size):
				tabFilesHandler[0].write(str(values[x].inv3) + "\n")
				tabFilesHandler[1].write(str(values[x].magnitude) + "\n")
				tabFilesHandler[2].write(str(values[x].maxInPlanePrincipal) + "\n")
				tabFilesHandler[3].write(str(values[x].maxPrincipal) + "\n")
				tabFilesHandler[4].write(str(values[x].midPrincipal) + "\n")
				tabFilesHandler[5].write(str(values[x].minInPlanePrincipal) + "\n")
				tabFilesHandler[6].write(str(values[x].minPrincipal) + "\n")
				tabFilesHandler[7].write(str(values[x].mises) + "\n")
				tabFilesHandler[8].write(str(values[x].outOfPlanePrincipal) + "\n")
				tabFilesHandler[9].write(str(values[x].press) + "\n")
				tabFilesHandler[10].write(str(values[x].tresca) + "\n")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].write("NODAL")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].close()
			tabFilesHandler = []

def exportSet(odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable, nodesElementsTab):
	if len(nodesElementsTab[0]) == 0:
		print "DID NOT FIND ANY SUITABLE ELEMENTS"
		return 0
	tabFilesHandler = []
	fieldOutputKeys = odb.steps[step].frames[frame].fieldOutputs.keys()
	for i in range(len(fieldOutputKeys)):
		try:  
			os.makedirs(fileName + fieldOutputKeys[i])
		except OSError as error:
			error
		if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values[0].elementLabel) != "None":
			fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
			for j in range(len(fieldOutputComponentLabelsKeys)):
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".txt",'w')
				values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
				for x in range(len(nodesElementsTab[1])):
					myFile.write(str(values[nodesElementsTab[1][x]].data[j]) + "\n")
				myFile.write("ELEMENT")
				myFile.close()
			if len(fieldOutputComponentLabelsKeys) == 0:
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.txt",'w')
				values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
				for x in range(len(nodesElementsTab[1])):
					myFile.write(str(values[nodesElementsTab[1][x]].data) + "\n")
				myFile.write("ELEMENT")
				myFile.close()
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.txt","w"))
			values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
			for x in range(len(nodesElementsTab[1])):
					tabFilesHandler[0].write(str(values[nodesElementsTab[1][x]].inv3) + "\n")
					tabFilesHandler[1].write(str(values[nodesElementsTab[1][x]].magnitude) + "\n")
					tabFilesHandler[2].write(str(values[nodesElementsTab[1][x]].maxInPlanePrincipal) + "\n")
					tabFilesHandler[3].write(str(values[nodesElementsTab[1][x]].maxPrincipal) + "\n")
					tabFilesHandler[4].write(str(values[nodesElementsTab[1][x]].midPrincipal) + "\n")
					tabFilesHandler[5].write(str(values[nodesElementsTab[1][x]].minInPlanePrincipal) + "\n")
					tabFilesHandler[6].write(str(values[nodesElementsTab[1][x]].minPrincipal) + "\n")
					tabFilesHandler[7].write(str(values[nodesElementsTab[1][x]].mises) + "\n")
					tabFilesHandler[8].write(str(values[nodesElementsTab[1][x]].outOfPlanePrincipal) + "\n")
					tabFilesHandler[9].write(str(values[nodesElementsTab[1][x]].press) + "\n")
					tabFilesHandler[10].write(str(values[nodesElementsTab[1][x]].tresca) + "\n")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].write("ELEMENT")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].close()
			tabFilesHandler = []

		else:
			fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
			for j in range(len(fieldOutputComponentLabelsKeys)):
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".txt",'w')
				values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
				tmpIndex = 0
				maxIndex = len(nodesElementsTab[0])
				for k in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)):
					if k == nodesElementsTab[0][tmpIndex]:
						myFile.write(str(values[k].data[j]) + "\n")
						tmpIndex += 1
						if tmpIndex == maxIndex:
							tmpIndex = 0
					else:
						myFile.write("None\n")
				myFile.write("NODAL")
				myFile.close()
			if len(fieldOutputComponentLabelsKeys) == 0:
				myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.txt",'w')
				values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
				tmpIndex = 0
				maxIndex = len(nodesElementsTab[0])
				for k in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)):
					if k == nodesElementsTab[0][tmpIndex]:
						myFile.write(str(values[k].data) + "\n")
						tmpIndex += 1
						if tmpIndex == maxIndex:
							tmpIndex = 0
					else:
						myFile.write("None\n")
				myFile.write("NODAL")
				myFile.close()
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.txt","w"))
			tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.txt","w"))
			values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
			tmpIndex = 0
			maxIndex = len(nodesElementsTab[0])
			for k in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)):
				if k == nodesElementsTab[0][tmpIndex]:
					tabFilesHandler[0].write(str(values[k].inv3) + "\n")
					tabFilesHandler[1].write(str(values[k].magnitude) + "\n")
					tabFilesHandler[2].write(str(values[k].maxInPlanePrincipal) + "\n")
					tabFilesHandler[3].write(str(values[k].maxPrincipal) + "\n")
					tabFilesHandler[4].write(str(values[k].midPrincipal) + "\n")
					tabFilesHandler[5].write(str(values[k].minInPlanePrincipal) + "\n")
					tabFilesHandler[6].write(str(values[k].minPrincipal) + "\n")
					tabFilesHandler[7].write(str(values[k].mises) + "\n")
					tabFilesHandler[8].write(str(values[k].outOfPlanePrincipal) + "\n")
					tabFilesHandler[9].write(str(values[k].press) + "\n")
					tabFilesHandler[10].write(str(values[k].tresca) + "\n")
					tmpIndex += 1
					if tmpIndex == maxIndex:
						tmpIndex = 0
				else:
					tabFilesHandler[0].write("None\n")
					tabFilesHandler[1].write("None\n")
					tabFilesHandler[2].write("None\n")
					tabFilesHandler[3].write("None\n")
					tabFilesHandler[4].write("None\n")
					tabFilesHandler[5].write("None\n")
					tabFilesHandler[6].write("None\n")
					tabFilesHandler[7].write("None\n")
					tabFilesHandler[8].write("None\n")
					tabFilesHandler[9].write("None\n")
					tabFilesHandler[10].write("None\n")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].write("NODAL")
			for j in range(len(tabFilesHandler)):
				tabFilesHandler[j].close()
			tabFilesHandler = []

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

##############################################################
#######validators
##############################################################
def checkIfElementIsValidInv3(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].inv3 >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].inv3 <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidMagnitude(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].magnitude >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].magnitude <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidMaxInPlanePrincipal(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].maxInPlanePrincipal >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].maxInPlanePrincipal <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidMaxPrincipal(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].maxPrincipal >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].maxPrincipal <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidMidPrincipal(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].midPrincipal >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].midPrincipal <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidMinInPlanePrincipal(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].minInPlanePrincipal >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].minInPlanePrincipal <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidMinPrincipal(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].minPrincipal >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].minPrincipal <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidOutOfPlanePrincipal(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].outOfPlanePrincipal >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].outOfPlanePrincipal <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidPress(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].press >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].press <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidTresca(min,max,fieldOutput,step,frame,i):
	if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].tresca >= min:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].tresca <= max:
			return True
		else:
			return False
	else:
		return False

def checkIfElementIsValidDataArray(min,max,fieldOutput,step,frame,i,j):
	if j != -1:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].data[j] >= min:
			if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].data[j] <= max:
				return True
			else:
				return False
		else:
			return False
	else:
		if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].data >= min:
			if odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[i].data <= max:
				return True
			else:
				return False
		else:
			return False
