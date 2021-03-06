# Complex Multi-Loop Topology:
#        6 --- 21 --- 20 --- 3
#        |    / |    / |
#        |  14  |  15  |
#        | /    | /    |
#       19 ---- 8 --- 30
#        |    / |    / |
#        |  31  |  40  |
#        | /    | /    |
# 2 --- 11 --- 16 ---- 4

topo = { 2 : [11], 
         3 : [20], 
         4 : [30, 16],
         6 : [19, 21],
         8 : [19, 21, 31, 15, 16, 30], 
         11: [2, 19, 31, 16],
         14: [19, 21],
         15: [8, 20],
         16: [11, 4, 40, 8],
         19: [6, 11, 14, 8],
         20: [21, 15, 30, 3],
         21: [6, 14, 8, 20],
         30: [4, 20, 40, 8],
         31: [11, 8],
         40: [16, 30] }
