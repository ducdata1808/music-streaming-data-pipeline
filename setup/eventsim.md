# EventSim Setup Guide

EventSim is a tool that generates event data for testing and simulating real-time systems.

## Prerequisites
- Java 8
- Scala & SBT (Scala Build Tool)

## 1. Installation

Install Java 8 and the SBT package manager:
```bash
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add
sudo apt-get update
sudo apt-get install openjdk-8-jdk scala sbt
```

Ensure Java 8 is the default version:
```bash
sudo update-alternatives --config java
```

Clone the repository and build:
```bash
git clone https://github.com/Interana/eventsim.git
cd eventsim
sbt assembly
```

## 2. Configuration & Permissions
Add execute permissions to the event generator script:
```bash
chmod +x bin/eventsim
```

If needed, edit the `bin/eventsim` file to point to the correct Java path and jar file:
```bash
#! /bin/bash 
java -XX:+AggressiveOpts -XX:+UseG1GC -XX:+UseStringDeduplication -Xmx4G -Duser.country=US -Duser.language=en -jar target/scala-2.12/eventsim-assembly-2.0.jar "$@"
```

> [!TIP]
> Test if it works by generating 100 sample records to a JSON file:
> `./bin/eventsim -c "examples/example-config.json" -n 100 test_data.json`

## 3. Running EventSim (Automated)
Instead of typing out the long command to stream to Kafka, you can use the helper script:

```bash
cd ~/eventsim_project/scripts
./run_eventsim.sh
```
This script will continually generate records simulating events from 2026 to 2099 and pipe them to the Kafka `music_events` topic.

## 4. Increase generating speed
Change n in run_eventsim.sh to a larger number
Change start_time in run_eventsim.sh to recent date to reduce generating time
Use multiple terminal to run multiple instances of run_eventsim.sh (use the same topic name)
