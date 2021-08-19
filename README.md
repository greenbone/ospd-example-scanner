![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_logo_resilience_horizontal.png)

:warning: This repository is unmaintained and will not get any further changes!

# ospd-example-scanner

This is an OSP example scanner useful as a starting point for writing an OSP server implementation

## Installation

### Requirements

Python 3.7 and later is supported.

## Usage

There are no special usage aspects for this module beyond the generic usage
guide.

Please follow the general usage guide for ospd-based scanners:

  <https://github.com/greenbone/ospd/blob/master/doc/USAGE-ospd-scanner.md>

For starting the daemon with the default options

    ospd-example-scanner -f

or you can copy the example configuration file in doc/ospd.conf and run 
   
    ospd-example-scanner -c <path-to-file>/ospd.conf

The ospd-example-scanner uploads a single VT as example

    gvm-cli --protocol OSP --timeout 120 socket --socketpath=/tmp/ospd-example-scanner.sock --xml "<get_vts/>"

With the gvm-cli tool, run the following command to test the ospd-example-scanner.

    gvm-cli --protocol OSP --timeout 120 socket --socketpath=/tmp/ospd-example-scanner.sock --xml "<start_scan scan_id='829097a9-85d5-4bb8-bac0-e64c362b2836'><targets><target><hosts>192.168.0.1</hosts><exclude_hosts></exclude_hosts><finished_hosts/><ports>T:22</ports><credentials><credential port='22' service='ssh' type='up'><username>some_user</username><password>some_path</password></credential></credentials></target></targets><scanner_params></scanner_params></start_scan>"

    gvm-cli --protocol OSP --timeout 120 socket --socketpath=/tmp/ospd-example-scanner.sock --xml "<stop_scan scan_id='829097a9-85d5-4bb8-bac0-e64c362b2836'/>"

    gvm-cli --protocol OSP --timeout 120 socket --socketpath=/tmp/ospd-example-scanner.sock --xml "<get_scans scan_id='829097a9-85d5-4bb8-bac0-e64c362b2836'/>"

    gvm-cli --protocol OSP --timeout 120 socket --socketpath=/tmp/ospd-example-scanner.sock --xml "<delete_scan scan_id='829097a9-85d5-4bb8-bac0-e64c362b2836'/>"

## Support

For any question on the usage of this template please use the [Greenbone
Community Portal](https://community.greenbone.net/c/gse).

## Maintainer

This project is maintained by [Greenbone Networks
GmbH](https://www.greenbone.net/).

## Contributing

Your contributions are highly appreciated.

For development you should use [poetry](https://python-poetry.org)
to keep you python packages separated in different environments. First install
poetry via pip

    python3 -m pip install --user poetry

Afterwards run

    poetry install

in the checkout directory of ospd-example-scanner (the directory containing the
`pyproject.toml` file) to install all dependencies including the packages only
required for development.

The ospd-example-scanner repository uses [autohooks](https://github.com/greenbone/autohooks)
to apply linting and auto formatting via git hooks. Please ensure the git hooks
are active.

    poetry install
    poetry run autohooks activate --force

## License

Copyright (C) 2018-2021 [Greenbone Networks GmbH](https://www.greenbone.net/)

Licensed under the [GNU Affero General Public License v3.0 or later](COPYING).
