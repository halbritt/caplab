<span id="part0018.xhtml"></span>
# 14: Choosing Names

Chapter 14

Choosing Names

Selecting names for variables, methods, and other entities is one of the most underrated aspects of software design. Good names are a form of documentation: they make code easier to understand. They reduce the need for other documentation and make it easier to detect errors. Conversely, poor name choices increase the complexity of code and create ambiguities and misunderstandings that can result in bugs. Name choice is an example of the principle that complexity is incremental. Choosing a mediocre name for a particular variable, as opposed to the best possible name, probably won’t have much impact on the overall complexity of a system. However, software systems have thousands of variables; choosing good names for all of these will have a significant impact on complexity and manageability.

<span id="part0018.xhtml#a2A6"></span>
14.1  Example: bad names cause bugs

Sometimes even a single poorly named variable can have severe consequences. The most challenging bug I ever fixed came about because of a poor name choice. In the late 1980’s and early 1990’s my graduate students and I created a distributed operating system called Sprite. At some point we noticed that files would occasionally lose data: one of the data blocks suddenly became all zeroes, even though the file had not been modified by a user. The problem didn’t happen very often, so it was exceptionally difficult to track down. A few of the graduate students tried to find the bug, but they were unable to make progress and eventually gave up. However, I consider any unsolved bug to be an intolerable personal insult, so I decided to track it down.

It took six months, but I eventually found and fixed the bug. The problem was actually quite simple (as are most bugs, once you figure them out). The file system <span id="part0018.xhtml#page_122"></span>code used the variable name <span class="class_s2c1">block</span> for two different purposes. In some situations, <span class="class_s2c1">block</span> referred to a physical block number on disk; in other situations, <span class="class_s2c1">block</span> referred to a logical block number within a file. Unfortunately, at one point in the code there was a <span class="class_s2c1">block</span> variable containing a logical block number, but it was accidentally used in a context where a physical block number was needed; as a result, an unrelated block on disk got overwritten with zeroes.

While tracking down the bug, several people, including myself, read over the faulty code, but we never noticed the problem. When we saw the variable <span class="class_s2c1">block</span> used as a physical block number, we reflexively assumed that it really held a physical block number. It took a long process of instrumentation, which eventually showed that the corruption <span class="class_s2c">must</span> be happening in a particular statement, before I was able to get past the mental block created by the name and check to see exactly where its value came from. If different variable names had been used for the different kinds of blocks, such as <span class="class_s2c1">fileBlock</span> and <span class="class_s2c1">diskBlock</span>, it’s unlikely that the error would have happened; the programmer would have known that <span class="class_s2c1">fileBlock</span> couldn’t be used in that situation. Even better would be to define distinct types for the two different kinds of blocks, so that they cannot possibly be interchanged.

Unfortunately, most developers don’t spend much time thinking about names. They tend to use the first name that comes to mind, as long as it’s reasonably close to matching the thing it names. For example, <span class="class_s2c1">block</span> is a pretty close match for both a physical block on disk and a logical block within a file; it’s certainly not a horrible name. Even so, it resulted in a huge expenditure of time to track down a subtle bug. Thus, you shouldn’t settle for names that are just “reasonably close”. Take a bit of extra time to choose great names, which are precise, unambiguous, and intuitive. The extra attention will pay for itself quickly, and over time you’ll learn to choose good names quickly.

<span id="part0018.xhtml#a2A7"></span>
14.2  Create an image

When choosing a name, the goal is to create an image in the mind of the reader about the nature of the thing being named. A good name conveys a lot of information about what the underlying entity is, and, just as important, what it is not. When considering a particular name, ask yourself: “If someone sees this name in isolation, without seeing its declaration, its documentation, or any code that uses the name, how closely will they be able to guess what the name refers to? Is there some other name that will paint a clearer picture?” Of course, there is a limit to how much information you can put in a single name; names become unwieldy if they contain more than two or three words. <span id="part0018.xhtml#page_123"></span>Thus, the challenge is to find just a few words that capture the most important aspects of the entity.

Names are a form of abstraction: they provide a simplified way of thinking about a more complex underlying entity. Like other forms of abstraction, the best names are those that focus attention on what is most important about the underlying entity while omitting details that are less important.

<span id="part0018.xhtml#a2A8"></span>
14.3  Names should be precise

Good names have two properties: precision and consistency. Let’s start with precision. The most common problem with names is that they are too generic or vague; as a result, it’s hard for readers to tell what the name refers to; the reader may assume that the name refers to something different from reality, as in the <span class="class_s2c1">block</span> bug above. Consider the following method declaration:

/\*\*

\* Returns the total number of indexlets this object is managing.

\*/

int IndexletManager::getCount() {...}

The term “count” is too generic: count of what? If someone sees an invocation of this method, they are unlikely to know what it does unless they read its documentation. A more precise name like <span class="class_s2c1">numActiveIndexlets</span> would be better: many readers will probably be able to guess what the method returns without having to look at its documentation.

<div class="class_sdg">

<img src="../assets/OEBPS/image_rsrc2HA.jpg" class="class_sda" />  <span class="class_s2by1">Red Flag: Vague Name</span>  <img src="../assets/OEBPS/image_rsrc2HA.jpg" class="class_sda" />

If a variable or method name is broad enough to refer to many different things, then it doesn’t convey much information to the developer and the underlying entity is more likely to be misused.

</div>

Here are some other examples of names that aren’t precise enough, taken from various student projects:

- A project building a GUI text editor used the names <span class="class_s2c1">x</span> and <span class="class_s2c1">y</span> to refer to the position of a character in the file. These names are too generic. They could <span id="part0018.xhtml#page_124"></span>mean many things; for example, they might also represent the coordinates (in pixels) of a character on the screen. Someone seeing the name x in isolation is unlikely to think that it refers to the position of a character within a line of text. The code would be clearer if it used names such as <span class="class_s2c1">charIndex</span> and <span class="class_s2c1">lineIndex</span>, which reflect the specific abstractions that the code implements.

- Another editor project contained the following code:

  // Blink state: true when cursor visible.

  private boolean blinkStatus = true;

- The name <span class="class_s2c1">blinkStatus</span> doesn’t convey enough information. The word “status” is too vague for a boolean value: it gives no clue about what a true or false value means. The word “blink” is also vague, since it doesn’t indicate what is blinking. The following alternative is better:

  // Controls cursor blinking: true means the cursor is visible,

  // false means the cursor is not displayed.

  private boolean cursorVisible = true;

- The name <span class="class_s2c1">cursorVisible</span> conveys more information; for example, it allows readers to guess what a true value means (as a general rule, names of boolean variables should always be predicates). The word “blink” is no longer in the name, so readers will have to consult the documentation if they want to know why the cursor isn’t always visible; this information is less important.

- A project implementing a consensus protocol contained the following code:

  // Value representing that the server has not voted (yet) for

  // anyone for the current election term.

  private static final String VOTED_FOR_SENTINEL_VALUE = "null";

- The name for this value indicates that it’s special but it doesn’t say what the special meaning is. A more specific name such as <span class="class_s2c1">NOT_YET_VOTED</span> would be better.

- A variable named <span class="class_s2c1">result</span> was used in a method with no return value. This name has multiple problems. First, it creates the misleading impression that it will be the return value of the method. Second, it provides essentially no information about what it actually holds, except that it is some computed value. The name should provide information about what the result actually is, such as <span class="class_s2c1">mergedLine</span> or <span class="class_s2c1">totalChars</span>. In methods that do actually have return values, then using the name <span class="class_s2c1">result</span> is reasonable. This name is still a bit generic, but readers can look at the method documentation to see its meaning, and it’s helpful to know that the value will eventually become the return value.

- <div id="part0018.xhtml#page_125">

  The Linux kernel contains two structures describing network sockets: <span class="class_s2c1">struct socket</span> and <span class="class_s2c1">struct sock</span>. A <span class="class_s2c1">struct sock</span> contains a <span class="class_s2c1">struct socket</span> as its first element; it’s effectively a subclass of struct socket. These names are so similar that it’s difficult to remember which is which. It would be better to choose names that are easy to distinguish and clarify the relationship between the two types, such as <span class="class_s2c1">struct sock_base</span> and <span class="class_s2c1">struct inet_sock</span>.

  </div>

Like all rules, the rule about choosing precise names has a few exceptions. For example, it’s fine to use generic names like <span class="class_s2c1">i</span> and <span class="class_s2c1">j</span> as loop iteration variables, as long as the loops only span a few lines of code. If you can see the entire range of usage of a variable, then the meaning of the variable will probably be obvious from the code so you don’t need a long name. For example, consider the following code:

for (i = 0; i \< numLines; i++) {

<span class="class_s2c2">...</span>

}

It’s clear from this code that <span class="class_s2c1">i</span> is being used to iterate over each of the lines in some entity. If the loop gets so long that you can’t see it all at once, or if the meaning of the iteration variable is harder to figure out from the code, then a more descriptive name is in order.

It’s also possible for a name to be too specific, such as in this declaration for a method that deletes a range of text:

void delete(Range selection) {...}

The argument name <span class="class_s2c1">selection</span> is too specific, since it suggests that the text being deleted is the text currently selected in the user interface. However, this method can be invoked on any range of text, selected or not. Thus, the argument name should be more generic, such as range.

If you find it difficult to come up with a name for a particular variable that is precise, intuitive, and not too long, this is a red flag. It suggests that the variable may not have a clear definition or purpose. When this happens, consider alternative factorings. For example, perhaps you are trying to use a single variable to represent several things; if so, separating the representation into multiple variables may result in a simpler definition for each variable. The process of choosing good names can improve your design by identifying weaknesses.

<div class="class_sdg">

<img src="../assets/OEBPS/image_rsrc2HA.jpg" class="class_sda" />  <span class="class_s2by1">Red Flag: Hard to Pick Name</span>  <img src="../assets/OEBPS/image_rsrc2HA.jpg" class="class_sda" />

If it’s hard to find a simple name for a variable or method that creates a clear image of the underlying object, that’s a hint that the underlying object may not have a clean design<span id="part0018.xhtml#page_126"></span>.

</div>

<span id="part0018.xhtml#a2A9"></span>
14.4  Use names consistently

The second important property of good names is consistency. In any program there are certain variables that are used over and over again. For example, a file system manipulates block numbers repeatedly. For each of these common usages, pick a name to use for that purpose, and use the same name everywhere. For example, a file system might always use <span class="class_s2c1">fileBlock</span> to hold the index of a block within a file. Consistent naming reduces cognitive load in much the same way as reusing a common class: once the reader has seen the name in one context, they can reuse their knowledge and instantly make assumptions when they see the name in a different context.

Consistency has three requirements: first, always use the common name for the given purpose; second, never use the common name for anything other than the given purpose; third, make sure that the purpose is narrow enough that all variables with the name have the same behavior. This third requirement was violated in the file system bug at the beginning of the chapter. The file system used <span class="class_s2c1">block</span> for variables with two different behaviors (file blocks and disk blocks); this led to a false assumption about the meaning of a variable, which in turn resulted in a bug.

Sometimes you will need multiple variables that refer to the same general sort of thing. For example, a method that copies file data will need two block numbers, one for the source and one for the destination. When this happens, use the common name for each variable but add a distinguishing prefix, such as <span class="class_s2c1">srcFileBlock</span> and <span class="class_s2c1">dstFileBlock</span>.

Loops are another area where consistent naming can help. If you use names such as <span class="class_s2c1">i</span> and <span class="class_s2c1">j</span> for loop variables, always use <span class="class_s2c1">i</span> in outermost loops and <span class="class_s2c1">j</span> for nested loops. This allows readers to make instant (safe) assumptions about what’s happening in the code when they see a given name<span id="part0018.xhtml#page_127"></span>.

<span id="part0018.xhtml#a2AA"></span>
14.5  Avoid extra words

Every word in a name should provide useful information; words that don’t help to clarify the variable’s meaning just add clutter (e.g. they may cause more lines to wrap). One common mistake is to add a generic noun such as <span class="class_s2c1">field</span> or <span class="class_s2c1">object</span> to a name, such as <span class="class_s2c1">fileObject</span>. In this case the word <span class="class_s2c1">Object</span> probably doesn’t provide useful information (are there also files that are not objects?), so it should be omitted from the name.

Some coding styles include type information in names, such as <span class="class_s2c1">filePtr</span> for a variable that is a pointer to a file object. An extreme example of this is Hungarian Notation, which was used for many years at Microsoft for C programming. In Hungarian Notation, every variable name has a prefix that indicates its full type. For example, the name <span class="class_s2c1">arru8NumberList</span> means that the variable is an array of unsigned 8-bit integers. Although I have included type information in variable names in the past, I no longer recommend it. With modern IDEs it is easy to click from a variable name to its declaration (or, the IDE may even display the type information automatically), so there is no need to include this information in the variable name.

Another example of extraneous words is when an instance variable of a class repeats the class name, such as an instance variable <span class="class_s2c1">fileBlock</span> in a class named <span class="class_s2c1">File</span>. It should be obvious from the context that the variable is part of the <span class="class_s2c1">File</span> class, so incorporating the class name in the variable name provides no useful information. Just name the variable <span class="class_s2c1">block</span> (unless the class contains multiple blocks of different types).

<span id="part0018.xhtml#a2AB"></span>
14.6  A different opinion: Go style guide

Not everyone shares my views about naming. Some of the developers of the Go language argue that names should be very short, often only a single character. In a presentation on name choice for Go, Andrew Gerrand states that “long names obscure what the code does.”<span id="part0018.xhtml#a2CV"></span><a href="#part0018.xhtml" class="class_s2ca">1</a> He presents this code sample, which uses single-letter variable names:

func RuneCount(b \[\]byte) int {

<span class="class_s2c2">i, n := 0, 0</span>

<span class="class_s2c2">for i \< len(b) {</span>

<span class="class_s2c2">if b\[i\] \< RuneSelf {</span>

<span class="class_s2c2">i+<span id="part0018.xhtml#page_128"></span>+</span>

<span class="class_s2c2">} else {</span>

<span class="class_s2c2">\_, size := DecodeRune(b\[i:\])</span>

<span class="class_s2c2">i += size</span>

<span class="class_s2c2">}</span>

<span class="class_s2c2">n++</span>

<span class="class_s2c2">}</span>

<span class="class_s2c2">return n</span>

}

and argues that it is more readable than the following version, which uses longer names:

func RuneCount(buffer \[\]byte) int {

<span class="class_s2c2">index, count := 0, 0</span>

<span class="class_s2c2">for index \< len(buffer) {</span>

<span class="class_s2c2">if buffer\[index\] \< RuneSelf {</span>

<span class="class_s2c2">index++</span>

<span class="class_s2c2">} else {</span>

<span class="class_s2c2">\_, size := DecodeRune(buffer\[index:\])</span>

<span class="class_s2c2">index += size</span>

<span class="class_s2c2">}</span>

<span class="class_s2c2">count++</span>

<span class="class_s2c2">}</span>

<span class="class_s2c2">return count</span>

}

Personally, I don’t find the second version any more difficult to read than the first. If anything, the name <span class="class_s2c1">count</span> gives a slightly better clue to the behavior of the variable than <span class="class_s2c1">n</span>. With the first version I ended up reading through the code trying to figure out what <span class="class_s2c1">n</span> means, whereas I didn’t feel that need with the second version. But, if <span class="class_s2c1">n</span> is used consistently throughout the system to refer to counts (and nothing else), then the short name will probably be clear to other developers.

The Go culture encourages the use of the same short name for multiple different things: <span class="class_s2c1">ch</span> for character or channel, <span class="class_s2c1">d</span> for data, difference, or distance, and so on. To me, ambiguous names like these are likely to result in confusion and error, just as in the <span class="class_s2c1">block</span> example.

Overall, I would argue that readability must be determined by readers, not writers. If you write code with short variable names and the people who read it find it easy to understand, then that’s fine. If you start getting complaints that your code is cryptic, then you should consider using longer names (a Web search for “go language short names” will identify several such complaints). Similarly, if I start getting complaints that long variable names make my code harder to read, then I’ll consider using shorter <span id="part0018.xhtml#page_129"></span>ones.

Gerrand makes one comment that I agree with: “The greater the distance between a name’s declaration and its uses, the longer the name should be.” The earlier discussion about using loop variables named <span class="class_s2c1">i</span> and <span class="class_s2c1">j</span> is an example of this rule.

<span id="part0018.xhtml#a2AC"></span>
14.7  Conclusion

Well chosen names help to make code more obvious; when someone encounters the variable for the first time, their first guess about its behavior, made without much thought, will be correct. Choosing good names is an example of the investment mindset discussed in [Chapter 3:](008-3-working-code-isnt-enough.md#part0007.xhtml) if you take a little extra time up front to select good names, it will be easier for you to work on the code in the future. In addition, you will be less likely to introduce bugs. Developing a skill for naming is also an investment. When you first decide to stop settling for mediocre names, you may find it frustrating and time-consuming to come up with good names. However, as you get more experience you’ll find that it becomes easier; eventually, you’ll get to the point where it takes almost no extra time to choose good names, so you will get the benefits almost for free.

<div class="class_se">

<img src="../assets/OEBPS/image_rsrc2HB.jpg" class="class_se1" />

</div>

<a href="#part0018.xhtml#a2CV" class="class_s2ca">1</a><https://talks.golang.org/2014/names.slide#1>
