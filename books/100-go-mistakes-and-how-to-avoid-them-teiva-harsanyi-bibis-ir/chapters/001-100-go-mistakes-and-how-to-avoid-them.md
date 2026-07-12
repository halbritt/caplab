![](../assets/_page_0_Figure_0.jpeg)

Teiva Harsanyi

![](../assets/_page_0_Picture_2.jpeg)

![](../assets/_page_1_Picture_0.jpeg)

# 100 Go Mistakes and How to Avoid Them


TEIVA HARSANYI

![](../assets/_page_4_Picture_2.jpeg)

For online information and ordering of this and other Manning books, please visit www.manning.com. The publisher offers discounts on this book when ordered in quantity. For more information, please contact

Special Sales Department Manning Publications Co. 20 Baldwin Road PO Box 761 Shelter Island, NY 11964 Email: orders@manning.com

©2022 by Manning Publications Co. All rights reserved.

No part of this publication may be reproduced, stored in a retrieval system, or transmitted, in any form or by means electronic, mechanical, photocopying, or otherwise, without prior written permission of the publisher.

Many of the designations used by manufacturers and sellers to distinguish their products are claimed as trademarks. Where those designations appear in the book, and Manning Publications was aware of a trademark claim, the designations have been printed in initial caps or all caps.

Recognizing the importance of preserving what has been written, it is Manning's policy to have the books we publish printed on acid-free paper, and we exert our best efforts to that end. Recognizing also our responsibility to conserve the resources of our planet, Manning books are printed on paper that is at least 15 percent recycled and processed without the use of elemental chlorine.

The author and publisher have made every effort to ensure that the information in this book was correct at press time. The author and publisher do not assume and hereby disclaim any liability to any party for any loss, damage, or disruption caused by errors or omissions, whether such errors or omissions result from negligence, accident, or any other cause, or from any usage of the information herein.

Manning Publications Co. 20 Baldwin Road PO Box 761 Shelter Island, NY 11964 Development editor: Doug Rudder
Technical development editor: Arthur Zubarev
Review editor: Mihaela Batinić
Production editor: Deirdre S. Hiam
Copyeditors: Frances Buran and

Tiffany Taylor

Proofreader: Katie Tennant
Technical proofreader: Tim van Deurzen
Typesetter and cover designer: Marija Tudor

ISBN 9781617299599 Printed in the United States of America To Davy Harsanyi: Keep being the person you are, little brother; the stars are your limit.

À Mélissa, ma puce.

### contents

preface xii
acknowledgments xiii
about this book xiv
about the author xvii
about the cover illustration xviii

### [ Go: Simple to learn but hard to master 1

- 1.1 Go outline 2
- 1.2 Simple doesn't mean easy 3
- 1.3 100 Go mistakes 4

Bugs 4 • Needless complexity 5 • Weaker readability 5 Suboptimal or unidiomatic organization 5 • Lack of API convenience 6 • Under-optimized code 6 • Lack of productivity 6

### Code and project organization

- 2.1 #1: Unintended variable shadowing 7
- 2.2 #2: Unnecessary nested code 9
- 2.3 #3: Misusing init functions 12Concepts 12 When to use init functions 15
- 2.4 #4: Overusing getters and setters 17
- 2.5 #5: Interface pollution 18

Concepts 18 • When to use interfaces 21 • Interface pollution 24

CONTENTS vii

| 2.6  | #6: Interface on the producer side 25                                                                                                                             |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.7  | #7: Returning interfaces 27                                                                                                                                       |
| 2.8  | #8: any says nothing 28                                                                                                                                           |
| 2.9  | #9: Being confused about when to use generics 31                                                                                                                  |
|      | Concepts 31 • Common uses and misuses 34                                                                                                                          |
| 2.10 | #10: Not being aware of the possible problems with type embedding 36                                                                                              |
| 2.11 | #11: Not using the functional options pattern 40                                                                                                                  |
|      | Config struct 41 • Builder pattern 42 • Functional options pattern 44                                                                                             |
| 2.12 | #12: Project misorganization 46                                                                                                                                   |
|      | Project structure 46 • Package organization 47                                                                                                                    |
| 2.13 | #13: Creating utility packages 48                                                                                                                                 |
| 2.14 | #14: Ignoring package name collisions 50                                                                                                                          |
| 2.15 | #15: Missing code documentation 51                                                                                                                                |
| 2.16 | #16: Not using linters 53                                                                                                                                         |
| Data | types 56                                                                                                                                                          |
| 3.1  | #17: Creating confusion with octal literals 56                                                                                                                    |
| 3.2  | #18: Neglecting integer overflows 57                                                                                                                              |
|      | Concepts 58 Detecting integer overflow when incrementing 59 Detecting integer overflows during addition 60 Detecting an integer overflow during multiplication 60 |
| 3.3  | #19: Not understanding floating points 61                                                                                                                         |
| 3.4  | #20: Not understanding slice length and capacity 64                                                                                                               |
| 3.5  | #21: Inefficient slice initialization 68                                                                                                                          |
| 3.6  | #22: Being confused about nil vs. empty slices 71                                                                                                                 |
| 3.7  | #23: Not properly checking if a slice is empty 74                                                                                                                 |
| 3.8  | #24: Not making slice copies correctly 76                                                                                                                         |
| 3.9  | #25: Unexpected side effects using slice append 77                                                                                                                |
| 3.10 | #26: Slices and memory leaks 80                                                                                                                                   |
|      | Leaking capacity 80 • Slice and pointers 81                                                                                                                       |
| 3.11 | #27: Inefficient map initialization 84                                                                                                                            |
|      | Concepts 84 • Initialization 86                                                                                                                                   |

viii CONTENTS

|   | 3.12   | #28: Maps and memory leaks 87                                         |
|---|--------|-----------------------------------------------------------------------|
|   | 3.13   | #29: Comparing values incorrectly 90                                  |
| 4 | Contr  | ol structures 95                                                      |
|   | 4.1    | #30: Ignoring the fact that elements are copied in range loops 95     |
|   |        | Concepts 96 • Value copy 96                                           |
|   | 4.2    | #31: Ignoring how arguments are evaluated in range loops 98           |
|   |        | Channels 100 • Array 100                                              |
|   | 4.3    | #32: Ignoring the impact of using pointer elements in range loops 102 |
|   | 4.4    | #33: Making wrong assumptions during map iterations 105               |
|   |        | Ordering 105 • Map insert during iteration 107                        |
|   | 4.5    | #34: Ignoring how the break statement works 108                       |
|   | 4.6    | #35: Using defer inside a loop 110                                    |
| 5 | String | rs 113                                                                |
|   | 5.1    | #36: Not understanding the concept of a rune 114                      |
|   | 5.2    | #37: Inaccurate string iteration 115                                  |
|   | 5.3    | #38: Misusing trim functions 118                                      |
|   | 5.4    | #39: Under-optimized string concatenation 119                         |
|   | 5.5    | #40: Useless string conversions 121                                   |
|   | 5.6    | #41: Substrings and memory leaks 123                                  |
| 6 | Funct  | ions and methods 126                                                  |
|   | 6.1    | #42: Not knowing which type of receiver to use 127                    |
|   | 6.2    | #43: Never using named result parameters 129                          |
|   | 6.3    | #44: Unintended side effects with named result parameters 132         |
|   | 6.4    | #45: Returning a nil receiver 133                                     |
|   | 6.5    | #46: Using a filename as a function input 136                         |
|   | 6.6    | #47: Ignoring how defer arguments and receivers are evaluated 138     |
|   |        | Argument evaluation 138 • Pointer and value receivers 141             |

CONTENTS ix

| 7 | Error | management 143                                                                                     |
|---|-------|----------------------------------------------------------------------------------------------------|
|   | 7.1   | #48: Panicking 143                                                                                 |
|   | 7.2   | #49: Ignoring when to wrap an error 146                                                            |
|   | 7.3   | #50: Checking an error type inaccurately 149                                                       |
|   | 7.4   | #51: Checking an error value inaccurately 152                                                      |
|   | 7.5   | #52: Handling an error twice 154                                                                   |
|   | 7.6   | #53: Not handling an error 156                                                                     |
|   | 7.7   | #54: Not handling defer errors 158                                                                 |
| 8 | Conci | urrency: Foundations 162                                                                           |
|   | 8.1   | #55: Mixing up concurrency and parallelism 163                                                     |
|   | 8.2   | #56: Thinking concurrency is always faster 166                                                     |
|   |       | Go scheduling 166 • Parallel merge sort 169                                                        |
|   | 8.3   | #57: Being puzzled about when to use channels or mutexes 173                                       |
|   | 8.4   | #58: Not understanding race problems 174                                                           |
|   |       | Data races vs. race conditions 174 • The Go memory model 179                                       |
|   | 8.5   | #59: Not understanding the concurrency impacts of a workload type 181                              |
|   | 8.6   | #60: Misunderstanding Go contexts 186                                                              |
|   |       | Deadline 186 • Cancellation signals 187 • Context values 188 • Catching a context cancellation 190 |
| 9 | Conci | urrency: Practice 193                                                                              |
|   | 9.1   | #61: Propagating an inappropriate context 193                                                      |
|   | 9.2   | #62: Starting a goroutine without knowing when to stop it 196                                      |
|   | 9.3   | #63: Not being careful with goroutines and loop variables 198                                      |
|   | 9.4   | #64: Expecting deterministic behavior using select and channels 200                                |
|   | 9.5   | #65: Not using notification channels 204                                                           |
|   | 9.6   | #66: Not using nil channels 205                                                                    |
|   | 9.7   | #67: Being puzzled about channel size 211                                                          |
|   | 9.8   | #68: Forgetting about possible side effects with string formatting 213                             |
|   |       | etcd data race 213 • Deadlock 214                                                                  |
|   |       |                                                                                                    |

X CONTENTS

11

| 9.9    | #69: Creating data races with append 216                                                                                                                                                                                                  |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 9.10   | #70: Using mutexes inaccurately with slices and maps 218                                                                                                                                                                                  |
| 9.11   | #71: Misusing sync.WaitGroup 221                                                                                                                                                                                                          |
| 9.12   | #72: Forgetting about sync.Cond 223                                                                                                                                                                                                       |
| 9.13   | #73: Not using errgroup 228                                                                                                                                                                                                               |
| 9.14   | #74: Copying a sync type 231                                                                                                                                                                                                              |
| The s  | tandard library 234                                                                                                                                                                                                                       |
| 10.1   | #75: Providing a wrong time duration 235                                                                                                                                                                                                  |
| 10.2   | #76: time.After and memory leaks 235                                                                                                                                                                                                      |
| 10.3   | #77: Common JSON-handling mistakes 238                                                                                                                                                                                                    |
|        | Unexpected behavior due to type embedding 238 • JSON and the monotonic clock 240 • Map of any 243                                                                                                                                         |
| 10.4   | #78: Common SQL mistakes 244                                                                                                                                                                                                              |
|        | Forgetting that sql. Open doesn't necessarily establish connections to a database 244 • Forgetting about connections pooling 245  Not using prepared statements 246 • Mishandling null values 247 • Not handling row iteration errors 248 |
| 10.5   | #79: Not closing transient resources 249                                                                                                                                                                                                  |
|        | HTTP body 250 • sql.Rows 252 • os.File 253                                                                                                                                                                                                |
| 10.6   | #80: Forgetting the return statement after replying to an                                                                                                                                                                                 |
|        | HTTP request 255                                                                                                                                                                                                                          |
| 10.7   | #81: Using the default HTTP client and server 256                                                                                                                                                                                         |
|        | HTTP client 256 • HTTP server 259                                                                                                                                                                                                         |
| Testin | g 262                                                                                                                                                                                                                                     |
| 11.1   | #82: Not categorizing tests 262                                                                                                                                                                                                           |
|        | Build tags 263 • Environment variables 264<br>Short mode 265                                                                                                                                                                              |
| 11.2   | #83: Not enabling the -race flag 266                                                                                                                                                                                                      |
| 11.3   | #84: Not using test execution modes 268                                                                                                                                                                                                   |
|        | The parallel flag 269 • The -shuffle flag 270                                                                                                                                                                                             |
| 11.4   | #85: Not using table-driven tests 271                                                                                                                                                                                                     |
| 11.5   | #86: Sleeping in unit tests 274                                                                                                                                                                                                           |
| 11.6   | #87: Not dealing with the time API efficiently 278                                                                                                                                                                                        |

CONTENTS xi

| 11.7          | #88: Not using testing utility packages 281                                                                                                                                                 |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 11.0          | The httptest package 281 • The iotest package 283                                                                                                                                           |
| 11.8          | #89: Writing inaccurate benchmarks 285                                                                                                                                                      |
|               | Not resetting or pausing the timer 286 • Making wrong assumptions about micro-benchmarks 287 • Not being careful about compiler optimizations 289 • Being fooled by the observer effect 291 |
| 11.9          | #90: Not exploring all the Go testing features 294                                                                                                                                          |
|               | Code coverage 294 • Testing from a different package 295<br>Utility functions 295 • Setup and teardown 296                                                                                  |
| <b>O</b> ptim | nizations 299                                                                                                                                                                               |
| 12.1          | #91: Not understanding CPU caches 300                                                                                                                                                       |
|               | CPU architecture 300 • Cache line 301 • Slice of structs vs.<br>struct of slices 304 • Predictability 305 • Cache placement<br>policy 307                                                   |
| 12.2          | #92: Writing concurrent code that leads to false sharing 312                                                                                                                                |
| 12.3          | #93: Not taking into account instruction-level parallelism 315                                                                                                                              |
| 12.4          | #94: Not being aware of data alignment 321                                                                                                                                                  |
| 12.5          | #95: Not understanding stack vs. heap 324                                                                                                                                                   |
|               | Stack vs. heap 324 • Escape analysis 329                                                                                                                                                    |
| 12.6          | #96: Not knowing how to reduce allocations 331                                                                                                                                              |
|               | API changes 331 • Compiler optimizations 332 • sync.Pool 332                                                                                                                                |
| 12.7          | #97: Not relying on inlining 334                                                                                                                                                            |
| 12.8          | #98: Not using Go diagnostics tooling 337                                                                                                                                                   |
|               | Profiling 337 • Execution tracer 344                                                                                                                                                        |
| 12.9          | #99: Not understanding how the GC works 347                                                                                                                                                 |
|               | Concepts 347 Examples 349                                                                                                                                                                   |
| 12.10         | #100: Not understanding the impacts of running Go in Docker and Kubernetes 352                                                                                                              |
|               | Final words 355                                                                                                                                                                             |
|               | index 357                                                                                                                                                                                   |

12
