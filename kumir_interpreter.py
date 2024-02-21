#!/bin/python3
import turtle
import sys
import argparse
import time
from math import pi, sin, cos, fabs, asin, acos, copysign
DEFAULT_SIZE = 20
DEFAULT_XCOUNT = 40
DEFAULT_YCOUNT = 40
def isclose(a, b, rel_tol=0.001):
    if fabs (a) < rel_tol and fabs (b) < rel_tol:
        return int (copysign (1, a)) == int (copysign (1, b))
    return fabs(a - b) / max(fabs (a), fabs (b)) <= rel_tol
def main ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--size", default = DEFAULT_SIZE, nargs = '?',type=int)
    parser.add_argument("--xcount", default = DEFAULT_XCOUNT, nargs = '?', type=int)
    parser.add_argument ("--ycount", default = DEFAULT_YCOUNT, nargs = '?', type = int)
    parser.add_argument ("--file", nargs = 1, type = str, required = True)
    args = parser.parse_args()
    filename = args.file[0]
    func = "def __temp__ ():\n"
    tablevel = 1
    names = "abcdefghijklmnopqrstuvwxyz"
    lines = []
    try:
        file = open (filename, "r")
        lines = file.read().split ('\n')
        file.close()
    except OSError as e:
        print ("open () failed")
        sys.exit (1)
    except IOError:
        print ("I/O error while opening")
        sys.exit (1)
    iterator = iter (lines)
    line = next (iterator, None)
    unary = ['up', 'down', ']', "break", "continue"]
    triple = ["for", "declare", "mod", "move", "if", "setpos"]
    fifth = ["circle"]
    whiles = ["while", "do_while"]
    do_while_conditions_level = {}
    #Синтаксис крайне простой, близок к turtle, практически соответствует исполнителям черепаха,
    #чертёжник и цапля. Все параметры не должны содержать пробелов. Можно писать в 1 строку 
    #множество команд без разделителей (команды не переносятся). Проверки параметров нет и не 
    #будет, фактически проверяется при запуске. Можно пользоваться sin, cos, asin, acos, pi, isclose.
    #forward COUNT - движение вперёд на COUNT (в сторону, куда направлена черепаха)
    #backward COUNT - движение назад на COUNT
    #left COUNT - поворот налево на COUNT
    #right COUNT - поворот направо на COUNT
    #break, continue - аналогично питоновским break и continue
    #for COUNT [ - повторение блока кода COUNT раз (закрывается через ] аналогично стандартной инструкции ФИПИ)
    #print ANYTHING - просто вывод строки, переменной, числа... Главное, чтобы в ANYTHING не было пробелов
    #while VALUE1 CONDITION VALUE2 [ - аналогично питоновскому while {VALUE1} {CONDITION} {VALUE2}:
    #do_while VALUE1 CONDITION VALUE2 [ - аналогично питоновскому while True с условием в конце цикла
    #if CONDITION [ - if {CONDITION}:
    #] - закрытие блока while, do_while, for, if
    #declare NAME VALUE - объявление переменной. {NAME} = {VALUE}
    #mod NAME OPERATION - {NAME} {OPERATION}. (арифметические операции и любые другие операции доступные в питоне). Можно вызывать методы переменных.
    #up, down - поднять и опустить хвост
    #move dx dy - переместиться на {dx, dy}
    #setpos newx newy - изменить позицию на новое положение.
    #circle radius a b alpha - рисует сектор окружности с центром в точке (x + a, y + b) радиусом radius с центральным углом alpha по часовой стрелке. Если против - нужен отрицательный радиус. Предварительно проверяет, возможна ли такая окружность (sqrt (a * a + b * b) == abs (radius)).
    #heading alpha - изменение направления движения. Угол в тригонометрическом виде в градусах.
    while line != None:
        if line == "":
            line = next (iterator, None)
            continue
        try:
            splitted = line.split (' ')
            cmd = splitted[0]
            arg = 0
            if len (splitted) > 1:
                if (splitted[1].lstrip ('-').isdigit()):
                    arg = int (splitted[1])
            func += tablevel * '\t'
            if cmd == "forward" or cmd == "backward":
                func += f"tur.{cmd} ({arg} * size)"
            elif cmd == "left" or cmd == "right":
                func += f"tur.{cmd} ({arg})"
            elif cmd == "break" or cmd == "continue":
                func += cmd
            elif cmd == "for":
                func += f"for {names[tablevel - 1]} in range ({arg}):"
                tablevel += 1
            elif cmd == "print":
                func += f"print ({splitted[1]})"
            elif cmd == "while":
                value1 = splitted[1]
                condition = splitted[2]
                value2 = splitted[2]
                func += f"while {value1} {condition} {value2}:"
                tablevel += 1
            elif cmd == "do_while":
                value1 = splitted[1]
                condition = splitted[2]
                value2 = splitted[3]
                do_while_conditions_level[tablevel + 1] = f"{value1} {condition} {value2}"
                func += "while True:"
                tablevel += 1
            elif cmd == "if":
                condition = splitted[1]
                func += f"if {condition}:"
                tablevel += 1
            elif cmd == "]":
                if tablevel in do_while_conditions_level:
                    func += f"if not ({do_while_conditions_level[tablevel]}):break"
                    del do_while_conditions_level[tablevel]
                tablevel -= 1
            elif cmd == "declare":
                func += f"{splitted[1]} = {splitted[2]}"
            elif cmd == "mod":
                change = splitted[2]
                func += f"{splitted[1]}{change}"
            elif cmd == "up" or cmd == "down":
                func += f"tur.{cmd}()"
            elif cmd == "move":
                dx = float (splitted[1])
                dy = float (splitted[2])
                func += f"tur.setpos (tur.pos()[0] + {dx} * size, tur.pos()[1] + {dy} * size)"
            elif cmd == "setpos":
                newx, newy = float (splitted[1]), float (splitted[2])
                func += f"tur.setpos ({newx} * size, {newy} * size)"
            elif cmd == "circle":
                radius = arg
                a, b, alpha = map (int, splitted[2:5])#alpha в градусах
                length = (a * a + b * b) ** .5
                if (a == 0 and b == 0) or fabs (radius) < 1e-4 or alpha == 0:
                    print ("Cannot draw a circle!")
                    sys.exit (1)
                elif not isclose (abs (radius), abs (length)):
                    print ("Invalid center or radius!")
                    sys.exit (1)
                func += "x, y = tur.pos ()\n"
                #Строго по часовой!
                #Center: (x + a; y + b)
                #Current: (x;y)
                #Нужно повернуть на угол beta, чтобы мы были на прямой касательной к окружности.
                #Немного геометрии. Нужно найти такой вектор{dx, dy}, который был бы перпендикулярен {a;b}
                #dx*a+dy*b=0=>dx=(-dy*b)/a
                #dx/dy=-b/a
                #пусть вектор имеет координаты {-b, a}
                #Так как графиком x/y=-b/a является прямая, то cos beta=-b/sqrt(a*a+b*b), sin beta=a/sqrt(a*a+b*b)
                cosine = -b / length
                sine = a / length
                angle = 0
                if cosine >= 0:
                    #I или IV координатная четверть
                    angle = asin (sine)
                else:
                    #II или III
                    if sine >= 0:
                        #II, arccos даст верный угол
                        angle = acos (cosine)
                    else:
                        #III
                        angle = asin (-sine) + pi
                func += tablevel * '\t' + f"tur.setheading ({angle * 180 / pi})\n"
                func += tablevel * '\t' + f"tur.circle ({-radius} * size, {alpha})"
            elif cmd == "heading":
                func += f"tur.setheading ({arg})"
            else:
                raise ValueError ("Invalid syntax")
            func += '\n'
            if (len (splitted) > 2) or (len (splitted) > 1 and cmd in unary):
                _from = 1 if cmd in unary else (5 if cmd in whiles or cmd in fifth else (3 if cmd in triple else 2))
                #print (_from,end = ':')
                #print (*(splitted[:_from]),sep=' ')
                line = ' '.join (splitted[_from:])
                continue
            line = next (iterator, None)
        except BaseException as e:
            print (e)
            print (line)
            print (splitted)
            print (func)
            sys.exit (1)
    print (func)
    sc = turtle.Screen()
    tur = turtle.Turtle()
    tur.speed ("fastest")
    xcount = args.xcount
    ycount = args.ycount
    size = args.size
    xshift = -xcount * size // 2
    yshift = -ycount * size // 2
    def draw(val, axis='x'):
        mv = size * (ycount if axis == 'x' else xcount)
        tur.up()
        tur.setpos (xshift + val, yshift) if axis == 'x' else tur.setpos (xshift, yshift + val)
        tur.down()
        if (axis == 'y' and val + yshift == 0) or (axis == 'x' and val + xshift == 0):
            default_color, default_width = tur.color (), tur.width ()
            default_color = default_color[0]
            tur.width (min ((size + 3) // 4, default_width * 2))
            tur.color ("blue")
            tur.forward(mv)
            tur.width(default_width)
            tur.color (default_color)
        else:
            tur.forward (mv)
    sc.setup(xcount * size, ycount * size)
    tur.up()
    tur.setpos(xshift, yshift)
    tur.down()
    #tur.left(90)
    for i in range (ycount):
        draw(size * (i + 1), 'y')
    tur.up()
    tur.setpos(xshift,yshift)#Крайний левый нижний.
    tur.down()
    tur.left (90)
    for i in range (xcount + 1):
        draw(size*(i+1), 'x')
    tur.up()
    
    tur.setpos(0,0)
    tur.setheading(90)
    tur.down()
    tur.color ("red")
    input_locals = {"tur" : tur, "size" : size, "isclose" : isclose, "sin" : sin, "cos" : cos, "asin" : asin, "acos" : acos, "pi" : pi}
    
    exec (compile(func + "\n__temp__()", "<string>", mode="exec"), input_locals)
    print ("Done!")
    time.sleep (120)
    #tur.hideturtle()
if __name__ == "__main__":
    try:
        main ()
    except KeyboardInterrupt:
        print ("Bye!")
