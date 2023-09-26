# supernets

Given a list of IP networks, this command line application will produce the smallest list of contiguous supernets that aggregate all of those networks.

## Usage
Supply the path of a file containing IPv4 or IPv6 subnets in CIDR notation (i.e., '216.58.192.0/24'). Each network must be on its own line.

`-h, --help     ` displays help.<br>

```
python supernets.py test_nets/google_nets.txt
```

## Logic
A global networks dictionary is created and all networks are added to it. Using a dictionary prevents duplicate networks. Networks are stored as ```ipaddress.ip_network``` objects.

For each network, we recursively decrement the prefix length, checking for existing networks of an exact match.  Finding one indicates that the current network is a subnet of an existing supernet and therefore we discard the subnetwork.

All non-duplicate networks are added to a prefix dictionary. Each prefix entry in the dictionary is a list of networks of the same prefix length.  The list of networks of the same prefix length is sorted and each network can then be compared to the next network, to test is they are both contiguous and can be aggregated together.  This test is done by decrementing the prefix length of each network and comparing the new values. If the two resulting networks are the same network, then we discard the original two networks and store the new aggregate in the two dictionaries.
