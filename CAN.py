import ctypes
import Queue
import types

import canlib


class pycanlibError(Exception):
    pass


class InvalidParameterError(pycanlibException):

    def __init__(self, parameterName, parameterValue, reason):
        self.parameterName = parameterName
        self.parameterValue = parameterValue
        self.reason = reason

    def __str__(self):
        return ("%s: invalid value '%s' for parameter '%s' - %s" %
          (self.__class__.__name__, self.parameterValue,
          self.parameterName, self.reason))


class InvalidBusParameterError(InvalidParameterError):
    pass


class InvalidMessageParameterError(InvalidParameterError):
    pass


class LogMessage(object):

    def __init__(self, timestamp=0):
        if not isinstance(timestamp, (types.IntType, types.FloatType,
          types.LongType)):
            raise InvalidMessageParameterError("timestamp", timestamp,
              ("expected int, float or long; received '%s'" %
              timestamp.__class__.__name__))
        if timestamp >= 0:
            self.timestamp = timestamp
        else:
            raise InvalidMessageParameterError("timestamp", timestamp,
              "timestamp value must be positive")

    def __str__(self):
        return "%.6f" % self.timestamp


class Message(LogMessage):

    def __init__(self, deviceID=0, data=[], dlc=0, flags=0, timestamp=0):
        LogMessage.__init__(self, timestamp)
        if not isinstance(deviceID, types.IntType):
            raise InvalidMessageParameterError("deviceID", deviceID,
              ("expected int; received '%s'" %
              deviceID.__class__.__name__))
        if deviceID not in range(0, 2 ** 11):
            raise InvalidMessageParameterError("deviceID", deviceID,
              "deviceID must be in range [0, 2**11-1]")
        self.deviceID = deviceID
        if len(data) not in range(0, 9):
            raise InvalidMessageParameterError("data", data,
              "data array length must be in range [0, 8]")
        for item in data:
            if not isinstance(item, types.IntType):
                raise InvalidMessageParameterError("data", data,
                  ("data array must contain only integers; found '%s'" %
                  item.__class__.__name__))
            if item not in range(0, 2 ** 8):
                raise InvalidMessageParameterError("data", data,
                  "data array element values must be in range [0, 2**8-1]")
        self.data = data
        if not isinstance(dlc, types.IntType):
            raise InvalidMessageParameterError("dlc", dlc,
              "expected int; received %s" % dlc.__class__.__name__)
        if dlc not in range(0, 9):
            raise InvalidMessageParameterError("dlc", dlc,
              "DLC value must be in range [0, 8]")
        self.dlc = dlc
        if not isinstance(flags, types.IntType):
            raise InvalidMessageParameterError("flags", flags,
              "expected int; received %s" % flags.__class__.__name__)
        if flags not in range(0, 2 ** 16):
            raise InvalidMessageParameterError("flags", flags,
              "flags value must be in range [0, 2**16-1]")
        self.flags = flags

    def __str__(self):
        _fieldStrings = []
        _fieldStrings.append(LogMessage.__str__(self))
        _fieldStrings.append("%.4x" % self.deviceID)
        _fieldStrings.append("%.4x" % self.flags)
        _fieldStrings.append("%d" % self.dlc)
        _dataStrings = []
        for byte in self.data:
            _dataStrings.append("%.2x" % byte)
        if len(_dataStrings) > 0:
            _fieldStrings.append(" ".join(_dataStrings))
        return "\t".join(_fieldStrings)


class InfoMessage(LogMessage):

    def __init__(self, timestamp=0, infoString=None):
        LogMessage.__init__(self, timestamp)
        self.infoString = infoString

    def __str__(self):
        if self.infoString != None:
            return ("%s\t%s" % (LogMessage.__str__(self), self.infoString))
        else:
            return "%s" % LogMessage.__str__(self)


class Bus(object):

    def __init__(self, channel=0, flags=0, speed=100000, tseg1=1, tseg2=1,
      sjw=1, noSamp=1):
        _numChannels = ctypes.c_int(0)
        canlib.canGetNumberOfChannels(ctypes.byref(_numChannels))
        if not isinstance(channel, types.IntType):
            raise InvalidBusParameterError("channel", channel,
              "expected int; received %s" % channel.__class__.__name__)
        if channel not in xrange(_numChannels.value):
            availableChannels = []
            for i in xrange(_numChannels.value):
                availableChannels.append(i)
            raise InvalidBusParameterError("channel", channel,
              ("channels available on this system: %s" %
                ", ".join(availableChannels)))
        self.channel = channel
        if not isinstance(flags, types.IntType):
            raise InvalidBusParameterError("flags", flags,
              "expected int; received %s" % flags.__class__.__name__)
        if flags not in range(0, 2 ** 16):
            raise InvalidBusParameterError("flags", flags,
              "flags value must be in range [0, 2**16-1]")