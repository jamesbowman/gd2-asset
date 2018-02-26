from distutils.core import setup
setup(name='gameduino2',
      version='0.2.3',
      author='James Bowman',
      author_email='jamesb@excamera.com',
      url='http://gameduino.com',
      description='Package of Gameduino 2/3 development tools',
      long_description='Gameduino 2 and 3 (http://gameduino.com) are Arduino video games adapters.  This package contains tools for developers: data preparation, remote control.',
      license='GPL',
      packages=['gameduino2'],
      scripts=['scripts/gd2asset', 'scripts/gd3asset'],
)
