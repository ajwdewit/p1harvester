# P1harvester

Allard de Wit (ajwdewit@xs4all.nl), September 2024
Licensed under the EUPL-1.2-or-later

P1 harvester is a python package to read energy usage data from a smart meter and store it
in a database. It was developed on a Raspberry Pi using Debian Buster. However, this should
work on other linux-based systems and with some modifications probably on other systems 
as well.

It only reads and stores data, nothing else. Visualisation and computations should be done by
database views and tools like Grafana.

# Setting up p1harvester

For this short user guide we will assume that p1harvester will be installed on a Raspberry Pi
running Raspberry Pi OS. Also the database for storing data as well as grafana will be running
on the same Pi.

## Preparing the MySQL/MariaDB database

First of all the MySQL/MariaDB needs to be set up. The easiest thing is to create a
database named `p1harvester`. Next add a user `p1harvester` and assign a password. For
this guide we assume the password is also `p1harvester`. 
See [here](https://raspberrytips.com/install-mariadb-raspberry-pi/) for a guide to install MariaDB on the Pi.

You don't need to create any tables because p1harvester will create the output table `p1_readouts`
when it starts.

## Configuring P1 harvester

First download p1harvester from github as a zip file, or clone the repository with git. Next
move into the p1harvester package folder and load config.py in your text editor. This sets a
few configurations, notably the USB serial device where the P1 cable is plugged in, the data source 
name (dsn) for the database and the number of seconds to sleep between readings. An example is provided below.

```python
# USB device for p1 port
USB_device = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AR4XH8HI-if00-port0"

# SQLite database
dsn = f"mysql+pymysql://p1harvester:p1harvester@localhost/p1harvester"

# Number of seconds to sleep between readouts
sleep = 60
```

First, define the correct serial device. You can usually find the right serial device 
under `/dev/serial/by-id`:
```shell
~ $ ll /dev/serial/by-id/
total 0
lrwxrwxrwx 1 root root 13 Sep 13 17:17 usb-FTDI_FT232R_USB_UART_AR4XH8HI-if00-port0 -> ../../ttyUSB0
```

But if you have many serial devices this could be a trial and error exercise. 

Update the dsn string with your database credentials this has the form 
`mysql+pymysql://<username>:<password>@<hostname>/<dbname>`. See the SQLAlchemy documentation for more info 
on [DSN configuration](https://docs.sqlalchemy.org/en/20/core/engines.html)
Since p1harvester uses SQLAlchemy to connect
to the database, you could also use another database like postgres or even SQLite. However, you will need
to adapt the SQL views in that case as they may be MySQL specific.

Finally, you can choose how many seconds the p1harvester should sleep between readouts. I choose 60 seconds 
which works quite well in my case. If you set `sleep=0` you get a readout every few seconds which will fill up 
the tables space faster as it generates a lot more data.

## Installing p1harvester

As we will install p1harvester as a system service, we will make use of the system python3 installation. 
Usually, it is not advised to rely on the system python installation but since p1harvester is a very 
simple script this is not really an issue here.

First make sure that python3 and the pip installer for python3 are available on your system:

```shell
$ sudo apt install python3 python3-pip
Reading package lists... Done
Building dependency tree       
Reading state information... Done
python3 is already the newest version (3.7.3-1).
python3-pip is already the newest version (18.1-5+rpt1).
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
$ python3
Python 3.7.3 (default, Mar 23 2024, 16:12:05) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```
For my system on Raspbian 10 (Buster) this is already installed. The python version 3.7.3 is relatively
old but still sufficient for our purposes.

Next, change directory in a terminal window to the p1harvester folder and run the pip installer:
```shell
$ pwd
/home/allard/Sources/p1harvester
$ ls
LICENSE.txt  p1harvester  pyproject.toml  README.md  sql  systemd
$ pip3 install .
Processing /home/allard/Sources/p1harvester
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pyserial==3.5
  Downloading pyserial-3.5-py2.py3-none-any.whl (90 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 90.6/90.6 kB 5.0 MB/s eta 0:00:00
Collecting sqlalchemy<2.0
  Downloading SQLAlchemy-1.4.54-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.6/1.6 MB 11.6 MB/s eta 0:00:00
Collecting PyMySQL==1.1
  Using cached PyMySQL-1.1.0-py3-none-any.whl (44 kB)
Collecting greenlet!=0.4.17
  Downloading greenlet-3.1.1-cp310-cp310-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (599 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 599.5/599.5 kB 11.1 MB/s eta 0:00:00
Building wheels for collected packages: p1harvester
  Building wheel for p1harvester (pyproject.toml) ... done
  Created wheel for p1harvester: filename=p1harvester-2024.0.0-py3-none-any.whl size=10564 sha256=c979ad6358a21f6f0350c7e78708cc9d9336f9743dbfa28ef65ae00e01996f48
  Stored in directory: /tmp/pip-ephem-wheel-cache-o28jfmqh/wheels/90/cf/50/7390c0adb65eefe3e8e0c86b13e8c92b71007b88ceb09de363
Successfully built p1harvester
Installing collected packages: pyserial, PyMySQL, greenlet, sqlalchemy, p1harvester
Successfully installed PyMySQL-1.1.0 greenlet-3.1.1 p1harvester-2024.0.0 pyserial-3.5 sqlalchemy-1.4.54
```
You should now have a command `p1harvester` that can be used to start the system:
```shell
$ which p1harvester
/usr/local/bin/p1harvester
```

You have now successfully installed p1harvester.

# Setting up a systemd service

The most convenient way for running p1harvester is to set it up as a systemd service.
On most modern linux systems services are controlled by systemd. To install
p1harvester as a systemd service we need a so-called unit file. You can find a prepared
unit file in the `systemd` folder of the p1harvester repository. It looks like this:
```shell
[Unit]
Description=Starts p1 harvester for collecting energy/gas usage data
After=syslog.target

[Service]
Type=simple
Restart=always
User=pi
Group=pi
ExecStart=/usr/local/bin/p1harvester
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
```
The systemd service assumes that p1harvester is running on raspberry pi OS, as it runs as 
user `pi`.  The most important entry that may need to be updated is `ExecStart`. This points
to the p1harvester executable script which you can find with the command `which p1harvester`.

To install the service it is sufficient to copy the file `p1harvester.service` to the
correct systemd folder and make sure that the ownership and permissions are correct:
```shell
sudo cp p1harvester.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/p1harvester.service
sudo chmod 644 /etc/systemd/system/p1harvester.service
```

Moreover we need to tell systemd that a new service is added:
```shell
sudo systemctl daemon-reload
sudo systemctl enable p1harvester
sudo service p1harvester start
```

Systemd should now recognize it as a service:
```shell
systemctl list-unit-files | grep p1
p1harvester.service                       enabled        
```

If everything goes fine the p1harvester will now start reading data from the P1 port and push
it to MariaDB into the table `p1_readouts`.

If you want to know more about systemd services see [here](https://github.com/torfsen/python-systemd-tutorial).

# Installing some views in the database

The data stored in `p1_readouts` is already useful in its 
raw form. Time is stored as UNIX time, electricity use in kW and 
gas use is the current meter reading which is just increasing with the
gas usage. See the table below for an example of the raw output in 
`p1_readouts`. I do not have any solar panels installed so the 
column `net_injection` is always NULL.

```sql
MariaDB [p1harvester]> select * from p1_readouts limit 10;
+------------+---------+---------------+-------------------+
| time       | net_use | net_injection | gas_meter_reading |
+------------+---------+---------------+-------------------+
| 1704644559 |   0.326 |          NULL |           4911.44 |
| 1704644608 |   0.324 |          NULL |           4911.44 |
| 1704644675 |   0.324 |          NULL |           4911.44 |
| 1704644696 |   0.323 |          NULL |           4911.44 |
| 1704644757 |   0.324 |          NULL |           4911.47 |
| 1704644818 |   0.325 |          NULL |           4911.47 |
| 1704644879 |   0.318 |          NULL |           4911.47 |
| 1704644940 |   0.323 |          NULL |           4911.47 |
| 1704645001 |   0.324 |          NULL |           4911.47 |
| 1704645062 |   0.323 |          NULL |           4911.47 |
+------------+---------+---------------+-------------------+
10 rows in set (0.012 sec)
```

To turn in the data in something more convenient, there are two views defined in the 
folder `sql/` in the git repository. The `view_gas_usage_m3.sql` turns the data into
records with m$^3$ gas usage per time step, while the `view_net_usage_kWh.sql` turns the
data in p1_readouts into electricity usage per time step in kWh. Moreover, for aggregating
results, UNIX time is converted to timestamps and a day, month and year is added.

See below for sample outputs from the two views.

```sql
MariaDB [p1harvester]> select * from net_usage_kWh limit 5;
+---------------------+------------+-------+------+-----------------------+
| date_time           | day        | month | year | net_usage_kWh         |
+---------------------+------------+-------+------+-----------------------+
| 2024-01-07 17:22:39 | 2024-01-07 |     1 | 2024 |                  NULL |
| 2024-01-07 17:23:28 | 2024-01-07 |     1 | 2024 |  0.004410000012980602 |
| 2024-01-07 17:24:35 | 2024-01-07 |     1 | 2024 |  0.006030000017748987 |
| 2024-01-07 17:24:56 | 2024-01-07 |     1 | 2024 | 0.0018841667473316341 |
| 2024-01-07 17:25:57 | 2024-01-07 |     1 | 2024 |  0.005490000016159525 |
+---------------------+------------+-------+------+-----------------------+
5 rows in set (1.686 sec)

MariaDB [p1harvester]> select * from gas_usage_m3 limit 5;
+---------------------+------------+-------+------+---------------+
| date_time           | day        | month | year | gas_usage_m3  |
+---------------------+------------+-------+------+---------------+
| 2024-01-07 17:22:39 | 2024-01-07 |     1 | 2024 |          NULL |
| 2024-01-07 17:23:28 | 2024-01-07 |     1 | 2024 |             0 |
| 2024-01-07 17:24:35 | 2024-01-07 |     1 | 2024 |             0 |
| 2024-01-07 17:24:56 | 2024-01-07 |     1 | 2024 |             0 |
| 2024-01-07 17:25:57 | 2024-01-07 |     1 | 2024 | 0.02099609375 |
+---------------------+------------+-------+------+---------------+
5 rows in set (1.510 sec)
```

# Visualizing data collected from the P1 port

For visualizing data that we recorded from the P1 port, we will use Grafana.
Grafana is a tool for visualizing data, with a particular focus on time-series
data like we have in our case. Grafana can be easily installed on the raspberry Pi,
see [here](https://grafana.com/tutorials/install-grafana-on-raspberry-pi/).

Explaining how Grafana works is too much for this readme, but there are some
important issues to take into account:
- Grafana requires a data source, this is the link to the p1harvester database. 
  See the Grafana documentation on how to add a data source.
- For time-series plots, Grafana requires a column from the database that it
  can recognize as a time variable. This can be the time column in the `p1_readouts`
  table or the `date_time` column in the views.
- Aggregated results, such as the amount of gas used per month can be obtained
  by transforming the data in Grafana. For this you can add a 'transform' to
  the query that reads from the database.

![A dashboard created wth grafana showing the actual electricy/gas usage and the monthly totals.](grafana_example.png "Grafana dashboard")