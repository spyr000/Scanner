from shapely.geometry import LineString
from shapely.geometry import Point
from math import *
import pygame,sys
import pygame.gfxdraw
import matplotlib
import matplotlib.pyplot as plt


WIDTH = 1000
HEIGHT = 1000
rays = []
COUNT = 310
DISTANCE = 2
ISMOVING = True
ANGLE = 0.1

pygame.init()

screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

def Rotate(point,fi,center = (0,0)):
    point_ = [point[0],point[1]]
    point_[0] += center[0]
    point_[1] += center[1]
    point_[0] = int(point_[0] * cos(fi) - point_[1] * sin(fi)) - center[0]
    point_[1] = int(point_[0] * sin(fi) + point_[1] * cos(fi)) - center[1]
    return point_

def RotateLine(line,fi,center = (0,0)):
    return LineString(coordinates=(Rotate(line.coords[0],fi,center = center),Rotate(line.coords[1], fi,center = center)))

def toScreenPoint(point):
    point_ = [point[0], point[1]]
    point_[0] += WIDTH//2
    point_[1] += HEIGHT//2
    point_[1] = HEIGHT - point_[1]
    return [int(point_[0]),int(point_[1])]

class Figure(object):
    def __init__(self,coords: list,coeff: float):
        self.coords = coords
        self.coeff = coeff

class Rectangle(Figure):
    def __init__(self,coords: list,width: int,height: int,coeff,angle = 0,lines = []):
        self.coords = coords
        self.lines = lines
        self.lines.append(LineString([coords,(coords[0]+width,coords[1])]))
        self.lines.append(LineString([(coords[0]+width,coords[1]), (coords[0] + width, coords[1]+height)]))
        self.lines.append(LineString([(coords[0] + width, coords[1] + height), (coords[0], coords[1] + height)]))
        self.lines.append(LineString([(coords[0], coords[1] + height), coords]))
        self.coeff = coeff
        turnedLines = []
        for line in self.lines:
            turnedLines.append(RotateLine(line,angle,center=coords))
        self.lines = turnedLines

    def Get_lines(self):
        return self.lines

    def Intersect(self,ray):
        intersection_list = []
        for line in self.lines:
            if ray.rayline.intersects(line):
                intersection_list.append(toScreenPoint((ray.rayline.intersection(line).x,ray.rayline.intersection(line).y)))

        if len(intersection_list)>0:
            ray.capacity -= Calculate_Capacity_Loss(intersection_list[0], intersection_list[1],self.coeff)
        return intersection_list

class Circle(Figure):
    def __init__(self,coords: list,radius: int,coeff):
        self.coords = coords
        self.bound = Point(coords[0],coords[1]).buffer(radius).boundary
        self.radius = radius
        self.coeff = coeff

    def Intersect(self,ray):
        intersection_list = []

        if self.bound.intersects(ray.rayline):
                int_point1 = self.bound.intersection(ray.rayline)[0].coords[0]
                int_point2 = self.bound.intersection(ray.rayline)[1].coords[0]
                ray.capacity -= Calculate_Capacity_Loss(int_point1,int_point2,self.coeff)
                intersection_list.append(toScreenPoint(int_point1))
                intersection_list.append(toScreenPoint(int_point2))

        return intersection_list

class Ray(LineString):
    def __init__(self,line,capacity=255):
        self.capacity = capacity
        self.rayline = line

    def Rotate(self,angle):
        A = (self.rayline.coords[0][0] * cos(angle) - self.rayline.coords[0][1] * sin(angle), self.rayline.coords[0][0] * sin(angle) + self.rayline.coords[0][1] * cos(angle))
        B = (self.rayline.coords[1][0] * cos(angle) - self.rayline.coords[1][1] * sin(angle), self.rayline.coords[1][0] * sin(angle) + self.rayline.coords[1][1] * cos(angle));
        self.rayline = LineString((A,B))

    def MoveDown(self,difference):
        self.rayline = LineString([(self.rayline.coords[0][0],int(self.rayline.coords[0][1] - difference)),(self.rayline.coords[1][0], int(self.rayline.coords[1][1] - difference))])

figures = []
r = Rectangle([-110,10],40,60,0.6,angle=100)
c = Circle([-100,-100],50,0.2)
c1 = Circle([-100,-100],20,0.9)

figures.append(c)
figures.append(r)
figures.append(c1)

def DrawFigure(figure):
    if type(figure) == Rectangle:
        for line in figure.Get_lines():
            pygame.gfxdraw.line(screen,toScreenPoint(line.coords[0])[0],toScreenPoint(line.coords[0])[1],toScreenPoint(line.coords[1])[0],toScreenPoint(line.coords[1])[1],(0, 0, 255, 100))
    elif type(figure) == Circle:
        pygame.gfxdraw.circle(screen,toScreenPoint(figure.coords)[0],toScreenPoint(figure.coords)[1],figure.radius,(0, 0, 255, 100))

def Init_Rays(count: int,distance: int):
    for i in range(count):
        rays.append(Ray(LineString([(-WIDTH,0+i*distance),(WIDTH,0 + i*distance)])))
    difference = int(fabs(rays[0].rayline.coords[0][1]-rays[-1].rayline.coords[0][1]))
    for ray in rays:
        ray.MoveDown(difference//2)
        pygame.gfxdraw.line(screen, toScreenPoint(ray.rayline.coords[0])[0], toScreenPoint(ray.rayline.coords[0])[1], toScreenPoint(ray.rayline.coords[1])[0],toScreenPoint(ray.rayline.coords[1])[1],\
                            (255, 0, 0, 70))

def Draw_Rays():
    for ray in rays:
        pygame.gfxdraw.line(screen, toScreenPoint(ray.rayline.coords[0])[0], toScreenPoint(ray.rayline.coords[0])[1],
                            toScreenPoint(ray.rayline.coords[1])[0], toScreenPoint(ray.rayline.coords[1])[1],
                            (60, 50, 20, 255 - ray.capacity))

def Calculate_Capacity_Loss(point1,point2,coeff):
    dx = fabs(point1[0]-point2[0])
    dy = fabs(point1[1]-point2[1])
    hyp = sqrt(dx*dx + dy*dy)
    return int(hyp * coeff * 0.1)

if __name__ == '__main__':
    screen.fill('white')
    for fig in figures:
        DrawFigure(fig)
    Init_Rays(COUNT,DISTANCE)

    pygame.display.update()
    clock.tick(1)

screen.fill('white')

fig, ax = plt.subplots()
plt.title(f"Количество излучателей = {COUNT}, Расстояние между излучателями = {DISTANCE}")
lab = 0


while True:
    cap_list = []

    for ray in rays:
        ray.capacity = 255
        for fig in figures:
            for inter in fig.Intersect(ray):
                pygame.gfxdraw.pixel(screen,inter[0],inter[1],[255,0,0,0])
        cap_list.append(ray.capacity)

    if ISMOVING:
        Draw_Rays()
        for ray in rays:
            ray.Rotate(ANGLE)
            lab += 0.1

    pygame.display.update()
    clock.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.QUIT
            plt.plot(cap_list, label="Угол =" + str(lab%6.28))
            plt.legend()
            plt.show()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                    ANGLE*=-1
            if event.key == pygame.K_SPACE:
                print("!!!")
                ISMOVING = not ISMOVING