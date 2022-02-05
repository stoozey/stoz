using stoz.Stoz.Structs;

namespace stoz.Stoz.Classes;

public class Frame
{
    private const int X = 0;
    private const int Y = 0;
    
    private readonly Size imageSize;
    private readonly short pixelSize;
    private byte[][] grid;
    private Size gridSize =>
        new (
            (int) Math.Ceiling((double) (this.imageSize.Height / this.pixelSize)),
            (int) Math.Ceiling((double) (this.imageSize.Width / this.pixelSize))
        );

    public byte GetPixel(int _x, int _y)
    {
        var _gridSize = this.gridSize;

        var _cellX = (int) Math.Max(0, Math.Min((_gridSize.Width - 1), Math.Floor((double) (_x / this.pixelSize))));
        var _cellY = (int) Math.Max(0, Math.Min((_gridSize.Height - 1), Math.Floor((double) (_y / this.pixelSize))));

        return this.GetCell(_cellX, _cellY);
    }
    
    private byte GetCell(int _x, int _y)
    {
        return this.grid[_x][_y];
    }
    
    private void GenerateGrid()
    {
        var _gridSize = this.gridSize;
        this.grid = new byte[_gridSize.Height][];
        for (int y = 0; y < this.imageSize.Height; y++) 
            this.grid[y] = new byte[_gridSize.Width];
    }
    
    public Frame(Size _imageSize, short _pixelSize = 1)
    {
        this.imageSize = _imageSize;
        this.pixelSize = _pixelSize;

        this.GenerateGrid();
    }
}