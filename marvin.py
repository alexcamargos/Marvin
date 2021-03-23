#  #!/usr/bin/env python
#  encoding: utf-8
#
#  --------------------------------------------------------------------------------------------------------------------
#
#  Name: marvin.py
#  Version: 0.0.1
#  Summary: Marvin a Pinpoint Network Problems
#           Visualize network performance data across hundreds of targets with tools built for monitoring both
#           local and remote devices, helping you find and fix problems fast. chegar a sua total liquidação.
#
#  Author: Alexsander Lopes Camargos
#  Author-email: alcamargos@vivaldi.net
#
#  License: MIT
#
#  --------------------------------------------------------------------------------------------------------------------

"""
Marvin a Pinpoint Network Problems

Visualize network performance data across hundreds of targets with tools built for monitoring both
local and remote devices, helping you find and fix problems fast. chegar a sua total liquidação.
"""

import sys

from commands import PingCommand


def ping(destination,
         timeout=2,
         count=5,
         size=24,
         payload=None,
         sweep_start=None,
         sweep_end=None,
         dont_fragment=False,
         verbose=False,
         output=sys.stdout,
         match=False):
    """Pings a remote host."""

    ping_command = PingCommand(destination,
                               timeout,
                               count,
                               size,
                               payload,
                               sweep_start,
                               sweep_end,
                               dont_fragment,
                               verbose,
                               output,
                               match)

    print(f'\nPinging {ping_command.destination}:\n', file=output)

    ping_responses = ping_command.run()

    print(f'\nPing statistics for {ping_command.destination}: ')

    print(f'\tPackets: Sent = {ping_command.count}, '
          f'Received = {(ping_command.count - ping_responses.packets_lost) :.0f}, '
          f'Lost = {ping_responses.packets_lost :.0f} '
          f'<{((ping_responses.packets_lost / ping_command.count) * 100) :.0f}% loss>',
          file=output)

    print('\nApproximate round trip times in milliseconds:')

    print(f'\tMinimum = {ping_responses.rtt_min_ms}ms, '
          f'Maximum = {ping_responses.rtt_max_ms}ms, '
          f'Average = {ping_responses.rtt_avg_ms}ms',
          file=output)


def main():
    """Main application."""
    destination = input('The remote hostname or IP address to ping: ') or 'google.com'
    ping(destination, verbose=True)


if __name__ == '__main__':
    main()
