from distutils.core import setup
setup(name='gameduino2',
      version='0.3.0',
      author='James Bowman',
      author_email='jamesb@excamera.com',
      url='http://gameduino.com',
      description='Package of Gameduino 2/3/3X development tools',
      long_description='Gameduino 2, 3 and 3X (http://gameduino.com) are Arduino video games adapters.  This package contains tools for developers: data preparation, remote control.',
      license='GPL',
      packages=['gameduino2'],
      scripts=['scripts/gd2asset', 'scripts/gd3asset'],
)
