import numpy
import leb128
import zlib
from PIL import Image, ImageSequence
from math import ceil, floor

from . import binary_util
from .enums import ImageMode, HeaderValue


BYTE_EMPTY = bytes([0x00])

stoz_version = 2


class Pixel():
    def __init__(self, image_mode: ImageMode = ImageMode.RGBA, r: int = 0, g: int = 0, b: int = 0, a: int = 0):
        self.image_mode: ImageMode = image_mode
        self.r: int = r
        self.g: int = g
        self.b: int = b
        self.a: int = a

    @property
    def bytearray(self) -> bytearray:
        array = bytearray()
        if (self.image_mode is ImageMode.L):
            array += binary_util.int_to_bytes(self.r)
        elif (self.image_mode is ImageMode.RGB):
            array += binary_util.int_to_bytes(self.r)
            array += binary_util.int_to_bytes(self.g)
            array += binary_util.int_to_bytes(self.b)
        elif (self.image_mode is ImageMode.RGBA):
            array += binary_util.int_to_bytes(self.r)
            array += binary_util.int_to_bytes(self.g)
            array += binary_util.int_to_bytes(self.b)
            array += binary_util.int_to_bytes(self.a)

        return array

    @property
    def tuple(self) -> tuple:
        if (self.image_mode == ImageMode.L):
            return (self.r,)
        elif (self.image_mode == ImageMode.RGB):
            return (self.r, self.g, self.b)
        elif (self.image_mode == ImageMode.RGBA):
            return (self.r, self.g, self.b, self.a)


class Frame():
    def __init__(self, image_mode: ImageMode = ImageMode.RGBA, size: tuple = (0, 0), pixel_size: int = 1):
        self.image_mode: ImageMode = image_mode
        self.size: tuple[int, int] = size
        self.pixel_size: int = pixel_size
        self.grid: list[list[Pixel]] = [[]]

        self.generate_grid()

    @property
    def bytearray(self) -> bytearray:
        array = bytearray()
        array += b"IMS"

        # generate chunks
        chunks: list[list[Pixel]] = []
        chunk: list[Pixel] = []
        def offload_chunk():
            if (len(chunk) == 0):
                return

            chunks.append(chunk.copy())
            chunk.clear()

        for y in range(len(self.grid)):
            row = self.grid[y]
            for x in range(len(row)):
                pixel = self.get_pixel((x, y))
                if ((len(chunk) > 0) and (chunk[0].tuple != pixel.tuple)):
                    offload_chunk()

                chunk.append(pixel)

        offload_chunk()

        # write chunks to bytearray
        for chunk in chunks:
            pixel = chunk[0]
            chunk_length = leb128.u.encode(len(chunk))
            byte_data = pixel.bytearray

            array += (chunk_length + byte_data)

        array += b"IME"
        return array

    @property
    def cell_count(self) -> tuple:
        return tuple([ceil(x / self.pixel_size) for x in self.size])

    def generate_grid(self) -> None:
        width, height = self.cell_count
        self.grid = [] * height
        for y in range(height):
            self.grid.append([Pixel(image_mode=self.image_mode)] * width)

    def get_cell_position(self, position: tuple):
        cell_count = self.cell_count
        return tuple([max(0, min((count - 1), floor(position[i] / self.pixel_size)))for i, count in enumerate(cell_count)])

    def set_pixel(self, position: tuple, pixel: Pixel) -> None:
        cell_position = self.get_cell_position(position)
        self.grid[cell_position[1]][cell_position[0]] = pixel

    def get_cell(self, cell_position: tuple):
        return self.grid[cell_position[1]][cell_position[0]]

    def get_pixel(self, position: tuple) -> Pixel:
        cell_position = self.get_cell_position(position)
        return self.get_cell(cell_position)


class Stoz():
    def __init__(self, size: tuple = (0, 0), version: int = stoz_version, image_mode: ImageMode = ImageMode.RGBA,
                 pixel_size: int = 1, frame_count: int = 1, frame_duration: int = None):
        self.size: tuple = size

        self.headers: list[any] = [None] * len(HeaderValue)
        self.set_header(HeaderValue.VERSION, version)
        self.set_header(HeaderValue.IMAGE_MODE, image_mode)
        self.set_header(HeaderValue.WIDTH, self.size[0])
        self.set_header(HeaderValue.HEIGHT, self.size[1])
        self.set_header(HeaderValue.PIXEL_SIZE, pixel_size)
        self.set_header(HeaderValue.FRAME_COUNT, frame_count)
        self.set_header(HeaderValue.FRAME_DURATION, frame_duration)

        self.frames: list[Frame] = []
        self.generate_frames()

    def set_header(self, header: HeaderValue, value: any) -> None:
        self.headers[header.value] = value

    def get_header(self, header: HeaderValue) -> any:
        return self.headers[header.value]

    def generate_frames(self) -> None:
        self.frames.clear()

        image_mode = self.get_header(HeaderValue.IMAGE_MODE)
        frame_count = self.get_header(HeaderValue.FRAME_COUNT)
        pixel_size = self.get_header(HeaderValue.PIXEL_SIZE)
        for i in range(frame_count):
            frame = Frame(image_mode=image_mode, size=self.size, pixel_size=pixel_size)
            frame.generate_grid()
            self.frames.append(frame)

    def save(self, filename: str) -> None:
        # headers
        headers = bytearray()
        headers += (b"STOZ" + BYTE_EMPTY + b"HDS")
        for i, value in enumerate(self.headers):
            if (value is None):
                continue

            header = HeaderValue(i)
            value = value if (type(value) != ImageMode) else value.value

            header_id = binary_util.int_to_bytes(header.value)
            header_value = leb128.u.encode(value)

            headers += (header_id + header_value)
        headers += b"HDE"

        # image data
        image_data = bytearray()
        for frame in self.frames:
            image_data += frame.bytearray

        # write it!!
        with open(filename, "wb") as file:
            buffer = (headers + zlib.compress(image_data))
            file.write(buffer)

    def to_image(self, filename: str) -> None:
        def convert_to_pillow_image(frame: Frame):
            array = []
            width, height = frame.size
            for y in range(height):
                subArray = []
                for x in range(width):
                    pixel = frame.get_pixel((x, y))
                    subArray.append(pixel.tuple)
                array.append(subArray)

            npArray = numpy.array(array, dtype=numpy.uint8)
            return Image.fromarray(npArray)

        frames = list([convert_to_pillow_image(frame) for frame in self.frames])
        frame_duration = self.get_header(HeaderValue.FRAME_DURATION)
        duration = 0 if (frame_duration is None) else frame_duration * len(frames)
        frames[0].save(filename, save_all=True, append_images=frames[1:], duration=duration, loop=0)

    @classmethod
    def load(cls, filename: str):
        pass

    @classmethod
    def from_image(cls, filename: str, pixel_size: int = 1):
        image: Image = Image.open(filename)
        is_animated = getattr(image, "is_animated", False)
        frame_count = 1 if (not is_animated) else image.n_frames

        try:
            image_mode = ImageMode[image.mode]
        except KeyError:
            image_mode = ImageMode.RGB

        frame_data = []
        duration = 0
        for frame in ImageSequence.Iterator(image):
            data = frame.convert("RGBA")
            frame_data.append(data.getdata())
            if (is_animated):
                duration += frame.info["duration"]

            duration = ceil(duration / frame_count)

        stoz = cls(image_mode=image_mode, size=image.size, pixel_size=pixel_size, frame_duration=duration, frame_count=frame_count)

        width, height = image.size
        for i, stoz_frame in enumerate(stoz.frames):
            image_frame = frame_data[i]
            for x in range(width):
                for y in range(height):
                    pixel_tuple = image_frame.getpixel((x, y))
                    pixel = Pixel(image_mode, *pixel_tuple)
                    stoz_frame.set_pixel((x, y), pixel)

        return stoz
