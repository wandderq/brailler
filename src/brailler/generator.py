import logging as lg
from pathlib import Path

from PIL import Image
from PIL.Image import Resampling

from brailler.const import Dither

logger = lg.getLogger(__name__)


class BrailleArtGenerator:
    """Braille-art generator."""

    def __init__(self, filepath: str | Path, *, debug: bool = False) -> None:
        """Initialize Braille-art generator.

        Args:
            filepath (str | Path): image filepath
            debug (bool, optional): enable debug features. Defaults to False.

        """
        self.debug = Path.cwd() / "debug" if debug else None
        self.image = self._load_image(filepath)

        self._BAYER4X4_M = (
            ( 0,  8,  2, 10),
            (12,  4, 14,  6),
            ( 3, 11,  1,  9),
            (15,  7, 13,  5),
        )


    def generate(self, *,
            resolution: tuple[int, int],
            dither: Dither,
            resampling: Resampling,
            threshold: int,
            invert: bool,
        ) -> str:
        """Generate Braille-art.

        Args:
            resolution (tuple[int, int]): target resolution in characters
            dither (Dither): dithering algorithm
            resampling (Resampling): resampling algorithm
            threshold (int): binnarization threshold
            invert (bool): whether invert colors or not

        Returns:
            str: Braille-art

        """
        logger.debug(
            (
                "generating art\n"
                "  image: %r\n"
                "  resolution (char): %s\n"
                "  dither: %s\n"
                "  resampling: %s\n"
                "  threshold: %s\n"
                "  invert: %s\n"
            ),
            self.image, resolution, dither.name, resampling.name, threshold, invert,
        )

        image = self._resize_image(self.image, resolution, resampling)
        image = self._binarize_image(image, dither, threshold)
        
        if invert:
            image = self._invert_image(image)

        return self._image_to_braille(image)
    
    def _load_image(self, filepath: str | Path) -> Image.Image:
        image = Image.open(filepath).convert("L")

        if self.debug:
            logger.debug("saving loaded.jpg")
            image.save(self.debug / "loaded.jpg")
        
        return image


    def _resize_image(self, image: Image.Image, resolution: tuple[int, int], resampling: Resampling) -> Image.Image:
        resolution_px = resolution[0] * 2, resolution[1] * 4

        logger.info("resizing image to %dx%d", *resolution_px)
        resized = image.resize(resolution_px, resample=resampling)

        if self.debug is not None:
            logger.debug("saving resized.jpg")
            resized.save(self.debug / "resized.jpg")
        
        return resized

    
    def _binarize_image(self, image: Image.Image, dither: Dither, threshold: int) -> None:
        logger.info("binarizing image")
        if dither == Dither.BAYER4X4:
            binarized = self._binarize_bayer4x4(image)
        
        elif dither == Dither.FLOYDSTEINBERG:
            binarized = self._binarize_floyd_steinberg(image, threshold)
        
        elif dither == Dither.ATKINSON:
            binarized = self._binarize_atkinson(image, threshold)
        
        elif dither == Dither.NONE:
            binarized = self._binarize_bare(image, threshold)
        
        else:
            err_msg = f"unsupported dither algorithm: {dither.name}"
            raise ValueError(err_msg)
        
        if self.debug:
            logger.debug("saving binarized.jpg")
            binarized.save(self.debug / "binarized.jpg")
        
        return binarized
    
    def _clamp(self, val: float) -> int:
        return max(0, min(255, round(val)))

    def _binarize_floyd_steinberg(self, image: Image.Image, threshold: int) -> Image.Image:
        w, h = image.size
        buffer = list(image.tobytes())

        for y in range(h):
            for x in range(w):
                i = (y * w) + x

                old = buffer[i]
                new = 255 if old > threshold else 0
                buffer[i] = new

                # 1/16 of error
                err = (old - new) / 16.0

                if x + 1 < w:
                    # (x+1, y): 7/16
                    buffer[i + 1] = self._clamp(buffer[i + 1] + err * 7)
                
                if y + 1 < h:
                    # (x, y+1): 5/16
                    buffer[i + w] = self._clamp(buffer[i + w] + err * 5)

                    if x - 1 >= 0:
                        # (x-1, y+1): 3/16
                        buffer[i + w - 1] = self._clamp(buffer[i + w - 1] + err * 3)
                    
                    if x + 1 < w:
                        # (x+1, y+1): 1/16
                        buffer[i + w + 1] = self._clamp(buffer[i + w + 1] + err)
        
        return Image.frombytes("L", (w, h), bytearray(buffer)).convert("1")


    def _binarize_atkinson(self, image: Image.Image, threshold: int) -> Image.Image:
        w, h = image.size
        buffer = list(image.tobytes())

        for y in range(h):
            for x in range(w):
                i = (y * w) + x

                old = buffer[i]
                new = 255 if old > threshold else 0
                buffer[i] = new

                # 1/8 of error
                err = (old - new) / 8.0

                if x + 1 < w:
                    # (x+1, y): 1/8
                    buffer[i + 1] = self._clamp(buffer[i + 1] + err)

                if x + 2 < w:
                    # (x+2, y): 1/8
                    buffer[i + 2] = self._clamp(buffer[i + 2] + err)
                
                if y + 1 < h:
                    # (x, y+1): 1/8
                    buffer[i + w] = self._clamp(buffer[i + w] + err)

                    if x - 1 >= 0:
                        # (x-1, y+1): 1/8
                        buffer[i + w - 1] = self._clamp(buffer[i + w - 1] + err)
                    
                    if x + 1 < w:
                        # (x+1, y+1): 1/8
                        buffer[i + w + 1] = self._clamp(buffer[i + w + 1] + err)
                
                if y + 2 < h:
                    # (x, y+2): 1/8
                    buffer[i + w * 2] = self._clamp(buffer[i + w * 2] + err)
        
        return Image.frombytes("L", (w, h), bytearray(buffer)).convert("1")

    
    def _binarize_bayer4x4(self, image: Image.Image) -> Image.Image:
        w, h = image.size
        buffer = list(image.tobytes())

        for y in range(h):
            for x in range(w):
                threshold = self._BAYER4X4_M[y % 4][x % 4] / 16
                pixel_i = (y * w) + x

                if buffer[pixel_i] / 255 > threshold:
                    buffer[pixel_i] = 255
                else:
                    buffer[pixel_i] = 0
        
        return Image.frombytes("L", (w, h), bytes(buffer)).convert("1")
    

    def _binarize_bare(self, image: Image.Image, threshold: int) -> Image.Image:
        return image.point(
            lambda p: 255 if p > threshold else 0,
            mode="L",
        )
    

    def _invert_image(self, image: Image.Image) -> Image.Image:
        logger.info("inverting image colors")
        return image.point(lambda p: 255 if p == 0 else 0)

    
    def _block_to_braille(self, block: tuple[int, ...]) -> str:
        bits = 0x2800

        if block[0]:
            bits |= 0b00000001
        if block[2]:
            bits |= 0b00000010
        if block[4]:
            bits |= 0b00000100
        if block[1]:
            bits |= 0b00001000
        if block[3]:
            bits |= 0b00010000
        if block[5]:
            bits |= 0b00100000
        if block[6]:
            bits |= 0b01000000
        if block[7]:
            bits |= 0b10000000

        return chr(bits)

    
    def _image_to_braille(self, image: Image.Image) -> str:
        logger.info("converting image into braille symbols")
        w, h = image.size
        blocks = [
            [
                tuple(image.crop((x, y, x+2, y+4)).getdata())
                for x in range(0, w, 2)
            ]
            for y in range(0, h, 4)
        ]

        b_w, b_h = w // 2, h // 4

        art = ""

        for y in range(b_h):
            for x in range(b_w):
                art += self._block_to_braille(blocks[y][x])
            
            if y != b_h - 1:
                art += "\n"
        
        if self.debug:
            logger.debug("saving art.txt")
            with (self.debug / "art.txt").open("w") as file:
                file.write(art)

        return art
