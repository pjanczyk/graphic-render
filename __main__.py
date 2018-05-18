import json
import re
from argparse import ArgumentParser

import jsonschema
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

import Schema
from ImageViewer import show_image_viewer


class ColorNotFoundException(Exception):
    pass


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('input', metavar='INPUT', help='input JSON file, description of image')
    parser.add_argument('-o', '--output', dest='output', help='save image to file (PNG)')
    return parser.parse_args()


class Graphic:
    def __init__(self, graphic):
        self.palette = {}
        self.palette = {name: self.decode_color(value)
                        for (name, value) in graphic['Palette'].items()}

        screen = graphic['Screen']
        self.screen_width = screen['width']
        self.screen_height = screen['height']
        self.screen_background = self.decode_color(screen['bg_color'])
        self.screen_foreground = self.decode_color(screen['fg_color'])

        figure_types = {
            'point': Point,
            'rectangle': Rectangle,
            'square': Square,
            'circle': Circle,
            'polygon': Polygon
        }

        def decode_figure(figure):
            type_ = figure['type']
            constructor = figure_types[type_]
            return constructor(figure, self)

        self.figures = list(map(decode_figure, graphic['Figures']))

    def decode_color(self, val):
        def make_color(r, g, b):
            return (r << 16) | (g << 8) | b

        if re.match(r'^#[0-9A-Fa-f]{6}$', val):
            r = int(val[1:3], 16)
            g = int(val[3:5], 16)
            b = int(val[5:7], 16)
            return make_color(r, g, b)

        elif re.match(r'^\(\d+,\d+,\d+\)$', val):
            r, g, b = map(int, val[1:-1].split(','))
            return make_color(r, g, b)

        else:
            color = self.palette.get(val)
            if color is None:
                raise ColorNotFoundException(f"Not found color '{val}'")
            return color

    def render(self):
        image = Image.new('RGB', (self.screen_width, self.screen_height), self.screen_background)
        draw = ImageDraw.Draw(image)

        for figure in self.figures:
            figure.draw(draw)

        return image


class Figure:
    def __init__(self, figure, graphic):
        if 'color' in figure:
            self.color = graphic.decode_color(figure['color'])
        else:
            self.color = graphic.screen_foreground


class Point(Figure):
    def __init__(self, figure, graphic):
        super().__init__(figure, graphic)
        self.x = figure['x']
        self.y = figure['y']

    def draw(self, draw):
        draw.point([self.x, self.y], self.color)


class Rectangle(Figure):
    def __init__(self, figure, graphic):
        super().__init__(figure, graphic)
        self.x = figure['x']
        self.y = figure['y']
        self.width = figure['width']
        self.height = figure['height']

    def draw(self, draw):
        x0 = self.x - self.width / 2
        y0 = self.y - self.height / 2
        x1 = self.x + self.width / 2
        y1 = self.y + self.height / 2

        draw.rectangle([x0, y0, x1, y1], self.color)


class Square(Figure):
    def __init__(self, figure, graphic):
        super().__init__(figure, graphic)
        self.x = figure['x']
        self.y = figure['y']
        self.size = figure['size']

    def draw(self, draw):
        x0 = self.x - self.size / 2
        y0 = self.y - self.size / 2
        x1 = self.x + self.size / 2
        y1 = self.y + self.size / 2

        draw.rectangle([x0, y0, x1, y1], self.color)


class Circle(Figure):
    def __init__(self, figure, graphic):
        super().__init__(figure, graphic)
        self.x = figure['x']
        self.y = figure['y']
        self.radius = figure['radius']

    def draw(self, draw):
        x0 = self.x - self.radius / 2
        y0 = self.y - self.radius / 2
        x1 = self.x + self.radius / 2
        y1 = self.y + self.radius / 2

        draw.ellipse([x0, y0, x1, y1], self.color)


class Polygon(Figure):
    def __init__(self, figure, graphic):
        super().__init__(figure, graphic)
        self.points = [tuple(point) for point in figure['points']]

    def draw(self, draw):
        draw.polygon(self.points, self.color)


def main():
    args = parse_arguments()
    input_ = args.input
    output = args.output

    with open(input_) as f:
        data = json.load(f)

    jsonschema.validate(data, Schema.schema)

    graphic = Graphic(data)
    image = graphic.render()

    if output:
        image.save(output, format='PNG')

    image_qt = ImageQt(image)
    exit(show_image_viewer(image_qt))


if __name__ == '__main__':
    main()
