# Chapter 6: Unit of Work Pattern

In this chapter we'll introduce the final piece of the puzzle that ties together the Repository and Service Layer patterns: the *Unit of Work* pattern.

If the Repository pattern is our abstraction over the idea of persistent storage, the Unit of Work (UoW) pattern is our abstraction over the idea of *atomic operations*. It will allow us to finally and fully decouple our service layer from the data layer.

Figure 6-1 shows that, currently, a lot of communication occurs across the layers of our infrastructure: the API talks directly to the database layer to start a session, it talks to the repository layer to initialize SQLAlchemyRepository, and it talks to the service layer to ask it to allocate.

## TIP

The code for this chapter is in the chapter 06 uow branch on GitHub:

```
git clone https://github.com/cosmicpython/code.git
cd code
git checkout chapter_06_uow
# or to code along, checkout Chapter 4:
git checkout chapter_04_service_layer
```

![](../assets/_page_164_Figure_0.jpeg)

Figure 6-1. Without UoW: API talks directly to three layers

Figure 6-2 shows our target state. The Flask API now does only two things: it initializes a unit of work, and it invokes a service. The service collaborates with the UoW (we like to think of the UoW as being part of the service layer), but neither the service function itself nor Flask now needs to talk directly to the database.

And we'll do it all using a lovely piece of Python syntax, a context manager.

![](../assets/_page_166_Figure_0.jpeg)

## The Unit of Work Collaborates with the Repository

Let's see the unit of work (or UoW, which we pronounce "you-wow") in action. Here's how the service layer will look when we're finished:

Preview of unit of work in action (src/allocation/service\_layer/services.py)

```
def allocate(
```

- We'll start a UoW as a context manager.
- uow. batches is the batches repo, so the UoW provides us access to our permanent storage.
- When we're done, we commit or roll back our work, using the UoW.

The UoW acts as a single entrypoint to our persistent storage, and it keeps track of what objects were loaded and of the latest state. 1

This gives us three useful things:

- A stable snapshot of the database to work with, so the objects we use aren't changing halfway through an operation
- A way to persist all of our changes at once, so if something goes wrong, we don't end up in an inconsistent state
- A simple API to our persistence concerns and a handy place to get a repository

## Test-Driving a UoW with Integration Tests

Here are our integration tests for the UOW:

A basic "round-trip" test for a UoW (tests/integration/test\_uow.py)

```
def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch1', 'HIPSTER-WORKBENCH', 100, None)
    session.commit()
\nuow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
```

- We initialize the UoW by using our custom session factory and get back a uow object to use in our with block.
- The UoW gives us access to the batches repository via uow. batches.
- **9** We call **commit()** on it when we're done.

For the curious, the insert\_batch and get\_allocated\_batch\_ref helpers look like this:

Helpers for doing SQL stuff (tests/integration/test\_uow.py)

```
def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES (:ref, :sku, :qty, :eta)',
        dict(ref=ref, sku=sku, qty=qty, eta=eta)
    )
def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(
        'SELECT id FROM order lines WHERE orderid=:orderid AND sku=:sku',
        dict(orderid=orderid, sku=sku)
    [[batchref]] = session.execute(
        'SELECT b.reference FROM allocations JOIN batches AS b ON batch_id =
b.id'
        ' WHERE orderline id=:orderlineid',
        dict(orderlineid=orderlineid)
    )
    return batchref
```

## Unit of Work and Its Context Manager

In our tests we've implicitly defined an interface for what a UoW needs to do. Let's make that explicit by using an abstract base class:

```
Abstract UoW context manager (src/allocation/service layer/unit of work.py)
```

```
class AbstractUnitOfWork(abc.ABC):
  batches: repository.AbstractRepository
```

```
def __exit__(self, *args): @
    self.rollback()
```

- The UoW provides an attribute called .batches, which will give us access to the batches repository.
- If you've never seen a context manager, \_\_enter\_\_ and \_\_exit\_\_ are the two magic methods that execute when we enter the with block and when we exit it, respectively. They're our setup and teardown phases.
- We'll call this method to explicitly commit our work when we're ready.
- If we don't commit, or if we exit the context manager by raising an error, we do a rollback. (The rollback has no effect if commit() has been called. Read on for more discussion of this.)

## The Real Unit of Work Uses SQLAlchemy Sessions

The main thing that our concrete implementation adds is the database session:

```
The real SQLAlchemy UoW (src/allocation/service_layer/unit_of_work.py)
```

```
DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(                                    
    config.get_postgres_uri(),
))
class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory 0
    def __enter__(self):
        self.session = self.session_factory() # type: Session @
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()
    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close() 0
    def commit(self): 4
        self.session.commit()
    def rollback(self): @
        self.session.rollback()
```

- The module defines a default session factory that will connect to Postgres, but we allow that to be overridden in our integration tests so that we can use SQLite instead.
- The \_\_enter\_\_ method is responsible for starting a database session and instantiating a real repository that can use that session.
- We close the session on exit.
- Finally, we provide concrete commit() and rollback() methods that use our database session.

### Fake Unit of Work for Testing

Here's how we use a fake UoW in our service-layer tests:

```
class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False @
    def commit(self):
        self.committed = True @
    def rollback(self):
        pass
def test_add_batch():
    uow = FakeUnitOfWork() 6
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)  
    assert uow.batches.get("b1") is not None
    assert uow.committed
def test_allocate_returns_allocation():
    uow = FakeUnitOfWork() 6
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)                                   
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow) 3
    assert result == "batch1"
```

- FakeUnitOfWork and FakeRepository are tightly coupled, just like the real UnitofWork and Repository classes. That's fine because we recognize that the objects are collaborators.
- Notice the similarity with the fake commit() function from FakeSession (which we can now get rid of). But it's a substantial improvement because we're now faking out code that we wrote rather than third-party code. Some people say, "Don't mock what you don't own".

In our tests, we can instantiate a UoW and pass it to our service layer, rather than passing a repository and a session. This is considerably less cumbersome.

#### DON'T MOCK WHAT YOU DON'T OWN

Why do we feel more comfortable mocking the UoW than the session? Both of our fakes achieve the same thing: they give us a way to swap out our persistence layer so we can run tests in memory instead of needing to talk to a real database. The difference is in the resulting design.

If we cared only about writing tests that run quickly, we could create mocks that replace SQLAlchemy and use those throughout our codebase. The problem is that Session is a complex object that exposes lots of persistence-related functionality. It's easy to use Session to make arbitrary queries against the database, but that quickly leads to data access code being sprinkled all over the codebase. To avoid that, we want to limit access to our persistence layer so each component has exactly what it needs and nothing more.

By coupling to the Session interface, you're choosing to couple to all the complexity of SQLAIChemy. Instead, we want to choose a simpler abstraction and use that to clearly separate responsibilities. Our UoW is much simpler than a session, and we feel comfortable with the service layer being able to start and stop units of work.

"Don't mock what you don't own" is a rule of thumb that forces us to build these simple abstractions over messy subsystems. This has the same performance benefit as mocking the SQLAIchemy session but encourages us to think carefully about our designs.

### Using the UoW in the Service Layer

Here's what our new service layer looks like:

Service layer using UoW (src/allocation/service layer/services.py)

```
def add_batch(
          ref: str, sku: str, qty: int, eta: Optional[date],
          uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()
```

```
def allocate(
```

• Our service layer now has only the one dependency, once again on an *abstract* UoW.

## Explicit Tests for Commit/Rollback Behavior

To convince ourselves that the commit/rollback behavior works, we wrote a couple of tests:

```
Integration tests for rollback behavior (tests/integration/test_uow.py)
```

```
def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, 'batch1', 'MEDIUM-PLINTH', 100, None)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []
```

```
def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass
\nuow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
with pytest.raises(MyException):
    with uow:
        insert_batch(uow.session, 'batch1', 'LARGE-FORK', 100, None)
        raise MyException()

new_session = session_factory()
rows = list(new_session.execute('SELECT * FROM "batches"'))
assert rows == []
```

### TIP

We haven't shown it here, but it can be worth testing some of the more "obscure" database behavior, like transactions, against the "real" database—that is, the same engine. For now, we're getting away with using SQLite instead of Postgres, but in Chapter 7, we'll switch some of the tests to using the real database. It's convenient that our UoW class makes that easy!

## Explicit Versus Implicit Commits

Now we briefly digress on different ways of implementing the UoW pattern.

We could imagine a slightly different version of the UoW that commits by default and rolls back only if it spots an exception:

A UoW with implicit commit... (src/allocation/unit\_of\_work.py)

```
class AbstractUnitOfWork(abc.ABC):
```

```
def __enter__(self):
    return self

def __exit__(self, exn_type, exn_value, traceback):
    if exn_type is None:
        self.commit()
```

- Should we have an implicit commit in the happy path?
- And roll back only on exception?

It would allow us to save a line of code and to remove the explicit commit from our client code:

```
...would save us a line of code (src/allocation/service_layer/services.py)
```

```
def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        # uow.commit()
```

This is a judgment call, but we tend to prefer requiring the explicit commit so that we have to choose when to flush state.

Although we use an extra line of code, this makes the software safe by default. The default behavior is to *not change anything*. In turn, that makes our code easier to reason about because there's only one code path that leads to changes in the system: total success and an explicit commit. Any other code path, any exception, any early exit from the UoW's scope leads to a safe state.

Similarly, we prefer to roll back by default because it's easier to understand; this rolls back to the last commit, so either the user did one, or we blow their changes away. Harsh but simple.

## Examples: Using UoW to Group Multiple Operations into an Atomic Unit

Here are a few examples showing the Unit of Work pattern in use. You can see how it leads to simple reasoning about what blocks of code happen together.

### Example 1: Reallocate

Suppose we want to be able to deallocate and then reallocate orders:

Reallocate service function

```
def reallocate(line: OrderLine, uow: AbstractUnitOfWork) -> str:
    with uow:
        batch = uow.batches.get(sku=line.sku)
        if batch is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batch.deallocate(line)
```

- If deallocate() fails, we don't want to call allocate(), obviously.
- If allocate() fails, we probably don't want to actually commit the deallocate() either.

### Example 2: Change Batch Quantity

Our shipping company gives us a call to say that one of the container doors opened, and half our sofas have fallen into the Indian Ocean.

Oops!

Change quantity

```
def change_batch_quantity(batchref: str, new_qty: int, uow: AbstractUnitOfWork):
    with uow:
        batch = uow.batches.get(reference=batchref)
        batch.change_purchased_quantity(new_qty)
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
```

Here we may need to deallocate any number of lines. If we get a failure at any stage, we probably want to commit none of the changes.

### Tidying Up the Integration Tests

We now have three sets of tests, all essentially pointing at the database:  $test\_orm.py$ ,  $test\_repository.py$ , and  $test\_uow.py$ . Should we throw any away?

```
    tests
```

You should always feel free to throw away tests if you think they're not going to add value longer term. We'd say that <code>test\_orm.py</code> was primarily a tool to help us learn SQLAlchemy, so we won't need that long term, especially if the main things it's doing are covered in <code>test\_repository.py</code>. That last test, you might keep around, but we could certainly see an argument for just keeping everything at the highest possible level of abstraction (just as we did for the unit tests).

#### EXERCISE FOR THE READER

For this chapter, probably the best thing to try is to implement a UoW from scratch. The code, as always, is on GitHub. You could either follow the model we have quite closely, or perhaps experiment with separating the UoW (whose responsibilities are <code>commit()</code>, <code>rollback()</code>, and providing the <code>.batches</code> repository) from the context manager, whose job is to initialize things, and then do the commit or rollback on exit. If you feel like going all-functional rather than messing about with all these classes, you could use <code>@contextmanager</code> from <code>contextlib</code>.

We've stripped out both the actual UoW and the fakes, as well as paring back the abstract UoW. Why not send us a link to your repo if you come up with something you're particularly proud of?

#### TIP

This is another example of the lesson from <u>Chapter 5</u>: as we build better abstractions, we can move our tests to run against them, which leaves us free to change the underlying details.

## Wrap-Up

Hopefully we've convinced you that the Unit of Work pattern is useful, and that the context manager is a really nice Pythonic way of visually grouping code into blocks that we want to happen atomically.

This pattern is so useful, in fact, that SQLAlchemy already uses a UoW in the shape of the Session object. The Session object in SQLAlchemy is the way that your application loads data from the database.

Every time you load a new entity from the database, the session begins to *track* changes to the entity, and when the session is *flushed*, all your changes are persisted together. Why do we go to the effort of abstracting away the SQLAlchemy session if it already implements the pattern we want?

Table 6-1 discusses some of the trade-offs.

Pros Cons

- We have a nice abstraction over the concept of atomic operations, and the context manager makes it easy to see, visually, what blocks of code are grouped together atomically.
- We have explicit control over when a transaction starts and finishes, and our application fails in a way that is safe by default. We never have to worry that an operation is partially committed.
- It's a nice place to put all your repositories so client code can access them.
- As you'll see in later chapters, atomicity isn't only about transactions; it can help us work with events and the message bus.

- Your ORM probably already has some perfectly good abstractions around atomicity. SQL Alchemy even has context managers. You can go a long way just passing a session around.
- We've made it look easy, but you have to think quite carefully about things like rollbacks, multithreading, and nested transactions. Perhaps just sticking to what Django or Flask-SQL Alchemy gives you will keep your life simpler.

For one thing, the Session API is rich and supports operations that we don't want or need in our domain. Our UnitOfWork simplifies the session to its essential core: it can be started, committed, or thrown away.

For another, we're using the UnitOfWork to access our Repository objects. This is a neat bit of developer usability that we couldn't do with a plain SQLAlchemy Session.

### UNIT OF WORK PATTERN RECAP

The Unit of Work pattern is an abstraction around data integrity

It helps to enforce the consistency of our domain model, and improves performance, by letting us perform a single *flush* operation at the end of an operation.

It works closely with the Repository and Service Layer patterns

The Unit of Work pattern completes our abstractions over data access by representing atomic updates. Each of our service-layer use cases runs in a single unit of work that succeeds or fails as a block.

This is a lovely case for a context manager

Context managers are an idiomatic way of defining scope in Python. We can use a context manager to automatically roll back our work at the end of a request, which means the system is safe by default.

SQLAlchemy already implements this pattern

We introduce an even simpler abstraction over the SQLAlchemy Session object in order to "narrow" the interface between the ORM and our code. This helps to keep us loosely coupled.

Lastly, we're motivated again by the dependency inversion principle: our service layer depends on a thin abstraction, and we attach a concrete implementation at the outside edge of the system. This lines up nicely with SQLAlchemy's own recommendations:

Keep the life cycle of the session (and usually the transaction) separate and external. The most comprehensive approach, recommended for more substantial applications, will try to keep the details of session, transaction, and exception management as far as possible from the details of the program doing its work.

-SQLALchemy "Session Basics" Documentation

<sup>1</sup> You may have come across the use of the word *collaborators* to describe objects that work together to achieve a goal. The unit of work and the repository are a great example of collaborators in the object-modeling sense. In responsibility-driven design, clusters of objects that collaborate in their roles are called *object neighborhoods*, which is, in our professional opinion, totally adorable.
