sudo rm -rf /usr/local/lib/python2.7/dist-packages/gameduino2/*
sudo python setup.py install
gd2asset -f xxx testdata/felix.png,testdata/felix.png,format=L1 testdata/Hobby-of-night.ttf testdata/0.wav
