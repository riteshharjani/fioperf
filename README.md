# fioperf
Fio based filesystem performance utility

## fioperf:	Fio based filesystem :open_file_folder: performance tool
##### Author:	Ritesh Harjani <ritesh.harjani@gmail.com>

[![About me](https://img.shields.io/badge/author-riteshh-brightgreen.svg)](https://github.com/riteshharjani)
[![TODO](https://img.shields.io/badge/development-TODO-lightgrey.svg)](#todo-)

==========================================

### Description:
fioperf is a simple fio based filesystem performance testing tool.
Main purpose for this is to test different filesystem mount options for
increasing number of threads. It also takes care by running each test 3 times
and updates the average read + write bandwidth in the sqlite table.

We use this sqlite3 table to then plot the bw graph to test for any scalability problems
w.r.t. filesystem mount options/patches.

It is still under development, so stay tuned.

### TODO:-
1. Implement small script to provide gnuplot based on sql tables.

### Requirements:-
```
pip3 install json
pip3 install configparser
pip3 install argparse
pip3 install sqlite3
```
### [local.config]:
```
[global]
BuildConfig=ilock
SqlDatabase=fio_dioread_db.db

[dioread_nolock]					// Note don't use '-' in names. Sqlite3 gives error in creating column with that name
mkfs=mkfs.ext4 -F -b 4096 testfs
mount=mount -t ext4 -o loop,dioread_nolock testfs ./mountdir/
mountdir=./mountdir/

[dioread_lock]
mkfs=mkfs.ext4 -F testfs
mount=mount -t ext4 -o loop testfs ./mountdir/
mountdir=./mountdir/
```

### [Sample output database]:
```
riteshh-> sqlite3 fio_dioread_db.db
SQLite version 3.26.0 2018-12-01 12:34:55
Enter ".help" for usage hints.
sqlite> .headers on
sqlite> .mode column
sqlite> SELECT * from dioread_
dioread_lock_dio_randrw_1M    dioread_lock_dio_rw_1M        dioread_nolock_dio_randrw_1M  dioread_nolock_dio_rw_1M
dioread_lock_dio_randrw_4K    dioread_lock_dio_rw_4K        dioread_nolock_dio_randrw_4K  dioread_nolock_dio_rw_4K
sqlite> SELECT * from dioread_nolock_dio_randrw_1M
   ...> ;
threads     ilock_read  ilock_write
----------  ----------  -----------
1           646981.0    431321.0
2           357184.0    535776.0
4           803832.0    1087537.0
8           789727.0    1068454.0
12          780067.0    1055385.0
16          944303.0    1310750.0
24          699710.0    869733.0
sqlite> SELECT * from dioread_nolock_dio_randrw_4K
   ...> ;
threads     ilock_read  ilock_write
----------  ----------  -----------
1           113075.0    116300.0
2           147392.0    153744.0
4           144729.0    150671.0
8           170660.0    175185.0
12          178191.0    180034.0
16          187429.0    188052.0
24          183832.0    183808.0
sqlite> .quit
```
### Contribution:-
1. In case if anyone would like to contribute to this project - please feel free to submit a pull request.
