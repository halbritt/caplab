<span id="page-253-1"></span>
<span id="page-253-0"></span>
# Chapter 19: My Project Is Not Object Oriented. How Do I Make Safe Changes?


The title of this chapter is a bit provocative. We can make safe changes in any language, but some languages make change easier than others. Even though object orientation has pretty much pervaded the industry, there are many other languages and ways of programming. There are rule-based languages, functional programming languages, constraint-based programming languages—the list goes on. But of all of these, none are as widespread as the plain old procedural languages, such as C, COBOL, FORTRAN, Pascal, and BASIC.

Procedural languages are especially challenging in a legacy environment. It's important to get code under test before modifying it, but the number of things you can do to introduce unit tests in procedural languages is pretty small. Often the easiest thing to do is think really hard, patch the system, and hope that your changes were right.

This testing dilemma is pandemic in procedural legacy code. Procedural languages often just don't have the seams that OO (and many functional) programming languages do. Savvy developers can work past this by managing their dependencies carefully (there is a lot of great code written in C, for instance), but it is also easy to end up with a real snarl that is hard to change incrementally and verifiably.

Because breaking dependencies in procedural code is so hard, often the best strategy is to try to get a large chunk of the code under test before doing anything else and then use those tests to get some feedback while developing. The techniques in Chapter 12, *I Need to Make Many Changes in One Area. Do I Have to Break Dependencies for All the Classes Involved?* can help. They apply to procedural code as well as object-oriented code. In short, it pays to look for a *pinch point (180)* and then use the *link seam (36)* to break dependencies well **My Project Is Not Object Oriented**

<span id="page-254-2"></span><span id="page-254-0"></span>enough to get the code in a test harness. If your language has a macro preprocessor, you can use the *preprocessing seam (33)* as well.

That's the standard course of action, but it isn't the only one. In the rest of this chapter, we look at ways to break dependencies locally in procedural programs, how to make verifiable changes more easily, and ways of moving forward when we're using a language that has a migration path to OO.

## An Easy Case

<span id="page-254-1"></span>Procedural code isn't always a problem. Here's an example, a C function from the Linux operating system. Would it be hard to write tests for this function if we had to make some changes to it?

```
void set_writetime(struct buffer_head * buf, int flag)
{
 int newtime;
 if (buffer_dirty(buf)) {
 /* Move buffer to dirty list if jiffies is clear */
 newtime = jiffies + (flag ? bdf_prm.b_un.age_super : 
 bdf_prm.b_un.age_buffer);
 if(!buf->b_flushtime || buf->b_flushtime > newtime)
 buf->b_flushtime = newtime;
 } else {
 buf->b_flushtime = 0;
 }
}
```

To test this function, we can set the value of the jiffies variable, create a buffer\_head, pass it into the function, and then check its values after the call. In many functions, we're not so lucky. Sometimes a function calls a function that calls another function. Then it calls something hard to deal with: a function that actually does I/O someplace or comes from some vendor's library. We want to test what the code does, but too often the answer is "It does something cool, but only something outside the program will know about it, not you."

## A Hard Case

Here is a C function that we want to change. It would be nice if we could put it under test before we do:

```
#include "ksrlib.h"
int scan_packets(struct rnode_packet *packet, int flag)
 struct rnode_packet *current = packet;
 int scan_result, err = 0;
 while(current) {
 scan_result = loc_scan(current->body, flag);
 if(scan_result & INVALID_PORT) {
 ksr_notify(scan_result, current);
 }
 ...
 current = current->next;
 }
 return err;
```

This code calls a function named ksr\_notify that has a bad side effect. It writes out a notification to a third party system, and we'd rather that it didn't do that while we're testing.

One way to handle this is to use a *link seam (36).* If we want to test without having the effect of all the functions in that library, we can make a library that contains fakes: functions that have the same names as the original functions but that don't really do what they are intended to do. In this case, we can write a body for ksr\_notify that looks like this:

```
void ksr_notify(int scan_code, struct rnode_packet *packet)
```

We can build it in a library and link to it. The scan\_packets function will behave exactly the same, except for one thing: It won't send the notification. But that's fine if we want to pin down other behavior in the function before changing it.

Is that the strategy we should use? It depends. If there are a lot of functions in the ksr library and we consider their calls to be sort of peripheral to the main logic of the system, then, yes, it would make sense to create a library of fakes and link to it during test. On the other hand, if we want to sense through those functions or we want to vary some of the values that they return, using *link seams (36)* isn't as nice; it's actually pretty tedious. Because the substitution happens at link time, we can provide only one function definition for each executable that we build. If we want a fake ksr\_notify function to behave one way in one test and another way in another test, we have to put code in the body and set up conditions in the test that will force it to act a certain way. All in all,

<span id="page-256-0"></span>![](../assets/_page_256_Picture_1.jpeg)

it is kind of messy. Unfortunately, many procedural languages don't leave us with any other options.

In C, there is another alternative. C has a macro preprocessor that we can use to make it easier to write tests against the scan\_packets function. Here is the file that contains scan\_packets after we've added testing code:

```
#include "ksrlib.h"
#ifdef TESTING
#define ksr_notify(code,packet)
#endif
int scan_packets(struct rnode_packet *packet, int flag)
{
 struct rnode_packet *current = packet;
 int scan_result, err = 0;
 while(current) {
 scan_result = loc_scan(current->body, flag);
 if(scan_result & INVALID_PORT) {
 ksr_notify(scan_result, current);
 }
 ...
 current = current->next;
 }
 return err;
}
#ifdef TESTING
#include <assert.h>
int main () {
 struct rnode_packet packet;
 packet.body = ...
 ...
 int err = scan_packets(&packet, DUP_SCAN);
 assert(err & INVALID_PORT);
 ...
 return 0;
}
#endif
```

In this code, we have a preprocessing define, TESTING, that defines the call to ksr\_notify out of existence when we are testing. It also provides a little stub that contains tests.

Mixing tests and source into a file like this isn't really the clearest thing we can do. Often it makes code harder to navigate. An alternative is to use file inclusion so that the tests and production code are in different files:

```
#include "ksrlib.h"
#include "scannertestdefs.h"
int scan_packets(struct rnode_packet *packet, int flag)
 struct rnode_packet *current = packet;
 int scan_result, err = 0;
 while(current) {
 scan_result = loc_scan(current->body, flag);
 if(scan_result & INVALID_PORT) {
 ksr_notify(scan_result, current);
 }
 ...
 current = current->next;
 }
 return err;
```

### #include "testscanner.tst"

With this change, the code looks reasonably close to what it would look like without the testing infrastructure. The only difference is that we have an #include statement at the end of the file. If we forward declare the functions we are testing, we can move everything in the bottom include file into the top one.

To run the tests, we just have to define TESTING and build this file by itself. When TESTING is defined, the main( ) function in testscanner.tst will be compiled and linked into an executable that will run the tests. The main( ) function we have in that file runs only tests for the scanning routines. We can set up things to run groups of tests at the same time by defining separate testing functions for each of our tests.

```
#ifdef TESTING
#include <assert.h>
void test_port_invalid() {
 struct rnode_packet packet;
 packet.body = ...
 ...
 int err = scan_packets(&packet, DUP_SCAN);
 assert(err & INVALID_PORT);
void test_body_not_corrupt() {
 ...
void test_header() {
 ...
```

<span id="page-258-1"></span>![](../assets/_page_258_Picture_1.jpeg)

```
}
#endif
   In another file, we can call them from main:
int main() {
 test_port_invalid();
 test_body_not_corrupt();
 test_header();
 return 0;
}
```

<span id="page-258-0"></span>We can go even further by adding registration functions that make test grouping easier. See the various C unit-testing frameworks available at <www.xprogramming.com>for details.

Although macro preprocessors are easily misused, they are actually very useful in this context. File inclusion and macro replacement can help us get past dependencies in the thorniest code. As long as we restrict rampant usage of macros to code that runs under test, we don't have to be too concerned that we'll misuse macros in ways that will affect the production code.

C is one of the few mainstream languages that have a macro preprocessor. In general, to break dependencies in other procedural languages, we have to use the *link seam (36)* and attempt to get larger areas of code under test.

#### Adding New Behavior


In procedural legacy code, it pays to bias toward introducing new functions rather than adding code to old ones. At the very least, we can write tests for the new functions that we write.

How do we avoid introducing dependency traps in procedural code? One way (outlined in Chapter 8, *How Do I Add a Feature?*) is to use *test-driven development (88)* (TDD). TDD works in both object-oriented and procedural code. Often the work of trying to formulate a test for each piece of code that we're thinking of writing leads us to alter its design in good ways. We concentrate on writing functions that do some piece of computational work and then integrate them into the rest of the application.

Often we have to think about what we are going to write in a different way to do this. Here's an example. We need to write a function called send\_command. The send\_command function is going to send an ID, a name, and a command string to another system through a function called mart\_key\_send. The code for the function won't be too bad. We can imagine that it will look something like this:

```
void send_command(int id, char *name, char *command_string) {
 char *message, *header;
 if (id == KEY_TRUM) {
 message = ralloc(sizeof(int) + HEADER_LEN + ...
 ...
 } else {
 ...
 }
 sprintf(message, "%s%s%s", header, command_string, footer);
 mart_key_send(message);
 free(message);
```

But how would we write a test for a function like that? Especially because the only way to find out what happens is to be right where the call to mart\_key\_send is? What if we took a slightly different approach?

We could test all of that logic before the mart\_key\_send call if it was in another function. We might write our first test like this:

```
char *command = form_command(1, 
 "Mike Ratledge", 
 "56:78:cusp-:78");
assert(!strcmp("<-rsp-Mike Ratledge><56:78:cusp-:78><-rspr>",
 command));
```

Then we can write a form\_command function, which returns a command:

```
char *form_command(int id, char *name, char *command_string)
    char *message, *header;
 if (id == KEY_TRUM) {
 message = ralloc(sizeof(int) + HEADER_LEN + ...
 ...
 } else {
 ...
 }
 sprintf(message, "%s%s%s", header, command_string, footer);
 return message;
```

When we have that, we can write the simple send\_command function that we need:

```
void send_command(int id, char *name, char *command_string) {
 char *command = form_command(id, name, command_string);
 mart_key_send(command);
 free(message);
```

**Adding New Behavior**

<span id="page-260-0"></span>In many cases, this sort of a reformulation is exactly what we need to move forward. We put all of the pure logic into one set of functions so we can keep them free of problematic dependencies. When we do this, we end up with little wrapper functions such as send\_command, which bind our logic and our dependencies. It's not perfect, but it's workable when the dependencies aren't too pervasive.

In other cases, we need to write functions that will be littered with external calls. There isn't much computation in these functions, but the sequencing of the calls that they make is very important. For example, if we are trying to write a function that calculates interest on a loan, the straightforward way of doing it might look something like this:

```
void calculate_loan_interest(struct temper_loan *loan, int calc_type) 
{
 ...
 db_retrieve(loan->id);
 ...
 db_retrieve(loan->lender_id);
 ...
 db_update(loan->id, loan->record);
 ...
 loan->interest = ... 
}
```

What do we do in a case like this? In many procedural languages, the best choice is to just skip writing the test first and write the function as best we can. Maybe we can test that it does the right thing at a higher level. But in C, we have another option. C supports function pointers, and we can use them to get another seam in place. Here's how:

We can create a struct that contains pointers to functions:

```
struct database
{
 void (*retrieve)(struct record_id id);
 void (*update)(struct record_id id, struct record_set *record);
 ...
};
```

We can initialize those pointers to the addresses of the database-access functions. We can pass that struct to any new functions we write that need to access the database. In production code, the functions can point to the real databaseaccess functions. We can have them point at fakes when we are testing.

With earlier compilers, we might have to use the old-style function pointer syntax:

```
extern struct database db;
(*db.update)(load->id, loan->record);
```

**Adding New Behavior**

<span id="page-261-1"></span><span id="page-261-0"></span>But with others, we can call these functions in a very natural object-oriented style:

```
extern struct database db;
db.update(load->id, loan->record);
```

This technique isn't C specific. It can be used in most languages that support function pointers.

## Taking Advantage of Object Orientation

In object-oriented languages, we have *object seams (40)* available. They have some nice properties:

- They are easy to notice in the code.
- They can be used to break code down into smaller, more understandable pieces.
- They provide more flexibility. Seams that you introduce for testing might be useful when you have to extend your software.

Unfortunately, not all software can be easily migrated to objects, but, in some cases, it is far easier than others. Many procedural languages have evolved into object-oriented languages. Microsoft's Visual Basic language only recently became fully object oriented, there are OO extensions to COBOL and Fortran, and most C compilers give you capability to compile C++, too.

When your language gives you the option to move toward object orientation, you have more options. The first step is usually to use *Encapsulate Global References (339)* to get the pieces you are changing under test. We can use it to get out of the bad dependency situation we had in the scan\_packets function earlier in the chapter. Remember that the problem we had was with the ksr\_notify function: We didn't want it to really notify whenever we ran our tests.

```
int scan_packets(struct rnode_packet *packet, int flag)
 struct rnode_packet *current = packet;
 int scan_result, err = 0;
 while(current) {
 scan_result = loc_scan(current->body, flag);
 if(scan_result & INVALID_PORT) {
 ksr_notify(scan_result, current);
 }
 ...
 current = current->next;
```

**Taking Advantage of Object Orientation**

<span id="page-262-0"></span>![](../assets/_page_262_Picture_1.jpeg)

```
 }
 return err;
```

}

The first step is to compile under C++ rather than under C. This can be either a small or a large change, depending on how we handle it. We can bite the bullet and attempt to recompile the entire project in C++, or we can do it piece by piece, but it does take some time.

When we have the code compiling under C++, we can start by finding the declaration of the ksr\_notify function and wrapping it in a class:

```
class ResultNotifier
{
public:
 virtual void ksr_notify(int scan_result, 
 struct rnode_packet *packet);
};
```

We can also introduce a new source file for the class and put the default implementation there:

```
extern "C" void ksr_notify(int scan_result, 
 struct rnode_packet *packet);
void ResultNotifier::ksr_notify(int scan_result, 
 struct rnode_packet *packet)
{
 ::ksr_notify(scan_result, packet);
}
```

Notice that we're not changing the name of the function or its signature. We're using *Preserve Signatures (312)* so that we minimize any chance of errors.

Next, we declare a global instance of ResultNotifier and put it into a source file:

ResultNotifier globalResultNotifier;

Now we can recompile and let the errors tell us where we have to change things. Because we've put the declaration of ksr\_notify in a class, the compiler doesn't see a declaration of it at global scope any longer.

Here's the original function:

```
#include "ksrlib.h"
int scan_packets(struct rnode_packet *packet, int flag)
{
 struct rnode_packet *current = packet;
 int scan_result, err = 0;
```

**Taking Advantage of Object Orientation**

```
 while(current) {
 scan_result = loc_scan(current->body, flag);
 if(scan_result & INVALID_PORT) {
 ksr_notify(scan_result, current);
 }
 ...
 current = current->next;
 }
 return err;
```

To make it compile now, we can use an extern declaration to make the globalResultNotifier object visible and preface ksr\_notify with the name of the object:

```
#include "ksrlib.h"
extern ResultNotifier globalResultNotifier;
int scan_packets(struct rnode_packet *packet, int flag)
 struct rnode_packet *current = packet;
 int scan_result, err = 0;
 while(current) {
 scan_result = loc_scan(current->body, flag);
 if(scan_result & INVALID_PORT) {
 globalResultNotifier.ksr_notify(scan_result, current);
 }
 ...
 current = current->next;
 }
 return err;
}
```

At this point, the code works the same way. The ksr\_notify method on ResultNotifier delegates to the ksr\_notify function. How does that do us any good? Well, it doesn't—yet. The next step is to find some way of setting things up so that we can use this ResultNotifier object in production and use another one when we are testing. There are many ways of doing this, but one that carries us further in this direction is to *Encapsulate Global References (339)* again and put scan\_packets in another class that we can call Scanner.

**Taking Advantage of Object Orientation**

<span id="page-264-1"></span>![](../assets/_page_264_Picture_1.jpeg)

```
class Scanner
{
public:
 int scan_packets(struct rnode_packet *packet, int flag);
};
```

Now we can apply *Parameterize Constructor (379)* and change the class so that it uses a ResultNotifier that we supply:

```
class Scanner
{
private:
 ResultNotifier& notifier;
public:
 Scanner();
 Scanner(ResultNotifier& notifier);
 int scan_packets(struct rnode_packet *packet, int flag);
};
// in the source file
Scanner::Scanner() 
: notifier(globalResultNotifier) 
{}
Scanner::Scanner(ResultNotifier& notifier) 
: notifier(notifier)
{}
```

When we make this change, we can find the places where scan\_packets is being used, create an instance of Scanner, and use it.

These changes are pretty safe and pretty mechanical. They aren't great examples of object-oriented design, but they are good enough to use as a wedge to break dependencies and allow us to test as we move forward.

## It's All Object Oriented

Some procedural programmers like to beat up on object orientation; they consider it unnecessary or think that its complexity doesn't buy anything. But when you really think about it, you begin to realize that all procedural programs are object oriented; it's just a shame that many contain only one object. To see this, imagine a program with about 100 functions. Here are their declarations:

**It's All Object Oriented**

```
...
int db_find(char *id, unsigned int mnemonic_id, 
 struct db_rec **rec);
...
...
void process_run(struct gfh_task **tasks, int task_count);
...
  Now imagine that we can put all of the declarations in one file and surround
them with a class declaration:
class program
public:
 ...
 int db_find(char *id, unsigned int mnemonic_id, 
 struct db_rec **rec);
 ...
 ...
 void process_run(struct gfh_task **tasks, int task_count);
 ...
};
  Now we can find each function definition (here's one):
int db_find(char *id, 
 unsigned int mnemonic_id, 
 struct db_rec **rec);
 ...
  And prefix its name with the name of the class:
int program::db_find(char *id, 
 unsigned int mnemonic_id, 
 struct db_rec **rec)
 ...
  Now we have to write a new main( )function for the program:
int main(int ac, char **av) 
 program the_program;
 return the_program.main(ac, av);
```

**It's All Object Oriented**

<span id="page-266-0"></span>![](../assets/_page_266_Picture_1.jpeg)

Does that change the behavior of the system? Not really. That change was just a mechanical process, and it kept the meaning and behavior of the program exactly the same. The old C system was, in reality, just one big object. When we start using *Encapsulate Global References (339)* we're making new objects, and subdividing the system in ways which make it easier to work with.

When procedural languages have object-oriented extensions, they allow us to move in this direction. This isn't deep object-orientation; it's just using objects enough to break up the program for testing.

What can we do besides extracting dependencies when our language supports OO? For one thing, we can incrementally move it toward a better object design. In general, this means that you have to group related functions in classes and extract plenty of methods so that you can break apart tangled responsibilities. For more advice on this, see Chapter 20, *This Class Is Too Big and I Don't Want It to Get Any Bigger*.

Procedural code doesn't present us with as many options as object-oriented code does, but we can make headway in procedural legacy code. The particular seams that a procedural language presents critically affect the ease of the work. If the procedural language you are using has an object-oriented successor, I recommend moving toward it. *Object seams (40)* are good for far more than getting tests in place. Link and preprocessing seams are great for getting code under test, but they really don't do much to improve design beyond that.

**It's All Object Oriented**
