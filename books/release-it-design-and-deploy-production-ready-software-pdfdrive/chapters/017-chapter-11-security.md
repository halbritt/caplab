# Chapter 11: Security

Poor security practices can damage your organization and many others. Your company may suffer direct losses from fraud or extortion. That damage gets multiplied by the cost of remediation, customer compensation, regulatory fines, and lost reputation. Individuals will lose their jobs, up to and including the CEO. In 2017, the "WannaCry" ransomware affected more than 70 countries. It hit office computers, subway displays, and hospitals. The UK's National Health Service got hit particularly hard, causing X-ray sessions to be canceled, stroke centers to close, and surgeries to be postponed. It put lives at risk. <sup>2</sup>

In an epic game of one-upmanship, Equifax revealed in 2017 that 145.5 million US consumers' identities had been stolen.<sup>3</sup> And Yahoo! upped the ante in the same year when they announced that 3 billion Yahoo! accounts were stolen. We may have to discover alien life to get another order of magnitude increase.

System breaches aren't always about extracting data. Sometimes they are about implanting it, as in the case of false identities or shipping documents. That kind of effort may have contributed to California's nut theft crisis in 2013.

Security must be baked in. It's not a seasoning to sprinkle onto your system at the end. Even if your company has a dedicated security team, you aren't off the hook. You're still responsible to protect your customers and your company.

KWWZSDSR/W MX\*[6X

<sup>2.</sup> KWWSWOQGWWKIHEHROWWHIQWDUWLFOHVDQGZDOXOXOXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

<sup>3.</sup> KWW \$4VQ ZLNLSHJGZIDNRU(TXLID[0D\ -XO\B BVHFXHDLFWK\BEU

ZZZ RXWVLGHRQOLQH FRP QXW MRE

In this chapter, we'll look at the "top ten" list of application vulnerabilities, as identified by the Open Web Application Security Project (OWASP). We'll also consider data protection and integrity so that nobody loses their valuable nuts.

## The OWASP Top 10

Since 2001, the OWASP Foundation has catalogued application security incidents and vulnerabilities. Its member organizations contribute data from real attacks, so these are real lessons rather than "what-if-isms." One way that OWASP promotes application security awareness is through its OWASP Top 10 list. It represents a consensus about the most critical web application security flaws, updated every three or four years. OWASP plans to release an updated and revised list in 2017. There's still considerable debate, so the list here (based on "Release Candidate 1") may not be the one that gets adopted. For that matter, it might actually turn out to be the 2018 update. It just goes to show that you can't ever stop worrying about security.

This section will discuss the Top 10 in brief. It would still be good to go read the whole document. (Be warned, though; you may not want to put anything on the Net ever again!)

### Injection

"Injection" is an attack on a parser or interpreter that relies on user-supplied input. The classic example is SQL injection, where ordinary user input is crafted to turn one SQL statement into more than one. This is the "Little Bobby Tables" attack. In that classic XKCD strip, a school administrator asks if the character's son is really named "Robert"); DROP TABLE Students;--". While an odd moniker, Bobby Tables illustrates a typical SQL injection attack. If the application concatenates strings to make its query, then the database will see an early sequence of—to terminate whatever query the application *really* meant to do. The next thing is the destructive '523 7\$%/(statement that does the dirty deed. The double-hyphen at the end indicates a comment so the database will ignore the remainder of the input (whatever was left over from the original query).

There's no excuse for SQL injections in this day and age. It happens when code bashes strings together to make queries. But every SQL library allows the use of placeholders in query strings. Don't do this:

```
9 X O Q H U DWE BLHO M H F W L R Q
6 W U L OT JX H U \ 6 ( / ( & 7 ) 5 2 0 6 7 8 ' ( 1 7: + ( 5 ( 1 $ 0 ( \ Q D P H
```

ZZZ RZD V SJ RU

KWWESREEWDEOHVFRP

#### Instead do this:

```
% HWWHU
6WULOTJKHU\ 6(/(&7 )520678'(17:+(5(1$0( "
3UHSDUHG6WDWMP₩ĐRWQQHFWLRQ SUHSDUH6WDWHPHQW TXHU\
VWPW VHW6WUQLDBH
5HVXOWBHWXOW♥WPW H[HFXWH4XHU\
```

For more defenses, see the OWASP SQL Injection Prevention Cheat Sheet.<sup>7</sup>

Other databases are also vulnerable to injection attacks. In general, if a service builds queries by bashing strings together and any of those strings come from a user, that service is vulnerable. Keep in mind that "comes from a user" doesn't only mean the input arrived just now in an HTTP request. Data from a database may have originated from a user as well.

Another common vector for injection attacks is XML. XML may not be the cool kid on the block anymore, but there's a lot of it flying around on the wires. One XML-based attack is the XML external entity (XXE) injection. You're no doubt familiar with the built-in XML entities such as DPS and OWBut did you know that XML allows any document to define new entities? Most of the time that's just used to make shortcuts for commonly referenced tags or attributes. But documents can also specify "external entities" in the document type declaration (DTD). These act like "include" statements. An XML parser will replace occurrences of the external entity with whatever it receives from the associated URL. An "external entity" looks like this:

```
"[POYHUVLRQ HQFRGLQJ ,62 "!
'2&7<3(RR>
(/(0(17|RR$1<!
(17,7<[[H6<67(0)LOH HWFSDVM@ZG|RR!][H |RR!
```

This oddly shaped bit of XML first defines an inline DTD with the "DOCTYPE" processing instruction. The DTD defines two things. First, it says there's a tag "foo" that can contain anything. Next it defines an entity "xxe" whose contents are found by reading the URL ILOH  $\,$  HWF. SDVVZG

An attacker would submit this document to an exposed API. Obviously it's not going to do anything useful with that API. Instead the attacker hopes that the error response from the endpoint will contain the offending input, with the external entity expanded.

Most XML parsers are vulnerable to XXE injection by default. You need to configure them to be safe. No, the answer is not to parse the XML yourself

ZZZ RZDVSI RŁOGGSIKS 64/B, QMHLPWHLG OVESRQB&KHDWB6KHHW

with regular expressions! Just use the OWASP XXE Prevention Cheat Sheet to configure your parser for safety.<sup>8</sup>

SQL injection and XXE are just two of the many ways user input can corrupt your service. Format string attacks, "Eval injection," XPATH injection...Injection attacks have held their top spot on the OWASP Top 10 since 2010. Before that they were number two. Don't let yourself fall prey.

### Broken Authentication and Session Management

Authentication and session management covers a myriad of problems. It can be as obvious as putting a session ID into URLs or as subtle as storing unsalted passwords in your user database. (If your user database stores passwords without hashing or encrypting them, please stop reading now and go fix that.) Let's look at some of the top offenders.

The first place to look is with session identifiers in web front ends. At one time, it was common to use query parameters on URLs and hyperlinks to carry session IDs. Not only are those session IDs visible to every switch, router, and proxy server, they are also visible to humans. Anyone who copies and pastes a link from his or her browser inadvertently shares his or her session with email recipients and chat bots.

An electronics retailer once had a spectacular outage when a special-offer email went out to many thousands of people. The email included a deep link to the product page, including the marketer's session ID. Thousands of random users tried to use that same session. The outage resulted from each of the front-end servers trying to take exclusive ownership of that session.

The general term for this is "session hijacking" (as opposed to truck hijacking). In the retailer's case, it was self-inflicted. But any session ID in plain text can be sniffed and duplicated by an attacker. The attacker gains control of the user's session. If we're lucky, only that user is affected and may be the victim of identity theft or fraud. If we are unlucky, the hijacked session may belong to an administrator working through a web GUI.

Session hijacking is easiest when the session ID is so visible. It can still happen, however, even if the session ID is embedded in a cookie. Sessions can also be compromised via cross-site scripting (XSS) attacks, which we'll look at a little bit later.

A variant of session hijacking is "session fixation." An attacker goes to the vulnerable application and gets issued a valid session ID. The attacker then

<sup>8.</sup> KWW SZZ R Z D V SJ RLOLIGSIKS ; 0/B ([ONDHOUB (Q W L W \UBH Y, H, Q BAZL R Q B & K H D W B 6 K H H W

supplies the target with a link to the application with the attacker's session ID in it. (It may be provided to the victim several ways, including client-side script or the 0(7\$ tag to set a cookie.) The receiving application accepts the session ID from the victim and generates a response within that session. From this point on, the victim uses a session that the attacker can access at any time. The attacker expects the user to authenticate the session, which grants both the victim and the attacker full access.

If your session IDs are generated by any kind of predictable process, then your service may also be vulnerable to a "session prediction" attack. This occurs when an attacker can guess or compute a session ID for a user. Any session IDs based on the user's own data are definitely at risk. Sequential session IDs are the absolute worst choice here. Just because a session ID looks random doesn't mean that it is random, though. It may be predictable but not sequential. Any algorithm used by the server that generates the ID is probably open source and available for the attacker to download too.

OWASP suggests the following guidelines for handling session IDs:

- Use a long session ID with lots of entropy.
- Generate session IDs using a pseudorandom number generator (PRNG) with good cryptographic properties. Your language's built-in UDQ function probably isn't it.
- Protect against XSS to avoid script execution that would reveal session IDs.
- When a user authenticates, generate a fresh session ID. That way, if a session fixation attack occurs, the attacker will not have access to the user's account.
- Use the session management features built into your platform. They've already been hardened against many of these attacks. But keep up-todate with security patches and versions. Too many systems run outdated versions with known vulnerabilities.
- Use cookies to exchange session IDs. Do not accept session IDs via other mechanisms. Some servers will emit session IDs in cookies but still accept them via query parameters. Disable that.

When it comes to credentials, the most common problem is still the simplest: credentials sent in the clear. This originates from two toxic development practices. First, TLS certificates have been hard to use and easy to install incorrectly. That means most developers have never dealt with certificates or certificate chains in a production server. There are too many formats and too

many "mysterious" problems. Second, most developer tools and runtimes leave it up to the user to configure a trust store. (Be honest, could *you* write a cURL command for a TLS-secured call to a development server using a self-signed certificate?) Consequently, we often write web services that use HTTP instead of HTTPS.

Hope is in the air, though. Let's Encrypt has some promise to make certificates easier to acquire and use in web servers. Cloud and PaaS players are building certificate management and TLS into their platform.

Large enterprises may roll out a Kerberos-based system, bridged to their active directory services. If that sentence meant anything to you, then congratulations! You are in the top 10 percent of security-aware developers! (Have an almond! Unless you're allergic, of course.) For the most part, one or two people will figure out a recipe to make this work in your world, and then everyone else will copy and paste the code that makes the security infrastructure happy.

"Authentication" means we verify the identity of the caller. Is the caller who he or she claims to be? That may be a person in the case of a user-facing application. For an external API, it may be another company. Internal services need to authenticate their callers. In the old world, we used the "pie crust" defense. You had to authenticate to cross a boundary, but services inside the "pie" could call each other freely. Boundaries are much less clear today, so we need to think about authentication everywhere. Don't trust calls based on their originating IP addresses, because those can be faked.

Let's start with the basics. Here are some do's and don'ts:

- Don't keep passwords in your database.
- Never email a password to a user as part of a "forgotten password" process.
- Do apply a strong hash algorithm to passwords. Use "salt," which is some random data added to the password to make dictionary attacks harder.
- Do allow users to enter overly long passwords.
- Do allow users to paste passwords into GUIs.
- Do plan on rehashing passwords at some point in the future. We have to keep increasing the strength of our hash algorithms. Make sure you can change the salt, too.
- Don't allow attackers to make unlimited authentication attempts.

One side note about the number of authentication attempts you allow: people instinctively want to limit this to three attempts before locking an account.

The trouble is that most of us have multiple devices with applications that can automatically retry authentication several times. It's not very friendly to lock out users because they changed their password via the web interface but your mobile app kept trying to log them in with an old password.

Authentication may be first-party or third-party. In first-party authentication, the authority (us) keeps a database of credentials. The principal (the caller who claims to have an identity) provides credentials that the authority checks against its database. If the credentials match, the authority accepts that identity for the principal.

In third-party authentication, the principal presents a "proof" that it acquired from some other authority. Our system can check that proof to verify that it could only have been issued by the authority. Of course, this relies on some exchange of secret information in advance that we can use to confirm the proof. For example, our service may have the public half of a keypair that the authority uses to sign its proofs. A second but equally important thing to check is that the proof wasn't intercepted and used by an attacker. Kerberos, NTLM, and OAuth are all third-party authentication systems.

### Cross-Site Scripting

Cross-site scripting (XSS) happens when a service renders a user's input directly into HTML without applying input escaping. It's related to injection attacks. Both take advantage of the fact that we represent structured data as sequences of ordinary characters by providing premature delimiters and unwanted commands. For example, suppose we have a service that echoes back the user's "search" parameter in the results page. It has some server-side rendering code like this:

```
'RO WGRWKLV
6WULOTXHU\%R[LQSXW\SH WH[WOOXH
UHTXH¥MWW3DUDPHWHHDWLFK ;66KDSSHÖNYUH
```

An attacker can run a search with this nasty little query string (wrapped to fit the page):

```
! VFULSOMREXPHOW ORFIDWAWBO ZZZ H[DPSOH FRP FDSWXUH"LG GREXPHOW FRWENLIEW!
```

After the server inserts that string, the resulting HTML looks like this (wrapped to fit the page):

```
LQSXW\SHWH[WYDOXH!
VFULSOWRFXPHQW ORFIDWWWBQ ZZZ H[DPSOH FRP FDSWXUH*LGGRFXPHQW FRWFRLW-6W!!
```

This is malformed HTML to be sure, but browsers are pretty lenient about that. When the client's browser hits the script tag in the middle, it makes a request over to ZZZ ḤDPSOH khth the user's cookie as a parameter, allowing the attacker to hijack the user's session.

This isn't just a problem with server-side rendering. Lots of front-end apps make service calls and put the content straight into the DOM without escaping. These clients are just as vulnerable to XSS.

A whole class of injection attacks aim at administrator or customer service GUIs. These attacks work through the browser. For example, a customer may fill out a "contact us" form with a bunch of hostile data with embedded JavaScript. When a high-authorization user pulls up that record, the Java-Script executes on the administrator's browser. It might be hours, days, or weeks later. Some injection attacks have targeted log viewers. These work by putting hostile data in log strings. If the log viewer doesn't apply good HTML escaping, it will execute code with the privileges of the user running the viewer (often an admin).

Automated scanning tools will find XSS flaws quickly. They submit forms with quasi-random data to see when it gets echoed to an output page without escaping. Expect an exploit within milliseconds.

XSS can be used to conscript your system into attacking others. The attacker injects script into your system, which then executes on your users' browsers to attack a different party entirely. Herd immunity is vital to stopping XSS.

The bottom line is this: never trust input. Scrub it on the way in and escape it on the way out. Java developers should use OWASP's Java Encoder Project.<sup>9</sup> And everyone should read the XSS Prevention Cheat Sheet. <sup>10</sup>

A secondary lesson is this: don't build structured data by smashing strings together. Look for an HTML generation library that automatically escapes *everything* and forces you to ask nicely to do unsafe things.

### Broken Access Control

Broken access control refers to application problems that allow attackers to access data they shouldn't. This can include other users' data or system-level data like password files.

<sup>9.</sup> ZZZ RZD V SI RLOQG SIK S 2\$:63 B - D Y D B (Q FUR GII HI UF 19/3

<sup>10.</sup> ZZZ RZD V SI RŁOUG SIKS ; 6 6 BR WŁUB 6 L W HB 6 F UŁYSHWOLWOLI REC28 & K HD W B 6 K HH W

One of the common forms of broken access control is "direct object access." This happens when a URL includes something like a database ID as a query parameter. An attacker sees the ID in the query parameter and starts probing for other numbers. Since database IDs are assigned sequentially, it's easy for an attacker to scan for other interesting data. For example, suppose a warehouse management system uses the customer's ID to display a report of shipments. An attacker can start trying other customer IDs to see what goods are en route.

The solution has two parts: reducing the value of URL probing and checking authorization to objects in the first place.

### Deter URL Probing

We can make it harder to find interesting values. First, don't use database IDs in URLs. We can generate unique but non-sequential identifiers to use in URLs. In that case, an attacker can probe the ID space but will have low odds of finding interesting results.

Another approach is to use a generic URL that is session-sensitive. For instance, instead of KWWS QUESOH FRP XVHUUSE KWWS QUESOH FRP XVHUUSE KWWS QUESOH FRP XVHUUS PH attacker may try a lot of values in place of "me" but won't be able to see anyone else's private data.

Yet another approach is to use a session-specific mapping from random IDs to real IDs. This uses more memory, but it avoids the extra storage needed for randomized IDs. When a user makes a request for KWWS MOPSOH FRIP SUILOHV, the service looks up that number in the session-scoped map. If it exists, the service can fetch the underlying object (probably from cache). If it doesn't exist, then the service returns a 404. This prevents attackers from probing for other users' data. One downside is that the service must populate all response URLs with randomly assigned identifiers. A second downside is that links will not persist across sessions. This violates REST principles.

### Authorize Access to Objects

The underlying reason direct object access problems happen is that our services confuse "possesses a URL" with "allowed to access resource." Callers may possess many URLs from sniffing, phishing, or probing that they should not be allowed to access.

If a resource should only be sent to authorized callers, your service must make that check on every request. You may think that a URL could only be generated by a secure service, but that's never the case. URLs are just text strings, and anybody can create whatever URL they like!

There's a subtle error that often causes information leakage here. Suppose your service responds with a "404 Not Found" when a caller requests a resource that doesn't exist, but responds with a "403 Authentication Required" for a resource that exists but isn't authorized. That means your service leaks information about what resources exist or not. That may not seem like much, but it could be. Suppose the resources in question are customers by ID. Then an attacker could find out how many customers you have by making requests for customer 1, 2, 3, and so on. When the response changes from 403 to 404, they've found the size of your customer base. It might be very interesting to see that number change from month to month.

Or, an attacker could probe your login service with different email addresses harvested from the web. A 403 means "yes, that's my customer," where a 404 means "never heard of them."

Rule of thumb: If a caller is not authorized to see the contents of a resource, it should be as if the resource doesn't even exist.

Another kind of broken access control leads to directory traversal attacks. This happens whenever a caller provides input that's used to construct a file name. The caller supplies a parameter with one or more—strings (for Unix systems) or—(for Windows.) The service concatenates that with some base directory and ends up opening a file outside the expected location (string concatenation again!). With just a few requests, a caller can find a way to the password file on the host.

Even worse, when a request involves a file upload, the caller can overwrite any file the service is allowed to modify. (Yet another reason to *not* run as root!) Your application might think it's saving the user's profile picture, but it actually writes a malicious executable into the filesystem.

The only safe way to handle file uploads is to treat the client's filename as an arbitrary string to store in a database field. Don't build a path from the filename in the request. Generate a unique, random key for the real filename and link it to the user-specified name in the database. That way, the names in the filesystem stay under your service's control and don't include external input as any part.

Directory traversals can be subtle and hard to scrub out of input. The entry for Common Weakness Enumeration 22 shows several failed attempts to protect against traversal. Fortunately, it also shows how to prevent it.

<sup>11.</sup> KWWRSZH PHWRLUGDWD GHILQLWLRQV KWPO

### Security Misconfiguration

How many times have you typed "admin' as a login? It may seem ridiculous, but default passwords are a serious problem. Attackers have entered applications, network devices, and databases by using the default, out-of-the-box admin login. This is just one kind of security misconfiguration.

Security misconfiguration usually takes the form of omission. Servers enable unneeded features by default. We forget (or don't know) to disable them and thereby leave an unconfigured, unmonitored entry point open.

Admin consoles are a common source of problems. Seek them out and force good password hygiene. Never allow a default password on a production server. Cast a wary eye on containers, especially if you're building on an image that includes applications. Base OS images shouldn't have servers running, but common bundles include servers like Redis, Mongo, Postgres, ZooKeeper, and so on. These have their own authentication mechanisms and default admin passwords.

The whole world got a vivid wake-up call in the early days of 2017, when somewhere north of 20,000 MongoDB installations were taken hostage. The databases had default credentials and were exposed to the Internet. Attackers took the data, wiped the database out, and replaced it with a demand for bitcoin. (Note that MongoDB, the company, has a thorough guide for securing the database; 12 it's unfortunate that the default installation at the time was not secured.) Remember the install script is the first step in installation, not the last.

Another common security misconfiguration relates to servers listening too broadly. We first encountered this in *Programming for Multiple Networks*, on page 145. You can improve information security right away by splitting internal traffic onto its own NIC separate from public-facing traffic. Security professionals talk about the "attack surface," meaning the sum of all IP addresses, ports, and protocols reachable to attackers. Split those admin interfaces to reduce the attack surface. This is especially easy in cloud environments, where another interface is just an API call away.

Some servers come with sample applications that have shockingly poor security protection and may be ages out of date. There's never a reason to put a sample application into production. Nevertheless, it happens. Once there, the sample apps are *never* patched. They're part of the exposed attack surface. Sample apps are well known and easy to find in the wild. It's easy to build an attack for flaws in those sample apps.

<sup>12.</sup> ZZZ PROJRGE FRP EORJ STOWWILKERD WOROLFLRXV DWW OFFXIONDWOODW UDQVRPV

Finally, make sure every administrator uses a personal account, not a group account. While you're at it, go ahead and add some logging to those administrative and internal calls. If nothing else, you'll be one of the few people to witness a smiling auditor.

### Sensitive Data Exposure

This is the big one. Credit cards (Equifax!). Medical records. Insurance files. Purchasing data. Emails (Yahoo!). All the valuable things people can steal from you or use against you. The stuff that makes for headlines and subpoenas. That's what OWASP means by "sensitive data." The "exposure" part is probably obvious.

Exposure doesn't mean that a hacker broke your crypto. Hackers don't attack your strong points. They look for cracks in your shell. It can be as simple as an employee's stolen laptop with a database extract in a spreadsheet. Maybe your system uses TLS at the edge but REST over plain HTTP internally—another "pie crust." An attacker can sniff the network to collect credentials and payload data.

Here are some guidelines to help you avoid headlines:

- Don't store sensitive information that you don't need. In retail, use a credit card tokenizer from your payment provider.
- Use HTTP Strict Transport Security. This is a step beyond HTTPS-first. It prevents clients from negotiating their way to insecure protocols.
- Stop using SHA-1. Just stop. It's no longer adequate.
- Never store passwords in plain text. Read OWASP's Password Storage Cheat Sheet for guidance on hash algorithms and good salting.<sup>13</sup>
- Make sure sensitive data is encrypted in the database. It's a pain, but necessary.
- Decrypt data based on the user's authorization, not the server's.

If you are in the AWS cloud, consider using AWS Key Management Service (KMS). AMS creates and manages master keys. Applications can request data encryption keys, which they use to encrypt or decrypt data. The data encryption keys are themselves encrypted with a key encryption key. It gets kind of recursive, but the point is that you don't leave decryption keys laying

<sup>13.</sup> ZZZ RZD V SI RELOGO SIK SD3V V ZORBJ6 W R U D J H B & K H D W B 6 K H H W

<sup>14.</sup> KWWGSREV DZV DPD]RQ FRP NPV ODWIHGYNV FGR-CMAHGSPNSM KWPO

around where an attacker could retrieve them. If you're running on your own premises, consider HashiCorp's Vault. <sup>15</sup> It manages "secrets" a bit more broadly than KMS.

Regardless of which tool you pick, don't try to hold it at arm's length. Use the tool fully as part of a holistic secure development process.

### Insufficient Attack Protection

Consider a production service protected by a firewall. It should be safe from attackers. Sadly, that is not the case. We must always assume that attackers have unlimited access to other machines behind the firewall. They can make arbitrary requests. That includes well-formed requests for unauthorized data, and it includes malformed requests aimed at compromising the service itself.

Services do not typically track illegitimate requests by their origin. They do not block callers that issue too many bad requests. That allows an attacking program to keep making calls, either to probe for weaknesses or extract data.

Your service probably detects bad input and rejects it like a closed pistachio. That leaves the attacker free to keep issuing requests. The service should log bad requests by source principal. Log collection tools, which we covered in *Logs and Stats*, on page 204, can collate those requests to find patterns.

It's probably not feasible to give every service a whitelist of allowed consumers. After all, we want consumers to be deployed on their own, without centralized control. We can, however, give a service a blacklist of disallowed consumers. This may be stored as a certificate revocation list (CRL) or by principal name in your authentication system (Active Directory name, for example).

"API Gateways" are a useful defense here. An API gateway can block callers by their API key. It can also throttle their request rate. Normally, this helps preserve capacity. In the case of an attack, it slows the rate of data compromise, thereby limiting the damage.

Network devices may help if your service is in a data center under your control. Application-layer firewalls (also called "layer 7" firewalls) can detect and block suspicious calls. They can also be loaded with signatures of well-known attacks to block probes.

<sup>15.</sup> ZZZ YD X ORWISHUF W LR

### Cross-Site Request Forgery

Cross-site request forgery (CSRF) used to be a bigger issue than it is now. These days, most web frameworks automatically include defenses against it. But a lot of old applications are out there. Some are vulnerable targets, while others can be used as stooges.

A CSRF attack starts on another site. An attacker uses a web page with JavaScript, CSS, or HTML that includes a link to your system. When the hapless user's browser accesses your system, your system thinks it's a valid request from that user. Boom, your user is roasted. Note that the user's browser will send all the usual cookies, including session cookies. Just because the user appears to have a logged-in session doesn't mean the request is intentional.

The first thing to do is make sure your site can't be used to launch CSRF attacks. XSS is a common trap. If the attacker can supply input that you display without proper escaping, the attacker can trick people into viewing it through your site. Don't be a part of it!

Second, make sure that requests with side effects—such as password changes, mailing address updates, or purchases—use anti-CSRF tokens. These are extra fields containing random data that your system emits when rendering a form. Your code expects get the same token back when the user submits the form. If the token is missing or doesn't match, it means the request is bogus. Most frameworks today do this for you, but you might have to enable CSRF protection in your service's configuration.

You can also tighten up your cookie policy with the relatively new "SameSite" attribute. <sup>16</sup> A cookie with that attribute looks like this in a response header:

6HW & RRN&H G G H DDG 6DPH6LWH VWULFW

The "SameSite" attribute causes the browser to send the cookie *only* if the document's origin is the same as the target's origin. That includes subdomains, so same-site cookies for "account.example.com" would not be sent to "images.example.com." Not every browser supports same-site cookies as of June 2017. The Chrome family supports it on desktop and mobile. Opera does as well, but Firefox, Internet Explorer, and Edge do not. Keep an eye on the Can I Use... website to see when your supported browsers have this feature.<sup>17</sup>

<sup>16.</sup> KWW SWARO VRJUHKWIPO WG UZDIVW ILU VEWIRSNDLUIWAY

<sup>17.</sup> KWWBDQLXVH FRP IHDW VDPH VLWH FRRNLH DWWULEXWH

Same-site cookies are not a zero-cost feature. In particular, they may require you to change your session management approach. A top-level navigation request (an in-bound link from another system) on a new page is *not* a same-site request when the cookie says "strict."

The RFC recommends using a pair of cookies:

- A session "read" cookie: not same-site. Allows HTTP GET requests.
- A session "write" cookie: same-site strict. Required for state-changing requests.

As with the other Top 10 items, OWASP has a cheat sheet for CSRF prevention. 18

### Using Components with Known Vulnerabilities

Is there anyone out there running Struts 2 between version 2.3.0 and 2.3.32 or 2.5.x before 2.5.10.1? Beware of an attack that allows remote code execution. <sup>19</sup> That's what got Equifax. Once you know that vulnerability exists, it should just be a matter of updating to a patched version and redeploying. But who keeps track of the patch level of all their dependencies? Most developers don't even know what all is in their dependency tree.

Sadly, most successful attacks are not the exciting "zero day, rush to patch before they get it" kind of thing that makes those cringe-worthy scenes in big budget thrillers. Most attacks are mundane. A workbench-style tool probes IP addresses for hundreds of vulnerabilities, some of them truly ancient. The attacker may just collect an inventory of targets and weaknesses, or they may run automated exploits to add the machine to a growing collection of compromised minions.

It's important to keep applications up-to-date. That means coming to grips with your dependency tree. Use your build tool to extract a report of *all* the artifacts that went into your build. (Don't forget about plugins to the build tool itself! They can also have vulnerabilities.) Keep that report someplace and check it once a week against the latest CVEs. Better yet, use a build tool plugin that automatically breaks the build if there's a CVE against any of your dependencies.<sup>20</sup> If that's too much work, you can sign up for a commercial service like VersionEye.<sup>21</sup>

<sup>18.</sup> ZZZ RZDVSJRLQGBKS RLWV 6LWTFXB45VPWDB)U\B &659HBY3HQWLRQB&KHDWB6KHHW

<sup>19.</sup> KWWSQWG QLVW JRY YXOQ GHWDLO &9(

<sup>20.</sup> KWW SZY Z RZD V SJ RLOQ [G SIKS 25:63 B 'H SHQ GHQ F \ B & KHFN

<sup>21.</sup> KWWSZZYHUVLRQH\H FRP

Many vulnerabilities never get published, though. Some are discussed on the project's mailing list or issue tracker but do not get CVEs, so you should keep an eye on those as well.

### Underprotected APIs

The final entry in the Top 10 is also a newcomer to the list. The rise of REST and rich clients elevated APIs to a primary architectural concern. For some companies, the API is their entire product. It's essential to make sure that APIs are not misused.

Security scanners have been slow to tackle APIs. In part, this is because there's no standard metadata description about how an API should work. That makes it hard for a testing tool to glean any information about it. After all, if you can't tell how it should work, how do you know when it's broken?

To make things even harder, APIs are meant to be used by programs. Well, attack tools are also programs. If an attack tool presents the right credentials and access tokens, it's indistinguishable from a legitimate user.

There are several keys to defense.

The first is a kind of bulkheading (see *Bulkheads*, on page 98). If one customer's credentials are stolen, that's bad. If the attacker can use those to get other customers' data, that's catastrophic. APIs must ensure that malicious requests cannot access data the original user would not be able to see. That sounds easy, but it's trickier than you might think. For instance, your API absolutely cannot use hyperlinks as a security measure. In other words, your API may generate a link to a resource as a way to say "access is granted" to that resource. But nothing says the client is only going to hit that link. It may issue 10,000 requests to figure out your URL templating pattern and then generate requests for every possible user ID. The upshot is that the API has to authorize the link on the way out and then reauthorize the request that comes back in.

Second, your API should use the most secure means available to communicate. For public-facing APIs this means TLS. Be sure to configure it to reject protocol downgrades. Also keep your root certificate authority (CA) files up-to-date. Bad actors compromise certificates way more often than you might think. For business-to-business APIs, you might want to use bidirectional certificates so each end verifies the other.

Third, whatever data parser you use—be it JSON, YAML, XML, Transit, EDN, Avro, Protobufs, or Morse code—make sure the parser is hardened against

malicious input. Use a generative testing library to feed it tons and tons of bogus input to make sure it rejects the input or fails in a safe way. Fuzztesting APIs is especially important because, by their nature, they respond as quickly as possible to as many requests as possible. That makes them savory targets for automated crackers.

## The Principle of Least Privilege

The principle of "least privilege" mandates that a process should have the lowest level of privilege needed to accomplish its task. This never includes running as root (UNIX/Linux) or administrator (Windows). Anything application services need to do, they should do as nonadministrative users.

I've seen Windows servers left logged in as administrator for weeks at a time—with remote desktop access—because some ancient piece of vendor software required it. (This particular package also was not able to run as a Windows service, so it was essentially just a Windows desktop application left running for a long time. That is *not* production ready!)

Software that runs as root is automatically a target. Any vulnerability in root-level software automatically becomes a critical issue. Once an attacker has cracked the shell to get root access, the only way to be sure the server is safe is to reformat and reinstall.

To further contain vulnerabilities, each major application should have its own user. The "Apache" user shouldn't have any access to the "Postgres" user, for example.

Opening a socket on a port below 1024 is the only thing that a UNIX application might require root privilege for. Web servers often want to open port 80 by default. But a web server sitting behind a load balancer (see *Load Balancing*, on page 177) can use any port.

## Containers and Least Privilege

Containers provide a nice degree of isolation from each other. Instead of creating multiple application-specific users on the host operating system, you can package each application into its own container. Then the host kernel will keep the containerized applications out of each others' filesystems. That's helpful for reducing the containers' level of privilege.

Be careful, though. People often start with a container image that includes most of an operating system. Some containerized applications run a whole init system inside the container, allowing multiple shells and processes. At that point, the container has its own fairly large attack surface. It must be secured. Sadly, patch management tools don't know how to deal with containers right now. As a result, a containerized application may still have operating system vulnerabilities that IT patched days or weeks ago.

The solution is to treat container images as perishable goods. You need an automated build process that creates new images from an upstream base and your local application code. Ideally this comes from your continuous integration pipeline. Be sure to configure timed builds for any application that isn't still under active development, though.

## Configured Passwords

Passwords are the Brazil nut of application security; every mix has them, but nobody wants to deal with them. There's obviously no way that somebody can interactively key in passwords every time an application server starts up. Therefore, database passwords and credentials needed to authenticate to other systems must be configured in persistent files somewhere.

As soon as a password is in a text file, it is vulnerable. Any password that grants access to a database with customer information is worth thousands of dollars to an attacker and could cost the company thousands in bad publicity or extortion. These passwords must be protected with the highest level of security achievable.

At the absolute minimum, passwords to production databases should be kept separate from any other configuration files. They should especially be kept out of the installation directory for the software. (I've seen operations zip up the entire installation folder and ship it back to development for analysis, for example, during a support incident.) Files containing passwords should be made readable only to the owner, which should be the application user. If the application is written in a language that can execute privilege separation, then it's reasonable to have the application read the password files before downgrading its privileges. In that case, the password files can be owned by root.

Password vaulting keeps passwords in encrypted files, which reduces the security problem to that of securing the single encryption key rather than securing multiple text files. This can assist in securing the passwords, but it is not, by itself, a complete solution. Because it's easy to inadvertently change or overwrite file permissions, intrusion detection software such as Tripwire should be employed to monitor permissions on those vital files.<sup>22</sup>

<sup>22.</sup> ZZZ WULBZRRP

AWS Key Management Service (KMS) is useful here. With KMS, applications use API calls to acquire decryption keys. That way the encrypted data (the database passwords) don't sit in the same storage as the decryption keys! If you use Vault, then it holds the database credentials directly in the vault.

In every case, it's important to expunge the key from memory as soon as possible. If the application keeps the keys or passwords in memory, then memory dumps will also contain them. For UNIX systems, core files are just memory dumps of the application. An attacker that can provoke a core dump can get the passwords. It's best to disable core dumps on production applications. For Windows systems, the "blue screen of death" indicates a kernel error, with an accompanying memory dump. This dump file can be analyzed with Microsoft kernel debugging tools; and depending on the configuration of the server, it can contain a copy of the entire physical memory of the machine—passwords and all.

## Security as an Ongoing Process

Frameworks can't protect you from the Top 10. Neither can a one-time review by your company's AppSec team. Security is an ongoing activity. It must be part of your system's architecture: crucial decisions about encrypted communication, encryption at rest, authentication, and authorization are all crosscutting concerns that affect your entire system.

New attacks emerge all the time. You must have a process to discover attacks (hopefully before they are used on you) and remediate your system quickly.

This is doubly true when you deploy technology that hasn't been battle-hardened. New technology with new APIs will have vulnerabilities. That doesn't mean you should give up the advantages it offers. It does mean that you need to be vigilant about patching it. Make sure you can redeploy your servers on a moment's notice.

## Wrapping Up

Application security affects life and livelihood. It's another area where we need to consider both the component-level behavior and the behavior of the system as a whole. Two secure components don't necessarily mix to make a secure system.

The most common target of value is user data, especially credit card information. Even if you don't handle credit cards, you might not be off the hook. Industrial espionage is real and it can sometimes look as harmless as the location of a shipment of tasty pecans.

Beware the pie crust defense. Internal APIs need to be protected with good authentication and authorization. It's also vital to encrypt data on the wire, even inside an organization. There's no such thing as a secure perimeter today. Bitter experience shows that breaches can be present for a long time before detection, more than enough for an attacker to devise recipes to get at that sweet user data.

Full treatment of application security is way beyond the scope of this book. The topics covered in this chapter earned their place by sitting in the intersection of software architecture, operations, and security. Consider this a starting point in a journey. Follow the trail from here into the rich and scary world of CVEs, <sup>23</sup> CWEs, <sup>24</sup> and CERTs. <sup>25</sup>

This finishes our slow zoom out from the physical substrate—copper, silicon, and iron oxide—all the way to systemic considerations. In the next part, we will look at the moment of truth: deployment!

<sup>23.</sup> KWWFSYHPHLWALU

<sup>24.</sup> KWW 57 H PHWRULQGNWPO

<sup>25.</sup> ZZZ FHUW RU
