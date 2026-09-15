import logging as lg
from pathlib import Path

from PIL import Image, ImageFile


class BrailleArtGenerator:
    """Braille-based text art generator."""

    def __init__(self, image_filepath: Path | str) -> None:
        """Initialize braille art generator.

        Args:
            image_filepath (Path | str): input image file path

        """
        self.logger = lg.getLogger("brailler.generator")

        self.image_filepath = Path(image_filepath).absolute()
        self._image: Image.Image | None = None


    def _load_image(
            self, *,
            resolution: tuple[str, str],
            threshold: int,
            resampling_algorithm: Image.Resampling,
            invert: bool,
        ) -> Image.Image:

        # loading
        if self._image is None:
            self.logger.info("loading image")
            image: Image.Image = Image.open(self.image_filepath)

            self.logger.debug("converting image to luminance mode")
            image = image.convert("L")

            self._image = image
        
        else:
            self.logger.debug("using cached image")
            image = self._image
        
        # resizing
        self.logger.debug("resizing image (resolution=%s, resampling_algorithm=%s)", resolution, resampling_algorithm.name)
        image = image.resize(resolution, resampling_algorithm)

        # binarizing
        low, high = (0, 255) if not invert else (255, 0)
        self.logger.debug("binarizing image (threshold=%d, invert=%d)", threshold, invert)
        image = image.point(
            lambda p: low if p < threshold else high,
            mode="L",
        )

        return image  # noqa: RET504
        

    def generate(
            self, *,
            resolution: tuple[str, str],
            threshold: int,
            resampling_algorithm: Image.Resampling = Image.Resampling.LANCZOS,
            invert: bool = False,
        ) -> str:
        """Generate Braille-art.

        Args:
            resolution (tuple[str, str]): art resolution (in characters)
            threshold (int): image binarization threshold
            resampling_algorithm (Image.Resampling, optional): image resampling algorithm.
                Defaults to Image.Resampling.LANCZOS.
            invert (bool, optional): invert image colors. Defaults to False.

        Returns:
            str: Braille-art

        """
        resolution = (resolution[0] * 2, resolution[1] * 4)

        image = self._load_image(
            resolution=resolution,
            threshold=threshold,
            resampling_algorithm=resampling_algorithm,
            invert=invert,
        )

        blocks = self._split_image_in_blocks(image, resolution)

        return self._generate_art(blocks)
    

    def _split_image_in_blocks(self, image: ImageFile.ImageFile, resolution: tuple[int, int]) -> list[list[tuple]]:
        self.logger.info("splitting image in blocks")

        blocks = []
        for y in range(0, resolution[1], 4):
            row = []
            for x in range(0, resolution[0], 2):
                image_block = image.crop((
                    x, y, x+2, y+4,
                ))

                block = tuple(image_block.getdata())
                row.append(block)
            blocks.append(row)
        
        return blocks
    
    
    def _generate_art(self, blocks: list[list[tuple]]) -> str:
        art = ""
        blocks_len = len(blocks)

        for i, blocks_row in enumerate(blocks, start=1):
            for block in blocks_row:
                art += self._block_to_braille(block)
            
            if i != blocks_len:
                art += "\n"
        
        return art
                

    def _block_to_braille(self, block: list) -> str:
        braille_bits = 0

        if block[0]:
            braille_bits |= 0b00000001
        if block[2]:
            braille_bits |= 0b00000010
        if block[4]:
            braille_bits |= 0b00000100
        if block[1]:
            braille_bits |= 0b00001000
        if block[3]:
            braille_bits |= 0b00010000
        if block[5]:
            braille_bits |= 0b00100000
        if block[6]:
            braille_bits |= 0b01000000
        if block[7]:
            braille_bits |= 0b10000000

        return chr(0x2800 + braille_bits)

