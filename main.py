from nbtlib.tag import *
from nbtlib import *
from math import floor
import re
import os
StructureSchema = schema('Structure', {
    'DataVersion': Int, #DONE
    'author': String, #DONE
    'size': List[Int], #DONE
    'palette': List[schema('State', {
        'Name': String, #DONE
        'Properties': Compound, #DONE
    })],
    'blocks': List[schema('Block', {
        'state': Int, #DONE
        'pos': List[Int], #DONE
        'nbt': Compound, #DONE
    })],
})

nbtSchem = StructureSchema()
nbtSchem["DataVersion"] = 2586
nbtSchem["palette"] = []
nbtSchem["blocks"] = []
nbtSchem["author"] = "Folfy_Blue"
if not os.path.exists(os.getcwd() + "\output"):
    os.makedirs(os.getcwd() + "\output")
for subdir, dirs, files in os.walk(os.getcwd() + "\input"):
    for file in files:
        filepath = subdir + os.sep + file
        if not os.path.exists(subdir.replace("input", "output")):
            os.makedirs(subdir.replace("input", "output"))
        if not os.path.exists(filepath):
            open(filepath)
        print (filepath)
        WE = load(filepath)
        bytePalette = dict(WE["Palette"])

        bytePalette = {int(v): k for k, v in bytePalette.items()} # Inverse keys and values while making the values actual ints
        newPalette = {}

        size = {
            "x":int(WE["Length"]),
            "y":int(WE["Height"]),
            "z":int(WE["Width"])
        }

        nbtSchem["size"] = [size["x"],size["y"],size["z"]]

        updatedPalette = {}
        #(minecraft:\w+)(\[.+\])?
        #((\w+)=(\w+))


        blockEntities = {}
        for cmpd in WE["BlockEntities"]:
            key = str(int(cmpd["Pos"][0]))+" "+str(int(cmpd["Pos"][1]))+" "+str(int(cmpd["Pos"][2]))
            cmpd["id"] = cmpd["Id"]
            del cmpd["Id"]
            del cmpd["Pos"]
            blockEntities[key] = cmpd

        for palette,block in bytePalette.items():
            blockName,blockProperties = re.findall("(minecraft:\w+)(\[.+\])?",block)[0]
            blockProperties = re.findall("((\w+)=(\w+))",blockProperties)
            bP = {}
            for blockProperty in blockProperties:
                bP[blockProperty[1]] = String(blockProperty[2])
            if len(bP) > 0:
                nbtSchem["palette"].append({"Name":blockName,"Properties":bP})
            else:
                nbtSchem["palette"].append({"Name":blockName})
            newPalette[block] = len(nbtSchem["palette"])-1


        for i in range(len(WE["BlockData"])):
            x = floor((i % (size["z"] * size["x"])) % size["z"])
            y = floor(i / (size["z"] * size["x"]))
            z = floor((i % (size["z"] * size["x"])) / size["z"])
            block = bytePalette[int(WE["BlockData"][i])]

            if str(x)+" "+str(y)+" "+str(z) in blockEntities:
                nbtSchem["blocks"].append({"state":newPalette[block],"pos":[x,y,z],"nbt":blockEntities[str(x)+" "+str(y)+" "+str(z)]})
            else:
                nbtSchem["blocks"].append({"state":newPalette[block],"pos":[x,y,z]})

            print("Processed "+str(i)+"/"+str(len(WE["BlockData"]))+" blocks. ("+str(round(i/len(WE["BlockData"])*100,2))+"%)",end="\r")

        print("\nDone! Saving...")
        File({'': Compound(nbtSchem)},gzipped=True).save(filepath.replace(".schem", ".nbt").replace("input", "output"))
        print("Saved to " + filepath.replace(".schem", ".nbt").replace("input", "output"))
