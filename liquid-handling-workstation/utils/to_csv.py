import csv

compounds = {} 
bottles = {}

with open('../coordinates/0725task.csv') as f:
  reader = csv.reader(f)
  headers = next(reader)
  
  for row in reader:
    bottle_no = row[0]
    for i,val in enumerate(row[1:]):
      if val:
        compound = headers[i+1]
        if compound not in compounds:
          compounds[compound] = 0
          
        compounds[compound] += float(val) 
        
        if bottle_no not in bottles:
          bottles[bottle_no] = []
        bottles[bottle_no].append((compound, float(val)))
        
with open('summary.csv','w') as f:
  writer = csv.writer(f)
  
  writer.writerow(['Compound','Total Amount','Bottles'])
  
for c,total in compounds.items():
  bottle_list = []
  for bottle,amounts in bottles.items():
    for amt in amounts:
      if amt[0] == c:
        bottle_list.append((bottle, amt[1]))

  writer.writerow([c, total, bottle_list])
