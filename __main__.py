import json
from argparse import ArgumentParser

from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

from ImageViewer import show_image_viewer


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('input', metavar='INPUT', help='input JSON file, description of image')
    parser.add_argument('-o', '--output', dest='output', help='save image to file (PNG)')
    return parser.parse_args()


def require_number(val):
    assert type(val) in [int, float]
    return val


def require_color(val, palette=None):
    assert type(val) is str
    if len(val) == 7 and val[0] == '#':
        r = int(val[1:3], 16)
        g = int(val[3:5], 16)
        b = int(val[5:7], 16)
        return (r << 16) | (g << 8) | b
    elif len(val) >= 2 and val[0] == '(' and val[-1] == ')':
        rgb = val[1:-1].split(',')
        assert len(rgb) == 3
        [r, g, b] = map(int, rgb)
        return (r << 16) | (g << 8) | b
    else:
        return require_color(palette[val])


def main():
    args = parse_arguments()
    input = args.input
    output = args.output

    with open(input) as f:
        data = json.load(f)

    print(json.dumps(data, sort_keys=True, indent=4))

    palette = data['Palette']

    screen = data['Screen']
    screen_width = screen['width']
    screen_height = screen['height']
    screen_background = require_color(screen['bg_color'], palette)
    screen_foreground = require_color(screen['fg_color'], palette)

    image = Image.new('RGB', (screen_width, screen_height), screen_background)

    draw = ImageDraw.Draw(image)

    for figure in data['Figures']:
        type_ = figure['type']

        if type_ == 'point':
            x = require_number(figure['x'])
            y = require_number(figure['y'])
            if 'color' in figure:
                color = require_color(figure['color'], palette)
            else:
                color = screen_foreground
            draw.point([x, y], color)

        elif type_ == 'rectangle':
            x = require_number(figure['x'])
            y = require_number(figure['y'])
            width = require_number(figure['width'])
            height = require_number(figure['height'])

            if 'color' in figure:
                color = require_color(figure['color'], palette)
            else:
                color = screen_foreground

            x0 = x - width / 2
            y0 = y - height / 2
            x1 = x + width / 2
            y1 = y + height / 2

            draw.rectangle([x0, y0, x1, y1], color)

        elif type_ == 'square':
            x = require_number(figure['x'])
            y = require_number(figure['y'])
            size = require_number(figure['size'])

            if 'color' in figure:
                color = require_color(figure['color'], palette)
            else:
                color = screen_foreground

            x0 = x - size / 2
            y0 = y - size / 2
            x1 = x + size / 2
            y1 = y + size / 2

            draw.rectangle([x0, y0, x1, y1], color)

        elif type_ == 'circle':
            x = require_number(figure['x'])
            y = require_number(figure['y'])
            radius = require_number(figure['radius'])

            if 'color' in figure:
                color = require_color(figure['color'], palette)
            else:
                color = screen_foreground

            x0 = x - radius / 2
            y0 = y - radius / 2
            x1 = x + radius / 2
            y1 = y + radius / 2

            draw.ellipse([x0, y0, x1, y1], color)

        elif type_ == 'polygon':

            if 'color' in figure:
                color = require_color(figure['color'], palette)
            else:
                color = screen_foreground

            def map_points(points):
                assert type(points) is list

                for point in points:
                    assert type(point) is list and len(point) == 2
                    yield (require_number(point[0]), require_number(point[1]))

            points = figure['points']
            points = list(map_points(points))

            draw.polygon(points, color)

        else:
            assert False

    if output:
        image.save(output, format='PNG')

    image_qt = ImageQt(image)
    exit(show_image_viewer(image_qt))


if __name__ == '__main__':
    main()
