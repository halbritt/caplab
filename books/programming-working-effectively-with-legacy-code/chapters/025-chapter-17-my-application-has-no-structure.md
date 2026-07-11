<span id="page-237-1"></span>
<span id="page-237-0"></span>
# Chapter 17: My Application Has No Structure


Long-lived applications tend to sprawl. They might have started out with a well-thought-out architecture, but over the years, under schedule pressure, they can get to the point at which nobody really understands the complete structure. People can work for years on a project and not have any idea where new features are intended to go; they just know the hacks that have been placed in the system recently. When they add new features, they go to the "hack points" because those are the areas that they know best.

There is no easy remedy for this sort of thing, and the urgency of the situation varies widely. In some cases, programmers run up against a wall. It's difficult to add new features, and that brings the entire organization into crisis mode. People are charged with the task of figuring out whether it would be better to rearchitect or rewrite the system. In other organizations, the system limps along for years. Yes, it takes longer than it should to add new features, but that is just considered the price of doing business. Nobody knows how much better it could be or how much money is being lost because of poor structure.

When teams aren't aware of their architecture, it tends to degrade. What gets in the way of this awareness?

- The system can be so complex that it takes a long time to get the big picture.
- The system can be so complex that there is no big picture.
- The team is in a very reactive mode, dealing with emergency after emergency so much that they lose sight of the big picture.

Traditionally, many organizations have used the role of architect to solve these problems. Architects are usually charged with the task of working out the big picture and making decisions that preserve the big picture for the team. That can work, but there is one strong caveat. An architect has to be out in the **My Application Has No Structure**

<span id="page-238-1"></span>![](../assets/_page_238_Picture_1.jpeg)

team, working with the members day to day, or else the code diverges from the big picture. There are two ways this can happen: Someone could be doing something inappropriate in the code or the big picture itself could need to be modified. In some of the worst situations I've encountered with teams, the architect of a group has a completely different view of the system than the programmers. Often this happens because the architect has other responsibilities and can't get into the code or can't communicate with the rest of the team often enough to really know what is there. As a result, communication breaks down across the organization.

<span id="page-238-0"></span>The brutal truth is that architecture is too important to be left exclusively to a few people. It's fine to have an architect, but the key way to keep an architecture intact is to make sure that everyone on the team knows what it is and has a stake in it. Every person who is touching the code should know the architecture, and everyone else who touches the code should be able to benefit from what that person has learned. When everyone is working off of the same set of ideas, the overall system intelligence of the team is amplified. If you have, say, a team of 20 and only 3 people know the architecture in detail, either those 3 have to do a lot to keep the other 17 people on track or the other 17 people just make mistakes caused by unfamiliarity with the big picture.

How can we get a big picture of a large system? There are many ways to do this. The book *Object-Oriented Reengineering Patterns*, by Serge Demeyer, Stephane Ducasse, and Oscar M. Nierstrasz (Morgan Kaufmann Publishers, 2002), contains a catalog of techniques that deal with just this issue. Here I describe several others that are rather powerful. If you practice them often on a team, they will help keep architectural concerns alive in the team—and that's perhaps the most important thing you can do to preserve architecture. It is hard to pay attention to something that you don't think about often.

## Telling the Story of the System

When I work with teams, I often use a technique that I call "telling the story of the system." To do it well, you need at least two people. One person starts off by asking another, "What is the architecture of the system?" Then the other person tries to explain the architecture of the system using only a few concepts, maybe as few as two or three. If you are the person explaining, you have to pretend that the other person knows nothing about the system. In only a few sentences, you have to explain what the pieces of the design are and how they interact. After you say those few sentences, you have articulated what you feel

<span id="page-239-0"></span>are the most essential things about the system. Next, you pick the next most important things to say about the system. You keep going until you've said just about everything important about the core design of the system.

When you start to do this, you'll notice an odd feeling. To really convey the system architecture that briefly, you have to simplify. You might say, "The gateway gets rule sets from the active database," but as you say that, part of you might be screaming, "No! The gateway gets rule sets from the active database, but it also gets them from the current working set." When you say the simpler thing, it kind of feels like you are lying; you just aren't telling the whole story. But you are telling a simpler story that describes an easier-to-understand architecture. For instance, why does the gateway have to get rule sets from more than one place? Wouldn't it be simpler if it was unified?

Pragmatic considerations often keep things from getting simple, but there is value in articulating the simple view. At the very least, it helps everyone understand what would've been ideal and what things are there as expediencies. The other important thing about this technique is that it really forces you to think about what is important in the system. What are the most important things to communicate?

Teams can go only so far when the system they work on is a mystery to them. In an odd way, having a simple story of how a system works just serves as a roadmap, a way of getting your bearing as you search for the right places to add features. It can also make a system a lot less scary.

On your team, tell the story of the system often, just so that you share a view. Tell it in different ways. Trade off whether one concept is more important than another. As you consider changes to the system, you'll notice that some changes fall more in line with the story. That is, they make the briefer story feel like less of a lie. If you have to choose between two ways of doing something, the story can be a good way to see which one will lead to an easier-tounderstand system.

Here is an example of this sort of story telling in action. Here's a session discussing JUnit. It does assume that you know a little bit about the architecture of JUnit. If you don't, take a little while to look at JUnit's source code. You can download it from [www.junit.org.](https://www.junit.org)

### What is the architecture of JUnit?

JUnit has two primary classes. The first is called Test, and the other is called TestResult. Users create tests and run them, passing them a TestResult. When a test fails, it tells the TestResult about it. People can then ask the TestResult for all of the failures that have occurred.

![](../assets/_page_240_Picture_1.jpeg)

#### Let's list the simplifications:

- 1. There are many other classes in JUnit. I'm saying that Test and TestResult are primary only because I think so. To me, their interaction is the core interaction in the system. Others might have a different, equally valid view of the architecture.
- 2. Users don't create test objects. Test objects are created from test case classes via reflection.
- 3. Test isn't a class; it's an interface. The tests that run in JUnit are usually written in subclasses of a class named TestCase, which implements Test.
- 4. People generally don't ask TestResults for failures. TestResults register listeners, which are notified whenever a TestResult receives information from a test.
- 5. Tests report more than failures: They report the number of tests run and the number of errors. (Errors are problems that occur in the test that aren't explicitly checked for. Failures are failed checks.)

Do these simplifications give us any insight into how JUnit could be simpler? A little. Some simpler xUnit testing frameworks make Test a class and drop TestCase entirely. Other frameworks merge errors and failures so that they are reported the same way.

Back to our story. *Is that all?*

> No. Tests can be grouped into objects called suites. We can run a suite with a test result just like a single test. All of the tests inside it run and tell the test result when they fail.

#### What simplifications do we have here?

- 1. TestSuites do more than just hold and run a set of tests. They also create instances of TestCase-derived classes via reflection.
- 2. There is another simplification, sort of a left over from the first one. Tests don't actually run themselves. They pass themselves to the TestResult class, which, in turn, calls the test-execution method back on the test itself. This back and forth happens at a rather low level. Thinking about it the simple way is kind of convenient. It is a bit of a lie, but it is actually the way JUnit used to be when it was a little simpler.

*Is that all?*

No. Actually, Test is an interface. There is a class called TestCase that implements Test. Users subclass TestCase and then write their tests as public void methods that start with the word test in their subclass. The TestSuite class uses reflection to build up a group of tests that can be run in a single call to TestSuite's run method.

We can go further, but what I've shown so far gives a sense of the technique. We start out by making a brief description. When we simplify and rip away detail to describe a system, we are really abstracting. Often when we force ourselves to communicate a very simple view of a system, we can find new abstractions.

If a system isn't as simple as the simplest story we can tell about it, does that mean that it's bad? No. Invariably, as systems grow, they get more complicated. The story gives us guidance.

Suppose that we were going to add a new feature to JUnit. We want to generate a report of all the tests that don't call any assertions when we run them. What options do we have given what was described in JUnit?

One option is to add a method to the TestCase class called buildUsageReport that runs each method and then builds up a report of all of the methods that don't call an assert method. Would that be a good way of adding this feature? What would it do to our story? Well, it would add another little "lie of omission" from our briefest description of the system:

JUnit has two primary classes. The first is called Test, and the other is called TestResult. Users create tests and run them, passing along a TestResult. When a test fails, it tells the TestResult about it. People can then ask the TestResult for all of the failures that have occurred.

It seems that Tests now have this completely different responsibility: generating reports, which we never mention.

What if we went about adding the feature in a different way? We could alter the interaction between TestCase and TestResult so that TestResult gets a count of the number of assertions run whenever a test runs. Then we can make a reportbuilding class and register it with TestResult as a listener. How does that impact the story of the system? It could be a good reason to generalize it a little. Tests don't just tell TestResults about the number of failures; they also tell them about the number of errors, the number of tests run, and the number of assertions run. We could change our brief story to this:

<span id="page-242-1"></span>JUnit has two primary classes. The first is called Test, and the other is called TestResult. Users create tests and run them, passing them a TestResult. When a test runs, it passes information about the test run to the TestResult. People can then ask the TestResult for **information** about all of the test runs.

Is that better? Frankly, I like the original, the version that described recording failures. To me, it is one of the core behaviors of JUnit. If we change the code so that TestResults record the number of assertions run, we'd still be lying a bit, but we're already glossing over the other information that we send from tests to test results. The alternative, putting the responsibility for running a bunch of cases and building a report from them on TestCase, would be a bolder lie: We aren't talking about this additional responsibility of TestCase at all. We're better off having tests report the number of assertions run as they execute. Our first story is generalized a little bit more but at least it is still substantially true. That means that our changes are falling more in line with the architecture of the system.

<span id="page-242-0"></span>**Naked CRC**

### Naked CRC

In the early days of object orientation, many people struggled with the issue of design. It's hard to get used to object orientation when most of your programming experience is in the use of procedural languages. Simply put, the way that you think about your code is different. I remember the first time someone tried to show me an object-oriented design on a piece of paper. I looked at all the shapes and lines and heard the description, but the question that I kept wanting to ask was "Where's main()? Where is the entry point for all of these new object things?" I was bewildered for a little while, but then it started to click. The problem wasn't just mine, though. It seemed like most of the industry was struggling with the same issues at roughly the same time. Frankly, every day people new to the industry confront these issues when they encounter objectoriented code for the first time.

In the 1980s, Ward Cunningham and Kent Beck were dealing with this issue. They were trying to help people start to think about design in terms of objects. At the time, Ward was using a tool named Hypercard, which allows you to create cards on a computer display and form links among them. Suddenly, the insight was there. Why not use real index cards to represent classes? It would <span id="page-243-0"></span>make them tangible and easy to discuss. Should we talk about the Transaction class? Sure, here is its card—on it we have its responsibilities and collaborators.

CRC stands for Class, Responsibility, and Collaborations. You mark up each card with a class name, its responsibilities, and a list of its collaborators (other classes that this class communicates with). If you think that a responsibility doesn't belong on a particular class, cross it out and write it on another class card, or create another class card altogether.

Although CRC became rather popular for a while, eventually there was a large push toward diagrams. Nearly everyone teaching OO on the planet had their own notation for classes and relationships. Eventually, there was a large multiyear effort to consolidate notations. UML was the result, and many people thought that ended any talk of how to design systems. People started to think that the notation was a method, that UML was a way of developing systems: Draw plenty of diagrams, and then write code afterward. It took a while for people to realize that although UML is a good notation for documenting systems, it's not the only way of working with the ideas that we use to build systems. At this point, I know that there is a much better way of communicating about design on a team. It's a technique that some testing friends of mine dubbed Naked CRC because it is just like CRC, except that you don't write on the cards. Unfortunately, it isn't all that easy to describe in a book. Here's my best attempt.

Several years ago, I met Ron Jeffries at a conference. He'd promised me that he would show me how he could explain an architecture using cards in a way that made the interactions rather vivid and memorable. Sure enough, he did. This is the way that it works. The person describing the system uses a set of blank index cards and lays them down on a table one by one. He or she can move the cards, point at them, or do whatever else is needed to convey the typical objects in the system and how they interact.

Here is an example, a description of an online voting system:

"Here's how the real-time voting system works. Here is a client session" (points at card).

**Naked CRC**

![](../assets/_page_244_Picture_0.jpeg)

#### **222** MY APPLICATION HAS NO STRUCTURE

"Each session has two connections, an incoming connection and an outgoing connection" (lays down each card on the original one and points at each, in turn).

![](../assets/_page_244_Picture_3.jpeg)

"When it starts up, a session is created on the server over here" (lays down the card on the right).

![](../assets/_page_244_Picture_5.jpeg)

**Naked CRC**

"Server sessions have two connections apiece also" (puts down the two cards representing the connections on the card on the right).

![](../assets/_page_244_Picture_9.jpeg)

![](../assets/_page_244_Picture_10.jpeg)

"When a server session comes up, it registers with the vote manager (lays down the card for the vote manager above the server session).

![](../assets/_page_244_Picture_12.jpeg)

![](../assets/_page_244_Picture_13.jpeg)

<span id="page-245-0"></span>"We can have many sessions on the server side" (puts down another set of cards for a new server session and its connections).

![](../assets/_page_245_Picture_3.jpeg)

"When a client votes, the vote is sent to the session on the server side" (motions with hands from one of the connections on the client-side session to a connection on a server-side session).

"The server session replies with an acknowledgment and then records the vote with the vote manager" (points from the server session back to the client session, and then points from that server session to the vote manager).

"Afterward, the vote manager tells each server session to tell its client session what the new vote count is" (points from the vote manager card to each server session, in turn).

I'm sure that this description is lacking something because I'm not able to move the cards around on the table or point at them the way I would if we were sitting at a table together. Still, this technique is pretty powerful. It makes pieces of a system into tangible things. You don't have to use cards; anything that is handy is fine. The key is that you are able to use motion and position to show how parts of the system interact. Often those two things can make involved scenarios easier to grasp. For some reason, these carding sessions make designs more memorable also.

There are just two guidelines in Naked CRC:

- 1. Cards represent instances, not classes.
- 2. Overlap cards to show a collection of them.

**Naked CRC**

<span id="page-246-1"></span>
<span id="page-246-0"></span>
## Conversation Scrutiny

In legacy code, it's tempting to avoid creating abstractions. When I'm looking at four or five classes that have about a thousand lines of code apiece, I'm not thinking about adding new classes as much as I'm trying to figure out what has to change.

Because we are so distracted when we're trying to figure out these things, often we miss things that can give us additional ideas. Here's an example. I was working with several members of a team once, and they were going through the exercise of making a large chunk of code executable from several threads. The code was rather complicated and there were several opportunities for deadlock. We realized that if we could guarantee that resources were locked in and unlocked in a particular order, we could avoid deadlock in the code. We started to look at how we could modify the code to enable this. All the while, we were talking about this new locking policy and figuring out how to maintain counts in arrays to enable it. When one of the other programmers started to write the policy code inline, I said, "Wait, we're talking about a locking policy, right? Why don't we create a class called LockingPolicy and maintain the counts in there? We can use method names that really describe what we are trying to do, and that will be clearer than code that bumps counts in an array."

The terrible thing is that the team wasn't inexperienced. There were some other very good-looking areas of the code base, but there is something mesmerizing about large chunks of procedural code: They seem to beg for more.

Listen to conversations about your design. Are the concepts you're using in conversation the same as the concepts in the code? I wouldn't expect them all to be. Software has to satisfy stronger constraints than just being easy to talk about, but if there isn't a strong overlap between conversation and code, it's important to ask why. The answer is usually a mixture of two things: The code hasn't been allowed to adapt to the team's understanding, or the team needs to understand it differently. In any case, being very tuned to the concepts people naturally use to describe the design is powerful. When people talk about design, they are trying to make other people understand them. Put some of that understanding in the code.

In this chapter, I've described a couple of techniques for uncovering and communicating the architecture of large existing systems. Many of the techniques are also perfectly good ways of working out the design of new systems. Design is design, regardless of when it happens in the development cycle. One

**Conversation Scrutiny**

### CONVERSATION SCRUTINY **225**

![](../assets/_page_247_Picture_1.jpeg)

of the worst mistakes a team can make is it to feel that design is over at some point in development. If design is "over" and people are still making changes, chances are good that new code will appear in poor places, and classes will bloat because no one feels comfortable introducing new abstraction. There is no surer way to make a legacy system worse.

> **Conversation Scrutiny**

![](../assets/_page_248_Picture_0.jpeg)
