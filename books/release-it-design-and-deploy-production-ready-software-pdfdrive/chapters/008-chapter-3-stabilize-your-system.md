# Chapter 3: Stabilize Your System

New software emerges like a new college graduate: full of optimistic vigor, suddenly facing the harsh realities of the world outside the lab. Things happen in the real world that just do not happen in the lab—usually bad things. In the lab, all the tests are contrived by people who know what answer they expect to get. The challenges your software encounters in the real world don't have such neat answers.

Enterprise software must be cynical. Cynical software expects bad things to happen and is never surprised when they do. Cynical software doesn't even trust itself, so it puts up internal barriers to protect itself from failures. It refuses to get too intimate with other systems, because it could get hurt.

The airline's Core Facilities project discussed in Chapter 2, Case Study: The Exception That Grounded an Airline, on page 9, was not cynical enough. As so often happens, the team got caught up in the excitement of new technology and advanced architecture. It had lots of great things to say about leverage and synergy. Dazzled by the dollar signs, it didn't see the stop sign and took a turn for the worse.

Poor stability carries significant real costs. The obvious cost is lost revenue. The retailer from Chapter 1, *Living in Production*, on page 1, loses \$1,000,000 per hour of downtime, and that's during the off-season. Trading systems can lose that much in a single missed transaction!

Industry studies show that it costs up to \$150 for an online retailer to acquire a customer. With 5,000 unique visitors per hour, assume 10 percent of those would-be visitors walk away for good. That's \$75,000 in wasted marketing.

<sup>1.</sup> KWWMXUWPNPHHUERP FXVWEPTHXJLVLWLRQ FRVW

Less tangible, but just as painful, is lost reputation. Tarnish to the brand might be less immediately obvious than lost customers, but try having your holiday-season operational problems reported in *Bloomberg Businessweek*. Millions of dollars in image advertising—touting online customer service—can be undone in a few hours by a batch of bad hard drives.

Good stability does not necessarily cost a lot. When building the architecture, design, and even low-level implementation of a system, many decision points have high leverage over the system's ultimate stability. Confronted with these leverage points, two paths might both satisfy the functional requirements (aiming for QA). One will lead to hours of downtime every year, while the other will not. The amazing thing is that the highly stable design usually costs the same to implement as the unstable one.

## Defining Stability

To talk about stability, we need to define some terms. A *transaction* is an abstract unit of work processed by the system. This is not the same as a database transaction. A single unit of work might encompass many database transactions. In an e-commerce site, for example, one common type of transaction is "customer places order." This transaction spans several pages, often including external integrations such as credit card verification. Transactions are the reason that the system exists. A single system can process just one type of transaction, making it a dedicated system. A *mixed workload* is a combination of different transaction types processed by a system.

The word *system* means the complete, interdependent set of hardware, applications, and services required to process transactions for users. A system might be as small as a single application, or it might be a sprawling, multitier network of applications and servers.

A robust system keeps processing transactions, even when transient impulses, persistent stresses, or component failures disrupt normal processing. This is what most people mean by "stability." It's not just that your individual servers or applications stay up and running but rather that the user can still get work done.

The terms *impulse* and *stress* come from mechanical engineering. An impulse is a rapid shock to the system. An impulse to the system is when something whacks it with a hammer. In contrast, stress to the system is a force applied to the system over an extended period.

A flash mob pounding the PlayStation 6 product detail page, thanks to a rumor that such a thing exists, causes an impulse. Ten thousand new sessions,

all arriving within one minute of each other, is very difficult for any service instance to withstand. A celebrity tweet about your site is an impulse. Dumping twelve million messages into a queue at midnight on November 21 is an impulse. These things can fracture the system in the blink of an eye.

On the other hand, getting slow responses from your credit card processor because it doesn't have enough capacity for all of its customers is a stress to the system. In a mechanical system, a material changes shape when stress is applied. This change in shape is called the *strain*. Stress produces strain. The same thing happens with computer systems. The stress from the credit card processor will cause strain to propagate to other parts of the system, which can produce odd effects. It could manifest as higher RAM usage on the web servers or excess I/O rates on the database server or as some other far distant effect.

A system with longevity keeps processing transactions for a long time. What is a long time? It depends. A useful working definition of "a long time" is the time between code deployments. If new code is deployed into production every week, then it doesn't matter if the system can run for two years without rebooting. On the other hand, a data collector in western Montana really shouldn't need to be rebooted by hand once a week. (Unless you want to live in western Montana, that is.)

## Extending Your Life Span

The major dangers to your system's longevity are memory leaks and data growth. Both kinds of sludge will kill your system in production. Both are rarely caught during testing.

Testing makes problems visible so you can fix them. Following Murphy's Law, whatever you do not test *against* will happen. Therefore, if you do not test for crashes right after midnight or out-of-memory errors in the application's forty-ninth hour of uptime, those crashes will happen. If you do not test for memory leaks that show up only after seven days, you will have memory leaks after seven days.

The trouble is that applications never run long enough in the development environment to reveal their longevity bugs. How long do you usually keep an application server running in your development environment? I'll bet the average life span is less than the length of a sitcom on Netflix. In QA, it might run a little longer but probably still gets recycled at least daily, if not more often. Even when it is up and running, it's not under continuous load. These

environments are not conducive to long-running tests, such as leaving the server running for a month under daily traffic.

These sorts of bugs usually aren't caught by load testing either. A load test runs for a specified period of time and then quits. Load-testing vendors charge large dollars per hour, so nobody asks them to keep the load running for a week at a time. Your development team probably shares the corporate network, so you can't disrupt such vital corporate activities as email and web browsing for days at a time.

So how do you find these kinds of bugs? The only way you can catch them before they bite you in production is to run your own longevity tests. If you can, set aside a developer machine. Have it run JMeter, Marathon, or some other load-testing tool. Don't hit the system hard; just keep driving requests all the time. (Also, be sure to have the scripts slack for a few hours a day to simulate the slow period during the middle of the night. That will catch connection pool and firewall timeouts.)

Sometimes the economics don't justify setting up a complete environment. If not, at least try to test important parts while stubbing out the rest. It's still better than nothing.

If all else fails, production becomes your longevity testing environment by default. You'll definitely find the bugs there, but it's not a recipe for a happy lifestyle.

## Failure Modes

Sudden impulses and excessive strain can both trigger catastrophic failure. In either case, some component of the system will start to fail before everything else does. In *Inviting Disaster [Chi01]*, James R. Chiles refers to these as "cracks in the system." He draws an analogy between a complex system on the verge of failure and a steel plate with a microscopic crack in the metal. Under stress, that crack can begin to propagate faster and faster. Eventually, the crack propagates faster than the speed of sound and the metal breaks explosively. The original trigger and the way the crack spreads to the rest of the system, together with the result of the damage, are collectively called a *failure mode*.

No matter what, your system will have a variety of failure modes. Denying the inevitability of failures robs you of your power to control and contain them. Once you accept that failures will happen, you have the ability to design your system's reaction to specific failures. Just as auto engineers create *crumple zones*—areas designed to protect passengers by failing first—you can

create safe failure modes that contain the damage and protect the rest of the system. This sort of self-protection determines the whole system's resilience.

Chiles calls these protections "crackstoppers." Like building crumple zones to absorb impacts and keep car passengers safe, you can decide what features of the system are indispensable and build in failure modes that keep cracks away from those features. If you do not design your failure modes, then you'll get whatever unpredictable—and usually dangerous—ones happen to emerge.

## Stopping Crack Propagation

Let's see how the design of failure modes applies to the grounded airline from before. The airline's Core Facilities project had not planned out its failure modes. The crack started at the improper handling of the 64/([FHSW] LR M) it could have been stopped at many other points. Let's look at some examples, from low-level detail to high-level architecture.

Because the pool was configured to block requesting threads when no resources were available, it eventually tied up all request-handling threads. (This happened independently in each application server instance.) The pool could have been configured to create more connections if it was exhausted. It also could have been configured to block callers for a limited time, instead of blocking forever when all connections were checked out. Either of these would have stopped the crack from propagating.

At the next level up, a problem with one call in CF caused the calling applications on other hosts to fail. Because CF exposed its services as Enterprise JavaBeans (EJBs), it used RMI. By default, RMI calls will never time out. In other words, the callers blocked waiting to read their responses from CF's EJBs. The first twenty callers to each instance received exceptions: a 64/([FHSWLRQ wrapped in an ,QYRFD WURWFHSWWRAPped in a 5HPRW ## SWITEN De precise. After that, the calls started blocking.

The client could have been written to set a timeout on the RMI sockets. For example, it could have installed a socket factory that calls 68 HWW VHWF6HRFXW on all new sockets it creates. At a certain point in time, CF could also have decided to build an HTTP-based web service instead of EJBs. Then the client could set a timeout on its HTTP requests. The clients might also have written their calls so the blocked threads could be jettisoned, instead of having the request-handling thread make the external integration call. None of these were done, so the crack propagated from CF to all systems that used CF.

At a still larger scale, the CF servers themselves could have been partitioned into more than one service group. That would have kept a problem within

one of the service groups from taking down all users of CF. (In this case, all the service groups would have cracked in the same way, but that would not always be the case.) This is another way of stopping cracks from propagating into the rest of the enterprise.

Looking at even larger architecture issues, CF could've been built using request/reply message queues. In that case, the caller would know that a reply might never arrive. It would have to deal with that case as part of handling the protocol itself. Even more radically, the callers could have been searching for flights by looking for entries in a tuple space that matched the search criteria. CF would have to have kept the tuple space populated with flight records. The more tightly coupled the architecture, the greater the chance this coding error can propagate. Conversely, the less-coupled architectures act as shock absorbers, diminishing the effects of this error instead of amplifying them.

Any of these approaches could have stopped the 64/([FHSW]pRD])em from spreading to the rest of the airline. Sadly, the designers had not considered the possibility of "cracks" when they created the shared services.

### Chain of Failure

Underneath every system outage is a chain of events like this. One small issue leads to another, which leads to another. Looking at the entire chain of failure after the fact, the failure seems inevitable. If you tried to estimate the probability of that exact chain of events occurring, it would look incredibly improbable. But it looks improbable only if you consider the probability of each event independently. A coin has no memory; each toss has the same probability, independent of previous tosses. The combination of events that caused the failure is not independent. A failure in one point or layer actually increases the probability of other failures. If the database gets slow, then the application servers are *more* likely to run out of memory. Because the layers are coupled, the events are not independent.

Here's some common terminology we can use to be precise about these chains of events:

Fault A condition that creates an incorrect internal state in your software. A fault may be due to a latent bug that gets triggered, or it may be due to an unchecked condition at a boundary or external interface.

*Error* Visibly incorrect behavior. When your trading system suddenly buys ten billion dollars of Pokemon futures, that is an error.

Failure An unresponsive system. When a system doesn't respond, we say it has failed. Failure is in the eye of the beholder...a computer may have the power on but not respond to any requests.

Triggering a fault opens the crack. Faults become errors, and errors provoke failures. That's how the cracks propagate.

At each step in the chain of failure, the crack from a fault may accelerate, slow, or stop. A highly complex system with many degrees of coupling offers more pathways for cracks to propagate along, more opportunities for errors.

Tight coupling accelerates cracks. For instance, the tight coupling of EJB calls allowed a resource exhaustion problem in CF to create larger problems in its callers. Coupling the request-handling threads to the external integration calls in those systems caused a remote problem to turn into downtime.

One way to prepare for every possible failure is to look at every external call, every I/O, every use of resources, and every expected outcome and ask, "What are all the ways this can go wrong?" Think about the different types of impulse and stress that can be applied:

- What if it can't make the initial connection?
- What if it takes ten minutes to make the connection?
- What if it can make the connection and then gets disconnected?
- What if it can make the connection but doesn't get a response from the other end?
- What if it takes two minutes to respond to my query?
- What if 10,000 requests come in at the same time?
- What if the disk is full when the application tries to log the error message about the 64/([FHSWtlkat] happened because the network was bogged down with a worm?

That's just the beginning of everything that can go wrong. The exhaustive brute-force approach is clearly impractical for anything but life-critical systems or Mars rovers. What if you actually have to deliver in this decade?

Our community is divided about how to handle faults. One camp says we need to make systems fault-tolerant. We should catch exceptions, check error codes, and generally keep faults from turning into errors. The other camp says it's futile to aim for fault tolerance. It's like trying to make a fool-proof device: the universe will always deliver a better fool. No matter what faults

you try to catch and recover from, something unexpected will always occur. This camp says "let it crash" so you can restart from a known good state.

Both camps agree on two things, though. Faults will happen; they can never be completely prevented. And we must keep faults from becoming errors. You have to decide for your system whether it's better to risk failure or errors—even while you try to prevent failures *and* errors. We'll look at some patterns that let you create shock absorbers to relieve those stresses.

## Wrapping Up

Every production failure is unique. No two incidents will share the precise chain of failure: same triggers, same fracture, same propagation. Over time, however, patterns of failure do emerge. A certain brittleness along an axis, a tendency for *this* problem to amplify *that* way. These are the stability antipatterns. Chapter 4, *Stability Antipatterns*, on page 31, deals with these patterns of failure.

If there are systematic patterns of failure, you might imagine that some common solutions would apply. You would be correct. Chapter 5, Stability Patterns, on page 91, deals with design and architecture patterns to defeat the antipatterns. These patterns cannot prevent cracks in the system. Nothing can. Some set of conditions will always trigger a crack. But these patterns stop cracks from propagating. They help contain damage and preserve partial functionality instead of allowing total failures.

First, the bad news. We must travel through the valley of shadows before we can reach the plateau of enlightenment. In other words, it's time to look at the antipatterns that will kill your systems.
