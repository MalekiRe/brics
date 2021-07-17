# brics
mars-iss-bricks repo for SPOCS

## DO NOT MAKE A COMMIT WITHOUT GETTING A PULL REQUEST APPROVED BY AN ADMIN ##

All devlopment work should take place in the "dev" branch or another development branch. Code that should be moved into "master" should only be moved there through a pull request. Setup instructions are below.

Contact _lglik_ if you have any questions!

## RPI dev setup Instructions 

In a Terminal window on the Raspberry Pi:

```sudo apt-get update```

```sudo apt-get upgrade```

```cd /```

```sudo mkdir Code```

```cd Code```

```sudo git clone https://github.com/stanford-ssi/brics.git```

Enter your GitHub username and password when prompted.

```cd brics```

```git config --local user.name "Firstname Lastname"```

```git config --local user.email "username@myEmail.com"```

```git checkout dev```

## RPI flight setup Instructions

In a Terminal window on the Raspberry Pi:

```sudo apt-get update```

```sudo apt-get upgrade```

```cd /```

```sudo mkdir Code```

```cd Code```

```sudo git clone https://github.com/stanford-ssi/brics.git```

Enter your GitHub username and password when prompted.

```cd /```

```sudo nano /etc/rc.local```

Edit /etc/rc.local to match the following:

```
#!/bin/sh -e
# 
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.
# Print the IP address

_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

sudo python /Code/brics/main.py &

exit 0
```

```Cntl-X``` to save

```sudo shutdown```
