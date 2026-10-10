// ======================================================================================================
//
// Copyright 2026 Heemin
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
// associated documentation files (the "Software"), to deal in the Software without restriction,
// including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
// LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
// IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
// WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
// ======================================================================================================

const fs = require('fs');

// ======================================================================================================

module.exports = { convertBitphaseJsonToNSFBytecode };

// ======================================================================================================
//
// Main Conversion Function
//
// ======================================================================================================

	let i_currentAddress = 0;
	let a_byteObjList = [];
	let a_labelAddrTbl = {};
function convertBitphaseJsonToNSFBytecode(btpModule = [], i_loadAddress = 0xA000) {
	// validation
	if (i_loadAddress > 0xFFFF || i_loadAddress < 0x0000) throw new Error("Load address must exist at 6502 memory range.");
	
	i_currentAddress = i_loadAddress;
	let a_byteObjList = [];
	let a_labelAddrTbl = {};

	return "test";
}

const pushByte = (val) => { a_byteObjList.push(val & 0xFF); i_currentAddress++; }
const pushWord = (val) => { a_byteObjList.push((val & 0xFF), ((val >> 8) & 0xFF)); i_currentAddress+=2; }
const setLabel = (labelstr) => a_labelAddrTbl[labelstr] = i_currentAddress;
const pushLabel = (labelname) => { a_byteObjList.push(labelname); i_currentAddress+=2; }

// ======================================================================================================
//
// Wrapper for CLI Excution
//
// ======================================================================================================

const zlib = require('zlib');
const path = require('path'); // really

if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
        console.log(`Usage: ${path.basename(process.argv[1])} <module.btp> <output.asm>`);
        process.exit(1);
    }

    try {
        fs.writeFileSync(args[1], convertBitphaseJsonToNSFBytecode(JSON.parse(zlib.gunzipSync(fs.readFileSync(args[0])).toString('utf8')), true), 'utf-8');
        console.log(`Data output without an error.`);
		process.exit(0);
    } catch (err) {
        console.error("Error:", err.message);
        process.exit(1);
    }
}