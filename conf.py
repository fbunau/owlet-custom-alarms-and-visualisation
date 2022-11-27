from dataclasses import dataclass
import configparser
import ast
import numpy as np

@dataclass
class Point:
  x: int
  y: int

@dataclass
class Box:
  top_left: Point
  bottom_right: Point

  def to_tuple(self):
    return (self.top_left.x, self.top_left.y, self.bottom_right.x, self.bottom_right.y)

  def from_matrix(m):
    return Box(
      Point(Box.__cast_pos(m[0][0]), Box.__cast_pos(m[0][1])), 
      Point(Box.__cast_pos(m[1][0]), Box.__cast_pos(m[1][1]))
    )

  def __cast_pos(x):
    return int(np.abs(x))

@dataclass
class Configuration:
  window_title: str
  label_locations: list[Box]

  
def read_box(config, box_label):
  m = ast.literal_eval(config["label_locations"][box_label])
  return Box.from_matrix(m)

def read_conf():
  config = configparser.ConfigParser()
  config.read("app.conf")

  title = config["default"]["window_title"]
  label_locations = config["label_locations"]

  return Configuration(
    title,
    dict([(key, read_box(config, key)) for key in label_locations])
  )
