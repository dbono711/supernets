#!/usr/bin/env python
"""Docstring missing."""
import argparse
import ipaddress
import sys
from collections import defaultdict

networks = {}
prefixes = defaultdict(list)
verbose_output = True


def verbose_print(*args, **kwargs):
    if verbose_output:
        output = ' '.join(args)
        print(output)

def add_network(network):
    if network not in networks:
        networks[network] = network.prefixlen
        add_network_to_prefixes(network)

def delete_network(*args):
    for network in args:
        networks.pop(network, None)

def add_network_to_prefixes(network):
    prefixes[network.prefixlen].append(network)

def process_input(subnets):
    try:
        with open(subnets) as data:
            for net in data:
                try:
                    network = ipaddress.ip_network(net.strip().encode().decode(), strict=False)
                    add_network(network)
                except ValueError:
                    print(f"{net} is not a valid network")
    except IOError:
        print("File not found, goodbye!")
        sys.exit(1)

def process_prefixes(prefix=0):
    global prefixes
    if prefix < 128:
        process_prefixes(prefix + 1)
    if prefix in prefixes:
        verbose_print("="*79, "\nPrefix Length = %s" % (prefix))
        compare_networks_of_same_prefix_length(sorted(prefixes[prefix]))

def compare_networks_of_same_prefix_length(prefix_list):
    previous_net = None

    for current_net in prefix_list:
        if existing_supernet := find_existing_supernet(current_net):
            delete_network(current_net)
            verbose_print(f"{current_net} found in {existing_supernet}")

        elif previous_net is None:
            previous_net = current_net

        else:
            supernet1 = previous_net.supernet(prefixlen_diff=1)
            supernet2 = current_net.supernet(prefixlen_diff=1)

            if supernet1 == supernet2:
                add_network(supernet1)
                delete_network(previous_net, current_net)
                verbose_print(f"{previous_net} and {current_net} aggregate to {supernet1}")
                previous_net = None

            else:
                verbose_print(f"{previous_net} is unique")
                previous_net = current_net

    if previous_net is not None:
        verbose_print(f"{previous_net} is unique")

def find_existing_supernet(network):
    result = None
    for prefix in range(network.prefixlen - 1, 0, -1):
        super_network = network.supernet(new_prefix=prefix)
        if super_network in networks:
            result = super_network
            break
    return result

def main():
    parser = argparse.ArgumentParser(
        description="Supply the names of one of more files used for input. If no files \
        are supplied, the application will process standard input, allowing you to \
        pipe input from another programs output. Each network must be on its own line \
        and in CIDR (i.e., '216.58.192.0/24') format.")
    parser.add_argument('subnetFile', nargs=1, help="Path to file containing subnets")
    parser.add_argument('-m', '--maxprefixlen', type=int)
    args = parser.parse_args()
    subnets = args.subnetFile[0]
    process_input(subnets)
    process_prefixes()

    for network in sorted(networks, key=lambda ip: ip.network_address.packed):
        if args.maxprefixlen and network.prefixlen < args.maxprefixlen:
            small_supers = list(network.subnets(new_prefix=16))
            for new_super in small_supers:
                print(new_super)
        else:
            print(network)


if __name__ == "__main__":
    main()
