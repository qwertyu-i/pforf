from pforf import Pforf
# for now, just set code as string
# all of these should return 4
p = Pforf()
p.run("2 2 +")
p.run("-2 ABS 2 +")
p.run("2 ?DUP 0 ?DUP + +")
p.run("1 1+ 1+ 1+")
p.run("0 IF 0 THEN 4 ELSE IF 4 THEN 0 ELSE")
# nested ifs test
p.run("1 IF 0 IF 0 THEN 4 ELSE THEN 0 ELSE")
