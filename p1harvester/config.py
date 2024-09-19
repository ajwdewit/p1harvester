# USB device for p1 port
USB_device = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AR4XH8HI-if00-port0"

# SQLite database
dsn = f"mysql+pymysql://p1monitor:p1monitor@localhost/p1monitor"

# Number of seconds to sleep between readouts
sleep = 60