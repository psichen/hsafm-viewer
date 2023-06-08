import numpy as np
# from vispy.color import Colormap

class HSAFM:
    """read asd file into np.array"""

    def __init__(self, fname):

        self.fullName = fname  # full name
        with open(self.fullName) as f:
            self.fileVersion = np.fromfile(f, "i", 1)[0]
            self.fileHeaderSize = np.fromfile(f, "i", 1)[0]
            self.frameHeaderSize = np.fromfile(f, "i", 1)[0]
            self.encNumber = np.fromfile(f, "i", 1)[0]
            self.operationNameSize = np.fromfile(f, "i", 1)[0]
            self.commentSize = np.fromfile(f, "i", 1)[0]
            self.dataTypeCh1 = np.fromfile(f, "i", 1)[0]
            self.dataTypeCh2 = np.fromfile(f, "i", 1)[0]
            self.numberFramesRecorded = np.fromfile(f, "i", 1)[0]
            self.numberFramesCurrent = np.fromfile(f, "i", 1)[0]
            self.scanDirection = np.fromfile(f, "i", 1)[0]
            self.fileName = np.fromfile(f, "i", 1)[0]
            self.xPixel = np.fromfile(f, "i", 1)[0]
            self.yPixel = np.fromfile(f, "i", 1)[0]
            self.xScanRange = np.fromfile(f, "i", 1)[0]
            self.yScanRange = np.fromfile(f, "i", 1)[0]
            self.avgFlag = np.fromfile(f, "?", 1)[0]
            self.avgNumber = np.fromfile(f, "i", 1)[0]
            self.yearRec = np.fromfile(f, "i", 1)[0]
            self.monthRec = np.fromfile(f, "i", 1)[0]
            self.dayRec = np.fromfile(f, "i", 1)[0]
            self.hourRec = np.fromfile(f, "i", 1)[0]
            self.minuteRec = np.fromfile(f, "i", 1)[0]
            self.secondRec = np.fromfile(f, "i", 1)[0]
            self.xRoundDeg = np.fromfile(f, "i", 1)[0]
            self.yRoundDeg = np.fromfile(f, "i", 1)[0]
            self.frameAcqTime = np.fromfile(f, "f", 1)[0]
            self.sensorSens = np.fromfile(f, "f", 1)[0]
            self.phaseSens = np.fromfile(f, "f", 1)[0]
            self.offset = np.fromfile(f, "i", 4)  # booked region of 12 bytes
            self.machineNum = np.fromfile(f, "i", 1)[0]

            # ADRange
            self.ADRange = np.fromfile(f, "i", 1)[0]
            if self.ADRange == 2 ** 18 or self.ADRange == 3:
                self.ADRange = 10
            elif self.ADRange == 2 ** 17 or self.ADRange == 2:
                self.ADRange = 5
            elif self.ADRange == 2 * 16 or self.ADRange == 1:
                self.ADRange = 2
            else:
                print("!!!CAUTION!!!/n")
                print(f"{self.fullName}: ADRange: {self.ADRange}")
            self.ADResolution = np.fromfile(f, "i", 1)[0]

            self.xMaxScanRange = np.fromfile(f, "f", 1)[0]  # nm
            self.yMaxScanRange = np.fromfile(f, "f", 1)[0]  # nm
            self.xPizeoConstant = np.fromfile(f, "f", 1)[0]  # nm/V
            self.yPizeoConstant = np.fromfile(f, "f", 1)[0]  # nm/V
            self.zPizeoConstant = np.fromfile(f, "f", 1)[0]  # nm/V
            self.zDriveGain = np.fromfile(f, "f", 1)[0]
            self.operatorName = np.fromfile(f, "c", self.operationNameSize)
            self.comment = np.fromfile(f, "c", self.commentSize)

            # decode binary string
            self.operatorName = "".join(
                letter.decode("UTF-8") for letter in self.operatorName
            )
            self.comment = "".join(letter.decode("UTF-8") for letter in self.comment)

            # AFM data per frame
            self.voltage = []
            self.frameNumber = []
            self.frameMaxData = []
            self.frameMinData = []
            self.xOffset = []
            self.dataType = []
            self.xTilt = []
            self.yTilt = []
            self.laserFlag = []

            for _ in np.arange(self.numberFramesCurrent):
                self.frameNumber.extend(np.fromfile(f, "i", 1))
                self.frameMaxData.extend(np.fromfile(f, "u2", 1))
                self.frameMinData.extend(np.fromfile(f, "u2", 1))
                self.xOffset.extend(np.fromfile(f, "u2", 1))
                self.dataType.extend(np.fromfile(f, "u2", 1))
                self.xTilt.extend(np.fromfile(f, "f", 1))
                self.yTilt.extend(np.fromfile(f, "f", 1))
                self.laserFlag.extend(np.fromfile(f, "?", 12))

                voltage_temp = np.fromfile(f, "u2", self.xPixel * self.yPixel)
                voltage_temp = np.reshape(voltage_temp, (self.yPixel, self.xPixel))
                voltage_temp = voltage_temp[::-1][:]  # flip image upside-down
                self.voltage.append(voltage_temp)
            del voltage_temp

            self.voltage = np.array(self.voltage, dtype="float32")
            self.height = (
                -1
                * self.voltage
                * self.zPizeoConstant
                * self.zDriveGain
                * self.ADRange
                / 4096
            )
            self.height -= np.repeat(
                np.min(self.height, (1, 2)), self.yPixel * self.xPixel
            ).reshape((self.numberFramesCurrent, self.yPixel, self.xPixel))
