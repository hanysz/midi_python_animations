import cairo
import math
import numpy as np

def angle_from_vector(x, y):
  return np.arctan2(x, y)

def angle_from_np_vector(v):
  return(np.arctan2(v[1], v[0]))

def vec_length(v): return np.linalg.norm(v) # numpy is annoying!

class CustomContext(cairo.Context):
  def x_marks_the_spot(ctx, x,y, size=10):
    ctx.move_to(x-size/2, y-size/2)
    ctx.line_to(x+size/2, y+size/2)
    ctx.stroke()
    ctx.move_to(x-size/2, y+size/2)
    ctx.line_to(x+size/2, y-size/2)
    ctx.stroke()

  def circle_lower_part(ctx, x, y, r, fraction):
    # draw an arc of the lower part of a circle
    # and return the start and end points so we can join on other things to it neatly

    # full circle should start at top, i.e. angle = 3*pi/2
    # nearly-empty circle should start near bottom, i.e. angle=pi/2
    start_angle = (0.5-fraction)*math.pi
    end_angle = math.pi - start_angle
    ctx.arc(x, y, r, start_angle, end_angle)
    start_point = (x+r*math.cos(start_angle), y+r*math.sin(start_angle))
    end_point = (x+r*math.cos(end_angle), y+r*math.sin(end_angle))
    return start_point, end_point

  def arc_given_centre_and_endpoints(ctx, cx, cy, x1, y1, x2, y2):
    # helper function while designing arc_to
    # dodgy assumption: circle centre (cx,cy) through (x1,y1) actually goes through (x2,y2)
     v1 = np.array((x1-cx, y1-cy))
     v2 = np.array((x2-cx, y2-cy))
     l  = np.array((x2-x1, y2-y1))
     r = vec_length(v1) # should be the same for v2, if the endpoint is actually in the right place
     start_angle = angle_from_np_vector(v1)
     end_angle   = angle_from_np_vector(v2)
     cross_product = (cx-x1)*(y2-y1) - (cy-y1)*(x2-x1)
     if cross_product > 0:
       ctx.arc_negative(cx, cy, r, start_angle, end_angle)
     else:
       ctx.arc(cx, cy, r, start_angle, end_angle)

  def arc_to(ctx, x, y, c):
    # draw a circular arc from current point to (x,y)
    # c = curvature, 0=straight line, higher numbers = more curved without limit
    # positive c will bow out to the right, negative to the left

    if c==0:
      ctx.line_to(x,y)
      return
    A = np.array(ctx.get_current_point())
    B = np.array((x,y))
    l = B-A # vector pointing along line from A to B
    M = (A+B)/2 # midpoint
    v = (l)/vec_length(l) # unit vector in the direction of AB
    r = vec_length(l)/c # distance to centre of arc; it's OK for this to be negative
    MC = r*np.array((-v[1], v[0])) # vector pointing from M to centre of arc
    C = M + MC # coordinates of centre of arc

    ctx.arc_given_centre_and_endpoints(C[0], C[1], A[0], A[1], B[0], B[1])

  def raindrop(ctx, x, y, r, bulbfrac=0.7, heightratio=2.7, curvature=0.7):
    start, end = ctx.circle_lower_part(x, y, r, bulbfrac)
    ctx.arc_to(x, y-r*heightratio, -curvature)
    ctx.arc_to(start[0], start[1], -curvature)

  def star(ctx, x, y, npoints, outradius, inradius):
  # draw a star with npoints points, centre (x,y)
  # outradius is the distance from centre to the tip of the points
    def angle_to_point(theta, r):
      return x+r*math.cos(theta), y+r*math.sin(theta)
    angles = [i*2*math.pi/npoints - math.pi/2 for i in range(npoints)]
    offset = math.pi/npoints
    ctx.move_to(*angle_to_point(angles[npoints-1]+offset, inradius))
    for theta in angles:
      ctx.line_to(*angle_to_point(theta, outradius))
      ctx.line_to(*angle_to_point(theta+offset, inradius))

