import turtle

def draw_square(size, color):
    turtle.fillcolor(color)
    turtle.begin_fill()
    for _ in range(4):
        turtle.forward(size)
        turtle.left(90)
    turtle.end_fill()

def draw_triangle(size, color):
    turtle.fillcolor(color)
    turtle.begin_fill()
    for _ in range(3):
        turtle.forward(size)
        turtle.left(120)
    turtle.end_fill()

def draw_house():
    turtle.shape("turtle")
    turtle.speed(3)
    
    # Move to start position
    turtle.penup()
    turtle.goto(-100, -100)
    turtle.pendown()
    
    # Draw the walls
    draw_square(200, "lightblue")
    
    # Move to roof position
    turtle.penup()
    turtle.goto(-100, 100)
    turtle.pendown()
    
    # Draw the roof
    draw_triangle(200, "brown")
    
    # Draw the door
    turtle.penup()
    turtle.goto(-30, -100)
    turtle.pendown()
    draw_square(60, "darkred")
    
    # Draw left window
    turtle.penup()
    turtle.goto(-80, 20)
    turtle.pendown()
    draw_square(40, "yellow")
    
    # Draw right window
    turtle.penup()
    turtle.goto(40, 20)
    turtle.pendown()
    draw_square(40, "yellow")
    
    # Hide turtle
    turtle.hideturtle()
    
    # Keep window open
    turtle.done()

# Call function to draw the house
draw_house()
