% Exact posteriors for the sprinkler network

0.5::cloudy.

0.8::rain :- cloudy.
0.2::rain :- \+cloudy.

0.1::sprinkler :- cloudy.
0.5::sprinkler :- \+cloudy.

0.99::wetgrass :- sprinkler, rain.
0.90::wetgrass :- sprinkler, \+rain.
0.90::wetgrass :- \+sprinkler, rain.

rain_with_sprinkler_off :- rain, \+sprinkler.

% Each subquery conditions the same rain model on its own evidence set.
% The result atoms expose those probabilities in the normal ProbLog output.
P::rain_given_sprinkler :- subquery(rain, P, [sprinkler]).
P::rain_given_cloudy_and_wetgrass :- subquery(rain, P, [cloudy, wetgrass]).
P::rain_given_sprinkler_and_wetgrass :- subquery(rain, P, [sprinkler, wetgrass]).

query(rain_given_sprinkler).
query(rain_given_cloudy_and_wetgrass).
query(rain_given_sprinkler_and_wetgrass).
