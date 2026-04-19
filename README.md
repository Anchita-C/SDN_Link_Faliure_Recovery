# Link Failure Detection and Recovery with Ryu and Mininet

This project contains a Ryu OpenFlow 1.3 controller that learns host MAC
locations, discovers the switch topology, computes shortest paths, and
reroutes traffic when a link failure is reported by Ryu topology events.

## Files

* `ryu_link_failure_recovery_controller.py`: Ryu controller application
* `three_switch_ring_topology.py`: Mininet topology with three switches and alternate paths

## Requirements

Install Ryu and Mininet in your SDN VM or Linux environment:

```bash
pip install ryu
sudo apt install mininet openvswitch-switch
```

Ryu topology discovery requires LLDP observation, so always run the controller
with `--observe-links`.

## Run the Ryu Controller

From this directory:

```bash
cd ~/ryu_link_recovery
ryu-manager --observe-links --ofp-tcp-listen-port 6653 ryu_link_failure_recovery_controller.py
```

Expected logs include messages like:

```text
Link detected: s1:2 -> s2:1
Link failure occurs: s1:2 -> s2:1
New path installed: 00:00:00:00:00:01 -> 00:00:00:00:00:02 via s1 -> s3 -> s2
```

## Start a Mininet Topology with Alternate Paths

In a second terminal, start Mininet with 3 switches and redundant links:

```bash
sudo mn --controller=remote,ip=127.0.0.1,port=6653 \
  --switch=ovsk,protocols=OpenFlow13 \
  --custom three_switch_ring_topology.py \
  --topo threering
```

This creates switch links `s1-s2`, `s2-s3`, and `s1-s3`, so traffic has an
alternate route when one switch link fails.

## Verify Basic Connectivity

Inside the Mininet CLI:

```text
mininet> net
mininet> links
mininet> pingall
mininet> h1 ping -c 5 h3
```

Start a longer ping so rerouting can be observed during a failure:

```text
mininet> h1 ping h3
```

## Simulate Link Failure

While the ping is running, bring down the `s1-s2` link:

```text
mininet> link s1 s2 down
```

The controller should log the failure, delete stale flows for affected host
pairs, compute a new path, and install replacement flow rules.

Bring the link back:

```text
mininet> link s1 s2 up
```

You can also fail the `s2-s3` link:

```text
mininet> link s2 s3 down
mininet> link s2 s3 up
```

## Verify with iperf

Inside Mininet:

```text
mininet> iperf h1 h3
```

For a longer TCP test:

```text
mininet> h3 iperf -s &
mininet> h1 iperf -c h3 -t 20
```

During the 20-second test, run:

```text
mininet> link s1 s2 down
```

Traffic should continue over the alternate `s1-s3` path after a short
reconvergence delay.

## Useful Debugging Commands

Show switch flow tables:

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
sudo ovs-ofctl -O OpenFlow13 dump-flows s2
sudo ovs-ofctl -O OpenFlow13 dump-flows s3
```

Clean Mininet state after testing:

```bash
sudo mn -c
```

---
