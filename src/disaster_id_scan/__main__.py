# SPDX-FileCopyrightText: 2023-present anjomro <py@anjomro.de>
#
# SPDX-License-Identifier: EUPL-1.2
import sys

if __name__ == "__main__":
    from disaster_id_scan.cli import disaster_id_scan

    sys.exit(disaster_id_scan())
