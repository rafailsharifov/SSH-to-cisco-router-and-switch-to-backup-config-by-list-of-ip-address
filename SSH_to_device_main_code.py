import paramiko
import time
import getpass
import tkinter as tk
from tkinter import filedialog
import os
import re


print("  _______          //\\       _________        __")
print(" ||      ||       //  \\      ||            //    \\\\")
print(" ||      ||      //    \\     ||           //      \\\\")
print(" ||------||     //------\\    ||-----     ||        ||")
print(" ||    \\\\      //        \\   ||           \\\\      //")
print(" ||     \\\\    //          \\  ||            \\\\ __ //")
#Ask for file select
try:
    print("Input your file that contains ip list of devices")
    time.sleep(0.1)
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
except Exception as error:
    print(error)
    input("Press 'Enter' to quit execute")
    raise

#Read file
try:
    file = open(file_path, "r")
except Exception as error:
    print(error)
    input("Press 'Enter' to quit execute")
    raise
#Path
path = os.path.split(file_path)[0]

#Ask for username&password
try:
    username = input("Input your username:").strip()
    password = getpass.getpass()
    enable_password = getpass.getpass("Enable password:(Optional)")
except Exception as error:
    print(error)
    input("Press 'Enter' to quit execute")
    raise


try:
    for line in file:
        print("Connecting:", line.strip(), "...")
        ip_address = line.strip()
        try:
            #SSH to Client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=ip_address, username=username,password=password)
            print("Successful connection to: ", ip_address)
            remote_connection = ssh_client.invoke_shell()
        except Exception as error:
            print(error)
            continue

        try:
            #Find device name
            for_devicename = remote_connection.recv(65535)

            #Enable password
            remote_connection.send("enable\n")
            time.sleep(1)
            output1 = remote_connection.recv(65535)

            if "Password" in str(output1):
                remote_connection.send(enable_password + "\n")
                print("Enable password entered")
            else:
                pass
        except Exception as error:
            print(error)
            continue

        try:
            #Push config
            remote_connection.send("terminal length 0\n")
            remote_connection.send("sh run\n")
            time.sleep(5)
            #copy running-config to startup-config
            remote_connection.send("wr\n")
            time.sleep(3)
            print("Copied running-config to startup-config")
            output = remote_connection.recv(65535)
            ssh_client.close
        except Exception as error:
            print(error)
            continue
        try:
            #Find device name
            device_name = for_devicename.decode('ascii')
            splited_name = device_name.split()[-1]
            name = re.split('[# >]', splited_name)[0]
            name= os.path.join(path, name+".txt")
            print("Config file saved to:", name)
            text_file =open(name, "w")
            text_file.write(output.decode("ascii"))
            text_file.close()
        except Exception as error:
            print(error)
            continue

except Exception as error:
    print(error)
    input("Press 'Enter' to quit execute")
    raise

file.close()

input("Press 'Enter' to quit execute")
