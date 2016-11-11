#!/usr/bin/env python

import sys
import random
from parse_arguments import parse_arguments
from os import path
from pantheon_help import check_call
import json


def create_metadata_file(args, metadata_fname):
    metadata = dict()
    metadata['runtime'] = args.runtime
    metadata['flows'] = args.flows
    metadata['interval'] = args.interval
    metadata['sender_side'] = args.sender_side
    metadata['run_times'] = args.run_times

    if args.local_info:
        metadata['local_information'] = args.local_info

    if args.remote_info:
        metadata['remote_information'] = args.remote_info

    if args.local_if:
        metadata['local_interface'] = args.local_if

    if args.remote_if:
        metadata['remote_interface'] = args.remote_if

    if args.local_addr:
        metadata['local_address'] = args.local_addr

    if args.remote:
        remote_addr = args.remote.split(':')[0].split('@')[1]
        metadata['remote_address'] = remote_addr

    metadata_file = open(metadata_fname, 'w')
    metadata_file.write(json.dumps(metadata))
    metadata_file.close()


def main():
    # arguments and source files location setup
    args = parse_arguments(path.basename(__file__))

    test_dir = path.abspath(path.dirname(__file__))
    pre_setup_src = path.join(test_dir, 'pre_setup.py')
    setup_src = path.join(test_dir, 'setup.py')
    test_src = path.join(test_dir, 'test.py')
    summary_plot_src = path.join(test_dir, 'summary_plot.py')
    combine_report_src = path.join(test_dir, 'combine_reports.py')
    metadata_fname = path.join(test_dir, 'pantheon_metadata')

    # test congestion control schemes
    pre_setup_cmd = ['python', pre_setup_src]
    setup_cmd = ['python', setup_src]
    test_cmd = ['python', test_src]

    if args.remote:
        pre_setup_cmd += ['-r', args.remote]
        setup_cmd += ['-r', args.remote]
        test_cmd += ['-r', args.remote]

    test_cmd += [
        '-t', str(args.runtime), '-f', str(args.flows),
        '--interval', str(args.interval), '--tunnel-server', args.server_side]

    if args.local_addr:
        test_cmd += ['--local-addr', args.local_addr]

    test_cmd += ['--sender-side', args.sender_side]

    if args.local_if:
        pre_setup_cmd += ['--local-interface', args.local_if]
        test_cmd += ['--local-interface', args.local_if]

    if args.remote_if:
        pre_setup_cmd += ['--remote-interface', args.remote_if]
        test_cmd += ['--remote-interface', args.remote_if]

    run_setup = True
    run_test = True
    if args.run_only == 'setup':
        run_test = False
    elif args.run_only == 'test':
        run_setup = False

    cc_schemes = ['default_tcp', 'vegas', 'koho_cc', 'ledbat', 'pcc', 'verus',
                  'scream', 'sprout', 'webrtc', 'quic']

    if args.random_order:
        random.shuffle(cc_schemes)

    # setup and run each congestion control
    if run_setup:
        check_call(pre_setup_cmd)
        for cc in cc_schemes:
            cmd = setup_cmd + [cc]
            check_call(cmd)

    if run_test:
        # create metadata file to be used by combine_reports.py
        create_metadata_file(args, metadata_fname)
        return

        for run_id in xrange(1, 1 + args.run_times):
            for cc in cc_schemes:
                cmd = test_cmd + ['--run-id', str(run_id), cc]
                check_call(cmd)

        cmd = ['python', summary_plot_src, '--run-times',
               str(args.run_times)] + cc_schemes
        check_call(cmd)

        cmd = ['python', combine_report_src, '--metadata-file', metadata_fname,
               '--run-times', str(args.run_times)] + cc_schemes
        check_call(cmd)


if __name__ == '__main__':
    main()
