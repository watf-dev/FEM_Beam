#!/usr/bin/env python3
# Created: Jan, 29, 2025 18:37:08 by Wataru Fukuda

def main():
  import argparse
  parser = argparse.ArgumentParser(description="""\
find max from binary file
""")
  parser.add_argument("file", metavar="input-file", help="input file")
  options = parser.parse_args()
  import numpy

  data = numpy.fromfile(options.file,dtype=">f8")
  max_value = numpy.max(data)
  print(f"{max_value}")


if(__name__ == '__main__'):
  main()

