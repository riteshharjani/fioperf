from subprocess import Popen
from subprocess import PIPE
import os
from os import path
import sys
import argparse
import configparser
import errno
import time
import json
from fiodb import *

FIO_DEBUG = 1

buildconfig = ""

fiosql_db = ""
fiosql_column = ""

Threads = [1, 2, 4, 8, 12, 16, 24]
Bursts = ["4K", "1M"]

def pr_debug(args):
    if FIO_DEBUG:
        print("fioperf: " + args)


def fioperf_create_path(path):
    try:
        os.makedirs(path)
    except OSError as err:
        if (err.errno == errno.EEXIST and os.path.isdir(path)):
            pass
        else:
            raise

def run_cmd(cmd):
    pr_debug("running cmd '{}'".format(cmd))

    p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE,universal_newlines=True)
    p.wait()
    ret = p.returncode
    out, err = p.communicate()
    if (ret != 0):
        pr_debug("Command '{}' failed to run, stderr=\n{}, stdout=\n{}".format(cmd, err, out))
        sys.exit(1)
    pr_debug("Output-\n\t{}".format(out))
    return 0

def fio_calc_avg(filenames):
    read_avg = 0
    write_avg = 0
    cnt = 0
    for file in filenames:
        json_data = open(file)
        data = json.load(json_data)
        cnt += 1
        cnt_job = 0
        for job in data['jobs']:
            cnt_job += 1;
            read_avg += job['read']['bw']
            write_avg += job['write']['bw']
        assert(cnt_job == 1)
        json_data.close()
    read_avg = read_avg/cnt
    write_avg = write_avg/cnt
    print(cnt)
    return (read_avg, write_avg)

def fio_get_tablename(section, fiotest, bs):
    tablename = section + "_" + fiotest[:-4] + "_" + bs
    return tablename

def fio_run_test(fio_cmd, testname, fiosql_con, thread, section, fiotest, bs):
    global fiosql_column
    fio_outs = []
    for iter in range(1, 4):
        fio_out = "results/{}-{}.json".format(testname, iter)
        cmd = " --output={}".format(fio_out)
        run_cmd(fio_cmd + cmd)
        fio_outs.append(fio_out)
    for f in fio_outs:
        print(f)
    read_bw, write_bw = fio_calc_avg(fio_outs)
    print("Avg read_bw = {}, write_bw = {}".format(read_bw, write_bw))

    tablename = fio_get_tablename(section, fiotest, bs)
    sql_update_table(fiosql_con, tablename, fiosql_column + ("_read"), thread, read_bw)
    sql_update_table(fiosql_con, tablename, fiosql_column + ("_write"), thread, write_bw)


def fio_run_tests(section, config, test, fiosql_con):
    print("section name = {}".format(section))
    for bs in Bursts:
        for thread in Threads:
            tm = time.strftime('%d-%m-%Y-%H-%M-%S')
            testname = "{}-{}-{}-{}".format(test[:-4], bs, thread, tm)

            pr_debug("Running test: testname-bs-thread-time = {}".format(testname))
            fio_cmd = "fio --output-format=json"
            fio_cmd += " --directory {}".format(config.get(section, 'mountdir'))
            fio_cmd += " --numjobs={}".format(thread)
            fio_cmd += " --bs={}".format(bs)
            fio_cmd += " {}".format("tests/" + test)
            fio_run_test(fio_cmd, testname, fiosql_con, thread, section, test, bs)


def fio_setup_sql(fiosql_con, section, columnname, fiotests):
    for fiotest in fiotests:
        for bs in Bursts:
            tablename = fio_get_tablename(section, fiotest, bs)
            sql_create_table(fiosql_con, tablename)
            col_read = columnname + "_read"
            col_write = columnname + "_write"
            sql_add_column(fiosql_con, tablename, col_read)
            sql_add_column(fiosql_con, tablename, col_write)

def fio_mount(section, config):
    if (config.has_option(section, "mkfs")):
        run_cmd(config.get(section, "mkfs"))
    if (config.has_option(section, "mount")):
        run_cmd(config.get(section, "mount"))
    if (config.has_option(section, "chown")):
        run_cmd(config.get(section, "chown"))

def fio_umount(section, config):
    if (config.has_option(section, "mountdir")):
        run_cmd("sudo umount " + config.get(section, "mountdir"))

def fio_setup_env():
    global buildconfig
    global fiosql_db
    global fiosql_column
#    parser = argparse.ArgumentParser()
#    parser.add_argument('-c', '--config', type=str, default='default',
#                        help = "Config for fioperf")
#    args = parser.parse_args()
#    if not config.has_section(args.config):
#        pr_debug("No section '{}' in local.config".format(args.config))
#        sys.exit(1)

    config = configparser.ConfigParser()
    fdconfig = open('local.config')
    config.read_file(fdconfig)
    fdconfig.close()
    sections = config.sections()
    print(sections)

    if not (path.exists("tests/") and path.isdir("tests/")):
        pr_debug("No tests/ directory")
        sys.exit(1)

    fioperf_create_path("results/")

    fiotests = []
    for (dirpath, dirnames, filenames) in os.walk("tests/"):
        #pr_debug(dirpath, dirnames, filenames)
        fiotests.extend(filenames)

    for section in sections:
        if (section == "global"):
            if (not config.has_option(section, "BuildConfig") or
               (not config.has_option(section, "SqlDatabase"))):
                pr_debug("No BuildConfig/SqlDatabase specified\n")
                sys.exit(1)
            else:
                buildconfig = config.get(section, "BuildConfig")
                fiosql_column = buildconfig
                fiosql_db = config.get(section, "SqlDatabase")
                fiosql_con = sql_connect(fiosql_db)
            continue
        if not config.has_option(section, "mountdir"):
            pr_debug("No mountdir specified in section '{}'".format(section))
            sys.exit(1)
        fio_setup_sql(fiosql_con, section, fiosql_column, fiotests)

        fio_mount(section, config)
        print("columnname = {}".format(fiosql_column))
        for fiotest in fiotests:
            #print(test)
            fio_run_tests(section, config, fiotest, fiosql_con)
        fio_umount(section, config)


fio_setup_env()
