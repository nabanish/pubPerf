# Performance Testing & Engineering - Open-source
## You need to have Java
  Firstly, on your RHEL machines, install java if not available already. Assuming you are root user:
  1. Update repo: `yum update`
  2. Install JDK: `yum install java-21-openjdk`
  3. Verify java version : `java -version`
  4. If the java version is not what was installed, use: `sudo update-alternatives --config 'java'`
  5. Select the correct java version from the list
  6. Verify again: `java -version`
## Installing JMeter in Linux(RHEL9)
On the RHEL machine that you will use as JMeter server, go to any directory of your choice. Here, the /opt directory will be used.
  1. Download the latest version of JMeter: `curl -O https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.6.3.tgz`
  2. Extract the tar: `tar -xvf apache-jmeter-5.6.3.tgz`
  3. Rename the extracted folder: `cp -r apache-jmeter-5.6.3 jmeter` and then remove the original folder: `rm -rf apache-jmeter-5.6.3`
  4. Get into jmeter folder and remove unnecessary folders or documents: cd jmeter and then: `rm -rf printable_docs/ docs/`
  5. Get into lib folder: `cd lib/` and download the latest cmd runner from maven: `curl -O https://repo1.maven.org/maven2/kg/apc/cmdrunner/2.3/cmdrunner-2.3.jar`
  6. Get into ext foleer: `cd ext/` and download the latest jmeter plugin manager: `curl -O https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/1.9/jmeter-plugins-manager-1.9.jar`
  7. For further steps, contact nabanishs@gmail.com or +91-9007084606
  8. Verify the version of jmeter: `jmeter --version`. You may use my fully automated script to do the same.
## Install and Setup Prometheus
1. Add system user group: `sudo groupadd --system prometheus` and `sudo useradd -s /sbin/nologin --system -g prometheus prometheus`
2. Create directory for Prometheus: `sudo mkdir /var/lib/prometheus`
3. For further steps, please contact nabanishs@gmail.com or +91-9007084606
4. You may alternatively use my shell script to do the installation.
## Install and Run Grafana
1.  Add Grafana to yum repository:
       ```
          cat <<EOF | sudo tee /etc/yum.repos.d/grafana.repo
          [grafana]
          name=grafana
          baseurl=https://packages.grafana.com/oss/rpm
          repo_gpgcheck=1
          enabled=1
          gpgcheck=1
          gpgkey=https://packages.grafana.com/gpg.key
          sslverify=1
          sslcacert=/etc/pki/tls/certs/ca-bundle.crt
          EOF
       ```
2.  For further steps, contact me on nabanishs@gmail.com or +91-9007084606
3.  Add Data-source as the prometheus already setup by providing the prometheus details: **http://server-ip:9090** and provide a name
4.  You may see the default metrics scraped by Prometheus for prometheus itself on the Metrics dashboard:
     
## Fully Automated Jenkins Job to deploy monitoring using Node-exporter-Prometheus-Grafana on multiple servers in the environment
1. This utilizes a one-time setup of Ansible and the Jenkins server mentioned in this ReadMe.
2. The ansible deploys the node-exporter, scrapping and the prometheus config update while Jenkins drives the automation using my self-written code with a single button-click.
3. For further details, contact nabanishs@gmail.com or +91-9007084606
   
## Monitoring Logstash with Prometheus-Grafana Stand-alone
1. Download logstash jmx exporter from https://github.com/kuskoman/logstash-exporter/releases. Refer to https://github.com/kuskoman/logstash-exporter/blob/master/README.md for more details.
2. For further steps, contact me on nabanishs@gmail.com or +91-9007084606
11. Import your prometheus in Grafana data-sources as outlined in previous section
12. Add dashboard in Grafana. You may add from Explore->Metrics or import an already created dashboard json file from git-hub:
    
	<img width="1702" alt="Logstash_Dashboard" src="https://github.com/user-attachments/assets/0f179d5a-fac1-485a-9d9e-ec931b5fb48d" />
 
## Monitoring Kafka with Prometheus
1.  Download Prometheus JMX Exporter: `wget https://repo.maven.apache.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar` or any latest version
2.  Move the exporter to kafka/libs: `sudo mv jmx_prometheus_javaagent-0.20.0.jar  /opt/kafka/libs/`
3.  For further steps, contact me on nabanishs@gmail.com or +91-9007084606
7.  Start zookeeper, if already not running, by: `./zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties` from /opt/kafka/bin
8.  Restart Kafka: `sudo systemctl daemon-reload` and start kafka service: `sudo systemctl restart kafka`
9.  Restart Prometheus: `sudo systemctl daemon-reload` and then start prometheus service: `sudo systemctl restart prometheus`
10. Verify kafka and prometheus status: `sudo systemctl status prometheus` and `sudo systemctl status kafka`
## Expose jmx metrics and monitor in jVisualVM or JConsole
To monitor any java application, the JMX metrics need to be exposed. For example, in case of Kafka, do the following:
1.  Contact me on nabanishs@gmail.com or +91-9007084606

## Monitoring Kafka-connect(source and sink connectors) with Prometheus
1. Use the same JMX Exporter as in the case of Kafka monitoring.
2. Place the exporter in `/opt/kafka/connect-distributed/` and .... Contact me on nabanishs@gmail.com or +91-9007084606 for further details.
   
## Install UI for Apache Kafka containerized in podman and monitoring Kafka
### Install podman on your machine
1.  `brew install podman` on Mac or RHEL: `dnf install container-tools` and then `dnf install container-tools`
2.  Contact me for further details on nabanishs@gmail.com or +91-9007084606
### Configure Kafka cluster to monitor and start using UI for Apache Kafka
1.  Run: `podman run -it -p 8080:8080 -e D
2.  For further steps, contact me on nabanishs@gmail.com or +91-9007084606
3.  Provide the default password 'changeit'
8.  Validate and if successful, Submit
UI will provide details about producers, consumers, brokers, message offsets, consumer lags etc.
<img width="1718" alt="UI for Apache Kafka" src="https://github.com/user-attachments/assets/fb974c00-5586-4491-9367-5f712e81cff3" />

## Integrate JMeter with Jenkins CI/CD pipeline
### Install and setup Jenkins
Make sure the latest open-jdk is installed on the jenkins server.
1.  Download Jenkins repo by running:
   ```
    sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
   ```
2.  For further steps, contact me on nabanishs@gmail.com or +91-9007084606
11. Set the username and password and Launch Jenkins
### Integrate JMeter with Jenkins
1.	After you install and setup Jenkins server, install the 'Performance' plugin using Manage Jenkins - Plugins.
2.	Contact me on nabanishs@gmail.com or +91-9007084606
	<img width="452" alt="image" src="https://github.com/user-attachments/assets/9d8460a0-289e-4aff-b65e-e083b97e1a92" />
4.	Check ‘This project is parameterized’ and add contact me on nabanishs@gmail.com or +91-9007084606 for further details
	<img width="452" alt="image" src="https://github.com/user-attachments/assets/dd007efd-1c24-42eb-9b78-5f83dcef324b" />
### What you get?
1. You may run the job with the parameters now supplied during run-time itself from Jenkins UI which is intuitive and any user may use it, without much scratching their heads

     <img width="452" alt="image" src="https://github.com/user-attachments/assets/6384787b-98ab-4d5d-a90c-c44a1b3658bf" />
2. Check the Performance Report once the result is parsed and created by Performance Plugin. A sample result looks like this:

     <img width="452" alt="image" src="https://github.com/user-attachments/assets/9ac64c5e-341f-4d76-b1d4-7c3d25e809fa" />
3. You also have the option to view Trend Results at one glance and therefore comparative analysis is already taken care of without using excels:

     <img width="452" alt="image" src="https://github.com/user-attachments/assets/63c73838-d084-4cad-ab86-c0f0c762af2b" />
4. You can also filter the trend results according to your needs, for e.g. view the trend for the last n builds or of a particular build, without searching all over:

     <img width="452" alt="image" src="https://github.com/user-attachments/assets/866f289b-6a67-4837-9d33-c9726bfaf843" />










