from hsafm_base import HSAFM
import sys
import os
import csv

file_path = sys.argv[1]
assert file_path.endswith('asd'), "input .asd file"
file_dir = os.path.dirname(file_path)
file_name = os.path.basename(file_path)[:-4]
df = HSAFM(file_path)

df.fps = 1/df.frameAcqTime*1e3
df.velocity = df.xScanRange*2*df.yPixel/df.frameAcqTime # um/s
df.samplingFreq = df.xPixel*2*df.yPixel/df.frameAcqTime # KHz
df.oscillation = 600/df.samplingFreq # default tip resonant frequency: 600 KHz
df.strike = 1e3/df.velocity*600/df.frameAcqTime # (s-1)
df.xResolution = df.xScanRange/df.xPixel # nm
df.yResolution = df.yScanRange/df.yPixel # nm

params = [
        ['xScanRange', df.xScanRange, 'nm'],
        ['yScanRange', df.yScanRange, 'nm'],
        ['xPixel', df.xPixel],
        ['yPixel', df.yPixel],
        ['xResolution', df.xResolution, 'nm'],
        ['yResolution', df.yResolution, 'nm'],
        ['frameNumber', df.numberFramesRecorded],
        ['frameTiem', df.frameAcqTime, 'ms'],
        ['fps', df.fps],
        ['tipVelocity', df.velocity, 'um/s'],
        ['sampleFreq', df.samplingFreq, 'KHz'],
        ['oscillation', df.oscillation],
        ['strike', df.strike],
        ]

with open(os.path.join(file_dir, f"{file_name}.txt"), 'w') as f:
    writer = csv.writer(f)
    writer.writerows(params)
