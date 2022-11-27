import pygetwindow as gw
import pyscreenshot as ImageGrab

import conf
c = conf.read_conf()

window = gw.getWindowsWithTitle(c.window_title)[0]

window_bbox = conf.Box.from_matrix([[window.left, window.top], [window.right, window.bottom]])
targets = {**c.label_locations, **{"window": window_bbox }}

print(targets)

for k, v in targets.items():
  print(k)
  print(v.to_tuple())
  l_snapshot = ImageGrab.grab(bbox=v.to_tuple())
  l_snapshot.save(f"out/{k}.jpg")


