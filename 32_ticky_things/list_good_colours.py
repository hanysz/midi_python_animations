# From pygame colour list, make a list of things that will show up on a black background.
# Remove duplicates.

from pygame.colordict import THECOLORS as COLOURS
import os, sys

if os.path.exists("good_colours.txt"):
  sys.exit("Error: output file good_colours.txt already exists")

def bright_enough(c):
  return (c[0]+c[1]+c[2]>150)

output = dict()
for name in COLOURS:
  if bright_enough(COLOURS[name]):
    output[name] = COLOURS[name]

output_unique = dict()
for key, value in output.items():
  if value not in output_unique.values():
    output_unique[key] = value

print(f'COLOURS: {len(COLOURS)}; output: {len(output)}; unique: {len(output_unique)}')

with open("good_colours.txt", 'a') as f:
  for n in output_unique.keys():
    f.write(n)
    f.write("\n")

print("Colour names written to file good_colours.txt")

