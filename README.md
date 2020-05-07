# RYU Load Balancer Controller
OpenFlow SDN Load Balancer using the RYU controller

Git repo at https://github.com/hakasapl/ryu_load_balancer

### Software Requirements
* OpenvSwitch version 2.9.5
* RYU version 4.15
* Mininet version 2.3.0d6
* Ubuntu 18.04.4 LTS

### Setup Environment
1. Install all above software requirements.
1. Run `ryu-manager load_balancer.py` to start the controller.
1. Run `sudo ./lb_start.py` to start mininet and create the bridges. When you `exit` mininet, the bridges will be deleted automatically.
1. `h1`, `h2`, `h3`, are load balancer slaves, and `c1` is the client. Connect to load balancer using `nc 128.128.129.1 6666` after all three hosts are listening on `6666`. ie. `nc -l -k 6666`

### Additional Info
* The `simple_switch.py` is a controller that comes with RYU. I slightly modified it to prevent it from adding flows so that my control test wouldn't be much faster than my load balancer test, since load balancer packets always go through the controller. Use `sudo ./sw_start.py` to create the control test environment.
* All data obtained in CSV format is in the `data_output` folder.
