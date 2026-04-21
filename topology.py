from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class MyTopo(Topo):
    def build(self):

        # Hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Host connections
        self.addLink(h1, s1)
        self.addLink(h2, s4)

        # Redundant switch paths
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s3, s4)


if __name__ == '__main__':
    topo = MyTopo()

    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(
            name,
            ip='127.0.0.1',
            port=6633
        ),
        link=TCLink
    )

    net.start()
    print("Network Started")
    CLI(net)
    net.stop()