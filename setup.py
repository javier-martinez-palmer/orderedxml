from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='orderedxml',
      version='0.1',
      description='simple module to read/write xml files keeping the order',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='xml ordered',
      url='https://github.com/matheboy/orderedxml.git',
      author='matheboy',
      author_email='franciscojmp@gmail.com',
      license='MIT',
      packages=['orderedxml'],
      install_requires=[
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      entry_points={
      },
      include_package_data=True,
      zip_safe=False)