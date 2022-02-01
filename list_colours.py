# From https://mike632t.wordpress.com/2018/02/10/displaying-a-list-of-the-named-colours-available-in-pygame/
# Run with python2 not python3, as python3 doesn't like the def _RGB line

# Modified by Alexander Hanysz to show colours in hsv order not alphabetical
#
# py-pygame-display-colors-htm.py
#
# Produces a table of all the pygame colours.
#
# This  program  is free software: you can redistribute it and/or  modify it
# under the terms of the GNU General Public License as published by the Free
# Software  Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This  program  is  distributed  in the hope that it will  be  useful,  but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public  License
# for more details.
#
# You  should  have received a copy of the GNU General Public License  along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# https://stackoverflow.com/questions/3121979
#
import sys
import pygame 
import colorsys
   
_format = { 'header'  : ( '<table width=800 style="' +
                          'vertical-align:middle;' +
                          'background:#ffffff; ' + 
                          'padding:0px; line-height:133%; ' + 
                          'font-family:monospace; white-space:nowrap; '
                          'white-space:pre; overflow:auto; ' + 
                          'font-size:10pt; color:#696969;"' +
                          '><tr>'),
 
            'colour'  : ( '<td width=64 style="' +
                          'background:'),
 
            'name'    : ( '">&nbsp;</td><td>&nbsp;'),
 
            'newline' : ('</td></tr>'),
 
            'footer'  : ('</table><br><p>\n')}
 
def _RGB ((_red, _blue, _green, _alpha)):
  return '#%06X' %  ((_red * 256 + _blue) * 256 +_green) # Ignores alpha
 
_colour_names = pygame.colordict.THECOLORS.items()
_colour_names.sort(key=lambda c: colorsys.rgb_to_hsv(*c[1][0:3])) # Sort list by colour RGB value
 
sys.stdout.write(_format['header'] + "\n")
for _colour in _colour_names:
  sys.stdout.write(_format['colour'] + _RGB(_colour[1]))
  sys.stdout.write(_format['name'] + _RGB(_colour[1]) + " " + _colour[0])
  sys.stdout.write(_format['newline'] + "\n")
    
sys.stdout.write(_format['footer'] + "\n")
 
pygame.quit()
exit(0) 
