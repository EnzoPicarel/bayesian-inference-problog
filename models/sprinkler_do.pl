% Sprinkler-on intervention

0.5::cloudy.

0.8::rain :- cloudy.
0.2::rain :- \+cloudy.

sprinkler.

0.99::wetgrass :- sprinkler, rain.
0.90::wetgrass :- sprinkler, \+rain.
0.90::wetgrass :- \+sprinkler, rain.

0.70::greenergrass :- wetgrass.
0.05::greenergrass :- \+wetgrass.

query(cloudy).
query(rain).
query(greenergrass).
