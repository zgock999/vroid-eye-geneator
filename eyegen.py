'''
MIT License

Copyright (c) 2020 @zgock999@mstdn.maud.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from PySide2 import QtWidgets,QtGui,QtCore
from PIL import Image,ImageDraw,ImageFilter
from PIL.ImageQt import ImageQt
import os
import sys
from image4layer import Image4Layer
import json

class QColorButton(QtWidgets.QPushButton):
    colorChanged = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        dlg = QtWidgets.QColorDialog()
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(e)

class PaneEdit(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(PaneEdit, self).__init__()
        self.base = None
        self.slot = -1
        self.tag = ""
        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("mode"))
        self.cmbMode = QtWidgets.QComboBox()
        hbox.addWidget(self.cmbMode)
        self.cmbMode.addItem("Normal")
        self.cmbMode.addItem("Overlay")
        self.cmbMode.addItem("SoftLight")
        self.cmbMode.addItem("HardLight")
        self.cmbMode.addItem("Screen")
        self.cmbMode.addItem("Multiply")
        self.cmbMode.currentIndexChanged[str].connect(self.valueChange)
        self.vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Dir"))
        self.cmbDir = QtWidgets.QComboBox()
        hbox.addWidget(self.cmbDir)
        self.cmbDir.addItems(("Both","Left","Right"))
        self.cmbDir.currentIndexChanged[str].connect(self.valueChange)
        self.vbox.addLayout(hbox)
 
    def setBase(self,base):
        self.base = base

    def getValue(self):
        return [self,self.tag,self.cmbMode.currentText(),self.cmbDir.currentText()]

    def updateBase(self):
        if self.base == None:
            return
        self.base.updateBase()

    def valueChange(self,str):
        if str != "":
            self.updateBase()

    def setValue(self,mode,dir):
        self.cmbMode.setCurrentText(mode)
        self.cmbDir.setCurrentText(dir)

class NumberEdit(QtWidgets.QLineEdit):
    def __init__(self,initial,onchange,parent=None):
        super(NumberEdit,self).__init__(initial)
        self.setFixedWidth(64)
        self.setValidator(QtGui.QIntValidator())
        self.textChanged[str].connect(onchange)

class PaneFill(PaneEdit):
    def __init__(self,parent=None):
        super(PaneFill, self).__init__()
        self.base = None
        self.slot = -1
        self.tag = "Fill"

        self.vbox.addWidget(QtWidgets.QLabel("Size"))
        hbox = QtWidgets.QHBoxLayout()
        self.slWidth = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slWidth.valueChanged[int].connect(self.sliderChange)
        hbox.addWidget(self.slWidth)
        self.txtWidth = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtWidth)
        self.vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        self.btnColor = QColorButton("")
        self.btnColor.setColor("#000000")
        self.btnColor.colorChanged.connect(self.updateBase)
        hbox.addWidget(QtWidgets.QLabel("Fill Color"))
        hbox.addWidget(self.btnColor)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("Blur"))
        hbox = QtWidgets.QHBoxLayout()
        self.slBlur = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slBlur.valueChanged[int].connect(self.blurSlide)
        hbox.addWidget(self.slBlur)
        self.txtBlur = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtBlur)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("X offset"))
        hbox = QtWidgets.QHBoxLayout()
        self.slXOffset = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slXOffset.valueChanged[int].connect(self.xOffSlide)
        hbox.addWidget(self.slXOffset)
        self.txtXOffset = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtXOffset)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("Y offset"))
        hbox = QtWidgets.QHBoxLayout()
        self.slYOffset = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slYOffset.valueChanged[int].connect(self.yOffSlide)
        hbox.addWidget(self.slYOffset)
        self.txtYOffset = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtYOffset)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("Rotate"))
        hbox = QtWidgets.QHBoxLayout()
        self.slRotate = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slRotate.valueChanged[int].connect(self.rotateSlide)
        hbox.addWidget(self.slRotate)
        self.slRotate.setMinimum(-180)
        self.slRotate.setMaximum(180)
        self.txtRotate = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtRotate)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("Cutoff"))
        hbox = QtWidgets.QHBoxLayout()
        self.slCutoff = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slCutoff.valueChanged[int].connect(self.cutoffSlide)
        hbox.addWidget(self.slCutoff)
        self.txtCutoff = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtCutoff)
        self.vbox.addLayout(hbox)


    def setBase(self,base):
        super(PaneFill,self).setBase(base)
        self.slWidth.setMaximum(int(base.imgBase.size[0] / 4))
        self.slXOffset.setMinimum(0 - int(base.imgBase.size[0] / 2))
        self.slXOffset.setMaximum(int(base.imgBase.size[0] / 2))
        self.slYOffset.setMinimum(0 - base.imgBase.size[1])
        self.slYOffset.setMaximum(base.imgBase.size[1])
        self.slCutoff.setMaximum(int(base.imgBase.size[0] / 4))

    def getValue(self):
        values = super(PaneFill,self).getValue()
        color = QtGui.QColor(self.btnColor.color()).toRgb()
        if color == None:
            return ("",())
        r,g,b,_ = color.getRgb()
        values.append((int(self.txtWidth.text()),r,g,b,int(self.txtBlur.text()),int(self.txtXOffset.text()),int(self.txtYOffset.text()),int(self.txtRotate.text()),int(self.txtCutoff.text())))
        #print(values)
        return values

    def setValue(self,mode,dir,value):
        super(PaneFill,self).setValue(mode,dir)
        width,r,g,b,blur,xOffset,yOffset,rotate,cutoff = value
        self.txtWidth.setText(str(width))
        self.slWidth.setValue(width)
        color = QtGui.QColor(r,g,b)
        self.btnColor.setColor(color.name())
        self.slBlur.setValue(blur)
        self.slXOffset.setValue(xOffset)
        self.slYOffset.setValue(yOffset)
        self.slRotate.setValue(rotate)
        self.slCutoff.setValue(cutoff)

    def sliderChange(self,value):
        self.txtWidth.setText(str(value))
    
    def blurSlide(self,value):
        self.txtBlur.setText(str(value))

    def xOffSlide(self,value):
        self.txtXOffset.setText(str(value))

    def yOffSlide(self,value):
        self.txtYOffset.setText(str(value))

    def rotateSlide(self,value):
        self.txtRotate.setText(str(value))

    def cutoffSlide(self,value):
        self.txtCutoff.setText(str(value))

class PaneLinear(PaneEdit):
    def __init__(self,parent=None):
        super(PaneLinear, self).__init__()
        self.base = None
        self.slot = -1
        self.tag = "Linear"

        self.vbox.addWidget(QtWidgets.QLabel("Top"))
        hbox = QtWidgets.QHBoxLayout()
        self.slWidth = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slWidth.valueChanged[int].connect(self.sliderChange)
        hbox.addWidget(self.slWidth)
        self.txtWidth = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtWidth)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("Bottom"))
        hbox = QtWidgets.QHBoxLayout()
        self.slCutoff = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slCutoff.valueChanged[int].connect(self.cutoffSlide)
        hbox.addWidget(self.slCutoff)
        self.txtCutoff = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtCutoff)
        self.vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        self.btnColor = QColorButton("")
        self.btnColor.setColor("#000000")
        self.btnColor.colorChanged.connect(self.updateBase)
        hbox.addWidget(QtWidgets.QLabel("Fill Color"))
        hbox.addWidget(self.btnColor)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("Blur"))
        hbox = QtWidgets.QHBoxLayout()
        self.slBlur = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slBlur.valueChanged[int].connect(self.blurSlide)
        hbox.addWidget(self.slBlur)
        self.txtBlur = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtBlur)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("Start offset"))
        hbox = QtWidgets.QHBoxLayout()
        self.slXOffset = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slXOffset.valueChanged[int].connect(self.xOffSlide)
        hbox.addWidget(self.slXOffset)
        self.txtXOffset = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtXOffset)
        self.vbox.addLayout(hbox)

        self.vbox.addWidget(QtWidgets.QLabel("End offset"))
        hbox = QtWidgets.QHBoxLayout()
        self.slYOffset = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slYOffset.valueChanged[int].connect(self.yOffSlide)
        hbox.addWidget(self.slYOffset)
        self.txtYOffset = NumberEdit("0",self.valueChange)
        hbox.addWidget(self.txtYOffset)
        self.vbox.addLayout(hbox)


    def setBase(self,base):
        super(PaneLinear,self).setBase(base)
        self.slWidth.setMaximum(int(base.imgBase.size[1]))
        self.slXOffset.setMinimum(0 - base.imgBase.size[1])
        self.slXOffset.setMaximum(base.imgBase.size[1])
        self.slYOffset.setMinimum(0 - base.imgBase.size[1])
        self.slYOffset.setMaximum(base.imgBase.size[1])
        self.slCutoff.setMaximum(base.imgBase.size[1])

    def getValue(self):
        values = super(PaneLinear,self).getValue()
        color = QtGui.QColor(self.btnColor.color()).toRgb()
        if color == None:
            return ("",())
        r,g,b,_ = color.getRgb()
        values.append((int(self.txtWidth.text()),r,g,b,int(self.txtBlur.text()),int(self.txtXOffset.text()),int(self.txtYOffset.text()),0,int(self.txtCutoff.text())))
        #print(values)
        return values

    def setValue(self,mode,dir,value):
        super(PaneLinear,self).setValue(mode,dir)
        width,r,g,b,blur,xOffset,yOffset,rotate,cutoff = value
        self.txtWidth.setText(str(width))
        self.slWidth.setValue(width)
        color = QtGui.QColor(r,g,b)
        self.btnColor.setColor(color.name())
        self.slBlur.setValue(blur)
        self.slXOffset.setValue(xOffset)
        self.slYOffset.setValue(yOffset)
        self.slCutoff.setValue(cutoff)

    def sliderChange(self,value):
        self.txtWidth.setText(str(value))
    
    def blurSlide(self,value):
        self.txtBlur.setText(str(value))

    def xOffSlide(self,value):
        self.txtXOffset.setText(str(value))

    def yOffSlide(self,value):
        self.txtYOffset.setText(str(value))

    def cutoffSlide(self,value):
        self.txtCutoff.setText(str(value))

class MainUI(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(MainUI, self).__init__()

        self.layers = []

        self.setWindowTitle("VRoid Eye Generator")
        self.imgBase = Image.open(os.path.join(os.path.dirname(sys.argv[0]),"data","base.png"))
        hbox = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()
        hbox2 = QtWidgets.QHBoxLayout()
        self.btnNew = QtWidgets.QPushButton("New")
        hbox2.addWidget(self.btnNew)
        self.btnNew.clicked.connect(self.newEye)
        self.btnOpen = QtWidgets.QPushButton("Open")
        self.btnOpen.clicked.connect(self.openEye)
        hbox2.addWidget(self.btnOpen)
        self.btnSave = QtWidgets.QPushButton("Save As")
        self.btnSave.clicked.connect(self.saveEye)
        hbox2.addWidget(self.btnSave)
        self.vbox.addLayout(hbox2)

        self.lstLayer = QtWidgets.QListWidget()
        self.lstLayer.currentRowChanged[int].connect(self.layerChanged)
        self.lstLayer.setFixedHeight(400)
        self.vbox.addWidget(self.lstLayer)

        self.cmbPane = QtWidgets.QComboBox()
        self.cmbPane.addItem("Fill")
        self.cmbPane.addItem("Linear")
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.cmbPane)
        self.btnAdd = QtWidgets.QPushButton("Add")
        self.btnAdd.clicked.connect(self.addLayer)
        hbox2.addWidget(self.btnAdd)
        self.vbox.addLayout(hbox2)

        self.btnRem = QtWidgets.QPushButton("Remove")
        self.btnRem.clicked.connect(self.removeLayer)
        self.vbox.addWidget(self.btnRem)

        self.btnDup = QtWidgets.QPushButton("Duplicate")
        self.btnDup.clicked.connect(self.dupeLayer)
        self.vbox.addWidget(self.btnDup)

        self.btnUp = QtWidgets.QPushButton("move Up")
        self.btnUp.clicked.connect(self.upLayer)
        self.vbox.addWidget(self.btnUp)

        self.btnDown = QtWidgets.QPushButton("move Down")
        self.btnDown.clicked.connect(self.downLayer)
        self.vbox.addWidget(self.btnDown)

        self.btnExport = QtWidgets.QPushButton("Export")
        self.vbox.addWidget(self.btnExport)
        self.btnExport.clicked.connect(self.exportEye)

        hbox.addLayout(self.vbox)

        self.gvMain = QtWidgets.QGraphicsView()
        hbox.addWidget(self.gvMain)
        self.gvScene = QtWidgets.QGraphicsScene()
        self.gvMain.setScene(self.gvScene)
        self.items = []
        self.items.append(QtWidgets.QGraphicsPixmapItem())
        self.gvScene.addItem(self.items[0])
        qim = ImageQt(self.imgBase)
        pix = QtGui.QPixmap.fromImage(qim).copy()
        self.items[0].setPixmap(pix)
        self.setLayout(hbox)
        self.updateBase()

        self.vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(self.vbox)

        self.addLayer()

        self.imgExport = None

    def layerChanged(self,idx):
        cur = len(self.layers) - idx - 1
        for i in range(len(self.layers)):
            if i == cur:
                self.layers[i].setVisible(True)
                self.layers[i].setFixedHeight(480)
                self.layers[i].setFixedWidth(320)
            else:
                self.layers[i].setVisible(False)
                self.layers[i].setFixedHeight(0)

    def updateBase(self):
        img = self.imgBase.copy()
        r0 = g0 = b0 = 0
        for layer in self.layers:
            _,tag,mode,dir,values = layer.getValue()
            img_left = self.imgBase.crop((0,0,int(self.imgBase.size[0] / 2),self.imgBase.size[1]))
            img_right = self.imgBase.crop((int(img.size[0] / 2),0,self.imgBase.size[0],self.imgBase.size[1]))
            mask0_l = img_left.split()[-1].copy()
            mask0_r = img_right.split()[-1].copy()
            img_left.paste((r0,g0,b0),(0,0,img_left.size[0],img_left.size[1]),mask0_l)
            img_right.paste((r0,g0,b0),(0,0,img_right.size[0],img_right.size[1]),mask0_r)
            img_base_l = img.crop((0,0,int(img.size[0] / 2),img.size[1]))
            img_base_r = img.crop((int(img.size[0] / 2),0,img.size[0],img.size[1]))
            img_new_l = Image.new("RGBA",img_base_l.size)
            img_new_r = Image.new("RGBA",img_base_r.size)
            draw = False
            if tag == "Fill":
                draw = True
                width,r,g,b,blur,xOffset,yOffset,rotate,cutoff = values
                if width >= int(self.imgBase.size[0] / 4):
                    continue
                if width > 0:
                    img_left = img_left.resize((img_left.size[0] - width*2,img_left.size[1] - width*2), Image.LANCZOS)
                    img_right = img_right.resize((img_right.size[0] - width*2,img_right.size[1] - width*2), Image.LANCZOS)
                cut_left = cut_right = None
                if cutoff > 0:
                    cut_left = img_left.resize((cutoff*2,cutoff * 2), Image.LANCZOS).split()[-1]
                    cut_right = img_right.resize((cutoff*2,cutoff * 2), Image.LANCZOS).split()[-1]
                mask_l = img_left.split()[-1]
                mask_r = img_right.split()[-1]
                mask2_l = Image.new("L",img_new_l.size)
                mask2_r = Image.new("L",img_new_r.size)
                mask2_l.paste(mask_l.convert("L"),(width,width))
                mask2_r.paste(mask_r.convert("L"),(width,width))
                if cut_right != None:
                    mask2_l.paste((0),(int(mask2_l.size[0] / 2) - cutoff,int(mask2_l.size[1] / 2) - cutoff),cut_left)
                if cut_right != None:
                    mask2_r.paste((0),(int(mask2_r.size[0] / 2) - cutoff,int(mask2_r.size[1] / 2) - cutoff),cut_right)
                mask2_l = mask2_l.rotate(rotate,translate=(xOffset,yOffset))
                mask2_r = mask2_r.rotate(0 - rotate,translate=(0 - xOffset,yOffset))
                if blur > 0:
                    mask2_l = mask2_l.filter(ImageFilter.GaussianBlur(blur))
                    mask2_r = mask2_r.filter(ImageFilter.GaussianBlur(blur))
                img_new_l.paste((r,g,b),(0,0,img_new_l.size[0],img_new_l.size[1]),mask2_l)
                img_new_r.paste((r,g,b),(0,0,img_new_r.size[0],img_new_r.size[1]),mask2_r)
                r0 = r
                g0 = g
                b0 = b

            if tag == "Linear":
                draw = True
                width,r,g,b,blur,xOffset,yOffset,rotate,cutoff = values
                mask2_l = Image.new("L",img_new_l.size)
                mask2_r = Image.new("L",img_new_r.size)
                d_l = ImageDraw.Draw(mask2_l)
                d_r = ImageDraw.Draw(mask2_r)
                d_l.polygon([(0,width + xOffset),(mask2_l.size[0],width + yOffset),(mask2_l.size[0],mask2_l.size[1] - cutoff + xOffset),(0,mask2_l.size[1] - cutoff + yOffset)],fill=255)
                d_r.polygon([(0,width + yOffset),(mask2_r.size[0],width + xOffset),(mask2_r.size[0],mask2_r.size[1] - cutoff + yOffset),(0,mask2_r.size[1] - cutoff + xOffset)],fill=255)
                if blur > 0:
                    mask2_l = mask2_l.filter(ImageFilter.GaussianBlur(blur))
                    mask2_r = mask2_r.filter(ImageFilter.GaussianBlur(blur))
                img_new_l.paste((r,g,b),(0,0,img_new_l.size[0],img_new_l.size[1]),mask2_l)
                img_new_r.paste((r,g,b),(0,0,img_new_r.size[0],img_new_r.size[1]),mask2_r)

            if draw == True:
                if mode == "Normal":
                    img_base_l = Image4Layer.normal(img_base_l,img_new_l)
                    img_base_r = Image4Layer.normal(img_base_r,img_new_r)
                elif mode == "Overlay":
                    img_base_l = Image4Layer.overlay(img_base_l,img_new_l)
                    img_base_r = Image4Layer.overlay(img_base_r,img_new_r)
                elif mode == "SoftLight":
                    img_base_l = Image4Layer.soft_light(img_base_l,img_new_l)
                    img_base_r = Image4Layer.soft_light(img_base_r,img_new_r)
                elif mode == "HardLight":
                    img_base_l = Image4Layer.hard_light(img_base_l,img_new_l)
                    img_base_r = Image4Layer.hard_light(img_base_r,img_new_r)
                elif mode == "Screen":
                    img_base_l = Image4Layer.screen(img_base_l,img_new_l)
                    img_base_r = Image4Layer.screen(img_base_r,img_new_r)
                elif mode == "MultiPly":
                    img_base_l = Image4Layer.multiply(img_base_l,img_new_l)
                    img_base_r = Image4Layer.multiply(img_base_r,img_new_r)
                if dir == "Left" or dir == "Both":
                    img.paste(img_base_l,(0,0),mask0_l)
                if dir == "Right" or dir == "Both":
                    img.paste(img_base_r,(int(img.size[0] / 2),0),mask0_r)

        self.imgExport = img.copy()
        qim = ImageQt(img)
        pix = QtGui.QPixmap.fromImage(qim).copy()
        self.items[0].setPixmap(pix)
    
    def addLayer(self):
        tag = self.cmbPane.currentText()
        pane = None
        if tag == "Fill":
            pane = PaneFill()
        elif tag == "Linear":
            pane = PaneLinear()
        if pane != None:
            pane.setBase(self)
            pane.slot = len(self.layers)
            pane.setVisible(False)
            self.layers.append(pane)
            self.lstLayer.insertItem(0,tag)
            self.vbox.addWidget(self.layers[-1])
            self.updateBase()
            self.lstLayer.setCurrentRow(0)
            self.layerChanged(0)
    
    def dupeLayer(self):
        row = self.lstLayer.currentRow()
        idx = len(self.layers) - 1 - row
        _,tag,mode,dir,values = self.layers[idx].getValue()
        pane = None
        if tag == "Fill":
            pane = PaneFill()
        elif tag == "Linear":
            pane = PaneLinear()
        if pane != None:
            pane.setBase(self)
            pane.setValue(mode,dir,values)
            pane.slot = len(self.layers)
            pane.setVisible(False)
            self.layers.append(pane)
            self.lstLayer.insertItem(0,tag)
            self.vbox.addWidget(self.layers[-1])
            self.updateBase()
            self.lstLayer.setCurrentRow(0)
            self.layerChanged(0)

    def removeLayer(self):
        row = self.lstLayer.currentRow()
        idx = len(self.layers) - 1 - row
        self.layers[idx].setVisible(False)
        self.vbox.removeItem(self.vbox.itemAt(idx))
        del self.layers[idx]
        self.lstLayer.takeItem(row)
        if row >= len(self.layers):
            row -= 1
        self.lstLayer.setCurrentRow(row)
        self.layerChanged(row)
        self.updateBase()

    def upLayer(self):
        row = self.lstLayer.currentRow()
        if row <= 0:
            return
        idx = len(self.layers) - 1 - row
        pane = self.layers[idx]
        del self.layers[idx]
        self.layers.insert(idx + 1,pane)
        self.lstLayer.takeItem(row)
        self.lstLayer.insertItem(row - 1,pane.tag)
        self.lstLayer.setCurrentRow(row - 1)
        self.layerChanged(row - 1)
        self.updateBase()

    def downLayer(self):
        row = self.lstLayer.currentRow()
        if row >= self.lstLayer.count():
            return
        idx = len(self.layers) - 1 - row
        pane = self.layers[idx]
        del self.layers[idx]
        self.layers.insert(idx - 1,pane)
        self.lstLayer.takeItem(row)
        self.lstLayer.insertItem(row + 1,pane.tag)
        self.lstLayer.setCurrentRow(row + 1)
        self.layerChanged(row + 1)
        self.updateBase()

    def saveEye(self):
        name,_ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Project", "", "Eyegen files (*.eye)")
        if name == "":
            return
        data = {}
        data["id"] = "Eyegen"
        data["version"] = "0.0"
        data["current"] = self.lstLayer.currentRow()
        data["layer"] = []
        for layer in self.layers:
            _,tag,mode,dir,values = layer.getValue()
            if tag == "Fill":
                width,r,g,b,blur,xOffset,yOffset,rotate,cutoff = values
                data["layer"].append([tag,mode,dir,(width,r,g,b,blur,xOffset,yOffset,rotate,cutoff)])
            elif tag == "Linear":
                width,r,g,b,blur,xOffset,yOffset,rotate,cutoff = values
                data["layer"].append([tag,mode,dir,(width,r,g,b,blur,xOffset,yOffset,rotate,cutoff)])

        f = open(name, 'w')
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))


    def newEye(self):
        for i in reversed(range(len(self.layers))):
            idx = len(self.layers) - 1 - i
            self.layers[idx].setVisible(False)
            self.vbox.removeItem(self.vbox.itemAt(idx))
            del self.layers[idx]
            self.lstLayer.takeItem(idx)
        self.cmbPane.setCurrentText("Fill")
        self.addLayer()
        self.updateBase()
            

    def openEye(self):
        name,_ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Project", "", "Eyegen files (*.eye)")
        if name == "":
            return
        data = json.load(open(name,"r"))
        if data["id"] != "Eyegen":
            return
        for i in reversed(range(len(self.layers))):
            idx = len(self.layers) - 1 - i
            self.layers[idx].setVisible(False)
            self.vbox.removeItem(self.vbox.itemAt(idx))
            del self.layers[idx]
            self.lstLayer.takeItem(idx)

        for d in data["layer"]:
            tag,mode,dir,values = d
            pane = None
            if tag == "Fill":
                pane = PaneFill()
            if tag == "Linear":
                pane = PaneLinear()
            if pane != None:
                pane.setBase(self)
                pane.slot = len(self.layers)
                pane.setVisible(False)
                pane.setValue(mode,dir,values)
                self.layers.append(pane)
                self.lstLayer.insertItem(0,tag)
                self.vbox.addWidget(self.layers[-1])
        
        self.lstLayer.setCurrentRow(data["current"])
        self.updateBase()

    def exportEye(self):
        if self.imgExport == None:
            return
        outName,_ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Eye Texture", "", "PNG file (*.png)")
        if outName == "":
            return
        self.imgExport.save(outName)        

if __name__ == "__main__":
#    os.chdir(os.path.dirname(__file__))
    os.chdir(os.path.dirname(sys.argv[0]))
    app = QtWidgets.QApplication(sys.argv)

    window = MainUI()
    
    window.show()

    sys.exit(app.exec_())