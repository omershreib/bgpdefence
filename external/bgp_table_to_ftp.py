from config import CONFIG
from time import gmtime, strftime
from ftplib import FTP
from io import BytesIO
import paramiko
import time
import threading

"""
BGP Table to FTP

honestly, i did not wanted to create all this code, but i do not have a choose... /:
originally i wanted to use Cisco's EEM script from the localISP router (this is a cron-job of cisco's IOS)
but what i wanted to do (snapshot BGP table every 1 minute and upload to FTP server) does not supported by GNS3
which is really sucks.

more about EEM is in this link:
https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-xe-16/216091-best-practices-and-useful-scripts-for-ee.html 
"""


def upload_to_ftp(only_latest=True):
    """
    Upload BGP Table Snapshot to FTP Server

    steps:
        1. connect to localISP router
        2. run "show ip bgp" command and save the output as string
        3. convert output to bytesIO
        4. connect to FTP server
        5. upload bytesIO as "latest_bgp_table.txt"
        6 (optional) upload bytesIO as "bgp_table_<current_time>.txt"
    """
    local_isp_credentials = CONFIG['ftp_process']['local_isp']
    router_ip = local_isp_credentials['router_ip']
    router_user = local_isp_credentials['user']
    router_pass = local_isp_credentials['password']

    ftp_credentials = CONFIG['ftp_process']
    ftp_server_ip = ftp_credentials['server_ip']
    ftp_user = ftp_credentials['user']
    ftp_pass = ftp_credentials['password']

    print("connecting to localISP...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(router_ip, username=router_user, password=router_pass)

    print("connected to localISP")

    stdin, stdout, stderr = ssh.exec_command("show ip bgp")
    output = stdout.read().decode()
    ssh.close()

    print("close connection with localISP")

    bio = BytesIO(output.encode('utf-8'))

    print("connecting to FTP server...")

    ftp = FTP(ftp_server_ip)
    ftp.login(user=ftp_user, passwd=ftp_pass)

    print("connected to FTP server")

    current_datetime = strftime("%Y_%m_%d_%H_%M", gmtime())

    ftp_filename = ftp_credentials['filename']
    latest_filename = f"latest_{ftp_filename}"
    current_filename = f"{ftp_filename.replace(".txt", f"_{current_datetime}.txt")}"

    ftp.storbinary(f"STOR {latest_filename}", bio)

    if not only_latest:
        ftp.storbinary(f"STOR {current_filename}", bio)

    print("close connection with FTP server")

    ftp.quit()


def bgp_worker():
    """BGP Thread Worker for FTP uploading

    implement what the EEM script should do in real cisco IOS equipment
    """
    bgp_worker_sleep = CONFIG['ftp_process']['thread_worker_sleep_time']
    while True:
        try:
            print("Uploading to FTP...")
            upload_to_ftp(only_latest=False)
            print("Upload complete.")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(bgp_worker_sleep)


if __name__ == "__main__":
    # Start thread
    t = threading.Thread(target=bgp_worker, daemon=True)
    t.start()

    # Keep main program alive
    while True:
        time.sleep(1)
