import turtle
import math

screen = turtle.Screen()
screen.bgcolor("black")

t = turtle.Turtle()
t.speed(0)
t.width(2)

colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"]

def heart(t_param, scale=11):
    x = 16 * (math.sin(t_param))**3
    y = (13 * math.cos(t_param) 
         - 5 * math.cos(2*t_param) 
         - 2 * math.cos(3*t_param) 
         - math.cos(4*t_param))
    return x * scale, y * scale

# 1. Sawiridda wadnaha
for i in range(250):
    t.pencolor(colors[i % len(colors)])
    pos = heart(i / 12)
    t.goto(pos)
    t.goto(0, 0)

# 2. Qoraalka Sare
t.penup()
t.goto(0, 180)         
t.pencolor("#FFFF00")  
t.write("Qofkaan u diyaariyey waa:", align="center", font=("Arial", 12, "bold"))

# 3. Magaca hoose oo aad hoos u degan
t.goto(0, -220)        
t.pencolor("#FF3366")  
t.write("Asmiitah", align="center", font=("Arial", 18, "bold"))

t.hideturtle()
turtle.done()

