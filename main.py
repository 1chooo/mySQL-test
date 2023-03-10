import json
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error

def get_data_from_sql(content, config,) -> None:
    # 建立資料庫連線
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # 執行 SELECT 指令選取表格的 data 欄位資料
    query = ("SELECT data from garmin_push_log;")

    # 執行 SELECT 指令
    cursor.execute(query)

    # 將資料匯出成 txt 檔案
    # with open(output_file_path, 'w') as f:
        
    for (data,) in cursor:
        content.append(data)
    # 關閉資料庫連線
    cursor.close()
    cnx.close()

    return content

def get_data_without_try(sleep_levels, content) -> list:
    sleep_levels = []

    for line in content:
        data = json.loads(line)
        if (data.get('sleeps')[0].get('sleepLevelsMap')) != None:
            sleep_levels.append(data.get('sleeps')[0].get('sleepLevelsMap'))
    
    return sleep_levels

def get_data_with_try(sleep_levels, content) -> list:
    sleep_levels = []

    for line in content:
        data = json.loads(line)
        try:
            sleep_level = data['sleeps'][0]['sleepLevelsMap']
            sleep_levels.append(sleep_level)
        # if (sleep_level != None):
        #     sleep_levels.append(sleep_level)
        # try:
            # data = json.loads(line)
            # sleep_levels.append(data['sleeps'][0]['sleepLevelsMap'])
        except:
            pass
    
    return sleep_levels

def show_sleep_level_maps(sleep_levels) -> None:
    print(f"Total sleep level maps we can use: {len(sleep_levels)}")

config = {
    'host': 'localhost',
    'database': 'database_name',
    'user': 'root',
    'password': 'pwd',
}
sleep_levels = []
content = []
content = get_data_from_sql(content, config)
sleep_levels = get_data_with_try(sleep_levels, content)
print(len(sleep_levels))
show_sleep_level_maps(sleep_levels)

def main(num,):
    try:
        # select the first sleep level map
        sleep_map = sleep_levels[num]

        # extract time range
        start_time = min(
            period['startTimeInSeconds']
            for phase in sleep_map.values()
            for period in phase
        )
        end_time = max(
            period['endTimeInSeconds']
            for phase in sleep_map.values()
            for period in phase
        )
        sleep_runtime = end_time - start_time
        sleep_runtime_in_hr = sleep_runtime / 3600
        print(f"Sleep time range: {start_time} - {end_time}")
        print(f"Sleep runtime: {sleep_runtime} s ({sleep_runtime_in_hr} hr)")

        # adjust time values relative to start_time
        for phase in sleep_map.values():
            for period in phase:
                for key, value in period.items():
                    if key.endswith('TimeInSeconds'):
                        period[key] = value - start_time

        # plot the figure
        phases = ['Deep', 'Light', 'Awake', 'REM']
        fig, ax = plt.subplots()
        for i, phase in enumerate(phases):
            y = i + 1
            for period in sleep_map.get(phase.lower(), []):
                start = period['startTimeInSeconds']
                end = period['endTimeInSeconds']
                duration = end - start
                ax.barh(
                    y, duration, left=start, height=0.5,
                    align='center', alpha=0.7, label=phase
                )

        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(phases)
        ax.set_xlabel('Time (s)')
        ax.set_xlim(0, end_time - start_time)
        ax.legend(loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.2))
        plt.legend().set_visible(False)
        plt.title(f'The cycle in one sleep.({num})')
        file_name = './img/' + str(num) + '.png'
        # file_name = './test_img/' + str(num) + '.png'
        plt.savefig(file_name)
        plt.show()
    except:
        pass

for i in range(len(sleep_levels)):
    main(i)