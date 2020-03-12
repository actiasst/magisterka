##############################################################
#######esential functions
##############################################################

def addVertex(x,y,z):
	myFile.write('v ' + str(x)+ ' ' + str(y) + ' ' + str(z) + '\n')

def addTriangle(v1,v2,v3):
	myFile.write('f ' + str(v1)+ ' ' + str(v2) + ' ' + str(v3) + '\n')

def addTexture(u1):
	myFile.write('u ' + str(u1) + '\n')

def exportCOORD(step,frame,node):
	addVertex(odb.steps[step].frames[frame].fieldOutputs["COORD"].values[node].data[0], odb.steps[step].frames[frame].fieldOutputs["COORD"].values[node].data[1], odb.steps[step].frames[frame].fieldOutputs["COORD"].values[node].data[2])

def exportU(step,frame,node,orientation):
	myFile.write(str(odb.steps[step].frames[frame].fieldOutputs["U"].values[node].data[orientation])+'\n')

##############################################################
#######actual exporter
##############################################################
import time
import visualization


print " "
print " "
print " "
start = time.time()
step = "Apply Load"
fileName = 'skrypty\\magisterka\\exported\\'
frame = 1
nodesCounter = len(odb.steps[step].frames[frame].fieldOutputs["COORD"].values)

print "STARTING EXPORTING"

print "STARTING EXPORTING COORD"
myFile = open(fileName+'COORD.txt','w')
for node in range(nodesCounter):
	exportCOORD(step,frame,node)
myFile.close()
print "COORD EXPORTED"
print " "

print "STARTING EXPORTING U"
print "EXPORTING U1"
myFile = open(fileName+'U1.txt','w')
for node in range(nodesCounter):
	exportU(step,frame,node,0)
myFile.close()
print "U1 EXPORTED"

print "EXPORTING U2"
myFile = open(fileName+'U2.txt','w')
for node in range(nodesCounter):
	exportU(step,frame,node,1)
myFile.close()
print "U2 EXPORTED"

print "EXPORTING U3"
myFile = open(fileName+'U3.txt','w')
for node in range(nodesCounter):
	exportU(step,frame,node,2)
myFile.close()
print "U3 EXPORTED"
print "U EXPORTED"
print " "

print "EXPORTING SCALE FACTOR"
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF, ))
myFile = open(fileName+'scale_factor.txt','w')
myFile.write(str(session.viewports["Viewport: 1"].odbDisplay.commonOptions.autoDeformationScaleValue))
myFile.close()
print "SCALE FACTOR EXPORTED"
print " "


end = time.time()
print "EXPORT TOOK " + str(end - start) + "s"