# Chapter 10: Control Plane

In the preceding chapters we worked our way up from bare metal through layers of abstraction and virtualization to create a sea of instances running on machines. We've got software scattered around like an upended box of LEGO blocks. It's up to the "control plane" to put these pieces in the right place and knit them together into a somewhat coherent whole.

The control plane encompasses all the software and services that run in the background to make production load successful. One way to think about it is this: if production user data passes through it, it's production software. If its main job is to manage other software, it's the control plane.

A challenge we'll face in this chapter is that the solution space is not well partitioned among tools, packages, and vendors. It's nowhere near as simple as picking one download from each column. There are overlaps and gaps. Not every combination will work together. No single package does everything. We are left with a lot of integration effort and plenty of trial and error.

## How Much Is Right for You?

As we look at the control plane, keep in mind that every part of this is optional. You can do without every piece of it, if you're willing to make some trade-offs. For example, logging and monitoring helps with postmortem analysis, incident recovery, and defect discovery. Without it, all those will take longer or simply not be done. If you can live with extended outages, or if it's okay to find out your software is down by getting a call from the CEO, then you don't need that part of the control plane.

In a more palatable example, you don't need IP management software if you're running a static network on physical hardware. Up to a certain scale, this is probably acceptable and may be more cost-effective. Once you move to an

overlay network with multiple VLANs and software switches, you'll go mad without IP management.

The more sophisticated your control plane becomes, the more it costs to implement and operate. Every piece represents ongoing operational cost. Think of it like trading off the fixed cost of dedicated people versus the variable cost of speeding up deployments, incident recovery, provisioning services, and so on. If you're small and the rate of change is low, you may find it's not worth it. If you can amortize the cost of a platform team across hundreds of services deployed hundreds of times per year, then it makes a lot more sense.

This cost equation isn't static, either. New open-source operations tools are released nearly every day. These are often created by a large-scale company scratching its own itch, but these companies release tools and libraries that lift up everyone else in the industry. When the first edition of this book was published in 2007, logging and monitoring was almost entirely a commercial market. Now it is almost entirely open source. At that time, automated provisioning of operating systems required either a large commercial package (six figures in license cost, six more in implementation cost) or a complete roll-your-own approach. Today, the hardest problem is choosing among all the fantastic alternatives!

Bottom line: Don't assume you must install one of everything you read about. But also keep evaluating the overhead and difficulty of different solutions. The landscape changes pretty quickly.

## Mechanical Advantage

"Mechanical advantage" is the multiplier on human effort that simple machines provide. With mechanical advantage, a person can move something much heavier than themselves. With a long-enough lever and a place to stand, Archimedes claimed he could move Earth itself.

The kicker about mechanical advantage is that it works for good or for ill. High leverage allows a person to make large changes with less effort. We hope that those are mostly beneficial, such as releasing new software to a fleet of ten thousand machines. Unfortunately, there are many examples of automation gone wrong. Back in *Force Multiplier*, on page 80, we saw how Reddit suffered from overeager automation. The Governor pattern discussed in *Governor*, on page 123, aims to reduce the harm when automation goes the wrong way.

Let's consider an example from a real outage that affected many people and companies.

On February 28, 2017, Amazon Web Services' S3 service in the US-East-1 region went down. Tens of thousands of companies suffered outages due to their own hard dependencies on S3. Large parts of the Net pretty much went dark. Operators went nuts. Users hammered status sites until those crumbled too. (At least, they hammered status sites that weren't themselves hosted on S3!) The total disruption in S3 lasted about two hours, but it was many more hours before all the S3 consumers were healthy. It was "reboot day" for a big chunk of the SaaS market.

Amazon, like other service providers, has learned that customer confidence can really be shaken with an event like this. One of the most important pieces of communication afterward is a postmortem review of the outage. Every postmortem review has three important jobs to do:

- 1. Explain what happened.
- Apologize.
- 3. Commit to improvement.

Amazon's write-up does a good job at all three of these. There are some really interesting lessons for us in that postmortem.

### System Failure, Not Human Error

Amazon clearly states that "[a]n authorized S3 team member using an established playbook executed a command which was intended to remove a small number of servers for one of the S3 subsystems that is used by the S3 billing process. Unfortunately, one of the inputs to the command was entered incorrectly and a larger set of servers was removed than intended." Parsing that just a little bit, we can understand that someone mistyped a command. First and foremost, whoever that was has my deepest sympathy. I've felt that shock and horror when I realized that I, personally, had just caused an outage. It's a terrible feeling. But there's much more that we should learn from this.

Take a moment to read or reread that postmortem. The words "human error" don't appear anywhere. It's hard to overstate the importance of that. This is not a case of humans failing the system. It's a case of the system failing humans. The administrative tools and playbooks allowed this error to happen. They amplified a minor error into enormous consequences. We must regard this as a system failure. "System" here means the whole system—S3 plus the control plane software and human processes to manage it all.

KWW SDVZ V DPD | RQ FRP PH V V D J H

The second thing to note is that the playbook involved here had apparently been used before. But it hadn't previously resulted in front-page news. Why not? For whatever reason, it worked before. We should try to learn from the successes as well as the failures. When the playbook was previously used, were the conditions different? There could be variations in any of the following:

- Who executed it? Was there a "second set of eyes"?
- Were there revisions to the playbook? Sometimes error-checking steps get relaxed over time.
- What feedback did the underlying system provide? Feedback may have helped avert previous problems.

We tend to have postmortem reviews of incidents with bad outcomes. Then we look for causes, and any anomaly either gets labeled as a root cause or a contributing factor. But many times those same anomalies are present during "ordinary" operations, too. We give them more weight after an outage because we have the benefit of hindsight.

We also have many opportunities to learn from successful operations. Anomalies are present all the time, but most of the time they don't cause outages. Let's devote some effort to learning from those. Have postmortems for successful changes. See what variations or anomalies happened. Find out what the "near misses" were. Did someone type an incorrect command but catch it before executing? That's a near miss. Find out how they caught it. Find out what safety net could have helped them catch it or stop it from doing harm.

## Automation Goes Really Fast

Another fascinating bit of information shows up in the AWS postmortem. "While removal of capacity is a key operational practice, in this instance, the tool used allowed too much capacity to be removed too quickly. We have modified this tool to remove capacity more slowly and added safeguards to prevent capacity from being removed when it will take any subsystem below its minimum required capacity level."

This part stuck out because it closely resembled the outage that Reddit.com suffered in August 2016.<sup>2</sup> After that outage, Reddit reported the event was precipitated by its autoscaling service. It observed a partially migrated ZooKeeper database that claimed Reddit only needed a tiny fraction of the servers it was running. The autoscaler dutifully shut down the rest of the servers.

<sup>2.</sup> ZZZ WGGLW FRP U DQQRXQFHPHQWV FRPPHQQWLWBZEDVEZCKREZWBRQBDXJB

A common thread running through these outages is that the automation is not being used simply to enact the will of a human administrator. Rather, it is more like industrial robotics: the control plane senses the current state of the system, compares it to the desired state, and effects changes to bring the current state into the desired state.

In both cases, it's totally normal to shut down an instance or two, maybe more. Most of the time, those individual VMs or processes don't matter. One machine out of thousands is no big deal. But at some point, the automation shuts down enough machines to make a noticeable dent in capacity. The exact threshold depends on how much spare capacity you have for handling bursts. But once we're talking about shutting down more than 50 percent of total server capacity, the automation probably ought to pause for some human confirmation that this is really the right course of action.

Automation has no judgment. When it goes wrong, it tends to do so really, really quickly. By the time a human perceives the problem, it's a question of recovery rather than intervention. How can we allow human intervention without putting a human in the loop for everything? We should use automation for the things humans are bad at: repetitive tasks and fast response. We should use humans for the things automation is bad at: perceiving the whole situation at a higher level.

With that groundwork in place, let's consider the major components of a control plane. In each area, we'll look at the budget approach and the Cadillac approach (bearing in mind that the landscape changes quickly).

## Platform and Ecosystem

Suppose we decide to put monitoring into the platform. There'll surely be a monitoring team within the platform team. Would we expect that team to respond to application alerts? Definitely not! Instead, that team should provide the capability that others then use. In other words, the monitoring team doesn't do the monitoring, it provides the ability for others to do their own monitoring. This is a mental shift from ownership of the domain to offering a service to customers.

Seems like an easy enough heuristic, but it leads immediately to a change in the way we view responsibilities. For example, it used to be common for the monitoring team to implement all the specific monitors, triggers, alerts, and thresholds. That puts them right in the middle of the change loop. It means they have to create a "request for monitoring" form for development teams to

fill out (whether paper or online). It means that tweaks and changes to monitoring have to go through a queue in the form of the other teams' inboxes.

If we respect the customer-centric model, then the monitoring team should not implement the actual monitors. Team members should work one level removed: they implement the tools that let their customers implement their own monitors. In other words, the monitoring team may need to build infrastructure to receive alerts, deployment tools that push their monitoring agents out (if applicable), or scripting tools that let developers provide a JSON description of the monitors they need.

This begins to look like creating interfaces in an object-oriented application. The monitoring team offers up an interface that development teams can use. The details of implementation are owned by the monitoring team and can change as long as they continue to support their contract.

What about database administrators? It's a shame that the acronym DBA can mean both "database administrator" and "database architect." The lines of responsibility have gotten blurred over the years. The administrator should ideally be concerned with creating a high-performance, stable platform on which development teams can build any kind of database. Sadly, technology constraints in days past led us to have DBAs that were responsible for both the health of the database server and the data model used by the applications. This caused a lot of tension when the data model was contorted to make the server happy instead of vice versa. A lot of the energy behind the NoSQL movement was really about refactoring those responsibilities.

With NoSQL and postrelational databases, we see a different split in the roles. The platform team includes database administrators who keep the database running and healthy. They ensure there's enough capacity but the data model is up to the application.

The picture is harder with SQL-based RDBMSs. It's too easy for one application to make a harmful schema change that affects other consumers. This leads us to decree a separate physical database for each service. It's not very resource-efficient, but it does unfreeze development teams to move independently, without a queue for DBA attention.

Is it possible to create a platform that allows safe, autonomous delivery into a shared SQL database? Yes, but it requires accommodation from both developers and DBAs. In particular, the difficulty of parsing SQL to do automated sanity checking is too high. Developers and DBAs have to agree on a simpler, machine-readable format that can be scripted against. Many migration frameworks offer XML, JSON, or YAML formats that suffice.

Keep in mind that the goal for the platform team is to enable their customers. The team should be trying to take themselves out of the loop on every day-to-day process and focus on building safety and performance into the platform itself. If you find that your technology choices or architecture make this really difficult, it's a good argument to change your technology!

## Development Is Production

Quick, think of a "dev server." What comes to mind? Probably a barely running mess full of old temp files, tarballs named after people, scripts that aren't in version control and nobody's quite sure if they're still used, SSH keys from developers who left years ago...in short, a big ramshackle mess.

Okay, now think about your QA environment. Does it fully work? Does it really? Or are there a bunch of integrations stubbed out? Maybe there are jobs that run in production that can't run in QA. Probably the database isn't very realistic, because the production data has PII that can't be copied around. Do you have high confidence that passing tests in QA means the software will work in production?

Maybe you're in the minority. If your image of a dev server is a fresh virtual machine with a known configuration, that's great! Maybe your image of QA is a whole environment stamped out by the same automation tools that deploy to production, with an anonymized sample of production data from within the last week. If so, you're doing quite well.

Most organizations treat their development environments like a shantytown. Stuff only works there because the developers run their own power by daisy-chaining extension cords from a nearby settlement. QA doesn't match production in topology or scale, and multiple dev teams are trying to get into QA but can't because there's only one environment. (Hint: There's no "right number" of QA environments. Virtualize them so every team can create its own ondemand QA environment.) In short, development environments are treated with utter disregard.

This is kind of odd when you think about it, because developers are creating content all the time. They build software that has to go into version control (a service), get constructed in CI (another service), tested in QA (a service), and stored in a repository (yet another service). When these services are down, developers can't do their jobs. Let's look at an analogy. Suppose your company's content management system went down so copywriters couldn't do their jobs. That would be at least a Severity 2 outage, right?

The tools, services, and environments that developers need to do their jobs should be treated with production-level SLAs. The development platform *is* the production environment for the job of creating software.

## System-Wide Transparency

Back in *Transparency*, on page 162, we saw how individual instances can reveal their state. That's the start of a total story about transparency. Now we look at how to assemble a picture of system-wide health from the individual instances' information.

The first place to start is by defining what we need from our efforts. When dealing with the system as a whole, two fundamental questions need to be answered:

- 1. Are users receiving a good experience?
- 2. Is the system creating the economic value we want?

Notice that the question, "Is everything running?" isn't on that list. Even at small scale, we should be able to survive periods where everything *isn't* running. At scale, "partially broken" is the normal state of operation. It's rare to find all instances running with no deployments or failures at any given moment.

### Real-User Monitoring

It is hard to deduce whether users are receiving a good experience from individual instance metrics. (It would require a model of the whole system that accounts for circuit breakers, caches, fallbacks, and a pile of other implementation details that change frequently.) Instead, the best way to tell if users are receiving a good experience is to measure it directly. This is known as real-user monitoring (or RUM, if you like).

Mobile and web apps can have instrumentation that reports their timing and failures up to a central service. That can take a lot of infrastructure, so you may consider a service such as New Relic or Datadog. <sup>3,4</sup> If you are at a scale where it makes sense to run it yourself, on-premise software such as AppDynamics or CA's APM might be the thing for you. <sup>5,6</sup> Some of these products also allow you to watch network traffic at the edge of your system, recording HTTP sessions for analysis or playback.

<sup>3.</sup> KWW SQWHZHLOLF FRP

<sup>4.</sup> ZZZ GDWDGRJKT FRP

ZZZ DSSG\QDPLFV FRP

ZZZFD FRP XAVGSEBW V DSSOLFDPWSQ#EQISRQLEWURULQJKW PO

Using these services has three advantages over the "DIY" approach. The first is rapid startup. You don't need to build infrastructure or configure monitoring software. It is quite possible to get going with data collection in under an hour. Second, they offer agents and connectors for a wide array of technology, which makes it much easier to integrate all your monitoring into one place. Finally, their dashboards and visualization tend to be more polished than open-source alternatives.

There are downsides, of course. For one thing, these are commercial services. You'll be paying a subscription fee. As your system scales, so will your fees. There may come a time when the fees become unpalatable, but the switching cost of moving to your own infrastructure is equally unpalatable. Second, some companies are absolutely unwilling to have even monitoring data crossing the Internet.

On-premise commercial solutions, such as AppDynamics, offer easy integration and polished visualization, but these lose the advantage of rapid startup and also have scaling fees.

The open-source arena has produced some excellent tools, but the usual open-source effect is at play: integrating the tools to your system can be a challenge. For that matter, integrating the tools with each other can be a challenge! The dashboards and visualization are also less polished and less user-friendly. While removing the very visible monthly fees for a service, the open source approach has less-visible costs in the form of labor and infrastructure.

Half of the vendors at operations or software architecture conferences are in this space, so the names may change by the time you read this. The broad category here is called "application performance management," and it seems to be one of the last areas of operations software that hasn't been replaced by open-source packages. As with other kinds of operations software, it's not that important to choose the ideal solution. Instead, focus on adopting your chosen solution thoroughly. Don't leave any "dead zones" in your system.

Real-user monitoring is most useful to understand in terms of the current state and recent history. Dashboards and graphs are the most common ways to visualize this.

### Economic Value

Some software exists as art and some exists as entertainment. Most of the software we write for companies exists to create economic value. It may seem odd to be talking about the economics of software systems in a section about transparency, but this is where we can most directly perceive the linkage

between our systems and our financial success. The value created by our systems can be harmed if the user experience is bad. It can also be harmed if the system cost is too high. These are the "top line" and "bottom line" effects. We should build our transparency in terms of revealing the way that the recent past, current state, and future state connect to revenue and costs.

The top line is income. Revenue. The good stuff. Our system should be able to tell us if we're making as much as we "should be" right now. In other words, are there performance bottlenecks that prevent us from signing up more new users? Is some crucial service returning errors that turn people off before they register? The specific needs here vary according to your domain, but you should plan to watch the following:

- Watch each step of a business process. Is there a rapid drop-off in some step? Is some service in a revenue-generating process throwing exceptions in logs? If so, it's probably reducing your top line.
- Watch the depth of queues. Queue depth is your first indicator of performance degradation. A non-zero queue depth always means work takes longer to get through the process. For many business transactions, that queuing time directly hits your revenue.

The bottom line is net profit (or loss). It is the top line minus costs. Cost comes from infrastructure, especially in these days of autoscaled, elastic, pay-as-you-go services. Nearly every startup has a horror story about unchecked autoscaling costing them thousands of dollars due to unchecked demand. Worse yet, that sometimes results from runaway automation spinning up too many resources.

Cost also comes from operations. The harder your software is to operate, the more time it takes from people. That's true whether you're in a DevOps-style organization or a traditional siloed organization. Either way, any time spent responding to incidents is unplanned work that could have gone to raising the top line.

Another less visible source of cost comes from our platforms and runtimes. Some languages are very fast to code in but require more instances to handle a particular workload. You can improve the bottom line by moving crucial services to technology with a smaller footprint or faster processing. Before you do, though, make sure it's a service that makes a difference. In other words, your feature that detects birds in photographs taken inside national parks may require a lot of CPU time; but if it only gets used once a month, it's not material to your bottom line.

So far we've talked about the current state and recent past. Our transparency tools should also help us consider the near future as well, such as these questions:

- Are there opportunities to increase the top line by improving performance or reducing queues?
- Are we going to hit a bottleneck that will prevent us from increasing the top line?
- Are there opportunities to increase the bottom line by optimizing services?
   Can we see places that are overscaled?
- Can we replace slow-performing or large-footprint instances with more efficient ones?

The idea of monitoring, log collection, alerting, and dashboarding as being about economic value more than technical availability may be unfamiliar. Even so, if you adopt this perspective, you'll find that it is easy to make decisions about what to monitor, how much data to collect, and how to represent it.

### The Risk of Fragmentation

The usual notion of perspectives splits into "technical" and "business" concerns. The "technical" perspective may even be split into "development" and "operations." Most of the time, these constituencies look at different measurements collected by different means. Imagine the difficulty in planning when marketing uses tracking bugs on web pages, sales uses conversions reported in a business intelligence tool, operations analyzes log files in Splunk, and development uses blind hope and intuition. Could this crew ever agree on how the system is doing? It'd be much better to integrate the information so all parties can see the same data through similar interfaces.

Different constituencies require different perspectives. These perspectives won't all be served by the same views into the systems, but they should be served by the same information system overall. Just as the question, "How's the weather?" means very different things to a gardener, a pilot, and a meteorologist, the question, "How's it going?" means something decidedly distinct when coming from the CEO or the system administrator. Likewise, a bunch of CPU utilization graphs won't mean a lot to the marketing team. Each "special interest group" in your company may have its own favorite dashboard, but everyone should be able to see how releases affect user engagement or conversion rate affects latency.

### Logs and Stats

In <u>Transparency</u>, on page 162, we saw the importance of good logging and metrics generation at the microscopic scale. At the system scale, we need to gather all that data and make sense of it. This is the job of log and metrics collectors.

Like a lot of these tools, log collectors can either work in push or pull mode. Push mode means the instance is pushing logs over the network, typically with the venerable syslog protocol. Push mode is quite helpful with containers, since they don't have any long-lived identity and often have no local storage.

With a pull-mode tool, the collector runs on a central machine and reaches out to all known hosts to remote-copy the logs. In this mode, services just write their logs to local files.

Just getting all the logs on one host is a minor achievement. The real beauty comes from indexing the logs. Then you can search them for patterns, make trendline graphs, and raise alerts when bad things happen. Splunk dominates the log indexing space today. The troika of Elasticsearch, Logstash, and Kibana is another popular implementation.

The story for metrics is much the same, except that the information isn't always available in files. Some information can only be retrieved by running a program on the target machine to sample, say, network interface utilization and error rates. That's why metrics collectors often come with additional tools to take measurements on the instances.

Metrics also have the interesting property that you can aggregate them over time. Most of the metrics databases keep fine-grained measurements for very recent samples, but then they aggregate them to larger and larger spans as the samples get older. For example, the error rate on a NIC may be available second by second for today, in one-minute granularity for the past seven days, and only as hourly aggregates before that. This has two benefits. First, it *really* saves on disk space! Second, it also makes queries across very large time spans possible.

## What to Expose

If you could predict which metrics would limit capacity, reveal stability problems, or expose other cracks in the system, then you could monitor only those. But that prediction will have two problems. First, you're likely to guess

<sup>7.</sup> KWWSWRROVRJUHKWWIPO UIF

<sup>8.</sup> ZZZ VSOXQN FRP

wrong. Second, even if you guess right, the key metrics change over time. Code changes and demand patterns change. The bottleneck that burns you next year probably doesn't exist right now.

Of course, you could spend an unlimited amount of effort exposing metrics for absolutely everything. Since your system still has to *do* something other than just collect data, I've found a few heuristics to help decide which variables or metrics to expose. Some of these will be available right away. For others, you might need to add code to collect the data in the first place. Here are some categories of things I've consistently found useful.

### Traffic indicators

Page requests, page requests total, transaction counts, concurrent sessions

### Business transaction, for each type

Number processed, number aborted, dollar value, transaction aging, conversion rate, completion rate

#### Users

Demographics or classification, technographics, percentage of users who are registered, number of users, usage patterns, errors encountered, successful logins, unsuccessful logins

### Resource pool health

Enabled state, total resources (as applied to connection pools, worker thread pools, and any other resource pools), resources checked out, highwater mark, number of resources created, number of resources destroyed, number of times checked out, number of threads blocked waiting for a resource, number of times a thread has blocked waiting

### Database connection health

Number of 64/([FHSWSLtRfpwn, number of queries, average response time to queries

### Data consumption

Number of entities or rows present, footprint in memory and on disk

### Integration point health

State of circuit breaker, number of timeouts, number of requests, average response time, number of good responses, number of network errors, number of protocol errors, number of application errors, actual IP address of the remote endpoint, current number of concurrent requests, concurrent request high-water mark

### Cache health

Items in cache, memory used by cache, cache hit rate, items flushed by garbage collector, configured upper limit, time spent creating items

All of the counters have an implied time component. You should read them as if they all end with "in the last n minutes" or "since the last reset."

As you can see, even a medium-sized system could have hundreds of metrics. Each one has some range in its normal and acceptable values. This might be a tolerance around a target value or a threshold that should not be crossed. The metric is "nominal" as long as it's within that acceptable range. Often, a second range will indicate a "caution" signal, warning that the parameter is approaching a threshold.

For continuous metrics, a handy rule-of-thumb definition for nominal would be "the mean value for this time period plus or minus two standard deviations." The choice of time period is where it gets interesting. Most metrics have a traffic-driven component, so the time period that shows the most stable correlation will be the "hour of the week"—that is, 2 p.m. on Tuesday. The day of the month means little. In certain industries—such as travel, floral, and sports—the most relevant measurement is counting backward from a holiday or event.

For a retailer, the "day of week" pattern will be overlaid on a strong "week of year" cycle. There is no one right answer for all organizations.

## Configuration Services

Configuration services like ZooKeeper and etcd are distributed databases that applications can use to coordinate their configuration. Onfiguration in this sense is more than just the static parameters that an instance would keep in SRISHUWfilesVIt does include simple settings such as hostnames, resource pool sizes, and timeouts. But "configuration" also includes the arrangement of instances among themselves. These configuration databases can be used for orchestration, leader election (in the case of a cluster with a master node), or quorum-based consensus.

However, these are built with code and not magic. They are still bound by the constraints of the CAP theorem and sub-light-speed communications. The configuration services are themselves distributed databases.

KWW \$FXRHNH SHOUSD FKJH RU

<sup>10.</sup> KWWSFRHURV FRP HWFG GRFV ODWHVW

These services are scalable but not elastic. That means you can add and remove nodes, but response time will degrade as the nodes rebalance their data. It often requires an admin action to get the cluster to accept a new member or to indicate that an old member is gone for good.

Keep in mind that the configuration service suffers the same network trauma that every other application does. There will be times that clients can't reach the configuration service. Worse, there will be times when the nodes of the configuration service can't reach each other but clients can reach the nodes. In this case, it has to be safe for the clients to run with slightly outdated configurations. Otherwise, you have no choice but to shut down applications when the configuration service is partitioned.

Information doesn't only need to flow from the service to client instances, either. Instances can report back with their version numbers (or commit SHAs) and node identifiers. That means you can write a program or script to reconcile the actual state of the system with the expected state after a deployment. Be somewhat careful with this, as the configuration services can sustain high read volume but have to go through some consensus mechanism for every write. It's OK to use these for relatively slowly changing configuration data, but they definitely don't stand in for a log collection system.

A few pointers about configuration services:

- Make sure your instances can start without the configuration service.
- Make sure your instances don't stop working when configuration is unreachable.
- Make sure that a partitioned configuration node doesn't have the ability to shut down the world.
- Replicate across geographic regions.

## Provisioning and Deployment Services

In Part III of this book, we look at how to design services and applications to be deployable. Here let's look at the supporting infrastructure to perform the deployments themselves.

Deployment may be the most well-trodden area of operations tools. It's an obvious nexus between development and production. To some organizations, deployment is "DevOps." It's understandable. In many organizations deployment is ridiculously painful, so it's a good place to start making life better.

Consequently, a host of deployment tools represent "push" and "pull" methods. A push-style tool uses SSH or another agent so a central server can reach out to run scripts on the target machines. The machines may not know their own roles. The server assigns them.

In contrast, pull-based deployment tools rely more on the machines to know their own roles. Software on the machine reaches out to a configuration service to grab the latest bits for its role.

Pull-based tools work especially well with elastic scaling. Elastically scaled virtual machines or containers have ephemeral identities, so there's no point in having a push-based tool maintain a mapping from machine identity to role—the machine identity will shortly disappear, never to be seen again! With long-lived virtual machines or even physical hosts, push-based tools can be simpler to set up and administer. That's because they use commodity software like SSH rather than agents that require their own configuration and authentication techniques.

The deployment tool by itself should be augmented with a package repository. Whether that's an official "artifact repository" tool or an S3 bucket is up to you. But it's important to have a location for blessed binary bits that isn't populated from a developer's laptop. Production builds need to be run on a clean build server using libraries with known provenance. The build pipeline should tag the build as it passes various stages, especially verification steps like unit or integration tests.

This isn't just being pedantic or jumping through hoops to satisfy a security department. Repeatable builds are important so code that works on your machine works in production, too.

### Build Server as Attack Vector

Any widely used piece of server software will be used for an attack. That includes build servers such as Jenkins, Bamboo, or GoCD.

At least one major software vendor was attacked by means of the build environment. The attacker compromised a plugin to the vendor's continuous integration server. The plugin injected code that targeted a well-known customer of this vendor (relayed in personal communication to the author). This vendor kept its libraries in a controlled artifact repository but had overlooked the plugins to the build system itself. Those were downloaded directly from the Net.

Canary deployments are an important job of the build tooling. The "canary" is a small set of instances that get the new build first. For a period of time, the instances running the new build coexist with instances running the old build. (See Chapter 14, *Handling Versions*, on page 263, to enable peaceful coexistence.) If the canary instances behave oddly, or their metrics go south, then the build is *not* rolled out to the remaining population.

Like every other stage of build and deployment, the purpose of the canary deployment is to reject a bad build before it reaches the users.

At a larger scale, the deployment tool needs to interact with another service to decide on placement. That placement service will determine how many instances of a service to run. It should be network-aware so it can place instances across network regions for availability. Typically, it'll also drive the interconnect layer to set up IP addresses, VLANs, load balancers, and firewall rules.

When you get to this scale, it's probably time to look at the platform players. We'll cover those a bit later in *The Platform Players*, on page 212. Even though a dedicated team will sustain and operate the platform, you'll want to learn what it can do. That's because your software needs to include a description of its needs and wants for the platform to provide (usually as a JSON or YAML file in the build artifacts.)

## Command and Control

Live control is only necessary if it takes your instances a long time to be ready to run. As a thought experiment, imagine that any configuration change took ten milliseconds to roll out and that each instance could be restarted in another hundred milliseconds. In that world, live control would be more trouble than it was worth. Whenever an instance needed to be modified, it would be simpler to just kill the instance and let the scheduler start a new one.

If your instances run in containers and get their configuration from a configuration service, then that is exactly the world you live in. Containers start very quickly. New configuration would be used immediately.

Sadly, not every service is made of instances that start up so quickly. Anything based on Oracle's JVM (or OpenJDK for that matter) needs a "warm-up" period before the JIT really kicks in and makes it fast. Many services need to hold a lot of data in cache before they perform well enough. That also adds to the startup time. If the underlying infrastructure uses virtual machines instead of containers, then it can take several minutes to restart.

### Controls to Offer

In those cases, you need to look at ways to send control signals to running instances. Here is a brief checklist of controls to plan for:

- · Reset circuit breakers.
- Adjust connection pool sizes and timeouts.
- Disable specific outbound integrations.
- · Reload configuration.
- · Start or stop accepting load.
- Feature toggles.

Not every service will need all of these controls. They should give you a place to start, though.

Many services also expose controls to update the database schema, or even to delete all data and reseed it. These are presumably helpful in test environments but extremely hazardous in production. These controls result from a breakdown in roles. Developers don't trust operations to deploy the software and run the scripts correctly. Operations doesn't allow developers to log in to the production machines to update the schemata. That breakdown is itself a problem to fix. Don't build a self-destruct button into your production code!

Another common control is the "flush cache" button. This is also quite hazardous. It may not be a self-destruct button, but it's the button that vents all your atmosphere into space. An instance that flushes a cache will have really bad performance for the next several minutes. It may also generate a dogpile on the underlying service or database. Some kinds of services just can't respond until their working set is loaded into memory.

## Sending Commands

Once you've decided which controls to expose, there's still the question of how to convey the operator's intention out to the instances themselves. The simplest approach is to offer an admin API over HTTP. Each instance of a service would listen on a port for these requests. It needs to be a different port than ordinary traffic, however. The admin API should not be available to the general public!

An HTTP API leaves the door open for higher levels of automation in the future. In the beginning, it's fine to use cURL or any other HTTP client to poke the admin API. If that API happens to be described in Open API format, 11 then a GUI comes for free with Swagger UI. 12

<sup>11.</sup> ZZZ RSHQDSLV RU

<sup>12.</sup> KWW\SZDJJHUR VZDJXJHU

At larger scales, simple scripts to call the admin API may no longer suffice. For one thing, it takes time to make the API call to each instance. Suppose each API call takes just a quarter-second to complete. It will take two minutes to loop over a fleet of 500 instances. Actually, that assumes all the instances are up and responding properly. More likely, whatever script loops over those API calls will stall out partway through because some instance doesn't respond.

That's when it's time to build a "command queue." This is a shared message queue or pub/sub bus that all the instances can listen to. The admin tool sends out a command that the instances then perform.

Be careful, though! With a command queue, it's even easier to create a dogpile. It's often a good idea to have each instance add a random bit of delay to spread them out a bit. It can also help to identify "waves" or "gangs" of instances. So a command may target "wave 1," followed by "wave 2" and "wave 3" a few minutes later.

### Scriptable Interfaces

Admin GUIs demo very well. Unfortunately, they are a nightmare in production. The chief problem with a GUI is all the clicking. Mice are not easily scriptable—operators have to resort to GUI testing tools like Watir or Robo-Forms to automate them. GUIs slow down operations by forcing administrators to do the same manual process on each service or instance (there might be many) every time the process is needed. For example, the clean shutdown sequence on a particular order management system I worked on required clicking—and waiting several minutes—on each of six different servers. Guess how often the clean shutdown sequence was observed? With a one-hour change window, nobody can afford to spend half of it waiting on the GUI.

The net result is that GUIs make terrible administrative interfaces for long-term production operation. The best interface for long-term operation is the command line. Given a command line, operators can easily build a scaffolding of scripts, logging, and automated actions to keep your software happy.

### Remember This

It's easy to get excited about control plane software. Blog posts and Hacker News will always egg you on to build more. But always keep the operating costs in mind. Anything you build must either be maintained or torn down. Choose the options that are appropriate for your team size and the scale of your workload.

Start with visibility. Use logging, tracing, and metrics to create transparency. Collect and index logs to look for general patterns. That also gets logs off of the machines for postmortem analysis when a machine or instance fails.

Use configuration, provisioning, and deployment services to gain leverage over larger or more dynamic systems. The more you move toward ephemeral machines, the more you need these. This pipeline to production is not just a set of development tools. It is the production environment that developers use to produce value. Treat it with the same care as you would any other production environment.

Once the system is (somewhat) stabilized and problems are visible, build control mechanisms. These should give you more precise control than just reconfiguring and restarting instances. A large system deployed to long-lived machines benefits more from control mechanisms than a highly dynamic environment will.

## The Platform Players

So far, the solutions we've seen need "some assembly required." That means you can adopt them incrementally and defer commitment. Optionality comes at a cost, though, because you'll end up devoting time and resources plumbing together different parts. For example, a basic yet frustrating aspect of rolling your own platform is getting all the authentication and role-based authorization systems working together. Another common stumbling block is integrating the components' monitoring to provide a unified view.

At the other end of the integration spectrum, we have the platform players. The platform is to the data center what the operating system is to the personal computer. It abstracts the underlying infrastructure and presents a friendlier programming model. It manages resources and schedules tasks, just across multiple computers. A platform offers assurance that its parts will all work together coherently.

The population of platform players persistently permutes. At the time of writing, the top contenders are Google's Kubernetes, <sup>13</sup> Apache's Mesos, <sup>14</sup> CloudFoundry, <sup>15</sup> and Docker's "Swarm Mode." The odds are good that one or more new players will arrive before this book hits print.

<sup>13.</sup> KWWSWEHQHWHVLR

<sup>14.</sup> KWWRSHVRV DSDRKH RU

<sup>15.</sup> ZZZ FORXGIR XQQGU\

<sup>16.</sup> KWW SCAREV CHRUENP HQJLQ IP VZDU

A distinguishing feature of the platforms versus the cloud providers is about location. With the platforms, the software is available to be installed at any location: on your premises, in a hosting facility, or on top of a public cloud.

It's relatively easy for one team in a large organization to deploy its own monitoring framework. That's not the case with the platforms. They require care and feeding in their own right. It is more likely that a big group within an organization will move to one of the prefab platforms. That also means that individual teams probably don't have the capacity or authority to build their own platforms. (It wouldn't be cost-efficient anyway, because you need to amortize the support cost across a larger number of teams to justify it.)

When these platforms work well, it can be an amazingly smooth experience to deploy services. A single command can bundle up a JAR file or Python project with its runtime, build a virtual machine or container image, run it, and set up DNS for you.

If you are adopting one of these platforms, you should really embrace it. There's no point in using one at arm's length. Don't try to wrap the API or provide your own set of scripts. You're investing a lot in the platform, so get the most you can out of it!

## The Shopping List

This chapter gradually introduced many moving parts, so here's a checklist of the things you *might* need. Remember that not every organization needs everything on this list. Apply a cost/benefit trade-off view toward each.

- · Log collection and search
- Metrics collection and visualization
- Deployment
- · Configuration service
- Instance placement
- Instance and system visualization
- Scheduling
- IP, overlay network, firewall, and route management
- Autoscaler
- Alerting and notification

## Wrapping Up

Every solution creates new problems. As our systems have scaled up and out, we've virtualized everything. Workload runs across containers and VMs, one

or more clouds, and physical data centers. Just keeping tabs on this far-flung network requires new tools and techniques.

We've looked at the ways we can create visibility across whole systems so we can answer two fundamental questions: Are users receiving a good experience? And is the system producing the economic value we want? To answer those, we need to collect information across instances and services. We need tracing tools to understand where bottlenecks, inhibitors, and points of failure exist.

Once we know what's happening across the system, we also need ways to intervene. Control systems and configuration services allow us to instruct running instances to change their behavior. Scheduling and deployment tools let us change the instance assortment dynamically as our internal and external environments shift.

In all these services, we need to understand that automation makes *everything* go faster. It also lacks human judgment, so when things go wrong, they go wrong very quickly. We need to build safety mechanisms into the automation itself.

We've almost finished our holistic journey through the layers of design for production. There's just one last area to look into: security.
