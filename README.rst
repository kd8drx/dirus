Dirus - SDR to Direwolf Gateway Daemon
**************************************

Dirus is a daemon for managing an SDR to Direwolf gateway, the purpose of which
is to allow an SDR (e.g. RTL-SDR, HackRF, etc.) to present as a KISS device
to other software (e.g. APRS Decoders).

This can be accomplished with Direwolf alone, but Dirus provides an easy way
to configure, manage and daemonize this process.

Requirements
============

Dirus' requirements are relatively minimal. You'll need at least one FM decoder
tool, and Dire Wolf.

Either one of:

* @rxseger's rx_tools https://github.com/rxseger/rx_tools
Good for non-RTL-SDR devices, such as HackRF (tested with Dirus).

* @steve-m's librtlsdr http://sdr.osmocom.org/trac/wiki/rtl-sdr
Good for RTL-SDR devices.

Plus:

* @wb2osz's Dire Wolf https://github.com/wb2osz/direwolf

That's it! Install one FM Decoder, Dire Wolf, and Dirus and you're off to the races!

Configuration
=====
A sample dirus.json file is included in the repository, showing the options you can
configure across the two applications. Most defaults will work out-of-the-box, but
you may need to update a few:

**path**: Defines the full path to rtl_fm or rx_fm, and direwolf.
**frequency**: Update to ensure the SDR listens on the right APRS frequency for your region.
**ppm**: Adjusts for natural errors in most RTL chipsets. Run `rtl_test -p` for at least 10 minutes to determine the error rate for your particular unit.
**gain** _(Optional)_: Set the manual gain for your RTL in dB, or leave at 0 to set to automatic (recommended)
**device_index**: Allows you to run dirus with multiple SDR units attached. Use `rtl_test` to identify devices available and their index.
**sample_rate**: Determines the audio sample rate (in Hz) used between rtl_fm and direwolf. The default of 44100 is sufficient for 1200 baud AFSK.
**conf**: Point to the configuration file for Direwolf, or leave blank to use a very simple, basic config that depends on Direwolf's defaults.

Usage
=====

Your best bet is to use dirus with supervisor, or another daemon management tool:

::

    # /etc/supervisor.d/dirus.conf
    [program:dirus]
    command=dirus -c /etc/dirus.json
    process_name=%(program_name)s
    numprocs=1
    numprocs_start=0
    priority=999
    autostart=true
    autorestart=true
    startsecs=1
    startretries=3
    exitcodes=0,2
    stopsignal=TERM
    stopwaitsecs=10
    redirect_stderr=false
    stdout_logfile=AUTO
    stdout_logfile_maxbytes=50MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=0
    stdout_events_enabled=false
    stderr_logfile=AUTO
    stderr_logfile_maxbytes=50MB
    stderr_logfile_backups=10
    stderr_capture_maxbytes=0
    stderr_events_enabled=false
    serverurl=AUTO


Source
======
Github: https://github.com/ampledata/dirus

Building from Source
======
A simple `make` file is included in the source. To build, you only need the basic `python2.7-dev` and `libpython2.7-dev` packages installed.

As implied, Dirus uses Python 2, not Python 3.

Author
======
Greg Albrecht W2GMD <oss@undef.net>

Contributors
======
Will Davidson KD8DRX <will@kilodelta.com>

Copyright
=========
Copyright 2016 Orion Labs, Inc.

License
=======
Apache License, Version 2.0