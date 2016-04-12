#!/bin/sh
rm *.log
# 5%
mkdir ../data/MDW029_S_E_05/out
cp ../data/MDW029_S_E_05/in/reference_strata-05.csv ../data/MDW029_S_E_05/in/reference_strata.csv
python main.py -c MDW029_S_E_05
python process_calc.py -a -c MDW029_S_E_05
python export_building_data.py -a -c MDW029_S_E_05 -o buildings_export_data-05.csv -f buildings_out_settings.csv
python plot_data_ccg.py -c MDW029_S_E_05 -a
rm -rf ../data/MDW029_S_E_05/out-05
mv ../data/MDW029_S_E_05/out ../data/MDW029_S_E_05/out-05
# 10%
mkdir ../data/MDW029_S_E_05/out
cp ../data/MDW029_S_E_05/in/reference_strata-10.csv ../data/MDW029_S_E_05/in/reference_strata.csv
python main.py -c MDW029_S_E_05
python process_calc.py -a -c MDW029_S_E_05
python export_building_data.py -a -c MDW029_S_E_05 -o buildings_export_data-10.csv -f buildings_out_settings.csv
python plot_data_ccg.py -c MDW029_S_E_05 -a
rm -rf ../data/MDW029_S_E_05/out-10
mv ../data/MDW029_S_E_05/out ../data/MDW029_S_E_05/out-10
# 15%
mkdir ../data/MDW029_S_E_05/out
cp ../data/MDW029_S_E_05/in/reference_strata-15.csv ../data/MDW029_S_E_05/in/reference_strata.csv
python main.py -c MDW029_S_E_05
python process_calc.py -a -c MDW029_S_E_05
python export_building_data.py -a -c MDW029_S_E_05 -o buildings_export_data-15.csv -f buildings_out_settings.csv
python plot_data_ccg.py -c MDW029_S_E_05 -a
rm -rf ../data/MDW029_S_E_05/out-15
mv ../data/MDW029_S_E_05/out ../data/MDW029_S_E_05/out-15
# Massimi
mkdir ../data/MDW029_S_E_05/out
cp ../data/MDW029_S_E_05/in/reference_strata-max.csv ../data/MDW029_S_E_05/in/reference_strata.csv
python main.py -c MDW029_S_E_05
python process_calc.py -a -c MDW029_S_E_05
python export_building_data.py -a -c MDW029_S_E_05 -o buildings_export_data-max.csv -f buildings_out_settings.csv
python plot_data_ccg.py -c MDW029_S_E_05 -a
rm -rf ../data/MDW029_S_E_05/out-max
mv ../data/MDW029_S_E_05/out ../data/MDW029_S_E_05/out-max
# Minimi
mkdir ../data/MDW029_S_E_05/out
cp ../data/MDW029_S_E_05/in/reference_strata-min.csv ../data/MDW029_S_E_05/in/reference_strata.csv
python main.py -c MDW029_S_E_05
python process_calc.py -a -c MDW029_S_E_05
python export_building_data.py -a -c MDW029_S_E_05 -o buildings_export_data-min.csv -f buildings_out_settings.csv
python plot_data_ccg.py -c MDW029_S_E_05 -a
rm -rf ../data/MDW029_S_E_05/out-min
mv ../data/MDW029_S_E_05/out ../data/MDW029_S_E_05/out-min
# Medi
mkdir ../data/MDW029_S_E_05/out
cp ../data/MDW029_S_E_05/in/reference_strata-medi.csv ../data/MDW029_S_E_05/in/reference_strata.csv
python main.py -c MDW029_S_E_05
python process_calc.py -a -c MDW029_S_E_05
python export_building_data.py -a -c MDW029_S_E_05 -o buildings_export_data-medi.csv -f buildings_out_settings.csv
python plot_data_ccg.py -c MDW029_S_E_05 -a
rm -rf ../data/MDW029_S_E_05/out-medi
mv ../data/MDW029_S_E_05/out ../data/MDW029_S_E_05/out-medi