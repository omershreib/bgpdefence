import paramiko
from ftplib import FTP
import os

# === FTP server details ===
FTP_SERVER = "203.0.113.1"
FTP_USER = "ftpuser"
FTP_PASS = "vbnWgoEbHUzapEGD1KYP"
FTP_FILENAME = "bgp_table.txt"


def pull_ip_route_from_ftp(filename):
    ftp = FTP(FTP_SERVER)
    ftp.login(user=FTP_USER, passwd=FTP_PASS)

    with open(filename, "wb") as file:
        # Command for Downloading the file "RETR filename"
        ftp.retrbinary(f"RETR {filename}", file.write)

    ftp.quit()


if __name__ == "__main__":
    print("pull latest ip route BGP table from FTP server...")
    pull_ip_route_from_ftp('ip_route_bgp.txt')
    print("Done!")
