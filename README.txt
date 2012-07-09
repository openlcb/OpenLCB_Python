
For serial port access from Python, see:

http://pyserial.sourceforge.net/

For pyUnit (we use 1.4.1), see:

http://pyunit.sourceforge.net/


Issues:
    
How handle prereqs, like config needed for datagram test?  Use PIP nicely?
Fallback if PIP not present? Eventually need an input form where you can
specify (once) what is present and should be tested.  Or just test it all,
say what's not there, and let that be a record for later?
   


Planned tests:

datagram test should test permanent-error-NAK, which doesn't get retransmission.

need to merge in testOverlappingDatagrams.py to allTest

Configuration test:
    Check for reading not-defined space - does what?
    Decode the status bits in address-space-reply messages
    