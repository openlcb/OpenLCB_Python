#!/usr/bin/env python
'''
MTI Constants

@author: Stuart Baker
'''

INITIALIZATION_COMPLETE         = 0x0100
VERIFY_NODE_ID_ADDRESSED        = 0x0488
VERIFY_NODE_ID_GLOBAL           = 0x0490
VERIFY_NODE_ID_NUMBER           = 0x0170
OPTIONAL_INTERACTION_REJECTED   = 0x0068
TERMINATE_DUE_TO_ERROR          = 0x00A8

PROTOCOL_SUPPORT_INQUIRY        = 0x0828
PROTOCOL_SUPPORT_REPLY          = 0x0668

IDENTIFY_CONSUMER               = 0x08F4
CONSUMER_RANGE_IDENTIFIED       = 0x04A4
CONSUMER_IDENTIFIED_UNKNOWN     = 0x04C7
CONSUMER_IDENTIFIED_VALID       = 0x04C4
CONSUMER_IDENTIFIED_INVALID     = 0x04C5
CONSUMER_IDENTIFIED_RESERVED    = 0x04C6
IDENTIFY_PRODUCER               = 0x0914
PRODUCER_RANGE_IDENTIFIED       = 0x0524
PRODUCER_IDENTIFIED_UNKNOWN     = 0x0547
PRODUCER_IDENTIFIED_VALID       = 0x0544
PRODUCER_IDENTIFIED_INVALID     = 0x0545
PRODUCER_IDENTIFIED_RESERVED    = 0x0546
IDENTIFY_EVENTS_ADDRESSED       = 0x0968
IDENTIFY_EVENTS_GLOBAL          = 0x0970
LEARN_EVENT                     = 0x0594
EVENT_REPORT                    = 0x05B4

TRACTION_CONTROL_COMMAND        = 0x05EB
TRACTION_CONTROL_REPLY          = 0x01E9
TRACTION_PROXY_COMMAND          = 0x05EA
TRACTION_PROXY_REPLY            = 0x01E8

XPRESSNET                       = 0x0820

REMOTE_BUTTON_REQUEST           = 0x0948
REMOTE_BUTTON_REPLY             = 0x0549

SIMPLE_TRAIN_NODE_IDENT_REQUEST = 0x0DA8
SIMPLE_TRAIN_NODE_IDENT_REPLY   = 0x0A08

SIMPLE_NODE_IDENT_REQUEST       = 0x0DE8
SIMPLE_NODE_IDENT_REPLY         = 0x0A08

DATAGRAM                        = 0x1C48
DATAGRAM_RECEIVED_OK            = 0x0A28
DATAGRAM_REJECTED               = 0x0A48

STREAM_INITIATE_REQUEST         = 0x0CC8
STREAM_INITIATE_REPLY           = 0x0868
STREAM_DATA_SEND                = 0x1F88
STREAM_DATA_PROCEED             = 0x0888
STREAM_DATA_COMPLETE            = 0x08A8

## Message structure.
class OlcbMessage :
    ## Constructor.
    # @param mti Message Type Indication
    # @param source source Node ID
    # @param dest destination Node ID
    # @param event 8-byte event, mutually exclusive with payload
    # @param payload payload bytes, mutually exclusive with event
    def __init__(self, mti=None, source=None, dest=None, event=[],
                 payload=[]) :
        self.mti = mti
        self.source = source
        self.dest = dest
        self.event = list(event)
        self.payload = list(payload)

    ## Set the MTI.
    # @param mti MTI to set
    def set_mti(self, mti) :
        self.mti = mti

    ## Set the source Node ID.
    # @param source Node ID to set
    def set_source(self, source) :
        self.source = source

    ## Set the destination Node ID.
    # @param dest Node ID to set
    def set_dest(self, dest) :
        self.dest = dest

    ## Set the event from a hex string representation.
    # @param event hex string containing event
    def set_event_from_hex_string(self, event) :
        self.event = [int(event[0:2],   16), int(event[2:4],   16),
                      int(event[4:6],   16), int(event[6:8],   16),
                      int(event[8:10],  16), int(event[10:12], 16),
                      int(event[12:14], 16), int(event[14:16], 16)]

    ## Append a list to the end of the data payload.
    # @param list_data data to append
    def append_list_data(self, list_data) :
        for x in list_data :
            self.payload.append(x)

    ## Append a data string to the end of the data paylaod.
    # @param data to append
    def append_data(self, data) :
        for x in range(len(data)) :
            self.payload.append(data[x])

    ## Append a data string to the end of the data paylaod.
    # @param data to append
    def append_data_from_hex_string(self, data) :
        x = 0
        while (x < len(data)) :
            self.payload.append(int(data[x:x+2], 16))
            x += 2

    ## Get the MTI of the message.
    # @return MTI
    def get_mti(self) :
        return self.mti

    ## Get the source Node ID of the message.
    # @return Node ID
    def get_source(self) :
        return self.source

    ## Get the destination Node ID of the message.
    # @return Node ID
    def get_dest(self) :
        return self.dest

    ## Get the event payload of the message.
    # @return event
    def get_event(self) :
        return self.event

    ## Get the data payload of the message.
    # @return payload
    def get_payload(self) :
        return self.payload

## Convert an OlcbMessage into a string representation.
# @param message OlcbMessage instance
# @return string representation
def olcb_message_to_string(message) :
    mti = message.get_mti()
    source = message.get_source()
    dest = message.get_dest()
    event = message.get_event()
    payload = message.get_payload()

    if (event != [] and payload != []) :
        assert False, "invalid message event/payload"

    string = "[0x" + ("000" + (hex(mti).upper()[2:]))[-3:] + "] <"
    for x in source :
        string += ("00"+(hex(x).upper()[2:]))[-2:] + "."
    string = string[:len(string) -1]
    string += "> "
    if (dest != None) :
        string += "<"
        for x in dest :
            string += ("00"+(hex(x).upper()[2:]))[-2:] + "."
        string = string[:len(string) -1]
        string += "> "
    if (event != []) :
        for x in event :
            string += ("00"+(hex(x).upper()[2:]))[-2:]
    elif (payload != []) :
        for x in payload :
            string += ("00"+(hex(x).upper()[2:]))[-2:]

    return string


