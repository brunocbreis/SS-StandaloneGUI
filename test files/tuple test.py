from dataclasses import dataclass

@dataclass
class Canvas:
    width: int
    height: int

    @property
    def resolution(self):
        return (self.width,self.height)

    @resolution.setter
    def resolution(self, value):
        self.width = value[0]
        self.height = value[1]

canvas = Canvas(1920,1080)

print(canvas)

canvas.resolution = (3840,2160)

print(canvas)