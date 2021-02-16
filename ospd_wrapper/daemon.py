# -*- coding: utf-8 -*-
# Copyright (C) 2014-2021 Greenbone Networks GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


# pylint: disable=too-many-lines

""" OSP wrapper template """

import logging
import time

from random import uniform

from ospd.ospd import OSPDaemon
from ospd.scan import ScanProgress, ScanStatus
from ospd.main import main as daemon_main
from ospd.network import target_str_to_list
from ospd.resultlist import ResultList

from ospd_wrapper import __version__

logger = logging.getLogger(__name__)


OSPD_DESC = """
This is an ospd wrapper template, which simulates a communication with a client,
generates example results, set hosts as 'started' and 'finished', calculates the
scan progress and finished the scan simulation.
"""

# This parameters are the server parameters.
# If the server is not able to shared its parameters, then
# the following are taken as default.
OSPD_PARAMS = {
    'example_param': {
        'type': 'boolean',
        'name': 'example_param',
        'default': 1,
        'mandatory': 1,
        'visible_for_client': True,
        'description': 'Some example param which is visible for the client',
    },
}


class OSPDwrapper(OSPDaemon):

    """ Class for ospd-wrapper daemon. """

    def __init__(self, *, niceness=None, lock_file_dir='/tmp/', **kwargs):
        """ Initializes the ospd-wrapper daemon's"""

        super().__init__(
            storage=dict,
            file_storage_dir=lock_file_dir,
            **kwargs,
        )

        self.server_version = __version__
        self._niceness = str(niceness)

        self.daemon_info['name'] = 'OSPd Wrapper'
        self.scanner_info['name'] = 'openvas'
        self.scanner_info['version'] = ''  # achieved during self.init()
        self.scanner_info['description'] = OSPD_DESC

        for name, param in OSPD_PARAMS.items():
            self.set_scanner_param(name, param)

        if not self.vts_version:
            self.load_vts()
            self.set_vts_version("1.2.3dev1")

    def load_vts(self):
        """ Load up the vts. It uses the internal ospd storage. """
        self.add_vt(
            vt_id="1234-5678",
            name="Vulnerability Test 1",
            vt_creation_time="Today",
        )

    @staticmethod
    def get_creation_time_vt_as_xml_str(  # pylint: disable=unused-argument
        vt_id: str, vt_creation_time
    ) -> str:
        return '<vt_creation_time>' + vt_creation_time + '</vt_creation_time>'

    def scheduler(self):
        """This method is called periodically to run tasks."""
        pass

    def check(self) -> bool:
        """Checks that the wrapper command line tool is found and
        is executable."""
        return True

    def stop_scan_cleanup(  # pylint: disable=arguments-differ
        self, scan_id: str
    ):
        """Make the necessary to finish the server gracefully, when the
        client stops a scan or something went wrong during the scan."""
        pass

    def target_is_finished(scan_id: str):
        """ This method can be used to check if the server finished"""
        pass

    def exec_scan(self, scan_id: str):
        """ Starts the scanner for scan_id scan. """

        # Get the host list
        target = self.scan_collection.get_host_list(scan_id)
        logger.info("The target list %s", target)
        host_list = target_str_to_list(target)

        # Get the port list
        ports = self.scan_collection.get_ports(scan_id)
        logger.info("The port list %s", ports)

        # Get exclude hosts list. It must not be scanned
        exclude_hosts = self.scan_collection.get_exclude_hosts(scan_id)
        logger.info("The exclude hosts list %s", exclude_hosts)

        # Get credentials for authenticated scans
        credentials = self.scan_collection.get_credentials(scan_id)
        for (
            service,
            credential,
        ) in credentials.items():
            cred_type = credential.get('type', '')
            username = credential.get('username', '')
            password = credential.get('password', '')
            logger.info(
                "Credential for %s: user: %s, type: %s",
                service,
                username,
                cred_type,
            )

        # Get the plugin list and its preferences, if the scanner
        # supports plugins
        nvts = self.scan_collection.get_vts(scan_id)

        # Ospd calculates the scan progress on fly, but it depends on the
        # results. Sometimes, the scanner can be more smart and detect
        # e.g. repeted hosts or hostnames which can not be resolved and
        # therefore will not be scanned.
        # In this cases, the amount of hosts scanned can differ with the amount
        # of hosts in the target list. Please consider to use the following
        # method if your scanner has the hability and provides these total hosts
        # and amount of dead hosts.
        self.set_scan_total_hosts(
            scan_id,
            count_total=len(host_list),
        )
        self.scan_collection.set_amount_dead_hosts(scan_id, total_dead=0)

        # Run the scan. This template does not run any scan, but generates
        # a fake result for each host in the  whole target list.
        # Also, it doesn't consider the excluded hosts. If the scanner allows
        # multiple hosts, you can excute the scanner just once and process
        # the results later.
        while host_list:
            # Get a host from the list
            current_host = host_list.pop()

            # Example using subprocess.Popen() to exec the scanner
            # cmd = []
            # if self._niceness:
            #    cmd += ['nice', '-n', self._niceness]
            #    logger.debug("Starting scan with niceness %s", self._niceness)
            # cmd += ['scanner_exec', current_host]
            # try:
            #    return subprocess.Popen(cmd, shell=False)
            # except (subprocess.SubprocessError, OSError) as e:
            #    # the command is not available
            #    logger.warning("Could not start scan process. Reason %s", e)
            #    return None

            # In some point you may want to check if something goes wrong or
            # if the scan was stopped by the client.
            # If your check is not successful, you can stop the server
            # gracefully.
            status = self.get_scan_status(scan_id)
            if status == ScanStatus.INTERRUPTED:
                self.stop_scan_cleanup(scan_id)
                logger.error(
                    'Something when wrong for task %s.',
                    scan_id,
                )
                return
            elif status == ScanStatus.STOPPED or status == ScanStatus.FINISHED:
                logger.debug(
                    'Task %s stopped or finished.',
                    scan_id,
                )
                return

            # Scan simulation for each single host.
            # Run the scan against the host, and generates results.
            res_list = ResultList()
            res_type = int(uniform(1, 5))
            # Error
            if res_type == 1:
                res_list.add_scan_error_to_list(
                    host=current_host,
                    hostname=current_host + ".hostname.net",
                    name="Some test name",
                    value="error running the script",
                    port=ports,
                    test_id="1234-5678",
                    uri="No location",
                )
            # Log
            elif res_type == 2:
                res_list.add_scan_log_to_list(
                    host=current_host,
                    hostname=current_host + ".hostname.net",
                    name="Some test name",
                    value="Some log",
                    port=ports,
                    qod="10",
                    test_id="1234-5678",
                    uri="No location",
                )
            # Host detail
            elif res_type == 3:
                res_list.add_scan_host_detail_to_list(
                    host=current_host,
                    hostname=current_host + ".hostname.net",
                    name="Some Test Name",
                    value="Some host detail",
                    uri="No location",
                )
            # Alarm
            else:
                res_list.add_scan_alarm_to_list(
                    host=current_host,
                    hostname=current_host + ".hostname.net",
                    name="Some Test Name",
                    value="Some Alarm",
                    port=ports,
                    test_id="1234-5678",
                    severity="10",
                    qod="10",
                    uri="No location",
                )

            # Add the result to the scan collection
            if len(res_list):
                logger.debug(
                    '%s: Inserting %d results into scan '
                    'scan collection table',
                    scan_id,
                    len(res_list),
                )
                self.scan_collection.add_result_list(scan_id, res_list)

            # Update the host status, so ospd can calculate the scan progress
            # This is quite importan, since the final scan status depends on
            # the progress calculation.
            finished_host = list()
            finished_host.append(current_host)
            self.sort_host_finished(scan_id, finished_host)

            # If you know exacly the host scan progress, you can use the
            # the following methods for a more precise progress calculation.
            host_progress = dict()
            # host_progress[current_host] = 45
            # host_progress[current_host] = ScanProgress.DEAD_HOST
            host_progress[current_host] = ScanProgress.FINISHED
            self.set_scan_progress_batch(scan_id, host_progress=host_progress)

            time.sleep(1)
        logger.debug('%s: End task', scan_id)


def main():
    """ OSP wrapper main function. """
    daemon_main('OSPD - wrapper', OSPDwrapper)


if __name__ == '__main__':
    main()
