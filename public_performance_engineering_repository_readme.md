# Public Performance Engineering Repository

> **Audience:** Beginners to intermediate engineers who want a *practical*, *production-minded* entry point into Performance Testing, Performance Engineering, and Observability.
>
> **Intent:** This repository is intentionally kept **simple and opinionated**. It serves as a **learning runway**, not a polished enterprise framework. Advanced utilities (Kubernetes autoscaling, capacity models, infra tooling) will be added incrementally.

---

## What this repository is (and is not)

### ✔ What it *is*
- A **starter kit** for performance testing & monitoring
- Hands-on walkthroughs for **JMeter, Jenkins CI, Prometheus, Grafana, Kafka**
- Examples that reflect **real-world service-based delivery constraints**
- Opinionated patterns I’ve used across large client environments

### ✖ What it is *not*
- A plug-and-play enterprise product
- A replacement for official documentation
- A dump of every internal tool I’ve built over the years

---

## Tooling & Concepts Covered

- **Performance Testing**: Apache JMeter (CLI-first)
- **CI/CD**: Jenkins-driven performance pipelines
- **Observability**: Prometheus, Grafana, Node Exporter
- **Messaging Systems**: Kafka & Kafka Connect monitoring
- **Automation**: Ansible + Jenkins parameterization
- **Java Diagnostics**: JMX, JConsole, jVisualVM

> Design philosophy: *Measure first → model capacity → recommend infra changes → validate again.*

---

## Prerequisites

- Linux (RHEL / Amazon Linux preferred)
- Java 17+ (examples use Java 21)
- Basic familiarity with shell, Jenkins, and JVM-based apps

---

## Java Setup (Required)

```bash
yum update -y
yum install java-21-openjdk -y
java -version
```

If multiple Java versions exist:

```bash
sudo update-alternatives --config java
```

---

## Apache JMeter Setup (RHEL 9)

```bash
cd /opt
curl -O https://dlcdn.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar -xvf apache-jmeter-5.6.3.tgz
mv apache-jmeter-5.6.3 jmeter
rm -rf apache-jmeter-5.6.3
```

Cleanup and plugin tooling:

```bash
cd jmeter
rm -rf printable_docs docs
cd lib
curl -O https://repo1.maven.org/maven2/kg/apc/cmdrunner/2.3/cmdrunner-2.3.jar
cd ext
curl -O https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/1.9/jmeter-plugins-manager-1.9.jar
```

Verify:

```bash
jmeter --version
```

---

## Jenkins + JMeter CI Integration

- Parameterized Jenkins jobs
- Runtime CSV uploads
- Trend analysis without spreadsheets
- CI-friendly execution (no GUI dependency)

This pattern is designed for **multi-client service delivery**, where test data and environments change frequently.

---

## Observability Stack

### Prometheus Setup (High-level)
- Dedicated system user
- Node Exporter based host metrics
- JMX Exporter for JVM apps

> Detailed scripts will be published incrementally to keep this repo beginner-friendly.

### Grafana
- Prometheus as primary datasource
- Infra + JVM dashboards
- Kafka & Logstash monitoring examples included

---

## Kafka Monitoring

Covers:
- Broker JVM metrics via JMX Exporter
- Kafka Connect (source/sink) monitoring
- Consumer lag visibility
- Infra sizing signals (heap, GC, network, partitions)

> Capacity modeling insights and infra recommendations are intentionally **lightly documented** here; future repos will deep-dive.

---

## Automation Patterns

### Jenkins-driven Ansible

- CSV-driven parameterization
- Python-based CSV → INI conversion
- One-click multi-host deployments

This pattern evolved from repeated **client onboarding pain points** in large programs.

---

## Who should use this repo

- Engineers new to **performance engineering**
- QA professionals transitioning into **non-functional ownership**
- Developers wanting **infra-aware testing**
- Anyone tired of theoretical PPT-heavy perf discussions 😉

---

## Roadmap (Incremental)

- Kubernetes HPA & autoscaling utilities
- Capacity modeling examples
- Kafka infra sizing templates
- Failure-mode & resilience experiments

---

## Author

**Nabanish Sinha**  
Performance & Resilience Architect  

> This repository reflects practical lessons from **service-based delivery**, not idealized greenfield setups.

---

## Disclaimer

- Examples are provided *as-is*
- Adapt before using in production
- This repo prioritizes **clarity over completeness**

---

If you’re learning performance engineering — start here, break things safely, and then go deeper.

