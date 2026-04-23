from datetime import datetime

def get_time_angles():
    now = datetime.now()

    seconds = now.second
    minutes = now.minute
    hours = now.hour % 12


    second_angle = -(seconds * 6)
    

    minute_angle = -(minutes * 6 + seconds * 0.1)
    

    hour_angle   = -(hours * 30 + minutes * 0.5)

    return hour_angle, minute_angle, second_angle