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
  7. Get back to the lib folder: cd .. and then start the installation of the jmeter plugins:
     ```
     java  -jar cmdrunner-2.3.jar --tool org.jmeterplugins.repository.PluginManagerCMD install-all-except jpgc-hadoop,jpgc-oauth,ulp-jmeter-autocorrelator-plugin,ulp-jmeter-videostreaming-plugin,ulp-jmeter-gwt-plugin,tilln-iso8583
     ```
  8. Go to the ~ directory: cd ~ and then open the .bashrc file using vi: vi .bashrc
  9. Add the path to JMeter and save the file:
      ```
        JMETER_HOME="/opt/jmeter"
        PATH="$JMETER_HOME/bin:$PATH"
        export PATH
      ```
  10. Source the file: `source ~/.bashrc`
  11.Go to bin folder of jmeter: `cd /opt/jmeter/bin` and change the heap, non-heap memory of jmeter as : `"${HEAP:="-Xms2g -Xmx2g -XX:MaxMetaspaceSize=512m"}"`
  12. Verify the version of jmeter: `jmeter --version`
## Install and Setup Prometheus
1. Add system user group: `sudo groupadd --system prometheus` and `sudo useradd -s /sbin/nologin --system -g prometheus prometheus`
2. Create directory for Prometheus: `sudo mkdir /var/lib/prometheus`
3. Create configuration directories for Prometheus:
 ```
   for i in rules rules.d files_sd; do
   sudo mkdir -p /etc/prometheus/${i};
   done
```
4. Go to the directory where you want Prometheus to reside: cd /opt and Download the latest version of Prometheus by running:  
  ```
  curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest \
  | grep browser_download_url \
  | grep linux-amd64 \
  | cut -d '"' -f 4 \
  | wget -qi -
  ```
5. Extract the file and place in the $PATH directory:
 ```
   tar xvf prometheus-*.tar.gz
   cd prometheus-*/
   sudo cp prometheus promtool /usr/local/bin/
 ```
6. If console and console_libraries are present, then copy them too: ```sudo cp -r prometheus.yml consoles/ console_libraries/ /etc/prometheus/```
7. Create a systemd service file for Prometheus: `sudo vi /etc/systemd/system/prometheus.service` and add the below contents:
   ```
    [Unit]
      Description=Prometheus
      Documentation=https://prometheus.io/docs/introduction/overview/
      Wants=network-online.target
      After=network-online.target
      
      [Service]
      Type=simple
      User=prometheus
      Group=prometheus
      ExecReload=/bin/kill -HUP $MAINPID
      ExecStart=/usr/local/bin/prometheus \
        --config.file=/etc/prometheus/prometheus.yml \
        --storage.tsdb.path=/var/lib/prometheus \
        --web.console.templates=/etc/prometheus/consoles \
        --web.console.libraries=/etc/prometheus/console_libraries \
        --web.listen-address=0.0.0.0:9090 \
        --web.external-url=
      
      SyslogIdentifier=prometheus
      Restart=always
      
      [Install]
      WantedBy=multi-user.target
     ```
8. Set correct directoy permissions:
      ```
         sudo chown -R prometheus:prometheus /etc/prometheus
         sudo chmod -R 775 /etc/prometheus/
         sudo chown -R prometheus:prometheus /var/lib/prometheus/
      ```
9. Reload the daemon:`sudo systemctl daemon-reload` and then start Prometheus service: `sudo systemctl start prometheus`
10. Verify the service to be running: `systemctl status prometheus`
11. Enable the service at start-up: `sudo systemctl enable prometheus`
12. Disable firewalld as required. You may use selective:
       ```
         sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" \
         source address="192.168.122.0/24" \
         port protocol="tcp" port="9090" accept'
         sudo firewall-cmd --reload
       ```
       OR allow all IPs
    ```
         sudo firewall-cmd --add-port=9090/tcp --permanent
         sudo firewall-cmd --reload
    ```
13. Open Prometheus UI using a browser by launching: **http://server-ip:9090**
    <img width="1723" alt="Prometheus_DefaultQueries" src="https://github.com/user-attachments/assets/8b538179-3b01-4d05-bf08-409d291db2db" />

14. You may alternatively use this shell script to do the installation, change the version as required: https://github.com/nabanish/Performance/blob/main/InstallPrometheus.sh
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
2.  Insall Grafana : `sudo dnf -y install grafana`
3.  Verify package info: `rpm -qi grafana`
4.  Start Grafana service: `sudo systemctl enable --now grafana-server.service`
5.  Verify the Grafana service status: `systemctl status grafana-server.service`
6.  Launch **http://server-ip:3000** to open Grafana UI
7.  Default credentials are admin/admin. Change the password on first login
8.  Add Data-source as the prometheus already setup by providing the prometheus details: **http://server-ip:9090** and provide a name
9.  You may see the default metrics scraped by Prometheus for prometheus itself on the Metrics dashboard:
     <img width="1723" alt="Grafana_Default_DashboardforPrometheus" src="https://github.com/user-attachments/assets/2d526502-1cd3-4211-9ffd-cb7133892584" />

## Monitoring Logstash with Prometheus-Grafana Stand-alone
1. Download logstash jmx exporter from https://github.com/kuskoman/logstash-exporter/releases. Refer to https://github.com/kuskoman/logstash-exporter/blob/master/README.md for more details.
2. Install golang:
    1. Update the repo: `sudo dnf update`
    2. Download the go tar: `wget https://go.dev/dl/go1.23.6.linux-amd64.tar.gz` or any latest build
    3. Copy in required directory: `sudo tar -C /usr/local -xzf go1.23.6.linux-amd64.tar.gz`
    4. Add the following in .bashrc:
       ```
         export PATH=$PATH:/usr/local/go/bin
         export GOPATH=$HOME/go
         export PATH=$PATH:$GOPATH/bin
       ```
3. Source ~/.bashrc and then check go version: `go version`  	
4. Change the prometheus.yml file to read logstash exporter metrics by vi /etc/prometheus/prometheus.yml with
     ``` 
      - job_name: 'logstash'
        static_configs:
          - targets: ["localhost:9198"]
      ```
5. Create a systemd service by vi /etc/systemd/system/logstashexport.service
   ```
      [Unit]
      Description=Logstash Exporter for Prometheus
      After=network.target
      [Service]
      User=root
      Group=root
      ExecStart=/var/logstash-exporter-linux
      Type=simple
      [Install]
      WantedBy=multi-user.target
   ```
 6. Reload daemon: `sudo systemctl daemon-reload` and then start the service: `systemctl start logstashexport.service`
 7. Verify the service running by: `systemctl status logstashexport.service` and then **curl http://localhost:9198/metrics**
 8. Enable the service on boot: `sudo systemctl enable logstashexport.service`
 9. Verify the metrics using **http://server-name:9198/metrics** from a local browser
 10. Restart prometheus to start reading the metrics
     ```
       sudo systemctl daemon-reload
       systemctl stop prometheus
       systemctl start prometheus
       systemctl status prometheus
     ```
11. Import your prometheus in Grafana data-sources as outlined in previous section
12. Add dashboard in Grafana. You may add from Explore->Metrics or import an already created dashboard json file from git-hub:
    
	<img width="1702" alt="Logstash_Dashboard" src="https://github.com/user-attachments/assets/0f179d5a-fac1-485a-9d9e-ec931b5fb48d" />
 
## Monitoring Kafka with Prometheus
1.  Download Prometheus JMX Exporter: `wget https://repo.maven.apache.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar` or any latest version
2.  Move the exporter to kafka/libs: `sudo mv jmx_prometheus_javaagent-0.20.0.jar  /opt/kafka/libs/`
3.  Configure Kafka to use the exporter by adding the below lines: `vi /opt/kafka/bin/kafka-server-start.sh`
    >KAFKA_OPTS="-javaagent:/opt/kafka/libs/jmx_prometheus_javaagent-0.20.0.jar=9091:/etc/prometheus/prometheus.yml"
    >KAFKA_OPTS="-javaagent:/opt/kafka/libs/jmx_prometheus_javaagent-0.20.0.jar=9091:/opt/kafka/config/sample_jmx_exporter.yml"
4.  Configure the JMX Exporter: Either use the below json by expanding details or use https://github.com/prometheus/jmx_exporter/blob/main/examples/kafka-2_0_0.yml
    >cd /opt/kafka/config
    >vi sample_jmx_exporter.yml
<details>
     lowercaseOutputName: true

rules:
- pattern : kafka.server<type=(.+), name=(.+), clientId=(.+), topic=(.+), partition=(.*)><>Value
  name: kafka_server_$1_$2
  type: GAUGE
  labels:
    clientId: "$3"
    topic: "$4"
    partition: "$5"
- pattern : kafka.server<type=(.+), name=(.+), clientId=(.+), brokerHost=(.+), brokerPort=(.+)><>Value
  name: kafka_server_$1_$2
  type: GAUGE
  labels:
    clientId: "$3"
    broker: "$4:$5"
- pattern : kafka.coordinator.(\w+)<type=(.+), name=(.+)><>Value
  name: kafka_coordinator_$1_$2_$3
  type: GAUGE
- pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*, (.+)=(.+), (.+)=(.+)><>Count
  name: kafka_$1_$2_$3_total
  type: COUNTER
  labels:
    "$4": "$5"
    "$6": "$7"
- pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*, (.+)=(.+)><>Count
  name: kafka_$1_$2_$3_total
  type: COUNTER
  labels:
    "$4": "$5"
- pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*><>Count
  name: kafka_$1_$2_$3_total
  type: COUNTER

- pattern: kafka.server<type=(.+), client-id=(.+)><>([a-z-]+)
  name: kafka_server_quota_$3
  type: GAUGE
  labels:
    resource: "$1"
    clientId: "$2"

- pattern: kafka.server<type=(.+), user=(.+), client-id=(.+)><>([a-z-]+)
  name: kafka_server_quota_$4
  type: GAUGE
  labels:
    resource: "$1"
    user: "$2"
    clientId: "$3"
- pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+), (.+)=(.+)><>Value
  name: kafka_$1_$2_$3
  type: GAUGE
  labels:
    "$4": "$5"
    "$6": "$7"
- pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+)><>Value
  name: kafka_$1_$2_$3
  type: GAUGE
  labels:
    "$4": "$5"
- pattern: kafka.(\w+)<type=(.+), name=(.+)><>Value
  name: kafka_$1_$2_$3
  type: GAUGE
- pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+), (.+)=(.+)><>Count
  name: kafka_$1_$2_$3_count
  type: COUNTER
  labels:
    "$4": "$5"
    "$6": "$7"
- pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.*), (.+)=(.+)><>(\d+)thPercentile
  name: kafka_$1_$2_$3
  type: GAUGE
  labels:
    "$4": "$5"
    "$6": "$7"
    quantile: "0.$8"
- pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+)><>Count
  name: kafka_$1_$2_$3_count
  type: COUNTER
  labels:
    "$4": "$5"
- pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.*)><>(\d+)thPercentile
  name: kafka_$1_$2_$3
  type: GAUGE
  labels:
    "$4": "$5"
    quantile: "0.$6"
- pattern: kafka.(\w+)<type=(.+), name=(.+)><>Count
  name: kafka_$1_$2_$3_count
  type: COUNTER
- pattern: kafka.(\w+)<type=(.+), name=(.+)><>(\d+)thPercentile
  name: kafka_$1_$2_$3
  type: GAUGE
  labels:
    quantile: "0.$4"
  </details>
5.  Edit the prometheus.yml to include Kafka data: `vi /etc/prometheus/prometheus.yml`
    <img width="804" alt="prometheus_kafka_yml" src="https://github.com/user-attachments/assets/3f42165a-6e51-465a-bd61-1657ecf4e84e" />
6. Update Kafka systemd unit file: `vi /etc/systemd/system/kafka.service`
   ```
      [Service]
      Type=simple
      Environment="JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64"
      Environment="KAFKA_OPTS=-javaagent:/opt/kafka/libs/jmx_prometheus_javaagent-0.20.0.jar=9091:/etc/prometheus/prometheus.yml"
      Environment="KAFKA_OPTS=-javaagent:/opt/kafka/libs/jmx_prometheus_javaagent-0.20.0.jar=9091:/opt/kafka/config/sample_jmx_exporter.yml"
      ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
      ExecStop=/opt/kafka/bin/kafka-server-stop.sh
      Restart=on-failure

      [Install]
      WantedBy=multi-user.target
   ```
7.  Start zookeeper, if already not running, by: `./zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties` from /opt/kafka/bin
8.  Restart Kafka: `sudo systemctl daemon-reload` and start kafka service: `sudo systemctl restart kafka`
9.  Restart Prometheus: `sudo systemctl daemon-reload` and then start prometheus service: `sudo systemctl restart prometheus`
10. Verify kafka and prometheus status: `sudo systemctl status prometheus` and `sudo systemctl status kafka`
## Expose jmx metrics and monitor in jVisualVM or JConsole
To monitor any java application, the JMX metrics need to be exposed. For example, in case of Kafka, do the following:
1.  Modify the kafka-run-class.sh to have JMX_PORT="nnnn". Pass this JMX_PORT variable to
    >KAFKA_JMX_OPTS: -Dcom.sun.management.jmxremote.port=$JMX_PORT -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false  -Dcom.sun.management.jmxremote.ssl=false
3.  Restart kafka service
4.  Open terminal and open jconsole
5.  In the Remote process, use the kafka server-ip and the JMX_PORT value and connect insecuredly.
    ![jconsole jvm monitoring](https://github.com/user-attachments/assets/bfab5f22-aff0-4eb4-b295-78b9ac89eaf5)
    ![VisualVM](https://github.com/user-attachments/assets/6eaab478-dd8a-4bf8-b4eb-8b57f2daca92)

## Install UI for Apache Kafka containerized in podman and monitoring Kafka
### Install podman on your machine
1.  brew install podman
2.  Verfify podman insallation by: podman --version (prefer >4.0)
3.  Start podman by: podman machine init  --now and then: podman machine start
### Configure Kafka cluster to monitor and start using UI for Apache Kafka
1.  Run: podman run -it -p 8080:8080 -e DYNAMIC_CONFIG_ENABLED=true provectuslabs/kafka-ui
2.  Launch UI for Apache kafka by loading: localhost:8080
3.  On any one of the Kafka brokers of your cluster, put in this sslconfit.txt file in /opt/kafka/bin
    ```
       security.protocol=SSL
       ssl.keystore.location=/path-to-cluster/kafkacluster/.serverkeystore.jks
       ssl.keystore.password=changeit
       ssl.keystore.type=JKS
       ssl.truststore.location=/path-to-cluster/kafkacluster/.truststore.jks
       ssl.truststore.password=changeit
       ssl.trustStore.type=JKS
    ```
4.  Copy the .serverkeystore.jks and .truststore.jks in local to facilitate upload in UI for Apache Kafka
5.  In configuring cluster, provide a name of the cluster to monitor and input the brokers' IP addresses and the default port of kafka 9093
6.  In the Truststore, upload the truststore.jks file and provide the default password 'changeit'
7.  In the Authentication section, select protocol SSL and then upload the serverkeystore.jks file. Provide the default password 'changeit'
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
2.  Import GPG key: sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
3.  Install Jenkins: sudo yum install jenkins
4.  Reload the systemd manager: sudo systemctl daemon-reload
5.  Start Jenkins server: sudo systemctl start jenkins
6.  Verify Jenkins service is running: sudo systemctl status jenkins
7.  Enable Jenkins to start at boot-up: sudo systemctl enable jenkins
8.  Launch Jenkins: http:<jenkins-server-name>:8080
9.  Unlock jenkins by copying the initial admin password kept here: car /var/lib/jenkins/secrets/initialAdminPassword into the Unlock window that appears on launch
10.  Install the requisite plugins
11.  Set the username and password and Launch Jenkins
### Integrate JMeter with Jenkins
1.	After you install and setup Jenkins server, install the 'Performance' plugin using Manage Jenkins - Plugins.
2.	Create a job related to your script(s). 
3.	While configuring the job, in the Build Steps section, use parameter values to pass in the command-line. For e.g. The host, port, dbName, dbuser, user pwd etc. have been passed along with constant timer, random timer(if any), user count to easily change workload model settings during execution. Add the line -j jmeter.save.saveservice.output_format=xml to this command-line invocation so that performance results can be produced and trend graphs displayed.
	<img width="452" alt="image" src="https://github.com/user-attachments/assets/9d8460a0-289e-4aff-b65e-e083b97e1a92" />
4.	Check ‘This project is parameterized’ and add the parameters(of course same name should be used) which you have passed in the Build Steps’ Execute shell section. 
5.	Add Post-Build Action to the Build, select the ‘Publish Performance test result report’ and add the path to your result jtl file(which you provided in the Execute Shell Command in Build Steps. Check the ‘Show Trend Graphs’, if not checked already and choose your Error Threshold. You may use Advanced options to choose the metrics to display, percentiles to display and also fail the build if the result jtl file is not present. 
6.	Now pass the parameters in your jmeter code. For JDBC Connection Configuration parameters, use the ${__P()} methods instead of regular parameters. Providing a jmx snippet below for better understanding:
	<img width="452" alt="image" src="https://github.com/user-attachments/assets/dd007efd-1c24-42eb-9b78-5f83dcef324b" />
### What you get?
1.	You may run the job with the parameters now supplied during run-time itself from Jenkins UI which is intuitive and any user may use it, without much scratching their heads
   <img width="452" alt="image" src="https://github.com/user-attachments/assets/6384787b-98ab-4d5d-a90c-c44a1b3658bf" />
2.	Check the Performance Report once the result is parsed and created by Performance Plugin. A sample result looks like this:
   <img width="452" alt="image" src="https://github.com/user-attachments/assets/9ac64c5e-341f-4d76-b1d4-7c3d25e809fa" />
3.	You also have the option to view Trend Results at one glance and therefore comparative analysis is already taken care of without using excels:
   <img width="452" alt="image" src="https://github.com/user-attachments/assets/63c73838-d084-4cad-ab86-c0f0c762af2b" />
4.	You can also filter the trend results according to your needs, for e.g. view the trend for the last n builds or of a particular build, without searching all over:
   <img width="452" alt="image" src="https://github.com/user-attachments/assets/866f289b-6a67-4837-9d33-c9726bfaf843" />










