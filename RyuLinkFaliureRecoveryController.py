from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class LinkFailureController(object):

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        log.info("Switch %s connected", connection.dpid)

    def _handle_PacketIn(self, event):
        packet = event.parsed

        if not packet.parsed:
            return

        # Flood packets initially
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.in_port = event.port
        self.connection.send(msg)


def start_switch(event):
    log.info("Controlling %s", event.connection)
    LinkFailureController(event.connection)


def launch():
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    log.info("Custom SDN Controller Started")