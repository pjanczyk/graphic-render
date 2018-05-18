import json
import re
import sys
from argparse import ArgumentParser

import jsonschema
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

import Schema
from ImageViewer import show_image_viewer


class ColorNotFoundException(Exception):
    pass


class Graphic:
    def __init__(self, data):
        self.palette = {}
        self.palette = {name: self.decode_color(value)
                        for (name, value) in data['Palette'].items()}

        screen = data['Screen']
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

        self.figures = [decode_figure(figure) for figure in data['Figures']]

    def decode_color(self, val: str) -> int:
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

    def render(self) -> Image:
        image = Image.new('RGB', (self.screen_width, self.screen_height), self.screen_background)
        draw = ImageDraw.Draw(image)

        for figure in self.figures:
            figure.draw(draw)

        return image


class Figure:
    def __init__(self, data, graphic: Graphic):
        if 'color' in data:
            self.color = graphic.decode_color(data['color'])
        else:
            self.color = graphic.screen_foreground


class Point(Figure):
    def __init__(self, data, graphic: Graphic):
        super().__init__(data, graphic)
        self.x = data['x']
        self.y = data['y']

    def draw(self, draw: ImageDraw):
        draw.point([self.x, self.y], self.color)


class Rectangle(Figure):
    def __init__(self, data, graphic: Graphic):
        super().__init__(data, graphic)
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']

    def draw(self, draw: ImageDraw):
        x0 = self.x - self.width / 2
        y0 = self.y - self.height / 2
        x1 = self.x + self.width / 2
        y1 = self.y + self.height / 2

        draw.rectangle([x0, y0, x1, y1], self.color)


class Square(Figure):
    def __init__(self, data, graphic: Graphic):
        super().__init__(data, graphic)
        self.x = data['x']
        self.y = data['y']
        self.size = data['size']

    def draw(self, draw: ImageDraw):
        x0 = self.x - self.size / 2
        y0 = self.y - self.size / 2
        x1 = self.x + self.size / 2
        y1 = self.y + self.size / 2

        draw.rectangle([x0, y0, x1, y1], self.color)


class Circle(Figure):
    def __init__(self, data, graphic: Graphic):
        super().__init__(data, graphic)
        self.x = data['x']
        self.y = data['y']
        self.radius = data['radius']

    def draw(self, draw: ImageDraw):
        x0 = self.x - self.radius / 2
        y0 = self.y - self.radius / 2
        x1 = self.x + self.radius / 2
        y1 = self.y + self.radius / 2

        draw.ellipse([x0, y0, x1, y1], self.color)


class Polygon(Figure):
    def __init__(self, data, graphic: Graphic):
        super().__init__(data, graphic)
        self.points = [tuple(point) for point in data['points']]

    def draw(self, draw: ImageDraw):
        draw.polygon(self.points, self.color)


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('input', metavar='INPUT', help='input JSON file, description of image')
    parser.add_argument('-o', '--output', dest='output', help='save image to file (PNG)')
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        with open(args.input) as f:
            raw_json = f.read()
    except Exception as e:
        print(f"Error: Failed to load input file:", e)
        sys.exit(1)

    try:
        data = json.loads(raw_json)
    except Exception as e:
        print(f"Error: Invalid JSON file: ", e)
        sys.exit(1)

    try:
        jsonschema.validate(data, Schema.schema)
    except jsonschema.exceptions.ValidationError as e:
        print("Error: JSON does not match schema:", e)
        sys.exit(1)

    try:
        graphic = Graphic(data)
    except ColorNotFoundException as e:
        print("Error:", e)
        sys.exit(1)

    image = graphic.render()

    if args.output:
        image.save(args.output, format='PNG')

    image_qt = ImageQt(image)
    sys.exit(show_image_viewer(image_qt))


if __name__ == '__main__':
    main()
