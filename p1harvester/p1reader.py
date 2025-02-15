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


def get_serial_config():
    """Returns the configuration for the serial port

    :return: a dict with pyserial settings
    """

    serial_config = dict(
        xonxoff = 0,
        rtscts = 0,
        timeout = 12,
        port = config.USB_device
    )
    if not config.DSMR_new_protocol:
        d = dict(
            # DSMR 2.2 > 9600 7E1:
            baudrate = 9600,
            bytesize = serial.SEVENBITS,
            parity = serial.PARITY_EVEN,
            stopbits = serial.STOPBITS_ONE,
        )
    else:
        d = dict(
            # DSMR 4.0/4.2 > 115200 8N1:
            baudrate = 115200,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
        )
    serial_config.update(d)

    return serial_config


def create_tables():
    """Creates output table on a relational DB system.

    returns a reference to the created or existing table
    """
    engine = sa.create_engine(config.dsn)
    meta = sa.MetaData(engine)
    tbl = sa.Table("p1_readouts", meta,
                   sa.Column("time", sa.Integer, primary_key=True),
                   sa.Column("net_use", sa.Float),
                   sa.Column("net_injection", sa.Float),
                   sa.Column("gas_meter_reading", sa.Float),
                   )
    try:
        tbl.create()
    except sa.exc.OperationalError as e:
        tbl = sa.Table("p1_readouts", meta, autoload=True)

    return tbl


def write_to_db(rec):
    """Writes the energy usage to the DB table.

    :param rec: the record holding energy usage data from P1
    """

    engine = sa.create_engine(config.dsn)
    meta = sa.MetaData(engine)
    tbl = sa.Table("p1_readouts", meta, autoload=True)
    i = tbl.insert().values(**rec)
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
    serial_config = get_serial_config()
    with serial.Serial(**serial_config) as ser:
        while True:
            s = ser.readline()
            s = s.decode('ascii')
            if s.startswith("1-0:1.7.0"):
                net_afname = parse_kilowatts(s)
            if s.startswith("1-0:2.7.0"):
                net_injectie = parse_kilowatts(s)
            if s.startswith("0-1:24.2.1"):
                gas_meterstand = parse_gas_m3(s)

            if None not in (net_afname, net_injectie, gas_meterstand):
                rec = dict(time=trunc(time.time()),
                            net_use=net_afname,
                            net_injection=net_injectie,
                            gas_meter_reading=gas_meterstand
                            )
                return rec


def main():
    create_tables()

    while True:
        try:
            rec = read_p1()
            write_to_db(rec)
        except Exception as e:
            msg = f"Failure getting data from P1 port {e}"
            print(msg)
            syslog.syslog(msg)

        time.sleep(config.sleep)


if __name__ == "__main__":
    main()
