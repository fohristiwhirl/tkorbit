import math, re, tkinter, tkinter.filedialog

WIDTH = 1024
HEIGHT = 768


class Root(tkinter.Tk):
    def __init__(self, *args, **kwargs):

        tkinter.Tk.__init__(self, *args, **kwargs)
        self.resizable(width = False, height = False)
        virtue = Virtue(self, width = WIDTH, height = HEIGHT, bd = 0, highlightthickness = 0)

        menubar = tkinter.Menu(self)

        file_menu = tkinter.Menu(menubar, tearoff = 0)
        file_menu.add_command(label = "Open", command = virtue.loader)
        file_menu.add_command(label = "Save As", command = virtue.saver)
        menubar.add_cascade(label = "File", menu = file_menu)

        delay_menu = tkinter.Menu(menubar, tearoff = 0)
        delay_menu.add_radiobutton(label = "2", variable = virtue.delay, value = 2)
        delay_menu.add_radiobutton(label = "4", variable = virtue.delay, value = 4)
        delay_menu.add_radiobutton(label = "8", variable = virtue.delay, value = 8)
        delay_menu.add_radiobutton(label = "16", variable = virtue.delay, value = 16)
        delay_menu.add_radiobutton(label = "32", variable = virtue.delay, value = 32)
        menubar.add_cascade(label = "Delay", menu = delay_menu)

        speed_menu = tkinter.Menu(menubar, tearoff = 0)
        speed_menu.add_radiobutton(label = "32", variable = virtue.speed, value = 32)
        speed_menu.add_radiobutton(label = "16", variable = virtue.speed, value = 16)
        speed_menu.add_radiobutton(label = "8", variable = virtue.speed, value = 8)
        speed_menu.add_radiobutton(label = "4", variable = virtue.speed, value = 4)
        speed_menu.add_radiobutton(label = "2", variable = virtue.speed, value = 2)
        speed_menu.add_radiobutton(label = "1", variable = virtue.speed, value = 1)
        menubar.add_cascade(label = "Speed", menu = speed_menu)

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

    def __str__(self):
        return "\"{}\" {} {} {} {} {} {} {} {}".format(
            self.name,
            self.x,
            self.y,
            self.z,
            self.speedx,
            self.speedy,
            self.speedz,
            self.mass,
            self.colour
        )


class Virtue(tkinter.Canvas):
    def __init__(self, owner, *args, **kwargs):
        tkinter.Canvas.__init__(self, owner, *args, **kwargs)
        self.owner = owner

        self.age = 0

        self.delay = tkinter.IntVar(value = 4)
        self.speed = tkinter.IntVar(value = 1)

        self.planar = tkinter.IntVar(value = 0)

        self.camera_x = 0
        self.camera_y = 0
        self.camera_z = 0
        self.zoom = 0.15
        self.lock = None

        self.bodies = []

        self.load("default.txt")

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
        return (int(screenx), int(screeny))

    def draw(self):
        self.delete(tkinter.ALL)    # DESTROY all! Perhaps instead we should move the objects already present, hmm...?

        self.create_rectangle(0, 0, WIDTH, HEIGHT, fill = "black")
        for b in self.bodies:
            screenx, screeny = self.get_screen_pos(b)
            self.create_oval(screenx - 2, screeny - 2, screenx + 2, screeny + 2, fill = b.colour)

    def iterate(self):

        for n in range(self.speed.get()):
            self.move_stuff(Body.gravitate_3d, Body.move_3d)
        self.draw()
        self.after(self.delay.get(), self.iterate)

    def load(self, filename):

        print("Loading {}".format(filename))

        newbodies = []

        try:
            with open(filename) as infile:
                for n, line in enumerate(infile):
                    extract = re.search(r'\"(.+)\"\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
                    try:
                        name = extract.group(1)
                        x = extract.group(2)
                        y = extract.group(3)
                        z = extract.group(4)
                        speedx = extract.group(5)
                        speedy = extract.group(6)
                        speedz = extract.group(7)
                        mass = extract.group(8)
                        colour = extract.group(9)

                        body = Body(
                               pos = [float(x), float(y), float(z)],
                               speed = [float(speedx), float(speedy), float(speedz)],
                               mass = float(mass),
                               name = name,
                               colour = colour
                               )

                        newbodies.append(body)
                    except:
                        if not line.isspace():
                            print("Ignored #{}:  {}".format(n, line))
        except:
            print("Failed to load {}".format(filename))

        self.bodies = newbodies

        if len(self.bodies):
            self.lock = self.bodies[0]
        else:
            self.lock = None

    def loader(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename:
            self.load(filename)

    def save(self, filename):
        try:
            with open(filename, "w") as outfile:
                for b in self.bodies:
                    outfile.write(b.__str__())
                    outfile.write("\n")
            print("Saved {}".format(filename))
        except:
            print("Failed to save {}".format(filename))

    def saver(self):
        filename = tkinter.filedialog.asksaveasfilename(defaultextension = ".txt")
        if filename:
            self.save(filename)


if __name__ == "__main__":
    app = Root()
    app.mainloop()
