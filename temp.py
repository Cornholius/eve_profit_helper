from collections import Counter

A = [0, 9550, 9702, 9800, 9822, 9863, 9916, 10014, 10130, 10184, 10266, 10349, 10523, 10685, 10783, 10890, 11035, 11175, 11318, 11496, 11639, 11737, 11877, 11981, 12125, 12297, 12470, 12546, 12760, 12935, 13036, 13143, 13287, 13481, 13658, 13767, 13886, 13989, 14080, 14221, 14362, 14508, 14637, 14791, 14932, 15126, 15254, 15413, 15507, 15639, 15744, 15865, 16000, 16150, 16299, 16455, 16616, 16801, 16884, 17033, 17156, 17324, 17452, 17575, 17738, 17843, 17993, 18143, 18271, 18389, 18617, 18758, 18906, 19033, 19194, 19277, 19402, 19552, 19655, 19814, 20386, 20858, 21008, 21111, 21317, 21548, 21683, 21725, 21830, 22003, 22090, 22219, 22304, 22445, 22617, 22785, 22956, 23063, 23153, 23301, 23439, 23543, 23684, 23838, 23917, 24042, 24164, 24378, 24446, 24598, 24695, 24870, 25012, 25136, 25240, 25405, 25632, 25721, 25812, 25927, 26007, 26153, 26211, 26359, 26526, 26619, 26745, 26880, 27042, 27186, 27315, 27482, 27570, 27725, 27954, 28062, 28225, 28332, 28475, 28588, 28691, 28956, 29010, 29112, 29253, 29410, 29595, 29722, 29974, 30156, 30245, 30415, 30949, 31179, 31281, 31420, 31524, 31631, 31767, 31922, 32068, 32180, 32310, 32443, 32570, 33080, 33176, 33357, 35256, 35404, 35493, 35610, 35748, 35922, 35988, 36111]
S = [0, 9550, 9702, 9800, 9822, 9863, 9916, 10014, 10130, 10184, 10266, 10349, 10523, 10685, 10783, 10890, 11035, 11175, 11318, 11496, 11639, 11737, 11877, 11981, 12125, 12297, 12470, 12546, 12760, 12935, 13036, 13143, 13287, 13481, 13658, 13767, 13886, 13989, 14080, 14221, 14362, 14508, 14637, 14791, 14932, 15126, 15254, 15413, 15507, 15639, 15744, 15865, 16000, 16150, 16299, 16455, 16616, 16801, 16884, 17033, 17156, 17324, 17452, 17575, 17738, 17843, 17993, 18143, 18271, 18389, 18617, 18758, 18906, 19033, 19194, 19277, 19402, 19552, 19655, 19814, 20386, 20858, 21008, 21111, 21317, 21548, 21683, 21725, 21830, 22003, 22090, 22219, 22304, 22445, 22617, 22785, 22956, 23063, 23153, 23301, 23439, 23543, 23684, 23838, 23917, 24042, 24164, 24378, 24446, 24598, 24695, 24870, 25012, 25136, 25240, 25405, 25632, 25721, 25812, 25927, 26007, 26153, 26211, 26359, 26526, 26619, 26745, 26880, 27042, 27186, 27315, 27482, 27570, 27725, 27954, 28062, 28225, 28332, 28475, 28588, 28691, 28956, 29010, 29112, 29253, 29410, 29595, 29722, 29974, 30156, 30245, 30415, 30949, 31179, 31281, 31420, 31524, 31631, 31767, 31922, 32068, 32180, 32310, 32443, 32570, 33080, 33176, 33357, 35256, 35404, 35493, 35610, 35748, 35922, 35988, 36111, 36111]


counter = {}

for elem in S:
    counter[elem] = counter.get(elem, 0) + 1

doubles = {element: count for element, count in counter.items() if count > 1}

print(doubles)