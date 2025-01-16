# USB device for p1 port
USB_device = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AR4XH8HI-if00-port0"

# P1 meter type, this can be either
# - the older type using the DSMR 2.2 protocol at 9600 baud -> use False
# - the new type using DSMR 4.0/4.2 at 115200 baud -> use True
# See also:
# - https://gist.github.com/tvdsluijs/14972f55f6b5efb92418ccb89ef73f5b
# - https://github.com/energietransitie/dsmr-info/blob/main/dsmr-p1-specs.csv
DSMR_new_protocol = False

# SQLite database
dsn = f"mysql+pymysql://p1harvester:p1harvester@localhost/p1harvester"

# Number of seconds to sleep between readouts
sleep = 60