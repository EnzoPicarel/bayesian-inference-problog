% Noisy-OR fever model

0.30::cold.
0.10::flu.
0.01::malaria.

0.40::fever :- cold.
0.80::fever :- flu.
0.90::fever :- malaria.

query(fever).
