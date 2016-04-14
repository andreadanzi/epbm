#!/bin/sh
rm -f *.log
mkdir ../data/MDW029_S_E_05/out
python main.py -c MDW029_S_E_05
python process_calc.py -a -c MDW029_S_E_05 -n 1 -t c
python export_building_data.py -a -c MDW029_S_E_05 -o buildings_export_data.csv -f buildings_out_settings.csv -s edifici.shp
python plot_data_ccg.py -c MDW029_S_E_05 -a
cp *.log* ../data/MDW029_S_E_05/out