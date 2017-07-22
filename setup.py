from distutils.core import setup
setup(name='gameduino2',
      version='0.1.8',
      author='James Bowman',
      author_email='jamesb@excamera.com',
      url='http://gameduino.com',
      description='Package of Gameduino 2 development tools',
      long_description='Gameduino 2 (http://gameduino.com) is an Arduino video games adapter.  This package contains tools for developers: data preparation, remote control.',
      license='GPL',
      packages=['gameduino2'],
      scripts=['scripts/gd2asset'],
)
