from config import CONFIG
import paramiko
from ftplib import FTP
import os


# # === FTP server details ===
# FTP_SERVER = "203.0.113.1"
# FTP_USER = "ftpuser"
# FTP_PASS = "051295"
# #FTP_PASS = "vbnWgoEbHUzapEGD1KYP"
# FTP_FILENAME = "latest_bgp_table.txt"


def pull_bgp_table(filename):
    ftp_credentials = CONFIG['ftp_process']
    ftp_server_ip = ftp_credentials['server_ip']
    ftp_user = ftp_credentials['user']
    ftp_pass = ftp_credentials['password']
    ftp = FTP(ftp_server_ip)
    ftp.login(user=ftp_user, passwd=ftp_pass)

    print("pull latest BGP table snapshot...")
    filepath = CONFIG['utilites']['bgp_table']

    with open(filepath, "wb") as file:
        ftp.retrbinary(f"RETR {filename}", file.write)

    print("done!")

    ftp.quit()


if __name__ == "__main__":
    print("pull latest bgp table from FTP server...")
    pull_bgp_table('latest_bgp_table.txt')
    print("Done!")
