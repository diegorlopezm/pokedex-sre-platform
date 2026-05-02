# Post-Mortem: Network Isolation and Forwarding Failure in Vagrant/Libvirt Environment

## Incident Summary
During the deployment of the [[Pokedex-SRE]] infrastructure laboratory, a total loss of connectivity (100% packet loss) was detected both towards the internet and between nodes in the `192.168.56.0/24` private network. The incident blocked [[Ansible]] provisioning and critical package downloads via `apt`. The **"smoking gun"** was identified as a kernel conflict on the host, where [[Kubernetes]] and [[Docker]] firewall rules intercepted and discarded traffic from the [[Libvirt]] bridges due to the `net.bridge.bridge-nf-call-iptables` parameter being enabled.

> [!IMPORTANT]
> **Business Impact:** This incident resulted in a total blockage of the [[IaC]] (Infrastructure as Code) Continuous Delivery pipeline. The Mean Time to Recovery ([[MTTR]]) was extended due to the opacity of [[Kubernetes]] networking rules residing on the host system.

---

## Chronology and Troubleshooting
1. **Detection**: Systematic failure of `ping 8.8.8.8` and `apt update` within the virtual machines.
2. **Layer 3 Analysis**: The `ip route get` command confirmed the [[Kernel]] was attempting to route traffic through the correct interfaces (`eth0` for management, `eth1` for data), but no responses were received.
3. **Layer 2 Analysis**: The [[ARP]] table showed `STALE` entries, and `arping` probes returned zero responses, indicating the packets reached the virtual bridge but were dropped before reaching the destination.
4. **Root Cause Identification**: It was discovered that `net.bridge.bridge-nf-call-iptables` was set to `1`. This forced Layer 2 bridge traffic to be processed by Layer 3 [[nftables]]/[[iptables]], where a global `policy DROP` from [[Kubernetes]] chains discarded the packets.

---

## Technical Tooling and Findings

| Command / Tool | Flag | Technical Purpose | Key Finding |
| :--- | :--- | :--- | :--- |
| `ip route get` | `[IP]` | Path determination | Confirmed L3 routing was logically correct but packets were disappearing. |
| `arping` | `-I eth1` | Layer 2 probing | Confirmed zero responses on the private segment; isolated the issue to the virtual bridge. |
| `tcpdump` | `-ni [bridge]`| Traffic capture | Observed `ECHO REQUEST` entering the bridge but never exiting the host's physical interface. |
| `nft` | `list ruleset` | Firewall inspection | Located `KUBE-SERVICES` and `KUBE-FORWARD` chains with `policy DROP` verdicts. |
| `sysctl` | `-w` | Kernel parameter tuning| Setting `bridge-nf-call-iptables=0` immediately restored the flow of traffic. |
| `bridge` | `link show` | Link association | Verified that all `vnet` interfaces were correctly "plugged" into the same virtual switch. |

---

## Root Causes
* **Netfilter Bridge Conflict**: The `net.bridge.bridge-nf-call-iptables` parameter enabled Layer 3 filtering on Layer 2 bridges, causing unintended interference.
* **Security Policy Clash**: Residual or active [[Kubernetes]]/[[Docker]] rules on the host enforced a restrictive `FORWARD` policy that did not account for [[Libvirt]] traffic.
* **Intentional Isolation Nuance**: The initial use of `forward_mode: "nat"` on the private network caused gateway collisions; switching to `forward_mode: "none"` was required to ensure strict **Intentional Isolation** for the data plane.

---

## Mitigation and Resolution
1. **Bridge Bypass**: Instead of globally disabling `bridge-nf-call-iptables`, we implemented high-priority bypass rules in the host's `FORWARD` chain via **Vagrant Triggers** to ensure granular traffic flow for the laboratory subnet.
2. **Network Refactoring**: Updated the `Vagrantfile` to set `libvirt__forward_mode: "none"` for the private network, preventing it from competing with the management network's default route.
3. **Firewalld Persistence**: Configured [[firewalld]] to treat [[Libvirt]] interfaces as part of the `trusted` zone to prevent future packet drops.
4. **Automation**: Implemented [[Vagrant Triggers]] to automatically apply these host-level fixes during `vagrant up` and clean them up during `vagrant destroy`.
