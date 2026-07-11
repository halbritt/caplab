<span id="part0029.xhtml"></span>
# Summary of Red Flags

Summary of Red Flags

Here are a few of of the most important red flags discussed in this book. The presence of any of these symptoms in a system suggests that there is a problem with the system’s design:

<span class="class_s2by">Shallow Module</span>: the interface for a class or method isn’t much simpler than its implementation (see [pp. 25](009-4-modules-should-be-deep.md#part0008.xhtml#a27T), [110](018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md#part0017.xhtml)).

<span class="class_s2by">Information Leakage</span>: a design decision is reflected in multiple modules (see [p. 31](010-5-information-hiding-and-leakage.md#part0009.xhtml)).

<span class="class_s2by">Temporal Decomposition</span>: the code structure is based on the order in which operations are executed, not on information hiding (see [p. 32](010-5-information-hiding-and-leakage.md#part0009.xhtml)).

<span class="class_s2by">Overexposure</span>: An API forces callers to be aware of rarely used features in order to use commonly used features (see [p. 36](010-5-information-hiding-and-leakage.md#part0009.xhtml)).

<span class="class_s2by">Pass-Through Method</span>: a method does almost nothing except pass its arguments to another method with a similar signature (see [p. 52](012-7-different-layer-different-abstraction.md#part0011.xhtml#a28K)).

<span class="class_s2by">Repetition</span>: a nontrivial piece of code is repeated over and over (see [p. 68](014-9-better-together-or-better-apart.md#part0013.xhtml)).

<span class="class_s2by">Special-General Mixture</span>: special-purpose code is not cleanly separated from general purpose code (see [p. 71](014-9-better-together-or-better-apart.md#part0013.xhtml)).

<span class="class_s2by">Conjoined Methods</span>: two methods have so many dependencies that its hard to understand the implementation of one without understanding the implementation of the other (see [p. 75](014-9-better-together-or-better-apart.md#part0013.xhtml)).

<span class="class_s2by">Comment Repeats Code</span>: all of the information in a comment is immediately obvious from the code next to the comment (see [p. 104](018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md#part0017.xhtml)).

<span class="class_s2by">Implementation Documentation Contaminates Interface</span>: an interface comment describes implementation details not needed by users of the thing being documented (see [p. 114](018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md#part0017.xhtml)).

<span class="class_s2by">Vague Name</span>: the name of a variable or method is so imprecise that it doesn’t convey much useful information (see [p. 123](019-14-choosing-names.md#part0018.xhtml))<span id="part0029.xhtml#page_184"></span>.

<span class="class_s2by">Hard to Pick Name</span>: it is difficult to come up with a precise and intuitive name for an entity (see [p. 125](019-14-choosing-names.md#part0018.xhtml)).

<span class="class_s2by">Hard to Describe</span>: in order to be complete, the documentation for a variable or method must be long. (see [p. 133](020-15-write-the-comments-first.md#part0019.xhtml)).

<span class="class_s2by">Nonobvious Code</span>: the behavior or meaning of a piece of code cannot be understood easily. (see [p. 150](023-18-code-should-be-obvious.md#part0022.xhtml)).
