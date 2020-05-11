##############################################################
#######esential functions
##############################################################

def addVertex(x,y,z):
	myFile.write(str(x)+ ' ' + str(y) + ' ' + str(z) + '\n')

##############################################################
#######actual exporter
#######model exporter
##############################################################
import time
import visualization


print " "
print " "
print " "
start = time.time()
step = "Step-1"
#step = "Apply Load"
fileName = 'skrypty\\magisterka\\exported\\'
try:  
    os.mkdir(fileName)  
except OSError as error:
	error
frame = 100
#frame= 1
nodesCounter = len(odb.rootAssembly.nodeSets[" ALL NODES"].nodes[0])
elementsCounter = len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[0])

print "STARTING EXPORTING"
print "STARTING EXPORTING COORD"

modelPath = fileName + "\\model\\"
try:  
    os.mkdir(modelPath)  
except OSError as error:
	error

myFile = open(modelPath+'COORD.txt','w')
tmpExportValue = odb.rootAssembly.nodeSets[" ALL NODES"].nodes[0]
for node in range(nodesCounter):
	addVertex(tmpExportValue[node].coordinates[0],tmpExportValue[node].coordinates[1],tmpExportValue[node].coordinates[2])
myFile.close()
print "COORD EXPORTED"
print " "

print "STARTING EXPORTING U"
print "EXPORTING U1"
myFile = open(modelPath+'U1.txt','w')
tmpExportValue = odb.steps[step].frames[frame].fieldOutputs["U"].values
for node in range(nodesCounter):
	myFile.write(str(tmpExportValue[node].data[0])+'\n')
myFile.close()
print "U1 EXPORTED"

print "EXPORTING U2"
myFile = open(modelPath+'U2.txt','w')
for node in range(nodesCounter):
	myFile.write(str(tmpExportValue[node].data[1])+'\n')
myFile.close()
print "U2 EXPORTED"

print "EXPORTING U3"
myFile = open(modelPath+'U3.txt','w')
for node in range(nodesCounter):
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
if len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[0][0].connectivity) == 8:
	tmpExportValue = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[0]
	for element in range(elementsCounter):
		myFile.write(str(tmpExportValue[element].connectivity[0] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[1] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[2] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[3] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[4] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[5] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[6] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[7] - 1) + '\n')
elif len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[0][0].connectivity) == 4:
	tmpExportValue = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[0]
	for element in range(elementsCounter):
		myFile.write(str(tmpExportValue[element].connectivity[0] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[1] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[2] - 1) + ' ' +
		str(tmpExportValue[element].connectivity[3] - 1) + '\n')
myFile.close()
print "ELEMENTS EXPORTED"
print " "
##############################################################
#######values exporter
##############################################################
fieldOutputsKeys = odb.steps[step].frames[frame].fieldOutputs.keys()
for fieldOutput in range(len(fieldOutputsKeys)):
	arrayLength = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values)
	try:  
		os.mkdir(fileName+fieldOutputsKeys[fieldOutput])  
	except OSError as error:
		error

	print "STARTING EXPORTING "+fieldOutputsKeys[fieldOutput]
	for componentLabel in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels)):
		print "EXPORTING "+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\'+odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+'.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].data[componentLabel]) + '\n')
		print odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].componentLabels[componentLabel]+" EXPORTED"
	myFile.close()
#INV3
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].inv3) != "None":
		print "EXPORTING INV3"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\inv3.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].inv3) + '\n')
		myFile.close()
		print "INV3 EXPORTED"
#MAGNITUDE
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].magnitude) != "None":
		print "EXPORTING MAGNITUDE"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\magnitude.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].magnitude) + '\n')
		myFile.close()
		print "MAGNITUDE EXPORTED"
#MAX_IN_PLAIN_PRINCIPAL
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].maxInPlanePrincipal) != "None":
		print "EXPORTING MAX_IN_PLAIN_PRINCIPAL"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\maxInPlanePrincipal.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].maxInPlanePrincipal) + '\n')
		myFile.close()
		print "MAX_IN_PLAIN_PRINCIPAL EXPORTED"
#MIN_IN_PLAIN_PRINCIPAL
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].minInPlanePrincipal) != "None":
		print "EXPORTING MIN_IN_PLAIN_PRINCIPAL"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\minInPlanePrincipal.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].minInPlanePrincipal) + '\n')
		myFile.close()
		print "MIN_IN_PLAIN_PRINCIPAL EXPORTED"
#OUT_OF_PLAIN_PRINCIPAL
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].outOfPlanePrincipal) != "None":
		print "EXPORTING OUT_OF_PLAIN_PRINCIPAL"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\outOfPlanePrincipal.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].outOfPlanePrincipal) + '\n')
		myFile.close()
		print "OUT_OF_PLAIN_PRINCIPAL EXPORTED"
#MAX_PRINCIPAL
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].maxPrincipal) != "None":
		print "EXPORTING MAX_PRINCIPAL"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\maxPrincipal.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].maxPrincipal) + '\n')
		myFile.close()
		print "MAX_PRINCIPAL EXPORTED"
#MID_PRINCIPAL
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].midPrincipal) != "None":
		print "EXPORTING MID_PRINCIPAL"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\midPrincipal.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].midPrincipal) + '\n')
		myFile.close()
		print "MID_PRINCIPAL EXPORTED"
#MIN_PRINCIPAL
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].minPrincipal) != "None":
		print "EXPORTING MIN_PRINCIPAL"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\minPrincipal.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].minPrincipal) + '\n')
		myFile.close()
		print "MIN_PRINCIPAL EXPORTED"
#MISES
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].mises) != "None":
		print "EXPORTING MISES"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\mises.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].mises) + '\n')
		myFile.close()
		print "MISES EXPORTED"
#PRESS
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].press) != "None":
		print "EXPORTING PRESS"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\press.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].press) + '\n')
		myFile.close()
		print "PRESS EXPORTED"
#TRESCA
	if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values[0].tresca) != "None":
		print "EXPORTING TRESCA"
		myFile = open(fileName+fieldOutputsKeys[fieldOutput]+'\\tresca.txt','w')
		tmpExportValue = odb.steps[step].frames[frame].fieldOutputs[fieldOutputsKeys[fieldOutput]].values
		for value in range(arrayLength):
			myFile.write(str(tmpExportValue[value].tresca) + '\n')
		myFile.close()
		print "TRESCA EXPORTED"

	print fieldOutputsKeys[fieldOutput]+" EXPORTED"
	print " "

##############################################################
#######end of exporter
##############################################################
end = time.time()
print "EXPORT TOOK " + str(end - start) + "s"