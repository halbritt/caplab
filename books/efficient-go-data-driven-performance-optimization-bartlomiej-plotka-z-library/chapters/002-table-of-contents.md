# Table of Contents

|    | Preface ix                                          |    |
|----|-----------------------------------------------------|----|
| 1. | Software Efficiency Matters 1                       |    |
|    | Behind Performance                                  | 3  |
|    | Common Efficiency Misconceptions                    | 7  |
|    | Optimized Code Is Not Readable                      | 7  |
|    | You Aren't Going to Need It                         | 14 |
|    | Hardware Is Getting Faster and Cheaper              | 17 |
|    | We Can Scale Horizontally Instead                   | 25 |
|    | Time to Market Is More Important                    | 29 |
|    | The Key to Pragmatic Code Performance               | 32 |
|    | Summary                                             | 34 |
| 2. | Efficient Introduction to Go 35                     |    |
|    | Basics You Should Know About Go                     | 36 |
|    | Imperative, Compiled, and Statically Typed Language | 37 |
|    | Designed to Improve Serious Codebases               | 37 |
|    | Governed by Google, Yet Open Source                 | 39 |
|    | Simplicity, Safety, and Readability Are Paramount   | 40 |
|    | Packaging and Modules                               | 41 |
|    | Dependencies Transparency by Default                | 43 |
|    | Consistent Tooling                                  | 45 |
|    | Single Way of Handling Errors                       | 47 |
|    | Strong Ecosystem                                    | 51 |
|    | Unused Import or Variable Causes Build Error        | 52 |
|    | Unit Testing and Table Tests                        | 53 |
|    | Advanced Language Elements                          | 55 |
|    | Code Documentation as a First Citizen               | 55 |

|    | Backward Compatibility and Portability        | 58  |
|----|-----------------------------------------------|-----|
|    | Go Runtime                                    | 58  |
|    | Object-Oriented Programming                   | 59  |
|    | Generics                                      | 63  |
|    | Is Go "Fast"?                                 | 67  |
|    | Summary                                       | 69  |
| 3. | Conquering Efficiency 71                      |     |
|    | Beyond Waste, Optimization Is a Zero-Sum Game | 73  |
|    | Reasonable Optimizations                      | 74  |
|    | Deliberate Optimizations                      | 77  |
|    | Optimization Challenges                       | 79  |
|    | Understand Your Goals                         | 80  |
|    | Efficiency Requirements Should Be Formalized  | 83  |
|    | Resource-Aware Efficiency Requirements        | 86  |
|    | Acquiring and Assessing Efficiency Goals      | 89  |
|    | Example of Defining RAER                      | 90  |
|    | Got an Efficiency Problem? Keep Calm!         | 94  |
|    | Optimization Design Levels                    | 98  |
|    | Efficiency-Aware Development Flow             | 102 |
|    | Functionality Phase                           | 104 |
|    | Efficiency Phase                              | 106 |
|    | Summary                                       | 109 |
| 4. | How Go Uses the CPU Resource (or Two)         | 111 |
|    | CPU in a Modern Computer Architecture         | 113 |
|    | Assembly                                      | 115 |
|    | Understanding Go Compiler                     | 118 |
|    | CPU and Memory Wall Problem                   | 126 |
|    | Hierachical Cache System                      | 127 |
|    | Pipelining and Out-of-Order Execution         | 129 |
|    | Hyper-Threading                               | 132 |
|    | Schedulers                                    | 133 |
|    | Operating System Scheduler                    | 134 |
|    | Go Runtime Scheduler                          | 138 |
|    | When to Use Concurrency                       | 145 |
|    | Summary                                       | 146 |
| 5. | How Go Uses Memory Resource 149               |     |
|    | Memory Relevance                              | 150 |
|    | Do We Have a Memory Problem?                  | 152 |
|    | Physical Memory                               | 153 |

|    | OS Memory Management                      | 156        |
|----|-------------------------------------------|------------|
|    | Virtual Memory                            | 158        |
|    | mmap Syscall                              | 162        |
|    | OS Memory Mapping                         | 168        |
|    | Go Memory Management                      | 172        |
|    | Values, Pointers, and Memory Blocks       | 176        |
|    | Go Allocator                              | 181        |
|    | Garbage Collection                        | 185        |
|    | Summary                                   | 191        |
| 6. | Efficiency Observability                  | 193        |
|    | Observability                             | 194        |
|    | Example: Instrumenting for Latency        | 199        |
|    | Logging                                   | 199        |
|    | Tracing                                   | 205        |
|    | Metrics                                   | 211        |
|    | Efficiency Metrics Semantics              | 220        |
|    | Latency                                   | 221        |
|    | CPU Usage                                 | 229        |
|    | Memory Usage                              | 234        |
|    | Summary                                   | 238        |
| 7. | Data-Driven Efficiency Assessment 239     |            |
|    | Complexity Analysis                       | 240        |
|    | "Estimated" Efficiency Complexity         | 241        |
|    | Asymptotic Complexity with Big O Notation | 243        |
|    | Practical Applications                    | 246        |
|    | The Art of Benchmarking                   | 250        |
|    | Comparison to Functional Testing          | 252        |
|    | Benchmarks Lie                            | 254        |
|    | Reliability of Experiments                | 256        |
|    | Human Errors                              | 256        |
|    | Reproducing Production                    | 258        |
|    | Performance Nondeterminism                | 260        |
|    | Benchmarking Levels                       | 266        |
|    | Benchmarking in Production                | 268        |
|    | Macrobenchmarks                           | 269        |
|    | Microbenchmarks                           | 270        |
|    | What Level Should You Use?                | 271<br>273 |
|    | Summary                                   |            |

| 8.  | Benchmarking 275                                        |     |
|-----|---------------------------------------------------------|-----|
|     | Microbenchmarks                                         | 275 |
|     | Go Benchmarks                                           | 277 |
|     | Understanding the Results                               | 284 |
|     | Tips and Tricks for Microbenchmarking                   | 288 |
|     | Too-High Variance                                       | 288 |
|     | Find Your Workflow                                      | 289 |
|     | Test Your Benchmark for Correctness!                    | 290 |
|     | Sharing Benchmarks with the Team (and Your Future Self) | 294 |
|     | Running Benchmarks for Different Inputs                 | 297 |
|     | Microbenchmarks Versus Memory Management                | 299 |
|     | Compiler Optimizations Versus Benchmark                 | 301 |
|     | Macrobenchmarks                                         | 306 |
|     | Basics                                                  | 307 |
|     | Go e2e Framework                                        | 310 |
|     | Understanding Results and Observations                  | 316 |
|     | Common Macrobenchmarking Workflows                      | 325 |
|     | Summary                                                 | 327 |
| 9.  | Data-Driven Bottleneck Analysis 329                     |     |
|     | Root Cause Analysis, but for Efficiency                 | 330 |
|     | Profiling in Go                                         | 331 |
|     | pprof Format                                            | 332 |
|     | go tool pprof Reports                                   | 340 |
|     | Capturing the Profiling Signal                          | 355 |
|     | Common Profile Instrumentation                          | 360 |
|     | Heap                                                    | 360 |
|     | Goroutine                                               | 365 |
|     | CPU                                                     | 367 |
|     | Off-CPU Time                                            | 369 |
|     | Tips and Tricks                                         | 373 |
|     | Sharing Profiles                                        | 373 |
|     | Continuous Profiling                                    | 373 |
|     | Comparing and Aggregating Profiles                      | 378 |
|     | Summary                                                 | 379 |
| 10. | Optimization Examples 381                               |     |
|     | Sum Examples                                            | 382 |
|     | Optimizing Latency                                      | 383 |
|     | Optimizing bytes.Split                                  | 387 |
|     | Optimizing runtime.slicebytetostring                    | 389 |
|     | Optimizing strconv.Parse                                | 391 |

|     | Index 467                                                      |            |
|-----|----------------------------------------------------------------|------------|
| A.  | Latencies for Napkin Math Calculations 465                     |            |
|     | Next Steps                                                     | 461        |
|     | Summary                                                        | 459        |
|     | Memory Reuse and Pooling                                       | 449        |
|     | Overusing Memory with Arrays                                   | 445        |
|     | Pre-Allocate If You Can                                        | 440        |
|     | Exhaust Things                                                 | 438        |
|     | Reliably Close Things                                          | 435        |
|     | Control the Lifecycle of Your Goroutines                       | 427        |
|     | Don't Leak Resources                                           | 426        |
|     | Recycle                                                        | 423        |
|     | Reuse Memory                                                   | 422        |
|     | Reduce Allocations                                             | 421        |
|     | The Three Rs Optimization Method                               | 421        |
|     | Trading Time for Space                                         | 420        |
|     | Trading Functionality for Efficiency<br>Trading Space for Time | 419<br>419 |
|     | Do Less Work                                                   | 416        |
|     | Common Patterns                                                | 416        |
| 11. | Optimization Patterns                                          | 415        |
|     |                                                                |            |
|     | Summary                                                        | 413        |
|     | Bonus: Thinking Out of the Box                                 | 411        |
|     | A Streamed, Sharded Worker Approach                            | 408        |
|     | A Worker Approach Without Coordination (Sharding)              | 406        |
|     | A Worker Approach with Distribution                            | 404        |
|     | A Naive Concurrency                                            | 402        |
|     | Optimizing Latency Using Concurrency                           | 402        |
|     | Optimizing bufio.Scanner                                       | 397        |
|     | Moving to Streaming Algorithm                                  | 395        |
|     | Optimizing Memory Usage                                        | 395        |
