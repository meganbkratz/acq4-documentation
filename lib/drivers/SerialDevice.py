import serial, time

class TimeoutError(Exception):
    """Raised when a serial communication times out."""
    pass

class DataError(Exception):
    """Raised when a serial communication is corrupt."""
    pass

class SerialDevice(object):
    """
    Class used for standardizing access to serial devices. 

    Provides some commonly used functions for reading and writing 
    serial packets.
    """
    def __init__(self, **kwds):
        """
        All keyword arguments define the default arguments to use when 
        opening the serial port (see pyserial Serial.__init__).

        If both 'port' and 'baudrate' are provided here, then 
        self.open() is called automatically.
        """
        self.serial = None
        self.__serialOpts = {
            'bytesize': serial.EIGHTBITS, 
            'timeout': 0, # no timeout. See SerialDevice._readWithTimeout()
        }
        self.__serialOpts.update(kwds)

        if 'port' in kwds and 'baudrate' in self.__serialOpts:
            self.open()


    def open(self, port=None, baudrate=None, **kwds):
        """ Open a serial port. If this port was previously closed, then calling 
        open() with no arguments will re-open the original port with the same settings.
        All keyword arguments are sent to the pyserial Serial.__init__() method.
        """
        if port is None:
            port = self.__serialOpts['port']
        if baudrate is None:
            baudrate = self.__serialOpts['baudrate']

        if isinstance(port, basestring) and port.lower()[:3] == 'com':
            port = int(port[3:]) - 1

        self.__serialOpts.update({
            'port': int(port),
            'baudrate': baudrate,
            })
        self.__serialOpts.update(kwds)
        self.serial = serial.Serial(**self.__serialOpts)

    def close(self):
        """Close the serial port."""
        self.serial.close()
        self.serial = None

    def readAll(self):
        """Read all bytes waiting in buffer; non-blocking."""
        n = self.serial.inWaiting()
        if n > 0:
            return self.serial.read(n)
        return ''
    
    def write(self, data):
        """Write *data* to the serial port"""
        self.serial.write(data)

    def read(self, length, timeout=5, term=None):
        """
        Read *length* bytes or raise TimeoutError after *timeout* has elapsed.

        If *term* is given, check that the pachet is terminated with *term* and 
        return the packet excluding *term*. If the packet is not terminated 
        with *term*, then DataError is raised.
        """
        #self.serial.setTimeout(timeout) #broken!
        packet = self._readWithTimeout(length, timeout)
        if len(packet) < length:
            raise TimeoutError("Timed out waiting for serial data (received so far: %s)" % repr(packet))
        if term is not None:
            if packet[-len(term):] != term:
                self.clearBuffer()
                raise DataError("Packet corrupt: %s (len=%d)" % (repr(packet), len(packet)))
            return packet[:-len(term)]
        return packet
        
    def _readWithTimeout(self, nBytes, timeout):
        # Note: pyserial's timeout mechanism is broken (specifically, calling setTimeout can cause 
        # serial data to be lost) so we implement our own in readWithTimeout().
        start = time.time()
        packet = ''
        # Interval between serial port checks is adaptive:
        #   * start with very short interval for low-latency reads
        #   * iteratively increase interval duration to reduce CPU usage on long reads
        sleep = 100e-6  # initial sleep is 100 us
        while time.time()-start < timeout:
            waiting = self.serial.inWaiting()
            if waiting > 0:
                readBytes = min(waiting, nBytes-len(packet))
                packet += self.serial.read(readBytes)
                sleep = 100e-6  # every time we read data, reset sleep time
            if len(packet) >= nBytes:
                break
            time.sleep(sleep)
            sleep = min(0.05, 2*sleep) # wait a bit longer next time
        return packet


    def readUntil(self, term, minBytes=0, timeout=5):
        """Read from the serial port until *term* is received, or *timeout* has elapsed.

        If *minBytes* is given, then this number of bytes will be read without checking for *term*.
        Returns the entire packet including *term*.
        """
        start = time.time()

        if minBytes > 0:
            packet = self.read(minBytes, timeout=timeout)
        else:
            packet = b''

        while True:
            elapsed = time.time()-start
            if elapsed >= timeout:
                raise TimeoutError("Timed out while reading serial packet. Data so far: '%s'" % repr(packet))
            try:
                packet += self.read(1, timeout=timeout-elapsed)
            except TimeoutError:
                raise TimeoutError("Timed out while reading serial packet. Data so far: '%s'" % repr(packet))
            if len(packet) > minBytes and packet[-len(term)] == term:
                return packet


    def clearBuffer(self):
        ## not recommended..
        d = self.readAll()
        time.sleep(0.1)
        d += self.readAll()
        if len(d) > 0:
            print self, "Warning: tossed serial data ", repr(d)
        return d



if __name__ == '__main__':
    import sys, os
    try:
        port, baud = sys.argv[1:3]
    except:
        print "Usage: python -i SerialDevice port baudrate"
        os._exit(1)

    sd = SerialDevice(port=port, baudrate=baud)
    print ""
    print "Serial port opened and available as 'sd'."
    print "Try using sd.write(...), sd.readAll(), and sd.read(length, term, timeout)"
