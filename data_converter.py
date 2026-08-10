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

# ======================================================================================================

def output_bytes(f, data_list, max_per_line=16, prefix=""):
    lines = []
    for i in range(0, len(data_list), max_per_line):
        chunk = data_list[i:i + max_per_line]
        formatted = []
        for val in chunk:
            if isinstance(val, int): formatted.append(f"{prefix}${val:02x}")
            else:                    formatted.append(f"{prefix}{val}")
        
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
    #   .WORD @tabl_list
    #   (96*2 bytes of note period table split in LSB and MSB)
    #   (pattern ptrs listed as pattern order)
    with open(sys.argv[2], 'w') as f: f.write(f"bp_{song_name}_header:\n")
    with open(sys.argv[2], 'a') as outf:
        outf.write(f"{DIR_WORD}@inst_list\n{DIR_WORD}@tabl_list\n")
        
        # write note table
        output_bytes(outf, module["songs"][0]["tuningTable"], 12, "<") # length SHOULD be 96
        output_bytes(outf, module["songs"][0]["tuningTable"], 12, ">") # length SHOULD be 96
        
        # write pattern list (ends with $00FF. end condition: if MSB is 0)
        for i in range (0, len(module["patternOrder"])): outf.write(f"{DIR_WORD}@pat_{i}\n")
        outf.write(f"{DIR_BYTE}$FF, 0\n")
        
        # write inst list
        outf.write(f"\n@inst_list:\n") # label
        # for i in range (0, len(module["instruments"])):