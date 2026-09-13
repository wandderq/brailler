import logging as lg
import sys
from argparse import ArgumentParser
from pathlib import Path

import colorlog as clg
import numpy as np
from PIL import Image

logger = lg.getLogger('brailler')
logger.handlers.clear()
logger.setLevel(lg.INFO)

stream_handler = lg.StreamHandler(stream=sys.stdout)
stream_handler.setFormatter(clg.ColoredFormatter(
    fmt="{log_color}[{levelname}]: {message}{reset}",
    style='{',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red'
    }
))

logger.addHandler(stream_handler)


class BrailleArt:
    def __init__(self, input_file_path: Path, size: tuple[int, int], threshold: int) -> None:
        self.input_file_path = input_file_path
        self.size = size
        self.threshold = threshold


    def load_input(self) -> Image:
        logger.debug(f'loading input image from {self.input_file_path}')
        img = Image.open(self.input_file_path)
        
        logger.debug('converting to mode=L')
        img = img.convert('L')
        
        logger.debug(f'resizing image to {self.size}')
        img = img.resize(self.size, Image.Resampling.LANCZOS)
        
        logger.debug(f'binaring image with threshold {self.threshold}')
        img = img.point(lambda x: 0 if x < self.threshold else 1, 'L')

        return img
    

    def generate(self) -> str:
        input_image = self.load_input()

        logger.debug('splitting image to 2x4 blocks (or 4x2 idk)')
        blocks = []
        for y in range(0, self.size[1], 2):
            blocks_row = []
            for x in range(0, self.size[0], 4):
                block = input_image.crop((
                    x,
                    y,
                    x + 2,
                    y + 4
                ))
                block_pixels = list(block.getdata())
                blocks_row.append(block_pixels)
            blocks.append(blocks_row)
        
        logger.debug('getting chars for every block')
        art = ""
        for row in blocks:
            for pixels in row:
                char = self.pixels_to_braille(pixels)
                art += char
            art += '\n'
        
        logger.debug('done!')
        return art

    def pixels_to_braille(self, pixel_block: list) -> str:
        matrix = np.array([
            [pixel_block[0], pixel_block[1]],
            [pixel_block[2], pixel_block[3]],
            [pixel_block[4], pixel_block[5]],
            [pixel_block[6], pixel_block[7]],
        ], dtype=int)

        braille_bits = 0

        if matrix[0, 0]:
            braille_bits |= 0b00000001

        if matrix[1, 0]:
            braille_bits |= 0b00000010

        if matrix[2, 0]:
            braille_bits |= 0b00000100

        if matrix[0, 1]:
            braille_bits |= 0b00001000

        if matrix[1, 1]:
            braille_bits |= 0b00010000

        if matrix[2, 1]:
            braille_bits |= 0b00100000

        if matrix[3, 0]:
            braille_bits |= 0b01000000

        if matrix[3, 1]:
            braille_bits |= 0b10000000
        
        unicode_code = 0x2800 + braille_bits

        return chr(unicode_code)


class BraillerCLI:
    def __init__(self) -> None:
        self.argparser = ArgumentParser(
            description="braille-based art generator"
        )
        
        self.argparser.add_argument(
            'input',
            type=Path,
            help='input image file (png/jpg)'
        )
        
        self.argparser.add_argument(
            '-o', '--output',
            default=None,
            help='output text file (default: None) (can be derived from input filename using \'[input]\')'
        )
        
        self.argparser.add_argument(
            '-s', '--size',
            default='128x64',
            help='output dimensions in WIDTHxHEIGHT format (default: 128x64)',
        )
        
        self.argparser.add_argument(
            '-t', '--threshold',
            type=int,
            default=160,
            help='binarization threshold (0-255) (default: 160)'
        )

        self.argparser.add_argument(
            '-p', '--print',
            action='store_true',
            help='print the result to the console'
        )
        
        self.argparser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='verbose mode (detailed processing information)'
        )
    

    def run(self) -> int:
        args = self.argparser.parse_args()

        if args.verbose:
            logger.setLevel(lg.DEBUG)
        
        if not args.input.exists():
            logger.error(f'{args.input} not found!')
            return 1
        
        if not args.output and not args.print:
            logger.error('nothing to do!')
            return 0

        input_file_path = args.input.absolute()
        size = [int(s) for s in args.size.split('x')][:2]
        threshold = args.threshold

        generator = BrailleArt(
            input_file_path,
            size,
            threshold
        )

        art = generator.generate()

        if args.output is not None:
            output_file_path = args.output if args.output != '[input]' else Path(input_file_path.name + '.txt')
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(art)
                logger.info(f'art writed to the {output_file_path}')
        
        if args.print:
            print(art, flush=True)
        
        return 0


def run_cli():
    try:
        app = BraillerCLI()
        exit_code = app.run()
        sys.exit(exit_code)

    except KeyboardInterrupt:
        sys.exit(0)
