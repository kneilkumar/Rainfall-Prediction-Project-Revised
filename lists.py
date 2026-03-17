# first fill

rain = ['Rain', 'whit_Rainfall [mm]', 'darg_Rainfall [mm]', 'mota_Rainfall [mm]', 'alba_Rainfall [mm]']
speed = ['Speed', 'whit_Speed [m/s]', 'darg_Speed [m/s]', 'mota_Speed [m/s]', 'alba_Speed [m/s]']
pressure = ['Pressure', 'mang_Mean sea level pressure [Hpa]', 'whit_Mean sea level pressure [Hpa]', 'darg_Mean sea level pressure [Hpa]', 'mota_Mean sea level pressure [Hpa]']
mean = ['Mean Temp', 'mang_Mean Temperature [Deg C]', 'whit_Mean Temperature [Deg C]', 'darg_Mean Temperature [Deg C]', 'mota_Mean Temperature [Deg C]', 'alba_Mean Temperature [Deg C]']
humidity = ['Humidity', 'mang_Mean Relative Humidity [percent]', 'whit_Mean Relative Humidity [percent]', 'darg_Mean Relative Humidity [percent]', 'mota_Mean Relative Humidity [percent]', 'alba_Mean Relative Humidity [percent]']
direction = ['Direction', 'whit_Direction [deg T]', 'darg_Direction [deg T]', 'mota_Direction [deg T]', 'alba_Direction [deg T]']


#  Easy access to cols for subdfs

rain_raw = ['Rain', 'mang_Rainfall [mm]','whit_Rainfall [mm]', 'darg_Rainfall [mm]', 'mota_Rainfall [mm]', 'alba_Rainfall [mm]']
rain_lag = ['Rain', 'mang_rain_event', 'darg_rain_event', 'alba_rain_event']
rain_raw_copy = ['Rain', 'mang_Rainfall [mm]', 'darg_Rainfall [mm]', 'alba_Rainfall [mm]']


speed_raw = ['Speed','mang_Speed [m/s]', 'whit_Speed [m/s]', 'darg_Speed [m/s]', 'mota_Speed [m/s]', 'alba_Speed [m/s]']
pressure_raw = ['Pressure', 'mang_Mean sea level pressure [Hpa]', 'whit_Mean sea level pressure [Hpa]', 'darg_Mean sea level pressure [Hpa]', 'mota_Mean sea level pressure [Hpa]']
humidity_raw = ['Humidity', 'mang_Mean Relative Humidity [percent]', 'whit_Mean Relative Humidity [percent]', 'darg_Mean Relative Humidity [percent]', 'mota_Mean Relative Humidity [percent]', 'alba_Mean Relative Humidity [percent]']
direction_raw = ['Direction', 'mang_Direction [deg T]','whit_Direction [deg T]', 'darg_Direction [deg T]', 'mota_Direction [deg T]', 'alba_Direction [deg T]']
dew_point_cols = ['mang_dewpoint', 'whit_dewpoint', 'darg_dewpoint', 'mota_dewpoint', 'alba_dewpoint']
temp_raw = ['Mean Temp', 'mang_Mean Temperature [Deg C]', 'whit_Mean Temperature [Deg C]', 'darg_Mean Temperature [Deg C]', 'mota_Mean Temperature [Deg C]', 'alba_Mean Temperature [Deg C]']
dewpoint_lag = ['Mean Temp','mang_dewpoint', 'darg_dewpoint', 'mota_dewpoint', 'alba_dewpoint']

temp_lag = ['Mean Temp', 'mang_Mean Temperature [Deg C]', 'darg_Mean Temperature [Deg C]', 'mota_Mean Temperature [Deg C]', 'alba_Mean Temperature [Deg C]']
humidity_lag = ['Humidity', 'mang_Mean Relative Humidity [percent]', 'darg_Mean Relative Humidity [percent]', 'mota_Mean Relative Humidity [percent]', 'alba_Mean Relative Humidity [percent]']
pressure_lag = ['Pressure', 'mang_Mean sea level pressure [Hpa]', 'darg_Mean sea level pressure [Hpa]', 'mota_Mean sea level pressure [Hpa]']


cos_cols = ['mang_cos', 'whit_cos', 'darg_cos', 'mota_cos', 'alba_cos']
sin_cols = ['mang_sin', 'whit_sin', 'darg_sin', 'mota_sin', 'alba_sin']

u_cols = ['mang_u_wind', 'whit_u_wind', 'darg_u_wind', 'mota_u_wind', 'alba_u_wind']
v_cols = ['mang_v_wind', 'whit_v_wind', 'darg_v_wind', 'mota_v_wind', 'alba_v_wind']

u_cols_lag = ['Speed','mang_u_wind','darg_u_wind', 'mota_u_wind', 'alba_u_wind']
v_cols_lag = ['Speed','mang_v_wind','darg_v_wind', 'mota_v_wind', 'alba_v_wind']

# FILES LIST

whitianga_list = ["/Users/neilkumar/Desktop/Python/Oceanum_Test/whitianga/whitianga_rain.csv",
                  "/Users/neilkumar/Desktop/Python/Oceanum_Test/whitianga/whitianga_wind.csv",
                  "/Users/neilkumar/Desktop/Python/Oceanum_Test/whitianga/whitianga_pressure.csv",
                  "/Users/neilkumar/Desktop/Python/Oceanum_Test/whitianga/whitianga_temperature.csv"]

motat_list = ["/Users/neilkumar/Desktop/Python/Oceanum_Test/motat/motat_rain.csv",
              "/Users/neilkumar/Desktop/Python/Oceanum_Test/motat/motat_wind.csv",
              "/Users/neilkumar/Desktop/Python/Oceanum_Test/motat/motat_pressure.csv",
              "/Users/neilkumar/Desktop/Python/Oceanum_Test/motat/motat_temperature.csv",]

dargaville_list = ["/Users/neilkumar/Desktop/Python/Oceanum_Test/dargaville/dargaville_rain.csv",
                   "/Users/neilkumar/Desktop/Python/Oceanum_Test/dargaville/dargaville_wind.csv",
                   "/Users/neilkumar/Desktop/Python/Oceanum_Test/dargaville/dargaville_pressure.csv",
                   "/Users/neilkumar/Desktop/Python/Oceanum_Test/dargaville/dargaville_temperature.csv",]

albany_list = ["/Users/neilkumar/Desktop/Python/Oceanum_Test/albany/albany_rain.csv",
               '/Users/neilkumar/Desktop/Python/Oceanum_Test/albany/albany_wind.csv',
               '/Users/neilkumar/Desktop/Python/Oceanum_Test/albany/albany_pressure.csv',
               '/Users/neilkumar/Desktop/Python/Oceanum_Test/albany/albany_temperature.csv',]

mangere_list = ['/Users/neilkumar/Desktop/Python/Oceanum_Test/mangere/mangere_rain.csv',
                '/Users/neilkumar/Desktop/Python/Oceanum_Test/mangere/mangere_wind.csv',
                '/Users/neilkumar/Desktop/Python/Oceanum_Test/mangere/mangere_pressure.csv',
                '/Users/neilkumar/Desktop/Python/Oceanum_Test/mangere/mangere_temperature.csv',]

location_list = ['mota', 'whit', 'darg', 'mang', 'alba']

#  Cols to drop

station_cols = ['mang_Station level pressure', 'whit_Station level pressure', 'darg_Station level pressure', 'mota_Station level pressure', 'alba_Station level pressure']
misc = ['mota_Rainfall [mm]','Base Label', 'Segment Label', 'Window Label', 'j_labels', 'hour', 'month','year', 'Observation time UTC',]

# lag dictionary

lag_dict = {'con_prox':['Direction', 'mang_con_prox', 'whit_con_prox', 'darg_con_prox', 'mota_con_prox'],
            'deltaH':['Humidity','mang_Hum8h', 'whit_Hum8h', 'darg_Hum8h', 'mota_Hum8h', 'alba_Hum8h'],
            'deltaPu':['Direction','mang_PT1_u', 'whit_PT1_u', 'darg_PT1_u', 'mota_PT1_u'],
            'deltaPv':['Direction','mang_PT1_v', 'whit_PT1_v', 'darg_PT1_v', 'mota_PT1_v'],
            'deltaTH':['Direction', 'mang_dTH8h', 'whit_dTH8h', 'darg_dTH8h', 'mota_dTH8h', 'alba_dTH8h'],
            'inverseTH':['Humidity', 'mang_invTH', 'whit_invTH', 'darg_invTH', 'mota_invTH', 'alba_invTH'],
            'rmin_pressure':['Humidity','mang_rmin_P', 'darg_rmin_P', 'mota_rmin_P', 'alba_rmin_P'],
            'dpd7h':['Mean Temp','mang_dpd7h', 'whit_dpd7h', 'darg_dpd7h', 'mota_dpd7h', 'alba_dpd7h'],
            'dpd8h':['Mean Temp','mang_dpd8h', 'whit_dpd8h', 'darg_dpd8h', 'mota_dpd8h', 'alba_dpd8h'],
            'wind_u':['Direction','mang_u_wind', 'whit_u_wind', 'darg_u_wind', 'mota_u_wind', 'alba_u_wind'],
            'wind_v':['Direction', 'mang_v_wind', 'whit_v_wind', 'darg_v_wind', 'mota_v_wind', 'alba_v_wind']
            }

