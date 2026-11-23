% Sprinkler network with prior queries for all four variables

0.5::cloudy.

0.8::rain :- cloudy.
0.2::rain :- \+cloudy.

0.1::sprinkler :- cloudy.
0.5::sprinkler :- \+cloudy.

0.99::wetgrass :- sprinkler, rain.
0.90::wetgrass :- sprinkler, \+rain.
0.90::wetgrass :- \+sprinkler, rain.

query(cloudy).
query(sprinkler).
query(rain).
query(wetgrass).
