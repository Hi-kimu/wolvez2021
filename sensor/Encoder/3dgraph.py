# -*- coding: utf-8 -*-
# 3D plot

#最初にいろいろとインストール必要があるのでいかに記す
#pip3 install --upgrade pip
#sudo pip3 install matplotlib
#pip3 install numpy --upgrade
#sudo apt-get install python3-gi-cairo
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def en(x,y,xc,yc,r):
    #z=math.exp(-(x^2+y^2)/2)*(x^2+y^2)/(2*pi)
    return np.exp(-((x-xc)**2/r**2+(y-yc)**2/r**2)/2)*((x-xc)**2/r**2+(y-yc)**2/r**2)/(2*math.pi)


# x, y, z成分のデータの作成
x = np.arange(-25, 25, 0.25)
y = np.arange(-25, 25, 0.25)
X, Y = np.meshgrid(x, y)

Z = en(X,Y,0,0,15)

#Z1 = en(X,Y,-5,-5)




fig = plt.figure()
ax = Axes3D(fig)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.plot_surface(X, Y, Z, cmap=plt.cm.coolwarm,linewidth=0, antialiased=False)
#ax.plot_surface(X, Y, Z1, cmap=plt.cm.coolwarm,linewidth=0, antialiased=False)


# z軸の設定
ax.set_xlim(-25.01, 25.01)
ax.set_ylim(-25.01, 25.01)
ax.set_zlim(0.0, 0.5)

# カラーバーの表示
#fig.colorbar(surf, shrink=0.5, aspect=10)

plt.show()