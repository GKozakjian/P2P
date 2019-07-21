# P2P

## Introduction
The `Client-Server` centralized architecture model worked for the past 50 years and provided the backbone of all the amazing services that
humans consumed. However, this architecture model is not holding still today, since the number of users being humans or devices has 
grown exponentially. This resulted in the melting of our best invented architecture models, which raised the danger flag for the 
technologists in order to come up with a new model that will, for some period of time, stand still against the needs of this new 
technological era.


Hence, The `Peer-To-Peer` architecture model emerged, bringing with it new architectural, design and implementational challenges with 
the promise of addressing the main limitations and weaknesses of the centralized architecture model. The main challenges in any P2P network
are the number of hopes that any peer needs to take to reach some other destination peer, and the routing table that a peer joining the 
P2P network has to maintain at each time in orde to be able to reach other peers. This goal is to create a P2P overlay network
where a middle point solution for the two challenges is found: `(1) any peer can reach other in limited number of hopes`, `(
2) peers don't need to store the full P2P network in the routing table, which may be a big problem, because at any time, there can be 
millions of peers in the network` .


This new model builds its pillerson the notion that today end devices including personal computers and IoT devices are no longer thin, 
low end clients, but `poweful computational devices` that can provide as well as consume services. So the basic idea of the P2P architecture is for the nodes to act 
as both clients and servers, and they will be known as peers, since they are equal in their functionalities in the P2P network. 


In this P2P implementation, a `basic P2P overlay network` will be designed and implemented based on the well-known chord DHT protocol. Also, 
a new and basic P2P overlay network will be designed and implemented.


## Implementation& Code
This implementation tries to simulate an overlay P2P networkc based on the chord-protocol whcih used DHTs to build the overlay network
and add peers to the DHT. The goal is to have a O(n) peer-join chord-like network, where peers join in linear time based on total 
number of peers in the P2P network so far. 

The Code is written in Python, and includes a good documentation to build on, or translate to other programming languages.


## Read More about it
Please read more in the "Report" directory of each Part.


## Developers 
George Kozakjian
