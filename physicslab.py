# events-example0.py
# Barebones timer, mouse, and keyboard events

from tkinter import *

# MODEL VIEW CONTROLLER (MVC)
####################################
# MODEL:       the data
# VIEW:        redrawAll and its helper functions
# CONTROLLER:  event-handling functions and their helper functions
####################################

import math
import string
####################################
# customize these functions
####################################

class Particle(object):
    k = 8.9876*10**9
    def __init__(self, x, y, data):
        self.r = 20
        self.x = x
        self.y = y
        self.isClicked = False
        self.color = 'blue'
        self.charge = -1 * 10**-9
        self.vel = 0
        self.mass = 1.673 * 10 ** -27 #kilograms
        
    def draw(self, canvas):
        cx, cy, r = self.x, self.y, self.r
        canvas.create_oval(cx - r, cy-r, cx+r, cy+r, fill = self.color)
        
    def move(self, x, y):
        self.x = x
        self.y = y
        
    def followPath(self, path):
        #for coord in path.pathList:
        if path.pathList != []:
            coord = (path.pathList.pop(0))
            self.move(coord[0], coord[1])
    
    def moveInMotion(self, data):
        #move in motion at velocity
        self.updateVel(data)
        dx = self.vel*math.cos(self.angForce)/data.meter
        dy = self.vel*math.sin(self.angForce)/data.meter
       #find old distances
        distances = []
        for particleList in data.particles:
            for particle in particleList:
                if particle != self:
                    d = self.distance((particle.x, particle.y))
                    distances.append((d, self.charge, particle.charge))
        self.move(self.x + dx, self.y + dy) #move particle
        
        #check new distances
        newDistances = []
        for particleList in data.particles:
            for particle in particleList:
                if particle != self:
                    d = self.distance((particle.x, particle.y))
                    newDistances.append(d)
        for i in range(len(distances)):
            #if opposite charges
            if ((distances[i][1]/abs(distances[i][1])) == 
                -1*(distances[i][2]/abs(distances[i][2]))):
                if (newDistances[i] > distances[i][0] or 
                    newDistances[i] < 2*self.r): 
                    self.move(self.x - dx, self.y - dy) 
        
    def updateVel(self, data):
        self.calcAcceleration(data)
        self.vel += self.acc
        self.vel /= 10**15
    
    def calcAcceleration(self, data):
        forceVec = self.calcNetForce(data.particles, data)
        self.force = forceVec[0]
        self.angForce = forceVec[1]
        self.acc = self.force/self.mass
        
    def calcNetForce(self, particles, data):
        netF = [[],[]]
        for particleList in data.particles:
            for particle in particleList:
                if particle != self:
                    (force, ang) = self.calcForce(particle, data)
                    netF[0].append(force)
                    netF[1].append(ang) #polar form
            
        vecSum = [0,0] # rectangular form
        for i in range(len(netF[0])):
            newVec = [netF[0][i] * math.cos(netF[1][i]), 
                      netF[0][i] * math.sin(netF[1][i])]
            vecSum[0] += newVec[0]
            vecSum[1] += newVec[1]
        avgAng = math.atan2(vecSum[1], vecSum[0])
        #convert vecSum to polar form
        vecSum[0] = math.sqrt((vecSum[0]**2)+(vecSum[1]**2))
        vecSum[1] = avgAng
        return vecSum
    
    def calcForce(self, particle, data):
        r = self.distance((particle.x, particle.y)) / (data.meter)
        if r == 0:
            r = .01
        force = particle.k * self.charge * particle.charge / (r**2)
        diffX = (self.x - particle.x) / (data.meter) #in meters
        diffY = (self.y - particle.y) / (data.meter) #in meters
        ang = abs(math.atan2(diffY,diffX))
        if diffX<0 and diffY>0: #4th Quadrant
            ang = abs(math.atan2(diffX,diffY))
            ang = math.pi/2 + ang
        elif diffX<0 and diffY<0: #1st Quad
            ang = abs(math.atan2(diffX,diffY)) + math.pi/2
        elif diffX>0 and diffY<0: #2nd Quad
            ang = abs(ang)
            ang = 2*math.pi - ang
        return (force, ang)
    
    def distance(self, p1):
        return math.sqrt((self.x - p1[0])**2 + (self.y - p1[1])**2)
            
class Proton(Particle):
    def __init__(self, x, y, data):
        super().__init__(x, y, data)
        self.color = 'red'
        self.charge = 1 * 10 **-9
        self.mass = 1.673 * 10 ** -27 #kilograms

    def draw(self, canvas):
        super().draw(canvas)
        margin = self.r/20
        crossW = self.r/3
        crossH = (self.r - margin)/1.8
        cx, cy = self.x+.5, self.y
        crossCoord = [cx-crossW/2, cy-crossH, #top left
                      cx+crossW/2, cy-crossH, #top right
                      cx+crossW/2, cy-(crossW/2), #top right L point
                      cx+crossH, cy-(crossW/2), #right top 
                      cx+crossH, cy+(crossW/2), #right bottom
                      cx+crossW/2, cy+(crossW/2), #bottom right L point
                      cx+crossW/2, cy+crossH, #bottom right 
                      cx-crossW/2, cy+crossH, #bottom left
                      cx-crossW/2, cy+(crossW/2), #bottom left L point, 
                      cx-crossH, cy+(crossW/2), #right bottom
                      cx-crossH, cy-(crossW/2), #right top
                      cx-(crossW/2), cy-(crossW/2)] #top left L point
        canvas.create_polygon(crossCoord, fill = 'white')
        
class Electron(Particle):
    def _init__(self, x, y, data):
        super().__init__(x, y, data)
        self.color = 'blue'
        self.charge = -1 * 10**-9
        self.mass = 9.109 * 10**-31 #kilograms
    
    def draw(self, canvas):
        super().draw(canvas)
        cx, cy, r = self.x, self.y, self.r
        width = (1.25*r)
        height = r/6
        canvas.create_rectangle(cx-width/2, cy-height, 
                                cx+width/2, cy+height, fill = 'white',
                                outline = 'white')
class Field(object):
    def __init__(self, x, y, data):
        self.x = x
        self.y = y
        self.width = 12.5
        self.height = 5
        self.arrowW = 10
        self.angle = 0
        self.getCoord()
        self.xCoeff = 1
        self.yCoeff = 1

    def draw(self, canvas):
        canvas.create_polygon(self.coord, 
            outline = 'white', fill = 'white')
    def getCoord(self):
        x, y, width, height = self.x, self.y, self.width, self.height
        arrowW = self.arrowW
        self.coord = [(x-width, y-height), #top-left
                 (x+width, y-height), #top-right
                 (x+width, y-2*height), #top-arrow-point
                 (x+width+arrowW, y), #right-most arrow point
                 (x+width, y+2*height), #bottom-arrow-point
                 (x+width, y+height), 
                 (x-width, y+height)]
    def turn(self, dAngle):
        for i in range(len(self.coord)):
            self.coord[i] = self.rotate((self.coord[i]), dAngle)
    
    def rotate(self, point, angle):
        #Counterclockwise rotates a single point
        cx, cy = self.x, self.y
        (x, y) = point
        qx = cx + math.cos(angle) * (x - cx) + math.sin(angle) * (y - cy)
        qy = cy - math.sin(angle) * (x - cx) + math.cos(angle) * (y - cy)
        return (qx, qy)
        
    def point(self, particles, data):
        self.netVector = self.calcNetField(particles, data)
        angle = self.netVector[1]
        dAngle = angle - self.angle
        self.turn(dAngle)
        self.angle = angle

    def calcNetField(self, particles, data):
        netF = [[],[]]
        for particleList in data.particles:
            for particle in particleList:
                eField = self.calcField(particle, data)
                netF[0].append(eField[0])
                netF[1].append(eField[1]) #polar form
            
        vecSum = [0,0] # rectangular form
        for i in range(len(netF[0])):
            newVec = [netF[0][i] * math.cos(netF[1][i]), 
                      netF[0][i] * math.sin(netF[1][i])]
            vecSum[0] += newVec[0]
            vecSum[1] += newVec[1]
        avgAng = math.atan2(vecSum[1], vecSum[0])
        #convert vecSum to polar form
        vecSum[0] = math.sqrt((vecSum[0]**2)+(vecSum[1]**2))
        vecSum[1] = avgAng
        return vecSum
    
    def calcField(self, particle, data):
        r = self.distance((particle.x, particle.y)) / (data.meter)
        if r == 0:
            r = .01
        eField = particle.k * particle.charge / (r**2)
        diffX = (self.x - particle.x) / data.meter #in meters
        diffY = (particle.y - self.y) / data.meter #in meters
        ang = abs(math.atan2(diffY,diffX))
        if diffX<0 and diffY>0: #4th Quadrant
            ang = abs(math.atan2(diffX,diffY))
            ang = math.pi/2 + ang
        elif diffX<0 and diffY<0: #1st Quad
            ang = abs(math.atan2(diffX,diffY)) + math.pi/2
        elif diffX>0 and diffY<0: #2nd Quad
            ang = abs(ang)
            ang = 2*math.pi - ang
        return (eField, ang)
        
    def distance(self, p1):
        return math.sqrt((self.x - p1[0])**2 + (self.y - p1[1])**2)
    
    def matchFunction(self, row, col, xCoeff, yCoeff, data):
        self.calcFuncField(row, col, xCoeff, yCoeff, data)
        self.pointWithFunc()
                
    def calcFuncField(self, row, col, xCoeff, yCoeff, data):
        y = row - (len(data.fields)/2)
        x = col - (len(data.fields[0])/2)
        # eval function
        xField = xCoeff * x
        yField = yCoeff * y
        self.netVector = []
        mag = math.sqrt(xField**2 + yField**2)
        self.netVector.append(mag)
        ang = abs(math.atan2(yField,xField))
        if x>0 and y<0: #3rd Quad
            ang = math.pi + ang
        elif x<0 and y<0: #2nd Quad
            ang = ang
        elif x<0 and y>0: #1st Quad
            ang = math.pi - ang
        elif x>0 and y>0: #4th Quad
            ang *= -1
        if x == 0:
            if y < 0:
                ang = math.pi
            else:
                ang = 0
        if y == 0:
            if x < 0:
                ang = math.pi/2
            else:
                ang = 3*math.pi/2
        self.netVector.append(ang)
        
    def pointWithFunc(self):
        angle = self.netVector[1]
        dAngle = angle - self.angle
        self.turn(dAngle)
        self.angle = angle
        
class Sensor(Field):
    def __init__(self, x, y, data):
        super().__init__(x, y, data)
        self.color = 'yellow'
        self.r = 10
        self.width = 12.5
        self.height = 5
        self.arrowW = 10
        self.isClicked = False
        self.netF = self.calcNetField(data.particles, data)
        
    def draw(self, canvas):
        cx, cy, r = self.x, self.y, self.r
        canvas.create_oval(cx - r, cy-r, cx+r, cy+r, fill = self.color)
        
        deg = '%.1f' % (self.netF[1]*180/math.pi)
        magnitude = '%.1f' % (self.netF[0])
        canvas.create_text(cx, cy-r, text = deg + ' deg', 
                           fill = 'green')
        canvas.create_text(cx, cy+r, text = magnitude + ' V/m', 
                           fill = 'green')
    def move(self, x, y, data):
        self.x = x
        self.y = y
        self.netF = self.calcNetField(data.particles, data)

class Voltmeter(Sensor):
    def __init__(self, data):
        self.margin = 10
        self.rx = 35
        self.ry = 60
        self.mainx = data.width - self.rx - self.margin
        self.mainy = data.height/2
        self.screenCord = [self.mainx-self.rx+self.margin, 
                           self.mainy-self.ry+3*self.margin, 
                           self.mainx+self.rx-self.margin, 
                           self.mainy]
        self.volts = 0
        self.isClicked = False
        
        #circle coord:
        self.x, self.y = self.mainx, self.mainy-(1.25*self.ry)
        
    def draw(self, canvas):
        x, y, rx, ry = self.mainx, self.mainy, self.rx, self.ry
        canvas.create_rectangle(x-rx, y-ry, x+rx, y+ry, fill = 'blue')
        canvas.create_rectangle(self.screenCord, fill = 'white')
        volts = '%.1f' % self.volts
        canvas.create_text(x, y-1.5*self.margin, text= volts + ' V')
        canvas.create_line(x, y-ry, x, y-(1.25*ry)+7, fill = 'white')
        r = 7
        cx, cy = self.x, self.y
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline = 'red')
    
    def move(self, x, y, data):
        super().move(x, y, data)
        self.mainx = self.x
        self.mainy = self.y + (1.25*self.ry)
        self.screenCord = [self.mainx-self.rx+self.margin, 
                           self.mainy-self.ry+3*self.margin, 
                           self.mainx+self.rx-self.margin, 
                           self.mainy]
    
    def calcVolt(self, particle, data):
        #electricField
        self.elecField = self.calcField(particle, data)
        d = self.distance((particle.x, particle.y)) / data.meter
        volt = abs(self.elecField[0]*d)
        if particle.charge < 0:
            mult = -1
        else:
            mult = 1
        volt *= mult
        return volt
    
    def calcNetVolt(self, data):
        netVolt = []
        for particleList in data.particles:
            for particle in particleList:
                volt = self.calcVolt(particle, data)
                netVolt.append(volt)
                
        netVoltMag = 0
        for volt in netVolt:
            netVoltMag += volt
            
        self.volts = netVoltMag
    
    def pulse(self, data):
        ogX, ogY, ogF = self.x, self.y, self.volts
        coord = []
        for particleList in data.particles:
            for particle in particleList:
                r = 1
                while r <= data.width:
                    ang = 0
                    while ang <= 2*math.pi:
                        cx, cy = particle.x, particle.y
                        x = (cx+(r*math.cos(ang))) 
                        y = (cy+(r*math.sin(ang)))
                        self.x, self.y = x, y
                        self.calcNetVolt(data)
                        if (ogF-1 <=self.volts<= ogF+1):
                            coord.append((x, y))
                        ang += math.pi/6
                    r+=1
        self.x, self.y, self.volts = ogX, ogY, ogF
        return coord
        
class startScreen(object):
    def __init__(self, data):
        self.width = data.width
        self.height = data.height
        self.titleX = self.width/2
        self.titleY = self.height/5
        self.startX = self.width/2
        self.startY = 3.5*self.height/5
        self.instructionX = self.width/2
        self.instructionY = 4.5*self.height/5
        
    def draw(self, canvas, data):
        #MAYBE ADD A NICE LOOKING GIF BACKGROUND HERE
        canvas.create_rectangle(0, 0, self.width, self.height, fill = 'black')
        canvas.create_text(self.titleX, self.titleY, text=''' Charges and 
Electric Fields''', fill = 'white', font=("Fixedsys", 80))

class instructions(object):
    def __init__(self, data):
        self.width = data.width
        self.height = data.height
        self.welcomeText = '''Welcome to the Charges and \
Electric Fields simulator!'''
        self.welcomeTextX = data.width/2
        self.welcomeTextY = data.height/20
        self.explanation = (
'''This program allows you to simulate electric fields by dragging 
and dropping protons and electrons onto a canvas.''')
        self.explanationX = data.width/2,
        self.explanationY = 2*data.height/20
        
        self.instructionsX = data.width/2
        self.instructionsY = 4*data.height/20
        self.instructionsStep = data.height/20
        
        
    def draw(self, canvas):
        canvas.create_rectangle(0,0,self.width, self.height, fill = 'black')
        canvas.create_text(self.welcomeTextX, self.welcomeTextY, 
                           text = self.welcomeText, fill = 'red', 
                           font = ("Courier", 20))
        canvas.create_text(self.explanationX, self.explanationY,
                           text = self.explanation, fill = 'red', 
                           font = ("Courier", 18))
        self.drawInstructions(canvas)
        
    def drawInstructions(self, canvas):
        canvas.create_text(self.instructionsX, 
                           self.instructionsY, 
                           text = (
'''1. To begin, click on a proton (particles are shown at the bottom of the canvas). A proton will begin 
following your mouse pointer. Click on anywhere else in the canvas to drop the proton and 
you will see the electric field created!'''),
                           fill = 'red', font = ("Courier", 15))
                           
        canvas.create_text(self.instructionsX/1.5, 
                           self.instructionsY + 2*self.instructionsStep, 
                           text = (
'''2. Click and drop as many protons and electrons to create a field.'''),
                           fill = 'red', font = ('Courier', 15))
                           
        canvas.create_text(self.instructionsX/1.02, 
                           self.instructionsY + 4*self.instructionsStep, 
                           text = ('''3. You can click and drop sensors at any point to find the \
angle and magnitude of the electric field 
at that point.'''),
                           fill = 'red', font = ('Courier', 15))
                           
        canvas.create_text(self.instructionsX/1.02, 
                           self.instructionsY + 6*self.instructionsStep, 
                           text = (
'''4. A voltmeter is placed to the right. Click it to move it around and measure volts around the field. 
If you press any key, an equipotential line will be drawn where the voltmeter is.'''),
                           fill = 'red', font = ('Courier', 15))

        self.drawModeDescriptions(canvas)
        
    def drawModeDescriptions(self, canvas):
        canvas.create_text(self.instructionsX, 
                           self.instructionsY + 8*self.instructionsStep, 
                           text = ('Path Mode'),
                           fill = 'red', font = ('Courier', 15))
        canvas.create_text(self.instructionsX, 
                           self.instructionsY + 9*self.instructionsStep, 
                           text = (
'''Place some particles onto the field and press 'p' to begin. Click on a particle 
and then draw a path. Click again to end the path drawing. You can do this to as many particles
as you'd like and then press any key. The particles will follow their path and the field will 
point accordingly.'''),
                           fill = 'red', font = ('Courier', 15))
        canvas.create_text(self.instructionsX, 
                           self.instructionsY + 10*self.instructionsStep, 
                           text = ('Motion Mode'),
                           fill = 'red', font = ('Courier', 15))
        canvas.create_text(self.instructionsX, 
                           self.instructionsY + 11*self.instructionsStep, 
                           text = (
'''Place some particles onto the field and press 'm' to begin. The particles will 
move in the appropriate direction with the appropriate force, velocity, and acceleration. However,
in real life, small particles like these would move extremely fast, so this program displays the 
movements 10^15 times slower.'''),
                           fill = 'red', font = ('Courier', 15))
        canvas.create_text(self.instructionsX, 
                           self.instructionsY + 12*self.instructionsStep, 
                           text = ('Function Mode'),
                           fill = 'red', font = ('Courier', 15))
        canvas.create_text(self.instructionsX, 
                           self.instructionsY + 13*self.instructionsStep, 
                           text = (
'''This mode will remove all particles from the electric field and generate a vector field based on the 
x-vector function and y-vector function you input.'''),
                           fill = 'red', font = ('Courier', 15))
                           
class Path(object):
    def __init__(self, data):
        self.r = 10
        self.pathList = []
        
    def draw(self, canvas):
        r = self.r
        if len(self.pathList)>1:
            for coord in self.pathList:
                canvas.create_oval(coord[0]-r, coord[1]-r, 
                                   coord[0]+r, coord[1]+r, fill = 'green', 
                                   outline = 'green')
    def addToPath(self, x, y):
        self.pathList.append((x, y))

class Button(object):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.isClicked = False
        
    def draw(self, canvas):
        x, y, width, height = self.x, self.y, self.width, self.height
        canvas.create_rectangle(x-width/2, y-height/2, 
                                x+width/2, y+height/2, fill = self.color)
        
    def checkClick(self, event):
        x, y, width, height = self.x, self.y, self.width, self.height
        if (x-width/2 <= event.x <= x+width/2 and 
            y-height/2<=event.y<=y+height/2):
            return True
        return False

class TextBox(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = 'white'
        self.text = '1'
        self.isClicked = False
        
    def draw(self, canvas):
        x, y, width, height = self.x, self.y, self.width, self.height
        canvas.create_rectangle(x-width/2, y-height/2, 
                                x+width/2, y+height/2, fill = self.color)
        canvas.create_text(x, y, text = self.text, fill = 'black')
        
    def checkClick(self, event):
        x, y, width, height = self.x, self.y, self.width, self.height
        if (x-width/2 <= event.x <= x+width/2 and 
            y-height/2<=event.y<=y+height/2):
            self.isClicked = not self.isClicked
            return True
        return False
    
    def addText(self, dig):
        nums = string.digits
        if dig in nums:
            if self.text == '0':
                self.text = dig
            else:
                self.text = self.text + dig
        elif dig == 'BackSpace':
            length = len(self.text)
            self.text = self.text[0:length-1]
        if len(self.text) == 0:
            self.text = '0'
    
#Cite: Barebones structure from course notes
# https://pd43.github.io/notes/notes4-2.html
            
# Initialize the data which will be used to draw on the screen.
def init(data):
    # load data as appropriate
    #screen booleans
    data.startScreenOn = True
    data.startScreen = startScreen(data)
    data.instructionsOn = False
    data.instructionScreen = instructions(data)
    initButtons(data)
    initBases(data)
    initModes(data)
    
def initButtons(data):
    data.startButton = Button(data.startScreen.startX, data.startScreen.startY, 
                              data.width/3, data.height/11, 'white')
    data.instructionButton = Button(data.startScreen.instructionX, 
                                    data.startScreen.instructionY, 
                                    data.width/3, data.height/11, 'white')
    data.menuButton = Button(9*data.width/10, 19*data.height/20, 
                             data.width/10, data.height/20, 'green')
    data.restartButton = Button(9*data.width/10, 17*data.height/20,
                                data.width/10, data.height/20, 'brown')
    #textboxes
    data.xText = TextBox(8*data.width/10, 9*data.height/20, data.width/10, 
                         data.height/20)
    data.yText = TextBox(8*data.width/10, 11*data.height/20, data.width/10, 
                         data.height/20)
    
def initBases(data):
    #unit conversion
    data.meter = data.width/10
    
    #make base of objects
    data.backgroundColor = 'black'
    data.protonBase = Proton(4*data.width/12.5, 
                         19*data.height/20, data)
    data.electronBase = Electron(6*data.width/12.5, 
                         19*data.height/20, data)
    data.voltmeter = Voltmeter(data)
    
    #list of objects
    data.protons = []
    data.electrons = []
    data.fields = []
    data.sensors = []
    for row in range(1, 9):
        newList = []
        for col in range(1, 9):
            newList.append(Field(row*data.width/12.5, col*data.height/10, 
                                     data))
        data.fields.append(newList)
    data.particles = [data.protons, data.electrons]
    
    data.trash = [data.width/15, 18.5*data.height/20, data.width/5, 
                  19.5*data.height/20]
    
    data.sensorBase = Sensor(8*data.width/12.5, 19*data.height/20, data)
    data.paths = []
    data.equipCoord = []
    
    data.fieldExists = False

def initModes(data):
    #MODES
    #path mode
    data.pathMode = False
    data.pathModeParticleClicked = False
    data.particleForPath = []
    data.drawingPath = False
    data.finishedDrawingAllPaths = True
    
    #motion mode
    data.motionMode = False
    
    #function mode
    data.functionMode = False
    data.xFunc = 'x'
    data.yFunc = 'y'
    
# These are the CONTROLLERs.
# IMPORTANT: CONTROLLER does *not* draw at all!
# It only modifies data according to the events.
def mousePressed(event, data):  
    if data.startScreenOn and data.startButton.checkClick(event):
        data.startScreenOn = False
        data.instructionsOn = False
        return      
    elif (data.startScreenOn and data.instructionButton.checkClick(event)):
        data.instructionsOn = True
        data.startScreenOn = False
        return
    elif ((data.instructionsOn or not data.startScreenOn) and
          data.menuButton.checkClick(event)):
        data.instructionsOn = False
        data.startScreenOn = True
        return
    elif (not data.startScreenOn) and data.restartButton.checkClick(event):
        init(data)
        data.startScreenOn = False
    elif (not data.startScreenOn) and data.xText.checkClick(event):
        data.xText.isClicked = True
        data.yText.isClicked = False
    elif (not data.startScreenOn) and data.yText.checkClick(event):
        data.yText.isClicked = True
        data.xText.isClicked = False 
            
    if data.pathMode: 
        pathModeMousePressed(event, data)
        return

    if moveAroundParticles(event, data) ==  True:
        return
    
    toggleVoltmeterClick(event, data)
    
    ableToMakeCopies(event, data)
def moveAroundParticles(event, data):
    #be able to move around protons and electrons 
    for i in range(len(data.protons)-1, -1, -1):
        if toggleParticleClick(event, data, data.protons[i]):
            return True
    for i in range(len(data.electrons)-1, -1, -1):
        if toggleParticleClick(event, data, data.electrons[i]): return True
    for i in range(len(data.sensors)-1, -1, -1):
        if toggleParticleClick(event, data, data.sensors[i]): return True
    
def toggleVoltmeterClick(event, data):
    ####toggle Click on Voltmeter
    diffX = abs(event.x - data.voltmeter.x)
    diffY = abs(event.y - data.voltmeter.y)
    #clicking the particle
    if (diffX <= data.voltmeter.rx and diffY <= data.voltmeter.ry
        and data.voltmeter.isClicked == False):
        data.voltmeter.isClicked = True
    #unclicking particle
    elif data.voltmeter.isClicked:
        data.voltmeter.isClicked = False
        
def ableToMakeCopies(event, data):
    #make copies of proton or electron
    diffXOfProt = abs(event.x - data.protonBase.x)
    diffYOfProt = abs(event.y - data.protonBase.y)
    diffXOfElec = abs(event.x - data.electronBase.x)
    diffYOfElec = abs(event.y - data.electronBase.y)
    diffXOfSens = abs(event.x - data.sensorBase.x)
    diffYOfSens = abs(event.y - data.sensorBase.y)    
    
    if diffXOfProt <= data.protonBase.r and diffYOfProt <= data.protonBase.r:
        data.protons.append(Proton(4*data.width/12.5, 
                         19*data.height/20, data))
        data.protons[-1].isClicked = True
    
    elif (diffXOfElec <= data.electronBase.r and 
          diffYOfElec <= data.electronBase.r):
        data.electrons.append(Electron(6*data.width/12.5, 
                         19*data.height/20, data))
        data.electrons[-1].isClicked = True
        
    elif (diffXOfSens <= data.sensorBase.r and 
          diffYOfSens <= data.sensorBase.r):
        data.sensors.append(Sensor(8*data.width/12.5, 
                         19*data.height/20, data))
        data.sensors[-1].isClicked = True
    
def toggleParticleClick(event, data, particle):
    #determines if particle is clicked
    #if yes, changes .isClicked to true
    #if already clicked, it unclicks
    diffX = abs(event.x - particle.x)
    diffY = abs(event.y - particle.y)
    #clicking the particle
    if (diffX <= particle.r and diffY <= particle.r
        and particle.isClicked == False):
        particle.isClicked = True
        return True
    #unclicking particle
    elif particle.isClicked:
        particle.isClicked = False
        return True
    return False
        
def mouseMotion(event, data):
    if data.pathMode:
        pathModeMouseMotion(event, data)
        return
    
    for proton in data.protons:
        if proton.isClicked:
            proton.move(event.x, event.y)
    
    for electron in data.electrons:
        if electron.isClicked:
            electron.move(event.x, event.y)

    for sensor in data.sensors:
        if sensor.isClicked:
            sensor.move(event.x, event.y, data)
            
    if data.voltmeter.isClicked:
        data.voltmeter.move(event.x, event.y, data)
        
def keyPressed(event, data):
    # use event.char and event.keysym
    if data.xText.isClicked:
        data.xText.addText(event.keysym)
    elif data.yText.isClicked:
        data.yText.addText(event.keysym)
        
    if event.keysym == 'i':
        data.instructionsOn = True
        data.startScreenOn = False
        return
    if data.startScreenOn and event.keysym == 's':
        data.startScreenOn = False
        return
    elif data.startScreenOn == False and event.keysym == 's':
        data.startScreenOn = True
        return
    elif data.startScreenOn == False and event.keysym == 'p':
        data.pathMode = not data.pathMode
        if data.pathMode:
            data.finishedDrawingAllPaths = False
            data.motionMode = False
            data.functionMode = False
        return
    elif data.startScreenOn == False and event.keysym == 'm':
        data.motionMode = not data.motionMode
        if data.motionMode:
            data.pathMode = False
            data.functionMode = False
        return
    elif data.startScreenOn == False and event.keysym == 'f':
        data.functionMode = not data.functionMode
        if data.functionMode:
            data.pathMode = False
            data.motionMode = False
        data.fieldExists = True
        return
    else:
        data.finishedDrawingAllPaths = True
    
    if not data.pathMode and not data.motionMode:
        data.equipCoord = data.voltmeter.pulse(data)
    
def timerFired(data):
    if data.pathMode:
        pathModeTimerFired(data)
    
    if len(data.particles[0])>0 or len(data.particles[1])>0:
        data.fieldExists = True
        for fieldList in data.fields:
            for field in fieldList:
                    field.point(data.particles, data)
    else:
        data.fieldExists = False
        
    if len(data.sensors)>0:
        for sensor in data.sensors:
            sensor.netF = sensor.calcNetField(data.particles, data)
    
    deleteParticlesAndSensors(data)
    
    data.voltmeter.calcNetVolt(data)   
    
    if data.motionMode:
        motionModeTimerFired(data)
    
    if data.functionMode:
        functionModeTimerFired(data)
        
def deleteParticlesAndSensors(data):
    for particleList in data.particles:
        i = 0
        while i < len(particleList):
            if (data.trash[0] <= particleList[i].x <= data.trash[2] and
                data.trash[1] <= particleList[i].y <= data.trash[3] and
                particleList[i].isClicked==False):
                del particleList[i]
            i += 1
            
    i = 0
    while i < len(data.sensors):
        if (data.trash[0] <= data.sensors[i].x <= data.trash[2] and
            data.trash[1] <= data.sensors[i].y <= data.trash[3] and
            data.sensors[i].isClicked==False):
            del data.sensors[i]
        i += 1
    
    
##########################PATH_MODE_CONTROLLERS############################
def pathModeMousePressed(event, data):
    doubleBreak = False
    #find what particle is clicked
    if data.drawingPath == False:
        for particleList in reversed(data.particles):
            for particle in reversed(particleList):
                diffX = abs(event.x - particle.x)
                diffY = abs(event.y - particle.y)
                
                if diffX <= particle.r and diffY <= particle.r:
                    data.particleForPath.append(particle)
                    data.paths.append(Path(data))
                    data.drawingPath = True
                    data.finishedDrawingAllPaths = False
                    doubleBreak = True
                    break
            if doubleBreak:
                break
    else:
        data.drawingPath = not data.drawingPath
    
def pathModeMouseMotion(event, data):
    if data.drawingPath:
        data.paths[-1].addToPath(event.x, event.y)
        
def pathModeTimerFired(data):
    if (not data.drawingPath and data.finishedDrawingAllPaths):
        for i in range(len(data.particleForPath)):
            data.particleForPath[i].followPath(data.paths[i])
            
##########################MOTION_MODE_CONTROLLERS############################
def motionModeMousePressed(event, data):
    pass
def motionModeMouseMotion(event, data):
    pass
def motionModeTimerFired(data):
    if (len(data.particles[0]) > 1 or len(data.particles[1]) > 1 or 
        len(data.particles[0]) + len(data.particles[1]) > 1):
        for particleList in data.particles:
            for particle in particleList:
                particle.moveInMotion(data)
                
##########################FUNCTION_MODE_CONTROLLERS############################
def functionModeMousePressed(event, data):
    pass
def functionModeMouseMotion(event, data):
    pass
def functionModeTimerFired(data):
    for row in range(len(data.fields)-1,-1,-1):
        for col in range(len(data.fields[0])):
            data.fields[row][col].matchFunction(row, col, 
                       int(data.xText.text), int(data.yText.text), 
                       data)

# This is the VIEW
# IMPORTANT: VIEW does *not* modify data at all!
# It only draws on the canvas.
def redrawAll(canvas, data):
    # draw in canvas
    if data.startScreenOn:
        drawStartScreen(canvas, data)
        return
    if data.instructionsOn:
        drawInstructionScreen(canvas, data)
        return
    
    canvas.create_rectangle(0,0,data.width, data.height,
                            fill = data.backgroundColor)
    data.protonBase.draw(canvas)
    data.electronBase.draw(canvas)
    data.sensorBase.draw(canvas)
    
    drawPartFieldSens(canvas, data)
    
    data.voltmeter.draw(canvas)
    
    drawTrash(canvas, data)
    
    drawButtons(canvas, data)

    drawTextBoxes(canvas, data)

    drawPathAndEquip(canvas, data)
    
    drawModeTitles(canvas, data)
    
def drawStartScreen(canvas, data):
    data.startScreen.draw(canvas, data)
    data.startButton.draw(canvas)
    canvas.create_text(data.startScreen.startX, 
                           data.startScreen.startY, text = 'Start',
                           fill = 'blue', font = ('Courier', 40))
        
    data.instructionButton.draw(canvas)
    canvas.create_text(data.startScreen.instructionX, 
                           data.startScreen.instructionY, 
                           text = 'Instructions', fill = 'black',
                           font = ("Courier", 40))

def drawInstructionScreen(canvas, data):
    data.instructionScreen.draw(canvas)
    data.menuButton.draw(canvas)
    canvas.create_text(9*data.width/10, 19*data.height/20, 
                           text = 'Menu', fill = 'black',
                           font = ("Courier", 20))

def drawPartFieldSens(canvas, data):
    for particleList in data.particles:
        for particle in particleList:
            particle.draw(canvas)

    if data.fieldExists or data.functionMode:
        for row in range(len(data.fields)):
            for col in range(len(data.fields[row])):
                data.fields[row][col].draw(canvas)
    
    for sensor in data.sensors:
        sensor.draw(canvas)

def drawTrash(canvas, data):
    canvas.create_rectangle(data.trash, fill = 'green')
    canvas.create_text((data.trash[2]+data.trash[0])/2,
                       (data.trash[3]+data.trash[1])/2, 
                       text = ('''Nuclear 
Waste Disposal'''), fill = 'red4')
    
def drawButtons(canvas, data):
    #buttons
    data.menuButton.draw(canvas)
    data.restartButton.draw(canvas)
    canvas.create_text(9*data.width/10, 19*data.height/20, 
                           text = 'Menu', fill = 'black',
                           font = ("Courier", 20))
    canvas.create_text(9*data.width/10, 17*data.height/20, 
                           text = 'Restart', fill = 'black',
                           font = ("Courier", 20))
    
def drawTextBoxes(canvas, data):
    #textboxes
    data.xText.draw(canvas)
    data.yText.draw(canvas)
    canvas.create_text(8.75*data.width/10, 9*data.height/20, 
                           text = 'x', fill = 'red',
                           font = ("Courier", 25))
    canvas.create_text(8.75*data.width/10, 11*data.height/20, 
                           text = 'y', fill = 'red',
                           font = ("Courier", 25))
    
def drawPathAndEquip(canvas, data):
    if len(data.equipCoord) > 1:
        for coord in data.equipCoord:
            canvas.create_text(coord, text = 'e', fill = 'orange')
            
    for path in data.paths:
        path.draw(canvas)
    
        
def drawModeTitles(canvas, data):
    if data.pathMode:
        canvas.create_text(data.width/2, data.height/20, text = 'Path Mode',
                           fill = 'green')
        
    elif data.motionMode:
        canvas.create_text(data.width/2, data.height/20, text = 'Motion Mode',
                           fill = 'green')
        
    elif data.functionMode:
        canvas.create_text(data.width/2, data.height/20, text = 'Function Mode',
                           fill = 'green')
####################################
####################################
# use the run function as-is
####################################
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)
    
    def mouseMotionWrapper(event, canvas, data):
        mouseMotion(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
        
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 1 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind('<Motion>', lambda event:
                            mouseMotionWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app

    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1000, 800)

###ignore_rest###
#TEST FUNCTION
def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def testDistance():
    assert(distance((0,0),(3,4)) == 5)
    assert(distance((0,0),(5,12)) == 13)
    assert(distance((0,0),(8,15)) == 17)
    print('Worked')
    
testDistance()
