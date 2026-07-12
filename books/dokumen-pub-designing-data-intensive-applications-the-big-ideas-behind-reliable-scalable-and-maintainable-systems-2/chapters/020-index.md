# Index

| Symbols                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | adjacency list/matrix, 85                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3FS (distributed filesystem), 459                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | admission control, 357                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| A aborts (transactions), 277, 280 cascading, 291\nin two-phase commit, 325 performance of optimistic concurrency control, 322 retrying aborted transactions, 287 abstraction, 16, 55, 66, 335 accidental complexity, 55 accountability, 587 accounting (financial data), 108, 509 Accumulo (database), 82, 140 ACID properties (transactions), 279 atomicity, 280, 284 consistency, 280, 576 durability, 128, 282\nisolation, 281, 284 acknowledgments (messaging), 493 active/active replication (see multi-leader replication) active/passive replication (see leader-based replication) ActiveMQ (messaging), 190, 330, 492 ActiveRecord (object-relational mapper), 68, 288 activity (workflows) (see workflow engines) actor model, 191, 518     (see also event-driven architecture) ad hoc queries, 478 | Advanced Message Queuing Protocol (AMQP), 492 (see also messaging systems) comparison to log-based messaging, 497, 500 message ordering, 494 aerospace systems, 378 Aerospike (database), 286 AGE (graph database), 88 aggregation data cubes and materialized views, 144\nin batch processes, 456\nin stream processes, 515 aggregation pipeline (MongoDB), 73, 82 Agile, 55 minimizing irreversibility, 452, 546 moving faster with confidence, 578 agreement, 427, 432 (see also consensus) AI (artificial intelligence), 147 (see also machine learning) AI Act (European Union), 24 AirByte (data connector), 8 Airflow (workflow scheduler), 188, 453, 465 cloud data warehouse integration, 474\nuse for ETL, 476 Akamai response time study, 41 Akka (actor framework), 191 algorithms algorithm correctness, 382 |
| adaptive capacity, 264                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | B-trees, 125-128                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | for distributed systems, 380                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

```
mergesort, 120, 471
                                                     relation to batch processing, 477-478
                                                     schemas for, 77-79
   scheduling, 464
   SSTables and LSM-trees, 119-124
                                                     snapshot isolation for queries, 294
all-to-all replication topologies, 218
                                                     stream analytics, 515
AllegroGraph (database), 85, 96
                                                  analytics engineers/engineering, 4
ALTER TABLE statement (SQL), 81
                                                  anti-entropy, 231
                                                  Antithesis (deterministic simulation testing),
Amazon
   Dynamo (see Dynamo (database))
   response time study, 41
                                                  Apache Accumulo (see Accumulo)
Amazon EBS (virtual block device), 16, 203
                                                  Apache ActiveMQ (see ActiveMQ)
Amazon Kinesis (messaging), 135
                                                  Apache Arrow (see Arrow (data format))
Amazon Neptune (graph database), 85
                                                  Apache Avro (see Avro)
   Cypher query language, 88
                                                  Apache Beam (see Beam)
   SPARQL query language, 96
                                                  Apache BookKeeper (see BookKeeper)
Amazon S3 (object storage), 15, 202, 453, 459,
                                                  Apache Cassandra (see Cassandra)
                                                  Apache Curator (see Curator)
   checking data integrity, 576
                                                  Apache DataFusion (see DataFusion (query
   conditional writes, 376
                                                     engine))
   object size, 16
                                                  Apache Druid (see Druid (database))
   S3 Express One Zone, 460, 461
                                                  Apache Flink (see Flink (processing frame-
   use in MapReduce, 466
                                                     work))
Amazon Web Services (AWS)
                                                  Apache Giraph, 478
   Amazon EBS, 16, 203
                                                  Apache HBase (see HBase)
                                                  Apache Hive (see Hive (data warehouse))
   Amazon Kinesis, 135
                                                  Apache Iceberg (see Iceberg (table format))
   Amazon Neptune, 85, 88, 96
   Amazon S3 (see Amazon S3 (object stor-
                                                  Apache Jena (see Jena)
      age))
                                                  Apache Kafka (see Kafka)
                                                  Apache Kinesis (messaging), 497
   Aurora, 15
   ClockBound, 365, 366
                                                  Apache Lucene (see Lucene)
   correctness testing, 384
                                                  Apache Oozie (see Oozie (workflow scheduler))
   DynamoDB (see DynamoDB (database))
                                                  Apache ORC (see ORC (data format))
   Kinesis (see Kinesis (messaging))
                                                  Apache Parquet (see Parquet (data format))
amplification
                                                  Apache Pig (query language), 474
   of bias, 587
                                                  Apache Pinot (see Pinot (database))
   of failures, 544
                                                  Apache Pulsar (see Pulsar)
   of tail latency, 41, 269
                                                  Apache Qpid (see Qpid)
   write amplification, 130
                                                  Apache Samza (see Samza)
AMQP (see Advanced Message Queuing Proto-
                                                  Apache Solr (see Solr)
   col (AMQP))
                                                  Apache Spark (see Spark (processing frame-
analytical systems, 4
                                                     work))
   as derived data systems, 11
                                                  Apache Storm (see Storm)
   ETL from operational systems, 7
                                                  Apache Superset (see Superset (data visualiza-
   governance, 10
                                                     tion software))
   operational systems compared with, 3-12
                                                  Apache Thrift (see Thrift)
analytics, 4-12
                                                  Apache Tinkerpop Gremlin, 474
                                                  Apache ZooKeeper (see ZooKeeper)
   comparison to transaction processing, 5
   data normalization, 74
                                                  Apama (stream analytics), 515
   data warehousing (see data warehousing)
                                                  APIs (see application programming interfaces
   predictive (see predictive analytics)
                                                     (APIs))
```

| append-only files (see logs)                  | distributed transactions, 323-335             |
|-----------------------------------------------|-----------------------------------------------|
| append-only log, 427                          | for multi-object transactions, 285            |
| application programming interfaces (APIs), 65 | for single-object writes, 286                 |
| for change streams, 506                       | relation to consensus, 432                    |
| for distributed transactions, 330             | auditability, 575-578                         |
| for services, 180-186                         | designing for, 577                            |
| (see also services)                           | self-auditing systems, 577                    |
| evolvability, <mark>186</mark>                | through immutability, 509                     |
| RESTful, 181                                  | tools for auditable data systems, 578         |
| application state (see state)                 | Aurora (cloud database), 15                   |
| approximate search (see similarity search)    | Aurora DSQL (database), 295                   |
| archival storage, data from databases, 179    | auto-scaling, 265                             |
| arcs (see edges)                              | Automerge (sync engine), 222                  |
| ArcticDB (database), 105                      | availability, 43                              |
| arithmetic mean, 40                           | (see also fault tolerance)                    |
| arrays                                        | in CAP theorem, 415                           |
| array databases, 107                          | in leader election, 436                       |
| multidimensional, 105                         | in service level agreements (SLAs), 42        |
| Arrow (data format), 138, 475                 | availability zones, 45, 212                   |
| artificial intelligence (AI), 147             | Avro (data format), 10, 172-177               |
| (see also machine learning)                   | dynamically generated schemas, 176            |
| ASCII text, 169                               | object container files, 175, 180              |
| ASN.1 (schema language), 177                  | reader determining writer's schema, 175       |
| associative table, 75, 87                     | schema evolution, 173                         |
| asynchronous communication, 190               | use in batch processing, 466                  |
| asynchronous networks, 347, 603               | awk (Unix tool), 454, 455, 461                |
| comparison to synchronous networks, 355       | AWS (Amazon Web Services) (see Amazon         |
| system model, 381                             | Web Services (AWS))                           |
| asynchronous replication, 200, 603            | Axon Framework, 105                           |
| data loss on failover, 205                    | Azkaban (workflow scheduler), 453             |
| reads from asynchronous follower, 209         | Azure Blob Storage (object storage), 15, 202, |
| with multiple leaders, 215                    | 376                                           |
| Asynchronous Transfer Mode (ATM), 357         | Azure Cosmos DB, 228                          |
| atomic broadcast, 430                         | Azure managed disks, 16                       |
| atomic clocks, 365, 366                       | Azure SQL DB (database), 15                   |
| (see also clocks)                             | Azure Storage, 460                            |
| atomicity (concurrency), 603                  | Azure Synapse Analytics (database), 15        |
| atomic increment, 286                         | Azure Virtual Machines, 465                   |
| compare-and-set (CAS), 302, 406               |                                               |
| (see also compare-and-set (CAS))              | В                                             |
| denormalized data, 74                         | B-trees (indexes), 115, 125-128               |
| fetch-and-add/increment, 417, 425, 431        | B+ trees, 128                                 |
| write operations, 300                         | branching factor, 126                         |
| atomicity (transactions), 280, 284, 603       | comparison to LSM-trees, 129-132              |
| atomic commit, 427                            | crash recovery, 127                           |
| avoiding, 568, 575                            | growing by splitting a page, 126              |
| blocking and nonblocking, 328                 | immutable variants, 128, 298                  |
| in stream processing, 329, 334, 527           | similarity to shard splitting, 257            |
| maintaining derived data, <mark>502</mark>    |                                               |

| variants, 128                                 | BERT (language model), 148                         |
|-----------------------------------------------|----------------------------------------------------|
| B2 (object storage), 459                      | BGP (Border Gateway Protocol), 357                 |
| Backblaze B2 (see B2 (object storage))        | BI (business intelligence), 4                      |
| backend, 3                                    | bias, 587                                          |
| backoff, exponential, 38, 288                 | bidirectional replication (see multi-leader repli- |
| backpressure, 38, 129, 489, 603               | cation)                                            |
| in batch processing, 464                      | big ball of mud, <mark>54</mark>                   |
| in TCP, 349                                   | big data, versus data minimization, 25, 596        |
| backups                                       | BigQuery (database), 15, 135, 453                  |
| database snapshot for replication, 202        | DataFrames, 474                                    |
| in multitenant systems, 254                   | sharding and clustering, 262                       |
| integrity of, <mark>576</mark>                | shuffling data, 470                                |
| snapshot isolation for, 294                   | snapshot isolation support, 295                    |
| using object storage, 202                     | Bigtable (database)                                |
| versus replication, 198                       | sharding scheme, 257                               |
| backward compatibility, 162                   | storage layout, 121                                |
| BadgerDB (database), 318                      | wide-column data model, 82, 140                    |
| bash shell (Unix), 116                        | binary data encodings, 167-178                     |
| Basically Available, Soft state, and Eventual | Avro, 172-177                                      |
| consistency (BASE), contrast to ACID, 279     | MessagePack, 168-169                               |
| batch processing, 451-482, 603                | Protocol Buffers, 169-171                          |
| and functional programming, 468               | binary strings, lack of support in JSON and        |
| benefits of, 451                              | XML, 165                                           |
| combining with stream processing, 546         | binlog (MySQL), 202, 208                           |
| comparison to stream processing, 513          | Bitcoin (cryptocurrency), 578                      |
| dataflow engines, 468-469                     | Byzantine fault tolerance, 378                     |
| fault tolerance, 465, 490                     | concurrency bugs in exchanges, 289                 |
| for data integration, 544-546                 | bitmap indexes, 139                                |
| graphs and iterative processing, 478          | BitTorrent uTP protocol, 348                       |
| high-level APIs and languages, 473-474        | Bkd-trees (indexes), 145                           |
| in cloud data warehouses, 474                 | blameless postmortems, 48                          |
| in distributed systems, 457                   | Blazegraph (database), <mark>85</mark> , 96        |
| join and group by, 471-473                    | blob storage (see object storage)                  |
| limitations, 452                              | block (filesystem), 458                            |
| log-based messaging and, 500                  | block device (disk), 16                            |
| maintaining derived state, 544                | blockchains, 108, 378, 426, 578                    |
| measuring performance, 452                    | blocking atomic commit, 328                        |
| models of, 466                                | Bloom filter (algorithm), 122, 129, 515            |
| resource allocation, 463-464                  | BookKeeper (replicated log), 439                   |
| resource managers, 462                        | Border Gateway Protocol (BGP), 357                 |
| schedulers, 462                               | bounded datasets, 481, 603                         |
| serving derived data, 479-481                 | (see also batch processing)                        |
| shuffling data, 469-471                       | bounded delays, 603                                |
| task execution, 462                           | in networks, 355                                   |
| use cases, 476-481                            | process pauses, 369                                |
| using Unix tools (example), 454-457           | BPEL (Business Process Execution Language),        |
| batch processing frameworks, comparison to    | 187                                                |
| operating systems, 457                        | BPMN (Business Process Model and Notation)         |
| Beam (dataflow library), 515, 546             | 187, 188                                           |

| broadcast (see shared logs)                 | lightweight transactions, 286              |
|---------------------------------------------|--------------------------------------------|
| brokerless messaging, 490                   | linearizability, lack of, 412              |
| BSP (bulk synchronous parallel), 478        | log-structured storage, 121                |
| BTM (transaction coordinator), 325          | multi-region support, 236                  |
| Bufstream (messaging), 499                  | secondary indexes, 270                     |
| build or buy, 12                            | use of clocks, 234                         |
| bulk synchronous parallel (BSP), 478        | vnodes (sharding), 252                     |
| bursty network traffic patterns, 356        | cat (Unix tool), 454                       |
| business analyst, 4, 9                      | catalog, 136                               |
| business data processing, 5                 | causal context, 242                        |
| business intelligence (BI), 4               | (see also causal dependencies)             |
| Business Process Execution Language (BPEL), | causal dependencies, 238-242               |
| 187                                         | capturing, 242, 542, 543, 560              |
| Business Process Model and Notation (BPMN), | in transactions, 319                       |
| 188                                         | sending message to friends (example), 543  |
| example, 187                                | causality, 604                             |
| byte sequence, encoding data in, 163        | causal ordering, 420                       |
| Byzantine faults, 377-380, 381, 603         | consistency with, 420-425                  |
| Byzantine fault-tolerant systems, 378       | happens-before relation, 238               |
| Byzantine Generals Problem, 377             | in serializable transactions, 319-322      |
|                                             | ordering events to capture, 543            |
| consensus algorithms and, 426, 578          |                                            |
| •                                           | violations of, 213, 220, 364               |
| C                                           | with synchronized clocks, 365              |
| caches, 134, 603                            | CCPA (California Consumer Privacy Act), 24 |
| and materialized views, 143                 | CDC (see change data capture (CDC))        |
| as derived data, 11, 547-551                | cell-based architecture, 254               |
| in CPUs, 143, 416                           | CEP (complex event processing), 514        |
| invalidation and maintenance, 501, 516      | CephFS (distributed filesystem), 453, 460  |
| linearizability, 403                        | certificate transparency, 578              |
| local disks in the cloud, 16                | cgroups, 462                               |
| calendar sync, 220, 222                     | chain of commands, 456                     |
| California Consumer Privacy Act (CCPA), 24  | change data capture (CDC), 208, 503        |
| Camunda (workflow engine), 188              | API support for change streams, 506        |
| canonical version (of data), 11             | comparison to event sourcing, 507          |
| CAP theorem, 414-415, 604                   | implementing, 504                          |
| capacity planning, 17                       | initial snapshot, 504                      |
| Cap'n Proto (data format), 164              | log compaction, 505                        |
| carbon emissions, 20                        | change stream, 199                         |
| CAS (see compare-and-set (CAS))             | changelogs, <mark>509</mark>               |
| cascading aborts, 291                       | change data capture, 503                   |
| cascading failures, 47, 265, 352            | in stream joins, <mark>524</mark>          |
| Cassandra (database)                        | log compaction, 505                        |
| change data capture, 504, 506               | chaos engineering, 44, 385                 |
| compaction strategy, 124                    | checkpointing                              |
| consistency level ANY, 236                  | in high-performance computing, 23          |
| hash-range sharding, 258, 262               | in stream processors, 527                  |
| last-write-wins conflict resolution, 237    | circuit breaker (limiting retries), 38     |
| leaderless replication, 229                 | circuit-switched networks, 355             |
|                                             | circular buffers, 498                      |

| circular replication topologies, 218            | code generation                                             |
|-------------------------------------------------|-------------------------------------------------------------|
| Citus (database), <mark>260</mark>              | for query execution, 142                                    |
| claiming a username (example), 306              | with Protocol Buffers, 169                                  |
| ClickHouse (database), 6, 15, 517               | collaborative editing, 220                                  |
| clickstream data, analysis of, <mark>471</mark> | column families (Bigtable), 82, 140                         |
| clients                                         | column-oriented storage, 136-143                            |
| calling services, 180                           | column compression, 139                                     |
| offline-capable, 220, 557                       | Parquet, 137, 180                                           |
| pushing state changes to, 558                   | sort order in, 140-141                                      |
| request routing, 266                            | vectorized processing, 142                                  |
| ClockBound (time sync), 365, 366                | versus wide-column model, 140                               |
| clocks, 358-371                                 | writing to, 141                                             |
| atomic clocks, 365, 366                         | comma-separated values (CSV), 116, 165                      |
| confidence interval, 364-366                    | command query responsibility segregation                    |
| for global snapshots, 365                       | (CQRS), 101-105, 510                                        |
| hybrid logical clocks, 422                      | commands (event sourcing), 102                              |
| logical (see logical clocks)                    | commit point, 326                                           |
| skew, 362-365, 412                              | commits (transactions), 277                                 |
| slewing, 360                                    | atomic commit, 323-335                                      |
| synchronization and accuracy, 360-362           | (see also atomicity; transactions)                          |
| synchronization using GPS, 358, 361, 365,       | read-committed isolation, 290                               |
| 366                                             | three-phase commit (3PC), 328                               |
| time-of-day versus monotonic clocks, 359        | two-phase commit (2PC), 324-328                             |
| timestamping events, 521                        | Common Object Request Broker Architecture                   |
| cloud native, 14-18                             | (CORBA), 183                                                |
| cloud services, 12-23                           | commutative operations, 303                                 |
| availability zones, 45, 212                     | compaction                                                  |
| data warehouses, 135                            | of changelogs, <mark>505</mark>                             |
| need for service discovery, 440                 | (see also logs, compaction)                                 |
| pros and cons, 13-14                            | of log-structured storage, 120                              |
| quotas, 18                                      | issues with, 129                                            |
| regions (see regions (geographic distribu-      | size-tiered and leveled approaches, 124,                    |
| tion))                                          | 131                                                         |
| serverless, 22                                  | compare-and-set (CAS), 302, 406                             |
| shared resources, 354                           | implementing locks, 438                                     |
| versus supercomputing, 23                       | implementing uniqueness constraints, 409                    |
| Cloudflare                                      | on object storage, 203                                      |
| R2 (see R2 (object storage))                    | relation to consensus, <b>413</b> , <b>425</b> , <b>429</b> |
| clustered indexes, 133                          | relation to fencing tokens, 376                             |
| clustering (record ordering), <mark>262</mark>  | relation to transactions, 286                               |
| CMS (concurrent mark sweep), 370                | compatibility, 178                                          |
| CockroachDB (database)                          | calling services, 186                                       |
| consensus-based replication, 199                | foward and backward, 162                                    |
| consistency model, 408                          | properties of encoding formats, 192                         |
| key-range sharding, 252, 257                    | using databases, 178-180                                    |
| serializable transactions, 318                  | compensating transactions, 510, 574                         |
| sharded secondary indexes, 271                  | compilation, 142                                            |
| transactions, 279, 333                          | complex event processing (CEP), 514                         |
| use of model-checking, 385                      | complexity                                                  |

| 3:-4:11:                                                     | L. L                                                 |
|--------------------------------------------------------------|------------------------------------------------------|
| distilling in theoretical models, 384                        | by aborting transactions, 318                        |
| essential and accidental, 55                                 | by apologizing, 574                                  |
| hiding using abstraction, 66                                 | in leaderless systems, 237                           |
| managing, 54<br>composing data systems (see unbundling data- | last write wins (LWW), 224, 363                      |
| bases)                                                       | using atomic operations, 302 using CRDTs and OT, 228 |
| compression, in SSTables, 119                                | determining what is a conflict, 228, 568             |
| compute-intensive applications, 1                            | in leaderless replication, 237                       |
| computer games, <mark>222</mark>                             | lost updates, 299-303                                |
| concatenated indexes, 145                                    | materializing, 308                                   |
| concurrency                                                  | siblings, 225, 240, 241                              |
| actor programming model, 191, 518                            | write skew (transaction isolation), 303-308          |
| (see also event-driven architecture)                         | Confluent                                            |
| bugs from weak transaction isolation, 289                    | Freight (messaging), 203, 499                        |
| conflict resolution, 222-229                                 | schema registry, <mark>166, 176</mark>               |
| definition, 223                                              | congestion (networks)                                |
| detecting concurrent writes, 237-242                         | avoidance, 349                                       |
| dual writes, problems with, 502                              | limiting accuracy of clocks, 364                     |
| happens-before relation, 238                                 | queueing delays, <mark>353</mark>                    |
| in replicated systems, 209-242, 402-417                      | consensus, 425-443, 604                              |
| lost updates, 299                                            | algorithms, 426, 433                                 |
| multiversion concurrency control (MVCC),                     | consensus numbers, 431                               |
| 295, 365                                                     | coordination services, 437-440                       |
| optimistic concurrency control, 318                          | cost of, 437                                         |
| ordering of operations, 405                                  | impossibility of, 426                                |
| reducing, through event logs, 511                            | preventing split brain, 434                          |
| time and relativity, 239                                     | reconfiguration, 436                                 |
| transaction isolation, 281                                   | relation to atomic commitment, 432                   |
| write skew (transaction isolation), 303-308                  | relation to compare-and-set (CAS), 413, 429          |
| concurrent mark sweep (CMS), 370                             | relation to fetch-and-add, 431                       |
| conditional write, 302                                       | relation to replication, 433                         |
| in transactions, 286                                         | relation to shared logs, 429                         |
| on object storage, <mark>203</mark>                          | relation to uniqueness constraints, 567              |
| conference management system (example), 101                  | safety and liveness properties, 428                  |
| confidence interval, 364                                     | single-value consensus, 427                          |
| conflict-free replicated datatypes (CRDTs), 227              | consent (GDPR), <mark>592</mark>                     |
| for leaderless replication, 240                              | consistency, 280, 571                                |
| preventing lost updates, 303                                 | across different databases, 205, 502, 511, 541       |
| conflicts                                                    | causal, 213, 220, 543                                |
| avoidance, 223                                               | consistent prefix reads, 213-214                     |
| causal dependencies, 238                                     | consistent snapshots, 202, 293-299, 365,             |
| conflict detection                                           | 504, 548                                             |
| in distributed transactions, 332                             | (see also snapshots)                                 |
| in log-based systems, 567                                    | crash recovery, 128                                  |
| in serializable snapshot isolation (SSI),                    | defined, <mark>561</mark>                            |
| 321                                                          | enforcing constraints (see constraints)              |
| in two-phase commit, 326                                     | eventual, 209                                        |
| conflict resolution, 222-229                                 | (see also eventual consistency)                      |
| automatic, 226                                               | in ACID transactions, 280, 576                       |
|                                                              |                                                      |

| in CAP theorem, 415                            | failure, 327                             |
|------------------------------------------------|------------------------------------------|
| in leader election, 436                        | in XA transactions, 330-333              |
| in microservices, 21                           | recovery, 331                            |
| linearizability, 215, 402-417                  | copy-on-write (B-trees), 128, 298        |
| meanings of, 280                               | CORBA (Common Object Request Broker      |
| monotonic reads, 212                           | Architecture), 183                       |
| of multi-leader replication, 217               | coronal mass ejection (see solar storm)  |
| of secondary indexes, 287, 298, 541, 548       | correctness                              |
| read-after-write, 210-211                      | auditability, 575-578                    |
| strong (see linearizability)                   | Byzantine fault tolerance, 378           |
| timeliness and integrity, 571                  | dealing with partial failures, 346       |
| using quorums, 233, 412                        | in log-based systems, 566-570            |
| consistent hashing, 263                        | of algorithm within system model, 382    |
| consistent prefix reads, 213                   | of derived data, 577                     |
| constraints (databases), <mark>281, 305</mark> | of immutable data, 510                   |
| coordination avoidance, 574                    | of personal data, <mark>587, 593</mark>  |
| ensuring idempotence, 564                      | of time, 220, 360-366                    |
| in log-based systems, <mark>566-570</mark>     | of transactions, 281, 561, 576           |
| across multiple shards, 568                    | timeliness and integrity, 571-575        |
| in two-phase commit, 324, 326                  | corruption of data                       |
| relation to consensus, 567                     | detecting, 565, 576-578                  |
| requiring linearizability, 409                 | due to pathological memory access, 45    |
| Consul (coordination service), 437, 440        | due to radiation, 378                    |
| consumers (message streams), 190, 488          | due to split brain, 205, 373             |
| backpressure, 489                              | due to weak transaction isolation, 289   |
| consumer groups, 493                           | integrity as absence of, 571             |
| consumer offsets in logs, 498                  | network packets, 379                     |
| failures, 498                                  | on disks, <mark>283</mark>               |
| fan-out, 35, 493, 497                          | preventing using write-ahead logs, 128   |
| load balancing, 492, 497                       | recovering from, 452                     |
| not keeping up with producers, 489, 498,       | cosine similarity (semantic search), 148 |
| 550                                            | Couchbase (database)                     |
| content models (JSON Schema), 166              | document data model, 67                  |
| contention                                     | durability, 134                          |
| between transactions, 288                      | hash sharding, 260                       |
| blocking threads, 367                          | join support, 83                         |
| performance of optimistic concurrency con-     | rebalancing, 264                         |
| trol, 318                                      | vBuckets (sharding), 252                 |
| under two-phase locking, 315                   | CouchDB (database), 453                  |
| context switches, 39, 368                      | as sync engine, 222                      |
| convergence (conflict resolution), 226-228     | B-tree storage, 298                      |
| coordination                                   | conflict resolution, 225                 |
| avoidance, 574                                 | coupling (loose and tight), 56           |
| cross-datacenter, 542                          | covering indexes, 133                    |
| cross-region, 216                              | CozoDB (database), 96                    |
| cross-shard ordering, 313, 365, 434, 568       | CPUs                                     |
| routing requests to shards, 267                | cache coherence and memory barriers, 416 |
| services, 408, 437-440                         | caching and pipelining, 143              |
| coordinator (in 2PC), <mark>325</mark>         | computing the wrong result, 45           |

| SIMD instructions, 143                           | data mesh, 477                                                                 |
|--------------------------------------------------|--------------------------------------------------------------------------------|
| CQRS (command query responsibility segrega-      | data minimization, 25, 596                                                     |
| tion), 101-105, 510                              | data models, 65-108                                                            |
| crash-stop and crash-recovery faults, 381        | DataFrames and arrays, 105                                                     |
| CRDTs (see conflict-free replicated datatypes)   | graph-like models, 84-101                                                      |
| CREATE INDEX statement (SQL), 132, 548           | Datalog language, 96-98                                                        |
| credit rating agencies, 587                      | property graphs, <mark>86</mark>                                               |
| crypto-shredding, 104, 512                       | RDF and triple stores, 92-96                                                   |
| cryptocurrencies, 108                            | relational model versus document model,                                        |
| cryptography, <mark>565</mark>                   | 67-84                                                                          |
| CSV (comma-separated values), 116, 165           | supporting multiple, 101                                                       |
| Curator (ZooKeeper recipes), 408, 439            | data pipelines, 10, 11, 476                                                    |
| Cypher (query language), <mark>85, 88, 95</mark> | data protection regulations (see General Data<br>Protection Regulation (GDPR)) |
| D                                                | data residence laws, 20, 255                                                   |
| Daft (processing framework)                      | data science/scientists, 4, 9                                                  |
| DataFrames, 475                                  | data silo, 7                                                                   |
| shuffling data, 470                              | data systems                                                                   |
| DAG (see directed acyclic graphs (DAG))          | correctness, constraints, and integrity,                                       |
| Dagster (workflow scheduler), 188, 453, 465,     | 561-578                                                                        |
| 474                                              | data integration, 539-546                                                      |
| dashboard (business intelligence), 6             | goals for using, 2                                                             |
| Dask (processing framework), 105                 | heterogeneous, keeping in sync, 501                                            |
| data catalog, 136                                | maintainability, <mark>52-56</mark>                                            |
| data connectors, 8                               | possible faults in, 277                                                        |
| data contracts, 477, 507                         | reliability, 43-49                                                             |
| data corruption (see corruption of data)         | hardware faults, 44                                                            |
| data cubes, 144                                  | human errors, 47                                                               |
| data engineers/engineering, 4                    | importance of, 48                                                              |
| data fabric, 477                                 | software faults, 46                                                            |
| data formats (see encoding)                      | scalability, 49-52                                                             |
| data infrastructure, 3                           | unbundling databases, 546-561                                                  |
| data integration, 539-546                        | unreliable clocks, 358-371                                                     |
| batch and stream processing, 544-546             | data warehousing, 7, 604                                                       |
| maintaining derived state, 544                   | cloud-based solutions, 135                                                     |
| reprocessing data, 545                           | ETL (extract-transform-load), 7, 501                                           |
| unifying, 546                                    | for batch processing, 453                                                      |
| by unbundling databases, 546-561                 | keeping data systems in sync, 501                                              |
| combining tools by deriving data, 540-544        | schema design, 77                                                              |
| derived data versus distributed transac-         | sharding and clustering, 262                                                   |
| tions, 541                                       | slowly changing dimension (SCD), 526                                           |
| limits of total ordering, 542                    | data-intensive applications, 1                                                 |
| ordering events to capture causality, 543        | database administrator (DBA), 17                                               |
| reasoning about dataflows, 541                   | database-internal distributed transactions, 329                                |
| need for, 11                                     | 333                                                                            |
| using batch processing, 452, 476                 | databases                                                                      |
| data lake, 9, 477                                | archival storage, 179                                                          |
| data locality (see locality)                     | comparison with message brokers, 492                                           |
| and recallly (see recallly)                      | dataflow through, 178                                                          |

| end-to-end argument for, 565-566, 577         | in Protocol Buffers, 171                     |
|-----------------------------------------------|----------------------------------------------|
| relation to event streams, 500-513            | numbers in XML and JSON, 165                 |
| (see also changelogs)                         | Datensparsamkeit, 25                         |
| API support for change streams, 506,          | Datomic (database)                           |
| 553                                           | B-tree storage, 298                          |
| change data capture, <mark>503-506</mark>     | data model, <mark>85</mark> , 92             |
| event sourcing, 507                           | Datalog query language, 96                   |
| keeping systems in sync, 501-502              | excision (deleting data), 512                |
| philosophy of immutable events,               | languages for transactions, 312              |
| 508-513                                       | serial execution of transactions, 309        |
| unbundling, 546-561                           | Daylight Saving Time (DST), 359              |
| composing data storage technologies,          | Db2 (database), 504                          |
| 547-551                                       | DBA (database administrator), 17             |
| designing applications around dataflow,       | DCOM (Distributed Component Object           |
| 551-555                                       | Model), 183                                  |
| observing derived state, 555-561              | DDD (domain-driven design), 55, 102          |
| Databricks, 136                               | DDSketch (percentile estimation), 42         |
| datacenters                                   | dead letter queues (DLQs), 495               |
| failures of, <mark>45</mark>                  | deadlocks, 301                               |
| geographically distributed (see regions (geo- | detection, in distributed transaction, 332   |
| graphic distribution))                        | in two-phase locking (2PL), 315              |
| multitenancy and shared resources, 354        | Debezium (change data capture), 504          |
| network architecture, 23                      | Cassandra, <mark>506</mark>                  |
| network faults, 350                           | for data integration, 551                    |
| dataflow, 178-191, 551-555                    | declarative languages, 66, 604               |
| correctness of dataflow systems, 572          | and sync engines, 221                        |
| dataflow engines, 468                         | Datalog, 96                                  |
| comparison to stream processing, 513          | in document databases, 83                    |
| DataFrames, 475                               | recursive SQL queries, 90                    |
| support in batch processing frameworks,       | SPARQL, 95                                   |
| 453                                           | decoding, 163                                |
| event-driven, 189-191                         | DeepSeek (see 3FS)                           |
| reasoning about, 541                          | delays                                       |
| through databases, 178                        | bounded network delays, 355                  |
| through services, 180-186                     | bounded process pauses, 369                  |
| workflow engines (see workflow engines)       | unbounded network delays, 353                |
| DataFrames, 105                               | unbounded process pauses, 367                |
| implementation, 475                           | deleting data, 512                           |
| in batch processing, 475                      | in LSM storage, <mark>132</mark>             |
| in notebooks, 479                             | legal basis, 24                              |
| support in batch processing frameworks,       | Delta Lake (table format), 122, 136, 262     |
| 453                                           | demilitarized zone (DMZ), 480                |
| DataFusion (query engine), 135                | denormalization (data representation), 72-77 |
| Datalog (query language), 85, 96-98           | 604                                          |
| Datastream (change data capture), 506         | in derived data systems, 11                  |
| datatypes                                     | in event sourcing/CQRS, 103                  |
| binary strings in XML and JSON, 165           | in social network case study, 74             |
| conflict-free, 227                            | materialized views, 143                      |
| in Avro encodings, 172                        | updating derived data, 284, 287, 540         |

| versus normalization, 511                   | faults and partial failures, 346               |
|---------------------------------------------|------------------------------------------------|
| derived data, 11, 487, 604                  | formalization of consensus, 427                |
| batch processing, 451                       | impossibility results, 415, 426                |
| event sourcing and CQRS, 101                | issues with failover, 205                      |
| from change data capture, 504               | multi-region (see regions (geographic distri   |
| maintaining derived state through logs,     | bution))                                       |
| 501-506, 508-512                            | network problems, 347-357                      |
| observing, by subscribing to streams, 559   | problems with, 20                              |
| outputs of batch and stream processing, 544 | quorums, relying on, 372                       |
| through application code, 551               | reasons for using, 19, 197                     |
| versus distributed transactions, 541        | synchronized clocks, relying on, 362-366       |
| deserialization (see decoding)              | system models, 380-387                         |
| design patterns, 55                         | use of clocks and time, 358                    |
| deterministic operations, 312, 346, 604     | distributed transactions (see transactions)    |
| and idempotence, 528, 541                   | Ditto (database), 222                          |
| computing derived data, 544, 573, 577       | Django (web framework), 288                    |
| in event sourcing, 104                      | DLQs (dead letter queues), 495                 |
| in state machine replication, 433, 501      | DMZ (demilitarized zone), 480                  |
| in statement-based replication, 207         | DNS (Domain Name System), 185, 268, 440        |
| in testing, 386                             | Docker (container manager), 552                |
| joins, 526                                  | document data model, 67-84                     |
| making code deterministic, 388              | comparison to relational model, 80-84          |
| overview, 387                               | multi-object transactions, need for, 287       |
| deterministic simulation testing (DST), 386 | sharded secondary indexes, 268                 |
| DevOps, 17                                  | versus relational model                        |
| DFSs (see distributed filesystems (DFSs))   | convergence of models, 83                      |
| dimension tables, 78                        | data locality, <mark>82</mark>                 |
| dimensional modeling (see star schemas)     | document-partitioned indexes (see local secon- |
| directed acyclic graphs (DAG), 464          | dary indexes)                                  |
| (see also workflow engines)                 | Domain Name System (DNS), 185, 268, 440        |
| dirty reads (transaction isolation), 290    | domain-driven design (DDD), 55, 102            |
| dirty writes (transaction isolation), 291   | dotted version vectors, 242                    |
| disaggregation, of storage and compute, 17  | double-entry bookkeeping, 108                  |
| Discord (group chat), 99                    | DRBD (Distributed Replicated Block Device),    |
| discrimination, 587                         | 199                                            |
| disk space usage, 131                       | drift (clocks), 360                            |
| disks (see hard disks)                      | drill-down, 135                                |
| distributed actor frameworks, 191           | Druid (database), 6, 138, 510                  |
| Distributed Component Object Model          | handling writes, 141                           |
| (DCOM), 183                                 | pre-aggregation, 477                           |
| distributed filesystems (DFSs), 458-460     | serving derived data, 481                      |
| comparison to object storage, 461           | Dryad (dataflow engine), 469                   |
| use by Flink, <mark>529</mark>              | DST (Daylight Saving Time), 359                |
| distributed ledgers, 108                    | DST (deterministic simulation testing), 386    |
| Distributed Replicated Block Device (DRBD), | dual writes, problems with, 501                |
| 199                                         | DuckDB (database), 21, 125                     |
| distributed systems, 345-389, 604           | column-oriented storage, 138                   |
| Byzantine faults, 377-380                   | use for ETL, 477                               |
| detecting network faults, 351               | duplicates, suppression of, 563, 564           |
| · ·                                         | - · · · · · · · · · · · · · · · · · · ·        |

| (see also idempotence)                          | embedding (vector), 147                                       |
|-------------------------------------------------|---------------------------------------------------------------|
| durability (transactions), 128, 282, 604        | encodings (data formats), 161-178                             |
| durable execution, 188                          | Avro, 172-177                                                 |
| reliance on determinism, 387                    | binary variants of JSON and XML, 167                          |
| Restate (see Restate (workflow engine))         | compatibility, 162                                            |
| Temporal (see Temporal (workflow engine))       | calling services, 186                                         |
| durable functions (see workflow engines)        | using databases, 178-180                                      |
| duration (time), 358, 359                       | defined, 163                                                  |
| dynamically typed languages, analogy to         | JSON, XML, and CSV, 165                                       |
| schema-on-read, 81                              | language-specific formats, 164                                |
| Dynamo (database), 229                          | merits of schemas, 177                                        |
| Dynamo-style databases (see leaderless replica- | Protocol Buffers, 169-171                                     |
| tion)                                           | representations of data, 163                                  |
| DynamoDB (database)                             | end-to-end argument, 565-566                                  |
| auto-scaling, 265                               | checking integrity, 577                                       |
| hash-range sharding, 262                        | publish/subscribe streams, 559                                |
| leader-based replication, 199                   | enrichment (stream), 524                                      |
| sharded secondary indexes, 271                  | Enterprise JavaBeans (EJB), 183                               |
| and the secondary indexes, Er I                 | enterprise software, 2                                        |
| г                                               | entities (see vertices)                                       |
| E                                               | ephemeral storage, 16                                         |
| EC2 (Elastic Compute Cloud), spot instances,    | epoch (consensus algorithms), 434                             |
| 465                                             |                                                               |
| ECC (error-correcting codes), 45, 459           | epoch (Unix timestamps), 359 Epsilon (garbage collector), 370 |
| EDB Postgres Distributed (database), 217        |                                                               |
| edges (in graphs), 84, 86                       | erasure coding (error correction), 459                        |
| edit distance (full-text search), 147           | Erlang/OTP (actor framework), 191                             |
| EE (Java Enterprise Edition), 183, 325, 330     | error handling                                                |
| effectively-once semantics, 526, 562, 572       | for network faults, 351                                       |
| (see also exactly-once semantics)               | in transactions, 287                                          |
| EFS (Elastic File System), 459                  | error-correcting codes (ECC), 45, 459                         |
| EJB (Enterprise JavaBeans), 183                 | Esper (CEP engine), 515                                       |
| Elastic Compute Cloud (EC2)                     | essential complexity, 55                                      |
| spot instances, 465                             | etcd (coordination service), 437-440                          |
| Elastic File System (EFS), 459                  | generating fencing tokens, 376, 438                           |
| elasticity, 19, 135                             | linearizable operations, 412, 436                             |
| Elasticsearch (search server)                   | locks and leader election, 408                                |
| local secondary indexes, 270                    | use for service discovery, 185, 440                           |
| percolator (stream search), 517                 | use for shard assignment, 267                                 |
| serving derived data, 480                       | use of Raft algorithm, 199                                    |
| shard rebalancing, 260                          | Ethereum (blockchain), 578                                    |
| use of Lucene, 147                              | Ethernet (networks), 23, 347, 356, 565                        |
| Elm (programming language), 559                 | ethics, 585-597                                               |
| ELT (extract-load-transform), 7, 476            | code of ethics and professional practice, 585                 |
| embarrassingly parallel (algorithms)            | legislation and self-regulation, 596                          |
| ETL (see extract-transform-load (ETL))          | predictive analytics, 586-589                                 |
| MapReduce, 468                                  | amplifying bias, <mark>587</mark>                             |
| (see also MapReduce)                            | feedback loops, 588                                           |
| embedded storage engines, 125                   | privacy and tracking, 589-597                                 |
|                                                 | consent and freedom of choice, 591                            |

| data as assets and power, 594 meaning of privacy, 592 surveillance, 590 respect, dignity, and agency, 596\nunintended consequences, 585, 589 ETL (see extract-transform-load (ETL)) Euclidean distance (semantic search), 148 European Union AI Act (see AI Act) GDPR (see General Data Protection Regula- | excision (Datomic), 512\nexclusive mode (locks), 314\nexponential backoff, 38, 288\next4 (filesystem), 458\neXtended Architecture transactions (see XA transactions)\nextract-load-transform (ELT), 7, 476\nextract-transform-load (ETL), 7, 501, 604 relation to batch processing, 476\nusing batch processing, 452 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tion (GDPR))                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                      |
| event sourcing, 101-105                                                                                                                                                                                                                                                                                    | F                                                                                                                                                                                                                                                                                                                    |
| and change data capture, 507 comparison to change data capture, 507\nimmutability and auditability, 508, 577 large, reliable data systems, 572 reliance on determinism, 387                                                                                                                                | FaaS (function as a service), 22 Facebook Faiss (vector index), 149 React (user interface library), 559 social graphs, 85                                                                                                                                                                                            |
| event streams (see streams)                                                                                                                                                                                                                                                                                | facts                                                                                                                                                                                                                                                                                                                |
| event-driven architecture, 189-191\nevents, 488                                                                                                                                                                                                                                                            | fact table (star schema), 77<br>in Datalog, 96                                                                                                                                                                                                                                                                       |
| deciding on total order of, 543                                                                                                                                                                                                                                                                            | in event sourcing, 102                                                                                                                                                                                                                                                                                               |
| deriving views from event log, 510                                                                                                                                                                                                                                                                         | fail-slow faults, 381                                                                                                                                                                                                                                                                                                |
| event time versus processing time, 519, 527, 546                                                                                                                                                                                                                                                           | fail-stop model, 381                                                                                                                                                                                                                                                                                                 |
|                                                                                                                                                                                                                                                                                                            | failover, 204, 604                                                                                                                                                                                                                                                                                                   |
| immutable, advantages of, 509, 577 ordering to capture causality, 543                                                                                                                                                                                                                                      | (see also leader-based replication)\nin leaderless replication, absence of, 230                                                                                                                                                                                                                                      |
| reads as, 559                                                                                                                                                                                                                                                                                              | potential problems, 205                                                                                                                                                                                                                                                                                              |
| stragglers, 520                                                                                                                                                                                                                                                                                            | failures                                                                                                                                                                                                                                                                                                             |
| timestamp of, in stream processing, 521                                                                                                                                                                                                                                                                    | amplification by distributed transactions,                                                                                                                                                                                                                                                                           |
| EventSource (browser API), 558                                                                                                                                                                                                                                                                             | 544                                                                                                                                                                                                                                                                                                                  |
| EventStoreDB (database), 105                                                                                                                                                                                                                                                                               | failure detection, 351                                                                                                                                                                                                                                                                                               |
| eventual consistency, 198, 209, 382                                                                                                                                                                                                                                                                        | automatic rebalancing causing cascading                                                                                                                                                                                                                                                                              |
| (see also conflicts)                                                                                                                                                                                                                                                                                       | failures, <mark>265</mark>                                                                                                                                                                                                                                                                                           |
| and perpetual inconsistency, 572                                                                                                                                                                                                                                                                           | timeouts and unbounded delays, 353,                                                                                                                                                                                                                                                                                  |
| strong eventual consistency, 226<br>evidence, data used as, 48                                                                                                                                                                                                                                             | 355                                                                                                                                                                                                                                                                                                                  |
| evolvability, 55, 161                                                                                                                                                                                                                                                                                      | using a coordination service, 438                                                                                                                                                                                                                                                                                    |
| calling services, 186                                                                                                                                                                                                                                                                                      | faults versus, 43                                                                                                                                                                                                                                                                                                    |
| event sourcing, 103                                                                                                                                                                                                                                                                                        | partial failures, 346, 388                                                                                                                                                                                                                                                                                           |
| graph-structured data, 88                                                                                                                                                                                                                                                                                  | Faiss (vector index), 149                                                                                                                                                                                                                                                                                            |
| of databases, 178-180, 510, 545                                                                                                                                                                                                                                                                            | false positive (Bloom filters), 123                                                                                                                                                                                                                                                                                  |
| reprocessing data, 545, 546                                                                                                                                                                                                                                                                                | fan-out (messaging systems), 35, 493                                                                                                                                                                                                                                                                                 |
| schema evolution in Avro, 173                                                                                                                                                                                                                                                                              | fault injection, 44, 351, 385                                                                                                                                                                                                                                                                                        |
| schema evolution in Protocol Buffers, 171                                                                                                                                                                                                                                                                  | fault isolation, 254                                                                                                                                                                                                                                                                                                 |
| schema-on-read, 80, 161, 178                                                                                                                                                                                                                                                                               | fault tolerance, 43-49, 605                                                                                                                                                                                                                                                                                          |
| exactly-once semantics, 44, 329, 334, 526, 562                                                                                                                                                                                                                                                             | formalization in consensus, 428                                                                                                                                                                                                                                                                                      |
| parity with batch processors, 546                                                                                                                                                                                                                                                                          | human fault tolerance, 452<br>in batch processing, 465                                                                                                                                                                                                                                                               |
| preservation of integrity, 572 using durable execution, 188                                                                                                                                                                                                                                                | in distributed systems, 19                                                                                                                                                                                                                                                                                           |

```
in log-based systems, 566, 571-573
                                                    Flink (processing framework), 453, 465, 468
   in stream processing, 526-529
                                                        cost efficiency, 475
      atomic commit, 527
                                                        DataFrames, 107, 475
      idempotence, 528
                                                        fault tolerance, 466, 527, 529
                                                        FlinkML, 478
      maintaining derived state, 544
                                                        for data warehouses, 135
      microbatching and checkpointing, 527
      rebuilding state after a failure, 529
                                                        high availability using ZooKeeper, 438
   of distributed transactions, 331-335
                                                        integration of batch and stream processing,
   of leader-based and leaderless replication.
                                                        query optimizer, 473
   transaction atomicity, 280, 323-330
                                                        shuffling data, 470
faults
                                                        stream processing, 515
   Byzantine faults, 377-380
                                                        streaming SQL support, 515
   failures versus, 43
                                                    flow control, 349, 489, 605
   handled by transactions, 277
                                                    FLP result (on consensus), 426
   handling in supercomputers and cloud
                                                    Flyte (workflow scheduler), 479
      computing, 23
                                                    followers, 199, 605
   hardware, 44
                                                        (see also leader-based replication)
   in distributed systems, 346
                                                        failure of, 204
                                                        setting up new, 201
   introducing deliberately (see fault injection)
   network faults, 350-352
                                                    formal methods, 384-387
                                                    formats, for encoding, 163-178
      asymmetric faults, 372
      detecting, 351
                                                    forward compatibility, 162
      tolerance of, in multi-leader replication,
                                                    Fossil (version control system), 512
          217
                                                    FoundationDB (database), 384
   software faults, 46
                                                        consistency model, 408
   tolerating (see fault tolerance)
                                                        deterministic simulation testing, 386
feature engineering (machine learning), 9
                                                        key-range sharding, 257
federated databases, 548
                                                        process-per-core model, 254
Feldera (database), 517
                                                        serializable transactions, 318, 322
fence (CPU instruction), 416
                                                        transactions, 279, 333
fencing (preventing split brain), 374-377
                                                    fractional indexing, 80
   generating fencing tokens, 434, 438
                                                    fragmentation (of B-trees), 131
   properties of fencing tokens, 382
                                                    frame (computer graphics), 221
                                                    frontend (web development), 3
   stream processors writing to databases, 528,
      562
                                                    FrostDB (database), 386
fetch-and-add, 427, 431
                                                    fsync (system call), 128, 282
Fibre Channel (networks), 459
                                                    full-text search, 108, 146, 605
field tags (Protocol Buffers), 170-171
                                                        Lucene storage engine, 147
Figma (graphics software), 220
                                                        sharded indexes, 268
filesystem in userspace (FUSE), 203, 459, 460
                                                    function as a service (FaaS), 22
financial data
                                                    functional programming, 468
   accounting ledgers, 108
                                                    functional requirements, 33
   immutability, 509
                                                    FUSE (see filesystem in userspace (FUSE))
   time-series data, 107
                                                    fuzzing, 384
Fivetran (data connector), 8
                                                    fuzzy search (see similarity search)
FizzBee (specification language), 384
flat index (vector index), 148
FlatBuffers (data format), 164
```

| G                                                              | data warehouse integration, 135              |
|----------------------------------------------------------------|----------------------------------------------|
| Gallina (specification language), 384                          | shuffling data, 470                          |
| game development, 222                                          | Datastream (change data capture), 506        |
| garbage collection (GC), 130                                   | Docs (collaborative editor), 220, 227        |
| immutability and, 512                                          | Dremel (query engine), 137                   |
| process pauses, 39, 368-371                                    | Firestore (database), 222                    |
| (see also process pauses)                                      | MapReduce (batch processing), 453            |
| gas stations algorithmic pricing, 589                          | (see also MapReduce)                         |
| GC (see garbage collection (GC))                               | Percolator (transaction system), 424         |
| GDPR (see General Data Protection Regulation                   | persistent disks (cloud service), 16         |
| (GDPR))                                                        | Pub/Sub (messaging), 190, 492, 497           |
| Gelly API (Flink), 478                                         | response time study, 41                      |
| GenBank (genome database), 108                                 | Sheets (collaborative spreadsheet), 220, 227 |
| General Data Protection Regulation (GDPR),                     | Spanner (see Spanner (database))             |
| 24, 512, 592                                                   | TrueTime (clock API), 365                    |
| consent, 592                                                   | gossip protocol, 267                         |
| data minimization, 596                                         | governance, 10                               |
| legitimate interest, 592                                       | government use of data, 594                  |
| right of access, 255                                           | GPS (see Global Positioning System (GPS))    |
| right to erasure, 24, 255                                      | GPT (language model), 148                    |
| genome analysis, 108                                           | GPU (graphics processing unit), 15, 19       |
| geographic distribution (see regions (geo-                     | GQL (Graph Query Language), 92               |
| graphic distribution))                                         | gradual rollout (see rolling upgrades)       |
| geospatial indexes, 145                                        | Graph Query Language (GQL), 92               |
| Git (version control system), 512                              | graphics processing unit (GPU), 15, 20       |
| local-first software, 221                                      | GraphQL (query language), 85, 98, 312        |
| merge conflicts, 225                                           | graphs, 605                                  |
| GitHub, postmortems, 205                                       | as data models, 84-101                       |
| Global Positioning System (GPS), use for clock                 | property graphs, <mark>86</mark>             |
| synchronization, 361, 365, 366                                 | RDF and triple-stores, 92-96                 |
| global secondary indexes, 270, 272                             | DAGs (see directed acyclic graphs)           |
| global transaction identifiers (GTIDs), 202                    | processing and analysis, 478                 |
| globally unique identifiers (see UUIDs)                        | query languages                              |
| GlusterFS (distributed filesystem), 453, 458,                  | Cypher, 88                                   |
| 460                                                            | Datalog, 96-98                               |
| GNU Coreutils (Linux), 457                                     | GraphQL, 98                                  |
| Go (programming language), 370                                 | Gremlin, <mark>85</mark>                     |
| GoldenGate (change data capture), 504                          | recursive SQL queries, 90                    |
| (see also Oracle)                                              | SPARQL, 95-96                                |
| Google                                                         | traversal, 87                                |
| BigQuery (see BigQuery (database))                             | GraphX API (Spark), 478                      |
| Bigtable (see Bigtable (database))                             | gray failures, 235, 381                      |
| Chubby (lock service), 438                                     | Gremlin (graph query language), 85           |
| Cloud Storage (object storage), 202, 376,                      | grep (Unix tool), 455                        |
| 460                                                            | gRPC (service calls), 22, 181, 186           |
|                                                                | GTIDs (global transaction identifiers), 202  |
| Compute Engine, 465 Dataflow (stream processor), 515, 528, 546 | GUIDs (see UUIDs)                            |
| (see also Beam)                                                |                                              |

| Н                                           | head-of-line blocking, 39                        |
|---------------------------------------------|--------------------------------------------------|
| Hadoop (data infrastructure)                | heap files (databases), 133, 296                 |
| comparison to distributed databases, 453    | heat management, 264                             |
| MapReduce (see MapReduce)                   | hedged requests, 235                             |
| NodeManager, 462                            | heterogeneous distributed transactions, 329,     |
| YARN (see YARN (job scheduler))             | 332                                              |
| Hadoop Distributed File System (HDFS), 453, | heuristic decisions (in 2PC), 332                |
| 458                                         | Hex (notebook), 479                              |
| (see also distributed filesystems)          | hexagons, for geospatial indexing, 145           |
| checking data integrity, 576                | Hibernate (object-relational mapper), 68         |
| DataNode, 458                               | hierarchical model, 67                           |
| NameNode, 459                               | hierarchical navigable small world (vector       |
| use in MapReduce, 466                       | index), 148                                      |
| workflow example, 464                       | hierarchical queries (see recursive queries, SQI |
| HANA (see SAP HANA (database))              | common table expressions)                        |
| happens-before relation, 238                | high availability (see fault tolerance)          |
| HAProxy, 185                                | high-frequency trading, 361                      |
| hard disks                                  | high-performance computing (HPC), 23             |
| detecting corruption, 565, 576              | highest random weight hashing algorithm, 263     |
| faults in, 44, 283                          | hinted handoff (leaderless replication), 231     |
| sequential versus random writes, 130        | histograms, 42                                   |
| sequential write throughput, 499            | Hive (data warehouse), 135, 473                  |
| hardware faults, 44                         | HNSW (hierarchical navigable small world)        |
| hash function, in Bloom filters, 122, 605   | (vector index), 148                              |
| hash join, in stream processing, 524        | homogeneous data, 85                             |
| hash sharding, 258-263, 272                 | hopping windows (stream processing), 522         |
| consistent hashing, <mark>263</mark>        | (see also windows)                               |
| problems with hash mod N, 258               | Hoptimator (query engine), 548                   |
| range queries, 261                          | Horizon scandal, 48, 278                         |
| suitable hash functions, 258                | horizontal scaling (see scaling out)             |
| with fixed number of shards, 259            | HornetQ (messaging), 190, 330, 492               |
| hash tables, 118                            | hot keys, 255                                    |
| Hazelcast (in-memory data grid)             | hot shard (see hot spots)                        |
| FencedLock, 376                             | hot spots, 255                                   |
| Flake ID Generator, 419                     | due to celebrities, 263                          |
| HBase (database)                            | for time-series data, 257                        |
| bug due to lack of fencing, 373             | relieving, 263                                   |
| key-range sharding, 257                     | hot standbys (see followers) (see leader-based   |
| log-structured storage, 121                 | replication)                                     |
| regions (sharding), <mark>252</mark>        | HPC (high-performance computing), 23             |
| request routing, 267                        | HTAP (see hybrid transactional/analytic pro-     |
| size-tiered compaction, 124                 | cessing)                                         |
| wide-column data model, 82, 140             | HTTP, use in APIs (see services)                 |
| HDFS (see Hadoop Distributed File System    | human errors, 47, 350                            |
| (HDFS))                                     | hybrid logical clocks, 422                       |
| HdrHistogram (percentile estimation), 42    | hybrid transactional/analytical processing       |
| head (Unix tool), 455, 461                  | (HTAP), 8, 135                                   |
| head vertex (property graphs), 87           | hydrating IDs (join), 74                         |
|                                             | HyPer (database), 318                            |

| hypergraph, 88                                                              | data loss due to last-write-wins, 363        |
|-----------------------------------------------------------------------------|----------------------------------------------|
| HyperLogLog (algorithm), 515                                                | disclosure of sensitive data due to primary  |
| 71 0 0 0                                                                    | key reuse, 205                               |
| 1                                                                           | errors in transaction serializability, 576   |
| I/O engrations, waiting for 369                                             | gigabit network interface with 1 Kb/s        |
| I/O operations, waiting for, 368 IaaS (infrastructure as a service), 12, 15 | throughput, 381                              |
| IBM                                                                         | leap second crash, 46                        |
|                                                                             | network faults, 350                          |
| Db2 (database)                                                              | network interface dropping only inbound      |
| distributed transaction support, 330 serializable isolation, 299, 314       | packets, 350                                 |
| MQ (messaging), 330, 492                                                    | network partitions and whole-datacenter      |
| System R (database), 278                                                    | failures, 346                                |
| WebSphere (messaging), 190                                                  | sending message to ex-partner, 543           |
| Iceberg (table format), 136, 477                                            | sharks biting undersea cables, 350           |
| databases on object storage, 203                                            | SSD failure after 32,768 hours, 46           |
| log-based message broker storage, 499                                       | thread contention bringing down a service,   |
|                                                                             | 367                                          |
| idempotence, 183, 528, 605<br>by giving requests unique IDs, 564            | vibrations in server rack, 39                |
| for exactly-once semantics, 335                                             | violation of uniqueness constraint, 576      |
| _                                                                           | incremental view maintenance (IVM), 516, 551 |
| idempotent operations, 562                                                  | indexes, 117, 605                            |
| in workflow engines, 189 IDL (interface definition language), 169, 172,     | and snapshot isolation, 298                  |
| 181                                                                         | as derived data, 11, 547-551                 |
|                                                                             | B-trees, 125-128                             |
| immutability                                                                | clustered, 133                               |
| advantages of, 509, 577                                                     | comparison of B-trees and LSM-trees,         |
| and right to erasure, 24, 132                                               | 129-132                                      |
| crypto-shredding for deletion, 104, 512                                     | covering (with included columns), 133        |
| deriving state from event log, 508-513                                      | creating, 548                                |
| for crash recovery, 122<br>in B-trees, 128, 298                             | full-text search, 146                        |
|                                                                             | geospatial, 145                              |
| in event sourcing, 101, 507<br>limitations of, 512                          | index-range locking, 317                     |
|                                                                             | multicolumn (concatenated), 145              |
| impedance mismatch, 68                                                      | secondary, 132                               |
| in doubt (transaction status), 327                                          | (see also secondary indexes)                 |
| holding locks, 331                                                          | sharding and secondary indexes, 268-271,     |
| orphaned transactions, 331                                                  | 272                                          |
| in-memory aggregation, 456<br>in-memory databases, 133                      | sparse, 119                                  |
| •                                                                           | SSTables and LSM-trees, 119-124              |
| durability, 283 serial transaction execution, 309                           | updating when data changes, 501, 516         |
| incidents                                                                   | Industrial Revolution, 595                   |
| accounting software bugs leading to wrong-                                  | InfiniBand (networks), 357                   |
| ful convictions, 48                                                         | InfluxDB IOx (storage engine), 138           |
| blameless postmortems, 48                                                   | information retrieval (see full-text search) |
| crashes due to leap seconds, 361                                            | infrastructure as a service (IaaS), 12, 15   |
| data corruption and financial losses due to                                 | InnoDB (storage engine)                      |
| concurrency bugs, 289                                                       | clustered index on primary key, 133          |
| data corruption on hard disks, 283                                          | not preventing lost updates, 301             |
| anta corruption on fidita disks, 200                                        | preventing write skew, 305, 314              |

| serializable isolation, 314<br>snapshot isolation support, 295 | comparison to log-based messaging, 497, 500 |
|----------------------------------------------------------------|---------------------------------------------|
| instance (cloud computing), 15                                 | distributed transaction support, 330        |
| integrating different data systems (see data inte-             | message ordering, 494                       |
| gration)                                                       | Java Transaction API (JTA), 324, 330        |
| integrity, 571                                                 | Java Virtual Machine (JVM)                  |
| coordination-avoiding data systems, 574                        | garbage collection, 368, 370                |
| correctness of dataflow systems, 572                           | JIT compilation, 142                        |
| in consensus formalization, 428, 432                           | process reuse in batch processors, 469      |
| integrity checks, 576                                          | JDBC (see Java Database Connectivity (JDBC) |
| (see also auditability)                                        | Jena (RDF framework), 94, 96                |
| end-to-end, 565, 577                                           | Jepsen (fault tolerance testing), 386, 561  |
| use of snapshot isolation, 294                                 | JIT (just-in-time) compilation, 142         |
| maintaining despite software bugs, 576                         | jitter (network delay), 40, 355             |
| interface definition language (IDL), 169, 172,                 | JMESPath (query language), 474              |
| 181                                                            | JMS (see Java Message Service (JMS))        |
| invariants, 281                                                | join table, 75, 87                          |
| (see also constraints)                                         | joins, 605                                  |
| inverted file (IVF) index (vector index), 148                  | expressing as relational operators, 473     |
| inverted index, 146                                            | handling GraphQL query, 101                 |
| irreversibility, minimizing, 56, 104, 452                      | in application code, 73, 74                 |
| ISDN (Integrated Services Digital Network),                    | in DataFrames, 105                          |
| 355                                                            | in relational and document databases, 72    |
| isolation (in operating systems) (see cgroups)                 | sort-merge joins, 471                       |
| isolation (in transactions), 279, 281, 284, 605                | stream joins, <b>523-526</b>                |
| correctness and, 561                                           | stream-stream join, 523                     |
| for single-object writes, 286                                  | stream-table join, <mark>524</mark>         |
| serializability, 308-322                                       | table-table join, <mark>524</mark>          |
| actual serial execution, 309-313                               | time-dependence of, 525                     |
| serializable snapshot isolation (SSI),                         | support in document databases, 83           |
| 317-322                                                        | JOTM (transaction coordinator), 325         |
| two-phase locking (2PL), 313-317                               | journaling (filesystems), 128               |
| violating, 284                                                 | ISON                                        |
| weak isolation levels, 288-308                                 | aggregation pipeline (query language), 82   |
| preventing lost updates, 299-303                               | Avro schema representation, 172             |
| read-committed, 290-293                                        | binary variants, 167                        |
| snapshot isolation, 293-299                                    | data locality, 82                           |
| IVF (vector index), 148                                        | document data model, 67                     |
| IVM (incremental view maintenance), 516, 551                   | for application data, issues with, 165      |
|                                                                | GraphQL response, 100                       |
| J                                                              | in relational databases, 80                 |
| Jaeger (tracing tool), 20                                      | representing a résumé (example), 69         |
| Java Database Connectivity (JDBC)                              | Schema, 166                                 |
| distributed transaction support, 330                           | JSON Pointer, 82                            |
| network drivers, 177                                           | JSON-LD, 94                                 |
| Java Enterprise Edition (EE), 183, 325, 330                    | JSONPath (query language), 82, 474          |
| Java Message Service (JMS), 492                                | JTA (Java Transaction API), 324             |
| (see also messaging systems)                                   | JuiceFS (distributed filesystem), 458, 460  |
| (occ moo messagnig systems)                                    | jump consistent hashing, 263                |

| Jupyter (notebook), 479                                            | L                                                           |
|--------------------------------------------------------------------|-------------------------------------------------------------|
| just-in-time (JIT) compilation, 142                                | L4S (Low Latency, Low Loss, and Scalable                    |
| JVM (see Java Virtual Machine (JVM))                               | Throughput), 357                                            |
|                                                                    | labeled property graphs (see property graphs)               |
| K                                                                  | lambda architecture, 546                                    |
| Kafka (messaging), 190, 497                                        | lambda calculus, <mark>553</mark>                           |
|                                                                    | Lamport timestamps, 420                                     |
| consumer groups, 493 for data integration, 551                     | Lance (data format), 136, 138                               |
| _                                                                  | (see also column-oriented storage)                          |
| for event sourcing, 105 Kafka Connect (database integration), 504, | large language models (LLMs), 147, 479                      |
| 506, 510                                                           | last write wins (LWW), 224, 237, 412                        |
| Kafka Streams (stream processor), 515                              | problems with, 363                                          |
| exactly-once semantics, 335                                        | prone to lost updates, 303                                  |
| fault tolerance, 529                                               | latency, 38                                                 |
| ksqlDB (stream database), 516                                      | (see also response time)                                    |
| leader-based replication, 199                                      | across regions, 19                                          |
| log compaction, 506, 516                                           | instability under two-phase locking, 315                    |
| message offsets, 496, 528                                          | network latency and resource utilization,                   |
| partitions (sharding), 252                                         | 356                                                         |
| request routing, 267                                               | reducing by request hedging, 235                            |
| schema registry, 176                                               | response time versus, 38                                    |
| serving derived data, 480                                          | tail latency, 40, 41, 269                                   |
| tiered storage, 499                                                | law (see legal matters)                                     |
| transactions, 333, 528                                             | layering (of cloud services), 15                            |
| unclean leader election, 436                                       | leader-based replication, 198-208                           |
| use of model-checking, 385                                         | (see also replication)                                      |
| kappa architecture, 546                                            | failover, 204                                               |
| key-value stores, 116                                              | handling node outages, 204                                  |
| comparison to object stores, 461                                   | implementation of replication logs                          |
| in-memory, 134                                                     | change data capture, 503-506                                |
| LSM storage, 118-132                                               | (see also changelogs)                                       |
| sharding, 255-264                                                  | statement-based, 206                                        |
| by hash of key, 258, 272                                           | write-ahead log (WAL) shipping, 207                         |
| by key range, 256, 272                                             | linearizability of operations, 411                          |
| skew and hot spots, 263                                            | locking and leader election, 408                            |
| Kinesis (messaging), 190                                           | log sequence number, 202, 498                               |
| knowledge graphs, <mark>85</mark>                                  | read-scaling architecture, 209, 235                         |
| Kryo (Java), <mark>164</mark>                                      | relation to consensus, <b>425</b> , <b>434</b> , <b>437</b> |
| ksqlDB (stream database), 516                                      | setting up new followers, 201                               |
| Kubernetes (cluster manager), 12, 22, 462, 552                     | synchronous versus asynchronous, 200-201                    |
| Kubeflow, 479                                                      | leaderless replication, 229-242                             |
| kubelet, 462                                                       | (see also replication)                                      |
| operators, 463                                                     | catching up on missed writes, 231                           |
| use of etcd, 267, 438                                              | detecting concurrent writes, 237-242                        |
| KùzuDB (database), 21, 85                                          | version vectors, 242                                        |
| as embedded storage engine, 125                                    | multi-region, 236                                           |
| Cypher query language, 88                                          | quorums, 231-237                                            |
| -11 11                                                             | consistency limitations, 233-235, 412                       |
|                                                                    | * '                                                         |

```
leaf page (B-tree), 126
                                                        coping with, 52
leap seconds, 46, 359, 361
                                                        describing, 50
leases, 366
                                                    load balancing, 38, 184
   implementation with coordination service,
                                                        in hardware, 184
                                                        in software, 185
   need for fencing, 373
                                                        using message brokers, 492
   relation to consensus, 427
                                                    load shedding, 38
ledgers (accounting), 108, 509
                                                    local secondary indexes, 268, 272
legacy systems, maintenance of, 53
                                                    local-first software, 221
legal matters, 24-25
                                                    locality (data access), 71, 82, 605
   data deletion, 24
                                                        in batch processing, 469
   data residence, 20, 255
                                                        in stateful clients, 220, 558
                                                        in stream processing, 524, 529, 555, 568
   privacy regulation, 24, 596
legitimate interest (GDPR), 592
                                                    location transparency, 183, 191
leveled compaction, 124, 131
                                                    lock-in, 14
Levenshtein automata, 147
                                                    locks, 605
limping (partial failure), 381
                                                        deadlock, 301, 315
Linear (project management software), 220
                                                        distributed locking, 373-377, 408
linear algebra, 106
                                                           fencing tokens, 374
linear scalability, 50
                                                           implementation with coordination ser-
linearizability, 215, 402-417, 605
   and consensus, 425
                                                           relation to consensus, 427
   cost of, 413-417
                                                        for transaction isolation
                                                           in snapshot isolation, 295
      CAP theorem, 414
                                                           in two-phase locking (2PL), 313-317
      memory on multi-core CPUs, 416
   definition, 404-407
                                                           making operations atomic, 300
   ID generation, 423
                                                           performance, 315
   in coordination services, 438
                                                           preventing dirty writes, 292
                                                           preventing phantoms with index-range
   of derived data systems, 574
   of different replication methods, 411-413
                                                              locks, 317, 321
                                                           read locks (shared mode), 292, 314
   reads in consensus systems, 436
                                                           shared mode and exclusive mode, 314
   relying on, 408-411
      constraints and uniqueness, 409
                                                        in distributed transactions
      cross-channel timing dependencies, 410
                                                           deadlock detection, 332
                                                           in-doubt transactions holding locks, 331
      locking and leader election, 408
   versus serializability, 407
                                                        materializing conflicts with, 307
linked data, 94
                                                        preventing lost updates by explicit locking,
LinkedIn
   Espresso (database), 176
                                                    log sequence number, 202, 498
   LIquid (database), 96
                                                    log-structured storage, 115-125
   profile (example), 69
                                                        (see also LSM-trees (indexes))
Linux, leap second bug, 46
                                                    logical clocks, 364, 417-425, 543
Litestream (backup tool), 202
                                                        for last-write-wins, 224
live migration, 368
                                                        for read-after-write consistency, 211
liveness properties, 382
                                                        hybrid logical clocks, 422
LLMs (large language models), 147, 479
                                                        insufficiency for enforcing constraints, 425
LLVM (compiler), 142
                                                        Lamport timestamps, 420
LMDB (storage engine), 125, 128, 298
                                                    logical replication, 208, 504
load
                                                    LogicBlox (database), 96
```

| logs (data structure), 117, 429, 606            | relation to batch processing, 478-479                  |
|-------------------------------------------------|--------------------------------------------------------|
| (see also shared logs)                          | using a data lake, 9                                   |
| advantages of immutability, 509                 | using GPUs, 15, 19                                     |
| and right to erasure, 24                        | using matrices, 106                                    |
| compaction, 120, 124, 505, 509                  | madsim (deterministic simulation testing), 386         |
| for stream operator state, 529                  | magic scaling sauce, 52                                |
| implementing uniqueness constraints, 567        | maintainability, 52-56, 539                            |
| log-based messaging, 495-500                    | evolvability (see evolvability)                        |
| comparison to traditional messaging,            | operability, <mark>53</mark>                           |
| 497, 500                                        | simplicity and managing complexity, 54                 |
| consumer offsets, 498                           | many-to-many relationships, 75, 84                     |
| disk space usage, 498                           | many-to-one relationships, 75, 79                      |
| replaying old messages, 500, 545                | MapReduce (batch processing), 453, 466-468             |
| slow consumers, 499                             | analysis of user activity events (example),            |
| using logs for message storage, 496             | 471                                                    |
| log-structured storage, 117-124                 | comparison to stream processing, 513                   |
| relation to consensus, 429                      | disadvantages and limitations of, 468                  |
| replication, 199, 206-208                       | fault tolerance, 466                                   |
| change data capture, 503-506                    | higher-level tools, 473                                |
| (see also changelogs)                           | mapper and reducer functions, 467                      |
| coordination with snapshot, 202                 | shuffling data, 470                                    |
| logical (row-based) replication, 208            | sort-merge joins, 471                                  |
| statement-based replication, 206                | workflows (see workflow engines)                       |
| write-ahead log (WAL) shipping, 207             | Marshal (Ruby), 164                                    |
| scalability limits, 542                         | marshaling (see encoding)                              |
| Looker (business intelligence software), 6, 478 | MartenDB (database), 105                               |
| loose coupling, 550                             | master-slave replication (obsolete term), 200          |
| lost updates (see updates)                      | materialization, 606                                   |
| Lotus Notes (sync engine), 222                  | aggregate values, 144                                  |
| Low Latency, Low Loss and Scalable Through-     | conflicts, 307                                         |
| put (L4S), 357                                  | materialized views, 143                                |
| LSM-trees (indexes), 119-124, 129-132           | as derived data, 11, 547-551                           |
| Lucene (storage engine), 147                    | in event sourcing, 102                                 |
| LWW (see last write wins)                       | incremental view maintenance, 516                      |
|                                                 | (see also incremental view mainte-                     |
| M                                               | nance (IVM))                                           |
| machine learning                                | maintaining, using stream processing,                  |
| batch inference, 478                            | 516, 525                                               |
| data preparation with DataFrames, 105           | social network timeline example, 36                    |
| deleting training data, 24                      | Materialize (database), 143, 517                       |
| deploying data products, 10                     | matrices, 105                                          |
| ethical considerations, 586                     | mean, 40                                               |
| (see also ethics)                               | median, 40                                             |
| feature engineering, 9, 478                     | meeting room booking (example), 305, 316               |
| in analytics systems, 4                         | Memgraph (database), <mark>85</mark> , <mark>88</mark> |
| iterative processing, 478                       | memory                                                 |
| LLMs (see large language models (LLMs))         | barrier (CPU instruction), 416                         |
| models derived from training data, 552          | corruption, 45                                         |
| •                                               | in-memory databases, 133                               |

```
durability, 283
                                                      relation to batch/stream processors, 451,
      serial transaction execution, 309
                                                   Microsoft
   in-memory representation of data, 163
   memtable (in LSM-trees), 120
                                                      Azure Blob Storage (see Azure Blob Stor-
   use by indexes, 118
memtable (in LSM-trees), 120
                                                      Azure managed disks, 16
Mercurial (version control system), 512
                                                      Azure Service Bus (messaging), 190, 492
merge (DataFrame operator), 105
                                                      Azure SQL DB (database), 15
merging sorted files, 120, 471
                                                      Azure Storage, 460
Merkle trees, 578
                                                      Azure Stream Analytics, 515
                                                      Azure Synapse Analytics (database), 15
Mesos (cluster manager), 552
                                                      DCOM (Distributed Component Object
message brokers (see messaging systems)
message queues (see messaging systems)
                                                         Model), 183
message-oriented middleware (see messaging
                                                      Microsoft Power BI (see Power BI (business
   systems)
                                                         intelligence software))
message-passing (see event-driven architecture)
                                                      MSDTC (transaction coordinator), 325
MessagePack (encoding format), 168
                                                      SQL Server (see SQL Server)
messaging systems, 189, 488-500
                                                   migrating (rewriting) data, 81, 179, 510, 545
   (see also streams)
                                                   MinIO (object storage), 459
                                                   mobile apps, 3, 125
   backpressure, buffering, or dropping mes-
                                                   model checking, 384
      sages, 489
   brokerless messaging, 490
                                                   modulus operator (%), 258
   event logs, 495-500
                                                   Mojo (programming language), 370
      as data model, 101
                                                   MongoDB (database), 453
      comparison to traditional messaging,
                                                      aggregation pipeline, 82
          497, 500
                                                      atomic operations, 300
      consumer offsets, 498
                                                      BSON, 82
      replaying old messages, 500, 545, 546
                                                      document data model, 67
      slow consumers, 499
                                                      hash-range sharding, 258, 262
   exactly-once semantics, 329, 334, 526
                                                      in the cloud, 15
   message brokers, 491-495
                                                      joins ($lookup operator), 73, 83
                                                      JSON Schema validation, 166
      acknowledgments and redelivery, 493
      comparison to event logs, 497, 500
                                                      leader-based replication, 199
      multiple consumers of same topic, 492
                                                      ObjectIDs, 419
      versus RPC, 189
                                                      range-based sharding, 257
   message loss, 490
                                                      request routing, 267
   reliability, 490
                                                      secondary indexes, 270
   uniqueness in log-based messaging, 567
                                                      shard splitting, 257
                                                      stored procedures, 312
metastable failure, 38
metered billing
                                                   monitoring, 17, 47, 54
   serverless, 22
                                                   monotonic clocks, 359
   storage, 17
                                                   monotonic reads, 212
metrics, for response time, 41
                                                   Morel (query language), 474
microbatching, 527
                                                   MSMQ (messaging), 330
microservices, 21
                                                   multi-leader replication, 215-229
   (see also services)
                                                      (see also replication)
   causal dependencies across services, 542
                                                      collaborative editing, 220
   loose coupling, 550
                                                      conflict detection, 228
                                                      conflict resolution, 222
```

| for multi-region replication, 216, 413<br>linearizability, lack of, 412 | natural language processing (NLP), 9<br>Neo4j (database)             |
|-------------------------------------------------------------------------|----------------------------------------------------------------------|
| offline-capable clients, 220                                            | Cypher query language, 88                                            |
| replication topologies, 218-220                                         | graph data model, 85                                                 |
| multi-object transactions, 287                                          | Neon (database), 203                                                 |
| Multi-Paxos (consensus algorithm), 229, 433                             | Nephele (dataflow engine), 469                                       |
| multi-reader single-writer lock, 314                                    | netcode (game development), 222                                      |
| multi-table index cluster tables (Oracle), 82                           | Network Attached Storage (NAS), 51, 459                              |
| multicolumn indexes, 145                                                | Network File System (NFS), 459, 460                                  |
| multidimensional arrays, 105                                            | network latency/delay, 39                                            |
| multidimensional index, 145                                             | network model (data representation), 67                              |
| multiplayer game (example), <mark>306</mark>                            | network partitions, 252                                              |
| multitenancy, 17, 354                                                   | Network Time Protocol (NTP), 358                                     |
| by sharding, 254                                                        | accuracy, 360, 364                                                   |
| using embedded databases, 125                                           | adjustments to monotonic clocks, 360                                 |
| multiversion concurrency control (MVCC),                                | multiple server addresses, 380                                       |
| 295, 336                                                                | networks                                                             |
| detecting stale MVCC reads, 319                                         | congestion and queueing, 353                                         |
| indexes and snapshot isolation, 298                                     | datacenter network topologies, 23                                    |
| using synchronized clocks, 365                                          | faults (see faults)                                                  |
| mutual exclusion, 318                                                   | linearizability and network delays, 416                              |
| (see also locks)                                                        | network partitions, 351                                              |
| MVCC (see multiversion concurrency control                              | in CAP theorem, 413                                                  |
| (MVCC))                                                                 | timeouts and unbounded delays, 352                                   |
| MySQL (database)                                                        | NewSQL, 67, 215, 279, 333                                            |
| archiving WAL to object stores, 202                                     | next-key locking, 317                                                |
| binlog coordinates, 202                                                 | NFS (Network File System), 459, 460                                  |
| change data capture, 504, 506                                           | NGINX, 185                                                           |
| circular replication topology, 218                                      | Nimble (data format), 136, 138                                       |
| consistent snapshots, 202                                               | (see also column-oriented storage)                                   |
| distributed transaction support, 330                                    | NLP (natural language processing), 9                                 |
| global transaction identifiers (GTIDs), 202                             | node (in graphs) (see vertices)                                      |
| in the cloud, 15                                                        | nodes (processes), 19, 606                                           |
| InnoDB storage engine (see InnoDB)                                      | allocating work to, 439                                              |
| leader-based replication, 199                                           | handling outages in leader-based replica-                            |
| multi-leader replication, 217                                           | tion, 204                                                            |
| row-based replication, 208                                              | system models for failure, 381                                       |
| sharding (see Vitess (database))                                        | writing to databases, 229-235                                        |
| snapshot isolation support, 298                                         | noisy neighbors, 354                                                 |
| (see also InnoDB)                                                       | Non-Volatile Memory Express (NVMe) (see                              |
| statement-based replication, 207                                        | solid state drives (SSDs))                                           |
| LI .                                                                    | nonblocking atomic commit, 328                                       |
| N                                                                       | nondeterministic operations, 207 (see also deterministic operations) |
| N+1 query problem, <mark>68</mark>                                      |                                                                      |
| nanomsg (messaging library), 490                                        | in distributed systems, 387<br>in workflow engines, 189              |
| Narayana (transaction coordinator), 325                                 | partial failures, 346                                                |
| NAS (Network Attached Storage), 51, 459                                 | sources of nondeterminism, 388                                       |
| NATS (messaging), 190                                                   | nonfunctional requirements, 33, 56                                   |
|                                                                         | nomanenonai requirements, 33, 30                                     |

| nonrepeatable reads, 293                        | (see also batch processing)                   |
|-------------------------------------------------|-----------------------------------------------|
| (see also read skew)                            | offline-first applications, 221, 558          |
| nonsimple domains, <mark>84</mark>              | offsets                                       |
| nonuniform memory access (NUMA), 254            | consumer offsets in sharded logs, 498         |
| normalization (data representation), 72-77, 606 | messages in sharded logs, 496                 |
| foreign-key references, 287                     | OLAP (online analytical processing), 5, 144,  |
| in social network case study, 74                | 606                                           |
| in systems of record, 11                        | OLTP (see online transaction processing       |
| versus denormalization, 511                     | (OLTP))                                       |
| NoSQL, 67, 215, 279, 547                        | on-premises deployment, 12, 135               |
| Notation3 (N3), 93                              | one big table (OBT), 77, 79                   |
| NP-hard, 464                                    | · ·                                           |
|                                                 | one-hot encoding, 106                         |
| NTP (see Network Time Protocol (NTP))           | one-to-few relationships, 71                  |
| NUMA (nonuniform memory access), 254            | one-to-many relationships, 69, 71             |
| numbers, in XML and JSON encodings, 165         | online analytical processing (OLAP), 5, 144,  |
| NumPy (Python library), 106, 138                | 606                                           |
| NVMe (Non-Volatile Memory Express) (see         | online systems, 23, 451                       |
| solid state drives (SSDs))                      | (see also services)                           |
|                                                 | online transaction processing (OLTP), 5, 606  |
| 0                                               | analytical queries versus, 477                |
| object databases, 67                            | data normalization, 74                        |
| object storage, 15, 460-461                     | storage engines optimized for, 115-134        |
| Amazon S3 (see Amazon S3 (object stor-          | workload characteristics, 309                 |
| age))                                           | ontologies, 94                                |
| •                                               | Oozie (workflow scheduler), 453               |
| Azure Blob Storage (see Azure Blob Stor-        | Open Graph protocol (Facebook), 94            |
| age)                                            | OpenAPI (service definition format), 22, 166, |
| comparison to distributed filesystems, 461      | 181                                           |
| comparison to key-value stores, 461             | openCypher (see Cypher (query language))      |
| databases backed by, 202                        | OpenHistogram (percentile estimation), 42     |
| for backups, 198                                | OpenLink Virtuoso (see Virtuoso (database))   |
| for cloud data warehouses, 135, 141             | OpenStack, 460                                |
| for database replication, 202                   | OpenTelemetry (tracing tool), 20              |
| Google Cloud Storage (see Google, Cloud         | operability, 53                               |
| Storage)                                        | - · · · · · · · · · · · · · · · · · · ·       |
| object size, <mark>16</mark>                    | operating systems versus databases, 546       |
| storing LSM segment files, 122                  | operational systems, 4, 11                    |
| support for fencing, 376                        | (see also online transaction processing       |
| use in data lakes, 10                           | (OLTP))                                       |
| object-relational mapping (ORM) frameworks,     | analytical systems compared with, 3-12        |
| 68                                              | ETL into analytical systems, 7                |
| error handling and aborted transactions,        | operational transformation (OT), 227          |
| 288                                             | operations teams, 17                          |
| unsafe read-modify-write cycle code, 300        | operators (query execution), 142, 513         |
| object-relational mismatch, 68                  | optimistic concurrency control, 318           |
| observability, 20, 47, 54                       | optimistic locking, 302                       |
| observability, 20, 47, 54                       | Oracle (database)                             |
| OBT (one big table), 77, 79                     | distributed transaction support, 330          |
|                                                 | GoldenGate (change data capture), 504         |
| offline systems, 451                            | hierarchical queries, 92                      |
|                                                 |                                               |

| lack of serializability, 282                  | use in batch processing, 466                          |
|-----------------------------------------------|-------------------------------------------------------|
| leader-based replication, 199                 | parsing (see decoding)                                |
| multi-leader replication, 217                 | partial failures, 346, 381, 388                       |
| multi-table index cluster tables, 82          | partial synchrony (system model), 380                 |
| not preventing write skew, 305                | partition key, 253, 256, 498                          |
| PL/SQL language, 311                          | partitioning (see sharding)                           |
| preventing lost updates, 301                  | Paxos (consensus algorithm), 426, 433                 |
| read-committed isolation, 292                 | ballot number, 434                                    |
| Real Application Clusters (RAC), 409          | Multi-Paxos, 433                                      |
| snapshot isolation support, 295, 298          | Payment Card Industry (PCI) compliance, 25            |
| TimesTen (in-memory database), 134            | percentiles, 40, 606                                  |
| WAL-based replication, 207                    | calculating efficiently, 42                           |
| ORC (data format), 136, 138                   | in service level agreements (SLAs), 42                |
| (see also column-oriented storage)            | in service level objectives (SLOs), 42                |
| orchestration (service deployment), 12, 22    | Percolator (Google), 424                              |
| batch job execution, 461-463                  | Percona XtraBackup (MySQL tool), 202                  |
| workflow engines, 453                         | performance                                           |
| ordering                                      | degradation as fault, 381                             |
| event logs, 105                               | describing, 37                                        |
| limits of total ordering, 542                 | of distributed transactions, 328                      |
| logical timestamps, 420                       | of in-memory databases, 134                           |
| of auto-incrementing IDs, 417                 | of linearizability, 416                               |
| shared logs, 433-437                          | of multi-leader replication, 217                      |
| Orkes (workflow engine), 188                  | permission isolation, 254                             |
| Orleans (actor framework), 191                | perpetual inconsistency, 572                          |
| ORM (see object-relational mapping (ORM)      | pessimistic concurrency control, 318                  |
| frameworks)                                   | pgcapture (change data capture), 504                  |
| orphan pages (B-trees), 128                   | pglogical (PostgreSQL extension), 217                 |
| OT (operational transformation), 227          | PGQL (Property Graph Query Language), 92              |
| outbox pattern, 507                           | pgvector (vector index), 149                          |
| outliers (response time), 40                  | phantoms (transaction isolation), 307                 |
| outsourcing, 12                               | materializing conflicts, 307                          |
| overload, 38, 288                             | preventing, in serializability, 316                   |
|                                               | physical clocks (see clocks)                          |
| •                                             | pickle (Python), <mark>164</mark>                     |
| PACELC principle, 415                         | Pinot (database), 6, 138                              |
| package managers, <mark>552</mark>            | handling writes, 141                                  |
| packet switching, <mark>356</mark>            | pre-aggregation, 477                                  |
| packets                                       | serving derived data, 480, 481                        |
| corruption of, 379                            | pipelined execution, in data warehouse queries        |
| sending via UDP, 490                          | 143                                                   |
| PageRank (algorithm), 84, 475                 | pivot table, 106                                      |
| paging (see virtual memory)                   | point in time, 358                                    |
| Pandas (Python library), 9, 105, 138, 475     | point queries, 5, 129                                 |
| Parquet (data format), 10, 136, 138, 180, 474 | Polaris (data catalog), 136                           |
| (see also column-oriented storage)            | polling, 35, 489-558                                  |
| databases on object storage, 203              | polystores, 548                                       |
| document data model, 137                      | portable operating system interface (POSIX), 203, 459 |
|                                               |                                                       |

| 1:+ C1+ 4C0                                                                   |                                                     |
|-------------------------------------------------------------------------------|-----------------------------------------------------|
| compliant filesystems, 460                                                    | primary (see leader-based replication)              |
| Post Office Horizon scandal, 48, 278                                          | primary keys, 132, 606                              |
| Post/Redirect/Get pattern, 564                                                | autoincrementing, 417                               |
| PostgreSQL (database)                                                         | versus partition key, 261                           |
| archiving WAL to object stores, 202                                           | primary-backup replication (see leader-based        |
| change data capture, 504, 506                                                 | replication)                                        |
| distributed transaction support, 330                                          | privacy, 589-597                                    |
| foreign data wrappers, 548                                                    | consent and freedom of choice, 591                  |
| full text search support, 540                                                 | data as assets and power, 594                       |
| in the cloud, <mark>15</mark>                                                 | deleting data, <mark>512</mark>                     |
| JSON Schema validation, 166                                                   | ethical considerations (see ethics)                 |
| leader-based replication, 199                                                 | legislation and self-regulation, 596                |
| log sequence number, 202                                                      | meaning of, 592                                     |
| logical decoding, <mark>208</mark>                                            | regulation, 24                                      |
| materialized view maintenance, 516                                            | surveillance, <mark>590</mark>                      |
| MVCC implementation, 295, 298                                                 | tracking behavioral data, <mark>58</mark> 9         |
| partitioning versus sharding, 252                                             | probabilistic algorithms                            |
| pgvector (vector index), 149                                                  | Bloom filters, 122                                  |
| PL/pgSQL language, 311                                                        | in stream analytics, 515                            |
| PostGIS geospatial indexes, 145                                               | percentile estimation, 42                           |
| preventing lost updates, 301                                                  | process pauses, 366-371                             |
| preventing write skew, 305, 318                                               | processing time (of events), 519                    |
| read-committed isolation, 292                                                 | producers (message streams), 488                    |
|                                                                               | product analytics, 6, 138                           |
| representing graphs, 87                                                       |                                                     |
| serializable snapshot isolation (SSI), 318<br>sharding (see Citus (database)) | programming languages for stored procedures,<br>311 |
| snapshot isolation support, 295, 298                                          | projections (event sourcing), 102                   |
| WAL-based replication, 207                                                    | Prolog (language), 97                               |
| postings list, 146, 268                                                       | (see also Datalog)                                  |
| postmortems, blameless, 48                                                    | Property Graph Query Language (PGQL), 92            |
| PouchDB (database), 222                                                       | property graphs, 86                                 |
| Power BI (business intelligence software), 6,                                 | Cypher query language, 88                           |
| 478                                                                           | Property Graph Query Language (PGQL),               |
| pre-aggregation, 477, 479                                                     | 92                                                  |
| pre-splitting, 257                                                            | property-based testing, 47, 384                     |
| Precision Time Protocol (PTP), 361                                            | Protocol Buffers (data format), 169-171             |
| predicate locks, 316                                                          | provenance of data, 577                             |
| predictive analytics, 4, 586-589                                              | PTP (Precision Time Protocol), 361                  |
| amplifying bias, 587                                                          | publish/subscribe model, 489                        |
| ethics of (see ethics)                                                        | publishers (message streams), 488                   |
| feedback loops, 588                                                           | Pulsar (streaming platform), 495                    |
| preemption, 463                                                               | PyTorch (machine learning library), 479             |
|                                                                               | ry forch (machine learning horary), 4/9             |
| in distributed schedulers, 465                                                | •                                                   |
| of threads, 369                                                               | Q                                                   |
| Prefect (workflow scheduler), 188, 453, 465,                                  | QoS (quality of service), 357                       |
| 474<br>D                                                                      | Qpid (messaging), 492                               |
| Pregel model, 479                                                             | quality of service (QoS), 357                       |
| Presto (query engine), 135                                                    | query engines                                       |
| preventing double-spending (example), 306                                     | - , ,                                               |

| compilation and vectorization, 142          | sensitivity to network problems, 437            |
|---------------------------------------------|-------------------------------------------------|
| in cloud data warehouse, 135                | term number, 434                                |
| operators, 142                              | use in etcd, 412                                |
| optimizing declarative queries, 66          | RAID (redundant array of independent disks),    |
| query languages, 65-108                     | 16                                              |
| Cypher, 88                                  | RAID (Redundant Array of Independent            |
| Datalog, 96                                 | Disks), 45, 459                                 |
| GraphQL, 98                                 | railways                                        |
|                                             | _ *                                             |
| MongoDB aggregation pipeline, 73, 82        | changing the gauge on, 545                      |
| recursive SQL queries, 90                   | modeling network as a graph, 84                 |
| SPARQL, 95                                  | RAM (see memory)                                |
| SQL, 72                                     | RAMCloud (in-memory storage), 134               |
| query optimizers, 142, 473                  | random writes (access pattern), 130             |
| queueing, 37                                | range (CockroachDB), <mark>252</mark>           |
| variability of network delays, 353          | range queries                                   |
| head-of-line blocking, 39                   | in B-trees, 125, 129                            |
| latency and response time, 38               | in LSM-trees, 129                               |
| queues (messaging), 190                     | not efficient in hash maps, 119                 |
| QUIC (protocol), 348                        | with hash sharding, 261                         |
| quorums, 231-237, 606                       | ranking algorithms, 478                         |
| for leaderless replication, 231             | Ray (workflow scheduler), 479                   |
| in consensus algorithms, 435                | RDF (Resource Description Framework), 94, 95    |
| limitations of consistency, 233-235, 412    | RDMA (Remote Direct Memory Access), 15, 23      |
| making decisions in distributed systems,    | React (user interface library), 559             |
| 372                                         | reactive programming, 222                       |
| monitoring staleness, 234                   | read models (event sourcing), 102               |
| multi-region replication, 236               | read path (derived data), 556                   |
| relying on durability, 383                  | read repair (leaderless replication), 231, 412  |
| quotas, 18                                  | read replicas (see followers) (see leader-based |
| quotas, 10                                  | replication)                                    |
| n                                           | read skew (transaction isolation), 293, 336     |
| R                                           | read uncommitted isolation level, 293           |
| R (language), 9, 105, 475                   |                                                 |
| R-trees (indexes), 145                      | read-after-write consistency, 210, 571          |
| R2 (object storage), 15, 459                | read-committed isolation level, 290-293         |
| RabbitMQ (messaging), 190, 199, 492         | implementing, 292                               |
| race conditions, 281                        | multiversion concurrency control (MVCC),        |
| (see also concurrency)                      | 295                                             |
| avoiding with linearizability, 410          | no dirty reads, 290                             |
| caused by dual writes, 502                  | no dirty writes, 291                            |
| causing loss of money, 289                  | read-modify-write cycle, 299                    |
| dirty writes, 291                           | read-scaling architecture, 209, 235, 253        |
| in counter increments, 291                  | read-your-writes consistency (see read-after-   |
| lost updates, 299-303                       | write consistency)                              |
| preventing with serializable isolation, 308 | reader's schema (Avro), 173                     |
| weak transaction isolation, 288             | reads as events, 559                            |
| write skew, 303-308                         | real-time                                       |
| Raft (consensus algorithm), 426, 433, 567   | analytics (see product analytics)               |
| leader-based replication, 199               | collaborative editing, 220                      |
| reduct based replication, 177               | publish/subscribe dataflow, 559                 |

| response time guarantees, 369                               | (see also datacenters)                            |
|-------------------------------------------------------------|---------------------------------------------------|
| time-of-day clocks, 359                                     | consensus across, 437                             |
| real-time operating system (RTOS), 370                      | definition, 212                                   |
| Realm (database), 222                                       | latency, 19                                       |
| rebalancing shards, 257, 606                                | linearizable ID generation, 424                   |
| (see also sharding)                                         | replication across, 216-220, 413, 542             |
| automatic or manual rebalancing, 264                        | leaderless, 236                                   |
| fixed number of shards, 259                                 | multi-leader, <mark>216</mark>                    |
| fixed number of shards per node, 262                        | regions (sharding), <mark>252</mark>              |
| problems with hash mod N, 258                               | register (data structure), 404                    |
| recency guarantee (linearizability), 403                    | regulation (see legal matters)                    |
| recipients (see consumers)                                  | relational data model, 9, 67-84                   |
| recommendation engines, 4                                   | comparison to document model, 80-84               |
| building using DataFrames, 106                              | graph queries in SQL, 90                          |
| iterative processing, 478                                   | in-memory databases with, 134                     |
| reconfiguration (consensus), 436                            | many-to-one and many-to-many relation-            |
| recursive queries                                           | ships, <b>75</b>                                  |
| in Cypher, 89                                               | multi-object transactions, need for, 287          |
| in Datalog, 96                                              | object-relational mismatch, 68                    |
| in SPARQL, 95                                               | representing a reorderable list, 80               |
| lack of, in GraphQL, 99                                     | versus document model                             |
| relational, 96-98                                           | convergence of models, 83                         |
| SQL common table expressions, 90                            | data locality, 82                                 |
| Red Hat, 166                                                | relational databases                              |
| red-black tree, 120                                         | eventual consistency, 209                         |
| redelivery (messaging), 494                                 | history, 67                                       |
| Redis (database)                                            | leader-based replication, 199                     |
| atomic operations, 300                                      | logical logs, 208                                 |
| CRDT support, 228                                           | philosophy compared to Unix, 547, 549             |
| durability, 134                                             | schema changes, 81, 161, 179                      |
| Lua scripting, 312                                          | sharded secondary indexes, 268                    |
| multi-leader replication, 217                               | statement-based replication, 206                  |
| process-per-core model, 254                                 | use of B-tree indexes, 125                        |
| single-threaded execution, 309                              | relationships (see edges)                         |
| redo log (see write-ahead log)                              | reliability, 43-49, 539                           |
| Redpanda (messaging), 190, 203, 499                         | building a reliable system from unreliable        |
| Redshift (database), 135                                    | components, 347                                   |
| redundancy                                                  | hardware faults, 44                               |
| hardware components, 45                                     | human errors, 47                                  |
| of derived data, 11                                         | importance of, 48                                 |
| (see also derived data)                                     | of messaging systems, 490                         |
| redundant array of independent disks (RAID),                | software faults, 46                               |
| 16                                                          | Remote Direct Memory Access (RDMA), 15, 23        |
| Redundant Array of Independent Disks                        | Remote Method Invocation (Java RMI), 183          |
| •                                                           |                                                   |
| (RAID), 45, 459  Read-Solomon codes (error correction), 459 | remote procedure calls (RPCs), 183-186            |
| Reed–Solomon codes (error correction), 459                  | (see also services)                               |
| refactoring, 55<br>(see also evolvability)                  | data encoding and evolution, 186 issues with, 183 |
| · ·                                                         |                                                   |
| regions (geographic distribution), 211                      | using Avro, 176                                   |

| versus message brokers, 189                   | residence laws for data, 20, 255             |
|-----------------------------------------------|----------------------------------------------|
| rendezvous hashing, <mark>263</mark>          | resilient systems, 43                        |
| renewable energy, <mark>20</mark>             | (see also fault tolerance)                   |
| repeatable reads (transaction isolation), 298 | Resource Description Framework (RDF), 94, 95 |
| replication, 197-244, 606                     | resource isolation, 23, 254                  |
| and durability, 283                           | resource limits, 18                          |
| conflict resolution and, 302                  | response time                                |
| consistency properties, 209-215               | as performance metric, 37, 451               |
| consistent prefix reads, 213                  | guarantees on, <mark>369</mark>              |
| monotonic reads, 212                          | impact on users, 41                          |
| reading your own writes, 210                  | in replicated systems, 235                   |
| in distributed filesystems, 459               | latency versus, 38                           |
| leaderless, 229-242                           | mean and percentiles, 40                     |
| detecting concurrent writes, 237-242          | metrics for, 41                              |
| limitations of quorum consistency,            | user experience, 40                          |
| 233-235, 412                                  | responsibility and accountability, 587       |
| monitoring staleness, 234                     | REST (Representational State Transfer), 181  |
| multi-leader, 215-229                         | (see also services)                          |
| across multiple regions, 216, 413             | Restate (workflow engine), 188               |
| conflict resolution, 222-229                  | RethinkDB (database)                         |
| replication topologies, 218-220               | join support, <mark>83</mark>                |
| reasons for using, 19, 197                    | key-range sharding, 257                      |
| replication lag, 209-215                      | retrieval-augmented generation, 147          |
| replication logs (see logs)                   | retry storm, 38, 47                          |
| sharding and, 251                             | reverse ETL, 10                              |
| single-leader, 198-208                        | Riak (database)                              |
| failover, 204                                 | CRDT support, 228, 237                       |
| implementation of replication logs,           | dotted version vectors, 242                  |
| 206-208                                       | gossip protocol, 267                         |
| relation to consensus, 434, 437               | hash sharding, <mark>260</mark>              |
| setting up new followers, 201                 | leaderless replication, 229                  |
| synchronous versus asynchronous,              | linearizability, lack of, 412                |
| 200-201                                       | multi-region support, 237                    |
| state machine replication, 207, 312, 433, 501 | rebalancing, 264                             |
| event sourcing, 102                           | secondary indexes, 270                       |
| reliance on determinism, 387                  | sloppy quorums, 236                          |
| using consensus, 437                          | vnodes (sharding), 252                       |
| using erasure coding, 459                     | ring buffers, 498                            |
| using object storage, 202                     | RisingWave (database), 517                   |
| versus backups, 198                           | road network, 84                             |
| with heterogeneous data systems, 502          | roaring bitmaps, 139                         |
| Representational State Transfer (REST), 181   | rockets, 378                                 |
| (see also services)                           | RocksDB (storage engine), 121                |
| representations of data (see data models)     | as embedded storage engine, 125              |
| reprocessing data, 500, 545, 546              | leveled compaction, 124                      |
| (see also evolvability)                       | serving derived data, 481                    |
| request hedging, 235                          | rollbacks (transactions), 277                |
| request identifiers, <mark>564, 568</mark>    | rolling upgrades, 46, 161, 255, 347          |
| request routing, 265-268                      | routing (see request routing)                |

| row-based replication, 208                 | in service calls, 186                          |
|--------------------------------------------|------------------------------------------------|
| row-oriented storage, 137                  | flexibility in document model, 80              |
| RPCs (see remote procedure calls)          | for analytics, 77-79                           |
| RTOS (real-time operating system), 370     | for JSON and XML, 165, 166                     |
| rules (Datalog), 97                        | generation and migration using ORMs, 68        |
| run-length encoding, 139                   | merits of, 177                                 |
| Rust (programming language), 370           | migration, <mark>81</mark>                     |
|                                            | Protocol Buffers, 169-171                      |
| S                                          | schema migration on railways, <mark>545</mark> |
|                                            | traditional approach to design, fallacy in,    |
| S3 (object storage) (see Amazon S3 (object | 511                                            |
| storage))                                  | scientific computing, 23                       |
| SaaS (see software as a service (SaaS))    | scikit-learn (Python library), 9               |
| safety and liveness properties, 382, 429   | SCTP (Stream Control Transmission Protocol),   |
| safety guarantees, 278                     | 348                                            |
| sagas (see compensating transactions)      | ScyllaDB (database)                            |
| Samza (stream processor), 515              | cluster metadata, 267                          |
| SAN (Storage Area Network), 51             | consistency level ANY, 236                     |
| SAP HANA (database), 135                   | hash-range sharding, 258, 262                  |
| scalability, 49-52, 539                    | last-write-wins conflict resolution, 237       |
| auto-scaling, 265                          | leaderless replication, 229                    |
| by sharding, 253                           | lightweight transactions, 286                  |
| describing load, 50                        | linearizability, lack of, 412                  |
| describing performance, 37                 | log-structured storage, 121                    |
| in distributed systems, 19                 | multi-region support, 236                      |
| linear, 50                                 | use of clocks, 234, 363                        |
| principles for, 52                         | vnodes (sharding), 252                         |
| replication and, 209                       | search engines (see full-text search)          |
| scaling up versus scaling out, 51          | searching on streams, 517                      |
| scaling out, 51, 253                       | secondaries (see followers) (see leader-based  |
| (see also shared-nothing architecture)     | replication)                                   |
| scaling up, 51                             | secondary indexes, 132, 607                    |
| SCD (slowly changing dimension), 526       | for many-to-many relationships, 77             |
| scheduling                                 | problems with dual writes, 502                 |
| algorithms, 464                            | sharding, 268-271, 272                         |
| batch jobs, 462-465                        | global, 270                                    |
| gang scheduling, 463                       | index maintenance, 545                         |
| schema-on-read, 80, 178                    | local, 268                                     |
| schema-on-write, 80                        | updating, transaction isolation and, 287       |
| schemaless databases (see schema-on-read)  | secondary sort (MapReduce), 472                |
| schemas, 606                               | sed (Unix tool), 455                           |
| Avro, 172-177                              | self-hosting, 12, 135                          |
| reader determining writer's schema, 175    | self-joins, 531                                |
| schema evolution, 173                      | self-validating systems, 577                   |
| dynamically generated, 176                 | semantic search, 147                           |
| evolution of, 545                          | Semantic Web, 94                               |
| affecting application code, 161            | semisynchronous replication, 201               |
| compatibility checking, 176                | sender (see producers)                         |
| in databases, 178-180                      | sequential writes (access pattern), 130        |
|                                            | sequential writes (access pattern), 130        |

| serializability, 282, 289, 308-322, 607        | hot shards, 255                             |
|------------------------------------------------|---------------------------------------------|
| linearizability versus, 407                    | in batch processing, 453                    |
| pessimistic versus optimistic concurrency      | key-range splitting, 257                    |
| control, 318                                   | multishard operations, 560                  |
| serial execution, 309-313                      | enforcing constraints, 568                  |
| sharding, 312                                  | secondary index maintenance, 545            |
| using stored procedures, 310, 433              | of key-value data, 255-264                  |
| serializable snapshot isolation (SSI), 317-322 | by key range, <mark>256</mark>              |
| detecting stale MVCC reads, 319                | skew and hot spots, 263                     |
| detecting writes that affect prior reads,      | origin of the term, <mark>252</mark>        |
| 321                                            | partition key, 253, 256                     |
| distributed execution, 322, 333                | rebalancing shards, 257-265                 |
| performance of SSI, 322                        | automatic or manual rebalancing, 26         |
| preventing write skew, 319-322                 | problems with hash mod N, 258               |
| strict serializability, 408, 571               | using fixed number of shards, 259           |
| two-phase locking (2PL), 313-317               | using N shards per node, 262                |
| index-range locks, 317                         | request routing, 265-268                    |
| performance, 315                               | secondary indexes, 268-271                  |
| Serializable (Java), <mark>164</mark>          | global, 270                                 |
| serializable snapshot isolation (SSI), 317-322 | local, 268                                  |
| serialization, 164                             | serial execution of transactions and, 312   |
| (see also encoding)                            | sorting sharded data, 469                   |
| serverless, 22                                 | shared logs, 433-437, 567                   |
| service discovery, 184, 265, 440               | algorithms, 433                             |
| registration, 185                              | for event sourcing, 105                     |
| using DNS, 185, 268, 440                       | for messaging, 495-500                      |
| service framework, <mark>182</mark>            | relation to consensus, 429                  |
| service level agreements (SLAs), 42, 50        | using, 433                                  |
| service level objectives (SLOs), 42            | shared mode (locks), 314                    |
| service mesh, 185                              | shared subscription (message queues), 493   |
| Service Organization Control (SOC), 25         | shared-disk architecture, 51, 459           |
| service time, 38                               | shared-memory architecture, 51              |
| service-oriented architecture (SOA), 21        | shared-nothing architecture, 51, 607        |
| (see also services)                            | distributed filesystems, 459                |
| services, 180-186                              | (see also distributed filesystems)          |
| causal dependencies across services, 542       | use of network, 347                         |
| loose coupling, 550                            | sharks                                      |
| microservices, 21                              | biting undersea cables, 350                 |
| relation to batch/stream processors, 451,      | counting (example), 83                      |
| 554                                            | Shenandoah (garbage collector), 370         |
| remote procedure calls (RPCs), 183-186         | shredding                                   |
| similarity to databases, 180                   | deletion (see crypto-shredding)             |
| web services, 181                              | in columnar encoding, 137                   |
| session windows (stream processing), 522       | in relational model, <mark>80</mark>        |
| (see also windows)                             | shuffle (batch processing), 469-471         |
| sharding, 251-272, 607                         | shunning (Fossil), 512                      |
| and consensus, 434                             | siblings (concurrent values), 225, 241, 303 |
| and replication, 251                           | (see also conflicts)                        |
| distributed transactions across shards, 323    | silo, 7                                     |

```
SIMD (single-instruction-multidata) instruc-
                                                        synchronized clocks for global snapshots,
   tions, 143
similarity search
                                                    Snowflake (database), 15, 135, 136, 453
   edit distance, 147
                                                        column-oriented storage, 138
                                                        handling writes, 141
   genome data, 108
simplicity, 54
                                                        sharding and clustering, 262
Singer (data connector), 8
                                                        Snowpark, 474
single-instruction-multidata (SIMD) instruc-
                                                    Snowflake (ID generator), 419
   tions, 143
                                                    snowflake schemas, 79
single-leader replication (see leader-based repli-
                                                    SOA (service-oriented architecture), 21
   cation)
                                                        (see also services)
single-threaded execution, 300, 309, 497, 511
                                                    SOAP (web services), 183
SingleStore (database), 134, 135
                                                    SOC (Service Organization Control), 25
site reliability engineer (SRE), 17
                                                    social graph, 85
size-tiered compaction, 124, 131
                                                    society, responsibility toward, 24, 597
skew, 607
                                                    sociotechnical systems, 47
   clock skew, 362-365, 412
                                                    software as a service (SaaS), 1, 12
   in transaction isolation
                                                        ETL from, 8
      read skew, 293, 336
                                                        multitenancy, 254
       write skew, 303-308, 319-322
                                                    software bugs, 46, 576
          (see also write skew)
                                                    solar storm, 45
   meanings of, 294
                                                    solid state drives (SSDs)
   unbalanced workload, 255
                                                        compared to object storage, 203
      compensating for, 263
                                                        detecting corruption, 565, 576
      due to celebrities, 263
                                                        failure rate, 44
      for time-series data, 257
                                                        faults in, 283
skip list, 120
                                                        firmware bugs, 46
Slack (group chat), 99
                                                        read throughput, 129
SLAs (service level agreements), 42, 50
                                                        sequential versus random writes, 130
SlateDB (database), 122, 203
                                                    Solr (search server)
slicing and dicing, 135
                                                       local secondary indexes, 270
sliding windows (stream processing), 522
                                                        request routing, 267
   (see also windows)
                                                        use of Lucene, 147
sloppy quorums, 236
                                                    sort (Unix tool), 455, 457, 461
                                                    sort-merge joins (MapReduce), 471
SLOs (service level objectives), 42
slowly changing dimension (data warehouses),
                                                    Sorted String Tables (see SSTables)
                                                    source of truth (see systems of record)
smearing (leap seconds adjustments), 361
                                                    Spanner (database)
snapshots (databases)
                                                        consistency model, 408
   as backups, 198
                                                        data locality, 82
   computing derived data, 548
                                                        in the cloud, 15
   in change data capture, 504
                                                        snapshot isolation using clocks, 366
   serializable snapshot isolation (SSI), 317-322
                                                        transactions, 279, 333
   setting up a new replica, 202
                                                        TrueTime API, 365
   snapshot isolation and repeatable read, 282,
                                                    Spark (processing framework), 9, 15, 453, 465,
       293-299
      implementing with MVCC, 295
                                                        cost efficiency, 475
      indexes and MVCC, 298
                                                        DataFrames, 105, 475
      visibility rules, 297
                                                        fault tolerance, 466
```

| for data warehouses, 135                                             | SS2PL (strong strict two-phase locking), 313                                            |
|----------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| high availability using ZooKeeper, 438                               | SSDs (see solid state drives)                                                           |
| MLlib, 478                                                           | SSI (serializable snapshot isolation), 317-322                                          |
| query optimizer, 473                                                 | SSTables (storage format), 119-124                                                      |
| shuffling data, 470                                                  | constructing and maintaining, 120                                                       |
| Spark Streaming, 515, 527                                            | making LSM-Tree from, 121                                                               |
| streaming SQL support, 515                                           | staged rollout (see rolling upgrades)                                                   |
| use for ETL, 477                                                     | staleness (old data), 210                                                               |
| SPARQL (query language), 85, 95                                      | cross-channel timing dependencies, 410                                                  |
| sparse bitmaps (columnar encoding), 139                              | in leaderless databases, 230                                                            |
| sparse indexes (SSTables), 119<br>sparse matrices, 1 <mark>06</mark> | in multiversion concurrency control, 319                                                |
|                                                                      | monitoring for, 234                                                                     |
| specialized hardware, in distributed systems, 19                     | of client state, 558                                                                    |
| split brain, 205, 266, 607                                           | versus linearizability, 403                                                             |
| enforcing constraints, 567                                           | versus timeliness, 571                                                                  |
| in consensus algorithms, 425, 434                                    | standbys (see leader-based replication)                                                 |
| preventing, 412                                                      | star replication topologies, 218                                                        |
| using fencing tokens to avoid, 374-377                               | star schemas, 77-79                                                                     |
| spot instances, 465                                                  | Star Wars analogy (event time versus process-                                           |
| spreadsheets, 2, 105                                                 | ing time), 519                                                                          |
| dataflow programming, 551                                            | starvation (scheduling), 463                                                            |
| pivot table, 106                                                     | state                                                                                   |
| SQL (Structured Query Language), 55, 67, 135                         | derived from log of immutable events, 508                                               |
| for analytics, 7, 136                                                | interplay between state changes and applica                                             |
| graph queries in, 90                                                 | tion code, 553                                                                          |
| isolation levels standard, issues with, 299                          | maintaining derived state, 544                                                          |
| joins, 72                                                            | maintenance by stream processor in                                                      |
| résumé (example), 69                                                 | stream-stream joins, 523                                                                |
| social network home timelines (example),                             | observing derived state, 555-561                                                        |
| 34                                                                   | rebuilding after stream processor failure,                                              |
| SQL injection vulnerability, 379                                     | 529                                                                                     |
| statement-based replication, 206                                     | separation of application code and, 552                                                 |
| stored procedures, 311<br>views, 97                                  | state machine replication, 207, 312, 433, 501                                           |
|                                                                      | event sourcing, 102                                                                     |
| SQL Server (database) archiving WAL to object stores, 202            | reliance on determinism, 387                                                            |
|                                                                      | stateless systems, 3                                                                    |
| change data capture, 504<br>data warehousing support, 135            | statement-based replication, 206, 387<br>statically typed languages, analogy to schema- |
| distributed transaction support, 330                                 | on-write, 81                                                                            |
| leader-based replication, 199                                        | statistical and numerical algorithms, 105                                               |
| multi-leader replication, 217                                        | StatsD (metrics aggregator), 491                                                        |
| preventing lost updates, 301                                         | steal time, 368                                                                         |
| preventing write skew, 305, 314                                      | stock market feeds, 490                                                                 |
| read-committed isolation, 292                                        | stop-the-world (see garbage collection)                                                 |
| serializable isolation, 314, 318                                     | storage area network (SAN), 51, 459                                                     |
| snapshot isolation support, 295                                      | storage engines, 115-151                                                                |
| T-SQL language, 311                                                  | column-oriented, 136-143                                                                |
| 1-5QL language, 311<br>SQLite (database), 21, 125, 202               | column compression, 139-140                                                             |
| SRE (site reliability engineer), 17                                  | defined, 137                                                                            |
| SKE (SHE TEHROLINY ENGINEET), 17                                     | defined, 15/                                                                            |

```
Parquet, 136, 137, 180
                                                           stream-table join, 524
      sort order in, 140-141
                                                           table-table join, 524
      versus wide-column model, 140
                                                           time-dependence of, 525
       writing to, 141
   in-memory storage, 133, 283
                                                       end-to-end, pushing events to clients, 559
   row-oriented, 116-134
                                                       messaging systems (see messaging systems)
      B-trees, 125-128
                                                       processing (see stream processing)
      comparing B-trees and LSM-trees,
                                                       relation to databases, 500-513
          129-132
                                                           (see also changelogs)
      defined, 137
                                                           API support for change streams, 506
stored procedures, 310-312, 607
                                                           change data capture, 503-506
                                                           derivative of state by time, 509
   and shared logs, 433
   pros and cons of, 311
                                                           event sourcing, 507
                                                           keeping systems in sync, 501-502
   similarity to stream processors, 552
                                                           philosophy of immutable events.
Storm (stream processor), 515
   distributed RPC, 518, 560
                                                              508-513
   Trident state handling, 528
                                                       topics, 488
straggler events, 520
                                                       transmitting, 488-500
Stream Control Transmission Protocol (SCTP),
                                                    strict serializability, 408, 571
                                                    striping (in columnar encoding), 137
stream processing, 487-531, 607
                                                    strong consistency (see linearizability)
   accessing external services within job, 527,
                                                    strong eventual consistency, 226
       528, 562
                                                    strong one-copy serializability, 408
   combining with batch processing, 546
                                                    strong strict two-phase locking (SS2PL), 313
                                                    Structured Query Language (see SQL (Struc-
   comparison to batch processing, 513
   complex event processing (CEP), 514
                                                       tured Query Language))
   fault tolerance, 526-529
                                                    subjects, predicates, and objects (in triple-
      atomic commit, 527
                                                       stores), 92
                                                    subscribers (message streams), 190, 488
      idempotence, 528
      microbatching and checkpointing, 527
                                                       (see also consumers)
      rebuilding state after a failure, 529
                                                    supercomputers, 23
   for data integration, 544-546
                                                    Superset (data visualization software), 478
   for event sourcing, 105
                                                    surveillance, <mark>590</mark>
   maintaining derived state, 544
                                                       (see also privacy)
   maintenance of materialized views, 516
                                                    sushi principle, 10
   messaging systems (see messaging systems)
                                                    sustainability, 20
   reasoning about time, 518-522
                                                    Swagger (service definition format), 181, 182
      event time versus processing time, 519,
                                                    swapping to disk (see virtual memory)
          527, 546
                                                    Swift (programming language), 370
      knowing when window is ready, 520
                                                    sync engines, 220-222
      types of windows, 521
                                                       examples of, 222
   relation to databases (see streams)
                                                       for local-first software, 221
   relation to services, 554
                                                    synchronous networks, 355, 607
   relationship to batch processing, 453
                                                       comparison to asynchronous networks, 355
   search on streams, 517
                                                       system model, 380
   single-threaded execution, 497, 511
                                                    synchronous replication, 200, 215, 607
   stream analytics, 515
                                                    system administrator (sysadmin), 17
   stream joins, 523-526
                                                    system models, 371, 380-387
       stream-stream join, 523
                                                       assumptions in, 575
```

| correctness of algorithms, 382                 | Enterprise Message Service, 492            |
|------------------------------------------------|--------------------------------------------|
| mapping to the real world, 383                 | StreamBase (stream analytics), 515         |
| safety and liveness, 382                       | TiDB (database)                            |
| systems of record, 11, 607                     | consensus-based replication, 199           |
| change data capture, 504, 541                  | regions (sharding), <mark>252</mark>       |
| event logs, 102                                | request routing, 267                       |
| treating event log as, 509                     | serving derived data, 481                  |
| systems thinking, <mark>58</mark> 9            | sharded secondary indexes, 271             |
| , 0                                            | snapshot isolation support, 295            |
| Т                                              | timestamp oracle, 424                      |
| •                                              | transactions, 279, 333                     |
| t-digest (algorithm), 42                       | use of model-checking, 385                 |
| Tableau (data visualization software), 6, 478  | tiered storage, 203, 499                   |
| table–table joins, 524                         | TigerBeetle (database), 108, 384, 386      |
| tail (Unix tool), 496                          | TigerGraph (database), 92                  |
| tail latency (see latency)                     | Tigris (object storage), 459               |
| tail vertex (property graphs), 87              | TileDB (database), 107                     |
| task (workflows) (see workflow engines)        | time                                       |
| TCP (Transmission Control Protocol), 348       | concurrency and, 239                       |
| comparison to circuit switching, 356           | cross-channel timing dependencies, 410     |
| comparison to UDP, 354                         |                                            |
| connection failures, 351                       | in distributed systems, 358-371            |
| flow control, <b>353</b> , <b>489</b>          | (see also clocks)                          |
| packet checksums, 379, 565, 575                | clock synchronization and accuracy, 360    |
| reliability and duplicate suppression, 563     | relying on synchronized clocks, 362-366    |
| retransmission timeouts, 355                   | process pauses, 366-371                    |
| use for transaction sessions, 285              | reasoning about, in stream processors,     |
| Temporal (workflow engine), 188                | 518-522                                    |
| TensorFlow (machine learning library), 479     | event time versus processing time, 519,    |
| Teradata (database), 15, 135                   | 527, 546                                   |
| term-partitioned indexes (see global secondary | knowing when window is ready, 520          |
| indexes)                                       | timestamp of events, 521                   |
| termination (consensus), 428, 432              | types of windows, 521                      |
| testing, 47                                    | system models for distributed systems, 380 |
| thrashing (out of memory), 368                 | time-dependence in stream joins, 525       |
| threads (concurrency)                          | time travel, 452                           |
| actor model, 191, 518                          | time-of-day clocks, 359, 422               |
| (see also event-driven architecture)           | time-series data                           |
| atomic operations, 280                         | as DataFrames, 107                         |
| background threads, 121                        | column-oriented storage, 138               |
| execution pauses, 357, 367-369                 | timeliness, 571                            |
| memory barriers, 416                           | coordination-avoiding data systems, 574    |
| preemption, 369                                | correctness of dataflow systems, 572       |
| single (see single-threaded execution)         | timeouts, 348, 607                         |
| three-phase commit (3PC), 328                  | dynamic configuration of, 355              |
| three-way relationships, 88                    | for failover, 206                          |
| Thrift (data format), 169                      | length of, 352                             |
| throughput, 37, 50, 452                        | TimescaleDB (database), 138                |
| TIBCO, 190                                     | timestamps, 420                            |
|                                                |                                            |

| assigning to events in stream processing,      | serializability, 308-322                     |
|------------------------------------------------|----------------------------------------------|
| 521                                            | actual serial execution, 309-313             |
| for read-after-write consistency, 211          | pessimistic versus optimistic concur-        |
| for transaction ordering, 366                  | rency control, 318                           |
| insufficiency for enforcing constraints, 425   | serializable snapshot isolation (SSI),       |
| key range sharding by, 257                     | 317-322                                      |
| Lamport, 420                                   | two-phase locking (2PL), 313-317             |
| logical, 543                                   | single-object and multi-object, 284-288      |
| ordering events, 362                           | handling errors and aborts, 287              |
| timestamp oracle, 424                          | need for multi-object transactions, 287      |
| TLA+ (specification language), 384             | single-object writes, <mark>286</mark>       |
| token bucket algorithm, <mark>38</mark>        | snapshot isolation (see snapshots)           |
| tombstones, 121, 132, 505                      | strict serializability, 408                  |
| topics (messaging), 190, 488                   | weak isolation levels, 288-308               |
| torn pages (B-trees), 128                      | preventing lost updates, 299-303             |
| total order, 427, 607                          | read-committed, 290-294                      |
| broadcast (see shared logs)                    | Transmission Control Protocol (TCP) (see TCP |
| limits of, 542                                 | (Transmission Control Protocol))             |
| on logical timestamps, 420                     | transmitting event streams, 488-500          |
| tracing, 20                                    | traversal (graphs), 87                       |
| tracking behavioral data, <mark>58</mark> 9    | trie (data structure), 119, 120, 147         |
| (see also privacy)                             | triggers (databases), 489                    |
| trade-offs, in data systems architecture, 1-25 | Trino (data warehouse), 135                  |
| transaction coordinator (see coordinator)      | federated databases, 548                     |
| transaction manager (see coordinator)          | query optimizer, 473                         |
| transaction processing, 5-6                    | use for ETL, 477                             |
| comparison to analytics, 5                     | workflow example, 464                        |
| comparison to data warehousing, 134            | triple-stores, 92-96                         |
| transactions, 277-337, 607                     | tumbling windows (stream processing), 522,   |
| ACID properties of, 279                        | 527                                          |
| atomicity, 280                                 | (see also windows)                           |
| consistency, 280                               | Turbopuffer (vector search), 203             |
| durability, <mark>282</mark>                   | Turtle (RDF data format), 93                 |
| isolation, 281                                 | Twitter (see X (social network))             |
| and derived data integrity, 571                | two-phase commit (2PC), 324-328, 608         |
| and replication, 215                           | confusion with two-phase locking, 313        |
| compensating (see compensating transac-        | coordinator failure, 327                     |
| tions)                                         | coordinator recovery, 331                    |
| concept of, 278                                | how it works, 326                            |
| distributed transactions, 323-335              | performance cost, 329                        |
| avoiding, 541, 549, 566-575                    | problems with XA transactions, 332           |
| failure amplification, 544                     | transactions holding locks, 331              |
| for sharded systems, 253                       | two-phase locking (2PL), 313-317, 608        |
| in doubt/uncertain status, 327, 331            | confusion with two-phase commit, 313         |
| two-phase commit, 324-328                      | growing and shrinking phases, 315            |
| use of, 328-330                                | index-range locks, 317                       |
| XA transactions, 330-333                       | performance of, 315                          |
| OLTP versus analytical queries, 477            | type checking, dynamic versus static, 81     |
| purpose of, 278                                |                                              |

| U                                             | uTP protocol (BitTorrent), 348                     |
|-----------------------------------------------|----------------------------------------------------|
| UDP (User Datagram Protocol)                  | UUIDs (universally unique identifiers), 419        |
| comparison to TCP, 354                        | · -                                                |
| multicast, 490                                | V                                                  |
| Ultima Online (game), 252                     |                                                    |
| unbounded datasets, 608                       | validity (consensus), 428, 432                     |
| (see also streams)                            | vBuckets (sharding), 252                           |
|                                               | vector clocks, 242                                 |
| unbounded delays, 608                         | (see also version vectors)                         |
| in networks, 353                              | and Lamport/hybrid logical clocks, 422             |
| process pauses, 367                           | and version vectors, 242                           |
| unbundling databases, 546-561                 | vector embedding, 147                              |
| composing data storage technologies,          | vectorized processing, 142, 147                    |
| 547-551                                       | vendor lock-in, 14                                 |
| designing applications around dataflow,       | Venice (database), 480                             |
| 551-555                                       | verification, 575-578                              |
| observing derived state, 555-561              | avoiding blind trust, 576                          |
| materialized views and caching, 556           | designing for auditability, 577                    |
| multishard data processing, 560               | end-to-end integrity checks, 577                   |
| pushing state changes to clients, 558         | tools for auditable data systems, <mark>578</mark> |
| uncertain (transaction status) (see in doubt) | version control systems                            |
| union type (in Avro), 175                     | merge conflicts, 225                               |
| uniq (Unix tool), 455, 461                    | reliance on immutable data, 512                    |
| uniqueness constraints                        | version vectors, 220, 242                          |
| requiring consensus, <mark>56</mark> 7        | dotted, 242                                        |
| requiring linearizability, 409                | versus vector clocks, 242                          |
| uniqueness in log-based messaging, 567        | Vertica (database), 135, 141                       |
| Unity (data catalog), 136                     | vertical scaling (see scaling up)                  |
| universally unique identifiers (UUIDs), 419   | vertices (in graphs), 84, 86                       |
| Unix philosophy                               | video games, 222                                   |
| comparison to relational databases, 547, 549  | video transcoding (example), 410                   |
| comparison to stream processing, 513          | views (SQL queries), 97                            |
| Unix pipes, 454, 464                          | (see also materialization)                         |
| unmarshaling (see decoding)                   | Viewstamped Replication (consensus algo-           |
| UPDATE statement (SQL), 81                    | rithm), 426, 433, 434                              |
| updates                                       | virtual block device, 16                           |
| preventing lost updates, 299-303              | virtual file system (VFS), 458, 459                |
| atomic write operations, 300                  | virtual machines, 15                               |
| automatically detecting lost updates, 301     | context switches, 368                              |
| compare-and-set (CAS), 302                    |                                                    |
| conflict resolution and replication, 302      | network performance, 353                           |
| using explicit locking, 300                   | noisy neighbors, 354                               |
| preventing write skew, 303-308                | virtualized clocks in, 361                         |
|                                               | virtual memory, 39, 368                            |
| User Datagram Protocol (UDP) (see UDP (User   | Virtuoso (database), 96                            |
| Datagram Protocol))<br>utilization            | VisiCalc (spreadsheets), 551                       |
|                                               | Vitess (database), 257                             |
| batch process scheduling, 463                 | vnodes (sharding), 252                             |
| increasing through preemption, 465            | vocabularies (linked data), 94                     |
| trade-off with latency, 356                   | Voice over IP (VoIP), 354                          |

| VoltDB (database)                                                       | characterizing, 303-307, 319                |
|-------------------------------------------------------------------------|---------------------------------------------|
| cross-shard serializability, 312                                        | examples of, 303, 305                       |
| deterministic stored procedures, 312                                    | materializing conflicts, 307                |
| in-memory storage, 134                                                  | occurrence in practice, 576                 |
| process-per-core model, 254                                             | phantoms, 307                               |
| secondary indexes, 270                                                  | preventing                                  |
| serial execution of transactions, 309                                   | in snapshot isolation, 319-322              |
| statement-based replication, 207, 529                                   | in two-phase locking, 316-317               |
| transactions in stream processing, 528                                  | options for, 304                            |
| r                                                                       | write-ahead log (WAL), 128, 188, 207        |
| W                                                                       | writer's schema (Avro), 173                 |
|                                                                         | writes (database)                           |
| WAL (write-ahead log), 128, 188, 207                                    | atomic write operations, 300                |
| WAL-G (backup tool), 202                                                | detecting writes affecting prior reads, 321 |
| wall-clock time, 359                                                    | preventing dirty writes with read commit-   |
| WarpStream (messaging), 203, 499                                        | ted, 291                                    |
| web graph, 84                                                           | WS-* framework, 183                         |
| web services, 181-183                                                   | WS-AtomicTransaction (2PC), 324             |
| (see also services)                                                     | W3-Atomic Hansaction (2FC), 324             |
| webhooks, 491                                                           | v                                           |
| webMethods (messaging), 190                                             | Χ                                           |
| WebSocket (protocol), 558                                               | X (social network)                          |
| wide-column data model, 82, 140                                         | constructing home timelines (example), 34,  |
| windows (stream processing), 515, 518-522                               | 511, 524, 557                               |
| infinite windows for changelogs, 516, 524                               | cost of joins, 74                           |
| knowing when all events have arrived, 520                               | Snowflake (ID generator), 419               |
| stream joins within a window, 523                                       | XA transactions, 324, 330-333               |
| types of windows, 521                                                   | heuristic decisions, 332                    |
| WITH RECURSIVE syntax (SQL), 90                                         | problems with, 332                          |
| Word2Vec (language model), 148                                          | xargs (Unix tool), 455                      |
| workflow engines, 187                                                   | XFS (filesystem), 458                       |
| Airflow (see Airflow (workflow scheduler))                              | XGBoost (machine learning library), 479     |
| batch processing, 464                                                   | XML                                         |
| Camunda (see Camunda (workflow                                          | binary variants, 167                        |
| engine))                                                                | data locality, 82                           |
| Dagster (see Dagster (workflow scheduler))                              | encoding RDF data, 94                       |
| durable execution, 188                                                  | for application data, issues with, 165      |
|                                                                         | in relational databases, 80                 |
| ETL (see extract-transform-load (ETL))\nexecutor, 187                   | XML databases, 67, 82                       |
|                                                                         |                                             |
| orchestrators, 187, 453                                                 | Xorq (query engine), 548                    |
| Orkes (see Orkes (workflow engine))                                     | XPath, 82                                   |
| Prefect (see Prefect (workflow scheduler)) reliance on determinism, 387 | XQuery, 82                                  |
| Restate (see Restate (workflow engine))                                 | γ                                           |
| Temporal (see Temporal (workflow engine))                               | Yahoo response time study, 41               |
| working set, <mark>45</mark> 7                                          | YARN (job scheduler), 462, 463, 465, 552    |
| write amplification, 130                                                | Yjs (sync engine), 222                      |
| write path (derived data), <mark>555</mark>                             | YugabyteDB (database)                       |
| write skew (transaction isolation), 303-308                             | hash-range sharding, 262                    |
|                                                                         | man mige and directing, 202                 |

| key-range sharding, 257                  | ZGC (Z garbage collector), 370            |
|------------------------------------------|-------------------------------------------|
| multi-leader replication, 217            | Zipkin (tracing tool), 20                 |
| request routing, 267                     | zombies (split brain), <mark>374</mark>   |
| sharded secondary indexes, 271           | zones (cloud computing) (see availability |
| tablets (sharding), 252                  | zones)                                    |
| transactions, 279, 333                   | ZooKeeper (coordination service), 437-440 |
| use of clock synchronization, 366        | generating fencing tokens, 376, 434, 438  |
|                                          | linearizable operations, 412              |
| 7                                        | locks and leader election, 408            |
| Zab (consensus algorithm), 412, 426, 433 | observers, 440                            |
| zero-copy, 164                           | use for service discovery, 185, 440       |
| zero-disk architecture (ZDA), 203        | use for shard assignment, 267             |
| ZeroMQ (messaging library), 490          | use of Zab algorithm, 426                 |
