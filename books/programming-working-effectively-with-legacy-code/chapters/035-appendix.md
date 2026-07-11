<span id="page-437-2"></span>
<span id="page-437-1"></span>
<span id="page-437-0"></span>
# Appendix

## Refactoring

**Refactoring**

Refactoring is a core technique for improving code. The canonical reference for refactoring is Martin Fowler's book *Refactoring: Improving the Design of Existing Code* (Addison-Wesley, 1999). I refer you to that book for more information about the kind of refactoring you can do when you have tests in place in code.

In this chapter, I describe one key refactoring: *Extract Method*. It should give you a flavor of the mechanics involved in refactoring with tests.

## Extract Method

Of all refactorings, *Extract Method* is perhaps the most useful. The idea behind *Extract Method* is that we can systematically break up large existing methods into smaller ones. When we do this, we make our code easier to understand. In addition, we can often reuse the pieces and avoid duplicating logic in other areas of our system.

In poorly maintained code bases, methods tend to grow larger. People add logic to existing methods, and they just continue to grow. As this happens, methods can end up doing two or three different distinct things for their callers. In pathological cases, they can end up doing tens or hundreds. *Extract Method* is the remedy in these cases.

When you want to extract a method, the first thing that you need is a set of tests. If you have tests that thoroughly exercise a method, you can extract methods from it using these steps:

- 1. Identify the code you want to extract, and comment it out.
- 2. Think of a name for the new method and create it as an empty method.
- 3. Place a call to the new method in the old method.
- 4. Copy the code that you want to extract into the new method

![](../assets/_page_438_Picture_1.jpeg)

- 5. *Lean On the Compiler (315)* to find out what parameters you'll have to pass and what values you'll have to return.
- 6. Adjust the method declaration to accommodate the parameters and return value (if any).
- 7. Run your tests.
- 8. Delete the commented-out code.

Here is a simple example in Java:

```
public class Reservation
{
 public int calculateHandlingFee(int amount) {
 int result = 0;
 if (amount < 100) {
 result += getBaseFee(amount);
 }
 else {
 result += (amount * PREMIUM_RATE_ADJ) + SURCHARGE;
 }
 return result;
 }
 ...
}
```

The logic in the else-statement calculates the handling fee for premium reservations. We need to use that logic someplace else in our system. Instead of duplicating the code, we can extract it from here and then use it in the other place.

Here is the first step:

```
public class Reservation
{
 public int calculateHandlingFee(int amount) {
 int result = 0;
 if (amount < 100) {
 result += getBaseFee(amount);
 }
 else {
 // result += (amount * PREMIUM_RATE_ADJ) + SURCHARGE;
 }
 return result;
 }
 ...
}
```

**Extract Method**

We want to call the new method getPremiumFee, so we add the new method and its call:

```
public class Reservation
 public int calculateHandlingFee(int amount) {
 int result = 0;
 if (amount < 100) {
 result += getBaseFee(amount);
 }
 else {
 // result += (amount * PREMIUM_RATE_ADJ) + SURCHARGE;
 result += getPremiumFee();
 }
 return result;
 }
 int getPremiumFee() {
 }
 ...
  Next we copy the old code into the new method and see if it compiles:
public class Reservation
 public int calculateHandlingFee(int amount) {
 int result = 0;
 if (amount < 100) {
 result += getBaseFee(amount);
 }
 else {
 // result += (amount * PREMIUM_RATE_ADJ) + SURCHARGE;
 result += getPremiumFee();
 }
 return result;
 }
 int getPremiumFee() {
 result += (amount * PREMIUM_RATE_ADJ) + SURCHARGE; 
 }
 ...
```

It doesn't. The code uses variables named result and amount that aren't declared. Because we are computing only a portion of the result, we can just return what we compute. We can also get hold of the amount if we make it a parameter to the method and add it to the call:

**Extract Method**

### **418** REFACTORING

```
Extract Method
```

```
public class Reservation
{
 public int calculateHandlingFee(int amount) {
 int result = 0;
 if (amount < 100) {
 result += getBaseFee(amount);
 }
 else {
 // result += (amount * PREMIUM_RATE_ADJ) + SURCHARGE;
 result += getPremiumFee(amount);
 }
 return result;
 }
 int getPremiumFee(int amount) {
 return (amount * PREMIUM_RATE_ADJ) + SURCHARGE; 
 }
 ...
}
```

Now we can run our tests and see if they still work. If they do, we can go back and get rid of the commented code:

```
public class Reservation
{
 public int calculateHandlingFee(int amount) {
 int result = 0;
 if (amount < 100) {
 result += getBaseFee(amount);
 }
 else {
 result += getPremiumFee(amount);
 }
 return result;
 }
 int getPremiumFee(int amount) {
 return (amount * PREMIUM_RATE_ADJ) + SURCHARGE; 
 }
 ...
}
```

Although it isn't strictly necessary, I like to comment out code that I am going to extract; that way, if I make a mistake and a test fails, I can easily go back to what I had, get the test to pass, and then try again.

The example I've just shown is just one way of doing *Extract Method*. When you have tests, it is a relatively simple and safe operation. If you have a

![](../assets/_page_441_Picture_1.jpeg)

<span id="page-441-0"></span>refactoring tool, it is even easier. All you have to do is select a portion of a method and make a menu selection. The tool checks to see if that code can be extracted as a method and prompts you for the new method's name.

*Extract Method* is a core technique for working with legacy code. You can use it to extract duplication, separate responsibilities, and break down long methods.

**Extract Method**

![](../assets/_page_442_Picture_0.jpeg)

#### Glossary
