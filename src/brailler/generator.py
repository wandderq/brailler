import logging as lg
from pathlib import Path

from PIL import Image

logger = lg.getLogger(__name__)

class BrailleArtGenerator:
    """Braille-based text art generator."""

    def __init__(self, image_filepath: Path | str, *, debug: bool = False) -> None:
        """Initialize braille art generator.

        Args:
            image_filepath (Path | str): input image file path
            debug (bool): enable debug features

        """
        self.image_filepath = Path(image_filepath).absolute()
        self._image: Image.Image | None = None

        self.debug = debug
        if debug:
            self.debug_path = Path.cwd() / "debug"
            self.debug_path.mkdir(exist_ok=True)

    def _get_image(
            self, *,
            resolution: tuple[int, int],
            threshold: int,
            resampling_algorithm: Image.Resampling,
            invert: bool,
        ) -> Image.Image:
        """Load, resize and binarize image.

        Args:
            resolution (tuple[int, int]): target resolution (px)
            threshold (int): binarization threshold
            resampling_algorithm (Image.Resampling): image resampling algorithm
            invert (bool): whether invert image colors or not

        Returns:
            Image.Image: image

        """
        image = self._load_image()
        if self.debug:
            logger.debug("saving image, stage=load")
            image.save(self.debug_path / "load.jpg")

        image = self._resize_image(
            image=image,
            resolution=resolution,
            resampling_algorithm=resampling_algorithm,
        )
        if self.debug:
            logger.debug("saving image, stage=resize")
            image.save(self.debug_path / "resize.jpg")

        image = self._binarize_image(
            image=image,
            threshold=threshold,
            invert=invert,
        )
        if self.debug:
            logger.debug("saving image, stage=binarize")
            image.save(self.debug_path / "binarize.jpg")
        
        return image
    

    def _load_image(self) -> Image.Image:
        """Load image from self.image_filepath and cache it.

        Use cached image if available

        Returns:
            Image.Image: loaded image

        """
        if self._image is not None:
            logger.debug("using cached image")
            return self._image

        logger.info("loading image")
        image: Image.Image = Image.open(self.image_filepath)

        logger.debug("converting image to luminance mode")
        image = image.convert("L")

        self._image = image
        return self._image
        

    def _resize_image(
            self, *,
            image: Image.Image,
            resolution: tuple[int, int],
            resampling_algorithm: Image.Resampling,
        ) -> Image.Image:
        """Resize image.

        Args:
            image (Image.Image): image
            resolution (tuple[int, int]): target resolution (px)
            resampling_algorithm (Image.Resampling): image resampling algorithm`

        Returns:
            Image.Image: resized image

        """
        logger.debug("resizing image (resolution=%s, resampling_algorithm=%s)", resolution, resampling_algorithm.name)
        return image.resize(resolution, resampling_algorithm)
    

    def _binarize_image(
            self, *,
            image: Image.Image,
            threshold: int,
            invert: bool,
        ) -> Image.Image:
        """Binarize image.

        Args:
            image (Image.Image): image (mode: L)
            threshold (int): binarization threshold
            invert (bool): whether invert colors or not

        Returns:
            Image.Image: binarized image (mode: 1)

        """
        low, high = (0, 255) if not invert else (255, 0)
        
        logger.debug("binarizing image (threshold=%d, invert=%d)", threshold, invert)

        return image.point(
            lambda p: low if p < threshold else high,
            mode="1",
        )
        

    def generate(
            self, *,
            resolution: tuple[int, int],
            threshold: int,
            resampling_algorithm: Image.Resampling = Image.Resampling.LANCZOS,
            invert: bool = False,
        ) -> str:
        """Generate Braille-art.

        Args:
            resolution (tuple[int, int]): art resolution (in characters)
            threshold (int): image binarization threshold
            resampling_algorithm (Image.Resampling, optional): image resampling algorithm.
                Defaults to Image.Resampling.LANCZOS.
            invert (bool, optional): invert image colors. Defaults to False.

        Returns:
            str: Braille-art

        """
        resolution_px = (resolution[0] * 2, resolution[1] * 4)

        image = self._get_image(
            resolution=resolution_px,
            threshold=threshold,
            resampling_algorithm=resampling_algorithm,
            invert=invert,
        )

        blocks = self._split_image_in_blocks(image)

        return self._generate_art(blocks)
    

    def _split_image_in_blocks(self, image: Image.Image) -> list[list[tuple]]:
        """Split image in 2x4 blocks.

        Args:
            image (Image.Image): image (mode: 1)

        Returns:
            list[list[tuple]]: 2D block matrix (block: tuple len=8)

        """
        logger.info("splitting image in blocks")

        blocks = []
        for y in range(0, image.height, 4):
            row = []
            for x in range(0, image.width, 2):
                image_block = image.crop((
                    x, y, x+2, y+4,
                ))

                block = tuple(image_block.getdata())
                row.append(block)
            blocks.append(row)
        
        return blocks
    
    
    def _generate_art(self, blocks: list[list[tuple]]) -> str:
        """Generate Braille-art from image blocks.

        Args:
            blocks (list[list[tuple]]): image blocks

        Returns:
            str: Braille-art

        """
        art = ""
        blocks_len = len(blocks)

        for i, blocks_row in enumerate(blocks, start=1):
            for block in blocks_row:
                art += self._block_to_braille(block)
            
            if i != blocks_len:
                art += "\n"
        
        return art
                

    def _block_to_braille(self, block: list) -> str:
        """Convert image block to Braille character.

        Args:
            block (list): image block

        Returns:
            str: Braille character

        """
        braille_bits = 0x2800

        if block[0]: # dot 1
            braille_bits |= 0b00000001
        if block[2]: # dot 2
            braille_bits |= 0b00000010
        if block[4]: # dot 3
            braille_bits |= 0b00000100
        if block[1]: # dot 4
            braille_bits |= 0b00001000
        if block[3]: # dot 5
            braille_bits |= 0b00010000
        if block[5]: # dot 6
            braille_bits |= 0b00100000
        if block[6]: # dot 7
            braille_bits |= 0b01000000
        if block[7]: # dot 8
            braille_bits |= 0b10000000

        return chr(braille_bits)

