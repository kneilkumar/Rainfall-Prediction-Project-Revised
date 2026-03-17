import time

import numpy as np
import pandas as pd
import os
import datetime
from lists import *


pd.set_option('mode.chained_assignment', None)


def read_data(directory_list):
    temp = pd.read_csv(directory_list[0])
    drop_list_0 = [feat_name for feat_name in temp.columns if 'Data Source'.lower() in feat_name.lower()
                 or 'PERIOD'.lower() in feat_name.lower() or 'Frequency'.lower() in feat_name.lower() or
                 'Deficit [mm]' in feat_name or 'Runoff [mm]' in feat_name or 'Grass Temperature [Deg C]' in feat_name]
    temp.drop(drop_list_0, axis=1, inplace=True)
    for directory in directory_list[1:]:
        weather_data = pd.read_csv(directory)
        drop_list = [feat_name for feat_name in weather_data.columns if 'Data Source'.lower() in feat_name.lower()
                     or 'PERIOD'.lower() in feat_name.lower() or 'Frequency'.lower() in feat_name.lower() or
                     'Deficit [mm]' in feat_name or 'Runoff [mm]' in feat_name or 'Grass Temperature [Deg C]' in feat_name
                     or 'Minimum Temperature' in feat_name or 'Maximum Temperature' in feat_name]
        weather_data.drop(drop_list, axis=1, inplace=True)
        temp = pd.merge(left=temp, right=weather_data, on='Observation time UTC', how='left')

    return temp


def add_prefix(df, location):
    df = df.add_prefix(f"{location}_")
    df.rename(columns={f"{location}_Observation time UTC": "Observation time UTC"}, inplace=True)
    return df


motat_weather = add_prefix(read_data(motat_list), location_list[0])
whitianga_weather = add_prefix(read_data(whitianga_list), location_list[1])
dargaville_weather = add_prefix(read_data(dargaville_list), location_list[2])
mangere_weather = add_prefix(read_data(mangere_list), location_list[3])
albany_weather = add_prefix(read_data(albany_list), location_list[4])

pre_feat_eng_data = mangere_weather
for weather in [whitianga_weather, dargaville_weather, motat_weather, albany_weather]:
    pre_feat_eng_data = pd.merge(left=pre_feat_eng_data, right=weather,on='Observation time UTC', how='left')

path = '/Users/neilkumar/Desktop/Python/Oceanum_Test/ml_datasets/pre_feat_eng_data.csv'

if os.path.exists(path=path):
    pass
else:
    pre_feat_eng_data.to_csv('/Users/neilkumar/Desktop/Python/Oceanum_Test/ml_datasets/pre_feat_eng_data.csv')
    print("the code didn't work")

# step 2: sort the data timewise

pre_feat_eng_data = pre_feat_eng_data.sort_values(by='Observation time UTC')


def sentinel_fill(lag_list, lag_df_shape, lag_df_cols, matching_index=None):
    feat_keys = {"Labels":[-150., -80.],"Humidity":[1e7, 1.2e7], "Speed":[-69420.,-42069.], "Pressure":[-20000., -10000.], "Max Temp":[-2000., -1200.],
                 "Min Temp":[1200, 2000], "Mean Temp":[110000., 119000.], "Direction":[-1e9,-1e8], "Rain":[-800.,-700.]}
    fill_array = np.ones(lag_df_shape)
    rng = np.random.default_rng(69420)
    fill_vals = rng.uniform(low=feat_keys[lag_list[0]][0], high=feat_keys[lag_list[0]][1],size=(1,lag_df_shape[1]))
    if matching_index is not None:
        fill_df = pd.DataFrame(data=fill_array * fill_vals, columns=list(lag_df_cols), index=matching_index)
    else:
        fill_df = pd.DataFrame(data=fill_array * fill_vals, columns=list(lag_df_cols))
    return fill_df


non_nan_cols = pre_feat_eng_data.columns[~pre_feat_eng_data.isna().any()].tolist()
copies = pre_feat_eng_data[non_nan_cols]
pre_feat_eng_data = pre_feat_eng_data.drop(non_nan_cols, axis=1)


for lagtypes in [rain, speed, pressure, mean, humidity, direction]:
    temp = pre_feat_eng_data[lagtypes[1:]]
    temp = temp.fillna(sentinel_fill(lagtypes, temp.shape, temp.columns))
    pre_feat_eng_data = pd.concat([pre_feat_eng_data, temp], axis=1)

pre_feat_eng_data = pd.concat([pre_feat_eng_data, copies],axis=1)
pre_feat_eng_data = pre_feat_eng_data.drop(station_cols + ['alba_Mean sea level pressure [Hpa]'], axis=1)
pre_feat_eng_data = pre_feat_eng_data.dropna(axis=1)


def sigmoid(df):
    return 1/(1+np.exp(df))


def rain_clock(series, area):
    block_starts = np.where(series[area] == 1)[0]
    final_block_length = series.index.values[-1] + 1 - block_starts[-1]
    final_block_repeated = np.repeat(block_starts[-1], final_block_length)
    block_lengths = np.diff(block_starts)
    expanded_starts = np.append(np.repeat(series.index.values[0], block_starts[0] - series.index.values[0]), np.repeat(block_starts[:-1], block_lengths))
    expanded_starts = np.append(expanded_starts, final_block_repeated)
    global_index = series.index.values
    clock = global_index - expanded_starts
    series[f"{area[:4]}_rain_clock"] = clock
    untrusted_ends = np.array(series.groupby('Segment Label')[f"{area[:4]}_rain_clock"].idxmin())
    untrusted_ends[0] = block_starts[0]
    untrusted_starts = np.append(np.array([0]), np.where(series['Segment Label'].diff() >= 1)[0])
    trust_col = np.ones(series.shape[0])
    for i in range(len(untrusted_starts)):
        trust_col[untrusted_starts[i]: untrusted_ends[i]] = 0
    series[f"{area[:4]}_trust_clock"] = trust_col
    return series[[f"{area[:4]}_rain_clock", f"{area[:4]}_trust_clock"]]


def feat_creation(df):
    df['Observation time UTC'] = pd.to_datetime(df['Observation time UTC'])
    df['Segment Label'] = np.where(df['Observation time UTC'].diff() > datetime.timedelta(hours=1), True,
                                   False).cumsum()
    rainfall_df = df[rain_raw[1:]]
    rainfall_df.drop(['mota_Rainfall [mm]', 'whit_Rainfall [mm]'], axis=1, inplace=True)
    rainfall_events = np.where(rainfall_df > 0.3, 1, 0)
    rainfall_events = pd.DataFrame(data=rainfall_events, columns=[f"{feat[:4]}_rain_event" for feat in rain_raw_copy[1:]])
    rainfall_events['Segment Label'] = df['Segment Label']

    rainfall_events_cols = list(rainfall_events.columns)
    clock_df = pd.DataFrame()
    for rains in rainfall_events_cols:
        if rains == 'Segment Label':
            continue
        area_clock = rain_clock(rainfall_events[[rains] + ['Segment Label']], rains)
        clock_df = pd.concat([clock_df, area_clock], axis=1)

    df = df.drop(list(rainfall_df.columns), axis=1)
    rainfall_events.drop(['Segment Label'],axis=1, inplace=True)

    humidity_df = df[humidity_raw[1:]].astype(float)
    temperature_df = np.array(df[temp_raw[1:]].astype(float))
    x = np.log(humidity_df/100)
    gamma = x + (17.625*temperature_df)/(243.04 + temperature_df)
    dewpoint_df = (243.04*gamma)/(17.625 - gamma)
    dewpoint_df.columns = dew_point_cols

    cyclic_df_sin = np.sin(df[direction_raw[1:]].astype(float)*np.pi/180)
    cyclic_df_cos = np.cos(df[direction_raw[1:]].astype(float)*np.pi/180)
    wind_u = pd.DataFrame(data=np.array(df[speed_raw[1:]]) * np.array(cyclic_df_cos), columns=u_cols)
    wind_v = pd.DataFrame(data=np.array(df[speed_raw[1:]]) * np.array(cyclic_df_sin), columns=v_cols)
    df = df.drop(direction_raw[1:], axis=1)

    deltaH = df[humidity_raw[1:] + ['Segment Label']].groupby('Segment Label').diff(8)
    deltaH = deltaH.fillna(sentinel_fill(['Humidity'], deltaH.shape, deltaH.columns, deltaH.index))
    deltaH.columns = [f"{feat[:4]}_Hum8h" for feat in temp_raw[1:]]

    delta2H = df[temp_raw[1:] + ['Segment Label']].groupby('Segment Label').diff(9).rolling(9).var()
    delta2H = delta2H.fillna(sentinel_fill(['Mean Temp'], delta2H.shape, delta2H.columns, delta2H.index))
    delta2H.columns = [f"{feat[:4]}_2Hum8h" for feat in temp_raw[1:]]
    delta2H.index = df.index

    inverseTH = (np.array(df[humidity_raw[1:]])) / np.array(df[temp_raw[1:]])
    inverseTH = pd.DataFrame(data=inverseTH, columns=[f"{feat[:4]}_invTH" for feat in temp_raw[1:]])
    inverseTH = inverseTH.replace([np.inf, -np.inf], np.nan)
    inverseTH = inverseTH.fillna(sentinel_fill(['Humidity'], inverseTH.shape, inverseTH.columns))

    inverseTH['Segment Label'] = df['Segment Label']
    deltaTH = inverseTH.groupby('Segment Label').rolling(9).var()
    deltaTH = deltaTH.fillna(sentinel_fill(['Direction'], deltaTH.shape, deltaTH.columns, deltaTH.index))
    deltaTH.columns = [f"{feat[:4]}_dTH8h" for feat in temp_raw[1:]]
    deltaTH.index = df.index
    inverseTH.drop('Segment Label', axis=1, inplace=True)

    PxW = pd.DataFrame(np.array(df[speed_raw[1:5]])/ np.array(df[pressure_raw[1:]]))
    PxW = PxW.fillna(sentinel_fill(['Mean Temp'], PxW.shape, PxW.columns, PxW.index))
    PxW.index = df.index
    PxW.columns = [f"{feat[:4]}_PxW" for feat in pressure_raw[1:]]

    rmin_pressure = df[humidity_lag[1:] + ['Segment Label']].groupby('Segment Label').rolling(8).var()
    rmin_pressure = rmin_pressure.fillna(sentinel_fill(['Humidity'], rmin_pressure.shape, rmin_pressure.columns, rmin_pressure.index))
    rmin_pressure.index = df.index
    rmin_pressure.columns = [f"{feat[:4]}_rmin_P" for feat in humidity_lag[1:]]

    df = pd.concat([df, rainfall_events, dewpoint_df, wind_u, wind_v, deltaH, inverseTH,PxW, cyclic_df_sin, cyclic_df_cos, deltaTH, rmin_pressure], axis=1)

    deltaPu = pd.DataFrame(np.array(df[pressure_raw[1:] + ['Segment Label']].groupby('Segment Label').diff(1)) * np.array(df[u_cols[:4]]))
    deltaPu = deltaPu.fillna(sentinel_fill(['Direction'], deltaPu.shape, deltaPu.columns, deltaPu.index))
    deltaPu.columns = [f"{feat[:4]}_PT1_u" for feat in v_cols[:4]]
    deltaPu.index = df.index

    deltaPv = pd.DataFrame(np.array(df[pressure_raw[1:] + ['Segment Label']].groupby('Segment Label').diff(1)) * np.array(df[v_cols[:4]]))
    deltaPv = deltaPv.fillna(sentinel_fill(['Direction'], deltaPv.shape, deltaPv.columns, deltaPv.index))
    deltaPv.columns = [f"{feat[:4]}_PT1_v" for feat in v_cols[:4]]
    deltaPv.index = df.index

    pure_clock = np.array(clock_df[['mang_rain_clock','darg_rain_clock']])
    clock_pu = np.where(deltaPu[['mang_PT1_u','darg_PT1_u']] > 0, 1, 0)
    clock_pv = np.where(deltaPv[['mang_PT1_v','darg_PT1_v']] > 0, 1, 0)
    pure_clock_u = pd.DataFrame(data=pure_clock * clock_pu, columns=['mang_rain_clock_u','darg_rain_clock_u'])
    pure_clock_v = pd.DataFrame(data=pure_clock * clock_pv, columns=['mang_rain_clock_v','darg_rain_clock_v'])

    dpd_base = pd.DataFrame(data=np.array(df[temp_raw[1:]].astype(float)) - np.array(dewpoint_df.astype(float)))
    dpd_base['Segment Label'] = df['Segment Label']
    for deltas in [7,8]:
        temp = dpd_base.groupby('Segment Label').diff(deltas)
        temp = temp.fillna(sentinel_fill(['Mean Temp'], temp.shape, temp.columns, temp.index))
        temp.columns = [f"{feat[:4]}_dpd{str(deltas)}h" for feat in temp_raw[1:]]
        df = pd.concat([df, temp], axis=1)

    df = df.drop(speed_raw[1:], axis=1)
    df['hour'] = df['Observation time UTC'].dt.hour
    df['month'] = df['Observation time UTC'].dt.month
    df['year'] = df['Observation time UTC'].dt.year
    df['hour_copy'] = df['hour'].astype(float)
    df['month_copy'] = df['month'].astype(float)
    df['year_copy'] = df['year'].astype(float)
    df['hour_cyclical_sin'] = np.sin(2*np.pi*df['hour_copy']/24)
    df['hour_cyclical_cos'] = np.cos(2*np.pi*df['hour_copy']/24)
    df['month_cyclical_sin'] = np.sin(2*np.pi*df['month_copy']/12)
    df['month_cyclical_cos'] = np.cos(2*np.pi*df['month_copy']/12)

    convective_proxy = np.array(df[humidity_raw[1:5]]) * np.array(df[['mang_dpd8h', 'whit_dpd8h', 'darg_dpd8h', 'mota_dpd8h']])
    convective_proxy = pd.DataFrame(convective_proxy/np.array((df[pressure_raw[1:]]))).rolling(9).var()
    convective_proxy = convective_proxy.replace([np.inf, -np.inf], np.nan)
    convective_proxy = convective_proxy.fillna(sentinel_fill(['Direction'], convective_proxy.shape, convective_proxy.columns, convective_proxy.index))
    convective_proxy.index = df.index
    convective_proxy.columns = [f"{feat[:4]}_con_prox" for feat in pressure_raw[1:]]

    df = pd.concat([df, deltaPv, deltaPu, convective_proxy, pure_clock_v, pure_clock_u], axis=1)

    return df


# setting up row expanded data
feat_created_df = feat_creation(pre_feat_eng_data)
copy = feat_created_df['mota_Rainfall [mm]']
feat_created_df = feat_created_df.shift(1).drop(['mota_Rainfall [mm]'], axis=1)
feat_created_df['mota_Rainfall [mm]'] = copy
feat_created_df = feat_created_df.dropna(axis=0)


def vectorised_row_expansion(df):
    df['Base Label'] = np.where(df['mota_Rainfall [mm]'] > 0.3, 1, 0)
    event_matrix_candidates = np.lib.stride_tricks.sliding_window_view(np.array(df['Base Label']), 8)
    base, segment, time = df['Base Label'], df['Segment Label'], df['Observation time UTC']
    segment_mask = np.lib.stride_tricks.sliding_window_view(np.array(df['Segment Label']), 8)
    event_matrix = event_matrix_candidates[(np.all(segment_mask == segment_mask[:, [0]], axis=1))]
    risk_matrix = np.where(event_matrix.cumsum(axis=1) <= 1, 1, 0)
    Y = np.array((event_matrix * risk_matrix))
    row_with_rain = Y.sum(axis=1) > 0
    termination_index = np.where(row_with_rain, np.argmax(Y, axis=1), 7)
    new_row_index = np.repeat(np.arange(0,Y.shape[0]), termination_index+1)
    block_ends = (termination_index + 1).cumsum()
    block_starts = block_ends - (termination_index + 1)
    global_index = np.arange(block_ends[-1])
    expanded_block_start = block_starts[new_row_index]
    j = global_index - expanded_block_start + 1
    y = Y[new_row_index, global_index - expanded_block_start]
    X = np.array(df)
    time_index = np.arange(X.shape[0])
    absolute_time_index = time_index[new_row_index] + (j - 1)
    X = X[absolute_time_index]
    df = pd.DataFrame(data=X, columns=df.columns)
    df['y_labels'] = y
    df['j_labels'] = j
    df['Window Label'] = np.cumsum(np.where(df['j_labels'] == 1, 1, 0))
    return df, base, segment, time


start = time.perf_counter()
row_expanded_df, base, segment, times = vectorised_row_expansion(feat_created_df)
print(f'{time.perf_counter() - start}')

# baselines

from sklearn.metrics import log_loss


def persistence_baseline_computation(expanded_df, base_labels, year):
    sub_df = expanded_df[['Observation time UTC', 'y_labels', 'j_labels', 'Window Label', 'Segment Label']]
    sub_df['year'] = pd.to_datetime(sub_df['Observation time UTC']).dt.year
    sub_df = sub_df[sub_df['year'] == year]
    first_loc = np.argmax(sub_df['j_labels'].values == 1)
    sub_df = sub_df.drop(sub_df.index[0:first_loc], axis=0)
    risk_end = np.max(np.where(sub_df['j_labels'].values == 8)[0])
    end_pos = sub_df.index.values.shape[0] - (risk_end + 1)
    if end_pos == 0:
        pass
    else:
        sub_df = sub_df.head(-end_pos)
    persistence_row = sub_df.groupby(['Segment Label', 'Window Label'])['y_labels'].shift(1)
    base_probability = base_labels.sum()/base_labels.shape[0]
    persistence_row = persistence_row.fillna(base_probability)
    persistence_row = np.minimum(np.maximum(persistence_row, 1e-4), 1 - 1e-4)
    sub_df['persistence_row_C'] = 1 - persistence_row
    persistence_window = 1 - sub_df.groupby(['Segment Label', 'Window Label'])['persistence_row_C'].prod()
    persistence_window = np.minimum(np.maximum(persistence_window, 1e-4), 1 - 1e-4)
    window_label = np.where(sub_df.groupby(['Segment Label','Window Label'])['y_labels'].sum() >= 1, 1, 0)
    persistence_ll = log_loss(window_label, persistence_window)
    return persistence_ll


persistence_ll = persistence_baseline_computation(row_expanded_df, base, 2025)


def cross_val_unsmoothclima(base, segment, time):
    no_seg_E = np.lib.stride_tricks.sliding_window_view(np.array(base), 8)
    seg_mask = np.lib.stride_tricks.sliding_window_view(np.array(segment), 8)
    E = no_seg_E[np.all(seg_mask == seg_mask[:,[0]], axis=1)]
    seg = np.where(np.all(seg_mask == seg_mask[:,[0]], axis=1))[0]
    obs_time = np.array(time.iloc[seg])
    climate_label = np.where(np.sum(E, axis=1)>= 1, 1, 0)
    temp = np.column_stack((obs_time, climate_label))
    climate_df = pd.DataFrame(data=temp, columns=['obs_time', 'climate_label'])

    climate_df['hour'] = climate_df['obs_time'].dt.hour
    climate_df['month'] = climate_df['obs_time'].dt.month
    climate_df['year'] = climate_df['obs_time'].dt.year
    climate_df['hour_month'] = list(zip(climate_df['hour'], climate_df['month']))
    cv_ll = 0

    for i in [2022, 2023, 2024, 2025]:
        train_set = climate_df[climate_df['year'] <= i]
        if i == 2025:
            break
        test_set = climate_df[climate_df['year'] == (i+1)]
        p_hm = train_set.groupby(['hour', 'month'])['climate_label'].sum()/train_set.groupby(['hour', 'month'])['climate_label'].size()
        p_hm_map = p_hm.to_dict()
        train_set['p_hm'] = train_set.set_index(['hour', 'month']).index.map(p_hm_map.get)
        train_set = train_set.drop_duplicates(subset=['hour', 'month'])
        train_set = train_set.set_index('hour_month')
        test_set['p_hm'] = test_set.set_index(['hour_month']).index.map(train_set['p_hm'].to_dict().get)

        cv_ll = cv_ll + log_loss(y_true=test_set['climate_label'].astype(float), y_pred=test_set['p_hm'])
    return cv_ll/3


unsmoothed_ll = cross_val_unsmoothclima(base, segment, times)


def cross_val_smoothclima(base, segment, time):
    no_seg_E = np.lib.stride_tricks.sliding_window_view(np.array(base), 8)
    seg_mask = np.lib.stride_tricks.sliding_window_view(np.array(segment), 8)
    E = no_seg_E[np.all(seg_mask == seg_mask[:,[0]], axis=1)]
    seg = np.where(np.all(seg_mask == seg_mask[:,[0]], axis=1))[0]
    obs_time = np.array(time.iloc[seg])
    climate_label = np.where(np.sum(E, axis=1)>= 1, 1, 0)
    temp = np.column_stack((obs_time, climate_label))
    climate_df = pd.DataFrame(data=temp, columns=['obs_time', 'climate_label'])
    climate_df['hour'] = climate_df['obs_time'].dt.hour
    climate_df['month'] = climate_df['obs_time'].dt.month
    climate_df['year'] = climate_df['obs_time'].dt.year
    climate_df['hour_month'] = list(zip(climate_df['hour'], climate_df['month']))

    hour_cv_ll = 0
    month_cv_ll = 0


    for i in [2022, 2023, 2024, 2025]:
        train_set = climate_df[climate_df['year'] <= i]
        if i == 2025:
            break
        test_set = climate_df[climate_df['year'] == (i+1)]
        p_hm = train_set.groupby(['hour', 'month'])['climate_label'].sum()/train_set.groupby(['hour', 'month'])['climate_label'].size()
        p_h = train_set.groupby(['hour'])['climate_label'].sum()/train_set.groupby(['hour'])['climate_label'].size()
        p_m = train_set.groupby(['month'])['climate_label'].sum()/train_set.groupby(['month'])['climate_label'].size()
        train_set['p_g'] = train_set['climate_label'].sum()/train_set['climate_label'].shape[0]

        w_hm = train_set.groupby(['hour', 'month'])['climate_label'].size()/(train_set.groupby(['hour', 'month'])['climate_label'].size() + 100)
        w_h = train_set.groupby(['hour'])['climate_label'].size()/(train_set.groupby(['hour'])['climate_label'].size() + 50)
        w_m = train_set.groupby(['month'])['climate_label'].size()/(train_set.groupby(['month'])['climate_label'].size() + 10)

        p_hm_map = p_hm.to_dict()
        p_h_map = p_h.to_dict()
        p_m_map = p_m.to_dict()
        train_set['p_h'] = train_set['hour'].map(p_h_map)
        train_set['p_m'] = train_set['month'].map(p_m_map)
        train_set['p_hm'] = train_set.set_index(['hour', 'month']).index.map(p_hm_map.get)

        w_hm_map = w_hm.to_dict()
        w_h_map = w_h.to_dict()
        w_m_map = w_m.to_dict()
        train_set['w_h'] = train_set['hour'].map(w_h_map)
        train_set['w_m'] = train_set['month'].map(w_m_map)
        train_set['w_hm'] = train_set.set_index(['hour', 'month']).index.map(w_hm_map.get)

        pass1h = train_set['w_hm']*train_set['p_hm'] + (1 - train_set['w_hm'])*train_set['p_h']
        train_set['p_smoothed_h'] = train_set['w_h']*pass1h + (1 - train_set['w_h'])*train_set['p_g']

        pass1m = train_set['w_hm']*train_set['p_hm'] + (1 - train_set['w_hm'])*train_set['p_m']
        train_set['p_smoothed_m'] = train_set['w_m']*pass1m + (1 - train_set['w_m'])*train_set['p_g']
        train_set = train_set.drop_duplicates(subset=['hour', 'month'])
        train_set = train_set.set_index('hour_month')
        test_set['p_smoothed_m'] = test_set.set_index(['hour_month']).index.map(train_set['p_smoothed_m'].to_dict().get)
        test_set['p_smoothed_h'] = test_set.set_index(['hour_month']).index.map(train_set['p_smoothed_h'].to_dict().get)
        test_set['p_smoothed_m'] = test_set['p_smoothed_m'].fillna(train_set['p_m'])
        test_set['p_smoothed_h'] = test_set['p_smoothed_h'].fillna(train_set['p_h'])

        hour_cv_ll = hour_cv_ll + log_loss(y_true=test_set['climate_label'].astype(float), y_pred=test_set['p_smoothed_h'])
        month_cv_ll = month_cv_ll + log_loss(y_true=test_set['climate_label'].astype(float), y_pred=test_set['p_smoothed_m'])

    return hour_cv_ll/3, month_cv_ll/3


cv1, cv2 = cross_val_smoothclima(base, segment, times)

# feat eng/feat creation

def incomplete_remover(df):
    first_loc = np.argmax(df['j_labels'].values == 1)
    df = df.drop(df.index[0:first_loc], axis=0)
    risk_end = np.max(np.where(df['j_labels'].values == 8)[0])
    end_pos = df.index.values.shape[0] - (risk_end + 1)
    if end_pos == 0:
        return df
    else:
        return df.head(-end_pos)


X_train = row_expanded_df[row_expanded_df['year'] < 2025]
X_train = incomplete_remover(X_train)
y_train = X_train['y_labels']
X_train = X_train.drop(['y_labels'],axis=1)

X_valid = row_expanded_df[row_expanded_df['year'] == 2022]
X_valid = incomplete_remover(X_valid)
y_valid = X_valid['y_labels']
X_valid = X_valid.drop(['y_labels'],axis=1)

X_test = row_expanded_df[row_expanded_df['year'] == 2025]
X_test = incomplete_remover(X_test)
y_test_rows = X_test['y_labels']

ll_test_df = X_test[['Window Label', 'Segment Label', 'j_labels', 'y_labels']]
window_labels = pd.Series(data=np.where(ll_test_df.groupby(['Segment Label', 'Window Label'])['y_labels'].sum() >= 1, 1, 0))

X_test = X_test.drop(['y_labels'], axis=1)


# Lagged features

def lagging_pipeline(df, laglist, hours_to_lag):
    lagfeats = laglist[1:]
    temp_lag_df = pd.DataFrame()
    for hour in hours_to_lag:
        lagged_var = df[lagfeats + ['Segment Label', 'Window Label'] ].groupby(['Segment Label', 'Window Label']).shift(hour)
        lagged_var.columns = [f"{feat[0:4]}_{laglist[1][4:]}_{str(hour)}_lag" for feat in lagged_var.columns]
        temp_lag_df = pd.concat([temp_lag_df, lagged_var],axis=1)
    temp_lag_df = temp_lag_df.fillna(sentinel_fill(laglist, temp_lag_df.shape, temp_lag_df.columns, temp_lag_df.index))
    return pd.concat([df, temp_lag_df],axis=1)


X_train = lagging_pipeline(X_train, pressure_raw, [1,2])
X_test = lagging_pipeline(X_test, pressure_raw, [1,2])

X_train = lagging_pipeline(X_train, u_cols_lag, [1])
X_test = lagging_pipeline(X_test, u_cols_lag, [1])

X_train = lagging_pipeline(X_train, v_cols_lag, [1])
X_test = lagging_pipeline(X_test, v_cols_lag, [1])

X_train = lagging_pipeline(X_train, dewpoint_lag, [1,2,3])
X_test = lagging_pipeline(X_test, dewpoint_lag, [1,2,3])

X_train = lagging_pipeline(X_train, temp_lag, [1,2,3,4])
X_test = lagging_pipeline(X_test, temp_lag, [1,2,3,4])

X_train = lagging_pipeline(X_train, rain_lag, [1,2,3,4])
X_test = lagging_pipeline(X_test, rain_lag, [1,2,3,4])

X_train = lagging_pipeline(X_train, lag_dict['dpd8h'], [1])
X_test = lagging_pipeline(X_test, lag_dict['dpd8h'], [1])

X_train = lagging_pipeline(X_train, lag_dict['deltaTH'], [1,2])
X_test = lagging_pipeline(X_test, lag_dict['deltaTH'], [1,2])

X_train = lagging_pipeline(X_train, lag_dict['con_prox'], [1,2,3])
X_test = lagging_pipeline(X_test, lag_dict['con_prox'], [1,2,3])


X_train.drop(misc, axis=1, inplace=True)
X_test.drop(misc, axis=1, inplace=True)
X_valid.drop(misc, axis=1, inplace=True)

# The actual ML part
print('reached ML')

from xgboost import XGBClassifier

# BASE TESTING

xgb = XGBClassifier(n_estimators=500, max_depth=10, learning_rate=0.01, random_state=69420, n_jobs=-1,
                    min_child_weight=4,colsample_bytree=0.9)

xgb.fit(X_train.values, y_train.values)
pred = np.minimum(np.maximum(xgb.predict(X_test.values), 1e-4), 1 - 1e-4)
ll_test_df['row_P_C'] = 1 - pred
survival_prod = 1 - ll_test_df.groupby(['Segment Label', 'Window Label'])['row_P_C'].prod()
window_pred = np.minimum(np.maximum(survival_prod, 1e-4), 1 - 1e-4)
window_pred.index = window_labels.index
window_ll = log_loss(window_labels, window_pred)

print("window ll ", window_ll)
