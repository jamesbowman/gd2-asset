cp scripts/gd2asset scripts/gd3asset
python setup.py install
python bringup.py
exit

# ./video-convert $HOME/Downloads/Fair*mp4
# exit
sudo rm -rf /usr/local/lib/python2.7/dist-packages/gameduino2/*
cp scripts/gd2asset scripts/gd3asset
sudo python setup.py install
gd2asset -f xxx \
  testdata/felix.png,format=RGB332 \
  testdata/Hobby-of-night.ttf \
diff xxx golden

gd2asset -f xxx \
  testdata/felix.png,format=RGB332 \
  testdata/Hobby-of-night.ttf,topchar=0x39 \
  testdata/0.wav \
  Aurek-Besh.ttf

exit
# gd3asset -f xxx \
#   testdata/felix.png,format=L2 \
#   testdata/Hobby-of-night.ttf \
#   testdata/0.wav \
#   Aurek-Besh.ttf

# gd2asset -f stage72.bin -o stage72_assets.h ~/Downloads/RexliaFree.ttf,size=83,format=L1
python try.py
