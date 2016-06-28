import math, tkinter

WIDTH = 1024
HEIGHT = 768


class Root(tkinter.Tk):
    def __init__(self, *args, **kwargs):

        tkinter.Tk.__init__(self, *args, **kwargs)
        self.resizable(width = False, height = False)
        virtue = Virtue(self, width = WIDTH, height = HEIGHT, bd = 0, highlightthickness = 0)

        menubar = tkinter.Menu(self)

        file_menu = tkinter.Menu(menubar, tearoff = 0)
        file_menu.add_command(label = "Open (Fixme)", command = lambda : None)
        file_menu.add_command(label = "Save (Fixme)", command = lambda : None)
        menubar.add_cascade(label = "File", menu = file_menu)

        delay_menu = tkinter.Menu(menubar, tearoff = 0)
        delay_menu.add_radiobutton(label = "5", variable = virtue.delay, value = 5)
        delay_menu.add_radiobutton(label = "10", variable = virtue.delay, value = 10)
        delay_menu.add_radiobutton(label = "15", variable = virtue.delay, value = 15)
        delay_menu.add_radiobutton(label = "20", variable = virtue.delay, value = 20)
        menubar.add_cascade(label = "Delay", menu = delay_menu)

        view_menu = tkinter.Menu(menubar, tearoff = 0)
        view_menu.add_radiobutton(label = "Polar", variable = virtue.planar, value = 0)
        view_menu.add_radiobutton(label = "Planar", variable = virtue.planar, value = 1)
        menubar.add_cascade(label = "View", menu = view_menu)

        self.config(menu = menubar)
        virtue.pack()


class Body():
    def __init__(self, pos, speed, mass = 0, name = "Unnamed", colour = "red"):
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]
        self.speedx = speed[0]
        self.speedy = speed[1]
        self.speedz = speed[2]
        self.mass = mass
        self.name = name
        self.colour = colour

    def gravitate_3d(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        distance_squared = dx * dx + dy * dy + dz * dz
        distance = math.sqrt(distance_squared)
        try:
            # This is now very optimised and isn't intuitive at all...
            adjusted_force = other.mass / (distance_squared * distance)
            self.speedx += dx * adjusted_force
            self.speedy += dy * adjusted_force
            self.speedz += dz * adjusted_force
        except ZeroDivisionError:
            pass

    def move_3d(self):
        self.x += self.speedx
        self.y += self.speedy
        self.z += self.speedz


class Virtue(tkinter.Canvas):
    def __init__(self, owner, *args, **kwargs):
        tkinter.Canvas.__init__(self, owner, *args, **kwargs)
        self.owner = owner

        self.age = 0
        self.delay = tkinter.IntVar(value = 5)
        self.planar = tkinter.IntVar(value = 0)

        self.camera_x = 0
        self.camera_y = 0
        self.camera_z = 0
        self.zoom = 0.15
        self.lock = None

        self.bodies = []

        self.bodies.append(Body([0,0,0], [0,0,0], 3333, name = "Sun", colour = "yellow"))
        self.bodies.append(Body([0,-100,0], [6,0,0], 5, name = "Mercury"))
        self.bodies.append(Body([0,200,0], [-4,0,0], 5, name = "Venus"))
        self.bodies.append(Body([-780,0,0], [0,-2.1,0], 10, name = "Earth", colour = "green"))
        self.bodies.append(Body([-840,0,0], [0,-1.67,0], 0.08, name = "Luna",  colour = "gray"))
        # Mars died
        self.bodies.append(Body([2000,0,0], [0,1.29,0], 120, name = "Jupiter"))
        self.bodies.append(Body([2050,0,0], [0,2.85,0], 0.04, name = "Io", colour = "gray"))
        self.bodies.append(Body([1880,0,0], [0,0.3,0], 0.04, name = "Europa", colour = "gray"))
        self.bodies.append(Body([-2200,2200,0], [-0.749,-0.749,0], 30, name = "Saturn"))
        self.bodies.append(Body([-2300,2300,0], [-1.1,-1.1,0], 0.02, name = "Titan", colour = "gray"))

        self.lock = self.bodies[0]

        self.iterate()


    def move_stuff(self, gravitate_func, move_func):

        for a in self.bodies:
            for b in self.bodies:
                if a is not b:
                    if b.mass:
                        gravitate_func(a, b)

        self.age += 1

        for a in self.bodies:
            move_func(a)

    def get_screen_pos(self, body):
        if self.lock:
            self.camera_x = self.lock.x
            self.camera_y = self.lock.y
            self.camera_z = self.lock.z
        dx = body.x - self.camera_x
        dy = body.y - self.camera_y
        dz = body.z - self.camera_z
        dx *= self.zoom
        dy *= self.zoom
        dz *= self.zoom
        screenx = dx + WIDTH / 2
        if self.planar.get():
            screeny = dz + HEIGHT / 2
        else:
            screeny = dy + HEIGHT / 2
        return (screenx, screeny)

    def draw(self):
        self.delete(tkinter.ALL)    # DESTROY all! Perhaps instead we should move the objects already present, hmm...?

        self.create_rectangle(0, 0, WIDTH, HEIGHT, fill = "black")
        for b in self.bodies:
            screenx, screeny = self.get_screen_pos(b)
            self.create_oval(screenx - 2, screeny - 2, screenx + 2, screeny + 2, fill = b.colour)

    def iterate(self):

        self.move_stuff(Body.gravitate_3d, Body.move_3d)
        self.draw()
        self.after(self.delay.get(), self.iterate)


if __name__ == "__main__":
    app = Root()
    app.mainloop()
