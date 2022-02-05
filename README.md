# .stoz Image Format (version 2)
-------

This is a joke file format that I made while bored.
Stoz supports animated images and both lossless and lossy compression.

This readme will contain documentation on how the format works, the code portion has language bindings to file generation and conversion into other file formats.

## Headers
At the beginning of the header is `STOZ` followed by 1 empty byte. Actual header information starts with `HDS` (short for header start).

Headers are in key & value pair format, the key being represented by an enum and the data being leb128 compressed.

### Header Keys Enum
- VERSION
	- Hex value: `00`
	- What version of the stoz format is the file using. Used for backwards compatibility.
- IMAGE_MODE
	- Hex value: `01`
	- This is another enum, which states how many colour channels are used:
		- L (`00`, 1 byte per pixel - black and white only)
		- RGB (`01`, 3 bytes per pixel - full RGB colour)
		- RBGA (`02`, 4 bytes per pixel - full RGB colour with transparency)
- WIDTH
	- Hex value: `02`
	- The width of the image.
- HEIGHT
	- Hex value: `03`
	- The height of the image.
- PIXEL_SIZE
	- Hex value: `04`
	- How many pixels does one cell in the image grid account for (more information below).
- FRAME_COUNT
	- Hex value: `05`
	- How many frames are in the image. A non animated stoz can ignore this value and by default have the count as 1.
- FRAME_DURATION
	- Hex value: `06`
	- How many milliseconds does each frame last for.

Not all headers are required, but the ones you need are:
- VERSION
- IMAGE_MODE
- WIDTH
- HEIGHT
- PIXEL_SIZE

After that byte would be the actual header's data (leb128 compressed).
> For example: a value stating the width as 420px would be: `02` `A4 03`


## Pixel Size / Lossy Compression
Stoz files are stored in a grid, with each cell being 1 or more pixels. A pixel size of `1` represents an uncompressed image where each cell is filling a single pixel of the image--the position `x: 9, y: 21` would be be equal to `x: 9, y: 21` on the grid. Whereas in an image with a pixel size of 2, `x: 9, y: 21` would represent `x: 4, y: 10` on the grid since the positions have been divided by the pixel size (number is floored), reducing filesize quite effectively at the cost of pixelation.


## Pixel Data / Frames
Even a .stoz file with no animation technically has frames, albeit only one. Frames are formatted like so: `IMS<binary data>IME`. They are placed one after eachother; so two frames would be `IMS<binary data>IMEIMS<binary data>IME`.

Inside a frame are the pixels themselves. Pixels are ordered starting horizontally from left to right then moving vertically from the top to the bottom, split up into rows.

As a minor method of lossless compression, pixels get stored into "chunks" where if the next pixel (to it's right) is the same as the current one, we dont bother to write it's data and instead say how many times this pixel is repeated.
> For example, three L pixels of 100 would be: `03 64`

## Final File Output
Headers are not zlib compressed, but frame data is zlib compressed.