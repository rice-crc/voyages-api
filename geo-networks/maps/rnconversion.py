import re
import json

'''
converts a legacy voyages routenodes js file to the new json format
'''

d=open("routeNodes.js",'r')
t=d.read()
d.close()

routenodelines=re.search("routeNodes.*?\[.*?\]",t,re.S).group(0)

latlngcontents=re.findall("(?<=LatLng\().*?(?=\))",routenodelines)

latlngs=[]
for llc in latlngcontents:
	a,b=[float(i.strip()) for i in llc.split(",")]
	latlngs.append([a,b])
	
# print(latlngs)

linklines=re.search("links.*?\[.*?\]",t,re.S).group(0)

linkcontents=re.findall("[0-9]+.*[0-9]+",linklines)

links=[]
for lkc in linkcontents:
	a,b=[int(i) for i in re.findall("[0-9]+",lkc)]
	links.append([a,b])

output={"nodes":[],"links":[]}

for latlng in latlngs:
	output["nodes"].append([str(i) for i in latlng])
	
for link in links:
	output["links"].append([str(i) for i in link])

d=open("output.json","w")
d.write(json.dumps(output,indent=1))
d.close()