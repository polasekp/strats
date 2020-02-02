To get SUM of km run:

from datetime import datetime
datetime_str = '09/19/18 13:55:26'
datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
float(Activity.objects.filter(start__gte=datetime_object, type=4).aggregate(total_km=Sum("distance"))["total_km"]/1000)
  