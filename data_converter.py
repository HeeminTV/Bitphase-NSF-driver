# ======================================================================================================
#
# Copyright 2026 Heemin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the “Software”), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ======================================================================================================

import gzip
import json
import sys

DIR_BYTE = "        .byte " # not sure about NESASM
DIR_WORD = "        .word " # not sure about NESASM but i'm not gonna support that shit anyway

SWEEPSHIFT_CONV = [0x17,0x16,0x15,0x14,0x13,0x12,0x11,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07]

# ======================================================================================================

def output_bytes(f, data_list, max_per_line=16, prefix=""):
    lines = []
    for i in range(0, len(data_list), max_per_line):
        chunk = data_list[i:i + max_per_line]
        formatted = []
        for val in chunk:
            if isinstance(val, int): formatted.append(f"{prefix}${val:02x}") # number
            else:                    formatted.append(f"{prefix}{val}") # label
        
        lines.append(DIR_BYTE + ", ".join(formatted))    
        
    f.write("\n".join(lines) + "\n")
    return
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Arguments: <input.btp> <output.asm>")
        sys.exit()

    with gzip.open(sys.argv[1], "rt", encoding="utf-8") as f: 
        module = json.load(f)
        print(f"Loaded json without error")
        
    if module["name"] == '':
        if module["author"] == '':  song_name = os.path.splitext(os.path.basename(sys.argv[2]))[0]
        else:                       song_name = module["author"] + '_song'
    else:                           song_name = module["name"]
    song_name = "".join(c if ("a" <= c <= "z" or "A" <= c <= "Z") else "_" for c in song_name)
    print(f"Song name: {song_name}")
        
    # write header
    
    # bp_song_header:
    #   .WORD @inst_list
    #   .WORD @table_list
    #   .BYTE inital_speed, -1
    #   (96*2 bytes of note period table split in LSB and MSB)
    #   (pattern ptrs listed as pattern order)
    with open(sys.argv[2], 'w') as f: f.write(f"bp_{song_name}_header:\n")
    with open(sys.argv[2], 'a') as outf:
        init_speed = module["songs"][0]["initialSpeed"]
        outf.write(f"{DIR_WORD}@inst_list\n{DIR_WORD}@table_list\n{DIR_BYTE}{init_speed}, $FF\n")
        
        # write note table
        output_bytes(outf, module["songs"][0]["tuningTable"], 12, "<") # length SHOULD be 96
        output_bytes(outf, module["songs"][0]["tuningTable"], 12, ">") # length SHOULD be 96
        
        # write pattern list (ends with $00FF. end condition: if MSB is 0)
        for i in range(0, len(module["patternOrder"])): outf.write(f"{DIR_WORD}@pat_{i}\n")
        outf.write(f"{DIR_BYTE}$FF, 0\n")
        
        # write inst list
        outf.write(f"\n@inst_list:\n") # label
        
        instid_replace_tbl={}
        for i, item in enumerate(module["instruments"]): # make convert table
            instid_replace_tbl[item["id"]] = i
            outf.write(f"{DIR_WORD}@inst_{i}\n")
        
        # write inst data (TODO: move to below table list and table data)
        
        # inst data format: 4 bytes per one row, loop by having negative first byte.
        # LRAPPPPP, R = reset phase, A = tone acc, P = tone offset MSB, L = bit 0 is MSB of loop row offset and next byte is LSB
        # WW0EVVVV, W = pulse width, E = env/constant, V = volume
        # PPPPPPPP, P = tone offset LSB
        # ERRRSSSS, E = enable sweep, R = speed, S = shift

        for i in range(0, len(instid_replace_tbl)): # i = inst number
            outf.write(f"\n@inst_{i}:\n")
            for j in range(0, len(module["instruments"][i]["rows"])):
                instrow = module["instruments"][i]["rows"][j]

                byte0 = (0x40 if instrow["retrigger"] else 0x00)|(0x20 if instrow["toneAccumulation"] else 0x00)|((instrow["toneAdd"]>>8)&0x1F)
                byte1 = ((instrow["pulseWidth"]<<6)&0xC0)|(0x00 if instrow["envelope"] else 0x10)|(instrow["volumeOrRate"]&0x0F)
                byte2 = instrow["toneAdd"]&0xFF
                byte3 = (0x80 if instrow["sweep"] else 0x00)|((instrow["sweepRate"]&0x07)<<4)|(SWEEPSHIFT_CONV[instrow["sweepShift"]+7]&0x0F)
                
                outf.write(f"{DIR_BYTE}${byte0:02x}, ${byte1:02x}, ${byte2:02x}, ${byte3:02x}\n")
            loopoffset = j-module["instruments"][i]["loop"]+1
            outf.write(f"{DIR_BYTE}${(0x80|((loopoffset>>8)&0x01)):02x}, ${(loopoffset&0xFF):02x}\n")
        
        # write table list
        # outf.write(f"\n@table_list:\n")
        # for i in range (0, len(module["tables"])):
            # if module["tables"][i]["id"] 
        
        # pattern data format: (it isn't CPU friendly but saves lot of space)
        # $00-$5F = notes (terminate reading)
        # $60-$8F = effects without terminating reading
        # $90-$BF = effects with terminating reading
        # $C0-$CF = volume column (terminate reading?)
        # $D0-$FF = seq delay (terminate reading)