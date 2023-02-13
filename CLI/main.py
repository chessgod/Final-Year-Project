import gpxpy;
import gpxpy.gpx;

with open('sail.gpx','r',encoding='utf-8') as file:
    gpx = gpxpy.parse(file)

print(gpx.get_bounds)
print()
print(gpx.get_duration)
print()
print(gpx.get_points_no)

