"# wolvez2021" 
Mission code in Python for Keio Wolve'Z CaSat project 2021

## About our CanSat
### What is CanSat
  CanSat is a small satellite sized approximately as small as soda can.
  Our ultimate goal is to develop an autonomous tracking rover which is able to recognize a moving object such as humans or the other rover and chase it until it stops. This rover would be beneficial when it comes to space exploration, especially when building a base on the other planet, where there would be very few people. We can use it as carrier robot for example, when carring something from one point to another. We are hoping this rover would cooperate with humans and make human space activity more efficiant.

### Our CanSat: Autonomous Tracking Robot by Image Processing
  We are assuming a rover which has LRF and optimal camera. Autonomous tracking is accomplished by image processing and distance. Considerring the CanSat regulation, we are making a rover which has optical camera and ultrasonic sensor in order to realize autonomous tracking.

<div align="center">
<img src="https://user-images.githubusercontent.com/57528969/90110593-6fd8ee80-dd88-11ea-88c2-6b1f03e266d6.png" width="50%" title="Our CanSat">
</div>

## Table of Contents
- [Wolve'Z CANSAT Project 2020](#wolvez-cansat-project-2020)
  - [About our CanSat](#about-our-cansat)
    - [What is CanSat](#what-is-cansat)
    - [Our CanSat: Autonomous Tracking Robot by Image Processing](#our-cansat-autonomous-tracking-robot-by-image-processing)
  - [Table of Contents](#table-of-contents)
  - [Our Mission](#our-mission)
    - [Human Following Robot](#human-following-robot)
    - [Mission Sequence](#mission-sequence)
    - [Image Processing](#image-processing)
  - [Hardware Requirements](#hardware-requirements)
  - [Software Requirements](#software-requirements)
    - [Setups](#setups)
  - [Usage](#usage)
    - [Algorithm](#algorithm)
  - [Project Member](#project-member)

## Our Mission
### Human Following Robot
For the purpose of simplification of autonomous human tracking, we assume that the target human wears **red T-shirts** and we utilize red-object-traking technique. 
### Mission Sequence
Here is our Mission Sequence. After the landing, the rover starts searching for human by using ultrasonic sensor. Once it detects human, it activates the camera and start to follow the target human.

<div align="center">
<img src="https://user-images.githubusercontent.com/57528969/96898453-b0609100-14ca-11eb-8ec9-45d6982e07f1.png" width="80%" title="Mission Sequence">
</div>

**Re-Following**  
Our CanSat have the abillity of re-following. In the case that it lost the target, it starts spinning, searching for the target using ultrasonic sensor. Once it detects the target again, it starts re-follow.

<div align="center">
<img src="https://user-images.githubusercontent.com/57528969/96900442-10583700-14cd-11eb-8eec-033e666a4063.png" width="80%" title="Refollow">
</div>

### Image Processing Algorithm
<div align="center">
<img src="https://user-images.githubusercontent.com/57528969/96898443-ae96cd80-14ca-11eb-9b5b-7c8019700ac0.png" width="80%" title="image processing">
</div>

## Hardware Requirements
- Microcomputer
  - Raspberry Pi 3B
  <div align="left">
  <img src="https://user-images.githubusercontent.com/57528969/90947202-008d8980-e46f-11ea-964d-d67bf354345d.png" width="20%" title="Raspberry Pi 3B">
  </div>
- Sensors
    
    |**Sensor**|**Products**|**image**|
    |:---|:---:|:---:|
    |Camera|[Raspberry Pi Camera Module V2](http://akizukidenshi.com/catalog/g/gM-10518/)|<img src="https://user-images.githubusercontent.com/57528969/91016338-95d37e00-e627-11ea-8958-fba777a15778.png" width="20%" title="Raspberry Pi Camera Module V2">|
    |Ultrasonic sensor|[HC-SR04](http://akizukidenshi.com/catalog/g/gM-11009/)|<img src="https://user-images.githubusercontent.com/57528969/90114657-fcd27680-dd8d-11ea-9fe1-95e3e4e484da.png" width="20%" title="Ultrasonic Sensor">|
    |Communication Module|[ES920LR](https://easel5.com/products/es920lr/)|<img src="https://user-images.githubusercontent.com/57528969/90114355-92b9d180-dd8d-11ea-8565-76540eea0920.png" width="20%" title="Communication Module">|
    |GPS module|[GYSFDMAXB](http://akizukidenshi.com/catalog/g/gK-09991/)|<img src="https://user-images.githubusercontent.com/57528969/90114335-89c90000-dd8d-11ea-82d3-70ab748fa5f2.png" width="20%" title="GPS Module">|
    |Accelaration Sensor|[BNO055](https://www.switch-science.com/catalog/5511/)|<img src="https://user-images.githubusercontent.com/57528969/90114534-ce549b80-dd8d-11ea-81fd-3569fe0b1477.png" width="20%" title="Accelaration Sensor">|
    |Motor|comming soon...||
    |Motor Driver|[TA7291P](https://toshiba.semicon-storage.com/jp/semiconductor/product/motor-driver-ics/brushed-dc-motor-driver-ics/detail.TA7291P.html)|<img src="https://user-images.githubusercontent.com/57528969/91016133-4725e400-e627-11ea-8397-be0234b8e773.png" width="20%" title="Motor Driver">|

## Software Requirements
Firstly, you need to clone this repository
```
git clone https://github.com/ujtk6014/WolveZ_CANSAT2020.git
```
### Setups
**1. OpenCV**  
  OpenCV is necessary for implimenting image processing in order to recognize following target. Go to `setup` folder and run `inst_opencv.sh` to install opencv.
  Check in python if you successflly installed opencv or not
  ```Python
  import cv2
  ```
**2. GPS Setup**  
  The proposed robot orients itself by GPS. run `setup_gps.sh`  in terminal.

**3. I2C Setup**  
  I2C is one of the ways of serial communication. This is necessary for BNO055 (acceralation sensor). run `setup_i2c`

**4. Access Point Setup (Additional)**  
  if you want to use Raspberry Pi remotely in **No Wi-fi** environment, you may want to use your Rasberry Pi as Wi-fi access point. Then go to `setup/ap` and run `setup_ap.sh`
  Once you activate access point, you cannot connect your Raspberry Pi to other Wi-fi networks. So you can turn it off by running `ap_off.sh`.
  If you want to re-activate, then, run  `ap_on.sh`

## Project Member
- Project manager   
  Yuki Ko
- Software (★: Part leader)  
  ★Yuji Tanaka, Yuki Ko, Kazuki Oshima, Hikaru Kimura, Miyuki Nakamura
- Hardware (★: Part leader)  
  ★Mina Park, Shinichiro Kaji
  
