# Chapter 12: Case Study: Waiting for Godot

It isn't enough to write the code. Nothing is done until it runs in production. Sometimes the path to production is a smooth and open highway. Other times, especially with older systems, it's a muddy track festooned with potholes, bandits, and checkpoints with border guards. This was one of the bad ones.

I turn my grainy eyes toward the clock on the wall. The hands point to 1:17 a.m. I'd swear time has stopped. It has always been 1:17. I've seen enough film noir that I expect a fly to crawl across the face of the clock. There is no fly. Even the flies are asleep now. On the Polycom, someone is reporting status. It's a DBA. One of the SQL scripts didn't work right, but he "fixed" it by running it under a different user ID.

The wall clock doesn't mean much right now. Our Lamport clock is still stuck a little before midnight. The playbook has a row that says SQL scripts finish at  $11:50~\rm p.m.$  We're still on the SQL scripts, so logically we're still at  $11:50~\rm p.m.$  Before dawn, we need our playbook time and solar time to converge in order for this deployment to succeed.

The first row in the playbook started yesterday afternoon with a round of status reports from each area: dev, QA, content, merchants, order management, and so on. Somewhere on the first page of the playbook we had a go/no-go meeting at 3 p.m. Everyone gave the deployment a go, although QA said that they hadn't finished testing and might still find a showstopper. After the go/no-go meeting, an email went out to the business stakeholders, announcing that the deployment would go forward. That email is their cue to go home, eat dinner at four in the afternoon, and get some sleep. We need them to get up at 1 a.m. to "smoke test" the new features. That's our UAT window: 1 to 3 a.m.

It's 1:17 and the business stakeholders are awake and waiting to do their thing. I'm waiting to do my thing. When we get to about 12:40 in the playbook

I run a script. I don't know how long I'll have to wait, but somehow I'm sure the clock will still say 1:17. Until then, I watch some numbers on a graph. In a release a couple of years ago, those numbers went the wrong way. So now we watch them. I know the code that triggered the problem was rewritten long ago. Nothing to be done. But the playbook calls for us to monitor those numbers and so we do. The release commander will sometimes ask what those numbers are.

Two days ago, we started reviewing and updating the playbook. We have a process for updating the process. The release commander walks through the whole thing row by row, and we confirm each row or update them for this particular release. Sometimes there are more steps, sometimes fewer. Different releases affect different features, so we need different people available to debug. Each review meeting takes two or three hours.

Around the long conference table, more than twenty heads are bowed over their laptops. They look like they are praying to the Polycoms: "Please say it worked." An equal number of people are dialed in to the same conference bridge from four locations around the world. In total, this release will consume more than forty of us over a 24-hour period. Most of the operations team members are here. The remainder are asleep so that they can be fresh to fix leftover problems in the morning. A while back we had an operator error that we blamed on fatigue. So now there's a step in the playbook for the "B team" to go home and sleep. I tried to sneak in rows from Sandra Boynton's *Going to Bed Book*—

"The day is done, they say goodnight.

And somebody turns off the light."

But the playbook has no room for whimsy.

Our Lamport clock jumps forward while I'm not looking. The release commander tells Sys Ops to update symlinks. That's my cue: I am Sys Ops. It's not as cool as saying, "I am Iron Man." The term "DevOps" won't exist for another year, and in a different galaxy than this conference room. I tap Enter in my PuTTY window logged in to the jumphost—the only machine the others will accept SSH connections from. My script does three things on each machine. It updates a symbolic link to point to the new code drop, runs the JSP precompiler, and starts the server processes. A different script placed the code on the servers hours ago.

Now my turn is done until we finish UAT. Some energy gets generated when a voice emanates from the Polycom, informing us, "It didn't work." That may

be the least helpful bug report ever received. It turns out the person was testing a page that wasn't part of this release and had a known bug from two or three years back.

I don't deal with boredom very well. After some fruitful contemplation on the nature of the buzz produced by fluorescent lights (and that the pitch must be different in countries on 50 hertz power), I start to wonder how much this deployment costs. A little napkin math surprises me enough that I make a spreadsheet. The size of the army times one day. I don't know the cost structure, but I can guess that \$100 per hour per person is not too far off. Add in some lost sales while the site is "gone fishing," but not a lot because we're offline during a slow part of the day. It's about \$100,000 to run this deployment. We do this four to six times a year.

Years later, I would witness a deployment at the online retailer Etsy. An investor was visiting, and as a routine part of the visit the company had him push the button to run its "deployinator." The investor seemed pleased but not impressed. I felt a kind of bubbling hysteria. I needed to grab him by the collar. Didn't he understand what that meant? How amazing it was? At the same time, I had a deep sense of loss: all that time in the deployment army. All that wasted potential. The wasted humanity! Using people as if they were bots. Disrupting lives, families, sleep patterns…it was all such a waste.

In the end, our deployment failed UAT. Some feature had passed QA because the data in the QA environment didn't match production. (Stop me if you've heard this one before.) Production had extra content that included some JavaScript to rewrite part of a page from a third party and it didn't work with the new page structure. The clock on the wall claimed it was around 5 a.m. when we finished the rollback procedure. That afternoon, we started planning the second attempt scheduled for two days hence.

You may have a deployment army of your own. The longer your production software has existed the more likely it is. In the following chapters, we'll look at the forces that lead to this antipattern. We'll also see how to climb out of the pit of despair. As you'll see, making deployments faster and more routine has an immediate financial benefit. More than that, though, a virtuous cycle kicks in that gives you new superpowers. Best of all, you can stop wasting human potential on jobs that should be scripts.
