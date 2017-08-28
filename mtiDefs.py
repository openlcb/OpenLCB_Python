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

def mti_print(mti, source, dest, event, payload) :
    if (event != None and payload != None) :
        assert False, "invalid message event/payload"

    string = "            [0x" + ("000" + (hex(mti).upper()[2:]))[-3:] + "] <"
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
    if (event) :
        for x in event :
            string += ("00"+(hex(x).upper()[2:]))[-2:]
    elif (payload) :
        string += payload

    print string

