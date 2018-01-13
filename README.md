# gd2-asset


usage:
    
    gd2asset <options> <assets>
    gd3asset <options> <assets>

      -3          target GD3 (FT810 series) - set by gd3asset
      -d          dither all pixel conversions
      -f <name>   output asset file (default is header file)
      -o <name>   output header file

    If no output header file is given, then "default_assets.h" is used

    Each asset is a filename, optionally followed by some var=val
    assignments. For example:
      pic1.png                 image, format ARGB4
      pic2.jpg,format=L8       image, format L8
      serif.ttf,size=16        font, 16 pixels high

    Options for the file types:

    jpg,png,bmp,gif:
     format   L1 L2 L4 L8 RGB332 ARGB2 ARGB4 RGB565 ARGB1555. Default ARGB4

    ttf,otf
     size     height in pixels. Default 12
     format   L1 L2 L4 L8 RGB332 ARGB2 ARGB4 RGB565 ARGB1555. Default ARGB4
     topchar  maximum ASCII code encoded. Default 127

    wav
     (no options)

    The assets are compiled into flash, or if the "-f" option is given
    into a file. In this case the file should be copied to the
    microSD card.
    In either case, calling LOAD_ASSETS() from the program loads all
    assets.

To test run `go`, it should produce:

    Assets report
    -------------
    Header file:    default_assets.h
    GD2 RAM used:   115104
    Output file:    xxx
    File size:      29664

To install do:

    python setup.py sdist
    twine upload dist/*
