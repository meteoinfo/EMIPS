f1 = addfile(r'C:\Users\chen\Desktop\wrfout_d01_2017-01-02_00_00_00_r')
f2 = addfile(r'C:\Users\chen\Desktop\wrfout_d01_2017-01-02_00_00_00')
height = 0
time = 0
vna1 = 'pan'
vna2 = 'pan'
mul = 4
levs = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
data1 = f1[vna1][time, height]
subplot(1, 2, 1, axestype='map', projinfo=f1.proj, gridline=True)
geoshow('country')
imshow(data1*10**mul, levs, proj=f1.proj)
colorbar()


data2 = f2[vna2][time, height]
subplot(1, 2, 2, axestype='map', projinfo=f2.proj, gridline=True)
geoshow('country')
imshow(data2*10**mul, levs, proj=f2.proj)
colorbar()

print(data1.sum())
print(data2.sum())
