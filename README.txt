
For serial port access from Python, see:

http://pyserial.sourceforge.net/

For pyUnit (we use 1.4.1), see:

http://pyunit.sourceforge.net/

The CDI test uses the xmllint utility.  To install that on Windows, see:
http://flowingmotion.jojordan.org/2011/10/08/3-steps-to-download-xmllint/

Issues:
    
How handle prereqs, like config needed for datagram test?  Use PIP nicely?
Fallback if PIP not present? Eventually need an input form where you can
specify (once) what is present and should be tested.  Or just test it all,
say what's not there, and let that be a record for later?
   
----

May 30, 2015:

Working on the TCP protocol.  

For now, "Ethernet" in default.py refers to GridConnect-over-TCP, while "TCP" refers
to the native TCP protocol.
This is being developed in parallel files:
    tcpolcblink.py
    tcpolcbutils.py
    verifyNodeGlobalTcp.py
copied from the CAN versions.

Handling TCP vs CAN at low level (below tests) is hard because you 
want to be able to do format checks...  Probably want to have a way
of doing content checks that's shared across all wire protocols, plus
some wire-protocol specific parts?

-----

Planned tests:

datagram test should test permanent-error-NAK, which doesn't get retransmission.

need to merge in testOverlappingDatagrams.py to allTest

Configuration test:
    Check for reading not-defined space - does what?
    Decode the status bits in address-space-reply messages
    
-----

The contents of this directory is copyrighted and is subject to license. 

All the contributions to this directory, including code and documentation, are the property of their individual authors. All contributing authors make their work available here under specific licenses. You must comply with the license terms to use these works.
All software, in any form, is made available subject to either the GPL version 2.0 license or successor, or the LGPL version 2.0 license or successor. If you are uncertain about the terms of these licenses or how they apply to what you want to do, you must consult OpenLCB or the original author before copying, modifying, or distributing the software.
All documentation and other writings are made available subject to the Creative Commons Attribution-Share Alike 3.0 United States License. If you are uncertain about the terms of these licenses or how they apply to what you want to do, you must consult OpenLCB or the original author before copying, modifying, or distributing the works.
All hardware designs are made available subject to the CERN Open Hardware Licence version 1.1. If you are uncertain about the terms of these licenses or how they apply to what you want to do, you must consult OpenLCB or the original author before manufacturing, modifying, distributing or using the designs.
For other arrangements, contact the specific author directly.
The “OpenLCB” name and associated logos are trademarks of the OpenLCB association. They may only be used in association with the documentation and software presented here. We are continuously working improving the documentation and software, including writing compatibility tests, and we reserve the right to publish our observations on compatibility of devices that use the “OpenLCB” name and associated logos.
The NMRA says that the “NMRAnet” name and associated logo are their trademarks. The NMRA determines the licensing status for its Standards and/or Recommended Practices.
Other terms appearing on this web site may be trademarks belonging to others.

Authors include:

    Bob Jacobsen jacobsen@mac.com

