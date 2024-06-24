import re
from ddnetBind import Bind


directory = r"C:\Users\xiang\AppData\Roaming\DDNet\w"[:-1]


defaultBinds = []
with open(directory + "settings_ddnet.cfg", "r") as f:
    while (line := f.readline()) != "":
        if Bind.isBind(line):
            defaultBinds.append(Bind(line))


# Usage of this script
# Put in the binds that you want to be mutually exclusive
# Eg. If you have 2 binds, kintafly and deepfly
# This script will edit the files so only one can be active at a time
# Add a "Usage: key" at the top of the text file so the program knows which key(s) are meant to turn on the bind
# Add a "Off: key" at the bottom so the program knows which keys(s) are meant to turn off the bind
# Usage: c
# echo Deepfly: ON
# bind mouse1 "+fire; +toggle cl_dummy_hammer 1 0; cl_dummy_restore_weapon 0; cl_dummy_control 0"
# Off: c
# echo Deepfly: Off; cl_dummy_hammer 0; (Add any addition things you want to run that do not include commands to turn off the bind)
# anything on the line above will run along with the off key
# 
# Advanced: You can add brackets after a key in the Usage section so the key executes the bind only under the condition that the file in the brackets is on
# For example
# deepflybasic.txt:
"""
Usage: c, lshift(copyflybasic.txt)
echo Deepfly: On
bind mouse1 "+fire; +toggle cl_dummy_hammer 1 0; cl_dummy_restore_weapon 0; cl_dummy_control 0"
Off: c
echo Deepfly: Off; cl_dummy_hammer 0;
"""
# This means if copyfly is currently on, lshift (my switch to pistol bind) will switch from copyfly to deepfly
# However, in all other conditions, lshift will not trigger an execute of deepflybasic.txt
# lshift ONLY TRIGGERS deepflybasic.txt when the copyflybasic bind is on
# (Note: It's actually copyflybasicon.txt rather than copyflybasic because we do not edit your original file, nor could your original file be executed)


# Enter the files in this list that you want to make mutually exclusive
# Please make sure your binds in the ddnet settings are the your default binds.
# When we turn off a bind, we will revert to your original default binds
# If you closed ddnet with deepfly on, your mouse1 will not be what you want.
# Turn off all your binds and exit ddnet to ensure correctness.

# Caution:
# If you have nested binds, eg bind a "bind mouse1 \"...\"" we will not revert back the bind inside (mouse1) because I am not checking recursively
# Therefore, in the document, in this example, add a bind mouse1 ""
# It does not do anything, but my program will know to reset the bind, ensuring correct behavior         

excl = ["deepflybasic.txt", "copyflybasic.txt", "throwteebasicleft.txt", "throwteebasicright.txt", "switchonfirebasic.txt", "edgejumpbasic.txt"]

for ind, fname in enumerate(excl):
    fOn = fname.removesuffix(".txt") + "on.txt"
    with open(directory + fOn, "w") as fOn:
        with open(directory + fname, "r+") as f:
            activation = f.readline()[:-1]
            activation = [
                x.strip() for x in activation.removeprefix("Usage:").split(",")
            ]
            for i,a in enumerate(activation):
                if a.endswith(')'):
                    start = a.find('(')
                    activation[i] = a.split('(')
                    activation[i][1] = activation[i][1][:-1]
                    activation[i] = tuple(activation[i])
                    
            changedKeys = []
            curStr = f.readline()
            while True:
                fOn.write(curStr)
                if Bind.isBind(curStr):
                    changedKeys.append(Bind(curStr).bindkey)
                curStr = f.readline()
                if curStr.startswith("Off: "):
                    break

            deactivation = curStr[:-1].removeprefix("Off:").split(",")
            deactivation = [x.strip() for x in deactivation]
            # changKeys tells us what binds we need to revert back to turn off our bind
            excl[ind] = [
                fname,
                changedKeys.copy(),
                activation.copy(),
                deactivation.copy(),
                f.read().strip()
            ]

for finfo in excl:
    # Replace activation keys in defaultbinds to execute files in excl
    updatedkeys = {}
    updatedkeys2 = {}
    fOn = finfo[0].removesuffix(".txt") + "on.txt"
    for ind, b in enumerate(defaultBinds):
        if b.bindkey in finfo[2]:  # activation keys
            defaultBinds[ind].updatecmd("exec " + fOn)
            updatedkeys[b.bindkey] = True
        if b.bindkey in [x[0] for x in finfo[2] if len(x)==2]:
            updatedkeys[b.bindkey]=True
        if b.bindkey in finfo[3]:
            updatedkeys2[b.bindkey] = True
            # If a deactivation key was not originally defined, we need to add it
    for key in finfo[3]:
        if key not in updatedkeys2:
            # If a deactivation key does not exist in the default list, add it
            defaultBinds.append(Bind(f"bind {key} \"\""))
            
    for key in finfo[2]:
        if len(key) == 2:
            key = key[0]
            if key not in updatedkeys:
                defaultBinds.append(Bind(f"bind {key[0]} \"\""))
        elif key not in updatedkeys:
            defaultBinds.append(Bind("bind " + key + " exec " + fOn))
    # Not important
    finfo[-1] = finfo[-1].strip()


pastein = ""

for finfo in excl:
    # excl[index] = {name, changedkeys, activationkeys, deactivationkeys, extra commands}
    # Creating the actual "bind off" file
    fname = finfo[0]
    foff = fname.removesuffix(".txt") + "off.txt"
    pastein+="exec "+foff+'; '
    fOn = fname.removesuffix(".txt") + "on.txt"
    with open(directory + foff, "w") as fmake:
        # For every bind ever, check if it's been edited by activationkey, deactivationkey, or changedKeys
        for b in defaultBinds:
            b: Bind
            if b.bindkey in (finfo[1] + finfo[2] + finfo[3] + [x[0] for x in finfo[2] if len(x) == 2]):
                fmake.write(str(b) + "\n")
            for other in excl:
                if finfo is other:
                    continue
                # Reset all other binds in your exclusion list
                if b.bindkey in other[2]:
                    fmake.write(str(b) + "\n")
                # check if another document uses a "partial activate"
                if (b.bindkey, fname) in other[2]:
                    fmake.write(str(b)+'\n')
                    
        # "bind off" file is finished, now edit "bind on" file

    with open(directory + fOn, "a") as fOn:
        fOn.write("\n")
        # Set all activation keys that aren't also deactivation keys to do what it previously did
        for keys in set(finfo[2]) - set(finfo[3]):
            if len(keys) == 2:
                if keys[0] in finfo[3]:
                    continue
                keys = keys[0]
            for b in defaultBinds:
                if b.bindkey == keys:
                    fOn.write(str(b)+'\n')
                
        # Add all the deactivation keys
        for deact in finfo[3]:
            fOn.write(f"bind {deact} \"{finfo[-1]} exec {foff}\"\n")
        # For all other binds, we need to turn off current bind and activate theirs
        for other in excl:
            if finfo is other:
                continue
            # For each activation key in the other file.
            for act in other[2]:
                if len(act) == 2:
                    if finfo[0] != act[1]:
                        continue
                    act = act[0]
                otherfOn = other[0].removesuffix(".txt") + "on.txt"
                fOn.write(f'bind {act} "exec {foff}; {finfo[-1]} exec {otherfOn}"\n')
                
print(pastein)
