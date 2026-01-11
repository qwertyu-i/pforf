from pforf import Pforf
# for now, just set code as string
# all of these should return 4, any amount of them
p = Pforf()
p.run("2 2 +")
p.run("-2 ABS 2 +")
p.run("2 ?DUP 0 ?DUP + +")
p.run("1 1+ 1+ 1+")
p.run("0 IF 0 THEN 4 ELSE IF 4 THEN 0 ELSE")
# nested ifs test
p.run("1 IF 0 IF 0 THEN 4 ELSE THEN 0 ELSE")
p.run("1 IF 1 IF 1 IF 4 THEN 1 ELSE THEN 2 ELSE THEN 3 ELSE")
p.run("1 3 0 DO 1 + LOOP")
p.run("0 IF 0 THEN 0 IF 0 THEN 4 ELSE ELSE ELSE")
p.run("4 1 IF 4 1 IF 4 1 IF 4 THEN 1 ELSE THEN 1 ELSE THEN 1 ELSE")
p.run("4 1 IF 0 IF 1 THEN 4 ELSE 4 THEN 1 ELSE")
