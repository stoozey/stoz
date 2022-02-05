using stoz.Stoz.Enums;

namespace stoz.Stoz.Classes;

public struct Pixel
{
    public readonly byte[] channels;
    
    private readonly ImageMode imageMode;
    private readonly bool alphaEnabled;

    public void SetChannels(params byte?[] _channels)
    {
        for (var i = 0; ((i < _channels.Length) && (i < this.channels.Length)); i++)
        {
            var _channel = _channels[i];
            if (_channel == null) continue;

            this.channels[i] = (byte) _channel;
        }
    }

    public Pixel(ImageMode _imageMode, bool _alphaEnabled)
    {
        this.imageMode = _imageMode;
        this.alphaEnabled = _alphaEnabled;
        
        var _arraySize = ((_alphaEnabled) ? 1: 0);
        switch (_imageMode)
        {
            case ImageMode.L:
                _arraySize += 1;
                break;
            
            case ImageMode.RGB:
                _arraySize += 3;
                break;
        }

        this.channels = new byte[_arraySize];
    }
}