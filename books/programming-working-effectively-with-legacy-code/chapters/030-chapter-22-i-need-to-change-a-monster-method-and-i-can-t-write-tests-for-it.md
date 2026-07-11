<span id="page-311-1"></span>
<span id="page-311-0"></span>
# Chapter 22: I Need to Change a Monster Method and I Can't Write Tests for It


One of the hardest things about working in legacy code is dealing with large methods. In many cases, you can avoid refactoring long methods by using the *Sprout Method (59)* and *Sprout Class (63)* techniques. Even when you are able to avoid it, though, it's just a shame that you have to. Long methods are quagmires in a code base. Whenever you have to change them, you have to go back and attempt to understand them again, and then you have to make your changes. Often that takes longer than it would if the code was cleaner.

Long methods are a pain, but monster methods are worse. A monster method is a method that is so long and so complex that you really don't feel comfortable touching it. Monster methods can be hundreds or thousands of lines long, with enough scattered indentation to make navigation nearly impossible. When you have monster methods you're tempted to print them on a couple of yards of continuous-feed paper and lay them out in a hallway so that you and your coworkers can figure them out.

I was once on the road at a meeting, and as we were walking back to our hotel rooms, a friend of mine said, "Hey, you've got to see this." He went into his room and pulled out his laptop and showed me a method that went on for more than a thousand lines. My friend knew that I'd been studying refactoring and said, "How in the world would you refactor this?" We started thinking it through. We knew that testing was key, but where do you even begin with such a big method?

This chapter outlines what I've learned since then.

**I Need to Change a Monster Method**

<span id="page-312-1"></span><span id="page-312-0"></span>![](../assets/_page_312_Picture_1.jpeg)

## Varieties of Monsters

Monster methods come in a couple of varieties. These aren't necessarily distinct types. Methods out in the field are kind of like platypuses—they look like mixtures of several types.

### Bulleted Methods

A bulleted method is a method with nearly no indentation. It is just a sequence of code chunks that reminds you of a bulleted list. Some of the code in the chunks might be indented, but the method itself isn't dominated by indentation. When you look at a bulleted method and squint your eyes, you see something like Figure 22.1.

This is the general form of a bulleted method. If you are lucky, someone will have put extra lines between the sections or comments to show you that they do somewhat distinct things. In an ideal world, you'd be able to just extract a method for each of the sections, but often the methods don't refactor easily that way. The space between the sections is a little bit deceptive because often temporary variables are declared in one section and used in the next. Breaking down the method often isn't as easy as just copying and pasting out code. Despite this, bulleted methods are a little less intimidating than the other varieties, mainly because that lack of wild indentation allows us to keep our bearings.

**Varieties of Monsters**

```
void Reservation::extend(int additionalDays)
 int status = RIXInterface::checkAvailable(type, location, startingDate);
 int identCookie = -1;
 switch(status) {
 case NOT_AVAILABLE_UPGRADE_LUXURY:
 identCookie = RIXInterface::holdReservation(Luxury,location,startingDate, 
 additionalDays +dditionalDays);
 break;
 case NOT_AVAILABLE_UPGRADE_SUV:
 {
 int theDays = additionalDays + additionalDays;
 if (RIXInterface::getOpCode(customerID) != 0)
 theDays++;
 identCookie = RIXInterface::holdReservation(SUV,location,startingDate, theDays);
 }
 break;
 case NOT_AVAILABLE_UPGRADE_VAN:
 identCookie = RIXInterface::holdReservation(Van,
 location,startingDate, additionalDays + additionalDays);
 break;
 case AVAILABLE:
 default:
 RIXInterface::holdReservation(type,location,startingDate);
 break;
 }
 if (identCookie != -1 && state == Initial) {
 RIXInterface::waitlistReservation(type,location,startingDate);
 }
 Customer c = res_db.getCustomer(customerID);
 if (c.vipProgramStatus == VIP_DIAMOND) {
 upgradeQuery = true;
 }
 if (!upgradeQuery)
 RIXInterface::extend(lastCookie, days + additionalDays);
 else {
 RIXInterface::waitlistReservation(type,location,startingDate);
 RIXInterface::extend(lastCookie, days + additionalDays +1);
 }
 ...
```

**Figure 22.1** *Bulleted method.*

**Varieties of Monsters**

<span id="page-314-0"></span>![](../assets/_page_314_Picture_1.jpeg)

#### Snarled Methods

A snarled method is a method dominated by a single large, indented section. The simplest case is a method that has one large conditional statement, as in Figure 22.2.

```
Reservation::Reservation(VehicleType type, int customerID, long startingDate, int days, XLocation l)
: type(type), customerID(customerID), startingDate(startingDate), days(days), lastCookie(-1),
state(Initial), tempTotal(0)
 location = l;
 upgradeQuery = false;
 if (!RIXInterface::available()) {
 RIXInterface::doEvents(100);
 PostLogMessage(0, 0, "delay on reservation creation");
 int holdCookie = -1;
 switch(status) {
 case NOT_AVAILABLE_UPGRADE_LUXURY:
 holdCookie = RIXInterface::holdReservation(Luxury,l,startingDate);
 if (holdCookie != -1) {
 holdCookie |= 9;
 }
 break;
 case NOT_AVAILABLE_UPGRADE_SUV:
 holdCookie = RIXInterface::holdReservation(SUV,l,startingDate);
 break;
 case NOT_AVAILABLE_UPGRADE_VAN:
 holdCookie = RIXInterface::holdReservation(Van,l,startingDate);
 break;
 case AVAILABLE:
 default:
 RIXInterface::holdReservation;
 state = Held;
 break;
 }
 }
```

**Figure 22.2** *Simple snarled method.*

But that sort of a snarl nearly has the same qualities as a bulleted method. The snarls that demand your full appreciation are methods with the form shown in Figure 22.3.

The best way to know whether you have a real snarl is to try to line up the blocks in a long method. If you start to feel vertigo, you've run into a snarled method.

**Varieties of Monsters**

```
Reservation::Reservation(VehicleType type, int customerID, long startingDate, int days, XLocation l)
: type(type), customerID(customerID), startingDate(startingDate), days(days), lastCookie(-1),
state(Initial), tempTotal(0)
 location = l;
 upgradeQuery = false;
 while(!RIXInterface::available()) {
 RIXInterface::doEvents(100);
 PostLogMessage(0, 0, "delay on reservation creation");
 int holdCookie = -1;
 switch(status) {
 case NOT_AVAILABLE_UPGRADE_LUXURY:
 holdCookie = 
 RIXInterface::holdReservation(Luxury,l,startingDate);
 if (holdCookie != -1) {
 if (l == GIG && customerID == 45) {
 // Special #1222
 while (RIXInterface::notBusy()) {
 int code = 
 RIXInterface::getOpCode(customerID);
 if (code == 1 || customerID > 0)) {
 PostLogMessage(1, 0, "QEX PID");
 for (int n = 0; n < 12; n++) {
 int total = 2000;
 if (state == Initial || state == Held)
 {
 total += getTotalByLocation(location);
 tempTotal = total;
 if (location == GIG && days > 2) 
 {
 if (state == Held)
 total += 30;
 }
 }
 RIXInterface::serveIDCode(n, total);
 }
 } else {
 RIXInterface::serveCode(customerID);
 }
 }
 }
 break;
 case NOT_AVAILABLE_UPGRADE_SUV:
 holdCookie = 
 RIXInterface::holdReservation(SUV,l,startingDate);
 break;
 case NOT_AVAILABLE_UPGRADE_VAN:
 holdCookie = 
 RIXInterface::holdReservation(Van,l,startingDate);
 break;
 case AVAILABLE:
 default:
 RIXInterface::holdReservation(type,l,startingDate);
 state = Held;
 break;
 }
 }
```

**Monsters Figure 22.3** *Very snarled method.*

Most methods are not purely bulleted or snarled, but something in between. Many snarls have long bulleted sections hidden deep in their nesting, but because they are nested it is hard to write tests that pin down their behavior. Snarls present unique challenges.

**Varieties of** 

<span id="page-316-1"></span><span id="page-316-0"></span>![](../assets/_page_316_Picture_1.jpeg)

When you are refactoring long methods, the presence or absence of a refactoring tool makes a difference. Nearly every refactoring tool supports the extract method refactoring because there is an incredible amount of leverage in that support. If a tool can extract methods for you safely, you don't need tests to verify your extractions. The tool does the analysis for you, and all that is left is learning how to use extractions to put a method into decent shape for further work.

When you don't have extract method support, cleaning up monster methods is more challenging. You often have to be more conservative because your work is bounded by the tests you can get in place.

## Tackling Monsters with Automated Refactoring Support

When you have a tool that extracts methods for you, you have to be clear about what it can and can't do for you. Most refactoring tools today do simple extract methods and a variety of other refactorings, but they don't handle all the auxiliary refactoring that people often want to do when they break up large methods. For instance, often we're tempted to reorder statements to group them for extraction. No current tool does the analysis needed to see whether reordering can be done safely. That's a shame because it can be a source of bugs.

To use refactoring tools effectively with large methods, it pays to make a series of changes solely with the tool and to avoid all other edits to the source. This might feel like refactoring with one hand behind your back, but it gives you a clean separation between changes that are known to be safe and changes that aren't. When you refactor like this, you should avoid even simple things, such as reordering statements and breaking apart expressions. If your tool supports variable renaming, that's great, but if it doesn't, put that off until later.

When doing automated refactoring without tests, use the tool exclusively. After a series of automated refactorings, you can often get tests in place that you can use to verify any manual edits that you make.

When you do your extractions, these should be your key goals:

- 1. To separate logic from awkward dependencies
- 2. To introduce seams that make it easier to get tests in place for more refactoring

**Tackling Monsters with Automated Refactoring Support**

```
Here is an example:
```

```
class CommoditySelectionPanel 
 ...
 public void update() {
 if (commodities.size() > 0
 && commodities.GetSource().equals("local")) {
 listbox.clear();
 for (Iterator it = commodities.iterator(); 
 it.hasNext(); ) {
 Commodity current = (Commodity)it.next();
 if (commodity.isTwilight() 
 && !commodity.match(broker))
 listbox.add(commodity.getView());
 }
 }
 ...
 }
 ...
```

In this method, a lot of things could be cleaned up. One of the odd things is that this sort of filtering work is happening on a panel class, something that should ideally just be responsible for display. Untangling this code is bound to be difficult. If we want to start writing tests against the method as it stands now, we could write them against the list box state, but that wouldn't move us too far along toward making the design better.

With refactoring support, we can start to name high-level pieces of the method and break dependencies at the same time. This is what the code would look like after a series of extractions.

```
class CommoditySelectionPanel 
 ...
 public void update() {
 if (commoditiesAreReadyForUpdate()) {
 clearDisplay();
 updateCommodities();
 }
 ...
 }
 private boolean commoditiesAreReadyForUpdate() {
 return commodities.size() > 0
 && commodities.GetSource().equals("local");
 }
```

**Tackling Monsters with Automated Refactoring Support**

<span id="page-318-0"></span>![](../assets/_page_318_Picture_1.jpeg)

```
 private void clearDisplay() {
 listbox.clear();
 }
 private void updateCommodities() {
 for (Iterator it = commodities.iterator(); it.hasNext(); ) {
 Commodity current = (Commodity)it.next();)
 if (singleBrokerCommodity(commodity)) {
 displayCommodity(current.getView());
 }
 }
 }
 private boolean singleBrokerCommodity(Commodity commodity) {
 return commodity.isTwilight() && !commodity.match(broker);
 }
 private void displayCommodity(CommodityView view) {
 listbox.add(view);
 }
 ...
}
```

Frankly, the code in update doesn't look that different structurally; it is still just an if-statement with some work inside of it. But the work has been delegated to methods now. The update method looks like a skeleton of the code that it came from. And what about those names? They seem a little hokey, don't they? But they are a good starting point. At the very least, they allow the code to communicate at a higher level, and they introduce seams that allow us to break dependencies. We can *Subclass and Override Method (401)* to sense through displayCommodity and clearDisplay. After we've done that, we can look atthe possibility of making a display class and moving those methods over it, using those tests as leverage. In this case, however, it would be more appropriate to see if we can move update and updateCommodities to another class and leave clearDisplay and displayCommodity here so that we can take advantage of the fact that this class is a panel, a display. We can rename methods later as they settle into place. After additional refactoring, our design can end up looking something like Figure 22.4.

**Tackling Monsters with Automated Refactoring Support**

![](../assets/_page_318_Figure_5.jpeg)

**Figure 22.4** *Logic class extracted from* CommoditySelectionPanel*.*

<span id="page-319-1"></span><span id="page-319-0"></span>The key thing to remember when you use an automated tool to extract methods is that you can do a lot of coarse work safely and handle the details after you get other tests in place. Don't be too concerned about methods that seem like they don't fit the class. Often they point toward the need to extract a new class later. See Chapter 20, *This Class Is Too Big and I Don't Want It to Get Any Bigger*, for more ideas on how to do this.

## The Manual Refactoring Challenge

When you have automated refactoring support, you don't have to do anything special to start breaking down large methods. Good refactoring tools check each refactoring that you attempt and disallow ones that they can't perform safely. But when you don't have a refactoring tool, correctness is something that you have to work to maintain, and tests are the strongest tool around.

Monster methods make testing, refactoring, and feature addition very difficult. If you are able to create instances of the class housing the method in a test harness, you can attempt to devise some set of test cases that will give you confidence as you break down the method. If the logic in the method is particularly complex, this can be a nightmare. Fortunately, in those cases, we can use a couple of techniques. Before we look at them, though, let's look at what can go wrong when we extract methods.

Here is a little list. It doesn't contain every possible error, but it has the most common ones:

- 1. We can forget to pass a variable into the extracted method. Often the compiler tells us about the missing variable (unless it has the same name as an instance variable), but we could just think that it needs to be a local variable and declare it in the new method.
- 2. We could give the extracted method a name that hides or overrides a method with the same name in a base class.
- 3. We could make a mistake when we pass in parameters or assign return values. We could do something really silly, such as return the wrong value. More subtly, we could return or accept the wrong types in the new method.

Quite a few things can go wrong. The techniques in this section can help make extraction less risky when we don't have tests in place.

<span id="page-320-0"></span>![](../assets/_page_320_Picture_1.jpeg)

### Introduce Sensing Variable

We might not want to add features to production code when we're refactoring it, but that doesn't mean that we can't add any code. Sometimes it helps to add a variable to a class and use it to sense conditions in the method that we want to refactor. When we've done the refactoring that we need to do, we can get rid of that variable, and our code will be in a clean state. This is called *Introduce Sensing Variable*. Here is an example. We start with a method on a Java class named DOMBuilder. We want to clean it up, but, unfortunately, we don't have a refactoring tool:

```
public class DOMBuilder
{
 ...
 void processNode(XDOMNSnippet root, List childNodes)
 {
 if (root != null) {
 if (childNodes != null)
 root.addNode(new XDOMNSnippet(childNodes));
 root.addChild(XDOMNSnippet.NullSnippet);
 }
 List paraList = new ArrayList();
 XDOMNSnippet snippet = new XDOMNReSnippet();
 snippet.setSource(m_state);
 for (Iterator it = childNodes.iterator();
 it.hasNext();) {
 XDOMNNode node = (XDOMNNode)it.next();
 if (node.type() == TF_G || node.type() == TF_H ||
 (node.type() == TF_GLOT && node.isChild())) {
 paraList.addNode(node);
 }
 ...
 }
 ... 
 }
 ...
}
```

In this example, it seems like a lot of the work in the method happens to an XDOMNSnippet. That means that we should be able to write whatever tests we need by passing different values as arguments to this method. But, in actuality, a lot of work happens tangentially, things that can be sensed in only a very indirect way. In a situation like this, we can introduce sensing variables to aid our work; we could introduce an instance variable to see that a node is added to the paraList when it has the proper node type.

```
public class DOMBuilder
{
```

```
 public boolean nodeAdded = false;
 ...
 void processNode(XDOMNSnippet root, List childNodes)
 {
 if (root != null) {
 if (childNodes != null)
 root.addNode(new XDOMNSnippet(childNodes));
 root.addChild(XDOMNSnippet.NullSnippet);
 }
      List paraList = new ArrayList();
 XDOMNSnippet snippet = new XDOMNReSnippet();
 snippet.setSource(m_state);
 for (Iterator it = childNodes.iterator(); 
 it.hasNext(); ) {
 XDOMNNode node = (XDOMNNode)it.next();
 if (node.type() == TF_G || node.type() == TF_H || 
 (node.type() == TF_GLOT && node.isChild())) {
 paraList.add(node);
 nodeAdded = true;
 }
 ...
 }
 ...
 }
 ...
```

With that variable in place, we still have to engineer the input to produce a case that covers that condition. When we do, we can extract that piece of logic, and our tests should still pass.

Here is a test that shows us that we add a node when the node type is TF\_G:

```
void testAddNodeOnBasicChild()
 DOMBuilder builder = new DomBuilder();
 List children = new ArrayList();
 children.add(new XDOMNNode(XDOMNNode.TF_G));
 Builder.processNode(new XDOMNSnippet(), children);
 assertTrue(builder.nodeAdded);
```

Here is a test that shows that we don't add a node when we have the wrong node type:

```
void testNoAddNodeOnNonBasicChild()
 DOMBuilder builder = new DomBuilder();
 List children = new ArrayList();
 children.add(new XDOMNNode(XDOMNNode.TF_A));
 Builder.processNode(new XDOMNSnippet(), children);
```

![](../assets/_page_322_Picture_1.jpeg)

```
 assertTrue(!builder.nodeAdded);
}
```

With these tests in place, we should feel better about extracting the body of the condition that determines whether nodes are added. We are copying the entire condition, and the test shows that the node was added when the condition was exercised.

```
public class DOMBuilder
{
 void processNode(XDOMNSnippet root, List childNodes)
 {
 if (root != null) {
 if (childNodes != null)
 root.addNode(new XDOMNSnippet(childNodes));
 root.addChild(XDOMNSnippet.NullSnippet);
 }
 List paraList = new ArrayList();
 XDOMNSnippet snippet = new XDOMNReSnippet();
 snippet.setSource(m_state);
 for (Iterator it = childNodes.iterator();
 it.hasNext();) {
 XDOMNNode node = (XDOMNNode)it.next();
 if (isBasicChild(node)) {
 paraList.addNode(node);
 nodeAdded = true;
 }
 ...
 }
 ... 
 }
 private boolean isBasicChild(XDOMNNode node) {
 return node.type() == TF_G
 || node.type() == TF_H
 || node.type() == TF_GLOT && node.isChild());
 }
 ...
}
```

Later, we can remove the flag and the test.

In this case, I used a boolean variable. I just wanted to see whether the node was still added after we extracted the condition. I felt pretty confident that I could extract the entire body of the condition without introducing errors, so I didn't test all of the logic of the condition. These tests just provided a quick way of checking to make sure that the condition was still part of the code path after the extraction. For more guidance on how much testing to do during method extraction see *Targeted Testing (189)* in Chapter 13, *I Need to Make a Change but I Don't Know What Tests to Write.*

<span id="page-323-0"></span>When you are using *sensing variables*, it is a good idea to keep them in the class over a series of refactorings and delete them only after your refactoring session. I often do this so that I can see all of the tests that I write to do the extractions and undo them easily if I find that I want to extract in a different way. When I'm done, I end up deleting these tests or refactoring them so that they test the methods I extract rather than the original method.

Sensing variables are a key tool for teasing apart monster methods. You can use them to do some refactoring deep inside snarled methods, but you can also use them to progressively de-snarl methods. For example, if we have a method that nests most of its code deep inside a set of conditional statements, we can use sensing variables to extract conditional statements or extract bodies of conditional statements into new methods. We can use sensing variables to work on those new methods as well until we've de-snarled the code.

#### Extract What You Know

Another strategy that we can use when we are working with monster methods is to start small and find little pieces of code that we can extract confidently without tests, and then add tests to cover them. Okay, I need to say this in a different way because everyone's idea of "little" is different. When I say "little," I mean two or three lines—five, at most, a chunk of code that you can easily name. The key thing to pay attention to when you do these little extractions is the *coupling count* of the extraction. The *coupling count* is the number of values that pass into and out of the method you are extracting. For example, if we extract a max method out of the following method, its count will be 3:

```
void process(int a, int b, int c) {
 int maximum;
 if (a > b)
 maximum = a;
 else
 maximum = b;
 ...
```

Here is the code after the extraction:

```
void process(int a, int b, int c) {
 int maximum = max(a,b);
 ...
}
```

The *coupling count* of the method is 3: two variables in and one variable out. It is good to favor extractions with a small count because it is not as easy to make a mistake. When you are trying to pick extractions, look for a small

<span id="page-324-0"></span>![](../assets/_page_324_Picture_1.jpeg)

number of lines and start counting the variables that come in and go out. Accesses of instance variables don't count because we are just cut/copy pasting them out; they don't pass through the interface of the method we are extracting.

The key danger in a method extraction is a type conversion error. We have a better chance of avoiding those if we extract only methods that have a low coupling count. When we've identified a possible extraction, we should look back and find where each variable that is passed is declared, to make sure that we get the method signature right.

If extractions with a low coupling count are safer, then extractions with a count of 0 must be the safest of all—and they are. You can make a lot of headway in a monster method by just extracting methods that don't accept any parameters and don't return any values. These methods are really commands to do something. You tell the object to do something to its state, or, more sleazily, you tell the object to do things with some global state. Regardless, when you attempt to name chunks of code like this, you often end up getting more insight into what the chunk is about and how it is supposed to affect the object. This sort of insight can cascade into more insights and cause you to see your design from different, more productive perspectives.

When you use *Extract What You Know*, make sure that you don't choose chunks that are too large. And if the coupling count is greater than 0, often it pays to use a *sensing variable*. After you extract, write a few tests for the method you extracted.

When you use this technique with small chunks, it is hard to see progress as you whittle away at a monster method, but progress has a way of sneaking up on you. Every time that you go back and extract another little piece that you know, you clarify the method a little bit. Over time, you might get a better sense of the method's scope and what directions you'd like to take it in.

When I don't have a refactoring tool, I often start to extract 0-count methods just to get a sense of the overall structure. Often it is a good prelude to testing and further work.

If you have a bulleted method, you might think that you'll be able to extract many 0-count methods and that each chunk will be a good one. Sometimes you'll find a chunk that is like that, but often chunks use temporary variables declared before them. Sometimes you have to ignore the "chunk structure" of a bulleted method and look for low-count methods inside chunks and across chunks.

<span id="page-325-0"></span>
#### Gleaning Dependencies

Sometimes there is code in a monster method that is kind of secondary to the method's main purpose. It is necessary, but it isn't terribly complex, and if you accidentally break it, it will be obvious. But although all of that is true, you simply cannot take a chance on breaking the main logic of the method. In cases like these, you can use a technique called gleaning dependencies. You write tests for the logic that you need to preserve. Afterward, you extract things that the tests do not cover. When you do this, you can at least have confidence that you are preserving the important behavior. Here is a simple example:

```
void addEntry(Entry entry) {
 if (view != null && DISPLAY == true) {
 view.show(entry);
 }
 ...
 if (entry.category().equals("single") 
 || entry.category("dual")) {
 entries.add(entry);
 view.showUpdate(entry, view.GREEN);
 }
 else {
 ...
 }
```

If we make a mistake with the display code, we'll see it pretty quickly. An error in the add logic, though, is something that might take quite a while to find. In a case like this, we can write tests for the method and verify that the adds happen under the right conditions. Then when we are confident that all of that behavior is covered, we can extract the display code and know that our extraction will not affect entry addition.

In some ways, *Gleaning Dependencies* feels like a cop-out. You are preserving one set of behaviors and working with another in an unprotected way. But not all behaviors are equal in an application. Some are more critical, and we can recognize that when we work.

*Gleaning Dependencies* is particularly powerful when critical behavior is tangled with other behavior. When you have solid tests for the critical behavior, you can do a lot of editing that technically isn't all covered by tests, but it helps you to preserve key behavior.

<span id="page-326-1"></span>![](../assets/_page_326_Picture_1.jpeg)

*Sensing variables* are very powerful tools in our arsenal, but sometimes you notice that you already have variables that would be ideal for sensing but that are local to the method. If they were instance variables, you could sense through them after a method runs. You can turn local variables into instance variables, but, in many cases, that can be confusing. The state that you put there will be common only to the monster method and the methods that you extract from it. Although it will be reinitialized every time the monster method is called, it can be hard to understand what the variables will hold if you want to call methods that you've extracted independently.

<span id="page-326-0"></span>One alternative is *Break Out Method Object (330)*. This technique was first described by Ward Cunningham, and it epitomizes the idea of an invented abstraction. When you break out a method object, you create a class whose only responsibility is to do the work of your monster method. The parameters of the method become parameters to a constructor on the new class, and the code of the monster method can go into a method named run or execute on the new class. When the code has been moved to the new class, we're in a great position to refactor. We can turn the temporary variables in the method into instance variables and sense through them as we break down the method.

Breaking out a method object is a pretty drastic move, but unlike introducing a *sensing variable*, the variables that you are using are needed for production. This allows you to build up tests that you can keep. See *Break Out Method Object (330)* for a detailed example.

### Strategy

The techniques I've described in this chapter can help you break up monster methods for additional refactoring or just feature addition. This section contains some guidance about how to make structural tradeoffs as you do this work.

**Strategy**

#### Skeletonize Methods

When you have a conditional statement and you are looking for places to extract a method, you have two choices. You can extract the condition and the body together, or you can extract them separately. Here is an example:

```
 if (marginalRate() > 2 && order.hasLimit()) {
 order.readjust(rateCalculator.rateForToday());
```

```
 order.recalculate();
 }
```

If you extract the condition and the body to two different methods, you are in a better position to reorganize the logic of the method later:

```
 if (orderNeedsRecalculation(order)) {
 recalculateOrder(order, rateCalculator);
 }
```

I call this skeletonizing because when you are done, all that is left in the method is a skeleton: the control structure and delegations to other methods.

#### Find Sequences

When you have a conditional statement and you are looking for places to extract a method, you have two choices. You can extract the condition and the body together or you can extract them separately. Here is another example:

```
 ...
 if (marginalRate() > 2 && order.hasLimit()) {
 order.readjust(rateCalculator.rateForToday());
 order.recalculate();
 }
 ...
```

If you extract the condition and the body to the same method, you are in a better position to identify a common sequence of operations:

```
 ...
 recalculateOrder(order, rateCalculator);
 ...
void recalculateOrder(Order order, 
 RateCalculator rateCalculator) {
 if (marginalRate() > 2 && order.hasLimit()) {
 order.readjust(rateCalculator.rateForToday());
 order.recalculate();
 }
}
```

It might turn out that the rest of the method is just a sequence of operations that happen one after another, and it will be clearer if we are able to see that sequence.

Wait, did I just give completely conflicting advice? Yes, I did. The fact is, I often go back and forth between skeletonizing methods and finding sequences. Chances are, you will, too. I skeletonize when I feel that the control structure **Strategy**

<span id="page-328-0"></span>![](../assets/_page_328_Picture_1.jpeg)

will need to be refactored after it is clarified. I attempt to find sequences when I feel that identifying an overarching sequence will make the code clearer.

Bulleted methods lean me toward finding sequences, and snarled methods lean me toward skeletonizing, but your choice of strategy really depends upon the design insights you get when you are doing your extractions.

### Extract to the Current Class First

When you start to extract methods from a monster method, you'll probably notice that some of the chunks of code that you are extracting really belong in other classes. One strong indication is the name you're tempted to use. If you look at a piece of code and you are tempted to use the name of one of the variables you are using in it, chances are good that the code belongs on the class of that variable. That would be the case in this snippet:

```
if (marginalRate() > 2 && order.hasLimit()) {
   order.readjust(rateCalculator.rateForToday());
   order.recalculate();
}
```

It looks like we could call this piece of code recalculateOrder. That would be a decent name, but if we are using the word *order* in the method name, maybe this piece of code should move onto the Order class and be called recalculate. Yes, there is a method named recalculate already, so we might want to think about what makes this recalculation different and use that information in the name, or rename the recalculate method that is already there. Regardless, it looks like this piece of code belongs on that class.

Although it is tempting to extract directly to another class, don't do it. Use the awkward name first. The name recalculateOrder is awkward, but it lets us do some easily undoable extractions and explore whether we've extracted the right chunk of code to move forward. We can always move the method to another class later when the best direction for our changes presents itself. In the meantime, extracting to the current class moves us forward and it is less error prone.

#### Extract Small Pieces

**Strategy**

I mentioned this earlier, but I want to underscore it: Extract small pieces first. Before you extract this small piece of a monster method, it looks like it won't make any difference at all. After you extract more pieces, you'll probably see the original method in a different way. You might see a sequence that was obscured before or see a better way for the method to be organized. When you see those directions, you can move toward them. This is a far better strategy

![](../assets/_page_329_Picture_1.jpeg)

<span id="page-329-0"></span>than trying to break up a method into large chunks from the beginning. Too often that isn't as easy as it looks; it isn't as safe. It's easier to miss the details, and the details are what make the code work.

#### Be Prepared to Redo Extractions

There are many ways to slice a pie and many ways to break down a monster method. After you make some extractions, you'll usually find better ways to accommodate new features more easily. Sometimes the best way to move forward is to undo an extraction or two and re-extract. When you do this, it doesn't mean that the first extractions were wasted effort. They gave you something very important: insight into old design and into a better way of moving forward.

**Strategy**

![](../assets/_page_330_Picture_0.jpeg)
