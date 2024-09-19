# p1_reader for reading data from smart energy meters
# January 2024, Allard de Wit (ajwdewit@xs4all.nl)
#
# Results are written to a relational database and can be visualized by grafana
#
import time
import re
from math import trunc
import syslog
import serial
import sqlalchemy as sa

from . import config


def create_tables():
    """Creates output table on a relational DB system.

    returns a reference to the created or existing table
    """
    engine = sa.create_engine(config.dsn)
    meta = sa.MetaData(engine)
    tbl = sa.Table("p1_readouts", meta,
                   sa.Column("time", sa.Integer, primary_key=True),
                   sa.Column("net_afname", sa.Float),
                   sa.Column("net_injectie", sa.Float),
                   sa.Column("gas_meterstand", sa.Float),
                   )
    try:
        tbl.create()
    except sa.exc.OperationalError as e:
        tbl = sa.Table("p1_readouts", meta, autoload=True)

    return tbl


def write_to_db(net_afname, net_injectie, gas_meterstand):
    """Writes the energy usage (net_afname [kW]) and gas gauge state
    (gas_meterstand [m3]) to the DB table.
    """
    engine = sa.create_engine(config.dsn)
    meta = sa.MetaData(engine)
    tbl = sa.Table("p1_readouts", meta, autoload=True)
    i = tbl.insert().values(time=trunc(time.time()),
                            net_afname=net_afname,
                            net_inject=net_injectie,
                            gas_meterstand=gas_meterstand
                            )
    i.execute()


def parse_kilowatts(s):
    """Parses the current energy use from the P1 telegram (s)
    """

    r = re.split("[( *]", s)
    return float(r[1])


def parse_gas_m3(s):
    """Parses the current gas gauge state from the P1 telegram (s)
    """

    r = re.split("[( *]", s)
    return float(r[2])


def read_p1():
    """Reads information from the P1 port of the smart energy gauge.
    """
    # print(f"reading from TTY {time.time()}")
    net_afname = None
    net_injectie = None
    gas_meterstand = None
    with serial.Serial(config.USB_device, baudrate=115200) as ser:
        while True:
            s = ser.readline()
            s = s.decode()
            if s.startswith("1-0:1.7.0"):
                net_afname = parse_kilowatts(s)
            if s.startswith("1-0:2.7.0"):
                net_injectie = parse_kilowatts(s)
            if s.startswith("0-1:24.2.1"):
                gas_meterstand = parse_gas_m3(s)

            if None not in (net_afname, net_injectie, gas_meterstand):
                return net_afname, net_injectie, gas_meterstand


def main():
    create_tables()

    while True:
        try:
            net_af, net_in, gas_stand = read_p1()
            write_to_db(net_af, net_in, gas_stand)
        except Exception as e:
            msg = f"Failure getting data from P1 port {e}"
            print(msg)
            syslog.syslog(msg)

        time.sleep(config.sleep)


if __name__ == "__main__":
    main()
