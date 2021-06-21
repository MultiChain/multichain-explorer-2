# -*- coding: utf-8 -*-

# MultiChain Explorer 2 (c) Coin Sciences Ltd
# All rights reserved under BSD 3-clause license

import os
import sys
import signal
import cfg
import readconf
import utils
import server

explorer_app = "MultiChain Explorer"
explorer_version = "2.0"


def main(argv):

    if len(argv) == 0:
        print ("""\nUsage: python3 explorer.py config-file.ini ( daemon | stop | status )

""" + explorer_app +""", version """ + explorer_app +"""

  config-file               Configuration file, see example.ini for examples.
  action                    Optional, one of the following:
      daemon                Start explorer as daemon
      stop                  Stop running explorer
      status                Get explorer status
""")
        return 0

    print (explorer_app + """, version """ + explorer_version + "\n")
    print ("")
    
    args=readconf.parse_argv(argv)
    if cfg.action is not None:
        if cfg.action == 'daemon':
            utils.become_daemon();
        
    if not readconf.read_conf(args):
        return 1;

    
    current_pid=utils.file_read(cfg.pid_file)
    if current_pid is not None:
        try:
            os.kill(int(current_pid), 0)
        except OSError:
            utils.remove_file(cfg.pid_file)
            current_pid=None
    
       
    if cfg.action is not None:
        if (cfg.action == 'stop') or (cfg.action == 'status'):
            if current_pid is None:
                print("Explorer is not running\n")
                return 0
            process_id=int(current_pid)
            print("Explorer found, PID " + str(process_id))
            if cfg.action == 'stop':
                utils.log_write("Stopping Explorer, PID: " + str(current_pid))
                print("Sending stop signal")
                try:
                    os.kill(int(current_pid),signal.SIGTERM)
                    utils.remove_file(cfg.pid_file)
                except OSError:
                    utils.log_write("Explorer already stopped")
                    utils.remove_file(cfg.pid_file)
            return 0

    if current_pid is not None:
        utils.print_error("Explorer for this configuration file is already running")
        return 1
    
    utils.file_write(cfg.pid_file,utils.get_pid())

    current_pid=utils.file_read(cfg.pid_file)
    utils.log_write("Explorer started, PID: " + str(current_pid))
    if not server.start():
        utils.remove_file(cfg.pid_file)
        return 1

    utils.remove_file(cfg.pid_file)
    utils.log_write("Explorer stopped")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
