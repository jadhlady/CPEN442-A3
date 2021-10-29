# Assignment 3
[Original Webpage](https://blogs.ubc.ca/cpen442/assignments/assignment-3/)

**Type of assignment:** This is a group assignment. This assignment must be done in same groups as the term project. Only one submission per project group will be considered.

**Points:** The maximum number of points for this assignment is 50, which will be prorated accordingly after all assignments for the course are posted.

## Problem (50 points):

In this assignment, you are to develop a simple VPN that allows data to be sent from one computer to another over a protected channel. Your channel must provide mutual authentication and key establishment. It must also provide confidentiality and integrity protection using a session key computed at both ends by your key establishment protocol.

For authentication and key establishment purposes, you can assume that there is a shared secret (a string of arbitrary length) already shared/established between the computers using a separate channel (e.g., through physical paper) that is of no concern to this problem. You should not use the shared secret as the session key or send it over the wire in plain text. Instead, you should use it to bootstrap your protocol.

You must provide your own implementation of mutual authentication and key establishment, as well as the confidentiality and integrity protection. This means that you can use third-party implementations of cryptographic primitives (e.g., hash functions and encryption algorithms) and modes of operation, but you cannot use full or partial third-party implementations of protected channels (e.g., SSL, TLS).

You may choose whichever mutual authentication protocol and whichever key establishment protocol (or whichever combined protocol), stream or block ciphers and modes of operation you wish. However, you must be able to justify why you chose it and why you believe it is suitable (i.e., sufficiently secure) for implementing a VPN. To keep things simple, appropriate cryptographic algorithms include AES, DES, MD5, SHA (various versions), RSA, D-H, HMAC-MD5. When using these, ignore all padding rules (i.e., when padding is required, pad with zeros) and use the smallest moduli that will work.

Apart from your protocol design, your implementation must also be secure. It must follow the principles of designing secure systems as taught in class. Insecure implementations (e.g., not sanitizing inputs) will result in reduced marks.

## Bonus Problem (5 Points):

Add a separate section to your report and explain: What principle(s) of designing secure systems did you follow when implementing your VPN? For each principle, you should specify what parts of code or protocol design decisions were influenced by it, and how it helped to make your implementation more secure. Generic answers (e.g., “it helped to improve confidentiality”) will not get any points.

## Implementation:

For implementation, you have two options:

    You can either use the project template hosted on Github. You will need to clone the repo, and implement your protocol by modifying the indicated parts of the code. More details are provided in the README file of the repo.
    Alternatively, you can implement everything from scratch. In that case, follow the instructions below.

## More details for implementing code from scratch:

The program you will create should be able to toggle between “client mode” and “server mode”. When set in server mode, the program waits for a TCP connection on a port that can be specified on the user interface (UI). When set in client mode, the program can initiate a TCP connection to a given host name (or IP address), on a given port. Both the target host name (IP address) and the TCP port are specified on the UI.

Your UI must allow the TA to see what data is actually sent and received over the wire at each point in the setup and communication processes. The TA should be able to step through these processes using a “Continue” button.

Your program must work properly (e.g., not crash), have reasonable platform requirements (target either Windows, macOS, or Linux)  and have a reasonably friendly user interface. Your program must have a Graphical User Interface (GUI). Command Line Interfaces (CLI) will not be accepted.

## Evaluation:

The TA will choose two machines (computers A and B), and install one instance of your program on A and another on B. Both instances will then be run, one in client mode and one in server mode, with the client connecting to the server. The TA will input shared secret value into “Shared Secret” text field on both, client and server.

On A, the TA will type some text into a “Data to be Sent” textbox and then click a “Send” button. On B, the received text will be displayed in a “Data Received” window. Similarly, it should be possible to type data at B and receive/display it at A.

By the time that the TA is ready to type into the “Data to be Sent” window, the two machines must be certain that they are talking to each other (i.e., no other machine is impersonating one of them) and must share a fresh symmetric key that no one else knows.

## Deliverables:

You are expected to write a [document](https://docs.google.com/document/d/1JRlaMrwFDA7UM4aOAmyj8gZ_BYR8wytl88DrWoQAPnk/edit) and your program. The document should include the following:

    A brief (no more than one page) but sufficient instructions for installing and executing your program installation (in case you decided not to use the project template).
    A brief description (no more than four pages) of how your VPN works. This description should include:
        A discussion of how the data is actually sent/received, and protected,
        A discussion of the mutual authentication and key establishment protocols you chose to use, why you chose them, and the computation performed by each side at each step in the protocol(s).
        A discussion of how you derive encryption and integrity-protection keys from the shared secret value.
        A short answer to the following question: if you were implementing this VPN as a real-world product for sale, what algorithms, modulus sizes, encryption key size, and integrity key size would you use?
        In case you did not use the project template: Explanation of what language the software is written in, the size of the program (lines of code; size of the executable), and the modules or major architectural components of your program (along with inputs, outputs, and functionality for each).

You should also deliver your source code. Upload your code to a hosting website (e.g., GitHub) and provide a link to your repo, in your assignment report.
