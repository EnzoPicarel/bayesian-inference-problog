% Burglary alarm Bayesian network

0.001::burglary.
0.002::earthquake.

0.95::alarm :- burglary, earthquake.
0.94::alarm :- burglary, \+earthquake.
0.29::alarm :- \+burglary, earthquake.
0.001::alarm :- \+burglary, \+earthquake.

0.90::johncalls :- alarm.
0.05::johncalls :- \+alarm.
0.70::marycalls :- alarm.
0.01::marycalls :- \+alarm.

world_jmanbne :- johncalls, marycalls, alarm, \+burglary, \+earthquake.

evidence(johncalls, true).
evidence(marycalls, true).
query(burglary).
query(earthquake).
