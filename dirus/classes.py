#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dirus Classes."""

import os
import logging
import logging.handlers
import subprocess
import tempfile
import threading
import time

import dirus

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


class Dirus(threading.Thread):

    """Dirus Class."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(dirus.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(dirus.LOG_LEVEL)
        _console_handler.setFormatter(dirus.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config
        self.direwolf_conf = None
        self.processes = {}
        self.daemon = True
        self._stop = threading.Event()

    def __del__(self):
        self.stop()

    def _write_direwolf_conf(self):
        
        tmp_fd, self.direwolf_conf = tempfile.mkstemp(
            prefix='dirus_', suffix='.conf')
        os.write(tmp_fd, "ADEVICE null null\n")
        os.close(tmp_fd)

    def run(self):
        # Configure / Run SDR
        # Allow use of 'rx_fm' for Soapy/HackRF
        rtl_path = self.config['rtl'].get('path', 'rtl_fm')

        frequency = "%sM" % self.config['rtl']['frequency']
        sample_rate = self.config['rtl'].get('sample_rate', dirus.SAMPLE_RATE)
        ppm = self.config['rtl'].get('ppm')
        gain = self.config['rtl'].get('gain')
        device_index = self.config['rtl'].get('device_index', '0')

        if bool(self.config['rtl'].get('offset_tuning')):
            enable_option = 'offset'
        else:
            enable_option = 'none'

        src_cmd = [rtl_path]
        src_cmd.extend(('-f', frequency))
        src_cmd.extend(('-s', sample_rate))
        src_cmd.extend(('-E', enable_option))
        src_cmd.extend(('-d', device_index))

        if ppm is not None:
            src_cmd.extend(('-p', ppm))

        if gain is not None:
            src_cmd.extend(('-g', gain))

        src_cmd.append('-')

        src_cmd = map(str, src_cmd)

        self._logger.debug('src_cmd="%s"', ' '.join(src_cmd))

        src_proc = subprocess.Popen(
            src_cmd,
            stdout=subprocess.PIPE
        )

        self.processes['src'] = src_proc

        ## Configure / Run Direwolf
        direwolf_path = self.config['direwolf'].get('command', 'direwolf')                
        direwolf_conf = self.config['direwolf'].get('conf')

        dw_cmd = [direwolf_path]
        # Configuration file name.
        if direwolf_conf is not None:
            dw_cmd.extend(('-c', direwolf_conf))
        else:
            self._write_direwolf_conf()
            dw_cmd.extend(('-c', self.direwolf_conf))
        
        # Text colors.  1=normal, 0=disabled.
        dw_cmd.extend(('-t', 0))
        # Number of audio channels, 1 or 2.
        dw_cmd.extend(('-n', 1))
        # Bits per audio sample, 8 or 16.
        dw_cmd.extend(('-b', 16))
        # Read from STDIN.
        dw_cmd.append('-')

        dw_cmd = map(str, dw_cmd)

        self._logger.debug('dw_cmd="%s"', ' '.join(dw_cmd))

        direwolf_proc = subprocess.Popen(
            dw_cmd,
            stdin=self.processes['src'].stdout,
            stdout=subprocess.PIPE
        )

        self.processes['direwolf'] = direwolf_proc

        while not self.stopped():
            time.sleep(0.01)

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        for name in ['direwolf', 'src']:
            try:
                proc = self.processes[name]
                proc.terminate()
            except Exception as ex:
                self._logger.exception(
                    'Raised Exception while trying to terminate %s: %s',
                    name, ex)
        self._stop.set()

    def stopped(self):
        """
        Checks if the thread is stopped.
        """
        return self._stop.isSet()
