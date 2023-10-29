import os.path
rootdir = "/media/ubuntu/ANL/Data/1extractFrame_Drone2"
parent = rootdir
#for parent, dirnames, filenames in os.walk(rootdir):
for filename in os.listdir(rootdir):
    if filename[0:1] == 'd' and int(filename[1:15])>=20221111165011:
        print(filename[1:-1])
        newName = filename[1:]
        os.rename(os.path.join(parent, filename), os.path.join(parent, newName))