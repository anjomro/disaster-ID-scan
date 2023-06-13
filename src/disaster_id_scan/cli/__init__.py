# SPDX-FileCopyrightText: 2023-present anjomro <py@anjomro.de>
#
# SPDX-License-Identifier: EUPL-1.2
import click

from disaster_id_scan.__about__ import __version__
from disaster_id_scan.id_scanner import id_scanner
from disaster_id_scan.ui import start_gui


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="Disaster ID Scan")
def disaster_id_scan():
    start_gui()


# Command to start id scanner as cli application
@click.command()
@click.option('--cam', '-c', default=0, help='Camera ID to use, default 0')
def scan(cam):
    """Starts ID scanner"""
    id_scanner(cam)


# Register commands
disaster_id_scan.add_command(scan)
