# Chapter 1: Domain Modeling

This chapter looks into how we can model business processes with code, in a way that's highly compatible with TDD. We'll discuss why domain modeling matters, and we'll look at a few key patterns for modeling domains: Entity, Value Object, and Domain Service.

Figure 1-1 is a simple visual placeholder for our Domain Model pattern. We'll fill in some details in this chapter, and as we move on to other chapters, we'll build things around the domain model, but you should always be able to find these little shapes at the core.

![](../assets/_page_46_Picture_0.jpeg)

## What Is a Domain Model?

In the introduction, we used the term business logic layer to describe the central layer of a three-layered architecture. For the rest of the book, we're going to use the term domain model instead. This is a term from the DDD community that does a better job of capturing our intended meaning (see the next sidebar for more on DDD).

The domain is a fancy way of saying the problem you're trying to solve. Your authors currently work for an online retailer of furniture. Depending on which system you're talking about, the domain might be purchasing and procurement, or product design, or logistics and delivery. Most programmers spend their days trying to improve or automate business processes; the domain is the set of activities that those processes support.

A *model* is a map of a process or phenomenon that captures a useful property. Humans are exceptionally good at producing models of things in their heads. For example, when someone throws a ball toward you, you're able to predict its movement almost unconsciously, because you have a model of the way objects move in space. Your model isn't perfect by any means. Humans have terrible intuitions about how objects behave at near-light speeds or in a vacuum because our model was never designed to cover those cases. That doesn't mean the model is wrong, but it does mean that some predictions fall outside of its domain.

The domain model is the mental map that business owners have of their businesses. All business people have these mental maps—they're how humans think about complex processes.

You can tell when they're navigating these maps because they use business speak. Jargon arises naturally among people who are collaborating on complex systems.

Imagine that you, our unfortunate reader, were suddenly transported light years away from Earth aboard an alien spaceship with your friends and family and had to figure out, from first principles, how to navigate home.

In your first few days, you might just push buttons randomly, but soon you'd learn which buttons did what, so that you could give one another instructions. "Press the red button near the flashing doohickey and then throw that big lever over by the radar gizmo," you might say.

Within a couple of weeks, you'd become more precise as you adopted words to describe the ship's functions: "Increase oxygen levels in cargo bay three" or "turn on the little thrusters." After a few months, you'd have adopted language for entire complex processes: "Start landing sequence" or "prepare for warp." This process would happen quite naturally, without any formal effort to build a shared glossary.

### THIS IS NOT A DDD BOOK. YOU SHOULD READ A DDD BOOK.

Domain-driven design, or DDD, popularized the concept of domain modeling, and it's been a hugely successful movement in transforming the way people design software by focusing on the core business domain. Many of the architecture patterns that we cover in this book—including Entity, Aggregate, Value Object (see Chapter 7), and Repository (in the next chapter)—come from the DDD tradition.

In a nutshell, DDD says that the most important thing about software is that it provides a useful model of a problem. If we get that model right, our software delivers value and makes new things possible.

If we get the model wrong, it becomes an obstacle to be worked around. In this book, we can show the basics of building a domain model, and building an architecture around it that leaves the model as free as possible from external constraints, so that it's easy to evolve and change.

But there's a lot more to DDD and to the processes, tools, and techniques for developing a domain model. We hope to give you a taste of it, though, and cannot encourage you enough to go on and read a proper DDD book:

- The original "blue book," Domain-Driven Design by Eric Evans (Addison-Wesley Professional)
- The "red book," Implementing Domain-Driven Design by Vaughn Vernon (Addison-Wesley Professional)

So it is in the mundane world of business. The terminology used by business stakeholders represents a distilled understanding of the domain model, where complex ideas and processes are boiled down to a single word or phrase.

When we hear our business stakeholders using unfamiliar words, or using terms in a specific way, we should listen to understand the deeper meaning and encode their hard-won experience into our software.

We're going to use a real-world domain model throughout this book, specifically a model from our current employment. MADE.com is a

successful furniture retailer. We source our furniture from manufacturers all over the world and sell it across Europe.

When you buy a sofa or a coffee table, we have to figure out how best to get your goods from Poland or China or Vietnam and into your living room.

At a high level, we have separate systems that are responsible for buying stock, selling stock to customers, and shipping goods to customers. A system in the middle needs to coordinate the process by allocating stock to a customer's orders; see Figure 1-2.

![](../assets/_page_51_Figure_0.jpeg)

Figure 1-2. Context diagram for the allocation service

For the purposes of this book, we're imagining that the business decides to implement an exciting new way of allocating stock. Until now, the business has been presenting stock and lead times based on what is physically available in the warehouse. If and when the warehouse runs out, a product is listed as "out of stock" until the next shipment arrives from the manufacturer.

Here's the innovation: if we have a system that can keep track of all our shipments and when they're due to arrive, we can treat the goods on those ships as real stock and part of our inventory, just with slightly longer lead times. Fewer goods will appear to be out of stock, we'll sell more, and the business can save money by keeping lower inventory in the domestic warehouse.

But allocating orders is no longer a trivial matter of decrementing a single quantity in the warehouse system. We need a more complex allocation mechanism. Time for some domain modeling.

### Exploring the Domain Language

Understanding the domain model takes time, and patience, and Post-it notes. We have an initial conversation with our business experts and agree on a glossary and some rules for the first minimal version of the domain model. Wherever possible, we ask for concrete examples to illustrate each rule.

We make sure to express those rules in the business jargon (the *ubiquitous language* in DDD terminology). We choose memorable identifiers for our objects so that the examples are easier to talk about.

"Some Notes on Allocation" shows some notes we might have taken while having a conversation with our domain experts about allocation.

#### SOME NOTES ON ALLOCATION

A product is identified by a SKU, pronounced "skew," which is short for stock-keeping unit.

Customers place orders. An order is identified by an order reference and comprises multiple order lines, where each line has a SKU and a quantity. For example:

- 10 units of RED-CHAIR
- 1 unit of TASTELESS-LAMP

The purchasing department orders small batches of stock. A batch of stock has a unique ID called a reference, a SKU, and a quantity.

We need to allocate order lines to batches. When we've allocated an order line to a batch, we will send stock from that specific batch to the customer's delivery address. When we allocate x units of stock to a batch, the available quantity is reduced by x. For example:

- We have a batch of 20 SMALL-TABLE, and we allocate an order line for 2 SMALL-TABLE.
- The batch should have 18 SMALL-TABLE remaining.

We can't allocate to a batch if the available quantity is less than the quantity of the order line. For example:

- We have a batch of 1 BLUE-CUSHION, and an order line for 2 BLUE-CUSHION.
- We should not be able to allocate the line to the batch.

We can't allocate the same line twice. For example:

- We have a batch of 10 BLUE-VASE, and we allocate an order line for 2 BLUE-VASE.
- If we allocate the order line again to the same batch, the batch should still have an available quantity of 8.

Batches have an *ETA* if they are currently shipping, or they may be in *warehouse stock*. We allocate to warehouse stock in preference to shipment batches. We allocate to shipment batches in order of which has the earliest ETA.

### Unit Testing Domain Models

We're not going to show you how TDD works in this book, but we want to show you how we would construct a model from this business conversation.

### EXERCISE FOR THE READER

Why not have a go at solving this problem yourself? Write a few unit tests to see if you can capture the essence of these business rules in nice, clean code.

You'll find some placeholder unit tests on GitHub, but you could just start from scratch, or combine/rewrite them however you like.

Here's what one of our first tests might look like:

A first test for allocation (test\_batches.py)

```
def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine('order-ref', "SMALL-TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18
```

The name of our unit test describes the behavior that we want to see from the system, and the names of the classes and variables that we use are taken from the business jargon. We could show this code to our nontechnical coworkers, and they would agree that this correctly describes the behavior of the system.

And here is a domain model that meets our requirements:

```
class OrderLine:
    orderid: str
    sku: str
    qty: int

class Batch:
    def __init__(
        self, ref: str, sku: str, qty: int, eta: Optional[date]
```

- OrderLine is an immutable dataclass with no behavior.<sup>2</sup>
- We're not showing imports in most code listings, in an attempt to keep them clean. We're hoping you can guess that this came via from dataclasses import dataclass; likewise, typing. Optional and datetime. date. If you want to double-check anything, you can see the full working code for each chapter in its branch (e.g., chapter\_01\_domain\_model).
- Type hints are still a matter of controversy in the Python world. For domain models, they can sometimes help to clarify or document what the expected arguments are, and people with IDEs are often grateful for them. You may decide the price paid in terms of readability is too high.

Our implementation here is trivial: a Batch just wraps an integer available\_quantity, and we decrement that value on allocation.

We've written quite a lot of code just to subtract one number from another, but we think that modeling our domain precisely will pay off.<sup>3</sup>

Let's write some new failing tests:

Testing logic for what we can allocate (test\_batches.py)

```
def make_batch_and_line(sku, batch_qty, line_qty):
   return (
       Batch("batch-001", sku, batch qty, eta=date.today()),
       OrderLine("order-123", sku, line qty)
   )
def test_can_allocate_if_available_greater_than_required():
   large batch, small line = make batch and line("ELEGANT-LAMP", 20, 2)
   assert large batch.can allocate(small line)
def test_cannot_allocate_if_available_smaller_than_required():
   small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
   assert small batch.can allocate(large line) is False
def test_can_allocate_if_available_equal_to_required():
   batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
   assert batch.can_allocate(line)
def test_cannot_allocate_if_skus_do_not_match():
   batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
   different sku line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
   assert batch.can_allocate(different_sku_line) is False
```

There's nothing too unexpected here. We've refactored our test suite so that we don't keep repeating the same lines of code to create a batch and a line for the same SKU; and we've written four simple tests for a new method can\_allocate. Again, notice that the names we use

mirror the language of our domain experts, and the examples we agreed upon are directly written into code.

We can implement this straightforwardly, too, by writing the can\_allocate method of Batch:

A new method in the model (model.py)

```
def can_allocate(self, line: OrderLine) -> bool:
    return self.sku == line.sku and self.available_quantity >= line.qty
```

So far, we can manage the implementation by just incrementing and decrementing Batch. available\_quantity, but as we get into deallocate() tests, we'll be forced into a more intelligent solution:

This test is going to require a smarter model (test\_batches.py)

```
def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20
```

In this test, we're asserting that deallocating a line from a batch has no effect unless the batch previously allocated the line. For this to work, our Batch needs to understand which lines have been allocated. Let's look at the implementation:

The domain model now tracks allocations (model.py)

```
class Batch:
    def __init__(
        self, ref: str, sku: str, qty: int, eta: Optional[date]
    ):
        self.reference = ref
```

```
self.sku = sku
    self.eta = eta
    self._purchased_quantity = qty
    self._allocations = set() # type: Set[OrderLine]
def allocate(self, line: OrderLine):
    if self.can_allocate(line):
        self._allocations.add(line)
def deallocate(self, line: OrderLine):
    if line in self._allocations:
        self._allocations.remove(line)
@property
def allocated_quantity(self) -> int:
    return sum(line.qty for line in self._allocations)
@property
def available_quantity(self) -> int:
    return self._purchased_quantity - self.allocated_quantity
def can_allocate(self, line: OrderLine) -> bool:
    return self.sku == line.sku and self.available quantity >= line.qty
```

Figure 1-3 shows the model in UML.

![](../assets/_page_58_Picture_2.jpeg)

Figure 1-3. Our model in UML

Now we're getting somewhere! A batch now keeps track of a set of allocated OrderLine objects. When we allocate, if we have enough

available quantity, we just add to the set. Our available\_quantity is now a calculated property: purchased quantity minus allocated quantity.

Yes, there's plenty more we could do. It's a little disconcerting that both allocate() and deallocate() can fail silently, but we have the basics.

Incidentally, using a set for .\_allocations makes it simple for us to handle the last test, because items in a set are unique:

Last batch test! (test\_batches.py)

```
def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
```

At the moment, it's probably a valid criticism to say that the domain model is too trivial to bother with DDD (or even object orientation!). In real life, any number of business rules and edge cases crop up: customers can ask for delivery on specific future dates, which means we might not want to allocate them to the earliest batch. Some SKUs aren't in batches, but ordered on demand directly from suppliers, so they have different logic. Depending on the customer's location, we can allocate to only a subset of warehouses and shipments that are in their region—except for some SKUs we're happy to deliver from a warehouse in a different region if we're out of stock in the home region. And so on. A real business in the real world knows how to pile on complexity faster than we can show on the page!

But taking this simple domain model as a placeholder for something more complex, we're going to extend our simple domain model in the rest of the book and plug it into the real world of APIs and databases and spreadsheets. We'll see how sticking rigidly to our principles of encapsulation and careful layering will help us to avoid a ball of mud.

![](../assets/_page_60_Figure_1.jpeg)

### Dataclasses Are Great for Value Objects

We've used line liberally in the previous code listings, but what is a line? In our business language, an *order* has multiple *line* items, where each line has a SKU and a quantity. We can imagine that a simple YAML file containing order information might look like this:

Order info as YAML

```
Order_reference: 12345
Lines:
- sku: RED-CHAIR
qty: 25
- sku: BLU-CHAIR
qty: 25
- sku: GRN-CHAIR
qty: 25
```

Notice that while an order has a *reference* that uniquely identifies it, a *line* does not. (Even if we add the order reference to the OrderLine class, it's not something that uniquely identifies the line itself.)

Whenever we have a business concept that has data but no identity, we often choose to represent it using the *Value Object* pattern. A *value object* is any domain object that is uniquely identified by the data it holds; we usually make them immutable:

OrderLine is a value object

```
@dataclass(frozen=True)
class OrderLine:
   orderid: OrderReference
   sku: ProductReference
   qty: Quantity
```

One of the nice things that dataclasses (or namedtuples) give us is value equality, which is the fancy way of saying, "Two lines with the same orderid, sku, and qty are equal."

More examples of value objects

```
from dataclasses import dataclass
from typing import NamedTuple
from collections import namedtuple
```

```
@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str

class Money(NamedTuple):
    currency: str
    value: int

Line = namedtuple('Line', ['sku', 'qty'])

def test_equality():
    assert Money('gbp', 10) == Money('gbp', 10)
    assert Name('Harry', 'Percival') != Name('Bob', 'Gregory')
    assert Line('RED-CHAIR', 5) == Line('RED-CHAIR', 5)
```

These value objects match our real-world intuition about how their values work. It doesn't matter which £10 note we're talking about, because they all have the same value. Likewise, two names are equal if both the first and last names match; and two lines are equivalent if they have the same customer order, product code, and quantity. We can still have complex behavior on a value object, though. In fact, it's common to support operations on values; for example, mathematical operators:

Math with value objects

```
fiver = Money('gbp', 5)
tenner = Money('gbp', 10)

def can_add_money_values_for_the_same_currency():
    assert fiver + fiver == tenner

def can_subtract_money_values():
    assert tenner - fiver == fiver
```

```
def adding_different_currencies_fails():
    with pytest.raises(ValueError):
        Money('usd', 10) + Money('gbp', 10)

def can_multiply_money_by_a_number():
    assert fiver * 5 == Money('gbp', 25)

def multiplying_two_money_values_is_an_error():
    with pytest.raises(TypeError):
        tenner * fiver
```

### Value Objects and Entities

An order line is uniquely identified by its order ID, SKU, and quantity; if we change one of those values, we now have a new line. That's the definition of a value object: any object that is identified only by its data and doesn't have a long-lived identity. What about a batch, though? That *is* identified by a reference.

We use the term *entity* to describe a domain object that has long-lived identity. On the previous page, we introduced a Name class as a value object. If we take the name Harry Percival and change one letter, we have the new Name object Barry Percival.

It should be clear that Harry Percival is not equal to Barry Percival:

A name itself cannot change...

```
def test_name_equality():
    assert Name("Harry", "Percival") != Name("Barry", "Percival")
```

But what about Harry as a *person*? People do change their names, and their marital status, and even their gender, but we continue to recognize

them as the same individual. That's because humans, unlike names, have a persistent *identity*:

But a person can!

```
class Person:

    def __init__(self, name: Name):
        self.name = name

def test_barry_is_harry():
    harry = Person(Name("Harry", "Percival"))
    barry = harry

    barry.name = Name("Barry", "Percival")

    assert harry is barry and barry is harry
```

Entities, unlike values, have *identity equality*. We can change their values, and they are still recognizably the same thing. Batches, in our example, are entities. We can allocate lines to a batch, or change the date that we expect it to arrive, and it will still be the same entity.

We usually make this explicit in code by implementing equality operators on entities:

Implementing equality operators (model.py)

```
class Batch:
    ...

def __eq__(self, other):
    if not isinstance(other, Batch):
        return False
    return other.reference = self.reference
```

```
def __hash__(self):
    return hash(self.reference)
```

Python's  $_{-eq}$  magic method defines the behavior of the class for the == operator. $_{-5}$ 

For both entity and value objects, it's also worth thinking through how \_\_hash\_\_ will work. It's the magic method Python uses to control the behavior of objects when you add them to sets or use them as dict keys; you can find more info in the Python docs.

For value objects, the hash should be based on all the value attributes, and we should ensure that the objects are immutable. We get this for free by specifying <code>@frozen=True</code> on the dataclass.

For entities, the simplest option is to say that the hash is None, meaning that the object is not hashable and cannot, for example, be used in a set. If for some reason you decide you really do want to use set or dict operations with entities, the hash should be based on the attribute(s), such as .reference, that defines the entity's unique identity over time. You should also try to somehow make *that* attribute read-only.

#### WARNING

This is tricky territory; you shouldn't modify \_\_hash\_\_ without also modifying \_\_eq\_\_. If you're not sure what you're doing, further reading is suggested.

"Python Hashes and Equality" by our tech reviewer Hynek Schlawack is a good place to start.

## Not Everything Has to Be an Object: A Domain Service Function

We've made a model to represent batches, but what we actually need to do is allocate order lines against a specific set of batches that represent all our stock.

```
Sometimes, it just isn't a thing.

—Eric Evans, Domain-Driven Design
```

Evans discusses the idea of Domain Service operations that don't have a natural home in an entity or value object. A thing that allocates an order line, given a set of batches, sounds a lot like a function, and we can take advantage of the fact that Python is a multiparadigm language and just make it a function.

Let's see how we might test-drive such a function:

Testing our domain service (test\_allocate.py)

```
def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

allocate(line, [in_stock_batch, shipment_batch])

assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
```

```
line = OrderLine("order1", "MINIMALIST-SPOON", 10)

allocate(line, [medium, earliest, latest])

assert earliest.available_quantity == 90
assert medium.available_quantity == 100

assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference
```

And our service might look like this:

A standalone function for our domain service (model.py)

```
def allocate(line: OrderLine, batches: List[Batch]) -> str:
   batch = next(
        b for b in sorted(batches) if b.can_allocate(line)
   )
   batch.allocate(line)
   return batch.reference
```

## Python's Magic Methods Let Us Use Our Models with Idiomatic Python

You may or may not like the use of next() in the preceding code, but we're pretty sure you'll agree that being able to use sorted() on our list of batches is nice, idiomatic Python.

To make it work, we implement \_\_gt\_\_ on our domain model:

```
class Batch:
    ...

def __gt__(self, other):
    if self.eta is None:
        return False
    if other.eta is None:
        return True
    return self.eta > other.eta
```

That's lovely.

### Exceptions Can Express Domain Concepts Too

We have one final concept to cover: exceptions can be used to express domain concepts too. In our conversations with domain experts, we've learned about the possibility that an order cannot be allocated because we are *out of stock*, and we can capture that by using a *domain exception*:

Testing out-of-stock exception (test\_allocate.py)

```
def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    allocate(OrderLine('order1', 'SMALL-FORK', 10), [batch])

with pytest.raises(OutOfStock, match='SMALL-FORK'):
    allocate(OrderLine('order2', 'SMALL-FORK', 1), [batch])
```

#### DOMAIN MODELING RECAP

#### Domain modeling

This is the part of your code that is closest to the business, the most likely to change, and the place where you deliver the most value to the business. Make it easy to understand and modify.

Distinguish entities from value objects

A value object is defined by its attributes. It's usually best implemented as an immutable type. If you change an attribute on a Value Object, it represents a different object. In contrast, an entity has attributes that may vary over time and it will still be the same entity. It's important to define what *does* uniquely identify an entity (usually some sort of name or reference field).

Not everything has to be an object

Python is a multiparadigm language, so let the "verbs" in your code be functions. For every FooManager, BarBuilder, or BazFactory, there's often a more expressive and readable manage\_foo(), build\_bar(), or get\_baz() waiting to happen.

This is the time to apply your best OO design principles

Revisit the SOLID principles and all the other good heuristics like "has a versus is-a," "prefer composition over inheritance," and so on.

You'll also want to think about consistency boundaries and aggregates

But that's a topic for Chapter 7.

We won't bore you too much with the implementation, but the main thing to note is that we take care in naming our exceptions in the ubiquitous language, just as we do our entities, value objects, and services:

Raising a domain exception (model.py)

```
class OutOfStock(Exception):
    pass

def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(
```

```
except StopIteration:
    raise OutOfStock(f'Out of stock for sku {line.sku}')
```

Figure 1-4 is a visual representation of where we've ended up.

![](../assets/_page_71_Figure_0.jpeg)

### Figure 1-4. Our domain model at the end of the chapter

That'll probably do for now! We have a domain service that we can use for our first use case. But first we'll need a database...

- DDD did not originate domain modeling. Eric Evans refers to the 2002 book Object Design by Rebecca Wirfs-Brock and Alan McKean (Addison-Wesley Professional), which introduced responsibility-driven design, of which DDD is a special case dealing with the domain. But even that is too late, and OO enthusiasts will tell you to look further back to Ivar Jacobson and Grady Booch; the term has been around since the mid-1980s.
- 2 In previous Python versions, we might have used a namedtuple. You could also check out Hynek Schlawack's excellent attrs.
- Or perhaps you think there's not enough code? What about some sort of check that the SKU in the OrderLine matches Batch.sku? We saved some thoughts on validation for Appendix E.
- 4 It is appalling. Please, please don't do this. —Harry
- 5 The \_\_eq\_ method is pronounced "dunder-EQ." By some, at least.
- Obmain services are not the same thing as the services from the service layer, although they are often closely related. A domain service represents a business concept or process, whereas a service-layer service represents a use case for your application. Often the service layer will call a domain service.
