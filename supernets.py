#!/usr/bin/env python
"""Docstring missing."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import fileinput
import ipaddress
import argparse
import sys


# define globals
networks = dict()
prefixes = defaultdict(list)
verbose_output = False


def verbose_print(*args, **kwargs):
    if verbose_output:
        output = ' '.join(args)
        print(output)


def add_network(*args):
    """ Adds network(s) to the global networks dictionary.
    Since network is a key value, duplicates are inherently removed.
    """
    global networks
    for network in args:
        if network not in networks:
            networks[network] = network.prefixlen
            add_network_to_prefixes(network)


def delete_network(*args):
    """Removes one of more networks from the global networks dictionary."""
    global networks
    for network in args:
        networks.pop(network, None)


def add_network_to_prefixes(network):
    """ Adds networks to the prefix dictionary.
    The prefix dictionary is keyed by prefixes.
    Networks of the same prefix length are stored in a list.
    """
    global prefixes
    prefix = network.prefixlen
    prefixes[prefix].append(network)


def process_input(subnets):
    """ Read each network from file and compare to the current supernet."""
    try:
        with open(subnets) as data:
            for net in data:
                try:
                    network = ipaddress.ip_network(net.strip().encode().decode(), strict=False)
                    add_network(network)
                except ValueError:
                    print('!!!', net, ' is not a valid network')
    except IOError:
        print("File not found, goodbye!")
        sys.exit(1)


def process_prefixes(prefix=0):
    """Read each list of networks starting with the largest prefixes."""
    global prefixes
    if prefix < 128:
        process_prefixes(prefix + 1)
    if prefix in prefixes:
        verbose_print("="*79, "\nPrefix Length = %s" % (prefix))
        compare_networks_of_same_prefix_length(sorted(prefixes[prefix]))


def compare_networks_of_same_prefix_length(prefix_list):
    previous_net = None
    for current_net in prefix_list:
        existing_supernet = find_existing_supernet(current_net)
        if existing_supernet:
            delete_network(current_net)
            verbose_print("%s found in %s" % (current_net, existing_supernet))
        elif previous_net is None:
            previous_net = current_net
        else:
            # Calculate a one bit larger subet and see if they are the same.
            supernet1 = previous_net.supernet(prefixlen_diff=1)
            supernet2 = current_net.supernet(prefixlen_diff=1)
            if supernet1 == supernet2:
                add_network(supernet1)
                delete_network(previous_net, current_net)
                verbose_print("%s and %s aggregate to %s"
                    % (previous_net, current_net, supernet1))
                previous_net = None
            else:
                verbose_print("%s is unique" % (previous_net))
                previous_net = current_net
    if previous_net is not None:
        verbose_print("%s is unique" % (previous_net))


def find_existing_supernet(network):
    """ This function checks if a subnet is part a of an existing supernet."""
    result = None
    for prefix in range(network.prefixlen - 1, 0, -1):
        super_network = network.supernet(new_prefix=prefix)
        if super_network in networks:
            result = super_network
            break
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Supply the names of one of more files used for input. " 
        "If no files are supplied, supernets will process standard input, "
        "allowing you to pipe input from another programs output. "
        "Each network must be on its own line and in CIDR format. "
        "supernets works with both IPv4 and IPv6 addresses.")
    parser.add_argument('subnetFile', nargs=1)
    parser.add_argument('-m', '--maxprefixlen', type=int)
    args = parser.parse_args()
    subnets = args.subnetFile[0]
    
    process_input(subnets)
    
    process_prefixes()
    
    for network in sorted(networks, key=lambda ip: ip.network_address.packed):
        if args.maxprefixlen:
            if network.prefixlen < args.maxprefixlen:
                small_supers = list(network.subnets(new_prefix=16))
                for new_super in small_supers:
                    print(new_super)
            else:
                print(network)
        else:
            print(network)


if __name__ == "__main__":
    main()


