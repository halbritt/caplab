# Index

<span id="page-486-0"></span>

| A                                             | B                                           |
|-----------------------------------------------|---------------------------------------------|
| A/B testing, 277                              | background threads, as source of noise, 263 |
| accessibility, efficiency and, 24             | backward compatibility, 58                  |
| accuracy, in performance context, 5           | benchmarks/benchmarking, 275-327            |
| Adamczewski, Bartosz, on optimizations/pessi‐ | (see also efficiency assessment)            |
| mizations, 381                                | avoiding efficiency comparisons with older  |
| Alexandrescu, Andrei                          | experiment results, 265                     |
| on code that "leans to the left", 131         | cheating/lying stereotype, 254              |
| on efficient design, 8                        | choosing test data and conditions, 280      |
| on speed versus correctness, 104              | compiler optimization countermeasures,      |
| algorithm and data structure optimization     | 303                                         |
| level, 100                                    | data-driven efficiency assessment and,      |
| Allen, Arnold O., on performance, 4           | 250-256                                     |
| alloc (heap) profile, 360-364                 | determining appropriate level, 271          |
| Allocator (see Go Allocator)                  | functional testing versus, 252-254          |
| Amazon, cost of latency to, 31                | human error and, 256-258                    |
| Andreessen, Marc, on democratization of soft‐ | implementation, 275-327                     |
| ware, 20                                      | levels of, 266-273                          |
| anonymous file mapping, 169                   | macrobenchmarks (see macrobenchmarks/       |
| arrays                                        | macrobenchmarking)                          |
| lined lists versus, 131                       | microbenchmarks (see microbenchmarks/       |
| overusing memory with, 445-449                | microbenchmarking)                          |
| Assembly language                             | misinterpretation of results, 255           |
| CPU time and, 115-118                         | noise problems, 260-266                     |
| machine code and, 116                         | in production, 268                          |
| asymptotic complexity with Big O notation,    | relevance, 258-260                          |
| 243-246                                       | stress/load tests versus, 251               |
| asymptotic complexity, "estimated" efficiency | benchstat tool, 286-288                     |
| complexity versus, 241                        | Bentley, Jon Louis                          |
| averages, percentiles versus, 226-229         | list of levels in software execution, 99    |
|                                               | on Pascal running time, 247                 |
|                                               | on primary concerns of programmer, 102      |
|                                               |                                             |

| on primary task of software engineers, 1       | CI (Continuous Integration) pipeline, noise  |
|------------------------------------------------|----------------------------------------------|
| on programmers' assessment of resource         | problems and, 264                            |
| consumption, 329                               | code coverage, 272                           |
| on test data choices, 252                      | code level optimization, 100                 |
| biases, in optimization, 102                   | Communicating Sequential Processes (CSP),    |
| Big O asymptotic complexity, 243-246           | 141                                          |
| "estimated" efficiency complexity versus,      | compilation (see Go compiler)                |
| 241                                            | compiler optimizations, microbenchmarks ver‐ |
| Big Theta, 245                                 | sus, 301-306                                 |
| binary file, 122                               | Completely Fair Scheduler (CFS), 136         |
| blameless culture, efficiency problems and, 95 | complexity analysis, 240-250                 |
| block starting symbol (.bss), 173              | asymptotic complexity with Big O notation,   |
| bottleneck analysis, 329-380                   | 243-246                                      |
| capturing the profiling signal, 355-360        | "estimated" efficiency complexity, 241-243   |
| comparing/aggregating profiles, 378            | practical applications, 246-250              |
| continuous profiling, 373-378                  | complexity, in RAER context, 88, 92          |
| in off-CPU time, 371                           | compressible resources, 262                  |
| profiling in Go, 331-355                       | concurrency                                  |
| (see also profiling)                           | advantages, 145                              |
| as root cause analysis for efficiency, 330     | CPU resource and, 145-146                    |
| sharing profiles, 373                          | disadvantages, 145                           |
| tips and tricks, 373-379                       | optimizing latency using, 402-411            |
| branch predictions, 131                        | containers                                   |
| Branczyk, Frederic                             | Go e2e framework and, 310-316                |
| on continuous profiling, 373                   | macrobenchmarking in, 311, 315               |
| bufio.Scanner, optimizing, 397-401             | versioning of images, 315                    |
| build errors due to unused import/variable, 52 | context switch, 130                          |
| Burks, Arthur W., on general-purpose comput‐   | Continuous Integration (CI) pipeline, noise  |
| ers, 113                                       | problems and, 264                            |
|                                                |                                              |
| byte (definition), 154                         | continuous profiling, 373-378                |
| bytes.Split, optimizing, 387-389               | Cox, Russ                                    |
|                                                | on generics, 63                              |
| C                                              | and Go team, 38                              |
| cache, hierarchical, 127                       | on sinks, 305                                |
| cardinality, 219                               | CPU overloading, 136                         |
| Carlton, Alexander, on performance bench‐      | CPU resource, 111-147                        |
| marks, 254                                     | Assembly language, 115-118                   |
| Carruth, Chandler                              | concurrency and, 145-146                     |
| on energy-efficient software, 24               | contiguous memory structure and, 131         |
| on time spent waiting for data, 127            | efficiency metrics semantics, 229-233        |
| CD Projekt, 30                                 | Go compiler and, 118-125                     |
| CFS (Completely Fair Scheduler), 136           | hierarchical cache system, 127               |
| channels, 141-143                              | Hyper-Threading and, 132-133                 |
| Cheney, Dave                                   | macrobenchmarking and, 321-322               |
| on goroutines, 427                             | memory wall problem, 126-133                 |
| on variables, 178                              | modern computer architecture and,            |
|                                                | 113-115                                      |

| on overloaded machine, 137                      | reacting to efficiency problems, 94-98           |
|-------------------------------------------------|--------------------------------------------------|
| pipelining and out-of-order CPU execution,      | speed versus, 32-34                              |
| 129-131                                         | understanding goals, 81-94                       |
| profiling CPU usage, 367-369                    | efficiency assessment, 239-273                   |
| profiling off-CPU time, 369-372                 | avoiding comparisons with older experi‐          |
| schedulers, 133-146                             | ment results, 265                                |
| Cramblitt, Bob, on repeatability, 253           | benchmarking, 250-256                            |
| Cyberpunk 2077 game, 30                         | benchmarking levels, 266-273                     |
|                                                 | complexity analysis, 240-250                     |
| D                                               | reliability of experiments, 256-266              |
| data-driven bottleneck analysis (see bottleneck | efficiency metrics semantics, 220-237            |
| analysis)                                       | CPU usage, 229-233                               |
| data-driven efficiency assessment (see effi‐    | latency, 221-229                                 |
| ciency assessment)                              | memory usage, 234-237                            |
| data-driven optimization level, 100             | efficiency observability (see observability)     |
| dead code elimination, 302                      | efficiency phase of TFBO, 106-109                |
| deliberate optimizations, 77                    | efficiency-aware development flow, 102-109       |
| Dennard, Robert H., on power efficiency of      | efficiency phase, 106-109                        |
| transistors, 22                                 | functionality phase, 104-106                     |
| Dennard's Rule, Moore's Law versus, 22          | emotions, in reaction to efficiency problems, 94 |
| dependencies, transparency of, 43-45            | energy consumption, execution speed and, 23      |
| development, efficiency-aware flow, 102-109     | Erdogmu, Hakan, on YAGNI, 14                     |
| Disassemble view, 354                           | error handling                                   |
| Docker containers, Go e2e framework and,        | Go's approach to, 47-51                          |
| 310-316                                         | importance of not ignoring, 50                   |
| documentation, as first citizen, 55-58          | wrapping errors, 50                              |
| dogfooding, 90                                  | errors due to unused import/variable, 52         |
| dynamic random-access memory (DRAM), 153        | "estimated" efficiency complexity, 241-243       |
|                                                 | experiment (definition), 251                     |
| E                                               |                                                  |
|                                                 | F                                                |
| e2e framework, 310-316                          | fat software, 20                                 |
| ecosystem, Go, 51                               | Favaro, John, on YAGNI, 14                       |
| efficiency (generally), 71-110                  | features, efficiency versus, 31                  |
| acquiring/assessing goals, 89                   | feedback loops, 267                              |
| common misconceptions about, 7-32               | file-based memory page, 169                      |
| (see also misconceptions about effi‐            | First Rule of Efficient Code, 144                |
| ciency)                                         | Flake, Halvar, on GC, 189                        |
| conquering, 71-110                              | Flame Graph view, 352-353                        |
| in context of performance, 5                    | Fowler, Susan J., on resources, 111              |
| defining/assessing requirements, 90-94          | FR (functional requirements) stage, 83-86        |
| efficiency-aware development flow, 102-109      | frames, 158                                      |
| features versus, 31                             | Full Go Profiler, 371                            |
| formalizing of requirements, 83-86              | function inlining, 121                           |
| importance of, 1-34                             | function stack, 174                              |
| key to pragmatic code performance, 32-34        | functional requirements (FR) stage, 83-86        |
| optimization and (see optimization)             |                                                  |
| performance definitions, 3-6                    |                                                  |

| functional testing, benchmarking versus,         | object-oriented programming, 59-63                                         |
|--------------------------------------------------|----------------------------------------------------------------------------|
| 252-254                                          | Go Allocator, 181-185                                                      |
| functionality phase of TFBO, 104-106             | internal Go runtime knowledge versus OS                                    |
|                                                  | knowledge, 184                                                             |
| G                                                | Go Assembly language                                                       |
| garbage collection (GC), 185-191                 | CPU time and, 115-118                                                      |
| heap management and, 185-191                     | machine code and, 117                                                      |
| memory inefficiency and, 152                     | Go benchmarks                                                              |
| recycling and, 423-426                           | average latency calculations, 201                                          |
| Geisendörfer, Felix, on original pprof tool, 332 | microbenchmarks, 277-284                                                   |
| general-purpose computers, 113                   | naming convention, 278                                                     |
| generic implementations, drawbacks of, 416       | running through IDE, 282                                                   |
| generics                                         | understanding results, 284-288                                             |
| about, 63-66                                     | go build command, 118-125                                                  |
| speed/efficiency issues, 66                      | Go compiler, 118-125                                                       |
| Go (generally)                                   | Go e2e framework, 310-316                                                  |
| advanced language elements, 55-66                | Go memory management, 172-191                                              |
| backward compatibility and portability, 58       | garbage collection, 185-191                                                |
| basics, 36-54                                    | Go Allocator, 181-185                                                      |
| code documentation as first citizen, 55-58       | Go Playground, 52                                                          |
| consistent tooling, 45                           | Go runtime scheduler, 138-145                                              |
| dependencies as transparent by default,          | Go slice, memory structure for, 178                                        |
| 43-45                                            | Go templates, 52                                                           |
| ecosystem, 51                                    | go tool pprof reports, 340-355                                             |
| error handling, 47-51                            | Disassemble view, 354                                                      |
| genealogy, 67                                    | Flame Graph view, 352-353                                                  |
| generics, 63-66                                  | function granularity flags, 345                                            |
| Go runtime, 58                                   | goroutines and, 346                                                        |
| Golang versus, 37                                | Graph view, 347-352                                                        |
| language: imperative, compiled, statically       | Peek view, 353                                                             |
| typed, 37                                        | Source view, 353                                                           |
| memory management, 172-191                       | Top report, 345-347                                                        |
| memory usage problems, 68                        | goals, understanding of, 81-94<br>acquiring/assessing efficiency goals, 89 |
| object-oriented programming, 59-63               | formalizing of efficiency requirements,                                    |
| open source/governed by Google, 39               | 83-86                                                                      |
| overview, 35-69                                  | Resource-Aware Efficiency Requirements,                                    |
| packaging and modules, 41                        | 86-89                                                                      |
| simplicity, safety, and readability, 40          | godoc tool, 55-58                                                          |
| speed issues, 67                                 | GOGC option, 186, 424                                                      |
| unit testing/table tests, 53                     | Golang                                                                     |
| unused import/variable as cause of build         | design to improve serious codebases, 37-39                                 |
| error, 52                                        | Go versus, 37                                                              |
| Go advanced features, 55-66                      | Goldstine, Herman H., on general-purpose                                   |
| backward compatibility and portability, 58       | computers, 113                                                             |
| code documentation as first citizen, 55-58       | GOMAXPROCS environmental variable, 144                                     |
| generics, 63-66                                  | GOMEMLIMIT option, 186, 424                                                |
| Go runtime, 58                                   |                                                                            |

| Google, Go governance and, 39                                                   | idiomatic coding style, 40                                              |
|---------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| goroutine                                                                       | ILP (Instruction-Level Parallelism), 129                                |
| common functions found in, 366                                                  | implementation (code) level of optimization                             |
| controlling lifecycle of, 427-434                                               | design, 100                                                             |
| Go runtime scheduler and, 138-145                                               | import statement, 52                                                    |
| goroutine profiler, 365-367                                                     | inclusiveness, efficiency and, 24                                       |
| granularity, 220, 224-226                                                       | inheritance, 60                                                         |
| Graph view, 347-352                                                             | inlining                                                                |
| Gregg, Brendan, on Flame Graph, 352                                             | function, 121                                                           |
| Griesemer, Robert                                                               | manual, 121                                                             |
| Algol 60 development, 67                                                        | Instruction Set Architecture (ISA), 118                                 |
| Go origins, 38, 40                                                              | Instruction-Level Parallelism (ILP), 129                                |
| Gryski, Damian, on GC and cost of memory                                        | instrumentation                                                         |
| allocation, 185                                                                 | common profile instrumentation, 360-372<br>forms of, 196                |
| H                                                                               | granularity-based classification, 197                                   |
| hardware                                                                        | hiding under abstractions, 210                                          |
| execution speed and energy efficiency, 23                                       | instrumentation (definition), 196                                       |
| misconceptions about increasing speed and                                       | Integrated Development Environment (IDE),                               |
| decreasing cost, 17-24                                                          | running Go benchmarks through, 282                                      |
| software speed versus hardware speed,                                           | internal packages, 43                                                   |
| 19-21                                                                           | Internet of Things (IoT), 21                                            |
| stability best practices, 264                                                   | ISA (Instruction Set Architecture), 118                                 |
| technological limits of speed, 22-23                                            |                                                                         |
| hardware level of optimization design, 101                                      | J                                                                       |
| heap                                                                            | Java, benchmarking in, 301                                              |
| Go Allocator and, 181-185                                                       | Jones, C., on thinking of metrics as distribu‐                          |
| Go memory management and, 173                                                   | tions, 227                                                              |
| optimizing usage, 174                                                           |                                                                         |
| profile, 360-364                                                                |                                                                         |
| runtime heap statistics, 234                                                    | K                                                                       |
| stack versus, 176                                                               | Kennedy, William                                                        |
| Hoare, C. A. R., on CSP paradigm, 141                                           | on context switching, 138                                               |
| Honnef, Dominik, on sync.Pool, 451                                              | on GC, 421                                                              |
| horizontal scalability, 26-29                                                   | on mechanical sympathy, 119                                             |
| House, Charles H., on time to market, 29                                        | Kernighan, Brian W.                                                     |
| Hsieh, Paul, on cost of optimization, 81                                        | on readability of code, 7                                               |
| human error, experiment reliability and,                                        | on true definition of efficiency, 2                                     |
| 256-258                                                                         | Kleppmann, Martin, on scalability, 25                                   |
| Hungarian Notation, 13                                                          | Knuth, Donald                                                           |
| Hyde, Randall, on premature optimization, 30                                    | complexity notations, 244                                               |
| Hyper-Threading, 132-133                                                        | on premature optimization, 13<br>Kubernetes with GOMEMLIMIT option, 424 |
| I                                                                               | L                                                                       |
| Icicle (Flame) Graph view, 352-353                                              | L-caches, 127                                                           |
| IDE (Integrated Development Environment),<br>running Go benchmarks through, 282 | latency                                                                 |

| difficulty of measuring shorter latencies, 223 | memory blocks, 178-181                     |
|------------------------------------------------|--------------------------------------------|
| efficiency metrics semantics, 221-229          | memory cells, 153                          |
| efficiency versus, 32-34                       | memory leak, 445-449                       |
| instrumenting for, 199-220                     | memory management                          |
| limitations of time/duration measurements,     | Go Allocator, 181-185                      |
| 223                                            | Go memory management, 172-191              |
| macrobenchmarking and, 318-320                 | microbenchmarks versus, 299-300            |
| napkin math calculations, 465                  | OS memory management, 156-171              |
| optimization, 383-394                          | values, pointers, and memory blocks,       |
| optimizing bytes.Split, 387-389                | 176-181                                    |
| optimizing runtime.slicebytetostring,          | Memory Management Unit (MMU), 159          |
| 389-391                                        | memory mapping, 168-171                    |
| optimizing strconv.Parse, 391-394              | memory overcommitment, 161                 |
| optimizing using concurrency, 402-411          | memory pooling, 451-459                    |
| percentiles versus averages, 226-229           | memory resource, 149-191                   |
| in RAER, 90                                    | efficiency metrics semantics, 234-237      |
| latency optimization                           | Go memory management, 172-191              |
| naive concurrency, 402-404                     | Go's use of, 149-191                       |
| streamed, sharded worker approach,             | identifying problems with, 152             |
| 408-411                                        | macrobenchmarking and, 322-324             |
| using concurrency, 402-411                     | moving to streaming algorithm, 395-397     |
| worker approach with distribution, 404-406     | optimization examples, 395-401             |
| worker approach without coordination,          | optimizing bufio.Scanner, 397-401          |
| 406-408                                        | OS memory management, 156-171              |
| leak (see resource leaks)                      | OS memory mapping, 168-171                 |
| lined lists, arrays versus, 131                | OS memory pages statistics, 236            |
| logger pattern, 202                            | overusing with arrays, 445-449             |
| logging, 199-205                               | physical, 153-156                          |
| Lozi, J. P., on OS thread scheduler, 134       | relevance of, 150-152                      |
|                                                | runtime heap statistics, 234               |
| M                                              | virtual memory, 158-168                    |
| machine code, 116                              | waste indications, 249                     |
| macrobenchmarks/macrobenchmarking              | when to debug/optimize, 152                |
| about, 269                                     | memory reuse, 449-459                      |
| basics, 307-310                                | memory wall, 126-133                       |
| common workflows, 325-327                      | CPU resource and, 126-133                  |
| containers for, 311                            | hierarchical cache system, 127             |
| CPU time and, 321-322                          | Hyper-Threading, 132-133                   |
| Go e2e framework, 310-316                      | pipelining and out-of-order CPU execution, |
| implementation, 306-325                        | 129-131                                    |
| memory and, 322-324                            | methods, Go, 61                            |
| server-side latency, 318-320                   | metrics, 211-220                           |
| understanding results/observations, 316        | cardinality, 219                           |
| mapping, OS memory, 168-171                    | definition, 211                            |
| measuring (definition), 239                    | documentation of, 226                      |
| mechanical sympathy, 112                       | efficiency metrics semantics, 220-237      |
| Bill Kennedy on, 119                           |                                            |
|                                                |                                            |

| numeric value versus metric observability     | monitoring versus, 195                        |
|-----------------------------------------------|-----------------------------------------------|
| signal, 220                                   | tracing, 205-211                              |
| Meyers, Scott, on optimization, 76            | off-CPU time                                  |
| microbenchmarks/microbenchmarking,            | bottleneck analysis in, 371                   |
| 270-271                                       | profiling, 369-372                            |
| compiler optimizations versus, 301-306        | on demand paging, 167                         |
| finding your workflow, 289-290                | OOM (out-of-memory), 167                      |
| implementation, 275-288                       | OOP (object-oriented programming), 59-63      |
| memory management versus, 299-300             | open source versus Go, 39                     |
| running for different inputs, 297-299         | operating system (OS) memory management,      |
| sharing with team, 294-297                    | 156-171                                       |
| testing for correctness, 290-293              | goals for, 156-158                            |
| tips and tricks for, 284-288                  | memory pages statistics, 236                  |
| too-high variance, 288                        | mmap syscall, 161-162                         |
| understanding results, 284-288                | OS memory mapping, 168-171                    |
| misconceptions about efficiency, 7-32         | virtual memory, 158-168                       |
| hardware speed/cost, 17-24                    | operating system (OS) optimization level, 100 |
| horizontal versus vertical scaling, 25-29     | operating system (OS) schedulers, 134-138     |
| time to market versus features, 29-32         | optimization                                  |
| unreadability of optimized code, 7-14         | acquiring/assessing efficiency goals, 89      |
| YAGNI rule, 14-17                             | computer science definition, 73               |
| mmap syscall, 161-162                         | deliberate, 77                                |
| MMU (Memory Management Unit), 159             | design levels, 98-102                         |
| modules, Go source code and, 41               | engineering definition, 73                    |
| monitoring, observability versus, 195         | examples (see optimization examples)          |
| Moore, Gordon, on IC component costs, 22      | formalizing of efficiency requirements,       |
| Moore's Law, 22                               | 83-86                                         |
|                                               | fundamental problems/challenges, 79-80        |
| N                                             | general definition, 73                        |
|                                               | guarding against biases, 102                  |
| napkin math, 92, 465                          | patterns (see optimization patterns)          |
| noise (performance nondeterminism), 260-266   | reasonable, 74-76                             |
| non-functional requirement (NFR) documen‐     | Resource-Aware Efficiency Requirements,       |
| tation, 84                                    | 86-89                                         |
| noncompressible resources, 262                | stakeholders and, 81                          |
| nondeterministic performance (noise), 260-266 | understanding goals, 81-94                    |
|                                               | as zero-sum game, 73-78                       |
| O                                             | optimization examples, 381-413                |
| object-oriented programming (OOP), 59-63      | alternative methods, 411                      |
| observability, 193-238                        | latency optimization, 383-394                 |
| basics, 194-198                               | moving to streaming algorithm, 395-397        |
| definition, 195                               | optimizing bufio.Scanner, 397-401             |
| efficiency metrics semantics, 220-237         | optimizing bytes.Split, 387-389               |
| instrumenting for latency, 199-220            | optimizing latency using concurrency,         |
| internal Go runtime knowledge versus OS       | 402-411                                       |
| knowledge, 184                                | optimizing memory usage, 395-401              |
| logging, 199-205                              |                                               |
| metrics, 211-220                              |                                               |

| optimizing runtime.slicebytetostring,            | on dependencies, 45                            |
|--------------------------------------------------|------------------------------------------------|
| 389-391                                          | on Go, 35                                      |
| optimizing strconv.Parse, 391-394                | on Go origins, 37                              |
| Sum examples, 382-383                            | pipelining, out-of-order CPU execution and,    |
| optimization patterns, 415-459                   | 129-131                                        |
| avoiding resource leak, 426-440                  | Plauger, P. J.                                 |
| avoiding unnecessary work, 416-418               | on readability of code, 7                      |
| common patterns, 416-421                         | on true definition of efficiency, 2            |
| memory reuse/pooling, 449-459                    | pointer receiver, 61                           |
| overusing memory with arrays, 445-449            | pointers, 178-179                              |
| pre-allocation, 440-445                          | power consumption, 23                          |
| three Rs method, 421-426                         | pprof format, 332-340                          |
| trading functionality for efficiency, 419        | (see also profiling)                           |
| trading space for time, 419                      | go tool pprof reports, 340-355                 |
| trading time for space, 420                      | Profile child objects, 337-339                 |
| optimized code (see readability/unreadability of | pre-allocation, 440-445                        |
| optimized code)                                  | premature optimization, 76                     |
| OS (see operating system entries)                | premature pessimization, 8                     |
| out-of-memory (OOM), 167                         | Price, Raymond L., on time to market, 29       |
| out-of-order CPU execution, 129-131              | Process Identification Number (PID), 134       |
| overcommitment, 161                              | production                                     |
| overloading, 136                                 | benchmarking in, 268                           |
|                                                  | reproducing in experiments, 258-260            |
| P                                                | profiler (definition), 332                     |
| packages                                         | profiling, 331-355                             |
| Go source code and, 41                           | capturing the profiling signal, 355-360        |
| internal directory and, 43                       | common profile instrumentation, 360-372        |
| padding, 179                                     | comparing/aggregating profiles, 378            |
| page fault, 167                                  | continuous, 373-378                            |
| page size, importance of, 159                    | CPU usage, 367-369                             |
| pages, 158                                       | go tool pprof reports, 340-355                 |
| paging, 158, 236                                 | goroutine profiler, 365-367                    |
| panics (exception mechanism), 48                 | heap profile, 360-364                          |
| parametric polymorphism (generics), 63-66        | off-CPU time, 369-372                          |
| Parca project, 374-378                           | pprof format, 332-340                          |
| Parkinson's Law, 19                              | sharing profiles, 373                          |
| Peek view, 353                                   | Prometheus                                     |
| percentiles, averages versus, 226-229            | benchmarking suites, 271                       |
| performance                                      | gauge metric problems, 323                     |
| basics, 3-6                                      | metric instrumentation, 231-233                |
| need to specify meaning, 4                       | pre-aggregated instrumentation, 211-218        |
| three core execution elements, 5                 | rate duration, 319                             |
| performance nondeterminism (noise), 260-266      | psychological safety, efficiency problems and, |
| pessimization, 8                                 | 94                                             |
| physical memory, 153-156                         | pull-based collection model, 198               |
| PID (Process Identification Number), 134         | push-based collection model, 198               |
| Pike, Rob                                        |                                                |

| R                                                                | sharding                                        |
|------------------------------------------------------------------|-------------------------------------------------|
| RAER (see Resource-Aware Efficiency Require‐<br>ments)           | streamed, sharded worker approach,<br>408-411   |
| random-access memory (RAM), 153-156                              | worker approach without coordination,           |
|                                                                  | 406-408                                         |
| readability/unreadability of optimized code                      | shared infrastructure, 264                      |
| code after optimization as more readable,                        | Simonov, Valentin, on hardware speed, 17        |
| 9-13                                                             | simultaneous multithreading (SMT), 132-133      |
| misconceptions about, 7-14                                       | Single Instruction Multiple Data (SIMD), 126    |
| now versus past, 13                                              | Single Instruction Single Data (SISD), 126      |
| readability as dynamic, 13                                       | Sink pattern, 304-305                           |
| waste reduction versus readability reduc‐                        | Site Reliability Engineering (SRE), 85          |
| tion, 76                                                         | slice, memory structure for, 178                |
| reasonable optimizations, 74-76                                  | SMT (simultaneous multithreading), 132-133      |
| reliability of experiments                                       | software speed, hardware speed versus, 19-21    |
| human error and, 256-258                                         | Source view, 353                                |
| performance nondeterminism (noise),                              | speculative execution, 131                      |
| 260-266                                                          | speed                                           |
| reproducing production, 258-260                                  | in context of performance, 5                    |
| repeatability (definition), 253                                  | efficiency versus, 32-34                        |
| resource leaks, avoiding, 426-440                                | Go (generally), 67                              |
| closing objects, 435-438                                         | software versus hardware, 19-21                 |
| controlling goroutine lifecycle, 427-434                         | SRAM (static random-access memory), 127         |
| definition, 426                                                  | Sridharan, Cindy, on observability signals, 195 |
| exhausting things, 438-440                                       | stack (function stack), 174                     |
| Resource-Aware Efficiency Requirements                           | stakeholders, optimization requests from, 81    |
| (RAER)                                                           | static random-access memory (SRAM), 127         |
| about, 86-89                                                     | statistics, risks in overusing, 263             |
| defining/assessment example, 90-94                               | strconv.Parse, 391-394                          |
| EADF and, 107                                                    | streaming algorithm, moving to, 395-397         |
| resources, compressible versus noncompressi‐                     | structure padding, 179                          |
| ble, 262                                                         | structures, as class equivalent, 60             |
| runtime heap statistics, 234                                     | Sutter, H.                                      |
| runtime scheduler, 138-145<br>runtime.slicebytetostring, 389-391 | on efficient design, 8                          |
|                                                                  | on speed versus correctness, 104                |
|                                                                  | sync.Pool structure, 451                        |
| S                                                                | system level of optimization design, 99         |
| scalability                                                      |                                                 |
| horizontal, 26-29                                                | T                                               |
| misconceptions about efficiency, 25-29                           |                                                 |
| vertical, 26                                                     | table tests, 53                                 |
| schedulers, 133-145                                              | Taylor, Ian, and Go team, 38                    |
| Go runtime scheduler, 138-145                                    | team, sharing microbenchmarks with, 294-297     |
| operating system schedulers, 134-138                             | test-driven development (TDD), 104              |
| script (using Go code), 39                                       | testing                                         |
| semantic diffusion, 4                                            | microbenchmarks, 290-293                        |
| server-side latency, macrobenchmarking and,<br>318-320           | unit testing/table tests, 53                    |

| TFBO (test, fix, benchmark, optimize) develop‐ | V                                      |
|------------------------------------------------|----------------------------------------|
| ment flow, 103-109                             | value receiver, 61                     |
| Thanos project, 27                             | values, 177-181                        |
| thermal scaling, as source of noise, 263       | variables                              |
| Thompson, Ken, and Go origins, 38              | build errors from unused variable, 52  |
| three Rs optimization method, 421-426          | heap versus stack allocation, 176      |
| recycling, 423-426                             | variance, microbenchmarking and, 288   |
| reducing allocations, 421                      | vertical scalability, 26               |
| reusing memory, 422                            | virtual memory, 158-162                |
| time to market (financial impact), 29-32       | Vitess project, 272                    |
| TLB (Translation Lookaside Buffer), 159        | von Neumann, John, and general-purpose |
| tooling, consistency of, 45                    | computers, 113                         |
| tracing                                        |                                        |
| basics, 205-211                                |                                        |
| downsides of, 209-211                          | W                                      |
| Translation Lookaside Buffer (TLB), 159        | waste, 74-76                           |
| types, embedding multiple, 61                  | Wirth, Niklaus                         |
|                                                | on fat software, 20                    |
| U                                              | and Go origins, 38                     |
|                                                | workflow, microbenchmarking, 289-290   |
| unit testing, 53                               |                                        |
| unreadability of optimized code (see readabil‐ |                                        |

ity/unreadability of optimized code)
