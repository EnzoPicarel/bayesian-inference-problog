% Overlapping alarm rules for comparison with exclusive CPT rows

0.001::burglary.
0.002::earthquake.

0.95::alarm :- burglary, earthquake.
0.94::alarm :- burglary.
0.29::alarm :- earthquake.
0.001::alarm :- \+burglary, \+earthquake.

evidence(burglary, true).
evidence(earthquake, true).
query(alarm).
