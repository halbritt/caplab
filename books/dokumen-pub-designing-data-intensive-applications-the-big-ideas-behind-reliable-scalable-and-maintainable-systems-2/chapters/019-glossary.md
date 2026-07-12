# Glossary

![](../assets/_page_626_Picture_1.jpeg)

The definitions in this glossary are short and simple, intended to convey the core idea but not the full subtleties of a term. For more detail, follow the references to the main text.

## asynchronous

Not waiting for something to complete (e.g., sending data over the network to another node), and not making any assumptions about how long it is going to take. See "Synchronous Versus Asynchronous Replication" on page 200, "Synchronous Versus Asynchronous Networks" on page 355, and "System Model and Reality" on page 380.

### atomic

- In the context of concurrency, describes an operation that appears to take effect at a single point in time, so another concurrent process can never encounter the operation in a "half-finished" state. See also isolation.
- 2. In the context of transactions, describes grouping together a set of writes that must either all be committed or all be rolled back, even if faults occur. See "Atomicity" on page 280 and "Two-Phase Commit" on page 324.

## backpressure

Forcing the sender of data to slow down when the recipient cannot keep up with it. Also known as *flow control*. See "When an Overloaded System Won't Recover" on page 38.

### batch process

A computation that takes a fixed (and usually large) set of data as input and produces other data as output, without modifying the input. See Chapter 11.

### hounded

Having a known upper limit or size. Used, for example, in the context of network delay (see "Timeouts and Unbounded Delays" on page 352) and datasets (see the introduction to Chapter 12).

## Byzantine fault

A fault that is characterized by a node behaving incorrectly in an arbitrary way (e.g., by sending contradictory or malicious messages to other nodes). See "Byzantine Faults" on page 377.

### cache

A component that remembers recently used data in order to speed up future reads of the same data. It is generally not complete; any data that is missing from the cache has to be fetched from

### CAP theorem

an underlying, slower data storage system that has a complete copy of the data.

### CAP theorem

A widely misunderstood theoretical result that is not useful in practice. See "The CAP theorem" on page 414.

### causality

The dependency between events that arises when one thing "happens before" another thing in a system—for example, a later event that occurs in response to, builds upon, or should be understood in the light of an earlier event. See "The happens-before relation and concurrency" on page 238.

### consensus

A fundamental problem in distributed computing concerning getting several nodes to agree on something (e.g., which node should be the leader for a database cluster). The problem is much harder than it seems at first glance. See "Consensus" on page 425.

## data warehouse

A database in which data from several OLTP systems has been combined and prepared to be used for analytics purposes. See "Data Warehousing" on page

### declarative

Describes the properties that something should have, but not the exact steps for how to achieve it. In the context of database queries, a query optimizer takes a declarative query and decides how it should best be executed. See "Terminology: Declarative Query Languages" on page 66.

### denormalize

To introduce some amount of redundancy or duplication in a normalized dataset, typically in the form of a cache or index, in order to speed up reads. A denormalized value is a kind of precomputed query result, similar to a materialized

view. See "Normalization, Denormalization, and Joins" on page 72.

### derived data

A dataset created from other data through a repeatable process, which you could run again if necessary. Usually, derived data is needed to speed up a particular kind of read access to the data. Indexes, caches, and materialized views are examples of derived data. See "Systems of Record and Derived Data" on page 10.

### deterministic

Describes a function that always produces the same output if you give it the same input. This means it cannot depend on random numbers, the time of day, network communication, or other unpredictable things. See "The Power of Determinism" on page 387.

## distributed

Running on several nodes connected by a network. Characterized by partial failures: a part of the system may be broken while other parts are still working, and it is often impossible for the software to know what exactly is broken. See "Faults and Partial Failures" on page 346.

Storing data in such a way that you believe it will not be lost, even if various faults occur. See "Durability" on page 282.

Extract-transform-load. The process of extracting data from a source database, transforming it into a form that is more suitable for analytical queries, and loading it into a data warehouse or batch processing system. See "Data Warehousing" on page 7.

### failover

In systems that have a single leader, failover is the process of moving the leadership role from one node to another. See "Handling Node Outages" on page 204.

### fault-tolerant

Able to recover automatically if something goes wrong (e.g., if a machine crashes or a network link fails). See "Reliability and Fault Tolerance" on page 43.

## flow control

See backpressure.

### follower

A replica that does not directly accept any writes from clients, but only processes data changes that it receives from a leader. Also known as a secondary, read replica, or hot standby. See "Single-Leader Replication" on page 198.

### full-text search

Searching text by arbitrary keywords, often with additional features such as matching similarly spelled words or synonyms. A full-text index is a kind of secondary index that supports such queries. See "Full-Text Search" on page 146.

### graph

A data structure consisting of vertices (things that you can refer to, also known as nodes or entities) and edges (connections from one vertex to another, also known as relationships or arcs). See "Graph-Like Data Models" on page 84.

### hash

A function that turns an input into a random-looking number. The same input always returns the same number as output. Two different inputs will likely have two different numbers as output, although two different inputs could produce the same output (this is called a collision). See "Sharding by Hash of Key" on page 258.

### idempotent

Describes an operation that can be safely retried: if it is executed more than once, it has the same effect as if it were executed only once. See "Idempotence" on page 528.

### index

A data structure that lets you efficiently search for all records that have a particular value in a particular field. See "Storage and Indexing for OLTP" on page 116.

### isolation

In the context of transactions, describes the degree to which concurrently executing transactions can interfere with each other. Serializable isolation provides the strongest guarantees, but weaker isolation levels are also used. See "Isolation" on page 281.

### inin

To bring together records that have something in common. Most commonly used when one record has a reference to another (a foreign key, a document reference, an edge in a graph) and a query needs to get the record that the reference points to. See "Normalization, Denormalization, and Joins" on page 72 and "Joins and Grouping" on page 471.

### leader

When data or a service is replicated across several nodes, the leader is the designated replica that is allowed to make changes. A leader may be elected through a protocol or manually chosen by an administrator. Also known as the primary or source. See "Single-Leader Replication" on page 198.

### linearizable

Behaving as if only a single copy of data is in the system, which is updated by atomic operations. See "Linearizability" on page 402.

### locality

A performance optimization: putting several pieces of data in the same place if they are frequently needed at the same time. See "Data locality for reads and writes" on page 82.

A mechanism to ensure that only one thread, node, or transaction can access something, and anyone else who wants to

access the same thing must wait until the lock is released. See "Two-Phase Locking" on page 313 and "Distributed Locks and Leases" on page 373.

### log

An append-only file for storing data. A write-ahead log is used to make a storage engine resilient against crashes (see "Making B-trees reliable" on page 127), a log-structured storage engine uses logs as its primary storage format (see "Log-Structured Storage" on page 118), a replication log is used to copy writes from a leader to followers (see "Single-Leader Replication" on page 198), and an event log can represent a data stream (see "Log-Based Message Brokers" on page 495).

## materialize

To perform a computation eagerly and write out its result, as opposed to calculating it on demand when requested. See "Event Sourcing and CQRS" on page 101.

### node

An instance of software running on a computer, which communicates with other nodes via a network in order to accomplish a task.

### normalized

Structured in such a way that there is no redundancy or duplication. In a normalized database, when a piece of data changes, you need to change it in only one place, not many copies in many places. See "Normalization, Denormalization, and Joins" on page 72.

### OLAP

Online analytical processing. An access pattern characterized by aggregating (e.g., count, sum, average) over a large number of records. See "Operational Versus Analytical Systems" on page 3.

### OLTP

Online transaction processing. An access pattern characterized by fast queries that read or write a small number of records. usually indexed by key. See "Operational Versus Analytical Systems" on page 3.

### percentile

A way of measuring the distribution of values by counting how many values are above or below a certain threshold. For example, the 95th percentile response time during some period is the time t such that 95% of requests in that period complete in less than t, and 5% take longer than t. See "Describing Performance" on page 37.

### primary key

A value (typically a number or a string) that uniquely identifies a record. In many applications, primary keys are generated by the system when a record is created (e.g., sequentially or randomly); they are not usually set by users. See also secondary index.

### quorum

The minimum number of nodes that need to vote on an operation before it can be considered successful. See "Using quorums for reading and writing" on page

## rehalance

To move data or services from one node to another in order to spread the load fairly. See "Sharding of Key-Value Data" on page 255.

### replication

Keeping a copy of the same data on several nodes (replicas) so that it remains accessible if a node becomes unreachable. See Chapter 6.

## schema

A description of the structure of data, including its fields and datatypes. Whether data conforms to a schema can be checked at various points in the data's lifetime (see "Schema flexibility in the document model" on page 80), and a schema can change over time (see Chapter 5).

### secondary index

An additional data structure that is maintained alongside the primary data storage and that allows you to efficiently search for records that match a certain kind of condition. See "Multicolumn and Secondary Indexes" on page 132 and "Sharding and Secondary Indexes" on page 268.

### seria lizable

An isolation guarantee that if several transactions execute concurrently, they behave the same as if they had executed one at a time, in a serial order. See "Serializability" on page 308.

### sharding

Splitting a large dataset or computation that is too big for a single machine into smaller parts and spreading them across several machines. Also known as partitioning. See Chapter 7.

### shared-nothing

An architecture in which independent nodes—each with its own CPUs, memory, and disks-are connected via a conventional network, in contrast to sharedmemory or shared-disk architectures. See "Shared-Memory, Shared-Disk, and Shared-Nothing Architectures" on page 51.

### skew

- 1. Imbalanced load across shards, such that some shards have lots of requests or data and others have much less. Also known as hot spots. See "Skewed Workloads and Relieving Hot Spots" on page 263.
- 2. A timing anomaly that causes events to appear in an unexpected, nonsequential order. See the discussions of read skew in "Snapshot Isolation and Repeatable Read" on page 293, write skew in "Write Skew and Phantoms" on page 303, and clock skew in "Timestamps for ordering events" on page 362.

### split brain

A scenario in which two nodes simultaneously believe themselves to be the leader,

which may cause system guarantees to be violated. See "Handling Node Outages" on page 204 and "The Majority Rules" on page 372.

### stored procedure

A way of encoding the logic of a transaction such that it can be entirely executed on a database server, without communicating back and forth with a client during the transaction. See "Actual Serial Execution" on page 309.

### stream process

A continually running computation that consumes a never-ending stream of events as input and derives output from it. See Chapter 12.

## synch ron ous

The opposite of asynchronous.

### system of record

A system that holds the primary, authoritative version of data, also known as the source of truth. Changes are first written here, and other datasets may be derived from the system of record. See "Systems of Record and Derived Data" on page 10.

### timeout

One of the simplest ways of detecting a fault-namely, by observing the lack of a response within a certain amount of time. However, it is impossible to know whether a timeout is due to a problem with the remote node or an issue in the network. See "Timeouts and Unbounded Delays" on page 352.

### total order

A way of comparing two things (e.g., timestamps) that allows you to always say which one is greater and which one is lesser. An ordering in which some things are incomparable (you cannot say which is greater or smaller) is called a partial order.

### transaction

Grouping together several reads and writes into a logical unit in order to

## two-phase commit (2PC)

simplify error handling and concurrency issues. See Chapter 8.

## two-phase commit (2PC)

An algorithm to ensure that several database nodes either all atomically commit or all abort a transaction. See "Two-Phase Commit" on page 324.

## two-phase locking (2PL)

An algorithm for achieving serializable isolation that works by a transaction acquiring a lock on all data it reads or writes and holding the lock until the end of the transaction. See "Two-Phase Locking" on page 313.

## unbounded

Not having any known upper limit or size. The opposite of bounded.
