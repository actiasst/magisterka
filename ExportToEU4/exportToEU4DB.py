# Do not edit this file or it may not load correctly
# if you try to open it with the RSG Dialog Builder.

# Note: thisDir is defined by the Activator class when
#       this file gets exec'd

from rsg.rsgGui import *
from abaqusConstants import INTEGER, FLOAT
dialogBox = RsgDialog(title='Exporter', kernelModule='executeExporter', kernelFunction='executePlugin', includeApplyBtn=False, includeSeparator=True, okBtnText='OK', applyBtnText='Apply', execDir=thisDir)
RsgVerticalFrame(name='VFrame_1', p='DialogBox', layout='LAYOUT_FILL_Y', pl=0, pr=0, pt=0, pb=0)
RsgGroupBox(name='GroupBox_1', p='VFrame_1', text='Step', layout='LAYOUT_FILL_X|LAYOUT_FILL_Y')
RsgTextField(p='GroupBox_1', fieldType='String', ncols=40, labelText=' ', keyword='stepName', default='LoadHist-1')
RsgGroupBox(name='GroupBox_2', p='VFrame_1', text='Frame', layout='LAYOUT_FILL_X|LAYOUT_FILL_Y')
RsgTextField(p='GroupBox_2', fieldType='String', ncols=40, labelText=' ', keyword='frames', default='10')
RsgGroupBox(name='GroupBox_3', p='VFrame_1', text='Set Name', layout='LAYOUT_FILL_X|LAYOUT_FILL_Y')
RsgTextField(p='GroupBox_3', fieldType='String', ncols=40, labelText=' ', keyword='setName', default='')
RsgGroupBox(name='GroupBox_4', p='VFrame_1', text='Instance Name', layout='LAYOUT_FILL_X|LAYOUT_FILL_Y')
RsgTextField(p='GroupBox_4', fieldType='String', ncols=40, labelText=' ', keyword='instanceName', default='')
RsgGroupBox(name='GroupBox_9', p='VFrame_1', text='Instance Set name', layout='LAYOUT_FILL_X')
RsgTextField(p='GroupBox_9', fieldType='String', ncols=40, labelText=' ', keyword='instanceSetName', default='')
RsgGroupBox(name='GroupBox_7', p='VFrame_1', text='Folder Path', layout='LAYOUT_FILL_X')
RsgTextField(p='GroupBox_7', fieldType='String', ncols=40, labelText=' ', keyword='folderPath', default='skrypty\\magisterka')
RsgGroupBox(name='GroupBox_5', p='VFrame_1', text='Folder Name', layout='LAYOUT_FILL_X|LAYOUT_FILL_Y')
RsgTextField(p='GroupBox_5', fieldType='String', ncols=40, labelText=' ', keyword='folderName', default='test')
RsgGroupBox(name='GroupBox_6', p='VFrame_1', text='File Name', layout='LAYOUT_FILL_Y')
RsgFileTextField(p='GroupBox_6', ncols=40, labelText=' ', keyword='fileName', default='E:/Abaqus/3Dmodels/DP_100x100x100_Ferrite67_Martensite33-E11.odb', patterns='Odb(*.odb)')
dialogBox.show()